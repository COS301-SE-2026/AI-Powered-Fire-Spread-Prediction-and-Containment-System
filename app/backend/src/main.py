from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from seed import seed
from user.user import router as user_router
from admin.adminRoleApproval import router as admin_router
from report.fireReports import router as fire_reports_router
from loginAndRegister.register import router as register_router
from loginAndRegister.login import router as login_router

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

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(fire_reports_router)
app.include_router(register_router)
app.include_router(login_router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "FireAway API is running and connected to PostgreSQL."}