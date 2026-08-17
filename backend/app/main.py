import logging
import sys
import os

# Add parent directory of 'app' to python path to resolve absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, Depends, BackgroundTasks, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from app.config import settings
from app.graphql.schema import schema
from app.auth.service import verify_jwt
from app.database.connection import get_db
from app.database.repositories import DocumentRepository
from app.documents.loader import upload_to_supabase
from app.documents.service import process_document_background
from app.database.connection import init_db

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai-document-assistant")

# Database init lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("lifespan: Initializing database tables...")
    await init_db()
    yield

# Initialize FastAPI application
app = FastAPI(
    title="AI Document Assistant API",
    description="Backend API for the AI Document Assistant learning application",
    version="0.1.0",
    lifespan=lifespan
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

# Register Strawberry GraphQL router
async def get_context(request: Request):
    user = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user = verify_jwt(token)
    return {
        "user": user
    }

graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
logger.info("GraphQL endpoint mounted on /graphql with custom auth context")

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

# Dependency helper to validate access tokens on REST endpoints
async def get_current_user(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: Authorization token is missing.")
    token = authorization.split(" ")[1]
    user = verify_jwt(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token or expired session.")
    return user

# REST Endpoint for File Uploads
@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validation: only PDF files allowed
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 2. Validation: limit file size to 10MB
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")

    user_id_str = current_user.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="User session is missing required ID payload.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="User ID token claim is not a valid UUID.")

    # 3. Upload raw file bytes to Supabase Storage
    try:
        storage_path = upload_to_supabase(file_bytes, file.filename, user_id_str)
    except Exception as e:
        logger.error(f"File upload failed to Supabase Storage: {e}")
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    # 4. Insert metadata row into PostgreSQL database
    try:
        doc = await DocumentRepository.create_document(
            db=db,
            name=file.filename,
            size=len(file_bytes),
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Database insertion failed for document metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database save failed for document metadata.")

    # 5. Start background processing worker task
    background_tasks.add_task(process_document_background, doc.id)

    return {
        "id": str(doc.id),
        "name": doc.name,
        "size": doc.size,
        "status": doc.status,
        "progress": doc.progress,
        "uploadedAt": doc.uploaded_at.isoformat()
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
