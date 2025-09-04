from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..crud.user import create_user, get_user_by_email
from ..schemas.auth import UserCreate

from ..core.config import settings


async def register_user(db: AsyncSession, user_data: UserCreate):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return await create_user(db, user_data)