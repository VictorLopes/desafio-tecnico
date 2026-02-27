from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "leads"
    EXTERNAL_API_URL: str = "https://dummyjson.com/users/1"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
