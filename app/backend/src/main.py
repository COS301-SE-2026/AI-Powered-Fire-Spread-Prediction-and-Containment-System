import os
from fastapi import FastAPI
from pydantic import BaseModel
from admin import adminRoleApproval

app = FastAPI(
    title="Fire Spread Prediction API",
    description="API for fire spread prediction, containment planning, and PostGIS-backed geo data.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

class PingResponse(BaseModel):
    status: str
    db_host: str

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