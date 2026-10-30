from unittest.mock import MagicMock
import pytest

from app.backend.src.services.auth import edit_password as edit_password_module
from app.backend.src.services.auth.edit_password import edit_password
from app.backend.src.services.auth.forgot_password import MIN_PASSWORD_LENGTH


class TestEditPassword:
    def test_current_password_incorrect_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(hashed_password="hashed_old_password")

        monkeypatch.setattr(edit_password_module, "verify_password", lambda plain, hashed: False)

        with pytest.raises(ValueError, match="Current password is incorrect"):
            edit_password(mock_db, mock_user, "wrong_password", "NewValidPass123")

        mock_db.commit.assert_not_called()

    def test_new_password_too_short_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(hashed_password="hashed_old_password")

        monkeypatch.setattr(edit_password_module, "verify_password", lambda plain, hashed: True)

        short_password = "a" * (MIN_PASSWORD_LENGTH - 1)
        expected_msg = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

        with pytest.raises(ValueError, match=expected_msg):
            edit_password(mock_db, mock_user, "old_password", short_password)

        mock_db.commit.assert_not_called()

    def test_new_password_same_as_current_raises_value_error(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(hashed_password="hashed_old_password")

        monkeypatch.setattr(edit_password_module, "verify_password", lambda plain, hashed: True)

        identical_password = "ExactSamePassword123"

        with pytest.raises(ValueError, match="New password must differ from the current one"):
            edit_password(mock_db, mock_user, identical_password, identical_password)

        mock_db.commit.assert_not_called()

    def test_edit_password_success(self, monkeypatch):
        mock_db = MagicMock()
        mock_user = MagicMock(hashed_password="hashed_old_password")

        monkeypatch.setattr(edit_password_module, "verify_password", lambda plain, hashed: True)
        monkeypatch.setattr(edit_password_module, "hash_password", lambda pw: f"hashed_{pw}")

        current_pw = "OldValidPassword123"
        new_pw = "NewValidPassword456"

        edit_password(mock_db, mock_user, current_pw, new_pw)

        assert mock_user.hashed_password == f"hashed_{new_pw}"
        mock_db.commit.assert_called_once()