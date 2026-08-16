import jwt
import logging
from app.config import settings

logger = logging.getLogger("ai-document-assistant.auth")

def verify_jwt(token: str) -> dict | None:
    """
    Decodes and verifies a Supabase JWT token using the secret key.
    Returns a dictionary containing the user's ID and email, or None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            logger.warning("JWT validation failed: 'sub' (user_id) claim is missing.")
            return None
            
        return {
            "user_id": user_id,
            "email": email
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT validation failed: Token has expired.")
        return None
    except jwt.InvalidSignatureError:
        logger.warning("JWT validation failed: Invalid signature. Check your SUPABASE_JWT_SECRET.")
        return None
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed with error: {e}")
        return None
