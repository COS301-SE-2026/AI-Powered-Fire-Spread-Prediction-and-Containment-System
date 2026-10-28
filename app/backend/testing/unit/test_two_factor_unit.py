from unittest.mock import MagicMock
import pytest
import pyotp

from app.backend.src.enums.user_role import UserRole
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.schemas.auth import Two_FA_Verify_Request, CompleteRegistrationRequest
from app.backend.src.services.auth import two_factor
from app.backend.src.services.auth.two_factor import (
    setup_2fa,
    verify_2fa,
    complete_registration,
)


class TestSetup2FA:
    def test_setup_2fa_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="User is not found or does not exist"):
            setup_2fa("nonexistent@example.com", mock_db)

    def test_setup_2fa_success(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        monkeypatch.setattr(pyotp, "random_base32", lambda: "JBSWY3DPEHPK3PXP")

        result = setup_2fa("user@example.com", mock_db)

        assert mock_user.totp_secret == "JBSWY3DPEHPK3PXP"
        assert mock_user.is_2fa_enabled is False
        mock_db.commit.assert_called_once()
        assert "otpauth://" in result["otpauth_url"]
        assert "user%40example.com" in result["otpauth_url"] or "user@example.com" in result["otpauth_url"]


class TestVerify2FA:
    def test_verify_2fa_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        req = Two_FA_Verify_Request(username="test@example.com", code="123456")

        with pytest.raises(ValueError, match="User does not exist or not found"):
            verify_2fa(mock_db, req)

    def test_verify_2fa_no_totp_secret_raises_value_error(self):
        mock_db = MagicMock()
        mock_user = MagicMock(totp_secret=None)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        req = Two_FA_Verify_Request(username="test@example.com", code="123456")

        with pytest.raises(ValueError, match="two factor auth is not enabled"):
            verify_2fa(mock_db, req)

    def test_verify_2fa_invalid_code_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(totp_secret="JBSWY3DPEHPK3PXP")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_totp = MagicMock()
        mock_totp.verify.return_value = False
        monkeypatch.setattr(pyotp, "TOTP", lambda secret: mock_totp)

        req = Two_FA_Verify_Request(username="test@example.com", code="000000")

        with pytest.raises(ValueError, match="Invalid code"):
            verify_2fa(mock_db, req)

    def test_verify_2fa_success(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(
            id="usr_12345678",
            email="test@example.com",
            totp_secret="JBSWY3DPEHPK3PXP",
            role=UserRole.firefighter,
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_totp = MagicMock()
        mock_totp.verify.return_value = True
        monkeypatch.setattr(pyotp, "TOTP", lambda secret: mock_totp)
        monkeypatch.setattr(two_factor, "create_access_token", lambda data: "mock_jwt_token")

        req = Two_FA_Verify_Request(username="test@example.com", code="123456")
        result = verify_2fa(mock_db, req)

        assert result == {
            "access_token": "mock_jwt_token",
            "role": UserRole.firefighter.value,
        }


class TestCompleteRegistration:
    def test_complete_registration_pending_not_found_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        monkeypatch.setattr(two_factor, "get_pending_registration", lambda token: None)

        req = CompleteRegistrationRequest(registration_token="token_xyz", code="123456")

        with pytest.raises(ValueError, match="Registration expired or not found, please register again"):
            complete_registration(mock_db, req)

    def test_complete_registration_invalid_code_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        pending_data = {
            "totp_secret": "JBSWY3DPEHPK3PXP",
            "requested_role": UserRole.user.value,
        }
        monkeypatch.setattr(two_factor, "get_pending_registration", lambda token: pending_data)

        mock_totp = MagicMock()
        mock_totp.verify.return_value = False
        monkeypatch.setattr(pyotp, "TOTP", lambda secret: mock_totp)

        req = CompleteRegistrationRequest(registration_token="token_xyz", code="999999")

        with pytest.raises(ValueError, match="Invalid code"):
            complete_registration(mock_db, req)

    def test_complete_registration_standard_user_success(self, monkeypatch):
        mock_db = MagicMock()
        pending_data = {
            "email": "civilian@example.com",
            "hashed_password": "hashed_secret_pw",
            "name": "John",
            "surname": "Doe",
            "id_number": "9001015000087",
            "totp_secret": "JBSWY3DPEHPK3PXP",
            "requested_role": UserRole.user.value,
        }
        monkeypatch.setattr(two_factor, "get_pending_registration", lambda token: pending_data)
        delete_mock = MagicMock()
        monkeypatch.setattr(two_factor, "delete_pending_registration", delete_mock)

        mock_totp = MagicMock()
        mock_totp.verify.return_value = True
        monkeypatch.setattr(pyotp, "TOTP", lambda secret: mock_totp)

        def make_fake_user(**kwargs):
            mock_user = MagicMock()
            for key, val in kwargs.items():
                setattr(mock_user, key, val)
            mock_user.role = UserRole.user
            return mock_user

        monkeypatch.setattr(two_factor, "User", make_fake_user)
        monkeypatch.setattr(two_factor, "create_access_token", lambda data: "mock_user_token")

        req = CompleteRegistrationRequest(registration_token="valid_token", code="123456")
        result = complete_registration(mock_db, req)

        assert result["access_token"] == "mock_user_token"
        assert result["role"] == UserRole.user.value
        assert result["pending_approval"] is False

        assert mock_db.add.call_count == 1
        added_user = mock_db.add.call_args[0][0]
        assert added_user.email == "civilian@example.com"
        assert added_user.is_active is True
        assert added_user.is_2fa_enabled is True

        mock_db.commit.assert_called_once()
        delete_mock.assert_called_once_with("valid_token")

    def test_complete_registration_firefighter_creates_role_request(self, monkeypatch):
        mock_db = MagicMock()
        pending_data = {
            "email": "firefighter@example.com",
            "hashed_password": "hashed_secret_pw",
            "name": "Jane",
            "surname": "Smith",
            "id_number": "9202025000084",
            "totp_secret": "JBSWY3DPEHPK3PXP",
            "requested_role": UserRole.firefighter.value,
        }
        monkeypatch.setattr(two_factor, "get_pending_registration", lambda token: pending_data)
        delete_mock = MagicMock()
        monkeypatch.setattr(two_factor, "delete_pending_registration", delete_mock)

        mock_totp = MagicMock()
        mock_totp.verify.return_value = True
        monkeypatch.setattr(pyotp, "TOTP", lambda secret: mock_totp)

        def make_fake_user(**kwargs):
            mock_user = MagicMock()
            for key, val in kwargs.items():
                setattr(mock_user, key, val)
            mock_user.role = UserRole.user
            return mock_user

        monkeypatch.setattr(two_factor, "User", make_fake_user)
        monkeypatch.setattr(two_factor, "create_access_token", lambda data: "mock_firefighter_token")

        req = CompleteRegistrationRequest(registration_token="valid_token_ff", code="654321")
        result = complete_registration(mock_db, req)

        assert result["access_token"] == "mock_firefighter_token"
        assert result["role"] == UserRole.user.value
        assert result["pending_approval"] is True

        assert mock_db.add.call_count == 2
        created_role_request = mock_db.add.call_args_list[1][0][0]
        assert created_role_request.requested_role == UserRole.firefighter
        assert created_role_request.current_role == UserRole.user
        assert created_role_request.status == RequestStatus.pending

        mock_db.commit.assert_called_once()
        delete_mock.assert_called_once_with("valid_token_ff")