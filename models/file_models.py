# models/file_upload.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal

class FileUploadDB(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    entity_type: Literal["course", "module", "scenario", "language", "bot_voice"]
    entity_id: UUID
    file_url: str
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}
