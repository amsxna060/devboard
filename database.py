from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

CONNECTION_STRING = "sqlite+aiosqlite:///./devboard.db"

engine = create_async_engine(CONNECTION_STRING,
                             pool_size = 5,
                             max_overflow = 10,
                             pool_timeout = 30,
                             pool_recycle = 1800,
                             pool_pre_print = True,
                             echo=True)

AsyncSessionLocal = async_sessionmaker(engine,expire_on_commit=False)

class Base(DeclarativeBase):
    pass



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # your code here
    # hint: async with AsyncSessionLocal() as session:
    async with AsyncSessionLocal() as session:
        yield session


