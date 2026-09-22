import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database.connection import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UPLOADED", nullable=False) # UPLOADED, PROCESSING, PROCESSED, FAILED
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Supabase Auth links user accounts via auth.users.id (created via custom DDL trigger)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 768-dimensional vector embedding column mapped to pgvector (Gemini text-embedding-004)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' or 'ai'
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    retrieved_chunks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Serialized citations list

    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

# Set up event listeners to add the actual FOREIGN KEY constraints to auth.users after tables are created.
# This prevents SQLAlchemy from throwing a NoReferencedTableError during metadata initialization.
from sqlalchemy import event, DDL

event.listen(
    Document.__table__,
    "after_create",
    DDL("ALTER TABLE documents ADD CONSTRAINT fk_documents_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE")
)

event.listen(
    ChatSession.__table__,
    "after_create",
    DDL("ALTER TABLE chat_sessions ADD CONSTRAINT fk_chat_sessions_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE")
)
