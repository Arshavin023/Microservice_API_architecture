from fastapi import HTTPException, Depends
from fastapi_jwt_auth2 import AuthJWT
import app.core.jwt_config  # noqa — registers load_config


def require_staff(Authorize: AuthJWT = Depends()):
    """
    Dependency that enforces staff-only access.
    All shipment write operations (create, dispatch, deliver) are restricted
    to staff users — regular customers cannot create or update shipments.
    """
    Authorize.jwt_required()
    claims = Authorize.get_raw_jwt()
    if not claims.get("is_staff"):
        raise HTTPException(
            status_code=403,
            detail="Staff access required",
        )


def get_current_user_id(Authorize: AuthJWT = Depends()):
    """
    Dependency that extracts user_id from JWT.
    Used for customer-facing read endpoints (track your own shipment).
    """
    Authorize.jwt_required()
    claims = Authorize.get_raw_jwt()
    user_id = claims.get("user_id")
    if not user_id:
        raise HTTPException(status_code=422, detail="Missing user_id claim in token")
    from uuid import UUID
    return UUID(user_id)
