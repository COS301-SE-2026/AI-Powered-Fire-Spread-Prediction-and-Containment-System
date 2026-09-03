import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


def send_email(to: str, subject: str, body: str) -> None:
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_HOST, SMTP_USER and SMTP_PASSWORD must be set to send email"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

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