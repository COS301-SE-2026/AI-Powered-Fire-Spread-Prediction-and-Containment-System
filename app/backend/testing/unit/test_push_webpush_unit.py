import json
from unittest.mock import MagicMock, patch

import pytest
from pywebpush import WebPushException

from app.backend.src.enums.notification_type import NotificationType
from app.backend.src.enums.severity import Severity
from app.backend.src.services.notifications import push_webpush as svc

SUBSCRIPTION = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/abc123",
    "keys": {"p256dh": "p256dh-key", "auth": "auth-key"},
}

def make_user(push_subscription=None):
    user = MagicMock()
    user.id = "u1"
    user.push_subscription = json.dumps(push_subscription) if push_subscription else None
    return user

def make_notification():
    n = MagicMock()
    n.id = "n1"
    n.fire_report_id = "f1"
    n.user_id = "u1"
    n.message = "Fire is 3.0km away"
    n.type = NotificationType.alert
    n.severity = Severity.high
    return n

@pytest.fixture
def db():
    return MagicMock()

@pytest.fixture
def configured():
    with patch.object(svc, "VAPID_PRIVATE_KEY_PATH", "/tmp/fake_private_key.pem"), patch.object(
        svc, "VAPID_CLAIM_SUB", "mailto:test@example.com"
    ):
        yield
        
class TestRegisterPushSubscription:
    def test_returns_false_and_skips_when_not_configured(self, db):
        user = make_user()
        with patch.object(svc, "VAPID_PRIVATE_KEY_PATH", None):
            result = svc.register_push_subscription(db, user, SUBSCRIPTION)
            
        assert result is False
        db.commit.assert_not_called()
        
    def test_stores_subscription_json_on_users(self, db, configured):
        user = make_user()
        result = svc.register_push_subscription(db, user, SUBSCRIPTION)
        
        assert result is True
        assert json.loads(user.push_subscription) == SUBSCRIPTION
        db.commit.assert_called_once()
        
class TestUnregisterPushSubscription:
    def test_clears_stored_subscription(self, db):
        user = make_user(push_subscription=SUBSCRIPTION)
        svc.unregister_push_subscription(db, user)
        
        assert user.push_subscription is None
        db.commit.assert_called_once()
        
    def test_noop_safe_when_user_has_no_subscription(self, db):
        user = make_user()
        svc.unregister_push_subscription(db, user)
        
        assert user.push_subscription is None
        db.commit.assert_called_once()
        
class TestSendPushNotification:
    def test_noop_when_user_never_subscribed(self, db, configured):
        user = make_user()
        notification = make_notification()
        with patch.object(svc, "webpush") as mock_webpush:
            svc.send_push_notification(db, user, notification)
            
        mock_webpush.assert_not_called()
        
    def test_noop_when_server_has_no_vapid_keys(self, db):
        user = make_user(push_subscription=SUBSCRIPTION)
        notification = make_notification()
        with patch.object(svc, "VAPID_PRIVATE_KEY_PATH", None), patch.object(
            svc, "webpush"
        ) as mock_webpush:
            svc.send_push_notification(db, user, notification)
            
        mock_webpush.assert_not_called()
        
    def test_delivers_via_webpush_with_vapid_claims(self, db, configured):
        user = make_user(push_subscription=SUBSCRIPTION)
        notification = make_notification()
        with patch.object(svc, "webpush") as mock_webpush:
            svc.send_push_notification(db, user, notification)
            
        mock_webpush.assert_called_once()
        _, kwargs = mock_webpush.call_args
        assert kwargs["subscription_info"] == SUBSCRIPTION
        assert kwargs["vapid_private_key"] == "/tmp/fake_private_key.pem"
        assert kwargs["vapid_claims"] == {"sub": "mailto:test@example.com"}
        payload = json.loads(kwargs["data"])
        assert payload["title"] == "Fire Alert"
        assert payload["body"] == "Fire is 3.0km away"
        
    def test_clears_subscription_when_push_service_reports_it_gone(self, db, configured):
        user = make_user(push_subscription=SUBSCRIPTION)
        notification = make_notification()
        fake_response = MagicMock(status_code=410)
        with patch.object(
            svc, "webpush", side_effect=WebPushException("gone", response=fake_response)
        ):
            svc.send_push_notification(db, user, notification)
            
        assert user.push_subscription is None
        db.commit.assert_called_once()
        
    def test_keeps_subscription_on_other_webpush_error(self, db, configured):
        user = make_user(push_subscription=SUBSCRIPTION)
        notification = make_notification()
        fake_response = MagicMock(status_code=500)
        with patch.object(
            svc, "webpush", side_effect=WebPushException("service error", response=fake_response)
        ):
            svc.send_push_notification(db, user, notification)
            
        assert user.push_subscription is not None
        db.commit.assert_not_called()
        
    def test_swallows_unexpected_errors(self, db, configured):
        user = make_user(push_subscription=SUBSCRIPTION)
        notification = make_notification()
        with patch.object(svc, "webpush", side_effect=RuntimeError("boom")):
            svc.send_push_notification(db, user, notification)
        