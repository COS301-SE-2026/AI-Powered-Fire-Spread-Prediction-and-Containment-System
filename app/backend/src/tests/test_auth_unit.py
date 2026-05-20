import pytest
from auth import hash_password, verify_password, create_access_token
from jose import jwt
from datetime import timedelta

def test_password_hashing():
    password = "SecurePass123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)

def test_jwt_creation():
    data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, "your-super-secret-key-change-this", algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    assert decoded["user_id"] == 1
    assert "exp" in decoded