# MinIO client and upload/presign logic
import os
import uuid
from datetime import timedelta
from io import BytesIO
from minio import Minio
from minio.error import S3Error

minio_client = Minio(
    os.environ["MINIO_ENDPOINT"],
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    secure=os.environ.get("MINIO_SECURE", "false").lower() == "true",
)

BUCKET = os.environ["MINIO_BUCKET"]
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10

def ensure_bucket():
    if not minio_client.bucket_exists(BUCKET):
        minio_client.make_bucket(BUCKET)

def validate_image(content_type: str, size_bytes: int):
    if content_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type")
    if size_bytes > MAX_SIZE_MB*1024*1024:
        raise ValueError("File size too large")
    
def upload_image(report_id: str, filename: str, content_type: str, contents: bytes) -> str:
    """Uploads to MinIO, returns object_key to store in DB"""
    validate_image(content_type, len(contents))
    ext = filename.split(".")[-1]
    object_key = f"{report_id}/{uuid.uuid4()}.{ext}"
    
    minio_client.put_object(
        BUCKET,
        object_key,
        data=BytesIO(contents),
        length=len(contents),
        content_type=content_type,
    )
    
    return object_key

def get_presigned_url(object_key: str, expires_minutes: int = 10) -> str:
    return minio_client.presigned_get_object(
        BUCKET,
        object_key,
        expires=timedelta(minutes=expires_minutes),
    )
    
def delete_photo(object_key: str):
    minio_client.remove_object(BUCKET, object_key)
    