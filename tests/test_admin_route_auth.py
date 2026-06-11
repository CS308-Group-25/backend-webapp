from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt

from core.database import get_db
from core.security import ALGORITHM, SECRET_KEY, create_access_token
from main import app


def _override_get_db():
    # get_db normally opens a real PostgreSQL session via SQLAlchemy.
    # We override it here so FastAPI injects a MagicMock instead,
    # keeping this test fully in-memory with no database connection.
    yield MagicMock()


def _create_expired_token(data: dict) -> str:
    # create_access_token always sets exp in the future, so we encode
    # directly here with an exp in the past to forge an expired token.
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def test_admin_route_with_expired_token_returns_401(client):
    expired_token = _create_expired_token({"user_id": 1, "role": "product_manager"})

    app.dependency_overrides[get_db] = _override_get_db

    client.cookies.set("access_token", expired_token)
    response = client.post("/api/v1/admin/products/", json={})
    client.cookies.clear()

    app.dependency_overrides.clear()

    assert response.status_code == 401


def test_admin_route_with_customer_token_returns_403(client):
    # The token is valid, but require_admin loads the User from the DB and
    # rejects any role outside the admin set. We mock UserRepository to return
    # a customer so the route should respond 403 (forbidden), not 401.
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
