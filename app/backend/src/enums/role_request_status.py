from enum import Enum

class RequestStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    REVOKED = "revoked"
