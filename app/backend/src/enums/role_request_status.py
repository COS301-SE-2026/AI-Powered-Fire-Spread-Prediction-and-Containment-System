from enum import Enum

class RequestStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"
    pending = "pending"
    revoked = "revoked"