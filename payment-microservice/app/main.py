from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes.payment import router as payment_router
import logging
import sys
from fastapi import status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('payment_service.log')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Microservice")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payment_router, prefix="/api/v1", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": "Payment Microservice mein aapka swagat hai!!!"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Payment Service is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Payment Service is shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 