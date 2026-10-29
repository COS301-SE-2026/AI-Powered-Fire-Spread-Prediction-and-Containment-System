from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import pytest

from app.backend.src.schemas.auth import ResetPasswordRequest
from app.backend.src.services.auth import forgot_password
from app.backend.src.services.auth.forgot_password import (
    MIN_PASSWORD_LENGTH,
    RESET_REQUEST_LIMIT,
    RESET_REQUEST_WINDOW_SECONDS,
    _hash_token,
    _rate_limit_key,
    request_password_reset,
    reset_password,
)


class TestForgotPasswordHelpers:
    def test_hash_token_sha256(self):
        token = "test_raw_token_value"
        hashed = _hash_token(token)
        assert isinstance(hashed, str)
        assert len(hashed) == 64
        assert hashed == _hash_token(token)

    def test_rate_limit_key_format(self):
        key = _rate_limit_key("user@example.com")
        assert key == "auth:reset-request:user@example.com"


class TestRequestPasswordReset:
    def test_first_attempt_sets_expiration(self, monkeypatch):
        mock_valkey = MagicMock()
        mock_valkey.incr.return_value = 1
        monkeypatch.setattr(forgot_password, "valkey_client", mock_valkey)

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        email, raw_token = request_password_reset(mock_db, "  TEST@example.com  ")

        assert email == "test@example.com"
        assert isinstance(raw_token, str)
        mock_valkey.incr.assert_called_once_with("auth:reset-request:test@example.com")
        mock_valkey.expire.assert_called_once_with(
            "auth:reset-request:test@example.com", RESET_REQUEST_WINDOW_SECONDS
        )
        assert mock_user.reset_token == _hash_token(raw_token)
        assert mock_user.reset_token_expires is not None
        mock_db.commit.assert_called_once()

    def test_subsequent_allowed_attempt_does_not_reset_expiration(self, monkeypatch):
        mock_valkey = MagicMock()
        mock_valkey.incr.return_value = 2
        monkeypatch.setattr(forgot_password, "valkey_client", mock_valkey)

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "user@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = request_password_reset(mock_db, "user@example.com")

        assert result is not None
        mock_valkey.expire.assert_not_called()
        mock_db.commit.assert_called_once()

    def test_rate_limit_exceeded_returns_none(self, monkeypatch):
        mock_valkey = MagicMock()
        mock_valkey.incr.return_value = RESET_REQUEST_LIMIT + 1
        monkeypatch.setattr(forgot_password, "valkey_client", mock_valkey)

        mock_db = MagicMock()
        result = request_password_reset(mock_db, "spammer@example.com")

        assert result is None
        mock_db.query.assert_not_called()

    def test_user_not_found_returns_none(self, monkeypatch):
        mock_valkey = MagicMock()
        mock_valkey.incr.return_value = 1
        monkeypatch.setattr(forgot_password, "valkey_client", mock_valkey)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = request_password_reset(mock_db, "missing@example.com")

        assert result is None
        mock_db.commit.assert_not_called()


class TestResetPassword:
    def test_password_too_short_raises_value_error(self):
        mock_db = MagicMock()
        short_password = "a" * (MIN_PASSWORD_LENGTH - 1)
        req = ResetPasswordRequest(token="some_token", new_password=short_password)

        with pytest.raises(
            ValueError,
            match=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
        ):
            reset_password(mock_db, req)

    def test_token_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        req = ResetPasswordRequest(token="invalid_token", new_password="ValidPassword123")

        with pytest.raises(ValueError, match="Invalid or expired reset link"):
            reset_password(mock_db, req)

    def test_user_missing_expiration_date_raises_value_error(self):
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.reset_token_expires = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        req = ResetPasswordRequest(token="valid_token", new_password="ValidPassword123")

        with pytest.raises(ValueError, match="Invalid or expired reset link"):
            reset_password(mock_db, req)

    def test_token_expired_naive_datetime_raises_value_error(self):
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.reset_token_expires = datetime(2020, 1, 1, 12, 0, 0)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        req = ResetPasswordRequest(token="expired_token", new_password="ValidPassword123")

        with pytest.raises(ValueError, match="Invalid or expired reset link"):
            reset_password(mock_db, req)

    def test_token_expired_aware_datetime_raises_value_error(self):
        mock_db = MagicMock()
        mock_user = MagicMock()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        mock_user.reset_token_expires = past_time
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        req = ResetPasswordRequest(token="expired_token", new_password="ValidPassword123")

        with pytest.raises(ValueError, match="Invalid or expired reset link"):
            reset_password(mock_db, req)

    def test_reset_password_success(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        monkeypatch.setattr(forgot_password, "hash_password", lambda p: f"hashed_{p}")

        req = ResetPasswordRequest(token="good_token", new_password="StrongNewPassword123")
        reset_password(mock_db, req)

        assert mock_user.hashed_password == "hashed_StrongNewPassword123"
        assert mock_user.reset_token is None
        assert mock_user.reset_token_expires is None
        mock_db.commit.assert_called_once()