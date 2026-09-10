import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
AWS_REGION = os.environ.get("SES_AWS_REGION", "us-east-1")
SES_SENDER_EMAIL = os.environ.get("SES_SENDER_EMAIL", "")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

_ses_client = boto3.client(
    "ses",
    region_name=AWS_REGION,
    aws_access_key_id=os.environ.get("SES_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("SES_AWS_SECRET_ACCESS_KEY"),
    )

def send_email(to: str, subject: str, body: str) -> None:
    if not SES_SENDER_EMAIL:
        raise RuntimeError("SES_SENDER_EMAIL is not set in environment variables.")
    try:
        _ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": body}},
            },
        )
    except NoCredentialsError as e:
        raise RuntimeError(
            "AWS credentials not found -- check AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY"
        ) from e
    except ClientError as e:
        raise RuntimeError(f"Failed to send email: {e.response['Error']['Message']}") from e

def send_password_reset_email(to: str, token: str) -> None:
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    body = (
        f"Hello,\n\n"
        f"You requested a password reset. Please click the link below to reset your password:\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\n"
        f"The Team"
    )
    send_email(to, "Password Reset Request", body)
