# MinIO client and upload/presign logic
import os
import uuid
from typing import Optional


import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Dev -> STORAGE_ENDPOINT_URL=http://minio:9000 + access keys
# staging/prod -> endpoint and keys gotten via real s3 instance role
ENDPOINT = os.getenv("STORAGE_ENDPOINT_URL") or None
PUBLIC_ENDPOINT = os.getenv("STORAGE_PUBLIC_ENDPOINT_URL") or ENDPOINT
REGION = os.getenv("AWS_REGION", "us-east-1")

KEYS = {}
if os.getenv("STORAGE_ACCESS_KEY"):
    KEYS = {
        "aws_access_key_id": os.environ["STORAGE_ACCESS_KEY"],
        "aws_secret_access_key": os.environ["STORAGE_SECRET_KEY"]
    }

CFG = Config(signature_version="s3v4", s3={"addressing_style": "path" if ENDPOINT else "virtual"})

s3 = boto3.client("s3", endpoint_url=ENDPOINT, region_name=REGION, config=CFG, **KEYS)
presign_client = boto3.client("s3", endpoint_url=PUBLIC_ENDPOINT, region_name=REGION, config=CFG, **KEYS) # signs url against host browser

BUCKET = os.environ["STORAGE_BUCKET"]
PREFIX = os.getenv("ENVIRONMENT", "dev") # prod and staging share a bucket
ALLOWED_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
MAX_SIZE_MB = 10

def ensure_bucket():
    if not ENDPOINT:
        return
    try:
        s3.head_bucket(Bucket=BUCKET)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET)


def validate_image(content_type: str, size_bytes: int):
    if content_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type")
    if size_bytes > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError("File size too large")


def upload_image(filename: str, content_type: str, contents: bytes) -> str:
    """Uploads the image, returns object_key to store in FireReports.image_url"""
    validate_image(content_type, len(contents))
    object_key = f"{PREFIX}/reports/{uuid.uuid4()}.{ALLOWED_TYPES[content_type]}"
    s3.put_object(Bucket=BUCKET, Key=object_key, Body=contents, ContentType=content_type)
    return object_key


def get_presigned_url(
    object_key: Optional[str], expires_minutes: int = 60
) -> Optional[str]:
    if not object_key:
        return None
    if object_key.startswith(("http://", "https://")):
        return object_key # e.g. seed placeholders
    return presign_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": object_key},
        ExpiresIn=expires_minutes * 60,
    )


def delete_photo(object_key: str):
    s3.delete_object(Bucket=BUCKET, Key=object_key)