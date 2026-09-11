from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.services.document_service import (
    process_document, get_latest, list_documents
)

router = APIRouter(tags=["documents"])

@router.get("/health")
def health():
    return {"status": "ok", "service": "document-intelligence"}

@router.post("/documents/process")
async def process(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    try:
        content = await file.read()
        result, status = process_document(
            file.filename or "unnamed",
            content,
            file.content_type or "",
            document_type
        )
        if status != 200:
            return JSONResponse(status_code=status, content=result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        # Do not expose stack traces/secrets to the client.
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check server logs for details."
        )

@router.get("/documents/{document_name}")
def get_document(document_name: str):
    result = get_latest(document_name)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found.")
    return result

@router.get("/documents")
def documents():
    return {"documents": list_documents()}
