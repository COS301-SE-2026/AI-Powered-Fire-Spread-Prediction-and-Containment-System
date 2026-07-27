from sqlalchemy.orm import Session
from models.users import User
from schemas.auth import LoginRequest
from auth import verify_password, create_access_token

def login_user(db:Session, request:LoginRequest):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise ValueError("Email incorrect please enter valid email")

    if not verify_password(request.password, user.hashed_password):
        raise ValueError("Password is incorrect please try again")

    if user.is_2fa_enabled:
        return {"requires_2fa": True, "email": user.email}

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id, "role": user.role.value,})

    return {"access_token": access_token, "role": user.role.value}
