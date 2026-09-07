from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from dependencies.auth import get_current_user_optional
from models.users import User
from services.storage import upload_image
from services.verification.photo_hashing import hash_photo

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])


@router.post(
    "/photo", responses={400: {"description": "Invalid file type or file size to big"}}
)
async def upload_image_endpoint(
    file: UploadFile,
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
):
    """Anonymous image upload. Returns object_key string
    Frontend passes this to FireReportCase.image_url  when calls POST /api/users/reported-fires
    """

    contents = await file.read()
    try:
        object_key = upload_image(file.filename, file.content_type, contents)
    except ValueError as e:
        raise HTTPException(400, str(e))

    photo_hash = hash_photo(contents)
    return {"object_key": object_key, "photo_hash": photo_hash}
