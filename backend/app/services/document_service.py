import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import UPLOAD_DIR
from app.core.database import SessionLocal
from app.core.logging import logger
from app.models.document import Document
from app.services.document_validation_service import validate_document
from app.services.ocr_service import extract_text
from app.services.extraction_service import extract
from app.services.financial_validation_service import validate

SUPPORTED_TYPES = {
    "invoice", "balance_sheet", "profit_and_loss", "cash_flow_statement"
}

def process_document(filename, content, content_type, document_type):
    started = time.perf_counter()

    if document_type not in SUPPORTED_TYPES:
        raise ValueError("Unsupported document_type.")

    validation = validate_document(filename, content, content_type)
    if validation["status"] != "PASS":
        return {
            "error": validation["error"],
            "file_validation": {k: v for k, v in validation.items() if k != "error"}
        }, 400

    safe_name = Path(filename).name
    (UPLOAD_DIR / safe_name).write_bytes(content)

    logger.info("Processing %s as %s", safe_name, document_type)
    ocr = extract_text(content, safe_name)
    extracted = extract(ocr["text"], document_type)
    financial = validate(extracted, document_type)

    status = "PASS" if financial["overall_status"] in ("PASS", "NOT_APPLICABLE") else "FAILED"
    processed_at = datetime.now(timezone.utc).isoformat()
    elapsed = int((time.perf_counter() - started) * 1000)

    result = {
        "document_name": safe_name,
        "document_type": document_type,
        "processing_status": status,
        "overall_confidence": None,
        "file_validation": validation,
        "extracted_data": extracted,
        "validation": financial,
        "processing_metadata": {
            "ocr_used": ocr["ocr_used"],
            "processed_at": processed_at,
            "processing_time_ms": elapsed,
            "pages_processed": len(ocr["pages"]),
        },
        "raw_text": ocr["text"],
    }

    db = SessionLocal()
    try:
        row = Document(
            document_name=safe_name,
            document_type=document_type,
            processing_status=status,
            processed_at=datetime.now(timezone.utc),
            result_json=json.dumps(result, ensure_ascii=False),
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    return result, 200

def get_latest(document_name):
    db = SessionLocal()
    try:
        row = (
            db.query(Document)
            .filter(Document.document_name == Path(document_name).name)
            .order_by(Document.id.desc())
            .first()
        )
        return json.loads(row.result_json) if row else None
    finally:
        db.close()

def list_documents():
    db = SessionLocal()
    try:
        rows = db.query(Document).order_by(Document.id.desc()).all()
        return [{
            "document_name": r.document_name,
            "document_type": r.document_type,
            "processing_status": r.processing_status,
            "processed_at": r.processed_at.isoformat()
        } for r in rows]
    finally:
        db.close()
