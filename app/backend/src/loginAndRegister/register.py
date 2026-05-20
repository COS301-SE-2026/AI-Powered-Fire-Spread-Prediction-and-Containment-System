from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from db import get_db_connection
from auth import hash_password

router = APIRouter(prefix="/api", tags=["Auth"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str
    id_number: str
    licence_number: Optional[str] = None
    role: str = "User"

class MessageResponse(BaseModel):
    message: str

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    """Register a new user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            existing = cur.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            hashed = hash_password(user.password)
            cur.execute(
                """INSERT INTO users 
                   (email, hashed_password, name, surname, id_number, licence_number, role)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (user.email, hashed, user.name, user.surname, user.id_number,
                 user.licence_number, user.role)
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
    return {"message": "User created successfully"}