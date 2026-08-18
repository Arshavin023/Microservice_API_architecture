import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from pydantic import BaseModel
from app.schemas.auth_schema import (
    SignUpModel,
    LoginModel,
    TokenResponse,
    RefreshResponse,
)
from app.services.auth_service import AuthService, AuthError
from app.models.user import UserAuth
from app.db.session import get_db
from app.utils.verification import (
    generate_verification_token,
    confirm_verification_token,
    generate_reset_token,
    confirm_reset_token,
)
from app.utils.email import send_verification_email, send_password_reset_email
from fastapi_jwt_auth2 import AuthJWT
from werkzeug.security import generate_password_hash
from sqlalchemy.future import select


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


router = APIRouter(prefix="/auth", tags=["Auth"])

# Base URL the verification link points back to. In this local-dev
# setup, the link targets auth-service directly. Once there's an API
# gateway or public-facing domain, point this there instead.
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8001")


@router.post("/register")
async def register(user: SignUpModel, db: AsyncSession = Depends(get_db)):
    try:
        created_user = await AuthService.register(db, user)
    except AuthError as e:
        raise HTTPException(status_code=409, detail=str(e))

    token = generate_verification_token(created_user.email)
    verification_link = f"{APP_BASE_URL}/auth/verify-email?token={token}"

    try:
        send_verification_email(created_user.email, verification_link)
    except RuntimeError as e:
        # The user account was already created successfully — don't
        # roll that back just because the email failed to send (e.g.
        # SES sandbox mode rejecting an unverified recipient). Surface
        # this clearly rather than silently swallowing it, since the
        # user otherwise has no way to verify their account.
        print("SEND VERIFICATION EMAIL ERROR:", str(e))
        raise HTTPException(
            status_code=201,
            detail="Account created, but the verification email could not be sent. Contact support.",
        )

    return {"message": "User created. Check your email to verify your account."}


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = confirm_verification_token(token)

    if not email:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification link"
        )

    activated = await AuthService.activate_user_by_email(db, email)

    if not activated:
        raise HTTPException(
            status_code=404, detail="No account found for this verification link"
        )

    return {"message": "Email verified. You can now log in."}


@router.post("/login", response_model=TokenResponse)
async def login(
    user: LoginModel, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()
):
    db_user = await AuthService.authenticate(db, user)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_active:
        raise HTTPException(
            status_code=403, detail="Please verify your email before logging in"
        )

    access = Authorize.create_access_token(
        subject=db_user.username,
        expires_time=timedelta(minutes=15),
        user_claims={
            "is_staff": db_user.is_staff,
            "user_id": str(db_user.id),  # embedded so downstream services can scope
        },  # operations to a user without knowing their username
    )

    refresh = Authorize.create_refresh_token(
        subject=db_user.username, user_claims={"user_id": str(db_user.id)}
    )

    return {"access": access, "refresh": refresh, "token_type": "bearer"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    claims = Authorize.get_raw_jwt()
    user_id = claims.get("user_id")

    new_access = Authorize.create_access_token(
        subject=current_user,
        expires_time=timedelta(minutes=15),
        user_claims={"user_id": user_id} if user_id else {},
    )

    return {"access": new_access, "token_type": "bearer"}


# ── POST /auth/forgot-password ────────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    Always returns 200 regardless of whether the email exists — this
    prevents user enumeration (attacker can't tell if an email is registered
    by comparing responses).
    """
    from app.utils.verification import generate_reset_token
    from app.utils.email import send_password_reset_email

    result = await db.execute(select(UserAuth).where(UserAuth.email == data.email))
    user = result.scalar_one_or_none()

    if user:
        token = generate_reset_token(data.email)
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        try:
            send_password_reset_email(data.email, reset_link)
        except Exception:
            # Log silently — don't reveal email sending failures to caller
            pass

    # Always return the same response — prevents user enumeration
    return {"detail": "If that email is registered, a reset link has been sent."}


# ── POST /auth/reset-password ─────────────────────────────────────────────────
@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using a valid reset token.
    Token must be unused and less than 1 hour old.
    """
    from app.utils.verification import confirm_reset_token
    from werkzeug.security import generate_password_hash

    email = confirm_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link. Please request a new one.",
        )

    result = await db.execute(select(UserAuth).where(UserAuth.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate new password meets requirements (reuse existing schema validation)
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=422, detail="Password must be at least 8 characters"
        )

    user.password = generate_password_hash(data.new_password)
    await db.commit()

    return {"detail": "Password reset successfully. You can now log in."}
