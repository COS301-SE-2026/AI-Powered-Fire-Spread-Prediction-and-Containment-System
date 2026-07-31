import uuid
from datetime import datetime, timezone

from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_ClosestPoint, ST_Distance, ST_GeomFromText
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy.orm import Session

from models.containment_lines import ContainmentLines
from models.reported_fires import FireReports

MAX_RADIUS = 2  # max radius for containement auto-detection of nearby fire


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
