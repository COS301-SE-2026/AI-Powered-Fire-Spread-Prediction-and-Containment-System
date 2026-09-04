import os
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.backend.src.ai.simulation_api import router as simulation_router
from app.backend.db import init_db, engine
from app.backend.src.routes import image_uploads
from app.backend.src.routes import router as notifications_and_location_router

from app.backend.src.routes.admin import router as admin_router
from app.backend.src.routes.firefighter import router as firefighter_router
from app.backend.src.routes.users import router as user_router
from app.backend.src.routes.guests import router as guest_router
from app.backend.src.routes.auth import router as auth_router

from app.backend.startup_migrations import run_startup_migrations
from app.backend.seed import seed
from app.backend.src.services.storage import ensure_bucket
from app.backend.src.services.notifications.websocket_manager import set_main_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    lifespan=lifespan,
)

# app = FastAPI(root_path="/api")


@app.on_event("startup")
def on_startup():
    run_startup_migrations(engine)


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
app.include_router(notifications_and_location_router)


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


@app.on_event("startup")
def startup():
    ensure_bucket()


@app.on_event("startup")
async def capture_main_loop():
    set_main_loop(asyncio.get_running_loop())
