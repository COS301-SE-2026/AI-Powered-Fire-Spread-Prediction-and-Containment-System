"""Integration tests for report verification testing against test db"""

from datetime import datetime, timedelta, timezone

import pytest
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.services.verification.rejection_checks import (
    rejection_check,
    valid_location,
    within_boundary,
    valid_timestamp,
    required_fields_present,
    duplicate_submission,
)

from app.backend.src.services.verification.report_corroboration import (
    corroborating_reports,
)
from app.backend.src.services.verification.report_spam_detection import (
    abnormal_rate,
    duplicate_photo_hash,
)

from app.backend.src.services.verification.reporter_trust import reporter_trust_score

from app.backend.src.services.verification.auto_verification import (
    auto_verify_report,
    AUTO_REJECT,
    AUTO_VERIFY,
    MANUAL_REVIEW,
)

from conftest import make_user, make_report

PRETORIA_LAT = -25.7479
PRETORIA_LNG = 28.2293

# outside AREA_BOUNDS
OUTSIDE_BOUNDARY_LAT = -25.0
OUTSIDE_BOUNDARY_LNG = 45.0


# valid_location tests
def test_valid_location_zeros_return_false():
    """Test (0, 0) that it shouldn't be valid"""
    assert valid_location(0.0, 0.0) is False


def test_valid_location_within_boundary_return_true():
    """Test valid coordinates inside the boundary it should be True"""
    assert valid_location(PRETORIA_LAT, PRETORIA_LNG) is True


# within_boundary tests
def test_within_boundary_invalid_coordinates_return_false():
    """Test coordinates outside the SA boundary it should be false"""
    assert within_boundary(OUTSIDE_BOUNDARY_LAT, OUTSIDE_BOUNDARY_LNG) is False


def test_location_within_boundary_return_true():
    """Test coordinates inside the SA boundary it should be True"""
    assert within_boundary(PRETORIA_LAT, PRETORIA_LNG) is True


# valid_timestamp tests
def test_valid_timestamp_future_returns_false():
    """Timestamp in future is not valid"""
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    assert valid_timestamp(future) is False


def test_valid_timestamp_older_than_report_duration_returns_false():
    """Timestamp older than max report duration should be rejected as stale"""
    old = datetime.now(timezone.utc) - timedelta(days=8)
    assert valid_timestamp(old) is False


def test_valid_timestamp_recent_returns_True():
    """Timestamp in within acceptable window is valid"""
    recent = datetime.now(timezone.utc) - timedelta(hours=2)
    assert valid_timestamp(recent) is True


# required_fields_present
def test_required_fields_present_complete_return_true(db):
    """report with every required field should pass the check"""
    user = make_user(db)
    report = make_report(db, user=user)
    assert required_fields_present(report) is True


def test_required_fields_present_missing_photo_return_false(db):
    """report with no image_url should fail the required-fields check"""
    user = make_user(db)
    report = make_report(db, user=user, image_url=None)
    assert required_fields_present(report) is False


# duplicate_submission
def test_duplicate_submission_same_user_returns_true(db):
    """Same user reporting fire again nearby and soon after counts as a duplicat"""
    user = make_user(db)
    make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    second = make_report(
        db, user=user, lat=PRETORIA_LAT + 0.001, lng=PRETORIA_LNG + 0.001
    )

    assert duplicate_submission(second, db) is True


def test_duplicate_submission_different_users_returns_false(db):
    """2 different users reportin the same location should not counts as a duplicates"""
    user_a = make_user(db, email="a@example.com")
    user_b = make_user(db, email="b@example.com")
    make_report(db, user=user_a, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    report_b = make_report(db, user=user_b, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    assert duplicate_submission(report_b, db) is False


def test_duplicate_submission_outside_window_returns_false(db):
    """report from same user outside window should not match"""
    user = make_user(db)
    old_time = datetime.now(timezone.utc) - timedelta(hours=12)
    make_report(
        db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG, submitted_at=old_time
    )
    recent = make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    assert duplicate_submission(recent, db) is False


# rejection_check
def test_rejection_clean_report_return_true(db):
    """report with no issue should pass all checks"""
    user = make_user(db)
    report = make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    passed, reason = rejection_check(report, db)
    assert passed is True
    assert reason is None


def test_rejection_outside_boundary_fails_with_reason_return_False(db):
    """report outside the boundary should fail with outside_boundary reason"""
    user = make_user(db)
    report = make_report(
        db, user=user, lat=OUTSIDE_BOUNDARY_LAT, lng=OUTSIDE_BOUNDARY_LNG
    )

    passed, reason = rejection_check(report, db)
    assert passed is False
    assert reason == "outside_boundary"


# corroborating_report
def test_corroborating_report_nearby_report_matches(db):
    """Nearby report from other user matches and should count as corroboration"""
    reporter = make_user(db, email="reporter@example.com")
    other_a = make_user(db, email="other_a@example.com")
    other_b = make_user(db, email="other_b@example.com")

    make_report(db, user=other_a, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    make_report(db, user=other_b, lat=PRETORIA_LAT + 0.001, lng=PRETORIA_LNG + 0.001)
    this_report = make_report(db, user=reporter, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    matches = corroborating_reports(this_report, db)
    assert len(matches) == 2


def test_corroborating_reports_anonymous_reporter_corroboration(db):
    """Anonymous report are able to receive corroboration from identified users"""
    other_a = make_user(db, email="other_a@example.com")
    other_b = make_user(db, email="other_b@example.com")
    make_report(db, user=other_a, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    make_report(db, user=other_b, lat=PRETORIA_LAT + 0.001, lng=PRETORIA_LNG + 0.001)
    anon_report = make_report(db, user=None, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    matches = corroborating_reports(anon_report, db)
    assert len(matches) == 2


def test_corroborating_reports_anonymous_dont_corroborate(db):
    """other anonymous reports shouldnt count as corroborators"""
    reporter = make_user(db, email="reporter3@example.com")
    make_report(db, user=None, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    this_report = make_report(db, user=reporter, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    matches = corroborating_reports(this_report, db)
    assert matches == []


def test_corroborating_report_same_user_return_false(db):
    """report from same user shouldnt corroborate"""
    user = make_user(db)
    make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    this_report = make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    matches = corroborating_reports(this_report, db)
    assert matches == []


def test_corroborating_reports_outside_radius_returns_empty(db):
    """outside corroboration radius should not count as a corroboration"""
    reporter = make_user(db, email="reporter2@example.com")
    other = make_user(db, email="other@example.com")
    make_report(db, user=other, lat=PRETORIA_LAT + 0.5, lng=PRETORIA_LNG + 0.5)
    this_report = make_report(db, user=reporter, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    matches = corroborating_reports(this_report, db)
    assert matches == []


# abnormal_rate
def test_abnormal_rate_under_treshold_return_false(db):
    """a single report from user shouldnt be true for rate limmit"""
    user = make_user(db)
    report = make_report(db, user=user)
    assert abnormal_rate(report, db) is False


def test_abnormal_rate_over_treshold_return_true(db):
    """more than rate limmit max should trigger signal"""
    user = make_user(db)
    now = datetime.now(timezone.utc)
    for _ in range(4):
        make_report(db, user=user, submitted_at=now)
    latest = make_report(db, user=user, submitted_at=now)

    assert abnormal_rate(latest, db) is True


# duplicate_photo_hash
def test_duplicate_photo_hash_true_returns_hash(db):
    """2 different users submitting sam photo hash should be the same"""
    user_a = make_user(db, email="photo_a@example.com")
    user_b = make_user(db, email="photo_b@example.com")
    shared_hash = "a" * 64

    make_report(db, user=user_a, photo_hash=shared_hash)
    report_b = make_report(db, user=user_b, photo_hash=shared_hash)

    matches = duplicate_photo_hash(report_b, db)
    assert len(matches) == 1


def test_duplicate_photo_hash_no_hash_return_empty(db):
    """a photo thats not duplicate should not match hash"""
    user = make_user(db)
    report = make_report(db, user=user, photo_hash=None)
    assert duplicate_photo_hash(report, db) == []


# reporter_trust_score
def test_reporter_trust_score_new_user(db):
    """new user should get default score"""
    user = make_user(db)
    assert reporter_trust_score(user.id, db) == 50.0


def test_reporter_trust_score_anon(db):
    """new anonymous reporter should get default score"""
    assert reporter_trust_score(None, db) == 50.0


def test_reporter_trust_history_returns_ratio(db):
    """the score of the amount of reports rejected/verified should be correct"""
    user = make_user(db)
    make_report(db, user=user, status=ReportStatus.verified)
    make_report(db, user=user, status=ReportStatus.verified)
    make_report(db, user=user, status=ReportStatus.verified)
    make_report(db, user=user, status=ReportStatus.rejected)

    assert reporter_trust_score(user.id, db) == 75.0


# auto_verify_report
def test_auto_verify_report_failed_rejection_check(db):
    """a report that failed a rejection_check should be auto-rejected with that reason"""
    user = make_user(db)
    report = make_report(
        db, user=user, lat=OUTSIDE_BOUNDARY_LAT, lng=OUTSIDE_BOUNDARY_LNG
    )

    decision, reason, signals = auto_verify_report(report, db)
    assert decision == AUTO_REJECT
    assert reason == "outside_boundary"


def test_auto_verify_report_duplicate_photo_returns_auto_reject(db):
    """A report matching another user's photo hash should be auto-rejected."""
    user_a = make_user(db, email="dup_a@example.com")
    user_b = make_user(db, email="dup_b@example.com")
    shared_hash = "b" * 64

    make_report(db, user=user_a, photo_hash=shared_hash)
    report_b = make_report(db, user=user_b, photo_hash=shared_hash)

    decision, reason, signals = auto_verify_report(report_b, db)
    assert decision == AUTO_REJECT
    assert reason == "duplicate_photo"


def test_auto_verify_report_isolated_report_returns_manual_review(db):
    """A clean report with no corroboration yet should fall to manual review."""
    user = make_user(db)
    report = make_report(db, user=user, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    decision, reason, signals = auto_verify_report(report, db)
    assert decision == MANUAL_REVIEW
    assert reason == "insufficient_signal_for_auto_decision"


def test_auto_verify_report_corroborated_and_trusted_returns_auto_verify(db):
    """Enough corroborators plus a sufficient trust score should auto-verify the report."""
    reporter = make_user(db, email="trusted_reporter@example.com")
    old_time = datetime.now(timezone.utc) - timedelta(days=30)
    make_report(db, user=reporter, status=ReportStatus.verified, submitted_at=old_time)
    make_report(db, user=reporter, status=ReportStatus.verified, submitted_at=old_time)
    make_report(db, user=reporter, status=ReportStatus.verified, submitted_at=old_time)

    other_a = make_user(db, email="corrob_a@example.com")
    other_b = make_user(db, email="corrob_b@example.com")
    other_c = make_user(db, email="corrob_c@example.com")
    make_report(db, user=other_a, lat=PRETORIA_LAT, lng=PRETORIA_LNG)
    make_report(db, user=other_b, lat=PRETORIA_LAT + 0.001, lng=PRETORIA_LNG + 0.001)
    make_report(db, user=other_c, lat=PRETORIA_LAT - 0.001, lng=PRETORIA_LNG - 0.001)

    report = make_report(db, user=reporter, lat=PRETORIA_LAT, lng=PRETORIA_LNG)

    decision, reason, signals = auto_verify_report(report, db)
    assert decision == AUTO_VERIFY
    assert reason == "corroborated_and_trusted"
