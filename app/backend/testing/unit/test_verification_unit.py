"""unit tests for report verification"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from enums.report_status import ReportStatus
from services.verification.rejection_checks import on_land, LocationCheckUnavailable
from services.verification.verification_runner import run_verification
from services.verification.auto_verification import (
    AUTO_REJECT,
    AUTO_VERIFY,
    MANUAL_REVIEW,
)


# on_land
@patch("services.verification.rejection_checks.httpx.get")
def test_on_land_no_water_returns_true(mock_get):
    """no water response means its on land"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"features": []}
    mock_get.return_value = mock_response

    assert on_land(-25.7479, 28.2293) is True


@patch("services.verification.rejection_checks.httpx.get")
def test_on_land_water_returns_false(mock_get):
    """water response means its in water"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"features": [{"id": "water.1"}]}
    mock_get.return_value = mock_response

    assert on_land(-25.7479, 28.2293) is False


@patch("services.verification.rejection_checks.httpx.get")
def test_on_land_http_error_location_check_unavailable(mock_get):
    """network/HTTP failure should show LocationCheckUnavailable"""
    mock_get.side_effect = httpx.ConnectError("connection failed")

    with pytest.raises(LocationCheckUnavailable):
        on_land(-25.7479, 28.2293)


# run_verification
@patch("services.verification.verification_runner.auto_verify_report")
@patch("services.verification.verification_runner.SessionLocal")
def test_run_verification_auto_reject_sets_status(mock_session_local, mock_auto_verify):
    """AUTO_REJECT should set report status to rejected and system_verified False"""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_report = MagicMock(id="report-1")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_report
    mock_auto_verify.return_value = (AUTO_REJECT, "outside_boundary", {})

    run_verification("report-1")

    assert mock_report.status == ReportStatus.rejected
    assert mock_report.system_verified is False
    mock_db.commit.assert_called_once()


@patch("services.verification.verification_runner.auto_verify_report")
@patch("services.verification.verification_runner.SessionLocal")
def test_run_verification_auto_verify_sets_status(mock_session_local, mock_auto_verify):
    """AUTO VERIFY should set report status to verified and system_verified True"""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_report = MagicMock(id="report-2")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_report
    mock_auto_verify.return_value = (AUTO_VERIFY, "corroborated_and_trusted", {})

    run_verification("report-2")

    assert mock_report.status == ReportStatus.verified
    assert mock_report.system_verified is True


@patch("services.verification.verification_runner.auto_verify_report")
@patch("services.verification.verification_runner.SessionLocal")
def test_run_verification_manual_review_sets_pending_status(
    mock_session_local, mock_auto_verify
):
    """MANUAL_REVIEW decision should set report status to pending and system_verified False"""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_report = MagicMock(id="report-4")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_report
    mock_auto_verify.return_value = (
        MANUAL_REVIEW,
        "insufficient_signal_for_auto_decision",
        {},
    )

    run_verification("report-4")

    assert mock_report.status == ReportStatus.pending
    assert mock_report.system_verified is False


@patch("services.verification.verification_runner.SessionLocal")
def test_run_verification_report_not_found_does_not_commit(mock_session_local):
    """If the report no longer exists, run_verification should exit quietly without committing"""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None

    run_verification("missing-report")

    mock_db.commit.assert_not_called()


@patch("services.verification.verification_runner.auto_verify_report")
@patch("services.verification.verification_runner.SessionLocal")
def test_run_verification_exception_rolls_back(mock_session_local, mock_auto_verify):
    """If auto_verify_report raises, run_verification should roll back instead of committing"""
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_report = MagicMock(id="report-3")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_report
    mock_auto_verify.side_effect = RuntimeError("boom")

    run_verification("report-3")

    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()
