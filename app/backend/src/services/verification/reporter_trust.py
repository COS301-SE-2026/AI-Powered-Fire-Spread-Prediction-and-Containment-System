"""Reporter trust scoring - give score to user based on verified reports"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports

# Initial score for user with no repor history
DEFAULT_SCORE = 50.0


def reporter_trust_score(user_id: str | None, session: Session) -> float:
    """Computes a 0-1 trust score based on reports history that were verified. New users or Anonymous users gets default score."""
    if user_id is None:
        return DEFAULT_SCORE

    query = select(FireReports.status).where(
        FireReports.user_id == user_id,
        FireReports.status.in_([ReportStatus.verified, ReportStatus.rejected]),
    )
    result = session.execute(query)
    statuses = [row[0] for row in result.all()]

    if not statuses:
        return DEFAULT_SCORE

    verified_count = sum(1 for status in statuses if status == ReportStatus.verified)
    return (verified_count / len(statuses)) * 100
