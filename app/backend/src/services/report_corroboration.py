""" This checks if 2 fire reports is of the same fire """

from datetime import timedelta

from geoalchemy2.functions import ST_DWithin
from geoalchemy2 import Geography

from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.report_status import ReportStatus
from models.reported_fires import FireReports

WINDOW = timedelta(hours=12)
RADIUS_METERS = 2000

async def corroborating_reports(report: FireReports, session: AsyncSession) -> list[str]:
    """ finds fire reports from other users near this fires location and time. Return list of IDs """

    start_time = report.submitted_at - WINDOW
    end_time = report.submitted_at + WINDOW

    if report.user_id is None:
        return []

    query = select(FireReports.id).where(
        FireReports.user_id != report.user_id,
        FireReports.id != report.id,
        FireReports.status != ReportStatus.rejected,
        FireReports.submitted_at >= start_time,
        FireReports.submitted_at <= end_time,
        ST_DWithin(
            cast(FireReports.location_geom, Geography),
            cast(report.location_geom, Geography),
            RADIUS_METERS,
        ),
    )

    result = await session.execute(query)
    return [row[0] for row in result.all()]