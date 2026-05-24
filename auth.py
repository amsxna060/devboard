from jose import jwt,JWTError
import bcrypt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
import secrets
from typing import Optional
from datetime import timedelta,datetime,timezone
from fastapi import Depends,HTTPException,status
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model import User
from schemas import UserOut

# Constants
SECRET_KEY = "devboard-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer('/auth/login') # OAuth2PasswordBearer pointing to /auth/login

# Two functions
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")



def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
        )

def create_access_token(data:dict,expire_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    exp_delta = datetime.now(timezone.utc) + (expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode['exp'] = exp_delta
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:str = Depends(oauth2_scheme),db:AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email = payload["sub"]
        results = await db.execute(select(User).where(User.email == email))
        user = results.scalar_one_or_none()
        if not user : 
            raise HTTPException(401, "Could not validate credentials")
        return user
    except JWTError as e:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # OAuth2 spec requires this
    )


