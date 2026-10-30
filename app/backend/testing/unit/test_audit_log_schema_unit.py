from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError

from app.backend.src.enums.audit_action import AuditAction
from app.backend.src.schemas.audit_log import AuditLogResponse, AuditLogListResponse


class TestAuditLogResponse:
    def test_valid_audit_log_response_full(self):
        now = datetime.now(timezone.utc)
        payload = {
            "id": "log_001",
            "timestamp": now,
            "user_email": "officer@example.com",
            "action": AuditAction.LOGIN,
            "detail": "Successful login via web interface",
        }
        res = AuditLogResponse(**payload)

        assert res.id == "log_001"
        assert res.timestamp == now
        assert res.user_email == "officer@example.com"
        assert res.action == AuditAction.LOGIN
        assert res.detail == "Successful login via web interface"

    def test_valid_audit_log_response_defaults(self):
        now = datetime.now(timezone.utc)
        payload = {
            "id": "log_002",
            "timestamp": now,
            "action": AuditAction.ROLE_REQUEST_APPROVED,
        }
        res = AuditLogResponse(**payload)

        assert res.id == "log_002"
        assert res.timestamp == now
        assert res.action == AuditAction.ROLE_REQUEST_APPROVED
        assert res.user_email is None
        assert res.detail is None

    def test_from_attributes_orm_mode(self):
        now = datetime.now(timezone.utc)
        orm_mock = MagicMock()
        orm_mock.id = "log_orm_003"
        orm_mock.timestamp = now
        orm_mock.user_email = "admin@example.com"
        orm_mock.action = AuditAction.ROLE_REVOKED
        orm_mock.detail = "Revoked firefighter role"

        res = AuditLogResponse.model_validate(orm_mock)

        assert res.id == "log_orm_003"
        assert res.timestamp == now
        assert res.user_email == "admin@example.com"
        assert res.action == AuditAction.ROLE_REVOKED
        assert res.detail == "Revoked firefighter role"

    def test_missing_required_fields_raises_validation_error(self):
        with pytest.raises(ValidationError):
            AuditLogResponse(id="log_004")

    def test_invalid_action_enum_raises_validation_error(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            AuditLogResponse(
                id="log_005",
                timestamp=now,
                action="NON_EXISTENT_ACTION",
            )


class TestAuditLogListResponse:
    def test_valid_audit_log_list_response(self):
        now = datetime.now(timezone.utc)
        item1 = AuditLogResponse(
            id="log_101",
            timestamp=now,
            action=AuditAction.PASSWORD_RESET_REQUESTED,
        )
        item2 = AuditLogResponse(
            id="log_102",
            timestamp=now,
            user_email="user@example.com",
            action=AuditAction.PASSWORD_RESET_COMPLETED,
            detail="Reset confirmed",
        )

        payload = {
            "data": [item1, item2],
            "total": 2,
            "page": 1,
            "limit": 10,
            "pages": 1,
        }
        res = AuditLogListResponse(**payload)

        assert len(res.data) == 2
        assert res.data[0].id == "log_101"
        assert res.data[1].id == "log_102"
        assert res.total == 2
        assert res.page == 1
        assert res.limit == 10
        assert res.pages == 1

    def test_audit_log_list_missing_field_raises_validation_error(self):
        with pytest.raises(ValidationError):
            AuditLogListResponse(
                data=[],
                total=0,
                page=1,
                limit=10,
            )