import logging
from typing import List

logger = logging.getLogger("ai-document-assistant.documents.embeddings")

# Cached model instance
_model_instance = None

def get_embeddings_model():
    """
    Returns the cached instance of the SentenceTransformer model.
    Loads it from local disk or downloads it on first call.
    """
    global _model_instance
    if _model_instance is None:
        try:
            # We import here to avoid loading the heavy library on server startup.
            # It will only load when the first file is uploaded or chat is initiated.
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2' (384 dimensions)...")
            from sentence_transformers import SentenceTransformer
            
            _model_instance = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize embedding model: {str(e)}")
            
    return _model_instance

def get_embedding(text: str) -> List[float]:
    """
    Generates a 384-dimensional vector embedding for a single text query.
    """
    if not text.strip():
        return [0.0] * 384
        
    model = get_embeddings_model()
    # encode returns a numpy array, which we convert to a plain list of float numbers
    vector_np = model.encode(text)
    return vector_np.tolist()

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generates vector embeddings for a batch of text chunks.
    Highly performant because it leverages batch processing operations.
    """
    if not texts:
        return []
        
    model = get_embeddings_model()
    vectors_np = model.encode(texts)
    return [vec.tolist() for vec in vectors_np]
