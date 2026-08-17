import strawberry
from typing import List, Optional

@strawberry.type
class DocumentType:
    id: str
    name: str
    size: int
    status: str
    progress: int
    uploadedAt: str
    errorMessage: Optional[str] = None

@strawberry.type
class RetrievedChunkType:
    text: str
    pageNumber: int
    score: float

@strawberry.type
class MessageType:
    id: str
    sender: str # 'user' or 'ai'
    text: str
    timestamp: str
    retrievedChunks: Optional[List[RetrievedChunkType]] = None

@strawberry.type
class SessionType:
    id: str
    documentId: str
    createdAt: str
