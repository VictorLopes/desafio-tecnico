from pymongo import AsyncMongoClient
from app.core.config import settings


class MongoDB:
    client: AsyncMongoClient = None
    db = None


db_client = MongoDB()


async def connect_to_mongo():
    db_client.client = AsyncMongoClient(settings.MONGODB_URL)
    db_client.db = db_client.client[settings.DATABASE_NAME]


async def close_mongo_connection():
    if db_client.client:
        await db_client.client.close()


async def get_db():
    if db_client.db is None:
        raise RuntimeError("Database not initialized")
    yield db_client.db
