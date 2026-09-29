import pyotp
import uuid
from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.users import User
from app.backend.src.schemas.auth import Two_FA_Verify_Request, CompleteRegistrationRequest
from app.backend.src.enums.user_role import UserRole
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.services.auth.pending_registration import (
    get_pending_registration,
    delete_pending_registration
)

def setup_2fa(username: str, db: Session):
    user = db.query(User).filter(User.email == username).first()

    if not user:
        raise ValueError("User is not found or does not exist")

    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.is_2fa_enabled = False
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


def complete_registration(db: Session, request: CompleteRegistrationRequest):
    pending = get_pending_registration(request.registration_token)
    if not pending:
        raise ValueError("Registration expired or not found, please register again")

    totp = pyotp.TOTP(pending["totp_secret"])
    if not totp.verify(request.code, valid_window=1):
        raise ValueError("Invalid code")

    requested_role = UserRole(pending["requested_role"])

    new_user = User(
        id=f"usr_{uuid.uuid4().hex[:8]}",
        email=pending["email"],
        hashed_password=pending["hashed_password"],
        name=pending["name"],
        surname=pending["surname"],
        id_number=pending["id_number"],
        is_active=True,
        is_2fa_enabled=True,
        totp_secret=pending["totp_secret"]
    )
    db.add(new_user)

    pending_approval = requested_role == UserRole.firefighter

    if pending_approval:
        db.add(
            RoleRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                user_id=new_user.id,
                requested_role=UserRole.firefighter,
                current_role=UserRole.user,
                status=RequestStatus.pending
            )
        )

    db.commit()
    delete_pending_registration(request.registration_token)

    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": new_user.id, "role": new_user.role.value}
    )
    
    return {"access_token": access_token, "role": new_user.role.value, "pending_approval": pending_approval}