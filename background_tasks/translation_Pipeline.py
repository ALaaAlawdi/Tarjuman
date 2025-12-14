import os
from pathlib import Path
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.logger import setup_logger
from ..services.file_service import file_service
from ..crud.translate import update_translation_status
from ..agentic.llms.deepseek_client import get_deepseek_chat
from ..agentic.prompts.translate import get_translate_prompt
from ..services.file_service import file_service
from ..models.translation import TranslationStatusEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import asyncio


logger = setup_logger(__name__)


async def run_translation_pipeline(
    file_id: int,
    filename: str,
    user_id: int,
    db: AsyncSession,
):
    """Run translation pipeline by splitting the markdown into chunks,
    translating each chunk, writing translated markdown and converting back to DOCX.
    """
    try:
        logger.info(f"[Pipeline] Starting translation for file: {filename}")
        
        workspace = file_service.make_file_workspace(user_id, file_id)

        original_path = workspace["original"] / filename
        converted_docx = workspace["converted"] / "file.docx"
        markdown_path = workspace["markdown"] / "file.md"
        translated_md = workspace["markdown"] / "translated.md"
        final_docx = workspace["output"] / "final.docx"

    
        # mark processing
        await update_translation_status(db=db, file_id=file_id, status=TranslationStatusEnum.pending)

        # Step 1: Detect file extension
        ext = Path(filename).suffix.lower()
        
        # -------------------------
        # Step 1 — Convert to DOCX
        # -------------------------
        if ext == ".pdf":
            await asyncio.to_thread(file_service.pdf_to_docx, original_path, converted_docx)
        elif ext == ".docx":
            converted_docx = original_path
        else:
            raise ValueError("Unsupported file type")
        logger.info(f"[Pipeline] Converted to DOCX: {converted_docx}")

        # -------------------------
        # Step 2 — DOCX → Markdown
        # -------------------------
        await asyncio.to_thread(
            file_service.docx_to_md,
            converted_docx,
            markdown_path,
            workspace["media"]
         )
        
        content = markdown_path.read_text(encoding="utf-8")

        # -------------------------
        # Step 3 — Chunk & Translate
        # -------------------------
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0,
            separators=["\n\n", "\n", ".", " "]
        )

        chunks = splitter.split_text(content)
        llm = get_deepseek_chat()
        translated = []

        for idx, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {idx+1}/{len(chunks)}")
            prompt = get_translate_prompt("Arabic", chunk)
            resp = await llm.ainvoke(prompt)
            text = getattr(resp, "content", resp)
            translated.append(f"<div style=\"text-align: justify;\" dir=\"rtl\"> {text.strip()}</div>")
            

            await asyncio.sleep(0.03)

        translated_md.write_text("\n\n".join(translated), encoding="utf-8")

        # -------------------------
        # Step 4 — Markdown → DOCX
        # -------------------------
        await asyncio.to_thread(
            file_service.md_to_docx,
            translated_md,
            final_docx,
            workspace["media"]
        )

        await update_translation_status(
        db=db,
        file_id=file_id,
        status=TranslationStatusEnum.translated,
        error_message="File translated successfully",
            )

        logger.info(f"[Pipeline] DONE → {final_docx}")
        
    except Exception as e:
        logger.error(f"[Pipeline] Error during translation: {e}")
        await update_translation_status(
            db=db,
            file_id=file_id,
            status=TranslationStatusEnum.error,
            error_message=str(e)
        )
