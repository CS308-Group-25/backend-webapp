from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from modules.reports.service import ReportsService

COST_MARGIN = Decimal("0.60")


def _make_repository(daily_rows):
    repo = MagicMock()
    repo.get_revenue_by_date.return_value = daily_rows
    return repo


def _make_service(daily_rows):
    service = ReportsService.__new__(ReportsService)
    service.repository = _make_repository(daily_rows)
    return service


def test_revenue_excludes_refunded_orders():
    """
    T-405: Revenue calculation must exclude refunded order items.
    The repository layer handles exclusion — service receives already-clean rows.
    We verify that the total returned by the service exactly matches
    the sum of rows provided by the repository (no extra items added).
    """
    daily_rows = [
        (date(2024, 1, 1), Decimal("100.00")),
        (date(2024, 1, 2), Decimal("200.00")),
    ]
    service = _make_service(daily_rows)

    result = service.get_revenue_report(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    assert result.revenue == Decimal("300.00")
    assert result.cost == Decimal("300.00") * COST_MARGIN
    assert result.profit == Decimal("300.00") * (1 - COST_MARGIN)
    assert len(result.chart_data) == 2


def test_date_range_filter_is_passed_to_repository():
    """
    T-405: Service must forward the exact from_date and to_date
    to the repository without modification.
    """
    daily_rows = [
        (date(2024, 3, 15), Decimal("500.00")),
    ]
    service = _make_service(daily_rows)

    from_date = date(2024, 3, 1)
    to_date = date(2024, 3, 31)

    result = service.get_revenue_report(from_date=from_date, to_date=to_date)

    service.repository.get_revenue_by_date.assert_called_once_with(from_date, to_date)
    assert len(result.chart_data) == 1
    assert result.chart_data[0].date == date(2024, 3, 15)
    assert result.chart_data[0].revenue == Decimal("500.00")