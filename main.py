import os
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_session_local
from users.routes import user_router
from movies.routes import movie_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(user_router, tags=["users"])
app.include_router(movie_router, prefix="/movies", tags=["movies"])
