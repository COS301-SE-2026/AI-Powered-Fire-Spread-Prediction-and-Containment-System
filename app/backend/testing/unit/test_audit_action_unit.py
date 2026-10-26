from enum import Enum
import pytest

from enums.audit_action import AuditAction


class TestAuditActionEnum:
    def test_enum_inheritance(self):
        assert issubclass(AuditAction, str)
        assert issubclass(AuditAction, Enum)

    def test_all_expected_members_exist(self):
        expected_members = {
            "LOGIN": "Login",
            "LOGIN_FAILED": "Login Failed",
            "LOGOUT": "Logout",
            "PASSWORD_RESET_REQUESTED": "Password Reset Requested",
            "PASSWORD_RESET_COMPLETED": "Password Reset Completed",
            "ACCOUNT_LOCKED": "Account Locked",
            "ACCOUNT_UNLOCKED": "Account Unlocked",
            "ACCOUNT_SUSPENDED": "Account Suspended",
            "ACCOUNT_REACTIVATED": "Account Reactivated",
            "ROLE_REQUEST_SUBMITTED": "Role Request Submitted",
            "ROLE_REQUEST_APPROVED": "Role Request Approved",
            "ROLE_REQUEST_REJECTED": "Role Request Rejected",
            "ROLE_REVOKED": "Role Revoked",
            "TOKEN_INVALIDATED": "Token Invalidated",
            "SIMULATION_RUN": "Simulation Run",
            "SIMULATION_RERUN": "Simulation Re-run",
        }

        assert len(AuditAction) == len(expected_members)
        for name, value in expected_members.items():
            member = AuditAction[name]
            assert member.value == value
            assert member == value
            assert isinstance(member, str)

    def test_lookup_by_value(self):
        assert AuditAction("Login") is AuditAction.LOGIN
        assert AuditAction("Simulation Run") is AuditAction.SIMULATION_RUN
        assert AuditAction("Role Revoked") is AuditAction.ROLE_REVOKED

    def test_invalid_value_raises_value_error(self):
        with pytest.raises(ValueError):
            AuditAction("INVALID_ACTION")