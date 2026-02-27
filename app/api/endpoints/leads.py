from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.asynchronous.database import AsyncDatabase
from app.db.mongodb import get_db
from app.schemas.lead import (
    LeadCreate,
    LeadResponseEnvelope,
    LeadListResponseEnvelope,
    ErrorResponseEnvelope,
)
from app.services import lead_service

router = APIRouter()


@router.post(
    "/",
    response_model=LeadResponseEnvelope,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponseEnvelope, "description": "Lead already exists"},
        422: {"model": ErrorResponseEnvelope, "description": "Validation Error"},
    },
)
async def create_lead(lead: LeadCreate, db: AsyncDatabase = Depends(get_db)):
    result = await lead_service.create_lead(db, lead)
    return {"status": "Ok", "data": result}


@router.get(
    "/",
    response_model=LeadListResponseEnvelope,
    responses={
        422: {"model": ErrorResponseEnvelope, "description": "Validation Error"}
    },
)
async def list_leads(
    page: int = 1, per_page: int = 50, db: AsyncDatabase = Depends(get_db)
):
    result = await lead_service.get_all_leads(db, page=page, per_page=per_page)
    return {"status": "Ok", "data": result}


@router.get(
    "/{lead_id}",
    response_model=LeadResponseEnvelope,
    responses={
        404: {"model": ErrorResponseEnvelope, "description": "Lead not found"},
        422: {"model": ErrorResponseEnvelope, "description": "Validation Error"},
    },
)
async def get_lead(lead_id: str, db: AsyncDatabase = Depends(get_db)):
    lead = await lead_service.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "Ok", "data": lead}
