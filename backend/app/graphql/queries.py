import strawberry
from typing import List

@strawberry.type
class DocumentType:
    id: str
    name: str
    size: int
    status: str
    progress: int
    uploaded_at: str
    error_message: str | None = None

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, info: strawberry.Info) -> str:
        user = info.context.get("user")
        if user and user.get("email"):
            return f"Hello, {user['email']}! Supabase Auth is fully working."
        return "Hello Anonymous! Connect authentication to see your email."

    @strawberry.field
    def get_documents(self) -> List[DocumentType]:
        return [
            DocumentType(
                id="doc-1",
                name="employee_policy.pdf",
                size=124000,
                status="PROCESSED",
                progress=100,
                uploaded_at="2026-08-16T12:00:00Z"
            ),
            DocumentType(
                id="doc-2",
                name="project_guide.pdf",
                size=450000,
                status="PROCESSING",
                progress=45,
                uploaded_at="2026-08-16T14:30:00Z"
            )
        ]
