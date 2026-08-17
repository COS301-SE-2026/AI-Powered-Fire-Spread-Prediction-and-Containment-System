# FastAPI endpoint: recieves simulation params from frontend, runs DCA pipeline, returns tick history

from __future__ import annotations

import math
import asyncio

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db
from enums.report_status import ReportStatus
from models.reported_fires import FireReports

from .dca import run_dca
from .geo import bbox_from_fire, touch_edge
from .resolve_tiles import resolve_tile_paths
from ml.features.real_data_loader import load_real_inference_data
from .simulation import build_boundary_ignition_mask

router = APIRouter(prefix="/api", tags=["simulation"])

METRES_PER_DEG_LAT = 111_320.0
TARGET_CELL_SIZE_M = 15.0 # 15 meter per cell
MIN_GRID_DIMENSION = 10
MAX_GRID_DIMENSION = 200

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

# Request/Response Schemas
# TODO: WeatherParams will become read-only once pull weather data
class WeatherParams(BaseModel):
    wind_u: float = Field(3.0, description="East-west wind component (m/s)")
    wind_v: float = Field(1.0, description="North-south wind component (m/s)")
    rel_humidity: float = Field(35.0, description="Relative humidity (%)")
    temperature: float = Field(28.0, description="Air temperature (degrees celcius)")


# TODO: StaticParams to be replaced by raster lookups
class StaticParams(BaseModel):
    elevation: float = Field(0.0, description="Mean elevation of the area (m)")
    slope: float = Field(0.0, description="Mean slope (degrees)")
    aspect_sin: float = Field(0.0)
    aspect_cos: float = Field(1.0)
    fuel_load: float = Field(0.5, description="Fuel load fraction 0-1")
    dryness: float = Field(0.5, description="Fuel dryness fraction 0-1")


class DCAParams(BaseModel):
    a: float = Field(0.1, description="Base fire spread coefficient")
    p_h: float = Field(0.4, description="Probability of horizontal spread")
    c_1: float = Field(0.1, description="Wind spread coefficient")
    c_2: float = Field(0.1, description="Slope spread coefficient")
    p_continue: float = Field(
        0.6, description="Probability a burning cell stays burning"
    )


class SimulationRequest(BaseModel):
    # Spatial extent (frontend sends bounding box it's rendering)
    # TODO: Pass lat/lng into build_weather_grids() & build_static_grids() to determine bounding box for raster/weather queries
    lat: float = Field(..., description="Map center latitude")
    lng: float = Field(..., description="Map center longitude")

    # Grid resolution (keep small for fast round-trips (Gonna use 30x30 as default))
    # TODO: These should match resolution of raster tiles
    grid_h: int = Field(30, ge=10, le=200, description="Grid rows")
    grid_w: int = Field(30, ge=10, le=200, description="Grid columns")

    # Amount of DCA ticks to run (1 tick +- is 1 model timestep)
    n_steps: int = Field(4, ge=1, le=500, description="Number of simulation steps")

    # Amount independent ignition points to seed
    n_ignition_points: int = Field(1, ge=1, le=10)

    weather: WeatherParams = WeatherParams()
    static: StaticParams = StaticParams()
    dca: DCAParams = DCAParams()


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


class SimulationResponse(BaseModel):
    # Flattened burn-state grids per tick (list of (H*W) ints in {0=unburned, 1=burning, 2=burned})
    # Frontend reshapes to [H, W] using grid_h/_w
    predictions: list[Prediction]
    n_steps_run: int

class OnDemandSimRequest(BaseModel):
    n_steps: int = Field(288, ge=1, le=288, description="Number of sim steps")
    dca: DCAParams = DCAParams()


def params_to_torch(dca: DCAParams):
    import torch

    return {
        "a": torch.tensor(dca.a),
        "p_h": torch.tensor(dca.p_h),
        "c_1": torch.tensor(dca.c_1),
        "c_2": torch.tensor(dca.c_2),
        "p_continue": torch.tensor(dca.p_continue),
    }


def burned_area_radius_m(
    burned_cells: int, H: int, W: int, lat_extent_deg: float, lon_extent_deg: float
) -> float:
    if burned_cells <= 0:
        return 0.0
    cell_h_m = (lat_extent_deg / H) * METRES_PER_DEG_LAT
    cell_w_m = (lon_extent_deg / W) * METRES_PER_DEG_LAT
    return math.sqrt(burned_cells * cell_h_m * cell_w_m / math.pi)

MAX_CONCURR_USERS = 10

async def simulate_single_fire(fire, dca: DCAParams, automatic_steps: int, semaphore: asyncio.Semaphore) -> Prediction:
    async with semaphore:
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

        resolved = await asyncio.to_thread(resolve_tile_paths,min_lon, min_lat, max_lon, max_lat)

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
            target_shape=(H, W)
        )

        ignition_mask = build_boundary_ignition_mask(
            H, W, cell_size_m, boundary_m
        )

        try:
            history = await asyncio.to_thread(
                run_dca,
                weather_grids=weather_grids,
                static_grids=static_grids,
                n_steps=automatic_steps,
                ignition_mask=ignition_mask,
                params=params_to_torch(dca),
                cell_size_m=cell_size_m
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Simulation failed for fire {fire.id}: {exc}"
            ) from exc
        
        final_grid = history[-1]
        burned_cells = int(((final_grid == 1) | (final_grid == 2)).sum())
        truncated = touch_edge(final_grid, burning_val=1, burned_val=2)
        
        return Prediction(
            ref=fire.reference_number,
            lat=fire.lat,
            lng=fire.lng,
            history=[g.ravel().tolist() for g in history],
            burned_cells=burned_cells,
            radius_m=burned_area_radius_m(burned_cells, H, W, lat_extent_deg, lon_extent_deg),
            truncated=truncated,
            lat_extent_deg=lat_extent_deg,
            lon_extent_deg=lon_extent_deg,
            grid_h=H,
            grid_w=W
        )

# The endpoint
@router.post(
    "/simulate",
    response_model=SimulationResponse,
    responses={500: {"description": "Internal server error simulation failed"}},
)
async def run_simulation(
    req: SimulationRequest, db: Session = Depends(get_db)
) -> SimulationResponse:
    """Run full DCA fire simulation pipeline and returns per-tick burn state grids.

    Runs the simulation for one hour on each verified fire. Computes a bounding box based on the fires current radius.
    Loads real data.

    Args:
        req (SimulationRequest): Incoming request payload containing grid dimentions,
        coordinates and simulation configuration parameters.

    Returns:
        SimulationResponse: Formatted response containing flattened per-tick grid histories, dimentions, stats and execution steps.

    Raises:
        HTTPException: Status 500 if underlying DCA model execution fails.
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

    automatic_steps = 4
    semaphore = asyncio.Semaphore(MAX_CONCURR_USERS)

    predictions = await asyncio.gather(
        *(simulate_single_fire(fire, req.dca, automatic_steps, semaphore) for fire in verified_fires)
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
    return await simulate_single_fire(fire, req.dca, req.n_steps, semaphore)