import uuid
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import models

class DocumentRepository:
    @staticmethod
    async def get_documents_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[models.Document]:
        """Fetches all documents belonging to a specific user, sorted by upload date (newest first)."""
        stmt = select(models.Document).where(models.Document.user_id == user_id).order_by(models.Document.uploaded_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_document_by_id(db: AsyncSession, doc_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.Document]:
        """Fetches a specific document by its ID and user ownership."""
        stmt = select(models.Document).where(models.Document.id == doc_id, models.Document.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_document(db: AsyncSession, name: str, size: int, user_id: uuid.UUID) -> models.Document:
        """Inserts a new document record in the UPLOADED state."""
        doc = models.Document(
            name=name,
            size=size,
            user_id=user_id,
            status="UPLOADED",
            progress=10
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def update_document_status(
        db: AsyncSession,
        doc_id: uuid.UUID,
        status: str,
        progress: int,
        error_message: Optional[str] = None
    ) -> Optional[models.Document]:
        """Updates the status and progress metrics of a document."""
        stmt = (
            update(models.Document)
            .where(models.Document.id == doc_id)
            .values(status=status, progress=progress, error_message=error_message)
        )
        await db.execute(stmt)
        await db.commit()
        
        # Fetch the updated document back
        # Note: Since user_id is not available here, we get by primary key directly
        stmt_fetch = select(models.Document).where(models.Document.id == doc_id)
        result = await db.execute(stmt_fetch)
        return result.scalar_one_or_none()

    @staticmethod
    async def search_similar_chunks(
        db: AsyncSession,
        doc_id: uuid.UUID,
        query_embedding: List[float],
        limit: int = 4
    ) -> List[models.DocumentChunk]:
        """
        Runs a pgvector similarity search to find the closest text chunks 
        for a document, ordered by cosine distance (<=>).
        """
        stmt = (
            select(models.DocumentChunk)
            .where(models.DocumentChunk.document_id == doc_id)
            .order_by(models.DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())



class ChatRepository:
    @staticmethod
    async def get_sessions_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[models.ChatSession]:
        """Lists all chat sessions belonging to a specific user."""
        stmt = select(models.ChatSession).where(models.ChatSession.user_id == user_id).order_by(models.ChatSession.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.ChatSession]:
        """Fetches a specific chat session verifying user ownership."""
        stmt = select(models.ChatSession).where(models.ChatSession.id == session_id, models.ChatSession.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_session(db: AsyncSession, document_id: uuid.UUID, user_id: uuid.UUID) -> models.ChatSession:
        """Initializes a new chat session linked to a document."""
        session = models.ChatSession(
            document_id=document_id,
            user_id=user_id
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session_messages(db: AsyncSession, session_id: uuid.UUID) -> List[models.ChatMessage]:
        """Retrieves message logs for a session, ordered chronologically."""
        stmt = select(models.ChatMessage).where(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.timestamp.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_message(
        db: AsyncSession,
        session_id: uuid.UUID,
        sender: str,
        text: str,
        retrieved_chunks: Optional[dict] = None
    ) -> models.ChatMessage:
        """Saves a message entry into database chat logs."""
        message = models.ChatMessage(
            session_id=session_id,
            sender=sender,
            text=text,
            retrieved_chunks=retrieved_chunks
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message
