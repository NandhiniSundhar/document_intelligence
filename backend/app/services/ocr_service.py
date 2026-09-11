import io
import fitz
import pytesseract
from PIL import Image
from app.core.config import OCR_LANG

def _ocr_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image, lang=OCR_LANG, config="--psm 6")

def extract_text(content: bytes, filename: str):
    pages = []
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=content, filetype="pdf")
        for idx, page in enumerate(doc):
            native = page.get_text("text").strip()
            # Always OCR image/scanned pages if native text is weak.
            if len(native) >= 80:
                text = native
                used_ocr = False
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = _ocr_image(image)
                used_ocr = True
            pages.append({"page_number": idx + 1, "text": text, "ocr_used": used_ocr})
    else:
        image = Image.open(io.BytesIO(content)).convert("RGB")
        pages.append({
            "page_number": 1,
            "text": _ocr_image(image),
            "ocr_used": True
        })

    return {
        "pages": pages,
        "text": "\n\n".join(f"[PAGE {p['page_number']}]\n{p['text']}" for p in pages),
        "ocr_used": any(p["ocr_used"] for p in pages),
    }
