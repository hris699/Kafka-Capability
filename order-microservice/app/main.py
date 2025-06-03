from fastapi import FastAPI
from app.routes.routes import router
from app.db import engine
from sqlalchemy import text
import logging
import sys
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI()
app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.on_event("startup")
def test_db_connection():
    try:
        print("Database connection successful at startup.")
    except Exception as e:
        print("Database connection failed at startup:", e)
