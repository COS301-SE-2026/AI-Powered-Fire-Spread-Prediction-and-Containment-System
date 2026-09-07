from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.containment_lines import (
    ContainmentLines,
    CreateContainmentLine,
    ContainmentLinesList
)
from app.backend.src.schemas.firefighter_dashboard import DashboardData
from app.backend.src.services.firefighter import (
    containment_lines,
    firefighter_dashboard,
)

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])


# returns nearby fires to location based on the long and lat selected by user or gotten via location aswell as environment variables based on coordinates
@router.get(
    "/dashboard",
    response_model=DashboardData,
    responses={404: {"description": "No nearby fires found"}},
)
def get_nearby_fires(
    lat: float, lng: float, radius_km: float = 20, db: Session = Depends(get_db)
):
    try:
        nearby_fires = firefighter_dashboard.get_nearby_fires(db, lat, lng, radius_km)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    try:
        environment_variables = firefighter_dashboard.get_current_environment_vars(
            lat, lng
        )

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {
        "nearby_fires": nearby_fires,
        "environment_variables": environment_variables,
    }


# calculates fire risk still to be implemented


# adds the drawn line to the containment lines table
@router.post(
    "/containment-line",
    response_model=ContainmentLines,
    responses={400: {"description": "fire not near the line"}},
)
def add_containment_line(line: CreateContainmentLine, db: Session = Depends(get_db)):
    try:
        return containment_lines.create_containment_line(db, line.wkt)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get(
    "/containment-lines/{fire_ref}",
    response_model=ContainmentLinesList,
    responses={404: {"description": "Fire not found"}},
)
def get_containment_lines(fire_ref: str, db: Session = Depends(get_db)):
    try:
        return containment_lines.get_lines_for_fire(db, fire_ref)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.delete(
    "/containment-line/{line_id}",
    status_code=204,
    responses={404: {"description": "Containment line not found"}}
)
def remove_containment_line(line_id: str, db: Session = Depends(get_db)):
    try:
        containment_lines.delete_containment_line(db, line_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))