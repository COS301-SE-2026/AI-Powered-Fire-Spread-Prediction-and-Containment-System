import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.backend.src.enums.notification_type import NotificationType
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.notification import Notification
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.users import User
from app.backend.src.schemas.notification import NotificationOut
from .geo import haversine_km, point_to_latlng
from .severity import severity_from_boundary_radius
from .websocket_manager import manager, get_main_loop

logger = logging.getLogger(__name__)

TIER_THRESHOLDS_KM = [20.0, 10.0, 5.0]

# Admin and firefighters get a wider escalation ladder since they may need broader situational awareness
STAFF_TIER_THRESHOLDS_KM = [50.0, 20.0, 10.0, 5.0, 2.0]


def tier_for_distance(distance_km: float, thresholds: list[float]) -> float | None:
    """
    Returns closest threshold the distance satisfies or none if beyond
    outermost tier entirely.
    """

    reached = None
    for threshold in thresholds:
        if distance_km <= threshold:
            reached = threshold
    return reached


def tier_thresholds_for_role(role: UserRole) -> list[float]:
    return TIER_THRESHOLDS_KM if role == UserRole.user else STAFF_TIER_THRESHOLDS_KM


def distance_to_fire_edge(
    user_lat: float, user_lng: float, fire_lat: float, fire_lng: float, boundary_radius
) -> float:
    """
    Distance from user to fire's reported boundary/edge
    """
    center_distance = haversine_km(user_lat, user_lng, fire_lat, fire_lng)
    return max(0.0, center_distance - float(boundary_radius))


def push(notification: Notification) -> None:
    payload = {
        "event": "notification",
        "data": NotificationOut.from_model(notification).model_dump(mode="json"),
    }
    loop = get_main_loop()
    if loop is None:
        logger.warning(
            "push() called before main_loop was set, notification %s for user %s was not delivered live",
            notification.id,
            notification.user_id,
        )
        return

    future = asyncio.run_coroutine_threadsafe(
        manager.send_to_user(notification.user_id, payload), loop
    )

    def log_if_failed(f: asyncio.Future) -> None:
        exc = f.exception()
        if exc is not None:
            logger.error(
                "Failed to push notification %s to user %s: %s",
                notification.id,
                notification.user_id,
                exc,
            )

    future.add_done_callback(log_if_failed)


def notify_fire_alert(
    db: Session, fire_report: FireReports, message: str
) -> list[Notification]:
    """
    Fan out a fire report as an "alert" notification.

    Only fires for reports with status == verified.

    - everyone is filtered by proximity
    - severity is derived from boundary_radius (services/severity.py) since FireReports doesn't track severity directly
    """

    if fire_report.status != ReportStatus.verified:
        return []

    fire_latlng = point_to_latlng(fire_report.location_geom)
    if fire_latlng is None:
        raise ValueError(
            "fire_report.location_geom not set. Cannot calculate distances"
        )
    fire_lat, fire_lng = fire_latlng

    severity = severity_from_boundary_radius(fire_report.boundary_radius)
    all_users = db.query(User).all()

    created: list[Notification] = []
    for user in all_users:
        user_latlng = point_to_latlng(getattr(user, "location_geom", None))
        if user_latlng is None:
            continue  # if location not shared, never notified

        distance = distance_to_fire_edge(
            user_latlng[0],
            user_latlng[1],
            fire_lat,
            fire_lng,
            fire_report.boundary_radius,
        )
        thresholds = tier_thresholds_for_role(user.role)
        if tier_for_distance(distance, thresholds) is None:
            continue

        personalized_message = f"{message} ({distance:.1f}km from you)"

        notification = Notification(
            user_id=user.id,
            fire_report_id=fire_report.id,
            type=NotificationType.alert,
            severity=severity,
            message=personalized_message,
            fire_location=fire_report.location_text,
            distance=distance,
        )
        db.add(notification)
        created.append(notification)

    db.commit()
    for n in created:
        db.refresh(n)
        push(n)
    return created


def check_proximity_for_user(db: Session, user: User) -> list[Notification]:
    """
    Re-checks every currently verified fire report against user's new location.
    For each fire, works out tier user in currently, compares it to closest tier they were already
    notified at for that fire (derived from their existing Notification rows, not a separate
    tracking table), and sends fresh notification only if they've moved into a closer tier than before
    """
    user_latlng = point_to_latlng(getattr(user, "location_geom", None))
    if user_latlng is None:
        return []

    thresholds = tier_thresholds_for_role(user.role)
    verified_fires = (
        db.query(FireReports).filter(FireReports.status == ReportStatus.verified).all()
    )

    created: list[Notification] = []
    for fire_report in verified_fires:
        fire_latlng = point_to_latlng(fire_report.location_geom)
        if fire_latlng is None:
            continue

        distance = distance_to_fire_edge(
            user_latlng[0],
            user_latlng[1],
            fire_latlng[0],
            fire_latlng[1],
            fire_report.boundary_radius,
        )
        new_tier = tier_for_distance(distance, thresholds)
        if new_tier is None:
            continue

        previous_best_distance = (
            db.query(func.min(Notification.distance))
            .filter(
                Notification.user_id == user.id,
                Notification.fire_report_id == fire_report.id,
            )
            .scalar()
        )

        old_tier = (
            tier_for_distance(previous_best_distance, thresholds)
            if previous_best_distance is not None
            else None
        )

        if old_tier is not None and new_tier >= old_tier:
            continue  # not closer than a tier they've already been fotified at

        severity = severity_from_boundary_radius(fire_report.boundary_radius)
        is_first_notification_for_fire = old_tier is None

        if is_first_notification_for_fire:
            personalized_message = (
                f"Fire reported at {fire_report.location_text} is within {new_tier:.0f}km "
                f"{distance:.1f}km away"
            )
            notify_type = NotificationType.alert
        else:
            personalized_message = (
                f"Fire at {fire_report.location_text} is within {new_tier:.0f}km "
                f"({distance:.1f}km away) "
            )
            notify_type = NotificationType.update

        notification = Notification(
            user_id=user.id,
            fire_report_id=fire_report.id,
            type=notify_type,
            severity=severity,
            message=personalized_message,
            fire_location=fire_report.location_text,
            distance=distance,
        )
        db.add(notification)
        created.append(notification)

    db.commit()
    for n in created:
        db.refresh(n)
        push(n)

    return created


def check_proximity_for_guest(
    db: Session, latitude: float, longitude: float
) -> list[NotificationOut]:
    """
    Stateless proximity check for guests. They have no account hence no persisted notifications.
    Computes matched directly against currently verified fires and hands them straight back in response.

    This has no history of what a guest has already seen; every call returns every fire currently within
    range. Frontend responsible for not re-toasting the same fire twice in a browsing session.

    Guests have same TIER_THRESHOLDS_KM as registered user.
    """

    thresholds = TIER_THRESHOLDS_KM
    verified_fired = (
        db.query(FireReports).filter(FireReports.status == ReportStatus.verified).all()
    )

    matches: list[NotificationOut] = []
    for fire_report in verified_fired:
        fire_latlng = point_to_latlng(fire_report.location_geom)
        if fire_latlng is None:
            continue

        distance = distance_to_fire_edge(
            latitude,
            longitude,
            fire_latlng[0],
            fire_latlng[1],
            fire_report.boundary_radius,
        )
        tier = tier_for_distance(distance, thresholds)
        if tier is None:
            continue

        severity = severity_from_boundary_radius(fire_report.boundary_radius)
        message = (
            f"Fire reported near {fire_report.location_text} ({distance:.1f}km away)"
        )

        # Synchronized directly. Prefixed so it can never collide with a genuine notification
        # id if a guest later registers
        matches.append(
            NotificationOut(
                id=f"guest-{fire_report.id}",
                fireId=fire_report.id,
                fireLocation=fire_report.location_text,
                distance=round(distance, 1),
                type=NotificationType.alert,
                severity=severity,
                message=message,
                time=datetime.now(timezone.utc),
                read=False,
            )
        )

    return matches


def notify_fire_update(
    db: Session, fire_report: FireReports, message: str
) -> list[Notification]:
    """
    Send "update" notification to everyone already tracking this fire.
    Needs to be called whenever `fire_report.status` changes.

    eg.
        report.status = ReportStatus.contained
        db.commit()
        notify_fire_update(db, report, "fire contained")
    """

    fire_latlng = point_to_latlng(fire_report.location_geom)
    if fire_latlng is None:
        raise ValueError(
            "fire_report.location_geom is not set - cannot calculate distance"
        )
    fire_lat, fire_lng = fire_latlng

    severity = severity_from_boundary_radius(fire_report.boundary_radius)

    user_ids = [
        row[0]
        for row in db.query(Notification.user_id)
        .filter(Notification.fire_report_id == fire_report.id)
        .distinct()
        .all()
    ]

    if not user_ids:
        return []

    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    created: list[Notification] = []
    for user_id in user_ids:
        user = users.get(user_id)
        if user is None:
            continue

        user_latlng = point_to_latlng(getattr(user, "location_geom", None))
        if user_latlng:
            distance = distance_to_fire_edge(
                user_latlng[0],
                user_latlng[1],
                fire_lat,
                fire_lng,
                fire_report.boundary_radius,
            )
            personalized_message = f"{message} ({distance:.1f}km away)"
        else:
            distance = 0.0
            personalized_message = message

        notification = Notification(
            user_id=user.id,
            fire_report_id=fire_report.id,
            type=NotificationType.update,
            severity=severity,
            message=personalized_message,
            fire_location=fire_report.location_text,
            distance=distance,
        )
        db.add(notification)
        created.append(notification)

    db.commit()
    for n in created:
        db.refresh(n)
        push(n)

    return created


def mark_notification_read(
    db: Session, user_id: str, notification_id: str
) -> Notification | None:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )

    if notification is None:
        return None

    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, user_id: str) -> int:
    unread = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read.is_(False))
        .all()
    )
    for n in unread:
        n.read = True
    db.commit()
    return len(unread)
