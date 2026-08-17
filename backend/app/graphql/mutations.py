import uuid
import strawberry
from typing import Optional
from app.graphql.types import SessionType, MessageType, RetrievedChunkType
from app.documents.embeddings import get_embedding

@strawberry.type
class AuthPayload:
    success: bool
    token: Optional[str] = None
    error_message: Optional[str] = None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login_user_mock(self, email: str, password: str) -> AuthPayload:
        """Mock login endpoint used as a fallback constraint."""
        if email == "demo@example.com" and password == "password":
            return AuthPayload(
                success=True,
                token="mock_jwt_token_for_" + email
            )
        return AuthPayload(
            success=False,
            error_message="Invalid credentials"
        )

    @strawberry.mutation
    async def create_chat_session(self, info: strawberry.Info, document_id: str) -> Optional[SessionType]:
        """Creates a new conversation session linked to an uploaded document."""
        user = info.context.get("user")
        if not user or not user.get("user_id"):
            return None

        try:
            user_id = uuid.UUID(user.get("user_id"))
            doc_uuid = uuid.UUID(document_id)
        except ValueError:
            return None

        from app.database.connection import async_session_maker
        from app.database.repositories import ChatRepository

        async with async_session_maker() as db:
            session = await ChatRepository.create_session(db, doc_uuid, user_id)
            return SessionType(
                id=str(session.id),
                documentId=str(session.document_id),
                createdAt=session.created_at.isoformat()
            )

    @strawberry.mutation
    async def send_message(self, info: strawberry.Info, session_id: str, text: str) -> Optional[MessageType]:
        """Processes user questions by running a pgvector semantic search and saving context logs."""
        user = info.context.get("user")
        if not user or not user.get("user_id"):
            return None

        try:
            user_id = uuid.UUID(user.get("user_id"))
            sess_uuid = uuid.UUID(session_id)
        except ValueError:
            return None

        from app.database.connection import async_session_maker
        from app.database.repositories import ChatRepository, DocumentRepository

        async with async_session_maker() as db:
            # 1. Verify session belongs to the user
            session = await ChatRepository.get_session_by_id(db, sess_uuid, user_id)
            if not session:
                return None
            
            # 2. Convert user's question text to a vector embedding
            query_vector = get_embedding(text)

            # 3. Perform pgvector similarity search against this document's text chunks
            similar_chunks = await DocumentRepository.search_similar_chunks(
                db=db,
                doc_id=session.document_id,
                query_embedding=query_vector,
                limit=3
            )

            # 4. Save the user's message to database logs
            await ChatRepository.create_message(
                db=db,
                session_id=sess_uuid,
                sender="user",
                text=text
            )

            # 5. Format search result citations for database storage
            retrieved_chunks = [
                {
                    "text": chunk.text,
                    "pageNumber": chunk.page_number,
                    "score": round(0.92 - (idx * 0.04), 2) # Simulated matching score mapping
                }
                for idx, chunk in enumerate(similar_chunks)
            ]

            # 6. Construct placeholder response listing the matched chunks (LLM will plug in Phase 10)
            if retrieved_chunks:
                citation_summary = "\n\n".join(
                    f'[Page {c["pageNumber"]}]: "{c["text"][:140]}..."'
                    for c in retrieved_chunks
                )
                ai_reply_text = (
                    f"**Phase 9 RAG Search**: I found {len(retrieved_chunks)} relevant matches inside "
                    f"your document to answer your question:\n\n{citation_summary}\n\n"
                    f"*(Real AI text generator will be connected in Phase 10)*"
                )
            else:
                ai_reply_text = (
                    "**Phase 9 RAG Search**: I could not find any relevant text matches inside your "
                    "document to answer your question."
                )

            # 7. Save AI's response to database logs
            ai_msg = await ChatRepository.create_message(
                db=db,
                session_id=sess_uuid,
                sender="ai",
                text=ai_reply_text,
                retrieved_chunks=retrieved_chunks
            )

            # 8. Return formatted MessageType back to client
            citations_list = [
                RetrievedChunkType(
                    text=c["text"],
                    pageNumber=c["pageNumber"],
                    score=c["score"]
                )
                for c in retrieved_chunks
            ]

            return MessageType(
                id=str(ai_msg.id),
                sender=ai_msg.sender,
                text=ai_msg.text,
                timestamp=ai_msg.timestamp.isoformat(),
                retrievedChunks=citations_list
            )
