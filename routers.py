from fastapi import APIRouter, Depends,HTTPException
from database import get_db
from schemas import UserCreate, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

router = APIRouter(prefix="/users",tags=["users"])

@router.post('/register',response_model=UserOut)
async def register_user(user:UserCreate, db : AsyncSession = Depends(get_db)):
    results = await db.execute(select(UserCreate).where(UserCreate.email==user.email))
    DBuser = results.scalar_one_or_none()
    if DBuser:
        raise HTTPException(400,"Email Already registered")
    new_user = UserCreate(user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/',response_model=List[UserOut])
async def get_all_user(db:AsyncSession=Depends(get_db)):
    results = await db.execute(select(UserCreate))
    userlist = results.scalars().all()
    return userlist