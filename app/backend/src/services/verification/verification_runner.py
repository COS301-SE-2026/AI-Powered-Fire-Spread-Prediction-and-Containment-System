"""runs auto verification on fire report in background after submission"""

import logging

from app.backend.db import SessionLocal
from app.backend.src.enums.report_status import ReportStatus, status_level
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.services.verification.auto_verification import (
    auto_verify_report,
    AUTO_REJECT,
    AUTO_VERIFY,
    MANUAL_REVIEW,
)
from app.backend.src.services.verification.report_corroboration import (
    corroborating_reports,
)

logger = logging.getLogger(__name__)


def run_verification(report_id: str, _visited: set[str] | None = None) -> None:
    """- opens own db sesacsion
    - refetches report by id
    - runs auto_verification
    - call action based on outcome"""

    visited = _visited if _visited is not None else set()
    if report_id in visited:
        return
    visited.add(report_id)

    db = SessionLocal()
    corroborator_ids: list[str] = []
    try:
        report = db.query(FireReports).filter(FireReports.id == report_id).first()
        if report is None:
            logger.warning("run_verification: report %s not found", report_id)
            return

        decision, reason, signals = auto_verify_report(report, db)

        if decision == AUTO_REJECT:
            report.status = ReportStatus.rejected
            report.system_verified = False
        elif decision == AUTO_VERIFY:
            report.status = ReportStatus.verified
            report.system_verified = True
        else:
            report.status = ReportStatus.pending
            report.system_verified = False

        report.status_index = status_level.get(report.status, 0)
        report.verification_notes = f"{decision}: {reason}"

        db.commit()
        logger.info(
            "Report %s auto-verification decision: %s (%s)", report_id, decision, reason
        )

        if decision in (AUTO_VERIFY, AUTO_REJECT):
            candidates = corroborating_reports(report, db)
            corroborator_ids = [cid for cid in candidates if cid not in visited]
    except Exception:
        logger.exception("run_verification failed for report %s", report_id)
        db.rollback()
    finally:
        db.close()

    for cid in corroborator_ids:
        run_verification(cid, visited)
