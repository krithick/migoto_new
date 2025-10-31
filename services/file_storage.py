# services/file_storage.py

import os
import shutil
import aiofiles
import mimetypes
from typing import Dict, List, Optional
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from datetime import datetime

class FileStorageService:
    """Service for handling file uploads and storage"""
    
    def __init__(
        self, 
        base_upload_dir: str = None,
        local_url_prefix: str = None,
        live_url_prefix: str = None
    ):
        self.base_upload_dir = base_upload_dir or os.environ.get("UPLOAD_DIR", "uploads")
        self.local_url_prefix = local_url_prefix or os.environ.get("LOCAL_URL_PREFIX", "http://localhost:9000/uploads")
        self.live_url_prefix = live_url_prefix or os.environ.get("LIVE_URL_PREFIX", "https://meta.novactech.in:5885/uploads")
        
        # Create base directory if it doesn't exist
        os.makedirs(self.base_upload_dir, exist_ok=True)
        
        # Create subdirectories for different file types
        self.subdirs = ["document", "video", "image", "audio", "other"]
        for subdir in self.subdirs:
            os.makedirs(os.path.join(self.base_upload_dir, subdir), exist_ok=True)
    
    async def save_file(
        self, 
        file: UploadFile, 
        file_type: str,
        max_file_size: int = 100 * 1024 * 1024  # 100MB default
    ) -> Dict[str, str]:
        """
        Save an uploaded file to the appropriate directory
        Returns dict with file info including the generated URLs
        
        Args:
            file: The uploaded file
            file_type: Type of file (document, video, image, etc.)
            max_file_size: Maximum allowed file size in bytes
            
        Returns:
            Dict with file metadata
        """
        # Validate file type
        if file_type not in self.subdirs:
            file_type = "other"
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_file_size/1024/1024}MB"
            )
        
        # Get original filename and extension
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid4()).replace("-", "")[:8]
        new_filename = f"{timestamp}_{unique_id}{file_ext}"
        
        # Determine save path
        save_path = os.path.join(self.base_upload_dir, file_type, new_filename)
        
        # Save the file
        try:
            async with aiofiles.open(save_path, "wb") as out_file:
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file: {str(e)}"
            )
            
        # Determine mime type
        mime_type, _ = mimetypes.guess_type(save_path)
        if not mime_type:
            if file_type == "document":
                mime_type = "application/octet-stream"
            elif file_type == "video":
                mime_type = "video/mp4"
            elif file_type == "image":
                mime_type = "image/jpeg"
            elif file_type == "audio":
                mime_type = "audio/mpeg"
            else:
                mime_type = "application/octet-stream"
        
        # Generate URLs
        local_url = f"{self.local_url_prefix}/{file_type}/{new_filename}"
        live_url = f"{self.live_url_prefix}/{file_type}/{new_filename}"
        
        # Return file info
        return {
            "original_filename": original_filename,
            "new_filename": new_filename,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": file_size,
            "file_path": save_path,
            "local_url": local_url,
            "live_url": live_url,
            "upload_date": datetime.now().isoformat()
        }
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the filesystem
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_path_from_url(self, url: str) -> Optional[str]:
        """
        Convert a URL back to a file path
        
        Args:
            url: Local or live URL to a file
            
        Returns:
            The file path if it can be determined, None otherwise
        """
        # Handle local URL
        if url.startswith(self.local_url_prefix):
            path_part = url[len(self.local_url_prefix):]
            if path_part.startswith("/"):
                path_part = path_part[1:]
            return os.path.join(self.base_upload_dir, path_part)
        
        # Handle live URL
        if url.startswith(self.live_url_prefix):
            path_part = url[len(self.live_url_prefix):]
            if path_part.startswith("/"):
                path_part = path_part[1:]
            return os.path.join(self.base_upload_dir, path_part)
        
        return None

# Create a singleton instance
file_storage_service = FileStorageService()