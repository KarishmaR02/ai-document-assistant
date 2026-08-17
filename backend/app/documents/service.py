import asyncio
import logging
import uuid
from app.database.connection import async_session_maker
from app.database.repositories import DocumentRepository

logger = logging.getLogger("ai-document-assistant.documents.service")

async def process_document_background(doc_id: uuid.UUID) -> None:
    """
    Background worker that simulates PDF text parsing, chunking, and indexing.
    Slowly advances the document status in PostgreSQL over a few seconds.
    """
    logger.info(f"Starting background processing for document: {doc_id}")
    
    try:
        # Step 1: Transition UPLOADED -> PROCESSING (40% progress)
        await asyncio.sleep(2.5)
        async with async_session_maker() as db:
            logger.info(f"Document {doc_id}: Status -> PROCESSING (40%)")
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSING",
                progress=40
            )

        # Step 2: Simulate text chunk extraction (80% progress)
        await asyncio.sleep(3.0)
        async with async_session_maker() as db:
            logger.info(f"Document {doc_id}: Progress -> 80% (Extracting chunks...)")
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSING",
                progress=80
            )

        # Step 3: Transition to PROCESSED (100% progress)
        await asyncio.sleep(2.0)
        async with async_session_maker() as db:
            logger.info(f"Document {doc_id}: Status -> PROCESSED (100%)")
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSED",
                progress=100
            )
            
    except Exception as e:
        logger.error(f"Error in background processing for document {doc_id}: {e}", exc_info=True)
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="FAILED",
                progress=100,
                error_message=f"Processing failed: {str(e)}"
            )
