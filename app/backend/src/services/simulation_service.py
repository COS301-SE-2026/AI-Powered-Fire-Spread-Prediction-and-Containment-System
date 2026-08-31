import asyncio
import logging
import math

import numpy as np
import torch
from fastapi import HTTPException

from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.geo import bbox_from_fire, touch_edge
from app.backend.src.ai.resolve_tiles import resolve_tile_paths
from app.backend.src.ai.simulation import build_boundary_ignition_mask
from app.backend.src.ai.weather_bridge import WeatherForecastBridge
from app.ml.features.real_data_loader import load_real_inference_data

logger = logging.getLogger(__name__)

METRES_PER_DEG_LAT = 111_320.0
TARGET_CELL_SIZE_M = 15.0
MIN_GRID_DIMENSION = 10
MAX_GRID_DIMENSION = 800

DEFAULT_DCA_PARAMS = {
    "a": torch.tensor(0.015),
    "p_h": torch.tensor(0.06),
    "c_1": torch.tensor(0.04),
    "c_2": torch.tensor(0.03),
    "p_continue": torch.tensor(0.6),
}


def grid_dimensions_for_extent(
    lat_extent_deg: float,
    lon_extent_deg: float,
    lat: float,
    target_cell_size_m: float = TARGET_CELL_SIZE_M,
) -> tuple[int, int]:
    """Calculates grid dimensions based on real-world target cell size.

    Args:
        lat_extent_deg (float): Latitude extent in degrees.
        lon_extent_deg (float): Longitude extent in degrees.
        lat (float): Central latitude for projection scaling.
        target_cell_size_m (float): Target size of one cell in meters.

    Returns:
        tuple[int, int]: The calculated height and width (H, W) for the grid.
    """
    lat_extent_m = lat_extent_deg * METRES_PER_DEG_LAT
    lon_extent_m = lon_extent_deg * METRES_PER_DEG_LAT * math.cos(math.radians(lat))

    grid_h = int(
        np.clip(
            round(lat_extent_m / target_cell_size_m),
            MIN_GRID_DIMENSION,
            MAX_GRID_DIMENSION,
        )
    )
    grid_w = int(
        np.clip(
            round(lon_extent_m / target_cell_size_m),
            MIN_GRID_DIMENSION,
            MAX_GRID_DIMENSION,
        )
    )

    return grid_h, grid_w


def burned_area_radius_m(
    burned_cells: int,
    grid_h: int,
    grid_w: int,
    lat_extent_deg: float,
    lon_extent_deg: float,
) -> float:
    """Calculates the estimated radius of the burned area in meters."""
    if burned_cells <= 0:
        return 0.0
    cell_h_m = (lat_extent_deg / grid_h) * METRES_PER_DEG_LAT
    cell_w_m = (lon_extent_deg / grid_w) * METRES_PER_DEG_LAT
    return math.sqrt(burned_cells * cell_h_m * cell_w_m / math.pi)


class SimulationService:
    """Service handling the orchestration of fire spread simulations."""

    def __init__(self) -> None:
        try:
            self.weather_bridge = WeatherForecastBridge.load("LATEST")
        except FileNotFoundError as exc:
            logger.warning(
                "Weather model checkpoint not found; relying on real-time weather fallback: %s",
                exc,
            )
            self.weather_bridge = None

    async def execute_single_fire_simulation(
        self, fire: any, automatic_steps: int, semaphore: asyncio.Semaphore
    ) -> dict:
        """Executes the DCA pipeline for a single fire entity.

        Args:
            fire (any): The database model instance representing the fire.
            automatic_steps (int): The number of simulation ticks to run.
            semaphore (asyncio.Semaphore): Concurrency limiter.

        Returns:
            dict: The prediction data payload containing history and metadata.

        Raises:
            HTTPException: If the simulation process fails internally.
        """
        async with semaphore:
            boundary_m = float(fire.boundary_radius) * 1000.0

            min_lon, min_lat, max_lon, max_lat = bbox_from_fire(
                lat=fire.lat,
                lng=fire.lng,
                boundary_radius_m=boundary_m,
                n_steps=automatic_steps,
            )

            lat_extent_deg = max_lat - min_lat
            lon_extent_deg = max_lon - min_lon

            grid_h, grid_w = grid_dimensions_for_extent(
                lat_extent_deg, lon_extent_deg, fire.lat
            )

            cell_size_lat_m = (lat_extent_deg / grid_h) * METRES_PER_DEG_LAT
            cell_size_lon_m = (
                (lon_extent_deg / grid_w)
                * METRES_PER_DEG_LAT
                * math.cos(math.radians(fire.lat))
            )
            cell_size_m = (cell_size_lat_m + cell_size_lon_m) / 2.0

            resolved = await asyncio.to_thread(
                resolve_tile_paths, min_lon, min_lat, max_lon, max_lat
            )

            static_grids, weather_data = await load_real_inference_data(
                b04_path=resolved.b04_path,
                b08_path=resolved.b08_path,
                b11_path=resolved.b11_path,
                dem_path=resolved.dem_path,
                min_lon=min_lon,
                min_lat=min_lat,
                max_lon=max_lon,
                max_lat=max_lat,
                scl_path=resolved.scl_path,
                target_shape=(grid_h, grid_w),
            )

            if self.weather_bridge is not None:
                input_hours = 6
                history_tensor = np.stack(
                    [
                        np.stack(
                            [
                                weather_data["wind_u"],
                                weather_data["wind_v"],
                                weather_data["temperature"],
                                weather_data["dryness"],
                            ],
                            axis=0,
                        )
                    ]
                    * input_hours,
                    axis=0,
                )

                hours_needed = max(1, int(np.ceil(automatic_steps / 4)))
                smoothed_weather = self.weather_bridge.forecast_for_simulation(
                    history_tensor=history_tensor,
                    rollout_steps=hours_needed,
                    substeps_per_hour=4,
                )

                weather_grids = []
                for i in range(0, len(smoothed_weather), 4):
                    frame = smoothed_weather[i]
                    weather_grids.append(
                        {
                            "wind_u": frame[0],
                            "wind_v": frame[1],
                            "temperature": frame[2],
                            "relative_humidity": frame[3],
                        }
                    )
            else:
                weather_grids = weather_data

            ignition_mask = build_boundary_ignition_mask(
                grid_h, grid_w, cell_size_m, boundary_m
            )

            try:
                history = await asyncio.to_thread(
                    run_dca,
                    weather_grids=weather_grids,
                    static_grids=static_grids,
                    n_steps=automatic_steps,
                    ignition_mask=ignition_mask,
                    params=DEFAULT_DCA_PARAMS,
                    cell_size_m=cell_size_m,
                )
            except Exception as exc:
                logger.error("DCA execution failed for fire %s: %s", fire.id, exc)
                raise HTTPException(
                    status_code=500, detail=f"Simulation failed for fire {fire.id}"
                ) from exc

            final_grid = history[-1]
            burned_cells = int(((final_grid == 1) | (final_grid == 2)).sum())
            truncated = touch_edge(final_grid, burning_val=1, burned_val=2)

            return {
                "ref": fire.reference_number,
                "lat": fire.lat,
                "lng": fire.lng,
                "history": [g.ravel().tolist() for g in history],
                "burned_cells": burned_cells,
                "radius_m": burned_area_radius_m(
                    burned_cells, grid_h, grid_w, lat_extent_deg, lon_extent_deg
                ),
                "truncated": truncated,
                "lat_extent_deg": lat_extent_deg,
                "lon_extent_deg": lon_extent_deg,
                "grid_h": grid_h,
                "grid_w": grid_w,
                "cell_size_m": cell_size_m,
            }
