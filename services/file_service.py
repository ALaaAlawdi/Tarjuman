from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..core.config import settings
from ..core.logger import setup_logger
from ..schemas.file import UploadResponse
from pdf2docx import Converter
from docx import Document
from PyPDF2 import PdfReader
import subprocess

logger = setup_logger(__name__)

class FileService:
    def __init__(self, base_dir: Path = settings.BASE_DIR,  media_base_dir: Path = settings.MEDIA_DIR):
        self.base_dir = base_dir
        self.media_base_dir = media_base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.media_base_dir.mkdir(parents=True, exist_ok=True)
        
    
    def make_file_workspace(self, user_id: int, file_id: int) -> dict:
            root = self.media_base_dir / f"user_{user_id}" / f"file_{file_id}"
            folders = {
                "root": root,
                "original": root / "original",
                "converted": root / "converted",
                "markdown": root / "markdown",
                "media": root / "media",
                "output": root / "output",
            }
            for f in folders.values():
                f.mkdir(parents=True, exist_ok=True)
            return folders

    async def save_file(self, file: UploadFile, user_id: int, file_id: int) -> Path:

        workspace = self.make_file_workspace(user_id, file_id)
        dest = workspace["original"] / file.filename

        with open(dest, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)

        logger.info(f"[FileService] Saved uploaded file → {dest}")
        return dest

   
    # ---------------------------
    # PDF → DOCX
    # ---------------------------
    def pdf_to_docx(self, pdf_path: Path, out_path: Path) -> Path:
        cv = Converter(str(pdf_path))
        cv.convert(str(out_path))
        cv.close()
        logger.info(f"Converted PDF → DOCX: {out_path}")
        return out_path
    
    # add read docx file 
    def read_docx_file(self, docx_filename: str) -> list[str] | None:
        """
        Read paragraphs from a DOCX file.
        """
        try:
            docx_path = self.base_dir / docx_filename
            logger.info(f"[FileService] Reading DOCX: {docx_path}")
            doc = Document(str(docx_path))
            return [p.text for p in doc.paragraphs if p.text.strip()]
        except Exception as e:
            logger.error(f"[FileService] Failed to read DOCX file: {e}")
            return None

    # read pdf file 
    def read_pdf_file(self, pdf_filename: str) -> str | None:
        """
        Extract plain text from a PDF file.
        """
        try:
            pdf_path = self.base_dir / pdf_filename
            reader = PdfReader(str(pdf_path))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            logger.info(f"[FileService] Extracted text from PDF: {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"[FileService] Failed to read PDF file: {e}")
            return None

    # ---------------------------
    # DOCX → Markdown
    # ---------------------------
    def docx_to_md(self, docx_path: Path, md_path: Path, media_dir: Path) -> Path:
        command = f'pandoc "{docx_path}" -o "{md_path}" --extract-media="{media_dir}"'
        subprocess.run(command, shell=True, check=True)
        return md_path
    
    # ---------------------------
    # Markdown → DOCX
    # ---------------------------
    def md_to_docx(self, md_path: Path, docx_out: Path, media_dir: Path) -> Path:
        command = (
            f'pandoc "{md_path}" -o "{docx_out}" --resource-path="{media_dir}"'
        )
        subprocess.run(command, shell=True, check=True)
        return docx_out
    

    



file_service = FileService()