# core/file_upload.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException,Depends
from uuid import UUID, uuid4
import os
from models.file_models import FileUploadDB
from typing import Literal,Any
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["File Upload"])
UPLOAD_DIR = "static/uploads"

async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

@router.post("/file", response_model=FileUploadDB)
async def upload_file(
    entity_type: Literal["course", "module", "scenario", "language", "bot_voice"] = Form(...),
    entity_id: UUID = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_database)
):
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid4()}{ext}"
        save_dir = os.path.join(UPLOAD_DIR, entity_type)
        save_path = os.path.join(save_dir, unique_name)
        os.makedirs(save_dir, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        file_url = f"/{save_path}"  # served via static

        file_record = FileUploadDB(
            entity_type=entity_type,
            entity_id=entity_id,
            filename=file.filename,
            file_url=file_url,
            uploaded_at=datetime.utcnow()
        )

        await db.fileupload.insert_one(file_record.dict(by_alias=True))

        return file_record

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
