# FastAPI endpoint: recieves simulation params from frontend, runs DCA pipeline, returns tick history

from __future__ import annotations

import math
import os
import logging
import uuid
import boto3
import asyncio
import torch
import json
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db
from enums.report_status import ReportStatus
from models.reported_fires import FireReports

from .dca import run_dca
from .model_pipeline import run_convlstm_dca
from .geo import bbox_from_fire, touch_edge
from .resolve_tiles import resolve_tile_paths
from ml.features.real_data_loader import load_real_inference_data
from .simulation import build_boundary_ignition_mask
from .cache import build_fire_cache_key, get_cached_prediction, cache_prediction
from ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig

logger = logging.getLogger("simulation_api")

router = APIRouter(prefix="/api", tags=["simulation"])

METRES_PER_DEG_LAT = 111_320.0
TARGET_CELL_SIZE_M = 15.0 # 15 meter per cell
MIN_GRID_DIMENSION = 10
MAX_GRID_DIMENSION = 800
TICKS_PER_HOUR = 4

GRID_H = 64
GRID_W = 64

AWS_REGION = os.environ.get("AWS_REGION")
INFERENCE_QUEUE_URL = os.environ["INFERENCE_QUEUE_URL"]
ARTIFACTS_ROOT = Path(os.environ.get("ARTIFACTS_ROOT", "/mnt/firefighter-system-artifacts"))
RESULTS_DIR = ARTIFACTS_ROOT / "results"

sqs = boto3.client("sqs", region_name=AWS_REGION)

RESULT_POLL_INTERVAL_S = 1.0
RESULT_POLL_TIMEOUT_S = 360.0

# device = "cuda" if torch.cuda.is_available() else "cpu"

# convlstm_cfg = WeatherDeltaModelConfig(input_dim=10, hidden_dims=[48,48], kernel_size=3, output_dim=4)
# convlstm_model = WeatherDeltaModel(convlstm_cfg).to(device)

# # CHECKPOINT_PATH = os.environ.get("CONVLSTM_CHECKPOINT", "app/artifact_store/weather_convlstm/LATEST/model.pt")
# # if os.path.exists(CHECKPOINT_PATH):
# #     convlstm_model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device))
# # convlstm_model.eval()

# # # will change after training
# # DEFAULT_DCA_PARAMS = {
# #     "a": torch.tensor(0.015),
# #     "p_h": torch.tensor(0.06),
# #     "c_1": torch.tensor(0.04),
# #     "c_2": torch.tensor(0.03),
# #     "p_continue": torch.tensor(0.6),
# # }

def grid_dimensions_for_extent(
        lat_extent_deg: float,
        lon_extent_deg: float,
        lat: float,
        target_cell_size_m: float = TARGET_CELL_SIZE_M
) -> tuple[int, int]:
    # gets H and W from the real world target cell size
    lat_extent_m = lat_extent_deg * METRES_PER_DEG_LAT
    lon_extent_m = lon_extent_deg * METRES_PER_DEG_LAT * math.cos(math.radians(lat))

    H = int(np.clip(round(lat_extent_m / target_cell_size_m), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))
    W = int(np.clip(round(lon_extent_m / target_cell_size_m), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))

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
    containment_lines: list[str] = Field(default_factory=list, description="List of WKT containment lines")

def burned_area_radius_m(
    burned_cells: int, H: int, W: int, lat_extent_deg: float, lon_extent_deg: float
) -> float:
    if burned_cells <= 0:
        return 0.0
    cell_h_m = (lat_extent_deg / H) * METRES_PER_DEG_LAT
    cell_w_m = (lon_extent_deg / W) * METRES_PER_DEG_LAT
    return math.sqrt(burned_cells * cell_h_m * cell_w_m / math.pi)

MAX_CONCURR_USERS = 10

async def wait_for_result(job_id: str) -> dict | None:
    """
    Polls the shared artifact mount for the result JSON written by worker.py 
    """

    result_path = RESULTS_DIR / f"{job_id}.json"
    elapsed = 0.0

    while elapsed < RESULT_POLL_TIMEOUT_S:
        if await asyncio.to_thread(result_path.exists):
            try:
                content = await asyncio.to_thread(result_path.read_text)
                return json.loads(content)
            except Exception as e:
                logger.warning(f"Error reading the results for the job {job_id}: {e}")

        await asyncio.sleep(RESULT_POLL_INTERVAL_S)
        elapsed += RESULT_POLL_INTERVAL_S

    return None

async def simulate_single_fire(fire, automatic_steps: int, semaphore: asyncio.Semaphore, containment_lines: list[str] | None=None) -> Prediction:
    """
    ECoordinates caching, dispatches job to SQS, and waits for worker output
    """
    lines = containment_lines or []
    boundary_m = float(fire.boundary_radius) * 1000

    min_lon, min_lat, max_lon, max_lat = bbox_from_fire(
        lat=fire.lat,
        lng=fire.lng,
        boundary_radius_m=boundary_m,
        n_steps=automatic_steps
    )

    lat_extent_deg = max_lat - min_lat
    lon_extent_deg = max_lon - min_lon

    H, W = grid_dimensions_for_extent(lat_extent_deg, lon_extent_deg, fire.lat)

    cell_size_lat_m = (lat_extent_deg / H) * METRES_PER_DEG_LAT
    cell_size_lon_m = (lon_extent_deg / W) * METRES_PER_DEG_LAT * math.cos(math.radians(fire.lat))
    cell_size_m = (cell_size_lat_m + cell_size_lon_m) / 2 # average of the 2

    cache_key = build_fire_cache_key(
        ref=fire.reference_number,
        lat=fire.lat,
        lng=fire.lng,
        boundary_radius_m=boundary_m,
        n_steps=automatic_steps,
        cell_size_m=cell_size_m,
        containment_lines=lines
    )

    if lines:
        cache_key = f"{cache_key}:lines_{hash(tuple(lines))}"

    cached_result = await asyncio.to_thread(get_cached_prediction, cache_key)
    if cached_result is not None:
        return Prediction(**cached_result)
        
    async with semaphore:
        cached_result = await asyncio.to_thread(get_cached_prediction, cache_key)
        if cached_result is not None:
            return Prediction(**cached_result)

        job_id = f"{fire.reference_number}-{uuid.uuid4().hex[:8]}"
        job = {
            "job_id": job_id,
            "region_id": fire.reference_number,
            "center_lat": fire.lat,
            "center_lon": fire.lng,
            "grid_bounds": [min_lon, min_lat, max_lon, max_lat],
            "duration_hours": automatic_steps / TICKS_PER_HOUR,
            "n_steps": automatic_steps,
            "cell_size_m": cell_size_m,
            "grid_h": H,
            "grid_w": W,
            "containment_lines": lines,
        }

        await asyncio.to_thread(
            sqs.send_message,
            QueueUrl=INFERENCE_QUEUE_URL,
            MessageBody=json.dumps(job),
        )

        raw_result = await wait_for_result(job_id)
        if raw_result is None:
            raise HTTPException(status_code=504, detail=f"Simulation for fire {fire.reference_number} timed out while waiting for worker")

        raw_history = raw_result.get("history", [])

        flattened_history: list[list[int]] = []
        for tick_grid in raw_history:
            if isinstance(tick_grid, list) and len(tick_grid) > 0 and isinstance(tick_grid[0], list):
                flattened_history.append([int(cell) for row in tick_grid for cell in row])
            else:
                flattened_history.append([int(cell) for cell in tick_grid])

        last_tick_flat = flattened_history[-1] if flattened_history else []
        burned_cells = sum(1 for c in last_tick_flat if c in (1,2))
        radius_m = burned_area_radius_m(burned_cells, H, W, lat_extent_deg, lon_extent_deg)

        last_grid_2d = np.array(raw_history[-1]) if raw_history else np.zeros((H, W))
        truncated = bool(touch_edge(last_grid_2d, burning_val=1, burned_val=2))

        prediction_payload = {
            "ref": fire.reference_number,
            "lat": fire.lat,
            "lng": fire.lng,
            "history": flattened_history,
            "burned_cells": burned_cells,
            "radius_m": radius_m,
            "truncated": truncated,
            "lat_extent_deg": lat_extent_deg,
            "lon_extent_deg": lon_extent_deg,
            "grid_h": H,
            "grid_w": W,
            "cell_size_m": cell_size_m,
        }

        await asyncio.to_thread(cache_prediction, cache_key, prediction_payload)
        return Prediction(**prediction_payload)


# The endpoint
@router.post(
    "/simulate",
    response_model=SimulationResponse,
    responses={500: {"description": "Internal server error simulation failed"}},
)
async def run_simulation(
    req: OnDemandSimRequest, 
    db: Session = Depends(get_db)
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
            FireReports.boundary_radius
        )
        .filter(FireReports.status == ReportStatus.verified)
        .all()
    )

    automatic_steps = req.n_steps
    semaphore = asyncio.Semaphore(MAX_CONCURR_USERS)

    predictions = await asyncio.gather(
        *(simulate_single_fire(fire, automatic_steps, semaphore, req.containment_lines) for fire in verified_fires)
    )

    n_steps_run = max((len(p.history) for p in predictions), default = 0)

    return SimulationResponse(
        predictions=list(predictions),
        n_steps_run=n_steps_run,
    )

@router.post(
    "/simulate/fire/{fire_id}",
    response_model=Prediction,
    responses={
        404: {"description": "Fire not found or verified"},
        500: {"description": "Internal server error"}
    }
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
            FireReports.boundary_radius
        )
        .filter(FireReports.reference_number == fire_id, FireReports.status == ReportStatus.verified)
        .first()
    )

    if fire is None:
        raise HTTPException(status_code=404, detail=f"Verified fire {fire_id} not found")

    semaphore = asyncio.Semaphore(1)
    return await simulate_single_fire(fire, req.n_steps, semaphore, req.containment_lines)