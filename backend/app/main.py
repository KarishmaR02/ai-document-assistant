import logging
import sys
import os

# Add parent directory of 'app' to python path to resolve absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai-document-assistant")

# Initialize FastAPI application
app = FastAPI(
    title="AI Document Assistant API",
    description="Backend API for the AI Document Assistant learning application",
    version="0.1.0"
)

# Set up CORS origins
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS origins configured: {cors_origins}")

# Basic error handling for unexpected exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please check server logs for details."
        }
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Document Assistant API. Access /docs for API documentation."
    }

# Health Check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint requested.")
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": settings.ENV
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True if settings.ENV == "development" else False
    )
