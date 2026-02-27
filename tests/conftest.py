import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from app.main import app
from app.db.mongodb import get_db


@pytest.fixture(scope="session")
def mock_db_client():
    return AsyncMongoMockClient()


@pytest.fixture(scope="function")
async def mock_db(mock_db_client):
    db = mock_db_client["test_db"]
    collections = await db.list_collection_names()
    for col in collections:
        await db.drop_collection(col)
    return db


@pytest.fixture(scope="function", autouse=True)
def override_get_db(mock_db):
    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
