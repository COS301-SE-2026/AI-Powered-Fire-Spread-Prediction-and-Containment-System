import uuid
import asyncio
import numpy as np
from datetime import datetime, timezone

from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_ClosestPoint, ST_Distance, ST_GeomFromText
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.backend.src.models.containment_lines import ContainmentLines
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.ai.simulation_api import simulate_single_fire
from app.backend.src.ai.suggest_containment import suggest_containment_line
from app.backend.src.schemas.containment_lines import (
    SuggestedContainmentLine,
    SuggestedContainmentLinesList,
)
MAX_RADIUS = 5  # max radius for containement auto-detection of nearby fire
SUGGESTION_HORIZON_STEPS = 288 #72h as in dca.py

# gets the containment lines
def get_all_containment_lines(db: Session):
    request = db.query(ContainmentLines).all()

    return request


# finds the nearest fire to the drawn containment line
def find_nearest_fire(db: Session, line_geom: str):
    # gets the fires ordered by nearest fire in terms of distance
    request = (
        db.query(
            FireReports,
            ST_Distance(
                FireReports.location_geom.cast(Geography),
                ST_GeomFromText(line_geom, 4326).cast(Geography),
            ).label("dist"),
        )
        .filter(FireReports.status == ReportStatus.verified)
        .order_by("dist")
        .first()
    )

    if not request:
        return None
    fire, dist_m = request

    if dist_m > MAX_RADIUS * 1000:
        raise ValueError("No fires within in radius of drawn lines search")

    return fire


def create_containment_line(db: Session, wkt: str):
    fire = find_nearest_fire(db, wkt)

    if fire is None:
        raise ValueError("No fires nearby the drawn line")

    new_line = ContainmentLines(
        id=str(uuid.uuid4()),
        fire_report_id=fire.id,
        line_geom=wkt,
        drawn_at=datetime.now(timezone.utc),
    )

    db.add(new_line)
    db.commit()
    db.refresh(new_line)
    new_line.line_geom = to_shape(new_line.line_geom).wkt
    return new_line

def get_lines_for_fire(db: Session, fire_ref: str):
    fire = (
        db.query(FireReports.id)
        .filter(FireReports.reference_number == fire_ref)
        .first()
    )

    if fire is None:
        raise ValueError(f"Fire {fire_ref} not found")

    rows = (
        db.query(
            ContainmentLines.id,
            ContainmentLines.fire_report_id,
            func.ST_AsText(ContainmentLines.line_geom).label("line_geom"),
            ContainmentLines.drawn_at
        )
        .filter(ContainmentLines.fire_report_id == fire.id)
        .order_by(ContainmentLines.drawn_at)
        .all()
    )

    return {"data": rows, "total": len(rows)}

def delete_containment_line(db: Session, line_id: str):
    line = (
        db.query(ContainmentLines)
        .filter(ContainmentLines.id == line_id)
        .first()
    )

    if line is None:
        raise ValueError(f"ContainmentLines line {line_id} not found")

    db.delete(line)
    db.commit()

async def get_suggested_containment_lines(
    db: Session, fire_ref: str, top_n: int = 1
) -> SuggestedContainmentLinesList:
    fire = (
        db.query(
            FireReports.id,
            FireReports.reference_number,
            func.ST_Y(FireReports.location_geom).label("lat"),
            func.ST_X(FireReports.location_geom).label("lng"),
            FireReports.boundary_radius,
        )
        .filter(
            FireReports.reference_number == fire_ref,
            FireReports.status == ReportStatus.verified,
        )
        .first()
    )
    
    if fire is None:
        raise ValueError(f"Verified fire {fire_ref} not found")

    existing_wkts = [row.line_geom for row in get_lines_for_fire(db, fire_ref)["data"]]

    semaphore = asyncio.Semaphore(1)
    prediction = await simulate_single_fire(
        fire, SUGGESTION_HORIZON_STEPS, semaphore, existing_wkts
    )

    history = [
        np.array(tick, dtype=np.int64).reshape(prediction.grid_h, prediction.grid_w)
        for tick in prediction.history
    ]
    suggestions = suggest_containment_line(
        history=history,
        fire_lat=fire.lat,
        fire_lng=fire.lng,
        boundary_radius_m=float(fire.boundary_radius) * 1000,
        cell_size_m=prediction.cell_size_m,
        n_steps=SUGGESTION_HORIZON_STEPS,
        top_n=top_n,
    )
    return SuggestedContainmentLinesList(
        data=[SuggestedContainmentLine(**s.__dict__) for s in suggestions],
        total=len(suggestions),
    )