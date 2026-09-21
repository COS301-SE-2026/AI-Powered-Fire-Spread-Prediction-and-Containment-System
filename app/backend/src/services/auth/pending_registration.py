import json
import os
import uuid

import pyotp
import redis

from app.backend.src.schemas.auth import RegisterRequest

VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey-cache")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

client = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, db=0)

PENDING_REGISTRATION_TTL = 15 * 60 # 15 min ttl for a regisration

def key(token: str) -> str:
    return f"pending_registration:{token}"


def create_pending_registration(request: RegisterRequest, hashed_pass: str) -> dict:
    token = uuid.uuid4().hex
    secret = pyotp.random_base32()

    payload = request.model_dump(mode="json", exclude={"password"})
    payload["hashed_password"] = hashed_pass
    payload["totp_secret"] = secret

    client.set(key(token), json.dumps(payload), ex=PENDING_REGISTRATION_TTL)

    otpauth_url = pyotp.TOTP(secret).provisioning_uri(name=request.email, issuer_name="FireAway")

    return {"registration_token": token, "otpauth_url": otpauth_url, "email": request.email}

def get_pending_registration(token: str) -> dict | None:
    raw = client.get(key(token))

    return json.loads(raw) if raw else None

def delete_pending_registration(token: str) -> None:
    client.delete(key(token))
