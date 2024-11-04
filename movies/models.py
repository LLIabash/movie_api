from sqlalchemy import Column, ForeignKey, Integer
from database import Base

class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    kinopoisk_id = Column(Integer, nullable=False)
