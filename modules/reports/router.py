from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_sales_manager
from modules.auth.model import User
from modules.reports.schema import RevenueReportResponse
from modules.reports.service import ReportsService

router = APIRouter(prefix="/api/v1/admin/reports", tags=["reports"])


@router.get("/revenue", response_model=RevenueReportResponse)
def get_revenue_report(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_manager),
):
    service = ReportsService(db)
    return service.get_revenue_report(from_date, to_date)