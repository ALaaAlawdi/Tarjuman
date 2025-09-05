from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..core.config import settings
from ..core.logger import setup_logger


logger = setup_logger(__name__)

class FileService:
    def __init__(self, base_dir: Path = settings.UPLOAD_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_file(self, file: UploadFile) -> dict:
        try:
            file_path = self.base_dir / file.filename
            with open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    f.write(chunk)

            logger.info(f"File uploaded: {file.filename} -> {file_path}")

            return {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "content_type": file.content_type,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            }
        except Exception as e:
            logger.error(f"File upload failed for {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # add read docx file 




    # add read pdf file 



    # add convert word to md file 

    

    



file_service = FileService()