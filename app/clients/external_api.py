import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def fetch_birth_date() -> str | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.EXTERNAL_API_URL, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            return data.get("birthDate")
    except Exception as e:
        logger.error(f"Failed to fetch birth date from external API: {e}")
        return None
