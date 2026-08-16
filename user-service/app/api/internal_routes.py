"""
Internal route for service-to-service calls.
Place at: user-service/app/api/internal_routes.py
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.user_service import UserProfileService

router = APIRouter(prefix="/users", tags=["Internal"])


@router.get("/internal/{user_id}")
async def get_user_internal(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Internal endpoint — returns email and username for a given user_id.
    Called by notification-service to get the recipient email.
    No JWT required — internal Docker network only.
    """
    profile = await UserProfileService.get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": str(profile.user_id),
        "email":   profile.email,
        "username": profile.username,
    }