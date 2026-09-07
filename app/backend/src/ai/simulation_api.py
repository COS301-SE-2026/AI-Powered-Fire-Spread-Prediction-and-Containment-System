# FastAPI endpoint: recieves simulation params from frontend, runs DCA pipeline, returns tick history

from __future__ import annotations

import math
import os
import asyncio
import torch

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports

from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.model_pipeline import run_convlstm_dca
from .geo import bbox_from_fire, touch_edge
from .resolve_tiles import resolve_tile_paths
from app.backend.ml.features.real_data_loader import load_real_inference_data
from app.backend.src.ai.simulation import build_boundary_ignition_mask
from .cache import build_fire_cache_key, get_cached_prediction, cache_prediction
from app.backend.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.backend.src.models.containment_lines import ContainmentLines
from collections import defaultdict

router = APIRouter(prefix="/api", tags=["simulation"])

METRES_PER_DEG_LAT = 111_320.0
TARGET_CELL_SIZE_M = 15.0  # 15 meter per cell
MIN_GRID_DIMENSION = 10
MAX_GRID_DIMENSION = 800

device = "cuda" if torch.cuda.is_available() else "cpu"

convlstm_cfg = WeatherDeltaModelConfig(
    input_dim=10, hidden_dims=[48, 48], kernel_size=3, output_dim=4
)
convlstm_model = WeatherDeltaModel(convlstm_cfg).to(device)

CHECKPOINT_PATH = os.environ.get(
    "CONVLSTM_CHECKPOINT", "app/artifact_store/weather_convlstm/LATEST/model.pt"
)
if os.path.exists(CHECKPOINT_PATH):
    convlstm_model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device))
convlstm_model.eval()

# will change after training
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
    # gets H and W from the real world target cell size
    lat_extent_m = lat_extent_deg * METRES_PER_DEG_LAT
    lon_extent_m = lon_extent_deg * METRES_PER_DEG_LAT * math.cos(math.radians(lat))

    H = int(
        np.clip(
            round(lat_extent_m / target_cell_size_m),
            MIN_GRID_DIMENSION,
            MAX_GRID_DIMENSION,
        )
    )
    W = int(
        np.clip(
            round(lon_extent_m / target_cell_size_m),
            MIN_GRID_DIMENSION,
            MAX_GRID_DIMENSION,
        )
    )

    return H, W


class Prediction(BaseModel):
    ref: str
    lat: float
    lng: float
    history: list[list[int]]
    burned_cells: int
    radius_m: float
    truncated: bool
    lat_extent_deg: float
    lon_extent_deg: float
    grid_h: int
    grid_w: int
    cell_size_m: float


class SimulationResponse(BaseModel):
    # Flattened burn-state grids per tick (list of (H*W) ints in {0=unburned, 1=burning, 2=burned})
    # Frontend reshapes to [H, W] using grid_h/_w
    predictions: list[Prediction]
    n_steps_run: int


class OnDemandSimRequest(BaseModel):
    n_steps: int = Field(288, ge=1, le=288, description="Number of sim steps")
    containment_lines: list[str] = Field(
        default_factory=list, description="List of WKT containment lines"
    )


def burned_area_radius_m(
    burned_cells: int, H: int, W: int, lat_extent_deg: float, lon_extent_deg: float
) -> float:
    if burned_cells <= 0:
        return 0.0
    cell_h_m = (lat_extent_deg / H) * METRES_PER_DEG_LAT
    cell_w_m = (lon_extent_deg / W) * METRES_PER_DEG_LAT
    return math.sqrt(burned_cells * cell_h_m * cell_w_m / math.pi)


MAX_CONCURR_USERS = 10


async def simulate_single_fire(
    fire,
    automatic_steps: int,
    semaphore: asyncio.Semaphore,
    containment_lines: list[str] | None = None,
) -> Prediction:
    """
    Executes the whole DCA pipeline for a single fire
    """
    lines = containment_lines or []
    boundary_m = float(fire.boundary_radius) * 1000

    min_lon, min_lat, max_lon, max_lat = bbox_from_fire(
        lat=fire.lat,
        lng=fire.lng,
        boundary_radius_m=boundary_m,
        n_steps=automatic_steps,
    )

    lat_extent_deg = max_lat - min_lat
    lon_extent_deg = max_lon - min_lon

    H, W = grid_dimensions_for_extent(lat_extent_deg, lon_extent_deg, fire.lat)

    cell_size_lat_m = (lat_extent_deg / H) * METRES_PER_DEG_LAT
    cell_size_lon_m = (
        (lon_extent_deg / W) * METRES_PER_DEG_LAT * math.cos(math.radians(fire.lat))
    )
    cell_size_m = (cell_size_lat_m + cell_size_lon_m) / 2  # average of the 2

    cache_key = build_fire_cache_key(
        ref=fire.reference_number,
        lat=fire.lat,
        lng=fire.lng,
        boundary_radius_m=boundary_m,
        n_steps=automatic_steps,
        cell_size_m=cell_size_m,
        containment_lines=tuple(sorted(lines)),
    )

    cached_result = await asyncio.to_thread(get_cached_prediction, cache_key)
    if cached_result is not None:
        return Prediction(**cached_result)

    async with semaphore:
        cached_result = await asyncio.to_thread(get_cached_prediction, cache_key)
        if cached_result is not None:
            return Prediction(**cached_result)

        resolved = await asyncio.to_thread(
            resolve_tile_paths, min_lon, min_lat, max_lon, max_lat
        )

        static_grids, weather_grids = await load_real_inference_data(
            b04_path=resolved.b04_path,
            b08_path=resolved.b08_path,
            b11_path=resolved.b11_path,
            dem_path=resolved.dem_path,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            scl_path=resolved.scl_path,
            target_shape=(H, W),
        )

        ignition_mask = build_boundary_ignition_mask(H, W, cell_size_m, boundary_m)
        grid_bounds = (min_lon, min_lat, max_lon, max_lat)

        if "aspect_sin" not in static_grids or "aspect_cos" not in static_grids:
            aspect_deg = static_grids.get("aspect")
            if aspect_deg is None:
                aspect_deg = np.zeros((H, W), dtype=np.float32)
            aspect_rad = np.radians(aspect_deg)
            static_grids["aspect_sin"] = np.sin(aspect_rad).astype(np.float32)
            static_grids["aspect_cos"] = np.cos(aspect_rad).astype(np.float32)

        wind_u = weather_grids.get("wind_u", np.zeros((H, W), dtype=np.float32))
        wind_v = weather_grids.get("wind_v", np.zeros((H, W), dtype=np.float32))
        temperature = weather_grids.get(
            "temperature", np.full((H, W), 25.0, dtype=np.float32)
        )

        if "rel_humidity" in weather_grids:
            rel_humidity = weather_grids["rel_humidity"]
        elif "dryness" in weather_grids:
            # approximate the humidty based on dryness (100 - dryness + temp)
            rel_humidity = np.clip(1.0 - weather_grids["dryness"], 0.05, 0.95).astype(
                np.float32
            )
        else:
            rel_humidity = np.full((H, W), 0.35, dtype=np.float32)

        current_frame = np.stack(
            [
                np.asarray(wind_u, dtype=np.float32),
                np.asarray(wind_v, dtype=np.float32),
                np.asarray(rel_humidity, dtype=np.float32),
                np.asarray(temperature, dtype=np.float32),
            ],
            axis=0,
        ).astype(np.float32)

        weather_history = torch.from_numpy(
            np.repeat(current_frame[np.newaxis, np.newaxis, ...], 3, axis=1)
        ).float()

        try:
            history = await asyncio.to_thread(
                run_convlstm_dca,
                convlstm_model=convlstm_model,
                weather_history=weather_history,
                static_grids=static_grids,
                cell_size_m=cell_size_m,
                n_steps=automatic_steps,
                ignition_mask=ignition_mask,
                containment_lines=lines,
                grid_bounds=grid_bounds,
                params=DEFAULT_DCA_PARAMS,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Simulation failed for fire {fire.id}: {exc}"
            ) from exc

        final_grid = history[-1]
        burned_cells = int(((final_grid == 1) | (final_grid == 2)).sum())
        truncated = touch_edge(final_grid, burning_val=1, burned_val=2)

        prediction_payload = {
            "ref": fire.reference_number,
            "lat": fire.lat,
            "lng": fire.lng,
            "history": [g.ravel().tolist() for g in history],
            "burned_cells": burned_cells,
            "radius_m": burned_area_radius_m(
                burned_cells, H, W, lat_extent_deg, lon_extent_deg
            ),
            "truncated": truncated,
            "lat_extent_deg": lat_extent_deg,
            "lon_extent_deg": lon_extent_deg,
            "grid_h": H,
            "grid_w": W,
            "cell_size_m": cell_size_m,
        }

        await asyncio.to_thread(cache_prediction, cache_key, prediction_payload, 1800)

        return Prediction(**prediction_payload)


# The endpoint
@router.post(
    "/simulate",
    response_model=SimulationResponse,
    responses={500: {"description": "Internal server error simulation failed"}},
)
async def run_simulation(
    req: OnDemandSimRequest, db: Session = Depends(get_db)
) -> SimulationResponse:
    """
    Endpoint for all verified fires

    Runs for 4 ticks which is a 1 hour spread simulation
    """

    verified_fires = (
        db.query(
            FireReports.id,
            FireReports.reference_number,
            func.ST_Y(FireReports.location_geom).label("lat"),
            func.ST_X(FireReports.location_geom).label("lng"),
            FireReports.boundary_radius,
        )
        .filter(FireReports.status == ReportStatus.verified)
        .all()
    )
    fire_ids = [f.id for f in verified_fires]
    lines_by_fire: dict[str, list[str]] = defaultdict(list)

    if fire_ids:
        rows = (
            db.query(
                ContainmentLines.fire_report_id,
                func.ST_AsText(ContainmentLines.line_geom),
            )
            .filter(ContainmentLines.fire_report_id.in_(fire_ids))
            .all()
        )
        for fire_report_id, wkt in rows:
            lines_by_fire[fire_report_id].append(wkt)

    automatic_steps = 4
    semaphore = asyncio.Semaphore(MAX_CONCURR_USERS)

    predictions = await asyncio.gather(
        *(
            simulate_single_fire(
                fire, automatic_steps, semaphore, list(dict.fromkeys(lines_by_fire.get(fire.id, []) + (req.containment_lines or [])))
            )
            for fire in verified_fires
        )
    )

    n_steps_run = max((len(p.history) for p in predictions), default=0)

    return SimulationResponse(
        predictions=list(predictions),
        n_steps_run=n_steps_run,
    )


@router.post(
    "/simulate/fire/{fire_id}",
    response_model=Prediction,
    responses={
        404: {"description": "Fire not found or verified"},
        500: {"description": "Internal server error"},
    },
)
async def run_single_fire_simulation(
    fire_id: str, req: OnDemandSimRequest, db: Session = Depends(get_db)
) -> Prediction:
    """
    Endpiont for spread on a single spread which spreads for 72 hours

    Runs the 72 hour spread which is 288 ticks for a fire selected on the map
    """ 

    fire = (
        db.query(
            FireReports.id,
            FireReports.reference_number,
            func.ST_Y(FireReports.location_geom).label("lat"),
            func.ST_X(FireReports.location_geom).label("lng"),
            FireReports.boundary_radius,
        )
        .filter(
            FireReports.reference_number == fire_id,
            FireReports.status == ReportStatus.verified,
        )
        .first()
    )

    if fire is None:
        raise HTTPException(
            status_code=404, detail=f"Verified fire {fire_id} not found"
        )

    persisted = [
            wkt
            for (wkt,) in db.query(func.ST_AsText(ContainmentLines.line_geom))
            .filter(ContainmentLines.fire_report_id == fire.id)
            .all()
        ]
    
    lines = list(dict.fromkeys(persisted + (req.containment_lines or [])))

    semaphore = asyncio.Semaphore(1)
    return await simulate_single_fire(
        fire, req.n_steps, semaphore, lines
    )
