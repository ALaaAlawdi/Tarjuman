from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ....schemas.file import UploadResponse, FileOut
from ....services.file_service import file_service
from ....crud.file import create_file, get_user_files, get_file_by_id, delete_file
from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User

router = APIRouter()


@router.post("/upload", response_model=FileOut)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Save to disk
    file_data = await file_service.save_file(file)
    # Save metadata to DB
    db_file = await create_file(db, file_data, current_user.id)
    return db_file

@router.get("/", response_model=list[FileOut])
async def list_files(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_files(db, current_user.id)

@router.get("/{file_id}", response_model=FileOut)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_file = await get_file_by_id(db, file_id, current_user.id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.delete("/{file_id}", response_model=dict)
async def remove_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_file(db, file_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found or already deleted")
    return {"status": "success", "message": "File deleted"}
