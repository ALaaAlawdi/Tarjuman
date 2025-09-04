from fastapi import FastAPI
from .api.v1.router import api_router
from .core.database import engine, Base

# IMPORTANT: import all models so they register on Base.metadata
from .models.user import User
from .models.file import File
# from Tarjuman.models.whatever import Whatever

app = FastAPI(title="My App")
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def create_tables():
    # For dev only; switch to Alembic in prod
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
