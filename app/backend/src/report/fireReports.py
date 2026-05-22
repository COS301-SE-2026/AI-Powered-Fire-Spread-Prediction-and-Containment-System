from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

from db import get_db
from models import FireReportModel, ReportStatus, User

router = APIRouter(prefix="/api/fire-reports", tags=["Fire Reports"])

# ── Self-contained auth ───────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this")
ALGORITHM  = "HS256"
_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)

def _get_optional_user(
    token: Optional[str] = Depends(_optional_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None
    return db.query(User).filter(
        (User.id == user_id) | (User.email == user_id)
    ).first()

def _get_current_user(
    token: Optional[str] = Depends(_optional_scheme),
    db: Session = Depends(get_db),
) -> User:
    user = _get_optional_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# ── Schemas ───────────────────────────────────────────────────────────────────
class FireReportOut(BaseModel):
    reference_number: str
    user_id: Optional[str] = None
    location_text: str
    description: str
    location_geom: str
    boundary_radius_km: float
    status: ReportStatus
    status_index: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FireReportCreate(BaseModel):
    location_text: str
    description: str
    location_geom: str
    boundary_radius_km: float = 1.0

class FireReportStatusUpdate(BaseModel):
    status: ReportStatus

# ── Helpers ───────────────────────────────────────────────────────────────────
STATUS_INDEX = {
    ReportStatus.received: 0,
    ReportStatus.pending:  1,
    ReportStatus.verified: 2,
    ReportStatus.notified: 3,
}

def _next_reference(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"FR-{year}-"
    last = (
        db.query(FireReportModel)
        .filter(FireReportModel.reference_number.like(f"{prefix}%"))
        .order_by(desc(FireReportModel.reference_number))
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.reference_number.split("-")[-1]) + 1
        except ValueError:
            pass
    return f"{prefix}{seq:03d}"

# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[FireReportOut])
def list_reports(
    status: Optional[ReportStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(FireReportModel)
    if status:
        q = q.filter(FireReportModel.status == status)
    return q.order_by(desc(FireReportModel.status_index)).offset(skip).limit(limit).all()


@router.get("/{reference_number}", response_model=FireReportOut)
def get_report(reference_number: str, db: Session = Depends(get_db)):
    report = db.query(FireReportModel).filter(
        FireReportModel.reference_number == reference_number
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/", response_model=FireReportOut, status_code=201)
def create_report(
    body: FireReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(_get_optional_user),  # ← changed
):
    report = FireReportModel(
        reference_number=_next_reference(db),
        user_id=current_user.id if current_user else None,
        location_text=body.location_text,
        description=body.description,
        location_geom=body.location_geom,
        boundary_radius_km=body.boundary_radius_km,
        status=ReportStatus.received,
        status_index=0,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.patch("/{reference_number}/status", response_model=FireReportOut)
def update_status(
    reference_number: str,
    body: FireReportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),  # ← changed
):
    if current_user.role not in ("admin", "firefighter"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    report = db.query(FireReportModel).filter(
        FireReportModel.reference_number == reference_number
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = body.status
    report.status_index = STATUS_INDEX[body.status]
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{reference_number}", status_code=204)
def delete_report(
    reference_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),  # ← changed
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    report = db.query(FireReportModel).filter(
        FireReportModel.reference_number == reference_number
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()