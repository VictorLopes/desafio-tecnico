from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase
from app.models.lead import LEAD_COLLECTION, LeadModel
from app.schemas.lead import LeadCreate
from app.clients.external_api import fetch_birth_date


async def create_lead(db: AsyncDatabase, lead_data: LeadCreate) -> dict:
    birth_date = await fetch_birth_date()

    lead_model = LeadModel(**lead_data.model_dump(), birth_date=birth_date)

    lead_dict = lead_model.model_dump()

    try:
        result = await db[LEAD_COLLECTION].insert_one(lead_dict)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409, detail="Lead with this email already exists"
        )

    lead_dict["id"] = str(result.inserted_id)
    return lead_dict


async def get_all_leads(
    db: AsyncDatabase, page: int = 1, per_page: int = 50
) -> list[dict]:
    skip = (page - 1) * per_page
    cursor = db[LEAD_COLLECTION].find({}).skip(skip).limit(per_page)
    leads = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        leads.append(document)
    return leads


async def get_lead_by_id(db: AsyncDatabase, lead_id: str) -> dict | None:
    try:
        obj_id = ObjectId(lead_id)
    except Exception:
        return None

    document = await db[LEAD_COLLECTION].find_one({"_id": obj_id})
    if document:
        document["id"] = str(document["_id"])
        return document
    return None
