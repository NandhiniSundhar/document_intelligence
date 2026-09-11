from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ErrorBody(BaseModel):
    code: str
    message: str

class FileValidation(BaseModel):
    file_type: str
    is_supported: bool
    is_readable: bool
    page_count: int
    status: str

class ValidationCheck(BaseModel):
    name: str
    formula: str
    operands: Dict[str, Any]
    calculated_value: Optional[float] = None
    reported_value: Optional[float] = None
    variance: Optional[float] = None
    status: str
    message: Optional[str] = None

class ValidationResult(BaseModel):
    checks: List[ValidationCheck]
    overall_status: str
    issues: List[str]

class ProcessingMetadata(BaseModel):
    ocr_used: bool
    processed_at: str
    processing_time_ms: int
    pages_processed: int

class DocumentResponse(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    overall_confidence: Optional[float] = None
    file_validation: FileValidation
    extracted_data: Dict[str, Any]
    validation: ValidationResult
    processing_metadata: ProcessingMetadata
