from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    amount: Decimal = Field(ge=0)


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vendor: str | None = None
    invoice_number: str | None = None
    date: date_type | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: Decimal | None = Field(default=None, ge=0)
    tax: Decimal | None = Field(default=None, ge=0)
    total: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
