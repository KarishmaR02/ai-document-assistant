import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger("ai-document-assistant.documents.loader")

# Initialize Supabase Admin client
# Using the service_role key lets the backend manage files on behalf of users in the storage bucket.
try:
    logger.info(f"Initializing Supabase client with URL: {settings.SUPABASE_URL}")
    supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
    supabase_client = None

def upload_to_supabase(file_content: bytes, filename: str, user_id: str) -> str:
    """
    Uploads file bytes to the Supabase Storage bucket named 'documents'.
    Saves the file at path: {user_id}/{filename}
    Returns the path of the uploaded file inside the bucket.
    """
    if supabase_client is None:
        raise ValueError("Supabase storage client is not initialized. Check your credentials.")

    # Secure file path: isolate files inside folder named after the user's UUID
    storage_path = f"{user_id}/{filename}"
    
    try:
        logger.info(f"Uploading file '{filename}' to Supabase Storage path: '{storage_path}'")
        
        # Upload using the storage client API (overwriting if file already exists using x-upsert)
        response = supabase_client.storage.from_("documents").upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": "application/pdf",
                "x-upsert": "true"
            }
        )
        
        logger.info(f"Successfully uploaded file to Supabase. Path returned: {storage_path}")
        return storage_path
        
    except Exception as e:
        logger.error(f"Supabase Storage upload failed for file '{filename}' at path '{storage_path}': {e}", exc_info=True)
        raise RuntimeError(f"Storage upload failed: {str(e)}")

def download_from_supabase(storage_path: str) -> bytes:
    """
    Downloads raw file bytes from the Supabase Storage bucket 'documents'.
    """
    if supabase_client is None:
        raise ValueError("Supabase storage client is not initialized. Check your credentials.")

    try:
        logger.info(f"Downloading file from Supabase Storage path: '{storage_path}'")
        # download returns raw bytes
        file_bytes = supabase_client.storage.from_("documents").download(storage_path)
        return file_bytes
    except Exception as e:
        logger.error(f"Failed to download file '{storage_path}' from Supabase Storage: {e}", exc_info=True)
        raise RuntimeError(f"Storage download failed: {str(e)}")
