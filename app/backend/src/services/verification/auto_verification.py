"""Combine rejection checks, corroboration, spam detection, reporter trust score  for auto-verification"""

from sqlalchemy.orm import Session

from models.reported_fires import FireReports
from services.verification.rejection_checks import rejection_check
from services.verification.report_corroboration import corroborating_reports
from services.verification.report_spam_detection import (
    abnormal_rate,
    duplicate_photo_hash,
)
from services.verification.reporter_trust import reporter_trust_score

# Tresholds
MIN_CORROBORATING_REPORTS = 3
MIN_TRUST_SCORE = 50.0

# possible outcomes
AUTO_REJECT = "auto_reject"
AUTO_VERIFY = "auto_verify"
MANUAL_REVIEW = "manual_review"


def auto_verify_report(report: FireReports, session: Session) -> tuple[str, str, dict]:
    """Runs verification signals on reports and return (decision, reason, signals)
    - decision: AUTO_REJECT, AUTO_VERIFY, MANUAL_REVIEW
    - reason: machine readable explanation
    - signals: dict of raw signal values"""

    not_rejected, rejection_reason = rejection_check(report, session)
    spam_by_rate = abnormal_rate(report, session)
    matching_photos = duplicate_photo_hash(report, session)
    corroborators = corroborating_reports(report, session)
    trust_score = reporter_trust_score(report.user_id, session)

    signals = {
        "not_rejected": not_rejected,
        "rejection_reason": rejection_reason,
        "abnormal_rate": spam_by_rate,
        "duplicate_photo_matches": matching_photos,
        "corroborating_reports": corroborators,
        "trust_score": trust_score,
    }

    if not not_rejected:
        if rejection_reason == "manual_review":
            return MANUAL_REVIEW, rejection_reason, signals
        return AUTO_REJECT, rejection_reason, signals

    if spam_by_rate:
        return AUTO_REJECT, "abnormal_rate", signals

    if matching_photos:
        return AUTO_REJECT, "duplicate_photo", signals

    if (
        len(corroborators) >= MIN_CORROBORATING_REPORTS
        and trust_score >= MIN_TRUST_SCORE
    ):
        return AUTO_VERIFY, "corroborated_and_trusted", signals

    return MANUAL_REVIEW, "insufficient_signal_for_auto_decision", signals
