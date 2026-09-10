# FastAPI endpoint: recieves simulation params from frontend, runs DCA pipeline, returns tick history

from __future__ import annotations

import math
import os
import logging
import uuid
import boto3
import asyncio
import json
import hashlib
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports

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
MAX_GRID_CELLS = 50000
TICKS_PER_HOUR = 4

AWS_REGION = os.environ.get("AWS_REGION")
INFERENCE_QUEUE_URL = os.environ["INFERENCE_QUEUE_URL"]
ARTIFACTS_S3_BUCKET = os.environ.get("ARTIFACTS_S3_BUCKET", "fire-system-artifacts-827257544258")
ARTIFACTS_ROOT = Path(os.environ.get("ARTIFACTS_ROOT", "/mnt/fire-system-artifacts"))
RESULTS_DIR = ARTIFACTS_ROOT / "results"

sqs = boto3.client("sqs", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

logger = logging.getLogger(__name__)

RESULT_POLL_INTERVAL_S = 1.0
RESULT_POLL_TIMEOUT_S = 360.0

def grid_dimensions_for_extent(
    lat_extent_deg: float,
    lon_extent_deg: float,
    lat: float,
    target_cell_size_m: float = TARGET_CELL_SIZE_M,
) -> tuple[int, int]:
    # gets H and W from the real world target cell size
    lat_extent_m = lat_extent_deg * METRES_PER_DEG_LAT
    lon_extent_m = lon_extent_deg * METRES_PER_DEG_LAT * math.cos(math.radians(lat))

    naive_h = lat_extent_m / target_cell_size_m
    naive_w = lon_extent_m / target_cell_size_m
    naive_cells = naive_h * naive_w

    if naive_cells > MAX_GRID_CELLS:
        scale_factor = math.sqrt(naive_cells / MAX_GRID_CELLS)
        effective_cell_size_m = target_cell_size_m * scale_factor
    else:
        effective_cell_size_m = target_cell_size_m

    raw_h = lat_extent_m / effective_cell_size_m
    raw_w = lon_extent_m / effective_cell_size_m

    dim_scale = max(raw_h / MAX_GRID_DIMENSION, raw_w / MAX_GRID_DIMENSION, 1.0)

    H = int(np.clip(round(raw_h / dim_scale), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))
    W = int(np.clip(round(raw_w / dim_scale), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))

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

async def wait_for_result(job_id: str) -> dict | None:
    """
    Polls the shared artifact mount for the result JSON written by worker.py 
    """

    result_path = RESULTS_DIR / f"{job_id}.json"
    s3_key = f"results/{job_id}.json"
    elapsed = 0.0

    while elapsed < RESULT_POLL_TIMEOUT_S:
        if await asyncio.to_thread(result_path.exists):
            try:
                content = await asyncio.to_thread(result_path.read_text)
                return json.loads(content)
            except Exception as e:
                logger.warning(f"Error reading the results for the job {job_id}: {e}")

        try:
            resp = await asyncio.to_thread(
                s3_client.get_object,
                Bucket=ARTIFACTS_S3_BUCKET,
                Key=s3_key
            )
            raw_body = await asyncio.to_thread(resp["Body"].read)
            return json.loads(raw_body.decode("utf-8"))
        except s3_client.exceptions.NoSuchKey:
            pass
        except Exception as err:
            logger.warning(f"Error reading {job_id} from s3: {err}")

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
            "boundary_radius_m": boundary_m,
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
    req: OnDemandSimRequest, db: Session = Depends(get_db)
) -> SimulationResponse:
    """
    Endpoint for all verified fires

    Runs for 4 ticks which is a 1 hour spread simulation
    """

    verified_fires_raw = (
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
    fire_ids = [f.id for f in verified_fires_raw]
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
            for fire in verified_fires_raw
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
