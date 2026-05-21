from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from seed import seed
from admin.adminRoleApproval import router as admin_router

init_db()

seed()

app = FastAPI(
    title="FireAway API",
    description="Backend for the AI-Powered Fire Spread Prediction and Containment System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js local development URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "FireAway API is running and connected to PostgreSQL."}