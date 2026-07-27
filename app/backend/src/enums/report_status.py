from enum import Enum

class ReportStatus(str, Enum):
    RECEIVED = "received"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

status_level = {
    ReportStatus.RECEIVED: 0,
    ReportStatus.PENDING: 1,
    ReportStatus.VERIFIED: 2,
    ReportStatus.REJECTED: 2,
}
