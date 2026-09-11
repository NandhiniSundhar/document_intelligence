from pathlib import Path
import fitz
from PIL import Image
from app.core.config import (
    ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_MB, MAX_PAGES
)

def validate_document(filename: str, content: bytes, content_type: str):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_MIME_TYPES:
        return {
            "file_type": content_type or "unknown",
            "is_supported": False,
            "is_readable": False,
            "page_count": 0,
            "status": "FAILED",
            "error": {
                "code": "UNSUPPORTED_FILE_TYPE",
                "message": "Only PDF / JPG / PNG documents are supported."
            }
        }

    if not content:
        return {
            "file_type": content_type,
            "is_supported": True,
            "is_readable": False,
            "page_count": 0,
            "status": "FAILED",
            "error": {"code": "EMPTY_FILE", "message": "The uploaded file is empty."}
        }

    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        return {
            "file_type": content_type,
            "is_supported": True,
            "is_readable": False,
            "page_count": 0,
            "status": "FAILED",
            "error": {
                "code": "FILE_TOO_LARGE",
                "message": f"Maximum file size is {MAX_FILE_SIZE_MB} MB."
            }
        }

    try:
        if ext == ".pdf":
            doc = fitz.open(stream=content, filetype="pdf")
            pages = len(doc)
            if pages < 1:
                raise ValueError("PDF has no pages")
            if pages > MAX_PAGES:
                return {
                    "file_type": content_type,
                    "is_supported": True,
                    "is_readable": True,
                    "page_count": pages,
                    "status": "FAILED",
                    "error": {
                        "code": "PAGE_LIMIT_EXCEEDED",
                        "message": f"Documents are limited to {MAX_PAGES} pages."
                    }
                }
        else:
            Image.open(__import__("io").BytesIO(content)).verify()
            pages = 1

        return {
            "file_type": content_type,
            "is_supported": True,
            "is_readable": True,
            "page_count": pages,
            "status": "PASS",
        }
    except Exception:
        return {
            "file_type": content_type,
            "is_supported": True,
            "is_readable": False,
            "page_count": 0,
            "status": "FAILED",
            "error": {
                "code": "CORRUPTED_FILE",
                "message": "The uploaded document could not be read."
            }
        }
