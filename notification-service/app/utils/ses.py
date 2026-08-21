import os
import logging
import resend

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL   = os.getenv("SES_SENDER_EMAIL")  # kept var name for compose compatibility

if not RESEND_API_KEY:
    raise RuntimeError("RESEND_API_KEY is not set")
if not SENDER_EMAIL:
    raise RuntimeError("SES_SENDER_EMAIL is not set")

resend.api_key = RESEND_API_KEY


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> bool:
    """
    Send an email via Resend.
    Returns True on success, False on failure (logged but not raised —
    a failed notification email must never crash the worker or prevent
    other events from being processed).
    """
    try:
        resend.Emails.send({
            "from": SENDER_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        })
        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Resend error sending to {to_email}: {e}")
        return False
