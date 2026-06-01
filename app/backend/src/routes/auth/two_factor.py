from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas.auth import Two_FA_Create_Response, Two_FA_Verify_Request
from services.auth.two_factor import setup_2fa, verify_2fa

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/setup-2fa", response_model=Two_FA_Create_Response)
def setup_2fa_route(username:str, db:Session = Depends(get_db)):
    try:
        return setup_2fa(username, db)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    
@router.post("/verify-2fa")
def verify_2fa_route(request:Two_FA_Verify_Request, db:Session = Depends(get_db)):
    try:
        return verify_2fa(db, request)
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err))