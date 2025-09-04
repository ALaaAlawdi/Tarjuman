from pydantic import BaseModel

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    content_type: str
    path: str
    size_bytes: int

    class Config:
        orm_mode = True

class FileOut(BaseModel):
    id: int
    filename: str
    content_type: str
    path: str
    size_bytes: int

    class Config:
        orm_mode = True
