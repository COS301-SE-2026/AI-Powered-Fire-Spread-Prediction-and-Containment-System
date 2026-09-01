# Placeholder data generator while waiting for our actual datasets to be preprocessed
# When we have our proper datasets, create a load_real_dataset() with same return signiture (X[N, len(FEATURES)], y[N], fire_ids[N])
# and swap one call into train_ignition.py
# fire_ids enables group-aware split

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from app.backend.src.ai.features import grid_to_fmatrix, neighbour_features, shift
from app.backend.src.ai.schema import BURNED, BURNING, UNBURNED


@dataclass
class SynthConfig:
    H: int = 64
    W: int = 64
    n_fires: int = 40
    n_ticks: int = 30
    seed: int = 7


def make_static(rng, H, W) -> dict[str, np.ndarray]:
    """Random-but-smooth terrain and fuel fields"""

    def smooth(field, passes=8):
        for i in range(passes):
            field = (
                field
                + shift(field, 0, 1, 0)
                + shift(field, 0, -1, 0)
                + shift(field, 1, 0, 0)
                + shift(field, -1, 0, 0)
            ) / 5.0
        return field

    elevation = smooth(rng.normal(size=(H, W))).astype(np.float32)
    elevation = (elevation - elevation.min()) / np.ptp(elevation) * 800 + 200
    gy, gx = np.gradient(elevation)
    slope = np.degrees(np.arctan(np.hypot(gy, gx) / 30.0)).astype(np.float32)
    aspect = np.arctan2(gy, gx).astype(np.float32)
    fuel = np.clip(smooth(rng.normal(0.6, 0.3, size=(H, W))), 0, 1)
    dryness = np.clip(smooth(rng.normal(0.55, 0.25, size=(H, W))), 0, 1)
    return {
        "elevation": elevation,
        "slope": slope,
        "aspect_sin": np.sin(aspect).astype(np.float32),
        "aspect_cos": np.cos(aspect).astype(np.float32),
        "fuel_load": fuel.astype(np.float32),
        "dryness": dryness.astype(np.float32),
    }


def make_weather(rng, H, W) -> dict[str, np.ndarray]:
    """One tick of spatially-smooth weather"""
    base_u, base_v = rng.normal(0, 4), rng.normal(0, 4)
    return {
        "wind_u": (base_u + rng.normal(0, 0.8, (H, W))).astype(np.float32),
        "wind_v": (base_v + rng.normal(0, 0.8, (H, W))).astype(np.float32),
        "rel_humidity": np.clip(
            rng.normal(35, 12) + rng.normal(0, 3, (H, W)), 5, 95
        ).astype(np.float32),
        "temperature": np.clip(
            rng.normal(28, 6) + rng.normal(0, 1.5, (H, W)), 5, 48
        ).astype(np.float32),
    }


def true_ignition_prop(feat: dict[str, np.ndarray]) -> np.ndarray:
    """The hidden 'physics' the model needs to approximately recover"""
    z = (
        -4.0
        + 1.1 * feat["n_burning_neighbours"]
        + 1.6 * feat["upwind_burning"]
        + 0.8 * feat["downslope_burning"]
        + 2.2 * feat["dryness"]
        + 1.8 * feat["fuel_load"]
        - 0.05 * feat["rel_humidity"]
        + 0.04 * feat["temperature"]
        + 0.02 * feat["slope"]
        - 0.55 * feat["dist_to_fire"]
    )
    p = 1.0 / (1.0 + np.exp(-z))
    return p * (feat["fuel_load"] > 0.05)


def generate_synthetic_dataset(
    cfg: SynthConfig = SynthConfig(),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns X [N, n_features], y [N], fire_ids [N]
    Candidate rows = UNBURNED cells only (mirrors how DCA queries model at inference time)
    """
    rng = np.random.default_rng(cfg.seed)
    X_parts, y_parts, id_parts = [], [], []

    for fire_id in range(cfg.n_fires):
        static = make_static(rng, cfg.H, cfg.W)
        burn = np.zeros((cfg.H, cfg.W), dtype=np.int8)
        while True:
            y0, x0 = rng.integers(8, cfg.H - 8), rng.integers(8, cfg.W - 8)
            if static["fuel_load"][y0, x0] > 0.3:
                break
        burn[y0, x0] = BURNING

        for tick in range(cfg.n_ticks):
            weather = make_weather(rng, cfg.H, cfg.W)
            nbf = neighbour_features(
                burn, weather["wind_u"], weather["wind_v"], static["elevation"]
            )
            p_true = true_ignition_prop({**weather, **static, **nbf})

            unburned = burn == UNBURNED
            ignites = (rng.random(burn.shape) < p_true) & unburned

            X_tick = grid_to_fmatrix(weather, static, burn)
            mask = unburned.ravel()
            X_parts.append(X_tick[mask])
            y_parts.append(ignites.ravel()[mask].astype(np.int8))
            id_parts.append(np.full(mask.sum(), fire_id, dtype=np.int32))

            burn[burn == BURNING] = BURNED
            burn[ignites] = BURNING
            static["fuel_load"] = static["fuel_load"] * ~ignites
            if not (burn == BURNING).any():
                break

    return (np.concatenate(X_parts), np.concatenate(y_parts), np.concatenate(id_parts))
