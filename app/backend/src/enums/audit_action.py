from enum import Enum

class AuditAction(str, Enum):
    LOGIN="Login"
    LOGIN_FAILED="Login Failed"
    LOGOUT="Logout"

    PASSWORD_RESET_REQUESTED = "Password Reset Requested"
    PASSWORD_RESET_COMPLETED = "Password Reset Completed"

    ACCOUNT_LOCKED = "Account Locked"
    ACCOUNT_UNLOCKED = "Account Unlocked"
    ACCOUNT_SUSPENDED = "Account Suspended"
    ACCOUNT_REACTIVATED = "Account Reactivated"

    ROLE_REQUEST_SUBMITTED = "Role Request Submitted"
    ROLE_REQUEST_APPROVED = "Role Request Approved"
    ROLE_REQUEST_REJECTED = "Role Request Rejected"
    ROLE_REVOKED = "Role Revoked"

    TOKEN_INVALIDATED = "Token Invalidated"

    SIMULATION_RUN="Simulation Run"
    SIMULATION_RERUN="Simulation Re-run"
