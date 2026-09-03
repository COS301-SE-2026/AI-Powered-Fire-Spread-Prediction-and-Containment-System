import os
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.backend.src.dependencies.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.backend.src.services.auth.login import (
    get_delay,
    check_rate_limits,
    record_failure,
    reset_counters,
)


def test_password_hashing():
    pw = "SecurePass123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("WrongPass", hashed)


def test_jwt_creation_and_decoding():
    os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this")
    data = {"sub": "test@example.com", "user_id": 42}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(
        token,
        os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this"),
        algorithms=["HS256"],
    )
    assert decoded["sub"] == data["sub"]
    assert decoded["user_id"] == data["user_id"]
    assert "exp" in decoded


def test_delay_schedule():
    assert get_delay(1) == 0
    assert get_delay(4) == 0
    assert get_delay(5) == 30
    assert get_delay(6) == 30
    assert get_delay(7) == 60
    assert get_delay(8) == 120
    assert get_delay(9) == 240
    assert get_delay(10) == 0


@patch("app.backend.src.services.auth.login.valkey_client")
def test_check_rate_limits_under_lockout(mock_valkey):
    mock_valkey.get.side_effect = lambda key: "locked" if "lockout" in key else None
    mock_valkey.ttl.return_value = 1200

    with pytest.raises(HTTPException) as exc_info:
        check_rate_limits("test@firecontain.com")
    assert exc_info.value.status_code == 423
    assert "locked" in exc_info.value.detail.lower()


@patch("app.backend.src.services.auth.login.valkey_client")
def test_check_rate_limits_throttled(mock_valkey):
    mock_valkey.get.side_effect = lambda key: "throttled" if "throttle" in key else None
    mock_valkey.ttl.return_value = 25

    with pytest.raises(HTTPException) as exc_info:
        check_rate_limits("test@firecontain.com")
    assert exc_info.value.status_code == 429
    assert "25 seconds" in exc_info.value.detail


@patch("app.backend.src.services.auth.login.valkey_client")
def test_record_failure_triggers_30s_delay_at_attempt_five(mock_valkey):
    mock_valkey.incr.return_value = 5

    with pytest.raises(HTTPException) as exc_info:
        record_failure("test@firecontain.com")
    assert exc_info.value.status_code == 429
    assert "30 seconds" in exc_info.value.detail
    mock_valkey.set.assert_called_with(
        "auth:throttle:test@firecontain.com", "throttled", ex=30
    )


@patch("app.backend.src.services.auth.login.valkey_client")
def test_record_failure_triggers_lockout_at_tenth_failure(mock_valkey):
    mock_valkey.incr.return_value = 10

    with pytest.raises(HTTPException) as exc_info:
        record_failure("test@firecontain.com")
    assert exc_info.value.status_code == 423
    assert "Account locked for 30 minutes" in exc_info.value.detail
    mock_valkey.set.assert_called_with(
        "auth:lockout:test@firecontain.com", "locked", ex=1800
    )


@patch("app.backend.src.services.auth.login.valkey_client")
def test_reset_counters_clears_keys(mock_valkey):
    reset_counters("test@frecontain.com")
    assert mock_valkey.delete.call_count == 2
