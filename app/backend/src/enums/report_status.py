from enum import Enum

class ReportStatus(str, Enum):
    received = "received"
    pending = "pending"
    verified = "verified"