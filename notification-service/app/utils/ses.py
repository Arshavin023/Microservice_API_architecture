import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

AWS_REGION     = os.getenv("AWS_REGION", "us-east-1")
SES_SENDER     = os.getenv("SES_SENDER_EMAIL")

if not SES_SENDER:
    raise RuntimeError("SES_SENDER_EMAIL is not set")

_ses_client = None


def _get_client():
    global _ses_client
    if _ses_client is None:
        _ses_client = boto3.client("ses", region_name=AWS_REGION)
    return _ses_client


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> bool:
    """
    Send an email via AWS SES.
    Returns True on success, False on failure (logged but not raised —
    a failed notification email must never crash the worker or prevent
    other events from being processed).
    """
    try:
        _get_client().send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                },
            },
        )
        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "MessageRejected":
            # SES sandbox — recipient not verified. Log as warning, not error,
            # since this is expected in test/sandbox mode.
            logger.warning(
                f"SES sandbox: {to_email} is not a verified recipient. "
                f"Email not sent. Add to SES verified addresses or request production access."
            )
        else:
            logger.error(f"SES error sending to {to_email}: {e}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {e}")
        return False
