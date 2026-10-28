from datetime import datetime
from unittest.mock import MagicMock
import pytest

from app.backend.src.services.verification import register_verification
from app.backend.src.services.verification.register_verification import (
    validate_sa_id,
    is_valid_id,
)


def _compute_valid_luhn_13(prefix12: str) -> str:
    total = 0
    for idx, char in enumerate(prefix12):
        digit = int(char)
        if idx % 2 != 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    check_digit = (10 - (total % 10)) % 10
    return f"{prefix12}{check_digit}"


class TestValidateSaId:
    def test_not_a_string_raises_value_error(self):
        with pytest.raises(ValueError, match="ID number not inputed"):
            validate_sa_id(1234567890123)

    def test_invalid_length_or_non_digit_raises_value_error(self):
        with pytest.raises(ValueError, match="ID number needs to be 13 digits long"):
            validate_sa_id("12345")

        with pytest.raises(ValueError, match="ID number needs to be 13 digits long"):
            validate_sa_id("900101500908A")

    def test_invalid_date_of_birth_raises_value_error(self):
        with pytest.raises(ValueError, match="ID number contains an invalid date of birth"):
            validate_sa_id("9002315009087")

    def test_future_birthday_raises_value_error(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 6, 1)
        mock_dt.now.return_value = datetime(2026, 6, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        valid_future_id = _compute_valid_luhn_13("260701500008")
        with pytest.raises(ValueError, match="ID contains a future birthday"):
            validate_sa_id(valid_future_id)

    def test_invalid_citizenship_digit_raises_value_error(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 1, 1)
        mock_dt.now.return_value = datetime(2026, 1, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        invalid_cit_id = _compute_valid_luhn_13("900101500028")
        with pytest.raises(ValueError, match="ID contains an invalid citizenship digit."):
            validate_sa_id(invalid_cit_id)

    def test_invalid_luhn_checksum_raises_value_error(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 1, 1)
        mock_dt.now.return_value = datetime(2026, 1, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        valid_id = _compute_valid_luhn_13("900101500008")
        corrupted_last_digit = str((int(valid_id[-1]) + 1) % 10)
        invalid_luhn_id = valid_id[:-1] + corrupted_last_digit

        with pytest.raises(ValueError, match="ID number is not valid. Please check and try again"):
            validate_sa_id(invalid_luhn_id)

    def test_valid_female_citizen_1900s(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 1, 1)
        mock_dt.now.return_value = datetime(2026, 1, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        clean_id = _compute_valid_luhn_13("900115499908")
        spaced_id = f"{clean_id[:6]} {clean_id[6:10]} {clean_id[10:]}"

        result = validate_sa_id(spaced_id)
        assert result["id_number"] == clean_id
        assert result["date_of_birth"] == datetime(1990, 1, 15)
        assert result["gender"] == "F"
        assert result["citizenship"] == "citizen"

    def test_valid_male_permanent_resident_2000s(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 1, 1)
        mock_dt.now.return_value = datetime(2026, 1, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        valid_id = _compute_valid_luhn_13("051225500018")

        result = validate_sa_id(valid_id)
        assert result["id_number"] == valid_id
        assert result["date_of_birth"] == datetime(2005, 12, 25)
        assert result["gender"] == "M"
        assert result["citizenship"] == "permanent_resident"


class TestIsValidId:
    def test_is_valid_id_returns_true(self, monkeypatch):
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.today.return_value = datetime(2026, 1, 1)
        mock_dt.now.return_value = datetime(2026, 1, 1)
        monkeypatch.setattr(register_verification, "datetime", mock_dt)

        valid_id = _compute_valid_luhn_13("900115499908")
        assert is_valid_id(valid_id) is True

    def test_is_valid_id_returns_false(self):
        assert is_valid_id("invalid_id_number") is False