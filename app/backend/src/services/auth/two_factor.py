import pyotp
from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.users import User
from app.backend.src.schemas.auth import Two_FA_Verify_Request


def setup_2fa(username: str, db: Session):
    user = db.query(User).filter(User.email == username).first()

    if not user:
        raise ValueError("User is not found or does not exist")

    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.is_2fa_enabled = True
    db.commit()

    otpauth_url = pyotp.TOTP(secret).provisioning_uri(
        name=username, issuer_name="FireAway"
    )
    return {"otpauth_url": otpauth_url}


def verify_2fa(db: Session, request: Two_FA_Verify_Request):
    user = (
        db.query(User)
        .filter(User.email == request.username, User.is_2fa_enabled == True)
        .first()
    )

    if not user:
        raise ValueError("User does not exist or not found")

    if not user.totp_secret:
        raise ValueError("two factor auth is not enabled")

    totp = pyotp.TOTP(user.totp_secret)

    if not totp.verify(request.code, valid_window=1):
        raise ValueError("Invalid code")

    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value,
        }
    )

    return {"access_token": access_token, "role": user.role.value}
