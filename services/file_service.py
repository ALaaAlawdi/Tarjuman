from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..core.config import settings
from ..core.logger import setup_logger
from pdf2docx import Converter
from docx import Document
from PyPDF2 import PdfReader
import subprocess

logger = setup_logger(__name__)

class FileService:
    def __init__(self, base_dir: Path = settings.UPLOAD_DIR,  media_base_dir: Path = settings.MEDIA_DIR):
        self.base_dir = base_dir
        self.media_base_dir = media_base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.media_base_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_file(self, file: UploadFile) -> dict | None:
        """
        Save an uploaded file to the uploads directory.
        """
        try:
            file_path = self.base_dir / file.filename
            with open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    f.write(chunk)

            logger.info(f"[FileService] Uploaded file saved: {file_path}")

            return {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "content_type": file.content_type,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            }
        except Exception as e:
            logger.error(f"[FileService] File upload failed: {e}")
            return None

    # convert pdf to docx 
    def convert_pdf_to_docx(self, pdf_filename: str) -> Path | None:
        """
        Convert a PDF file to a DOCX file using pdf2docx.
        """
        try:
            pdf_path = self.base_dir / pdf_filename
            output_path = pdf_path.with_suffix(".docx")

            logger.info(f"[FileService] Converting PDF to DOCX: {pdf_path}")
            cv = Converter(str(pdf_path))
            cv.convert(str(output_path), start=0, end=None)
            cv.close()

            logger.info(f"[FileService] Converted to DOCX: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"[FileService] PDF to DOCX conversion failed: {e}")
            return None
        
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

    #  convert word to md file 
    def convert_docx_to_markdown(self, docx_filename: str, file_id: str) -> Path | None:
        """
        Convert a DOCX file to Markdown using Pandoc.
        Extracts media (images) into media/images/{file_id}/.
        """
        try:
            docx_path = self.base_dir / docx_filename
            output_path = docx_path.with_suffix(".md")

            media_output_dir = self.media_base_dir / file_id
            media_output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"[FileService] Converting DOCX to Markdown: {docx_path}")
            command = (
                f'pandoc "{docx_path}" -o "{output_path}" '
                f'--extract-media="{media_output_dir}"'
            )
            subprocess.run(command, shell=True, check=True)

            logger.info(f"[FileService] Extracted media to: {media_output_dir}")
            logger.info(f"[FileService] Converted to Markdown: {output_path}")

            return output_path
        except Exception as e:
            logger.error(f"[FileService] DOCX to Markdown conversion failed: {e}")
            return None
    
    # Convert markdown to word file 
    def convert_markdown_to_docx(self, markdown_filename: str, file_id: str) -> Path | None:
        """
        Convert Markdown back to DOCX using Pandoc.
        Supports images stored in media/images/{file_id}/.
        """
        try:
            md_path = self.base_dir / markdown_filename
            output_path = self.base_dir / md_path.with_suffix(".docx").name
            resource_path = self.media_base_dir / file_id

            logger.info(f"[FileService] Converting Markdown to DOCX: {md_path}")
            command = (
                f'pandoc "{md_path}" -o "{output_path}" '
                f'--resource-path="{resource_path}"'
            )
            subprocess.run(command, shell=True, check=True)

            logger.info(f"[FileService] Markdown converted to DOCX: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"[FileService] Markdown to DOCX conversion failed: {e}")
            return None

    

    



file_service = FileService()