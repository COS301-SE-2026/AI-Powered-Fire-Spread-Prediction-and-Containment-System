from enum import Enum


class UserRole(str, Enum):
    user = "user"
    firefighter = "firefighter"
    admin = "admin"
