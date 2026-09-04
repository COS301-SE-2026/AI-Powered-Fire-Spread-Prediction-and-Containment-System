from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.backend.src.enums.notification_type import NotificationType
from app.backend.src.enums.severity import Severity


class NotificationOut(BaseModel):
    """
    Mirrors frontend `FireNotification` type exactly
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    fireId: str
    fireLocation: str
    distance: float
    type: NotificationType
    severity: Severity
    message: str
    time: datetime
    read: bool

    @classmethod  # Converts from snake_case to camelCase for frontend to comply with coding standards
    def from_model(cls, n) -> "NotificationOut":
        return cls(
            id=n.id,
            fireId=n.fire_report_id,
            fireLocation=n.fire_location,
            distance=round(n.distance, 1),
            type=n.type,
            severity=n.severity,
            message=n.message,
            time=n.time,
            read=n.read,
        )


class NotificationListOut(BaseModel):
    notifications: list[NotificationOut]
    unread_count: int
    locationEnabled: bool
