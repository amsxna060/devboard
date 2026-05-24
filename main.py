from fastapi import FastAPI
from database import engine,Base
from contextlib import asynccontextmanager
from routers import router as users_router,auth_router
from project_router import proj_router as project_router


# Explain this function how it works? is this lifespan function automatically run at startup? and engine code as well?
@asynccontextmanager
async def lifespan(app):
    #create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title='DevBoard',lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(project_router)

@app.get('/')
async def root():
    return {"message": "DevBoard is running", "version": "0.1.0"}

@app.get('/health')
async def health_check():
    return {
    "status": "healthy",
    "app": "DevBoard",
    }   

