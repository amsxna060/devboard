from typing import Annotated, List,Optional
from fastapi import Depends,APIRouter,HTTPException,status,Response,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,or_,func
from sqlalchemy.orm import selectinload
from auth import get_current_user
from database import get_db
from model import User,Project,Task,TaskStatus
from schemas import TaskCreate,TaskOut,TaskUpdate,BulkAssignRequest
import asyncio
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


task_router = APIRouter(prefix="/tasks",tags=["Tasks"])

class PaginationParams:
    def __init__(self,skip : int =  Query(default=0,ge=0,description="Records to Skip"), 
                 limit:int = Query(default=10,ge=1,le=100,description="Record to show")):
        self.skip = skip
        self.limit = limit

Pagination = Annotated[PaginationParams,Depends(PaginationParams)]

@task_router.get('/',response_model=List[TaskOut])
async def get_all_task(user : CurrentUser, 
                       db : DbSession,pagination:Pagination,
                       status:Optional[TaskStatus] = None,
                       project_id:Optional[int]= None,
                       assignee_id:Optional[int] = None
                       ):
    stmt = select(Task).join(Project,Task.project_id == Project.id).where(Project.owner_id == user.id)
    if status:
        stmt = stmt.where(Task.status == status)
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
    if assignee_id:
        stmt = stmt.where(Task.assignee_id == assignee_id)

    results = await db.execute(stmt.offset(pagination.skip).limit(pagination.limit))
    tasks = results.scalars().all()
    return [TaskOut.model_validate(task) for task in tasks]

@task_router.get('/count')
async def count_project(user : CurrentUser, db : DbSession,
                        status:Optional[TaskStatus]= None,
                        project_id:Optional[int]= None,
                        assignee_id:Optional[int]= None
                       ):
    stmt = select(func.count(Task.id)).join(Project,Task.project_id == Project.id).where(Project.owner_id == user.id)

    if status:
        stmt = stmt.where(Task.status == status)
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
    if assignee_id:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    
    results = await db.execute(stmt)
    count = results.scalar_one()
    return {"Total": count}

@task_router.post("/", response_model=TaskOut)
async def create_task(data: TaskCreate, db: DbSession, user: CurrentUser):
    # Verify project belongs to user
    proj_result = await db.execute(
        select(Project).where(
            Project.id == data.project_id,
            Project.owner_id == user.id
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(404, "Project not found or not yours")

    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskOut.model_validate(task)

@task_router.post('/bulk-assign')
async def assign_bulk_task(bulktasks:BulkAssignRequest,db:DbSession,user:CurrentUser):
    current_user_results = await db.execute(select(Project.id).where(Project.owner_id==user.id))
    current_user_projects = current_user_results.scalars().all()
    sem = asyncio.Semaphore(3)
    async def assign_one(task_id):
        async with sem:
            results = await db.execute(select(Task).where(Task.id == task_id))
            task = results.scalar_one_or_none()
            if not task:
                raise HTTPException(404,'Task Not Found')
            if task.project_id not in current_user_projects:
                raise HTTPException(401,"Task Associate to Project Not Belong to Current User")
            task.assignee = bulktasks.assignee_id
            db.commit()
            return {"result":"assigned successfully"}
    
    results = await asyncio.gather(*[assign_one(task_id) for task_id in bulktasks.task_ids],return_exceptions=True)
    return {"succesfully assigned": sum(1 for d in results if d == {"result":"assigned successfully"})}

