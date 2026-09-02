from __future__ import annotations

import argparse
import json
from pathlib import Path
import warnings

import numpy as np
import optuna
import torch

from app.backend.src.ai.dca import run_dca
from ml.features.fuel_load import process_sentinal2_and_worldcover
from ml.features.terrain import extract_terrain_features

warnings.filterwarnings("ignore", category=UserWarning)

class HistoricalFireDataset:
    """Preloads and caches raster structures in memory for low-latency Optuna evaluations"""
    
    def __init__(self, data_dir: str | Path, cell_size_m: float = 15.0):
        self.data_dir = Path(data_dir)
        self.cell_size_m = cell_size_m
        self.events: list[dict] = []
        self._load_and_cache_events()
        
    def _load_and_cache_events(self) -> None:
        npz_files = sorted(list(self.data_dir.glob("fire_*.npz")))
        if not npz_files:
            raise FileNotFoundError(f"No .npz files found in {self.data_dir}")
        
        print(f"Preloading and extracting static layers for {len(npz_files)} fire events...")
        
        for p in npz_files:
            data = np.load(p, allow_pickle=True)
            H, W = data["target_burned_mask"].shape
            target_shape = (H, W)
            
            # 1. extract static features if not already pre-extracted
            if "static_elevation" in data:
                static_grids = {
                    "elevation": data["static_elevation"].astype(np.float32),
                    "slope": data["static_slope"].astype(np.float32),
                    "aspect_sin": data["static_aspect_sin"].astype(np.float32),
                    "aspect_cos": data["static_aspect_cos"].astype(np.float32),
                    "fuel_load": data["static_fuel_load"].astype(np.float32),
                    "dryness": data["static_dryness"].astype(np.float32),
                }
            else:
                # fallback to raster extraction from saved hrefs
                terrain = extract_terrain_features(
                    dem_path=str(data["dem_vsis3"]),
                    min_lon=0.0,
                    min_lat=0.0,
                    max_lon=1.0,
                    max_lat=1.0,
                    target_shape=target_shape,
                )
                aspect_rad = np.radians(terrain["aspect"])
                veg = process_sentinal2_and_worldcover(
                    b04_path=str(data["b04_href"]),
                    b08_path=str(data["b08_href"]),
                    b11_path=str(data["b11_href"]),
                    min_lon=0.0,
                    min_lat=0.0,
                    max_lon=1.0,
                    max_lat=1.0,
                    target_shape=target_shape,
                )
                static_grids = {
                    "elevation": terrain["elevation"].astype(np.float32),
                    "slope": terrain["slope"].astype(np.float32),
                    "aspect_sin": np.sin(aspect_rad).astype(np.float32),
                    "aspect_cos": np.cos(aspect_rad).astype(np.float32),
                    "fuel_load": veg["fuel_load"].astype(np.float32),
                    "dryness": veg["dryness"].astype(np.float32),
                }
            
            # 2. reconstruct weather timeline
            weather_u = data["weather_u"]
            weather_v = data["weather_v"]
            weather_temp = data["weather_temp"]
            weather_rh = data["weather_rh"]
            n_hours = weather_u.shape[0]
            
            hourly_weather = [
                {
                    "wind_u": weather_u[t].astype(np.float32),
                    "wind_v": weather_v[t].astype(np.float32),
                    "temperature": weather_temp[t].astype(np.float32),
                    "rel_humidity": weather_rh[t].astype(np.float32),
                }
                for t in range(n_hours)
            ]
            
            self.events.append({
                "fire_id": str(data["fire_id"]),
                "ground_truth": data["target_burned_mask"].astype(bool),
                "ignition_mask": data["ignition_mask"].astype(bool),
                "static_grids": static_grids,
                "hourly_weather": hourly_weather,
                "n_steps": max(4, n_hours * 4),     # 4 cellular automata ticks per hour
            })
            
        print(f"Cached {len(self.events)} events in RAM")
        
def compute_iou(simulated: np.ndarray, ground_truth: np.ndarray) -> float:
    """Calculates Jaccard Index / Intersection-over-Union"""
    intersection = np.logical_and(simulated, ground_truth).sum()
    union = np.logical_or(simulated, ground_truth).sum()
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    return float(intersection / (union + 1e-6))

class DCAObjective:
    def __init__(self, dataset: HistoricalFireDataset):
        self.dataset = dataset
        
    def __call__(self, trial: optuna.Trial) -> float:
        # sample the 5 core DCA spread mechanics parameters
        trial_params = {
            # a: base fuel ignition cooefficient
            "a": torch.tensor(trial.suggest_float("a", 0.001, 0.08, log=True)),
            # p_h: spotting / jump ignition probability
            "p_h": torch.tensor(trial.suggest_float("p_h", 0.005, 0.25)),
            # c_1: wind alignment exponential multiplier
            "c_1": torch.tensor(trial.suggest_float("c_1", 0.005, 0.15)),
            # c_2: slope / terrain angle alignment multiplier
            "c_2": torch.tensor(trial.suggest_float("c_2", 0.005, 0.15)),
            # p_continue: probability of a burning cell continuing to burn next step
            "p_continue": torch.tensor(trial.suggest_float("p_continue", 0.2, 0.9)),
        }
        
        iou_scores: list[float] = []
        
        for step_idx, event in enumerate(self.dataset.events):
            try:
                history = run_dca(
                    weather_grids=event["hourly_weather"],
                    static_grids=event["static_grids"],
                    cell_size_m=self.dataset.cell_size_m,
                    n_steps=event["n_steps"],
                    ignition_mask=event["ignition_mask"],
                    params=trial_params,
                )
                final_grid = history[-1]
                # In DCA: 1 = currently burning, 2 = burned out
                sim_burned = (final_grid == 1) | (final_grid == 2)
                iou = compute_iou(sim_burned, event["ground_truth"])
                iou_scores.append(iou)
                
            except Exception as e:
                # penalize configurations causing numerical explosions or crashes
                return 0.0
            
            # pruning hook: allow Optuna to terminate unpromising parameter trials early
            current_mean_iou = float(np.mean(iou_scores))
            trial.report(current_mean_iou, step=step_idx)
            if trial.should_prune():
                raise optuna.TrialPruned()
            

        