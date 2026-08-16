from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth2.exceptions import AuthJWTException
from app.api.shipment_routes import router as shipment_router

app = FastAPI(title="Shipping Service")

@app.exception_handler(AuthJWTException)
async def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

app.include_router(shipment_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
