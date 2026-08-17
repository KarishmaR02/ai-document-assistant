import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger("ai-document-assistant.auth")

# Initialize a Supabase client to call Auth APIs directly
try:
    supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client in auth service: {e}")
    supabase_client = None

def verify_jwt(token: str) -> dict | None:
    """
    Verifies the JWT token by validating it against Supabase Auth.
    Returns the user payload (id and email) if valid, or None if invalid.
    """
    if not supabase_client:
        logger.error("Supabase client is not initialized in auth service.")
        return None

    try:
        # Call the Supabase Auth API to get the user corresponding to this token.
        # This securely verifies signature, expiration, and claims on the Supabase server.
        response = supabase_client.auth.get_user(token)
        
        if response and response.user:
            return {
                "user_id": str(response.user.id),
                "email": response.user.email
            }
        
        logger.warning("Token verification failed: No user found in response.")
        return None
        
    except Exception as e:
        logger.warning(f"JWT verification failed via Supabase API: {e}")
        return None
