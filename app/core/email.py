import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from app.core.config import settings


def send_verification_email(email: str, token: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = email
        msg["Subject"] = "Email Verification"

        verification_link = f"http://localhost:8000/api/v1/auth/verify-email/{token}"
        body = f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>Please click the following link to verify your email:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>If you did not request this verification, please ignore this email.</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send verification email: {str(e)}"
        )


def send_password_reset_email(email: str, token: str):
    """Send a password reset email to the user.
    
    Args:
        email (str): User's email address
        token (str): Password reset token
        
    Raises:
        HTTPException: If email sending fails
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = email
        msg["Subject"] = "Password Reset Request"

        reset_link = f"http://localhost:8000/api/v1/auth/reset-password/{token}"
        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Click the link below to proceed:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>If you did not request this password reset, please ignore this email.</p>
                <p>This link will expire in 1 hour.</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send password reset email: {str(e)}"
        )
