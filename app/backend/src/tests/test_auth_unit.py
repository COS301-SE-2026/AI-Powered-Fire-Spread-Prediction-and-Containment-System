import pytest
from auth import hash_password, verify_password, create_access_token
from jose import jwt
from datetime import timedelta
import os

def test_password_hashing():
    pw = "SecurePass123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("WrongPass", hashed)

def test_jwt_creation_and_decoding():
    data = {"sub": "test@example.com", "user_id": 42}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this"), algorithms=["HS256"])
    assert decoded["sub"] == data["sub"]
    assert decoded["user_id"] == data["user_id"]
    assert "exp" in decoded