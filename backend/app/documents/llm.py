import logging
from typing import List
from app.config import settings

logger = logging.getLogger("ai-document-assistant.documents.llm")

# Flag to track if Gemini has been configured
_is_configured = False

def ensure_genai_configured():
    """
    Configures the Google Generative AI SDK using the API key.
    """
    global _is_configured
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your-gemini-api-key-placeholder":
        raise ValueError(
            "Google Gemini API Key is missing or using default placeholder. "
            "Please copy your API key from Google AI Studio (https://aistudio.google.com) "
            "and update GEMINI_API_KEY inside backend/.env."
        )

    if not _is_configured:
        try:
            logger.info("Configuring Google Generative AI SDK...")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            _is_configured = True
            logger.info("Google Generative AI SDK configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure Google Generative AI SDK: {e}", exc_info=True)
            raise RuntimeError(f"Generative AI setup failed: {str(e)}")

def generate_answer(query: str, context_chunks: List[str]) -> str:
    """
    Feeds PDF text chunks and the user question to Gemini.
    Attempts multiple model strings in sequence (self-healing loop)
    to handle deprecated models or project constraints.
    """
    try:
        ensure_genai_configured()
    except ValueError as val_err:
        logger.warning(val_err)
        return (
            "⚠️ **Gemini API Key Required**\n\n"
            "To get real AI answers based on your documents, please:\n"
            "1. Visit [Google AI Studio](https://aistudio.google.com) to generate a free API Key.\n"
            "2. Open your local `backend/.env` file.\n"
            "3. Set `GEMINI_API_KEY=your_copied_key_here`.\n"
            "4. Restart the backend server.\n\n"
            f"*(Currently showing matching context blocks from your database query)*"
        )
    except Exception as e:
        logger.error(f"Failed to load generative model: {e}")
        return f"⚠️ **AI Setup Error**: {str(e)}"

    import google.generativeai as genai

    # 1. Build secure RAG prompt template
    context_text = "\n\n".join(f"[Segment {idx+1}]: {text}" for idx, text in enumerate(context_chunks))
    
    prompt = f"""
You are an intelligent AI document assistant.
Your goal is to answer the user's question using ONLY the provided document context segments below.

Strict Constraints:
1. Base your answer strictly on the text segments provided. Do not use external knowledge or make up facts.
2. If the answer cannot be found in the provided context, respond exactly with: "I cannot find the answer to your question in the provided document."
3. Keep your answer professional, accurate, and format it nicely using Markdown lists, bold text, or paragraphs where appropriate.

Document Context Segments:
{context_text}

User Question:
{query}

AI Response:
"""

    # 2. Self-healing loop: try different models in sequence
    model_names = ["gemini-3.1-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]
    last_exception = None

    for model_name in model_names:
        try:
            logger.info(f"Attempting API generation using model: '{model_name}'")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if response and response.text:
                logger.info(f"Successfully generated AI response using model '{model_name}'.")
                return response.text
                
        except Exception as e:
            logger.warning(f"Model '{model_name}' failed to generate content: {e}")
            last_exception = e
            continue

    # If all models failed, return the final error details
    error_msg = str(last_exception) if last_exception else "Unknown API Error"
    logger.error(f"All Gemini models failed. Last error: {error_msg}")
    return (
        "⚠️ **Gemini API Query Failed**\n\n"
        f"Error details: `{error_msg}`\n\n"
        "Please check that your GEMINI_API_KEY is valid and has access to Gemini model endpoints."
    )
