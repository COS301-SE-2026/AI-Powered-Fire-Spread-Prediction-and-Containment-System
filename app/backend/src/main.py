import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import init_db
from routes import image_uploads
from routes.admin import admin_dashboard
from routes.admin.analytics import router as admin_analytics_router
from routes.admin.fire_reports import router as admin_fire_router
from routes.admin.role_requests import router as admin_roles_router
from routes.auth.login import router as login_router
from routes.auth.logout import router as logout_router
from routes.auth.register import router as register_router
from routes.auth.two_factor import router as two_factor_router
from routes.firefighter.fire_reports import router as firefighter_reports
from routes.firefighter.firefighter_dashboard import \
    router as firefighter_dashboard
from routes.guests.fire_reports import router as guest_fire_router
from routes.guests.guests_dashboard import router as guests_dashboard_router
from routes.users.fire_reports import router as user_fire_router
from seed import seed
from services.storage import ensure_bucket

if os.environ.get("SKIP_DB_INIT") != "1":
    init_db()

if os.environ.get("SKIP_SEED") != "1":
    seed()

app = FastAPI(
    title="FireAway API",
    description="Backend for the AI-Powered Fire Spread Prediction and Containment System",
    version="1.0.0",
    redirect_slashes=False,
)

#app = FastAPI(root_path="/api")

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

app.include_router(user_fire_router)
app.include_router(admin_roles_router)
app.include_router(admin_fire_router)
app.include_router(guest_fire_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(two_factor_router)
app.include_router(admin_analytics_router)
app.include_router(admin_dashboard.router)
app.include_router(firefighter_reports)
app.include_router(firefighter_dashboard)
app.include_router(logout_router)
app.include_router(image_uploads.router)
app.include_router(guests_dashboard_router)


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
    
