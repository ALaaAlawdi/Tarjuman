from fastapi import APIRouter
from .endpoints import  upload

api_router = APIRouter()


api_router.include_router(upload.router, prefix="/files", tags=["Files"])
