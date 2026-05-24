from fastapi import APIRouter, Depends,HTTPException,status
from database import get_db
from schemas import UserOut,TokenOut,UserRegister
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from model import User
from fastapi.security import OAuth2PasswordRequestForm
from auth import verify_password, create_access_token,hash_password,get_current_user


router = APIRouter(prefix="/users",tags=["users"])
auth_router = APIRouter(prefix="/auth",tags=["auth"])

@router.post('/register',response_model=UserOut)
async def register_user(user:UserRegister, db : AsyncSession = Depends(get_db)):
    results = await db.execute(select(User).where(User.email==user.email))
    DBuser = results.scalar_one_or_none()
    if DBuser:
        raise HTTPException(400,"Email Already registered")
    new_user = User(
        email = user.email,
        name = user.name,
        password_hash = hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserOut.model_validate(new_user)

@router.get('/',response_model=List[UserOut])
async def get_all_user(db:AsyncSession=Depends(get_db)):
    results = await db.execute(select(User))
    userlist = results.scalars().all()
    return userlist

@auth_router.post('/login')
async def login_user(form : OAuth2PasswordRequestForm = Depends(),db: AsyncSession = Depends(get_db)):
    email = form.username
    password = form.password
    results = await db.execute(select(User).where(User.email == email))
    user = results.scalar_one_or_none()
    if not user : 
        raise HTTPException(401, "Could not validate credentials")
    if not verify_password(password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Password is Incorrect")
    payload = {
        "sub":user.email
    }
    token = create_access_token(payload)
    return TokenOut(access_token=token)

@auth_router.get('/me')
async def get_me(user:UserOut = Depends(get_current_user)):
    return user

    
    
    

