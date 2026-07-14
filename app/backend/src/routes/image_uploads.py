from fastapi import APIRouter, UploadFile, HTTPException, Depends
from services.storage import upload_image
from typing import Optional
from dependencies.auth import get_current_user_optional
from models.users import User

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])

@router.post("/image")
async def upload_image(file: UploadFile, current_user: Optional[User]):
    """ Anonymous image upload for guests. Returns an object_key string. 
        Frontend passes this to FireReportCreate.image_url when calls POST /api/users/reported-fires
    """
    
    contents = await file.read()
    try:
        object_key = upload_image(file.filename, file.content_type, contents)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    return {"object_key": object_key}