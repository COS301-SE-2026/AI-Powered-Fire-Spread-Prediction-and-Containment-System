import os
from datetime import datetime, timezone
from fastapi import HTTPException, status
import redis
from sqlalchemy import func
from sqlalchemy.orm import Session

from dependencies.auth import create_access_token, verify_password
from models.users import User
from schemas.auth import LoginRequest

# needs t.b. added to env files, these are just temp
# odes not need to be ip address, that's only for fire reports
VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

valkey_client = redis.Redis(
    host=VALKEY_HOST, port=VALKEY_PORT, db=0, decode_responses=True
)

SHORT_WINDOW_SECONDS = 15 * 60
LOCKOUT_SECONDS = 30 * 60

DELAY_SCHEDULE = {
    5: 30,
    6: 30,
    7: 60,
    8: 120,
    9: 240,
}


def get_delay(fails: int) -> int:
    return DELAY_SCHEDULE.get(fails, 0)


# email needs to be ip, but still need to hear from Ryan how to get it
def check_rate_limits(email_key: str) -> None:
    lockout_key = f"auth:lockout:{email_key}"
    throttle_key = f"auth:throttle:{email_key}"

    is_locked = valkey_client.get(lockout_key)
    if is_locked:
        ttl = valkey_client.ttl(lockout_key)
        minutes_left = max(1, ttl // 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Your account is locked due to 10 consecutive failed login attempts. You will be able to try to login again in {minutes_left} minutes.",
        )

    is_throttled = valkey_client.get(throttle_key)
    if is_throttled:
        ttl = valkey_client.ttl(throttle_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have tried to login unsuccessfully too many times. Please wait {ttl} seconds before you try to login again.",
        )


# change to IP here also, probably IP and device
def record_failure(email_key: str) -> None:
    lockout_key = f"auth:lockout:{email_key}"
    consecutive_key = f"auth.consecutive:{email_key}"
    throttle_key = f"auth:throttle:{email_key}"

    fails = valkey_client.incr(consecutive_key)
    valkey_client.expire(consecutive_key, SHORT_WINDOW_SECONDS)

    if fails >= 10:
        valkey_client.set(lockout_key, "locked", ex=LOCKOUT_SECONDS)
        valkey_client.delete(consecutive_key)
        valkey_client.delete(throttle_key)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked for 30 minutes due to 10 consecutive failed login attempts",
        )

    delay = get_delay(fails)
    if delay > 0:
        valkey_client.set(throttle_key, "throttled", ex=delay)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Incorrect credentials. Please wait {delay} seconds before retrying to login",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )


def reset_counters(email_key: str) -> None:
    consecutive_key = f"auth.consecutive:{email_key}"
    throttle_key = f"auth:throttle:{email_key}"
    valkey_client.delete(consecutive_key)
    valkey_client.delete(throttle_key)


def login_user(db: Session, request: LoginRequest):
    # email_key needs to change to ip
    email_key = request.email.strip().lower()

    check_rate_limits(email_key)

    user = db.query(User).filter(func.lower(User.email) == email_key).first()

    hashed = user.hashed_password

    if not user or not verify_password(request.password, hashed):
        record_failure(email_key)

    reset_counters(email_key)

    if user.is_2fa_enabled:
        return {"requires_2fa": True, "email": user.email}

    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value,
        }
    )

    return {"access_token": access_token, "role": user.role.value}
