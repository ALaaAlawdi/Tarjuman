import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.logger import setup_logger
from ..services.file_service import file_service
from ..crud.translate import update_translation_status
from ..agentic.llms.openai_client import get_openai_client
from ..agentic.prompts.translate import get_translate_prompt




logger = setup_logger(__name__)

async def run_translation_pipeline(
    file_id: int,
    filename: str,
    db: AsyncSession,
):
    try:
        logger.info(f"[Pipeline] Starting translation for file: {filename}")

        # Step 1: Detect file extension
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            docx_path = file_service.convert_pdf_to_docx(filename)
            if not docx_path:
                raise ValueError("PDF to DOCX conversion failed")
        elif ext == ".docx":
            docx_path = file_service.base_dir / filename
        else:
            raise ValueError("Unsupported file format")

        # Step 2: Convert DOCX → Markdown
        md_path = file_service.convert_docx_to_markdown(docx_path.name, str(file_id))
        if not md_path:
            raise ValueError("DOCX to Markdown conversion failed")

        # Step 3: Read page-by-page from Markdown
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        pages = content.split("\f") if "\f" in content else content.split("\n\n\n")
        translated_pages = []

        llm = get_openai_client()

        for i, page in enumerate(pages):
            if not page.strip():
                continue

            prompt = get_translate_prompt("Arabic", page)
            response = await llm.ainvoke(prompt)

            translated_pages.append(f'<div dir="rtl">{response.content.strip()}</div>')
            logger.info(f"[Pipeline] Translated page {i+1}")

        # Step 4: Save translated Markdown
        translated_md_path = md_path.with_name(f"{md_path.stem}_translated.md")
        with open(translated_md_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(translated_pages))

        # Step 5: Convert translated Markdown → DOCX
        final_docx_path = file_service.convert_markdown_to_docx(
            translated_md_path.name, str(file_id)
        )
        if not final_docx_path:
            raise ValueError("Markdown to DOCX conversion failed")

        # Step 6: Update status in DB
        await update_translation_status(
            db=db,
            file_id=file_id,
            status="translated",
            translated_path=str(final_docx_path),
        )

        logger.info(f"[Pipeline] Translation completed: {final_docx_path}")

    except Exception as e:
        logger.error(f"[Pipeline] Error in translation: {e}")
        await update_translation_status(
            db=db,
            file_id=file_id,
            status="error",
            error_message=str(e),
        )
