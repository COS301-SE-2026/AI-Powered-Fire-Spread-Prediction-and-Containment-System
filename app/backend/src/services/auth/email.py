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

# ---- Role request approval email notification
def send_role_approved_email(to: str, name: str, role: str) -> None:
    role_label = role.replace("_", " ").title()
    body = (
        f"<p>Hello {name},</p>"
        f"<p>Your request for the <strong>{role_label}</strong> role has been approved. "
        f"Your account not has {role_label} access.</p>"
        f"<p><a href='{FRONTEND_URL}/login'>Login</a> to get started. "
        f"You may need to logout and back in for the changes to take effect.</p>"
        f"<p>Best regards,<br>The Fire Away Team</p>"
    )
    send_email(to, f"Your {role_label} role request has been approved", body)
    
def send_role_rejected_email(to: str, name: str, role: str) -> None:
    role_label = role.replace("_", " ").title()
    body = (
        f"<p>Hello {name},</p>"
        f"<p>Unfortunately, your request for the <strong>{role_label}</strong> role "
        f"was been rejected. Your account role has not been changed.</p>"
        f"<p>If you have any questions, please contact an administrator.</p>"
        f"<p>Best regards,<br>The Fire Away Team</p>"
    )
    send_email(to, f"Your {role_label} role request has been rejected", body)
    
def send_role_revoked_email(to: str, name: str, role: str) -> None:
    role_label = role.replace("_", " ").title()
    body = (
        f"<p>Hello {name},</p>"
        f"<p>Your <strong>{role_label}</strong> role has been revoked bu an administrator. "
        f"Your account has been returned to it's previous role.</p>"
        f"<p>If you believe this to be a mistake, please contact an administrator.</p>"
        f"<p>Best regards,<br>The Fire Away Team</p>"
    )
    send_email(to, f"Your {role_label} role has been revoked", body)