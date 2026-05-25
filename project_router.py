from typing import Annotated, List
from fastapi import Depends,APIRouter,HTTPException,status,Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,or_
from sqlalchemy.orm import selectinload
from auth import get_current_user
from database import get_db
from model import User,Project
from schemas import ProjectCreate,ProjectOut,ProjectUpdate

# Define these Annotated aliases at the top of the file
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# GET /projects — return all projects owned by current user (filter by owner_id)
# POST /projects — create project, set owner_id = current_user.id
# GET /projects/{id} — return one project (must be owner, else 403)
# PATCH /projects/{id} — update name/description (owner only)
#                        use response_model_exclude_unset=True
# DELETE /projects/{id} — delete (owner only)

proj_router = APIRouter(prefix="/projects",tags=["Projects"])

@proj_router.get('/', response_model=List[ProjectOut])
async def get_projects(user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.owner_id==user.id))
    projects = results.scalars().all()
    return [ProjectOut.model_validate(project) for project in projects]

@proj_router.post('/',response_model=ProjectOut)
async def create_project(project:ProjectCreate,user:CurrentUser,db:DbSession):
    db_project = Project(
        name = project.name,
        description = project.description,
        owner_id = user.id
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return ProjectOut.model_validate(db_project)

@proj_router.post("/seed")
async def seed_data(db: DbSession):
    """Temporary endpoint to create test data"""
    from model import Task, TaskStatus

    # Create 3 projects with tasks
    for i in range(1, 4):
        project = Project(
            name=f"Project {i}",
            description=f"Description for project {i}",
            owner_id=1   # assumes user with id=1 exists
        )
        db.add(project)
        await db.flush()   # flush to get project.id without committing

        for j in range(1, 4):
            task = Task(
                title=f"Task {j} in Project {i}",
                project_id=project.id,
                assignee_id=1
            )
            db.add(task)

    await db.commit()
    return {"message": "Seeded 3 projects with 3 tasks each"}

@proj_router.get("/with-tasks")
async def get_projects_with_tasks_naive(db: DbSession, user: CurrentUser)->List[dict]:
    """
    INTENTIONAL N+1 — Educational purposes
    This fetches projects, then accesses tasks relationship
    In async SQLAlchemy, this raises MissingGreenlet
    """
    result = await db.execute(select(Project).where(Project.owner_id == user.id))
    projects = result.scalars().all()

    # ❌ This is where N+1 happens
    # In sync SQLAlchemy: lazy loads tasks per project = N+1 queries
    # In async SQLAlchemy: raises MissingGreenlet error
    response = []
    for project in projects:
        response.append({
            "id": project.id,
            "name": project.name,
            "task_count": len(project.tasks),  # ← accessing relationship without loading
        })

    return response
@proj_router.get("/with-tasks-fixed")
async def get_projects_with_tasks_fixed(db: DbSession, user: CurrentUser) -> List[dict]:
    """
    CORRECT — Uses selectinload to prevent N+1
    Watch the logs: exactly 2 queries regardless of project count
    """
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == user.id)
        .options(selectinload(Project.tasks))  # ← load ALL tasks in one extra query
    )
    projects = result.scalars().all()

    response = []
    for project in projects:
        response.append({
            "id": project.id,
            "name": project.name,
            "task_count": len(project.tasks),  # ✅ already loaded — no extra query
            "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in project.tasks]
        })

    return response
@proj_router.get('/{id}',response_model=ProjectOut)
async def get_project(id:int,user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id,Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    return ProjectOut.model_validate(project)

@proj_router.patch('/{id}',response_model=ProjectOut,response_model_exclude_unset=True)
async def update_project(id:int,project_update:ProjectUpdate,user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id,Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    # Not Sure how to do Patch Update here, use response_model_exclude_unset=True this is also don't know how to use it.
    project_update = project_update.model_dump(exclude_unset=True)
    for key,value in project_update.items():
        setattr(project,key,value)
    await db.commit()
    await db.refresh(project)
    return ProjectOut.model_validate(project)

@proj_router.delete('/{id}')
async def delete_project(id:int,user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id,Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    await db.delete(project)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)




    



