"""This checks if 2 fire reports is of the same fire"""

from datetime import timedelta

from geoalchemy2.functions import ST_DWithin
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape

from sqlalchemy import cast, select
from sqlalchemy.orm import Session

from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports

WINDOW = timedelta(hours=12)
RADIUS_METERS = 2000


# anonymous reports can never corroborate another report(no identity) they can receive corroboration from other registered user
def corroborating_reports(report: FireReports, session: Session) -> list[str]:
    """finds fire reports from other users near this fires location and time. Return list of IDs"""

    start_time = report.submitted_at - WINDOW
    end_time = report.submitted_at + WINDOW

    report_point_wkt = f"SRID=4326;{to_shape(report.location_geom).wkt}"

    identity = (
        True
        if report.user_id is None
        else FireReports.user_id != report.user_id
    )

    query = select(FireReports.id).where(
        identity,
        FireReports.id != report.id,
        FireReports.status != ReportStatus.rejected,
        FireReports.submitted_at >= start_time,
        FireReports.submitted_at <= end_time,
        ST_DWithin(
            cast(FireReports.location_geom, Geography),
            cast(report_point_wkt, Geography),
            RADIUS_METERS,
        ),
    )

    result = session.execute(query)
    return [row[0] for row in result.all()]
