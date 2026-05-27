import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
# import app from main FastAPI application
from main import app
from database import Base, get_db

TEST_DB_STRING = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Fresh engine pointing to test DB
    engine = create_async_engine(TEST_DB_STRING)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Fresh sessionmaker bound to test engine
    test_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with test_session_factory() as session:
        yield session   # test runs here

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()   # close all connections


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post("/users/register", json={
        "email": "test@test.com",
        "name": "Test User",
        "password": "Test@123"
    })
    response = client.post("/auth/login", data={
        "username": "test@test.com",
        "password": "Test@123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}