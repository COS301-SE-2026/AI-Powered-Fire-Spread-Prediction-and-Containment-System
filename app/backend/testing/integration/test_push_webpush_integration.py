import json 
from unittest.mock import patch

import pytest

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.notification import Notification
from app.backend.src.services.notifications import notifications as svc
from app.backend.src.services.notifications import push_webpush

from conftest import make_report, make_user

SUBSCRIPTION = {
    "endpoint": "https://fcm.googleapis.com/fmc/send/aabc123",
    "keys": {"p256dh": "p256dh-key", "auth": "auth-key"},
}

@pytest.fixture(autouse=True)
def vapid_configured():
    """
    Every test gets a "server has VAPID keys" backend so register/send go through
    their happy path unless test explicitly overrides this to test the unconfigured case
    """
    with patch.object(
        push_webpush, "VAPID_PRIVATE_KEY_PATH", "/tmp/fake_private_key.pem"
    ), patch.object(push_webpush, "VAPID_CLAIM_SUB", "mailto:test@example.com"):
        yield
        
def auth_cookie(client, user):
    token = create_access_token({"user_id": user.id})
    client.cookies.set("access_token", token)
    
class TestPushRegisterRoute:
    def test_register_persists_subscription_for_authenticated_user(self, db, client):
        user = make_user(db, role="user")
        auth_cookie(client, user)
        
        response = client.post("/api/notifications/push/register", json=SUBSCRIPTION)
        
        assert response.status_code == 200
        assert response.json() == {"registered": True}
        db.refresh(user)
        assert json.loads(user.push_subscription) == SUBSCRIPTION
        
    def test_register_without_auth_cookie_is_rejected(self, client):
        response = client.post("/api/notifications/push/register", json=SUBSCRIPTION)
        
        assert response.status_code == 401
        
    def test_register_returns_false_when_server_has_no_vapid_keys(self, db, client):
        user = make_user(db, role="user")
        auth_cookie(client, user)
        
        with patch.object(push_webpush, "VAPID_PRIVATE_KEY_PATH", None):
            response = client.post("/api/notifications/push/register", json=SUBSCRIPTION)
            
        assert response.status_code == 200
        assert response.json() == {"registered": False}
        db.refresh(user)
        assert user.push_subscription is None
        
    def test_register_rejects_malformed_subscription_body(self, db, client):
        user = make_user(db, role="user")
        auth_cookie(client, user)
        
        response = client.post(
            "/api/notifications/push/register", json={"endpoint": "https://example.com"}
        )
        
        assert response.status_code == 422
        
class TestPushUnregisterRoute:
    def test_unregister_clears_a_real_subscription(self, db, client):
        user = make_user(db, role="user")
        auth_cookie(client, user)
        client.post("/api/notifications/push/register", json=SUBSCRIPTION)
        db.refresh(user)
        assert user.push_subscription is not None
        
        response = client.delete("/api/notifications/push")
        
        assert response.status_code == 200
        assert response.json() == {"registered": False}
        db.refresh(user)
        assert user.push_subscription is None
        
    def test_unregister_without_auth_cookie_is_rejected(self, client):
        response = client.delete("/api/notifications/push")
        
        assert response.status_code == 401

class TestPushFiresThroughRealNotificationWiring:
    def test_notify_fire_alert_delivers_push_to_a_subscribed_user(self, db):
        user = make_user(db, lat=-25.75, lng=28.24, role="user")
        user.push_subscription = json.dumps(SUBSCRIPTION)
        db.commit()
        
        fire = make_report(
            db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
        )
        
        with patch.object(push_webpush, "webpush") as mock_webpush:
            created = svc.notify_fire_alert(db, fire, "New fire nearby")
            
        assert len(created) == 1
        row = db.query(Notification).filter_by(user_id=user.id).first()
        assert row is not None
        
        mock_webpush.assert_called_once()
        _, kwargs = mock_webpush.call_args
        assert kwargs["subscription_info"] == SUBSCRIPTION
        assert kwargs["vapid_private_key"] == "/tmp/fake_private_key.pem"
        payload = json.loads(kwargs["data"])
        assert payload["title"] == "Fire Alert"
        
    def test_notify_fire_alert_skips_push_for_unsubscribed_user(self, db):
        user = make_user(db, lat=-25.75, lng=28.24, role="user")
        fire = make_report(
            db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
        )
        
        with patch.object(push_webpush, "webpush") as mock_webpush:
            created = svc.notify_fire_alert(db, fire, "New fire nearby")
            
        assert len(created) == 1
        mock_webpush.assert_not_called()
        
    def test_notify_fire_alert_clears_subscription_on_410_gone(self, db):
        from pywebpush import WebPushException
        from unittest.mock import MagicMock
        
        user = make_user(db, lat=-25.75, lng=28.24, role="user")
        user.push_subscription = json.dumps(SUBSCRIPTION)
        db.commit()
        
        fire = make_report(
            db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
        )
        
        fake_response = MagicMock(status_code=410)
        with patch.object(
            push_webpush,
            "webpush",
            side_effect=WebPushException("gone", response=fake_response),
        ):
            svc.notify_fire_alert(db, fire, "New fire nearby")
            
        db.refresh(user)
        assert user.push_subscription is None
        
class TestGuestsNeverTriggerPush:
    def test_guest_nearby_fires_creates_no_notification_row_and_no_push(self, db, client):
        fire = make_report(
            db, lat=-25.75, lng=28.24, status=ReportStatus.verified, boundary_radius=0.0
        )
        
        with patch.object(push_webpush, "webpush") as mock_webpush:
            response = client.post(
                "/api/guests/nearby-fires",
                json={"latitude": -25.75, "longitude": 28.24},
            )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert db.query(Notification).count() == 0
        mock_webpush.assert_not_called()
        