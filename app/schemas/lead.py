from pydantic import BaseModel
from app.models.lead import LeadBase, LeadModel


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadModel):
    id: str


class LeadResponseEnvelope(BaseModel):
    status: str = "Ok"
    data: LeadResponse


class LeadListResponseEnvelope(BaseModel):
    status: str = "Ok"
    data: list[LeadResponse]


class ErrorResponseEnvelope(BaseModel):
    status: str = "Error"
    data: str
