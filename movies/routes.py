import os
from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from movies.crud import add_favorite_movie, delete_favorite_movie, is_favorite_movie_exists
from movies.models import FavoriteMovie
from users.schemas import UserResponse
from users.utils import get_current_user
from typing import List, Dict, Any
from database import get_session_local

movie_router = APIRouter()

API_KEY = os.getenv("KINOPOISK_API_KEY")

@movie_router.get("/search", response_model=list)
async def search_movies(query: str, current_user: UserResponse = Depends(get_current_user)):
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    url = f"https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={query}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Kinopoisk")

    movies_data = response.json().get('films', [])
    
    short_info = [
        {
            "title": movie.get("nameRu"), 
            "description": movie.get("description"),  
            "year": movie.get("year"),
            "filmId": movie.get("filmId")
        }
        for movie in movies_data
    ]
    
    return short_info

@movie_router.get("/favorites", response_model=List[Dict[str, Any]])
async def view_favorites(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_local)
):
    favorite_movies = await get_favorite_movies(db, current_user.id)
    movies_with_details = []
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        for movie in favorite_movies:
            url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie.kinopoisk_id}"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                movie_details = response.json()
                movies_with_details.append({
                    "id": movie.id,
                    "kinopoisk_id": movie.kinopoisk_id,
                    "details": movie_details
                })
            else:
                movies_with_details.append({
                    "id": movie.id,
                    "kinopoisk_id": movie.kinopoisk_id,
                    "details": {"error": "Failed to fetch details"}
                })

    return movies_with_details

@movie_router.post("/favorites")
async def add_to_favorites(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_local)
):
    body = await request.json()
    kinopoisk_id = body.get("kinopoisk_id")

    if kinopoisk_id is None:
        raise HTTPException(status_code=400, detail="kinopoisk_id is required")

    if await is_favorite_movie_exists(db, current_user.id, kinopoisk_id):
        raise HTTPException(status_code=400, detail="This movie is already in favorites")

    favorite_movie = FavoriteMovie(user_id=current_user.id, kinopoisk_id=kinopoisk_id)
    await add_favorite_movie(db, favorite_movie)
    return {"message": "Movie added to favorites"}

@movie_router.delete("/favorites/{kinopoisk_id}")
async def remove_from_favorites(
    kinopoisk_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_local)
):
    if not await is_favorite_movie_exists(db, current_user.id, kinopoisk_id):
        raise HTTPException(status_code=404, detail="Movie not found in favorites")

    await delete_favorite_movie(db, current_user.id, kinopoisk_id)
    
    return {"message": "Movie removed from favorites"}

async def get_favorite_movies(db: AsyncSession, user_id: int):
    query = select(FavoriteMovie).where(FavoriteMovie.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
