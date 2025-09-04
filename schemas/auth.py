from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserGoogleAccountCreate(BaseModel):
    user_id: int
    google_access_token: str
    google_refresh_token: str
    token_validity_in_seconds: int


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserCreate):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLoginResponse(BaseModel):
    user: User
    token: Token

    class Config:
        from_attributes = True


class GoogleAuthUrlRequest(BaseModel):
    scopes: list[str] = []


class GoogleAuthUrlResponse(BaseModel):
    auth_url: str
    error: bool = False
    error_message: str | None = None


class GoogleAuthCallbackResponse(BaseModel):
    message: str
    status: bool = False
