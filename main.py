from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session, engine, Base, get_session_local
from crud import create_user, get_user_by_email
from schemas import LoginRequestBody, UserCreate, UserResponse
from utils import create_access_token, get_current_user, verify_password

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_session_local)):
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db, user)

@app.post("/login", response_model=dict)
async def login_for_access_token(
    form_data: LoginRequestBody,  # Схема для тела запроса
    db: AsyncSession = Depends(get_session_local)
):
    user = await get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_model=UserResponse)
async def read_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user
