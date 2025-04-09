import logging
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


async def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    """Send an email using SMTP.
    
    Args:
        to_email: Recipient email address.
        subject: Email subject.
        body: Email body in HTML format.
        
    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        message = MIMEText(body, "html")
        message["From"] = settings.SMTP_USERNAME
        message["To"] = to_email
        message["Subject"] = subject

        async with aiosmtplib.SMTP(
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            use_tls=True,
        ) as smtp:
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(message)
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_verification_email(
    email: str,
    verification_token: str,
    verification_url: Optional[str] = None,
) -> bool:
    """Send email verification email.
    
    Args:
        email: User's email address.
        verification_token: Email verification token.
        verification_url: Optional custom verification URL.
        
    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    if not verification_url:
        verification_url = f"http://localhost:8000/api/v1/auth/verify-email/{verification_token}"

    template = env.get_template("email_verification.html")
    html_content = template.render(verification_url=verification_url)

    return await send_email(
        to_email=email,
        subject="Email Verification",
        body=html_content,
    )


async def send_password_reset_email(
    email: str,
    reset_token: str,
    reset_url: Optional[str] = None,
) -> bool:
    """Send password reset email.
    
    Args:
        email: User's email address.
        reset_token: Password reset token.
        reset_url: Optional custom reset URL.
        
    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    if not reset_url:
        reset_url = f"http://localhost:8000/reset-password?token={reset_token}"

    template = env.get_template("password_reset.html")
    html_content = template.render(reset_url=reset_url)

    return await send_email(
        to_email=email,
        subject="Password Reset Request",
        body=html_content,
    )
