import os
import boto3
from botocore.exceptions import ClientError

AWS_REGION     = os.getenv("AWS_REGION", "us-east-1")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL")
if not SES_SENDER_EMAIL:
    raise RuntimeError("SES_SENDER_EMAIL is not set")

_ses_client = boto3.client("ses", region_name=AWS_REGION)


def _send(to_email: str, subject: str, body_text: str, body_html: str) -> None:
    try:
        _ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
    except ClientError as e:
        raise RuntimeError(
            f"Failed to send email: {e.response['Error']['Message']}"
        ) from e


def send_verification_email(to_email: str, verification_link: str) -> None:
    """Sends account email verification link via AWS SES."""
    _send(
        to_email=to_email,
        subject="Verify your Pizzasale account",
        body_text=(
            f"Welcome to Pizzasale!\n\n"
            f"Please verify your email by visiting:\n{verification_link}\n\n"
            f"If you didn't create this account, ignore this email."
        ),
        body_html=f"""
<html><body>
  <div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
    <h2 style="color:#FF6B35">Welcome to Pizzasale! 🍽️</h2>
    <p>Please verify your email by clicking the button below:</p>
    <a href="{verification_link}"
       style="display:inline-block;background:#FF6B35;color:#fff;padding:12px 24px;
              border-radius:8px;text-decoration:none;font-weight:600;margin:12px 0">
      Verify my email
    </a>
    <p style="color:#6b7280;font-size:13px">
      If you didn't create this account, you can ignore this email.
    </p>
  </div>
</body></html>""",
    )


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """Sends password reset link via AWS SES. Token expires in 1 hour."""
    _send(
        to_email=to_email,
        subject="Reset your Pizzasale password",
        body_text=(
            f"You requested a password reset for your Pizzasale account.\n\n"
            f"Click the link below to reset your password (valid for 1 hour):\n"
            f"{reset_link}\n\n"
            f"If you didn't request this, ignore this email — your password is unchanged."
        ),
        body_html=f"""
<html><body>
  <div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:24px">
    <h2 style="color:#1A1A2E">Reset your password 🔐</h2>
    <p>You requested a password reset for your Pizzasale account.</p>
    <p>Click the button below to choose a new password.
       This link is valid for <strong>1 hour</strong>.</p>
    <a href="{reset_link}"
       style="display:inline-block;background:#FF6B35;color:#fff;padding:12px 24px;
              border-radius:8px;text-decoration:none;font-weight:600;margin:12px 0">
      Reset my password
    </a>
    <p style="color:#6b7280;font-size:13px">
      If you didn't request this, ignore this email — your password hasn't changed.
    </p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
    <p style="color:#6b7280;font-size:13px">Pizzasale — fresh Nigerian flavours.</p>
  </div>
</body></html>""",
    )
