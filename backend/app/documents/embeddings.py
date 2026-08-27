import logging
from typing import List
from app.documents.llm import ensure_genai_configured

logger = logging.getLogger("ai-document-assistant.documents.embeddings")

def get_embedding(text: str) -> List[float]:
    """
    Generates a 768-dimensional vector embedding for a single text query using Google Gemini API.
    """
    if not text.strip():
        return [0.0] * 768
        
    try:
        ensure_genai_configured()
        import google.generativeai as genai
        
        logger.info("Generating embedding via Gemini API...")
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        return response['embedding']
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}", exc_info=True)
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generates 768-dimensional vector embeddings for a batch of text chunks using Google Gemini API.
    """
    if not texts:
        return []
        
    try:
        ensure_genai_configured()
        import google.generativeai as genai
        
        logger.info(f"Generating batch embeddings for {len(texts)} chunks via Gemini API...")
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=texts,
            task_type="retrieval_document",
            output_dimensionality=768
        )
        return response['embedding']
    except Exception as e:
        logger.error(f"Failed to generate batch embeddings: {e}", exc_info=True)
        raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
