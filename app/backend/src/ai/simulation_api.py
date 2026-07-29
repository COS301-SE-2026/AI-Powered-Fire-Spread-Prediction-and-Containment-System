# FastAPI endpoint: recieves simulation params from frontend, runs DCA pipeline, returns tick history

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from .dca import run_dca

router = APIRouter(prefix="/api", tags=["simulation"])


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
    n_steps: int = Field(48, ge=1, le=500, description="Number of simulation steps")

    # Amount independent ignition points to seed
    n_ignition_points: int = Field(1, ge=1, le=10)

    weather: WeatherParams = WeatherParams()
    static: StaticParams = StaticParams()
    dca: DCAParams = DCAParams()


class TickStats(BaseModel):
    tick: int
    burning: int
    burned: int
    total_cells: int


class SimulationResponse(BaseModel):
    # Flattened burn-state grids per tick (list of (H*W) ints in {0=unburned, 1=burning, 2=burned})
    # Frontend reshapes to [H, W] using grid_h/_w
    history: list[list[int]]
    grid_h: int
    grid_w: int
    tick_stats: list[TickStats]
    n_steps_run: int


# Grid Builders


# Temp func. Delete when integrate real spatial data
def build_uniform_grid(h: int, w: int, value: float, dtype=np.float32) -> np.ndarray:
    return np.full((h, w), value, dtype=dtype)


def build_weather_grids(
    h: int, w: int, w_params: WeatherParams
) -> dict[str, np.ndarray]:
    # TODO: replace build_uniform_grid() calls with real fetches
    return {
        "wind_u": build_uniform_grid(h, w, w_params.wind_u),
        "wind_v": build_uniform_grid(h, w, w_params.wind_v),
        "rel_humidity": build_uniform_grid(h, w, w_params.rel_humidity),
        "temperature": build_uniform_grid(h, w, w_params.temperature),
    }


def build_static_grids(h: int, w: int, s_params: StaticParams) -> dict[str, np.ndarray]:
    # TODO: Replace build_uniform_grids() call with real raster lookups
    return {
        "elevation": build_uniform_grid(h, w, s_params.elevation),
        "slope": build_uniform_grid(h, w, s_params.slope),
        "aspect_sin": build_uniform_grid(h, w, s_params.aspect_sin),
        "aspect_cos": build_uniform_grid(h, w, s_params.aspect_cos),
        "fuel_load": build_uniform_grid(h, w, s_params.fuel_load),
        "dryness": build_uniform_grid(h, w, s_params.dryness),
    }


def params_to_torch(dca: DCAParams):
    import torch

    return {
        "a": torch.tensor(dca.a),
        "p_h": torch.tensor(dca.p_h),
        "c_1": torch.tensor(dca.c_1),
        "c_2": torch.tensor(dca.c_2),
        "p_continue": torch.tensor(dca.p_continue),
    }
