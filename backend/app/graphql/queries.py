import uuid
import strawberry
from typing import List
from app.graphql.types import DocumentType, MessageType, RetrievedChunkType

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, info: strawberry.Info) -> str:
        """Handshake check query returning user status."""
        user = info.context.get("user")
        if user and user.get("email"):
            return f"Hello, {user['email']}! Supabase Auth is fully working."
        return "Hello Anonymous! Connect authentication to see your email."

    @strawberry.field
    async def get_documents(self, info: strawberry.Info) -> List[DocumentType]:
        """Loads all documents uploaded by the authenticated user."""
        user = info.context.get("user")
        if not user or not user.get("user_id"):
            return []
            
        try:
            user_id = uuid.UUID(user.get("user_id"))
        except ValueError:
            return []

        from app.database.connection import async_session_maker
        from app.database.repositories import DocumentRepository

        async with async_session_maker() as db:
            docs = await DocumentRepository.get_documents_by_user(db, user_id)
            return [
                DocumentType(
                    id=str(doc.id),
                    name=doc.name,
                    size=doc.size,
                    status=doc.status,
                    progress=doc.progress,
                    uploadedAt=doc.uploaded_at.isoformat(),
                    errorMessage=doc.error_message
                )
                for doc in docs
            ]

    @strawberry.field
    async def get_chat_messages(self, info: strawberry.Info, session_id: str) -> List[MessageType]:
        """Loads the historical conversation logs for a chat session, verifying ownership."""
        user = info.context.get("user")
        if not user or not user.get("user_id"):
            return []

        try:
            user_id = uuid.UUID(user.get("user_id"))
            sess_uuid = uuid.UUID(session_id)
        except ValueError:
            return []

        from app.database.connection import async_session_maker
        from app.database.repositories import ChatRepository

        async with async_session_maker() as db:
            # Secure Filter: Verify this session actually belongs to the active user
            session = await ChatRepository.get_session_by_id(db, sess_uuid, user_id)
            if not session:
                return []

            messages = await ChatRepository.get_session_messages(db, sess_uuid)
            
            result = []
            for msg in messages:
                # Map JSON citations context
                chunks = None
                if msg.retrieved_chunks and isinstance(msg.retrieved_chunks, list):
                    chunks = [
                        RetrievedChunkType(
                            text=c.get("text", ""),
                            pageNumber=c.get("pageNumber", 1),
                            score=c.get("score", 0.0)
                        )
                        for c in msg.retrieved_chunks
                    ]
                
                result.append(
                    MessageType(
                        id=str(msg.id),
                        sender=msg.sender,
                        text=msg.text,
                        timestamp=msg.timestamp.isoformat(),
                        retrievedChunks=chunks
                    )
                )
            return result
