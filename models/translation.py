from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class TranslationStatusEnum(str, enum.Enum):
    pending = "pending"
    translated = "translated"
    error = "error"


class FileTranslationStatus(Base):
    __tablename__ = "file_translation_status"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # "pending", "translated", "error"
    status = Column(Enum(TranslationStatusEnum), nullable=False, default=TranslationStatusEnum.pending)
    
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to file
    file = relationship("File", backref="translation_status")
