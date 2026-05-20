from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from modules.reports.repository import ReportsRepository
from modules.reports.schema import RevenueDataPoint, RevenueReportResponse

COST_MARGIN = Decimal("0.60")


class ReportsService:
    def __init__(self, db: Session):
        self.repository = ReportsRepository(db)

    def get_revenue_report(
        self, from_date: date, to_date: date
    ) -> RevenueReportResponse:
        daily_rows = self.repository.get_revenue_by_date(from_date, to_date)

        chart_data = []
        total_revenue = Decimal("0")

        for day, revenue in daily_rows:
            profit = revenue * (1 - COST_MARGIN)
            total_revenue += revenue
            chart_data.append(
                RevenueDataPoint(date=day, revenue=revenue, profit=profit)
            )

        total_cost = total_revenue * COST_MARGIN
        total_profit = total_revenue - total_cost

        return RevenueReportResponse(
            revenue=total_revenue,
            cost=total_cost,
            profit=total_profit,
            chart_data=chart_data,
        )