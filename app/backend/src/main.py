import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from db import get_db_connection, init_db
from auth import hash_password, verify_password, create_access_token
from fastapi.middleware.cors import CORSMiddleware
from TwoFactorAuth.twoStepAuth import router as auth_router

app = FastAPI(
    title="Fire Spread Prediction API",
    description="API for fire spread prediction, containment planning, and PostGIS-backed geo data.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str
    id_number: str
    licence_number: Optional[str] = None  # for fierefighters
    role: str = "User"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str

app.include_router(auth_router)

class PingResponse(BaseModel):
    status: str
    db_host: str
@app.post("/api/login", tags=["Auth"])
def login(user: UserLogin):
    """Authenticate user and return JWT token or require 2FA."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, hashed_password, is_2fa_enabled FROM users WHERE email = %s",
                (user.email,)
            )
            db_user = cur.fetchone()
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not verify_password(user.password, db_user["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # If 2FA is enabled, do not issue token yet
            if db_user["is_2fa_enabled"]:
                return {
                    "message": "2FA required",
                    "user_id": db_user["id"],
                    "email": db_user["email"]
                }

            # No 2FA – issue JWT immediately
            access_token = create_access_token(data={"sub": db_user["email"], "user_id": db_user["id"]})
            return {"access_token": access_token, "token_type": "bearer"}
@app.on_event("startup")
def startup():
    init_db()

@app.get("/health", response_model=PingResponse, tags=["Health"])
def health():
    return {
        "status": "ok",
        "db_host": os.environ.get("DB_HOST", "postgres"),
    }

@app.get("/api/ping", tags=["Health"])
def ping():
    return {"message": "pong"}


@app.post("/api/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user: UserRegister):
    """Register a new user with all fields."""
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
class TwoFactorVerifyRequest(BaseModel):
    email: str
    code: str

@app.post("/api/verify-2fa", response_model=TokenResponse, tags=["Auth"])
def verify_2fa(payload: TwoFactorVerifyRequest):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, totp_secret FROM users WHERE email = %s", (payload.email,))
            db_user = cur.fetchone()
            if not db_user or not db_user["totp_secret"]:
                raise HTTPException(status_code=404, detail="User not found or 2FA not enabled")
            
            import pyotp
            totp = pyotp.TOTP(db_user["totp_secret"])
            if not totp.verify(payload.code, valid_window=1):
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
            
            access_token = create_access_token(data={"sub": db_user["email"], "user_id": db_user["id"]})
            return {"access_token": access_token, "token_type": "bearer"}