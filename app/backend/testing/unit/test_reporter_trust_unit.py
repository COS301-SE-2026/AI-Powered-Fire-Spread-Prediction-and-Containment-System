from unittest.mock import MagicMock
import pytest

from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.services.verification import reporter_trust
from app.backend.src.services.verification.reporter_trust import (
    DEFAULT_SCORE,
    reporter_trust_score,
    trust_score_from_counts,
    reporter_report_counts,
)


class TestReporterTrustScore:
    def test_user_id_none_returns_default_score(self):
        mock_session = MagicMock()
        score = reporter_trust_score(None, mock_session)
        assert score == DEFAULT_SCORE
        mock_session.execute.assert_not_called()

    def test_no_reports_history_returns_default_score(self):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        score = reporter_trust_score("user-1", mock_session)
        assert score == DEFAULT_SCORE

    def test_reports_with_verified_and_rejected(self):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (ReportStatus.verified,),
            (ReportStatus.verified,),
            (ReportStatus.rejected,),
            (ReportStatus.verified,),
        ]
        mock_session.execute.return_value = mock_result

        score = reporter_trust_score("user-1", mock_session)
        assert score == 75.0

    def test_trust_score_from_counts_fallback_to_default_score(self, monkeypatch):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [(ReportStatus.verified,)]
        mock_session.execute.return_value = mock_result

        monkeypatch.setattr(reporter_trust, "trust_score_from_counts", lambda v, r: None)

        score = reporter_trust_score("user-1", mock_session)
        assert score == DEFAULT_SCORE


class TestTrustScoreFromCounts:
    def test_zero_total_returns_none(self):
        assert trust_score_from_counts(0, 0) is None

    def test_all_verified(self):
        assert trust_score_from_counts(5, 0) == 100.0

    def test_all_rejected(self):
        assert trust_score_from_counts(0, 4) == 0.0

    def test_mixed_counts(self):
        assert trust_score_from_counts(1, 3) == 25.0


class TestReporterReportCounts:
    def test_empty_user_ids_returns_empty_dict(self):
        mock_session = MagicMock()
        counts = reporter_report_counts([], mock_session)
        assert counts == {}
        mock_session.execute.assert_not_called()

    def test_multiple_users_counts_aggregation(self):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("user-1", ReportStatus.verified),
            ("user-1", ReportStatus.rejected),
            ("user-1", ReportStatus.verified),
            ("user-2", ReportStatus.rejected),
        ]
        mock_session.execute.return_value = mock_result

        user_ids = ["user-1", "user-2", "user-3"]
        counts = reporter_report_counts(user_ids, mock_session)

        assert counts == {
            "user-1": (2, 1),
            "user-2": (0, 1),
            "user-3": (0, 0),
        }