from pydantic import BaseModel

class FavoriteMovieCreate(BaseModel):
    kinopoisk_id: int

class FavoriteMovieResponse(BaseModel):
    id: int
    kinopoisk_id: int

    class Config:
        orm_mode = True