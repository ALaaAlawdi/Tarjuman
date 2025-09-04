from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from ..models.file import File
from ..schemas.file import UploadResponse

async def create_file(db: AsyncSession, file_data: UploadResponse, user_id: int) -> File:
    db_file = File(
        filename=file_data.filename,
        content_type=file_data.content_type,
        path=file_data.path,
        size_bytes=file_data.size_bytes,
        user_id=user_id,
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file

async def get_user_files(db: AsyncSession, user_id: int) -> list[File]:
    result = await db.execute(select(File).where(File.user_id == user_id))
    return result.scalars().all()

async def get_file_by_id(db: AsyncSession, file_id: int, user_id: int) -> File | None:
    result = await db.execute(
        select(File).where(File.id == file_id, File.user_id == user_id)
    )
    return result.scalars().first()

async def delete_file(db: AsyncSession, file_id: int, user_id: int) -> bool:
    stmt = delete(File).where(File.id == file_id, File.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
