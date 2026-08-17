import io
import logging
from typing import List, Dict
import pypdf

logger = logging.getLogger("ai-document-assistant.documents.processor")

def extract_pdf_chunks(
    file_bytes: bytes,
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[Dict]:
    """
    Parses a PDF from raw bytes, extracts page-by-page text,
    and slices the text into overlapping chunks.
    
    Returns a list of dictionaries with metadata:
    [
      {
        "text": str,
        "page_number": int,
        "chunk_index": int
      },
      ...
    ]
    """
    logger.info("Initializing PDF extraction and chunking process...")
    
    # 1. Wrap bytes in memory stream and read PDF
    try:
        pdf_stream = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_stream)
        total_pages = len(reader.pages)
        logger.info(f"Successfully loaded PDF. Total pages found: {total_pages}")
    except Exception as e:
        logger.error(f"Error loading PDF from bytes: {e}", exc_info=True)
        raise ValueError(f"Failed to parse PDF binary file: {str(e)}")

    chunks = []
    chunk_counter = 0

    # 2. Iterate through each page
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text()
            if not page_text:
                logger.warning(f"No text extracted from Page {page_num} (could be scanned/image-only page).")
                continue

            # Standardize spacing (replace multiple spaces/newlines with a single space)
            cleaned_text = " ".join(page_text.split())
            if not cleaned_text.strip():
                continue

            text_length = len(cleaned_text)
            
            # 3. Slice text into chunks of `chunk_size` with `chunk_overlap`
            i = 0
            while i < text_length:
                chunk_slice = cleaned_text[i : i + chunk_size]
                
                # Record chunk data
                chunks.append({
                    "text": chunk_slice,
                    "page_number": page_num,
                    "chunk_index": chunk_counter
                })
                chunk_counter += 1
                
                # Check boundary limit
                if i + chunk_size >= text_length:
                    break
                
                # Shift start window by chunk_size minus overlap
                i += (chunk_size - chunk_overlap)

            logger.info(f"Page {page_num}/{total_pages} processed. Extracted {chunk_counter} total chunks so far.")
            
        except Exception as e:
            logger.error(f"Error processing Page {page_num}: {e}", exc_info=True)
            # We continue processing other pages even if one page fails
            continue

    logger.info(f"PDF extraction complete. Total chunks generated: {len(chunks)}")
    return chunks
