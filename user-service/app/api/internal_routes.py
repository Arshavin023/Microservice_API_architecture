"""
Internal route for service-to-service calls.
Place at: user-service/app/api/internal_routes.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from uuid import UUID
from typing import cast
from app.services.user_service import UserProfileService

router = APIRouter(prefix="/users", tags=["Internal"])

@router.get("/internal/{user_id}")
async def get_user_internal(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user_id format")

    profile = await UserProfileService.get_profile_by_user_id(db, uid)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": str(profile.user_id),
        "email": cast(str, profile.email),
        "username": cast(str, profile.username),
    }