from typing import Annotated
from fastapi import Depends,APIRouter,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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

proj_router = APIRouter("/projects",tags=["Projects"])

@proj_router.get('/')
async def get_projects(user:CurrentUser,db:DbSession):
    return user.projects

@proj_router.post('/')
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

@proj_router.get('/{id}')
async def get_project(user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id and Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    return ProjectOut.model_validate(project)

@proj_router.patch('/{id}')
async def get_project(user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id and Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    # Not Sure how to do Patch Update here, use response_model_exclude_unset=True this is also don't know how to use it.
    return ProjectOut.model_validate(project)

@proj_router.delete('/{id}')
async def get_project(user:CurrentUser,db:DbSession):
    results = await db.execute(select(Project).where(Project.id == id and Project.owner_id == user.id))
    project = results.scalar_one_or_none()
    if not project:
        raise HTTPException(403,detail="UnAuthourised User")
    await db.delete(project)
    await db.commit()
    return status.HTTP_204_NO_CONTENT


    



