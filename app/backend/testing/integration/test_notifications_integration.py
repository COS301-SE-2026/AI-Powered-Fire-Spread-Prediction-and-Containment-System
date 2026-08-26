from unittest.mock import patch

import pytest

from enums.notification_type import NotificationType
from enums.report_status import ReportStatus
from enums.user_role import UserRole
from models.notification import  Notification
from services.notifications  import notifications as svc

from conftest import make_report, make_user

@pytest.fixture(autouse=True)
def patched_push():
    with patch.object(svc, "push") as mock_push:
        yield mock_push
        
def test_notify_fire_alert_persists_a_real_row(db, patched_push):
    user = make_user(db, lat=-25.75, lng=28.24)
    fire = make_report(db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0)
    
    created = svc.notify_fire_alert(db, fire, "New fire nearby")
    
    assert len(created) == 1
    row = db.query(Notification).filter_by(user_id=user.id).first()
    assert row is not None
    assert row.type == NotificationType.alert
    patched_push.assert_called_once()
    
def test_check_proximity_for_user_does_not_duplicate_on_repeat_call(db):
    user = make_user(db, lat=-25.75, lng=28.24)
    make_report(db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0)
    
    first_call = svc.check_proximity_for_user(db, user)
    second_call = svc.check_proximity_for_user(db, user)
    
    assert len(first_call) == 1
    assert second_call == []
    assert db.query(Notification).filter_by(user_id=user.id).count() == 1
    
def test_admin_gets_wider_radius_than_regular_user(db):
    admin = make_user(db, role=UserRole.admin, lat=0.0, lng=0.28)
    regular = make_user(db, role=UserRole.user, lat=0.0, lng=0.28)
    fire = make_report(db, lat=0.0, lng=0.0, status=ReportStatus.verified, boundary_radius=0.0)
    
    created = svc.notify_fire_alert(db, fire,"New fire nearby")
    
    notified_ids = {n.user_id for n in created}
    assert admin.id in notified_ids
    assert regular.id not in notified_ids
    assert regular.id not in notified_ids
    
def test_check_proximity_for_guest_persists_nothing(db, patched_push):
    make_report(db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0)
    
    before = db.query(Notification).count()
    results = svc.check_proximity_for_guest(db, -25.75, 28.24)
    after = db.query(Notification).count()
    
    assert len(results) == 1
    assert before == after == 0
    patched_push.assery_not_called()