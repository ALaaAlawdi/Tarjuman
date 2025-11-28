from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
from ....schemas.file import UploadResponse, FileOut
from ....services.file_service import file_service
from ....crud.file import create_file, get_user_files, get_file_by_id, delete_file
from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....crud.translate import create_translation_status
from ....background_tasks.translation_Pipeline import run_translation_pipeline
from pathlib import Path

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    
):  
    
    fake_meta = UploadResponse(
    status="pending",
    message="initial record",
    filename=file.filename,
    content_type=file.content_type,
    path="",          # file not saved yet
    size_bytes=0      # will update after save
    )


    db_file = await create_file(db, fake_meta, current_user.id)

    # Save to disk → returns dict
    saved_path = await file_service.save_file(
        file=file,
        user_id=current_user.id,
        file_id=db_file.id
    )

    # Update DB with physical path
    # 4️⃣ Update DB entry
    db_file.path = str(saved_path)
    db_file.size_bytes = Path(saved_path).stat().st_size
    db_file.status = "saved"
    db_file.message = "File uploaded successfully"

    await db.commit()
    await db.refresh(db_file)
    
    
    await create_translation_status(db, db_file.id)

    background_tasks.add_task(
        run_translation_pipeline,
        file_id=db_file.id,
        filename=db_file.filename,
        user_id=current_user.id,
        db=db
    )

    
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
