# This is for any route that needs to check if person is logged and has correct role
# Reads cookie, decodes token and either blocks or allows request
from fastapi import Depends, HTTPException, Request
from jose import jwn, JWTError
from sqlalchemy.orm import Session
from db import get_db
from models.users import User
from auth import SECRET_KEY, ALGORITHM

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    
    if not token:
        auth_header = request.headers.get("Autherization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            
    if not token:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid/Expired Token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def require_role(*allowed_roles):
    """ Usage on any route that needs restricting:
        @router.get("/dashboard/summary)
        def get_summary(user: User = Depends(require_role(UserRole.admin))): ...
    """
    
    def role_checker(user: User = Depends(require_role(UserRole.admin))):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
        return user
    
    return role_checker
    