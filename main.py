from fastapi import FastAPI
from database import engine,Base
from contextlib import asynccontextmanager
from handlers import handle_business_error, handle_forbidden_error, handle_not_found_error
from routers import router as users_router,auth_router
from project_router import proj_router as project_router
from task_router import task_router as task_router
from middleware import LoggingMiddleware
from exceptions import NotFoundError,ForbiddenError,BusinessError


# Explain this function how it works? is this lifespan function automatically run at startup? and engine code as well?
# @asynccontextmanager
# async def lifespan(app):
#     #create all tables
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield

app = FastAPI(title='DevBoard')
app.add_middleware(LoggingMiddleware)
app.add_exception_handler(NotFoundError,handle_not_found_error)
app.add_exception_handler(ForbiddenError,handle_forbidden_error)
app.add_exception_handler(BusinessError,handle_business_error)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)

@app.get('/')
async def root():
    return {"message": "DevBoard is running", "version": "0.1.0"}

@app.get('/health')
async def health_check():
    return {
    "status": "healthy",
    "app": "DevBoard",
    }   

