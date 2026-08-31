"""Flags reuse photos & abnormally fast submission rates from a single user"""

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from enums.report_status import ReportStatus
from models.reported_fires import FireReports

WINDOW = timedelta(hours=1)
MAX_REPORTS = 3


def abnormal_rate(report: FireReports, session: Session) -> bool:
    """Checks if user has submitted more than MAX_REPORTS within WINDOW"""
    if report.user_id is None:
        return False

    start = report.submitted_at - WINDOW

    query = (
        select(func.count())
        .select_from(FireReports)
        .where(
            FireReports.user_id == report.user_id,
            FireReports.submitted_at >= start,
            FireReports.submitted_at <= report.submitted_at,
        )
    )
    result = session.execute(query)
    count = result.scalar_one()
    return count > MAX_REPORTS


def duplicate_photo_hash(report: FireReports, session: Session) -> list[str]:
    """Find users that used same exact photo. Returns IDs of matching reports"""

    if not report.photo_hash:
        return []

    query = select(FireReports.id).where(
        FireReports.photo_hash == report.photo_hash,
        FireReports.user_id != report.user_id,
        FireReports.id != report.id,
        FireReports.status != ReportStatus.rejected,
    )

    result = session.execute(query)
    return [row[0] for row in result.all()]
