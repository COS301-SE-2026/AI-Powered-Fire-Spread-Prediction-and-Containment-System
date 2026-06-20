from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas.auth import RegisterRequest, MsgResponse
from services.auth.register import register_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=MsgResponse, status_code=201)
def register_route(request:RegisterRequest, db:Session = Depends(get_db)):
    try:
        register_user(db, request)
        return {"message": "User succefully registered"}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    