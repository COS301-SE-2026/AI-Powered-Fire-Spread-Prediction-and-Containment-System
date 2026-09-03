from unittest.mock import patch

import pytest

from dependencies.auth import create_access_token
from enums.notification_type import NotificationType
from enums.report_status import ReportStatus
from enums.user_role import UserRole
from enums.severity import Severity
from models.notification import Notification
from src.routes import notifications as notifications_route
from services.notifications import notifications as svc

from conftest import make_report, make_user


@pytest.fixture()
def patched_push():
    """
    Request this only in tests that assert something about push()
    """
    with patch.object(svc, "push") as mock_push:
        yield mock_push


def test_notify_fire_alert_persists_a_real_row(db, patched_push):
    user = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    created = svc.notify_fire_alert(db, fire, "New fire nearby")

    assert len(created) == 1
    row = db.query(Notification).filter_by(user_id=user.id).first()
    assert row is not None
    assert row.type == NotificationType.alert
    patched_push.assert_called_once()


def test_distance_is_computed_from_real_geometry(db):
    user = make_user(db, lat=0.0, lng=0.0)
    fire = make_report(
        db, lat=0.1, lng=0.0, status=ReportStatus.verified, boundary_radius=0.0
    )

    created = svc.notify_fire_alert(db, fire, "New fire nearby")

    assert len(created) == 1
    assert created[0].distance == pytest.approx(11.12, abs=0.1)


def test_user_outside_every_tier_gets_nothing(db):
    make_user(db, lat=0.0, lng=0.0)
    fire = make_report(
        db, lat=10.0, lng=10.0, status=ReportStatus.verified, boundary_radius=0.0
    )

    created = svc.notify_fire_alert(db, fire, "New nearby fire")
    assert created == []
    assert db.query(Notification).count() == 0


def test_user_with_no_location_is_skipped(db):
    make_user(db)
    fire = make_report(db, status=ReportStatus.verified)

    created = svc.notify_fire_alert(db, fire, "New fire nearby")
    assert created == []


def test_unverified_report_notifies_nobody(db):
    make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(db, lat=-25.75, lng=28.24, status=ReportStatus.pending)

    created = svc.notify_fire_alert(db, fire, "New fire nearby")
    assert created == []
    assert db.query(Notification).count() == 0


def test_admin_gets_wider_radius_than_regular_user(db):
    admin = make_user(db, role=UserRole.admin, lat=0.0, lng=0.28)
    regular = make_user(db, role=UserRole.user, lat=0.0, lng=0.28)
    fire = make_report(
        db, lat=0.0, lng=0.0, status=ReportStatus.verified, boundary_radius=0.0
    )

    created = svc.notify_fire_alert(db, fire, "New fire nearby")

    notified_ids = {n.user_id for n in created}
    assert admin.id in notified_ids
    assert regular.id not in notified_ids
    assert regular.id not in notified_ids


def test_severity_reflects_real_boundary_radius(db):
    make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=6.0
    )

    created = svc.notify_fire_alert(db, fire, "New fire nearby")
    assert created[0].severity == Severity.extreme


# check_proximity_for_user
def test_first_time_in_range_persists_an_alery(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    created = svc.check_proximity_for_user(db, user)
    row = db.query(Notification).filter_by(user_id=user.id).first()
    assert row.type == NotificationType.alert


def test_check_proximity_for_user_does_not_duplicate_on_repeat_call(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    first_call = svc.check_proximity_for_user(db, user)
    second_call = svc.check_proximity_for_user(db, user)

    assert len(first_call) == 1
    assert second_call == []
    assert db.query(Notification).filter_by(user_id=user.id).count() == 1


def test_moving_closer_creates_a_real_update_row(db):
    user = make_user(db, lat=0.0, lng=0.0)
    fire = make_report(
        db, lat=0.0, lng=0.15, status=ReportStatus.verified, boundary_radius=0.0
    )

    first_call = svc.check_proximity_for_user(db, user)
    assert len(first_call) == 1
    assert first_call[0].type == NotificationType.alert

    # move user closer to same fire
    user.location_geom = "SRID=4326;POINT(0.148 0.0)"  # ~0.2km from fire now
    db.commit()

    second_call = svc.check_proximity_for_user(db, user)
    assert len(second_call) == 1
    assert second_call[0].type == NotificationType.update

    all_rows = (
        db.query(Notification)
        .filter_by(user_id=user.id)
        .order_by(Notification.time)
        .all()
    )
    assert len(all_rows) == 2
    assert all_rows[0].type == NotificationType.alert
    assert all_rows[1].type == NotificationType.update


def test_only_verified_fires_are_ever_considered(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.pending, boundary_radius=0.0
    )
    make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.rejected, boundary_radius=0.0
    )

    created = svc.check_proximity_for_user(db, user)
    assert created == []


def test_user_with_no_location_short_circuits_before_any_query(db):
    user = make_user(db)
    created = svc.check_proximity_for_user(db, user)
    assert created == []


# notify_fire_update
def test_notifies_everyone_with_an_existing_notification_for_that_fire(
    db, patched_push
):
    user1 = make_user(db, lat=-25.75, lng=28.24)
    user2 = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    svc.notify_fire_alert(db, fire, "New fire nearby")
    patched_push.reset_mock()

    updated = svc.notify_fire_update(db, fire, "Fire contained")

    updated_user_ids = {n.user_id for n in updated}
    assert updated_user_ids == {user1.id, user2.id}
    assert all(n.type == NotificationType.update for n in updated)


def test_user_never_alerted_gets_no_updated(db):
    never_notified = make_user(db, lat=50.0, lng=50.0)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    updated = svc.notify_fire_update(db, fire, "Fire contained")
    assert never_notified.id not in {n.user_id for n in updated}
    assert updated == []


# check_proximity_for_guest
def test_check_proximity_for_guest_persists_nothing(db, patched_push):
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    before = db.query(Notification).count()
    results = svc.check_proximity_for_guest(db, -25.75, 28.24)
    after = db.query(Notification).count()

    assert len(results) == 1
    assert results[0].fireId == fire.id
    assert before == after == 0
    patched_push.assery_not_called()


def test_excludes_fires_beyond_regular_user_tier(db):
    make_report(
        db, lat=0.0, lng=0.28, status=ReportStatus.verified, boundary_radius=0.0
    )

    results = svc.check_proximity_for_guest(db, 0.0, 0.0)
    assert results == []


# mark_notification_read / mark_all_read
def test_mark_motification_read_persists_the_flag(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    [notification] = svc.notify_fire_alert(db, fire, "New fire nearby")
    assert notification.read is False

    svc.mark_notification_read(db, user.id, notification.id)

    refetched = db.query(Notification).filter_by(id=notification.id).first()
    assert refetched.read is True


def test_wrong_user_id_does_not_mark_it_read(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    other_user = make_user(db)

    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )
    [notification] = svc.notify_fire_alert(db, fire, "New fire nearby")

    result = svc.mark_notification_read(db, other_user.id, notification.id)

    assert result is None
    refetched = db.query(Notification).filter_by(id=notification.id).first()
    assert refetched.read is False


def test_mark_all_read_only_affects_that_users_notifications(db):
    user1 = make_user(db, lat=-25.75, lng=28.24)
    user2 = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )

    svc.notify_fire_alert(db, fire, "New fire nearby")
    count = svc.mark_all_read(db, user1.id)

    assert count == 1

    user1_notification = db.query(Notification).filter_by(user_id=user1.id).first()
    user2_notification = db.query(Notification).filter_by(user_id=user2.id).first()

    assert user1_notification.read is True
    assert user2_notification.read is False


@pytest.mark.timeout(5)
def test_websocket_receives_a_real_in_app_notification(db, client):
    import asyncio
    import threading
    from services.notifications.websocket_manager import set_main_loop

    user = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(
        db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
    )
    token = create_access_token({"user_id": user.id})

    def test_get_db():
        yield db

    loop_ready = threading.Event()
    found_loop: list[asyncio.AbstractEventLoop] = []

    async def grab_loop():
        found_loop.append(asyncio.get_running_loop())
        loop_ready.set()

    with patch.object(notifications_route, "get_db", side_effect=test_get_db):
        client.cookies.set("access_token", token)
        with client.websocket_connect("/api/notifications/ws") as websocket:

            client.portal.call(grab_loop)
            assert loop_ready.wait(timeout=2)

            set_main_loop(found_loop[0])

            svc.notify_fire_alert(db, fire, "New fire nearby")
            message = websocket.receive_json()

    assert message["event"] == "notification"
    assert message["data"]["fireId"] == fire.id


def test_websocket_rejects_missing_auth_cookie(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/api/notification/ws"):
            pass


def test_websocket_rejects_invalid_token(client):
    client.cookies.set("access_token", "not-a-real-token")
    with pytest.raises(Exception):
        with client.websocket_connect("/api/notification/ws"):
            pass
