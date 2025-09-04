import jwt
from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from .config import settings
from .database import get_db
from ..models.user import User, UserGoogleAccount

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.AGENT_VERSION_ROUTER_API}/auth/token"
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.ACCESS_TOKEN_EXPIRY_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_google_token_by_user(
    db: AsyncSession, user_id: str
) -> UserGoogleAccount | None:
    result = await db.execute(
        select(UserGoogleAccount).filter(
            UserGoogleAccount.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_user_by_email(db, email)
    if not user:
        raise credentials_exception
    return user


async def get_current_user_from_token(
    token: str,
    db: AsyncSession,
) -> User:
    """
    Authenticate user from JWT token string directly.
    Used for WebSocket authentication where token comes from URL path.
    """
    try:
        if not token:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="Missing token"
            )
        
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise Exception("Token missing subject")

        user = await get_user_by_email(db, email)
        if not user:
            raise Exception("User not found")

        return user
    except Exception as e:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason=f"Auth failed: {str(e)}"
        )


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        token = websocket.headers.get("authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            token = websocket.query_params.get("token")

        if not token:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="Missing token"
            )
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise Exception("Token missing subject")

        user = await get_user_by_email(db, email)
        if not user:
            raise Exception("User not found")

        return user
    except Exception as e:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason=f"Auth failed: {str(e)}"
        )