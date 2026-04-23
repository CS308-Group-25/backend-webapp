from unittest.mock import MagicMock, patch

from core.database import get_db
from core.security import create_access_token
from main import app


def _override_get_db():
    # get_db normally opens a real PostgreSQL session via SQLAlchemy.
    # We override it here so FastAPI injects a MagicMock instead,
    # keeping this test fully in-memory with no database connection.
    yield MagicMock()


def test_admin_products_with_customer_token_returns_403(client):
    customer_token = create_access_token({"user_id": 1, "role": "customer"})

    app.dependency_overrides[get_db] = _override_get_db

    with patch("core.dependencies.UserRepository") as MockRepo:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role = "customer"
        MockRepo.return_value.get_by_id.return_value = mock_user

        client.cookies.set("access_token", customer_token)
        response = client.post("/api/v1/admin/products/", json={})
        client.cookies.clear()

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_admin_products_with_no_token_returns_401(client):
    app.dependency_overrides[get_db] = _override_get_db

    response = client.post("/api/v1/admin/products/", json={})

    app.dependency_overrides.clear()

    assert response.status_code == 401
