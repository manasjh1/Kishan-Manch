from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Base
from database import get_db, engine
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/api/register")
async def register_user(user: dict, db: AsyncSession = Depends(get_db)):
    username = user["username"]
    password = user["password"]

    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(username=username, password=password)
    db.add(new_user)
    await db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login_user(user: dict, db: AsyncSession = Depends(get_db)):
    username = user["username"]
    password = user["password"]

    result = await db.execute(select(User).where(User.username == username))
    user_record = result.scalar_one_or_none()

    if not user_record or user_record.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
