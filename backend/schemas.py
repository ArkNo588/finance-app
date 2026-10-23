from datetime import date as DateType
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class Token(BaseModel):
    access_token: str
    token_type: str


TransactionType = Literal["buy", "sell", "dividend", "deposit", "withdrawal"]


class TransactionCreate(BaseModel):
    account_id: int
    type: TransactionType
    ticker: str | None = Field(default=None, max_length=20)
    quantity: Decimal | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    amount: Decimal | None = Field(default=None, gt=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    date: DateType
    note: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def check_fields(self):
        if self.type in ("buy", "sell"):
            if not self.ticker or self.quantity is None or self.unit_price is None:
                raise ValueError("ticker, quantity et unit_price sont requis")
        elif self.amount is None:
            raise ValueError("amount est requis pour ce type de transaction")
        return self


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: str
    ticker: str | None
    quantity: Decimal | None
    unit_price: Decimal | None
    amount: Decimal
    fees: Decimal
    date: DateType
    note: str | None


class PositionRead(BaseModel):
    account_id: int
    ticker: str
    quantity: Decimal
    average_cost: Decimal
    total_cost: Decimal
    last_price: Decimal | None = None
    price_date: DateType | None = None
    market_value: Decimal | None = None
    unrealized_pl: Decimal | None = None


class AccountValue(BaseModel):
    account_id: int
    name: str
    type: str
    cash: Decimal
    holdings_value: Decimal
    total_value: Decimal
    unpriced_positions: int


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    currency: str
    price_date: DateType