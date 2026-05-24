from typing import Annotated
from fastapi import Depends,APIRouter,HTTPException,status,Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,or_
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


    



