from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
import random
import string
from datetime import datetime, timezone

router = APIRouter(prefix="/api/reports", tags=["Reports"])

StatusType = Literal["received", "pending", "verified", "notified"]

STATUS_INDEX = {
    "received": 0,
    "pending":  1,
    "verified": 2,
    "notified": 3,
}

class FireReport(BaseModel):
    reference_number:    str
    location:            str
    description:         str                = ""
    lat:                 float | None       = None
    lng:                 float | None       = None
    boundary_radius_km:  float | None       = None
    status:              StatusType         = "received"
    status_index:        int                = 0
    submitted_at:        str

class FireReportCreate(BaseModel):
    location:            str
    description:         Optional[str]      = ""
    lat:                 Optional[float]    = None
    lng:                 Optional[float]    = None
    boundary_radius_km:  Optional[float]    = None

class StatusUpdate(BaseModel):
    status: StatusType

# MOCK DATA
FIRE_REPORTS: List[dict] = [
    {
        "reference_number":   "FW-SEED001",
        "location":           "Johannesburg CBD, Gauteng, South Africa",
        "description":        "Grass fire spreading towards informal settlement.",
        "lat":                -26.195246,
        "lng":                28.034088,
        "boundary_radius_km": 1.5,
        "status":             "verified",
        "status_index":       2,
        "submitted_at":       "2025-05-21T08:00:00+00:00",
    },
    {
        "reference_number":   "FW-SEED002",
        "location":           "Pretoria East, Gauteng, South Africa",
        "description":        "Warehouse fire with possible chemical storage.",
        "lat":                -25.7479,
        "lng":                28.2293,
        "boundary_radius_km": 0.5,
        "status":             "pending",
        "status_index":       1,
        "submitted_at":       "2025-05-21T09:30:00+00:00",
    },
    {
        "reference_number":   "FW-SEED003",
        "location":           "Soweto, Gauteng, South Africa",
        "description":        "Industrial fire, units on scene.",
        "lat":                -26.267,
        "lng":                27.858,
        "boundary_radius_km": 3.0,
        "status":             "received",
        "status_index":       0,
        "submitted_at":       "2025-05-21T10:15:00+00:00",
    },
]


def _generate_ref() -> str:
    """Mirrors the frontend's generateMockRef(): FW-YYYYMMDD-XXXXX"""
    date  = datetime.now(timezone.utc).strftime("%Y%m%d")
    token = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"FW-{date}-{token}"


@router.post("", response_model=FireReport, status_code=201)
def submit_report(payload: FireReportCreate):
    """
    Called by ReportDetailsForm's onSubmit (via ReportPage.handleSubmit).
    Returns reference_number and status_index=0 so the frontend can:
      - setActiveRefNum(report.reference_number)
      - setStatusIndex(report.status_index)
    """
    new_report = {
        "reference_number":   _generate_ref(),
        "location":           payload.location,
        "description":        payload.description or "",
        "lat":                payload.lat,
        "lng":                payload.lng,
        "boundary_radius_km": payload.boundary_radius_km,
        "status":             "received",
        "status_index":       0,
        "submitted_at":       datetime.now(timezone.utc).isoformat(),
    }
    FIRE_REPORTS.append(new_report)
    return new_report


@router.get("", response_model=List[FireReport])
def list_reports():
    return FIRE_REPORTS


@router.get("/{reference_number}", response_model=FireReport)
def get_report(reference_number: str):
    for report in FIRE_REPORTS:
        if report["reference_number"] == reference_number:
            return report
    raise HTTPException(status_code=404, detail="Report not found")


@router.post("/{reference_number}/advance", response_model=FireReport)
def advance_status(reference_number: str):
    """Move the report one step forward through the 4 ReportStatus steps."""
    for report in FIRE_REPORTS:
        if report["reference_number"] == reference_number:
            if report["status_index"] >= 3:
                raise HTTPException(status_code=400, detail="Report already at final status")
            next_index  = report["status_index"] + 1
            next_status = [k for k, v in STATUS_INDEX.items() if v == next_index][0]
            report["status"]       = next_status
            report["status_index"] = next_index
            return report
    raise HTTPException(status_code=404, detail="Report not found")


@router.post("/{reference_number}/status", response_model=FireReport)
def set_status(reference_number: str, body: StatusUpdate):
    """Set a report to any specific status directly (admin/dispatch use)."""
    for report in FIRE_REPORTS:
        if report["reference_number"] == reference_number:
            report["status"]       = body.status
            report["status_index"] = STATUS_INDEX[body.status]
            return report
    raise HTTPException(status_code=404, detail="Report not found")