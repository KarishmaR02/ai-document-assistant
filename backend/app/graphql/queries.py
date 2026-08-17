import uuid
import strawberry
from typing import List

@strawberry.type
class DocumentType:
    id: str
    name: str
    size: int
    status: str
    progress: int
    uploadedAt: str
    errorMessage: str | None = None

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, info: strawberry.Info) -> str:
        user = info.context.get("user")
        if user and user.get("email"):
            return f"Hello, {user['email']}! Supabase Auth is fully working."
        return "Hello Anonymous! Connect authentication to see your email."

    @strawberry.field
    async def get_documents(self, info: strawberry.Info) -> List[DocumentType]:
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
