import smtplib
from email.message import EmailMessage

from config import ALERT_FROM_EMAIL, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME


def send_email(to_address: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP. Raises on failure; callers are
    responsible for catching and recording the failure rather than crashing."""
    message = EmailMessage()
    message["From"] = ALERT_FROM_EMAIL
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
