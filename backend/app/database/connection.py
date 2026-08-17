import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger("ai-document-assistant.database")

# Declarative Base for models
Base = declarative_base()

# Async Engine Setup
logger.info(f"Connecting to database with URL configured in environment Settings.")
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENV == "development" else False,
    future=True
)

# Async Sessionmaker Setup
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# FastAPI session dependency
async def get_db():
    """Dependency that yields a database session and closes it when done."""
    async with async_session_maker() as session:
        yield session

# Auto-table initialization helper
async def init_db():
    """Creates database tables automatically if they do not exist."""
    # We import models here to register tables on Base.metadata
    from app.database import models
    try:
        async with engine.begin() as conn:
            logger.info("Enabling pgvector extension if not exists...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            logger.info("Initializing database tables...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}", exc_info=True)
        raise e
