from typing import TypeVar, Generic,Optional,List
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from model import Task
from sqlalchemy import select
from sqlalchemy.orm import selectinload

T = TypeVar('T')

class BaseRepository(ABC,Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_by_id(self,id: int) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass
    @abstractmethod
    async def create(self,data: dict) -> T:
        pass
    @abstractmethod
    async def delete(self,id: int) -> bool:
        pass

class TaskRepository(BaseRepository[Task]):
    async def get_by_id(self, id: int) -> Optional[Task]:
        result = await self.session.execute(select(Task).where(Task.id == id).options(selectinload(Task.assignee),selectinload(Task.project)))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Task]:
        result = await self.session.execute(select(Task).options(selectinload(Task.assignee),selectinload(Task.project)))
        return result.scalars().all()

    async def create(self, data: dict) -> Task:
        new_task = Task(**data)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task

    async def delete(self, id: int) -> bool:
        task = await self.get_by_id(id)
        if task:
            await self.session.delete(task)
            await self.session.commit()
            return True
        return False

