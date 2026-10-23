from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=30)
    institution: str | None = Field(default=None, max_length=100)
    balance: Decimal = Decimal("0")
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class AccountRead(AccountCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime