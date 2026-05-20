from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RevenueDataPoint(BaseModel):
    date: date
    revenue: Decimal
    profit: Decimal

    model_config = {"from_attributes": True}


class RevenueReportResponse(BaseModel):
    revenue: Decimal
    cost: Decimal
    profit: Decimal
    chart_data: list[RevenueDataPoint]