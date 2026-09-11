import io
from PIL import Image
from app.services.document_validation_service import validate_document

def test_png_validation():
    b = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(b, format="PNG")
    result = validate_document("test.png", b.getvalue(), "image/png")
    assert result["status"] == "PASS"
    assert result["page_count"] == 1

def test_unsupported_file():
    result = validate_document("test.txt", b"hello", "text/plain")
    assert result["status"] == "FAILED"
    assert result["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
