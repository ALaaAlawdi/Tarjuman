from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User
from ..schemas.auth import UserCreate
from ..core.security import get_password_hash
from ..core.config import settings
from ..core.logger import setup_logger

logger = setup_logger(__name__)


async def create_user(db: AsyncSession, user: UserCreate) -> User | None:
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"Created user with email: {user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user with email {user.email}: {e}")
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            logger.info(f"Retrieved user by email: {email}")
        else:
            logger.info(f"No user found with email: {email}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {e}")
        return None
