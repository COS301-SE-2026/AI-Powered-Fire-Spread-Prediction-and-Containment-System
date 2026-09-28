from __future__ import annotations

import json
import logging
import os

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.backend.src.models.notification import Notification
from app.backend.src.models.users import User

logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY_PATH = os.environ.get("VAPID_PRIVATE_KEY_PATH")
VAPID_CLAIM_SUB = os.environ.get("VAPID_CLAIM_SUB")


def configured() -> bool:
    return bool(VAPID_PRIVATE_KEY_PATH and VAPID_CLAIM_SUB)


def register_push_subscription(db: Session, user: User, subscription: dict) -> bool:
    """
    Stores browser's PushSubscription (from pushManager.subscribe() posted as JSON by frontend)
    on user.
    Called from POST /api/notifications/push/register
    """
    if not configured():
        logger.warning(
            "VAPID keys not configured - push registration skipped for user %s",
            user.id,
        )
        return False

    user.push_subscription = json.dumps(subscription)
    db.commit()
    return True


def unregister_push_subscription(db: Session, user: User) -> None:
    """
    Clears user's stored subscription. Called from DELETE /api/notifications/push
    (eg. on logout or when user disables push notifications)
    """
    user.push_subscription = None
    db.commit()


def title_for(notification: Notification) -> str:
    return "Fire Alert" if notification.type.value == "alert" else "Fire Update"


def send_push_notification(db: Session, user: User, notification: Notification) -> None:
    if not user.push_subscription:
        return  # user hasn't subscribed browser yet
    if not configured():
        return  # server has no VAPID keys to sign with

    subscription_info = json.loads(user.push_subscription)
    payload = json.dumps(
        {
            "title": title_for(notification),
            "body": notification.message,
            "notificationId": notification.id,
            "fireReportId": notification.fire_report_id,
            "type": notification.type.value,
            "severity": notification.severity.value,
        }
    )

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY_PATH,
            vapid_claims={"sub": VAPID_CLAIM_SUB},
        )
    except WebPushException as exc:
        response = exc.response
        if response is not None and response.status_code in (404, 410):
            logger.info(
                "Push subscription gone for user %s - clearing stored subscription",
                user.id,
            )
            user.push_subscription = None
            db.commit()
        else:
            logger.exception(
                "Failed to deliver push notification %s to user%s",
                notification.id,
                user.id,
            )
    except Exception:
        logger.exception(
            "Failed to deliver push notification %s to user %s",
            notification.id,
            user.id,
        )
