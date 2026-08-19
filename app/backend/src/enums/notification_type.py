import enum

class NotificationType(str, enum.Enum):
    alert = "alert"
    update = "update"