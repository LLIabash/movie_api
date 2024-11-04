from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from users.models import User
from users.schemas import UserCreate
from users.utils import hash_password

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = await hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()
