import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.auth_routes import router as auth_router
from app.db.base import Base
from typing import cast
from app.db.session import engine
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")

class Settings(BaseModel):
    authjwt_secret_key: str = cast(str, JWT_SECRET)


@AuthJWT.load_config  # type: ignore[misc]
def get_config() -> Settings:
    return Settings()


app = FastAPI(title="Authentication Service")
app.include_router(auth_router)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
