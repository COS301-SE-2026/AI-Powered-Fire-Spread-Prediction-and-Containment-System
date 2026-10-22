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
    score = trust_score_from_counts(verified_count, len(statuses) - verified_count)
    if score is None:
        return DEFAULT_SCORE
    return score

# for displaying the admin reporter score
def trust_score_from_counts(verified: int, rejected: int) -> float | None:
    """Compute a 0-1 trust score from report counts"""

    total = verified + rejected
    if total == 0:
        return None 
    return (verified / total) * 100

def reporter_report_counts(user_ids: list[str], session: Session) -> dict[str, tuple[int, int]]:
    """Counts each user's verified and rejected reports in a single query."""
    counts = {user_id: (0, 0) for user_id in user_ids}
    if not user_ids: 
        return counts
    
    query = select(FireReports.user_id, FireReports.status).where(
        FireReports.user_id.in_(user_ids),
        FireReports.status.in_([ReportStatus.verified, ReportStatus.rejected]),
    )

    for user_id, status in session.execute(query).all():
        verified, rejected = counts[user_id]
        if status == ReportStatus.verified:
            counts[user_id] = (verified + 1, rejected)
        else:
            counts[user_id] = (verified, rejected + 1)
    return counts