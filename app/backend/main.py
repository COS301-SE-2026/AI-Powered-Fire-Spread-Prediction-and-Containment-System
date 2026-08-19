import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from ai.simulation_api import router as simulation_router
from db import init_db
from routes import image_uploads

from routes.admin import router as admin_router
from routes.firefighter import router as firefighter_router
from routes.users import router as user_router
from routes.guests import router as guest_router
from routes.auth import router as auth_router

from seed import seed
from services.storage import ensure_bucket

@asynccontextmanager
async def liefspan(app: FastAPI):
    ensure_bucket()

    if os.environ.get("SKIP_DB_INIT") != "1":
        init_db()

    if os.environ.get("SKIP_SEED") != "1":
        seed()

    yield

app = FastAPI(
    title="FireAway API",
    description="Backend for the AI-Powered Fire Spread Prediction and Containment System",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=liefspan
)

# app = FastAPI(root_path="/api")

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js local development URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(firefighter_router)
app.include_router(user_router)
app.include_router(guest_router)
app.include_router(image_uploads.router)
app.include_router(simulation_router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "FireAway API is running and connected to PostgreSQL.",
    }


@app.get("/api/ping")
def ping():
    return {"message": "pong"}


@app.get("/health")
def health_check():
    return {"status": "ok"}



