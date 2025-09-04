from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ....core.database import get_db
from ....core.security import authenticate_user, create_access_token, get_current_user
from ....schemas.auth import (
    User as UserSchema,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    Token
)
from ....crud.user import (
    create_user,
    # get_google_auth_url,
    # save_user_google_account_info_and_access,
)
from ....models.user import User
from ....core.logger import setup_logger
# from ..enums import GoogleScopes


logger = setup_logger(__name__)
router = APIRouter()


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await authenticate_user(db, user.email, user.password)
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="User already exists")
        new_user = await create_user(db, user)
        logger.info(f"User signed up with email: {user.email}")
        return UserSchema.from_orm(new_user)
    except HTTPException as e:
        logger.error(f"HTTPException during signup: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"Access token created for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        logger.error(f"HTTPException during token generation: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token generation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/users/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Retrieved current user info for: {current_user.email}")
        return UserSchema.from_orm(current_user)
    except Exception as e:
        logger.error(f"Unexpected error retrieving current user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/login", response_model=UserLoginResponse, tags=["Authentication"])
async def login(
    login_data: UserLogin,  # Use the custom request model
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await authenticate_user(db, login_data.email, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User logged in: {user.email}")
        user = UserSchema.from_orm(user)
        token = Token(access_token=access_token, token_type="bearer")
        return UserLoginResponse(user=user, token=token)
    except HTTPException as e:
        logger.error(f"HTTPException during login: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

