import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.services.simulation_service import SimulationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["simulation"])

MAX_CONCURR_USERS = 10
simulation_service = SimulationService()


class Prediction(BaseModel):
    ref: str
    lat: float
    lng: float
    history: list[list[int]]
    burnedCells: int = Field(..., alias="burned_cells")
    radiusM: float = Field(..., alias="radius_m")
    truncated: bool
    latExtentDeg: float = Field(..., alias="lat_extent_deg")
    lonExtentDeg: float = Field(..., alias="lon_extent_deg")
    gridH: int = Field(..., alias="grid_h")
    gridW: int = Field(..., alias="grid_w")
    cellSizeM: float = Field(..., alias="cell_size_m")

    class Config:
        populate_by_name = True


class SimulationResponse(BaseModel):
    predictions: list[Prediction]
    nStepsRun: int = Field(..., alias="n_steps_run")

    class Config:
        populate_by_name = True


class OnDemandSimRequest(BaseModel):
    nSteps: int = Field(288, ge=1, le=288, alias="n_steps", description="Number of sim steps")

    class Config:
        populate_by_name = True


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    responses={500: {"description": "Internal server error simulation failed"}},
)
async def run_simulation(db: Session = Depends(get_db)) -> SimulationResponse:
    """Executes a 1-hour spread simulation (4 ticks) for all verified fires."""
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

    automatic_steps = 4
    semaphore = asyncio.Semaphore(MAX_CONCURR_USERS)

    prediction_dicts = await asyncio.gather(
        *(
            simulation_service.execute_single_fire_simulation(fire, automatic_steps, semaphore)
            for fire in verified_fires
        )
    )

    predictions = [Prediction(**p) for p in prediction_dicts]
    n_steps_run = max((len(p.history) for p in predictions), default=0)

    return SimulationResponse(
        predictions=predictions,
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
    """Executes an extended spread simulation for a specific fire on demand."""
    fire = (
        db.query(
            FireReports.id,
            FireReports.reference_number,
            func.ST_Y(FireReports.location_geom).label("lat"),
            func.ST_X(FireReports.location_geom).label("lng"),
            FireReports.boundary_radius,
        )
        .filter(FireReports.reference_number == fire_id, FireReports.status == ReportStatus.verified)
        .first()
    )

    if fire is None:
        logger.warning("Simulation requested for unknown or unverified fire: %s", fire_id)
        raise HTTPException(status_code=404, detail=f"Verified fire {fire_id} not found")

    semaphore = asyncio.Semaphore(1)
    prediction_dict = await simulation_service.execute_single_fire_simulation(fire, req.nSteps, semaphore)

    return Prediction(**prediction_dict)