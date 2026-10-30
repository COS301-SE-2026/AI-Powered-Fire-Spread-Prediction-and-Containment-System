from unittest.mock import MagicMock
import pytest

from app.backend.src.services.verification import auto_verification
from app.backend.src.services.verification.auto_verification import (
    AUTO_REJECT,
    AUTO_VERIFY,
    MANUAL_REVIEW,
    auto_verify_report,
)


class TestAutoVerifyReport:
    def test_rejection_check_manual_review_branch(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (False, "manual_review"))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 75.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == MANUAL_REVIEW
        assert reason == "manual_review"
        assert signals["not_rejected"] is False
        assert signals["rejection_reason"] == "manual_review"

    def test_rejection_check_auto_reject_branch(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (False, "outside_geographical_bounds"))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 50.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == AUTO_REJECT
        assert reason == "outside_geographical_bounds"
        assert signals["not_rejected"] is False

    def test_spam_by_rate_auto_reject(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (True, None))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: True)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: ["rep-2", "rep-3"])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 80.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == AUTO_REJECT
        assert reason == "abnormal_rate"
        assert signals["abnormal_rate"] is True

    def test_matching_photos_auto_reject(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (True, None))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: ["photo_match_hash_1"])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: ["rep-2", "rep-3"])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 85.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == AUTO_REJECT
        assert reason == "duplicate_photo"
        assert signals["duplicate_photo_matches"] == ["photo_match_hash_1"]

    def test_corroborated_and_trusted_auto_verify(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (True, None))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: ["rep-2", "rep-3"])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 50.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == AUTO_VERIFY
        assert reason == "corroborated_and_trusted"
        assert len(signals["corroborating_reports"]) == 2
        assert signals["trust_score"] == 50.0

    def test_insufficient_signal_due_to_low_trust_score(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (True, None))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: ["rep-2", "rep-3"])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 49.9)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == MANUAL_REVIEW
        assert reason == "insufficient_signal_for_auto_decision"

    def test_insufficient_signal_due_to_few_corroborators(self, monkeypatch):
        mock_report = MagicMock(user_id="usr-1")
        mock_session = MagicMock()

        monkeypatch.setattr(auto_verification, "rejection_check", lambda r, s: (True, None))
        monkeypatch.setattr(auto_verification, "abnormal_rate", lambda r, s: False)
        monkeypatch.setattr(auto_verification, "duplicate_photo_hash", lambda r, s: [])
        monkeypatch.setattr(auto_verification, "corroborating_reports", lambda r, s: ["rep-2"])
        monkeypatch.setattr(auto_verification, "reporter_trust_score", lambda u, s: 95.0)

        decision, reason, signals = auto_verify_report(mock_report, mock_session)

        assert decision == MANUAL_REVIEW
        assert reason == "insufficient_signal_for_auto_decision"