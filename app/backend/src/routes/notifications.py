from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from db import get_db
from dependencies.auth import decode_token, get_current_user
from models.notification import Notification
from models.users import User
from schemas.notification import NotificationListOut, NotificationOut
from services.notifications.notifications import mark_all_read, mark_notification_read
from services.notifications.websocket_manager import manager

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

PANEL_WINDOW_HOURS = 24


@router.get("", response_model=NotificationListOut)
def list_notifications(
    limit: int = 50,
    offset: int = 0,
    hours: int = PANEL_WINDOW_HOURS,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns notifications from last `hours` (default 24h).
    For notifications sidebar recent-history view.
    Unread count scoped same way
    """

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.time >= cutoff)
        .order_by(Notification.time.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    unread_count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.read.is_(False),
            Notification.time >= cutoff,
        )
        .count()
    )

    return NotificationListOut(
        notifications=[NotificationOut.from_model(n) for n in notifications],
        unread_count=unread_count,
        locationEnabled=user.location_geom is not None,
    )


@router.post("/{notification_id}/read", response_model=NotificationOut)
def read_notification(
    notification_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = mark_notification_read(db, user.id, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationOut.from_model(notification)


@router.post("/read-all")
def read_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = mark_all_read(db, user.id)
    return {"marked_read": count}


@router.websocket("/ws")
async def notification_ws(websocket: WebSocket):
    """
    Client connects with wss://host/api/notifications/ws

    Auth comes from same `access_token` httpOnly cookie REST endpoints use.
    (browsers attach cookies to WebSocket handshake automatically same as any other request to this orgin) -
    no token in URL so never ends up in server logs or browser history.

    Pushes new notifications for authenticated user as they're created by services.notifications.py.
    No client -> server messages expected
    """

    token = websocket.cookies.get("access_token")
    user_id = decode_token(token) if token else None
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        user = db.query(User).filter(User.id == user_id).first()
    finally:
        db_gen.close()

    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user.id, websocket)
