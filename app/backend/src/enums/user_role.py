from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    FIREFIGHTER = "firefighter"
    ADMIN = "admin"
    