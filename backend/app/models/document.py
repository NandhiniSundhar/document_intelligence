from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    document_name = Column(String(512), index=True, nullable=False)
    document_type = Column(String(64), nullable=False)
    processing_status = Column(String(32), nullable=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    result_json = Column(Text, nullable=False)
