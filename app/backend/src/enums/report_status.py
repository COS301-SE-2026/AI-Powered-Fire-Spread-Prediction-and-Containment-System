from enum import Enum


class ReportStatus(str, Enum):
    received = "received"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


status_level = {
    ReportStatus.received: 0,
    ReportStatus.pending: 1,
    ReportStatus.verified: 2,
    ReportStatus.rejected: 2,
}
