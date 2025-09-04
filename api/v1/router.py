from fastapi import APIRouter
from .endpoints import  upload, auth

api_router = APIRouter()


api_router.include_router(upload.router, prefix="/files", tags=["Files"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])