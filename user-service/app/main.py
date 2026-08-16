# from fastapi import FastAPI
# from app.api.user_routes import router as user_router
# from app.core import jwt_config  # noqa: F401 — import triggers @AuthJWT.load_config registration

# app = FastAPI(title="User Service")
# app.include_router(user_router)


# @app.get("/health")
# async def health():
#     return {"status": "ok"}

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth2.exceptions import AuthJWTException

from app.api.user_routes import router as user_router
from app.core import jwt_config  # noqa: F401 — triggers @AuthJWT.load_config registration

from app.api.internal_routes import router as internal_router


app = FastAPI(title="User Service")
app.include_router(user_router)
app.include_router(internal_router)

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}