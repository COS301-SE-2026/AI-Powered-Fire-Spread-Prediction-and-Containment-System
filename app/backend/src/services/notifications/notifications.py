from sqlalchemy.orm import Session

from enums.notification_type import NotificationType
from enums.report_status import ReportStatus
from enums.user_role import UserRole
from models.notification import Notification
from models.reported_fires import FireReports
from models.users import User
from schemas.notification import NotificationOut
from geo import haversine_km, point_to_latlng
from severity import severity_from_boundary_radius
from websocket_manager import manager

# radius (km) used to decide which user-role accounts get notified about a new fire alert based on proximity.
# Admin and firefighters get a wider radius since they may need broader situational awareness

# Adjust these once ai model has been changed to fir more accurately 
DEFAULT_USER_ALERT_RADIUS  = 25.0
STAFF_ALERT_RADIUS_KM = 100.0

def push(notification: Notification) -> None:
    payload = {
        "event": "notification",
        "data": NotificationOut.from_model(notification).model_dump(mode="json"),
    }
    
    import asyncio
    
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.send_to_user(notification.user_id, payload))
    except RuntimeError:
        asyncio.run(manager.send_to_user(notification.user_id, payload))
        
    def notify_fire_alert(db: Session, fire_report: FireReports, message: str) -> list[Notification]:
        """
        Fan out a fire report as an "alert" notification.
        
        Only fires for reports with status == verified.
        
        - everyone is filtered by proximity
        - severity is derived from boundary_radius (services/severity.py) since FireReports doesn't track severity directly
        """
        
        if fire_report.status != ReportStatus.verified:
            return[]
        
        fire_latlng = point_to_latlng(fire_report.location_geom)
        if fire_latlng is None:
            raise ValueError("fire_report.location_geom not set. Cannot calculate distances")
        fire_lat, fire_lng = fire_latlng
        
        severity = severity_from_boundary_radius(fire_report.boundary_radius)
        all_users = db.query(User).all()
        
        created: list[Notification] = []
        for user in all_users:
            user_latlng = point_to_latlng(getattr(user, "location_geom", None))
            radius = STAFF_ALERT_RADIUS_KM if user.role != UserRole.user else DEFAULT_USER_ALERT_RADIUS
            
            if user_latlng is None:
                if user.role == UserRole.user:
                    continue
                distance = 0.0
            else:
                distance = haversine_km(user_latlng[0], user_latlng[1], fire_lat, fire_lng)
                if distance > radius:
                    continue
            
            notification = Notification(
                user_id=user.id,
                fire_report_id=fire_report.id,
                type=NotificationType.alert,
                severity=severity,
                message=message,
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
    
def notify_fire_update(db: Session, fire_report: FireReports, message: str) -> list[Notification]:
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
        raise ValueError("fire_report.location_geom is not set - cannot calculate distance")
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
        distance = haversine_km(user_latlng[0], user_latlng[1], fire_lat, fire_lng)
        
        