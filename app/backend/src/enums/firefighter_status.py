from enum import Enum

class FirefighterReportStatus(str, Enum):
    rejected = "rejected"
    pending = "pending"
    verified = "verified"