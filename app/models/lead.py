from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re
from typing import Optional

LEAD_COLLECTION = "leads"


class LeadBase(BaseModel):
    name: str = Field(
        ..., min_length=1, description="Valid name", examples=["João Silva"]
    )
    email: EmailStr = Field(..., description="Valid email", examples=["joao@email.com"])
    phone: str = Field(
        ..., description="Valid phone number", examples=["+5511999999999"]
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError(
                "The phone number should be in format like (ex: +5511999999999)"
            )
        return v


class LeadModel(LeadBase):
    birth_date: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
