from ..models.file import File
from ..models.translation import FileTranslationStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update


async def create_translation_status(db: AsyncSession, file_id: int) -> FileTranslationStatus:
    status = FileTranslationStatus(
        file_id=file_id,
        status="pending",
        error_message=None
    )
    db.add(status)
    await db.commit()
    await db.refresh(status)
    return status


async def get_translation_status(db: AsyncSession, file_id: int) -> FileTranslationStatus | None:
    result = await db.execute(
        select(FileTranslationStatus).where(FileTranslationStatus.file_id == file_id)
    )
    return result.scalars().first()


async def update_translation_status(
    db: AsyncSession,
    file_id: int,
    status: str,
    error_message: str | None = None
) -> FileTranslationStatus | None:
    stmt = (
        update(FileTranslationStatus)
        .where(FileTranslationStatus.file_id == file_id)
        .values(status=status, error_message=error_message)
        .returning(FileTranslationStatus)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_translation_status(db: AsyncSession, file_id: int) -> bool:
    stmt = delete(FileTranslationStatus).where(FileTranslationStatus.file_id == file_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
