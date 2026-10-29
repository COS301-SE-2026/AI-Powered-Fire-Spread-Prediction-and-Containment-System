from datetime import datetime, timezone
from sqlalchemy import inspect
import pytest

from app.backend.src.enums.audit_action import AuditAction
from app.backend.src.models.audit_log import AuditLog


class TestAuditLogModel:
    def test_tablename(self):
        assert AuditLog.__tablename__ == "audit_log"

    def test_columns_metadata_and_constraints(self):
        mapper = inspect(AuditLog)
        columns = {col.key: col for col in mapper.columns}

        expected_columns = {"id", "user_id", "action", "details", "created_at"}
        assert set(columns.keys()) == expected_columns

        assert columns["id"].primary_key is True
        assert columns["id"].index is True

        assert columns["user_id"].nullable is False
        fk_targets = [fk.target_fullname for fk in columns["user_id"].foreign_keys]
        assert "users.id" in fk_targets

        assert columns["action"].nullable is False

        assert columns["details"].nullable is True

        assert columns["created_at"].nullable is False
        assert columns["created_at"].index is True
        assert columns["created_at"].default is not None

    def test_instantiation_and_attributes(self):
        now = datetime.now(timezone.utc)
        record = AuditLog(
            id="audit_log_001",
            user_id="usr_abc123",
            action=AuditAction.LOGIN,
            details="User logged in from web client",
            created_at=now,
        )

        assert record.id == "audit_log_001"
        assert record.user_id == "usr_abc123"
        assert record.action == AuditAction.LOGIN
        assert record.details == "User logged in from web client"
        assert record.created_at == now

    def test_default_created_at_callable(self):
        created_at_col = inspect(AuditLog).columns["created_at"]
        default_obj = created_at_col.default
        assert default_obj is not None
        assert default_obj.is_callable is True

        default_fn = default_obj.arg
        try:
            generated_dt = default_fn()
        except TypeError:
            generated_dt = default_fn(None)

        assert isinstance(generated_dt, datetime)