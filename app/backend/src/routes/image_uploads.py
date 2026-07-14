from fastapi import APIRouter, UploadFile, HTTPException
from services.storage import upload_image

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])

@router.post("/image")
async def upload_image(file: UploadFile):
    """"""