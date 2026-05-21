import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from db import get_db_connection, init_db
from auth import hash_password, verify_password, create_access_token
from fastapi.middleware.cors import CORSMiddleware
from TwoFactorAuth.twoStepAuth import router as auth_router
from loginAndRegister.register import router as register_router
from loginAndRegister.login import router as login_router
from admin import adminRoleApproval
from reportfire import reportFire

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
@app.on_event("startup")
def startup():
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("Running without database — mock data only.")

@app.get("/health", response_model=PingResponse, tags=["Health"])
def health():
    return {
        "status": "ok",
        "db_host": os.environ.get("DB_HOST", "postgres"),
    }

@app.get("/api/ping", tags=["Health"])
def ping():
    return {"message": "pong"}

# Include admin role approval routes
app.include_router(adminRoleApproval.router)

app.include_router(register_router)
app.include_router(login_router)

app.include_router(reportFire.router)
