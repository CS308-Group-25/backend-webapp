from unittest.mock import MagicMock, patch

from fastapi import status

from core.database import get_db
from core.security import create_access_token
from main import app
from modules.invoices.model import Invoice as InvoiceModel
from modules.invoices.service import InvoiceService


def _override_get_db():
    yield MagicMock()


def test_get_invoice_by_order_id_success():
    # Arrange
    mock_invoice_repo = MagicMock()

    mock_invoice = MagicMock(spec=InvoiceModel)
    mock_invoice.id = 1
    mock_invoice.order_id = 10
    mock_invoice_repo.get_by_order_id.return_value = mock_invoice

    service = InvoiceService(mock_invoice_repo)

    # Act
    result = service.get_by_order_id(order_id=10)

    # Assert
    assert result.order_id == 10
    mock_invoice_repo.get_by_order_id.assert_called_once_with(10)


def test_get_invoice_wrong_user_returns_403(client):
    customer_token = create_access_token({"user_id": 1, "role": "customer"})

    app.dependency_overrides[get_db] = _override_get_db

    with patch("modules.invoices.router.OrderRepository") as MockOrderRepo:
        mock_order = MagicMock()
        mock_order.user_id = 2  # different user
        MockOrderRepo.return_value.get_by_order_id.return_value = mock_order

        client.cookies.set("access_token", customer_token)
        response = client.get("/api/v1/orders/99/invoice")
        client.cookies.clear()

    app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_403_FORBIDDEN
