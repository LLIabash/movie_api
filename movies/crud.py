from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from movies.models import FavoriteMovie

async def add_favorite_movie(db: AsyncSession, favorite_movie: FavoriteMovie):
    db.add(favorite_movie)
    await db.commit()

async def delete_favorite_movie(db: AsyncSession, user_id: int, kinopoisk_id: int):
    query = select(FavoriteMovie).where(
        FavoriteMovie.user_id == user_id,
        FavoriteMovie.kinopoisk_id == kinopoisk_id
    )
    result = await db.execute(query)
    favorite_movie = result.scalars().first()

    if favorite_movie:
        await db.delete(favorite_movie)
        await db.commit() 
    else:
        raise HTTPException(status_code=404, detail="Favorite movie not found")

async def is_favorite_movie_exists(db: AsyncSession, user_id: int, kinopoisk_id: int) -> bool:
    query = select(FavoriteMovie).where(
        FavoriteMovie.user_id == user_id,
        FavoriteMovie.kinopoisk_id == kinopoisk_id
    )
    result = await db.execute(query)
    return result.scalar() is not None