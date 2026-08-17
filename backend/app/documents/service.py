import logging
import uuid
from sqlalchemy import select
from app.database.connection import async_session_maker
from app.database import models
from app.database.repositories import DocumentRepository
from app.documents.loader import download_from_supabase
from app.documents.processor import extract_pdf_chunks

logger = logging.getLogger("ai-document-assistant.documents.service")

async def process_document_background(doc_id: uuid.UUID) -> None:
    """
    Background worker task. Downloads the PDF from Supabase Storage,
    extracts the text pages, splits it into semantic overlapping chunks,
    and stores them in the PostgreSQL database.
    """
    logger.info(f"Starting background processing for document: {doc_id}")
    
    try:
        # 1. Fetch document metadata from database to get user_id and filename
        async with async_session_maker() as db:
            stmt = select(models.Document).where(models.Document.id == doc_id)
            result = await db.execute(stmt)
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error(f"Failed to find document metadata for ID: {doc_id}")
                return
            
            user_id = str(doc.user_id)
            filename = doc.name

        # 2. Update progress -> 20% (Connecting to storage)
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSING",
                progress=20
            )

        # 3. Download the PDF file bytes from Supabase Storage
        storage_path = f"{user_id}/{filename}"
        logger.info(f"Downloading document bytes from path: '{storage_path}'")
        file_bytes = download_from_supabase(storage_path)

        # 4. Update progress -> 50% (Parsing pages)
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSING",
                progress=50
            )

        # 5. Extract text pages and generate overlapping chunks
        logger.info(f"Extracting PDF text chunks for file: {filename}")
        chunks_data = extract_pdf_chunks(file_bytes)
        
        # 6. Update progress -> 80% (Saving chunks to database)
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSING",
                progress=80
            )

        # 7. Bulk insert document chunks into PostgreSQL
        logger.info(f"Saving {len(chunks_data)} text chunks to database...")
        async with async_session_maker() as db:
            db_chunks = [
                models.DocumentChunk(
                    document_id=doc_id,
                    text=chunk["text"],
                    page_number=chunk["page_number"],
                    chunk_index=chunk["chunk_index"]
                )
                for chunk in chunks_data
            ]
            db.add_all(db_chunks)
            await db.commit()
            logger.info(f"Successfully saved {len(db_chunks)} chunks to table 'document_chunks'.")

        # 8. Complete process -> 100% (PROCESSED)
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="PROCESSED",
                progress=100
            )
            logger.info(f"Background parsing complete for document {doc_id}.")

    except Exception as e:
        logger.error(f"Error occurred during background processing of document {doc_id}: {e}", exc_info=True)
        # Mark document as failed, saving the error message
        async with async_session_maker() as db:
            await DocumentRepository.update_document_status(
                db=db,
                doc_id=doc_id,
                status="FAILED",
                progress=100,
                error_message=f"Failed to process document: {str(e)}"
            )
