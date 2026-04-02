from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from core.database import get_db
from main import app
from modules.auth.model import User as UserModel
from modules.auth.schema import LoginRequest, RegisterRequest
from modules.auth.service import AuthService, pwd_context


def test_register_hashes_password_never_plain_text():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_by_email.return_value = None  # Ensure user doesn't already exist
    
    # Setup dummy user to be returned when the mock repository creates a user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.role = "customer"
    mock_repo.create_user.return_value = mock_user

    service = AuthService(repo=mock_repo)
    plain_password = "super_secret_password"
    
    # Create the request that simulates user registration
    req = RegisterRequest(
        name="Test User",
        email="test@example.com",
        password=plain_password,
        tax_id="123456789",
        address="123 Example St"
    )

    # Act
    service.register(req)

    # Assert
    # Obtain the arguments that were passed into the repository's `create_user` method
    _, kwargs = mock_repo.create_user.call_args
    
    stored_hash = kwargs.get("password_hash")
    
    
    # 1. Confirm the password is never stored as plain text
    assert stored_hash is not None, (
        "A password hash should be provided to the repository."
    )

    assert stored_hash != plain_password, (
        "The stored password MUST NOT match the plain text!"
    )
    
    # 2. Confirm it was correctly hashed using our passlib configuration
    assert pwd_context.verify(plain_password, stored_hash) is True

def test_register_success(mock_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.role = "customer"

    mock_repo.get_by_email.return_value = None
    mock_repo.create_user.return_value = mock_user

    service = AuthService(repo=mock_repo)
    data = RegisterRequest(
        name="Test User",
        email="test@example.com",
        password="secret123",
        tax_id="12346789",
        address="123 Example St",
    )

    result = service.register(data)

    assert result.email == "test@example.com"
    assert result.role == "customer"

def test_register_duplicate_email_raises_400(mock_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.role = "customer"

    mock_repo.get_by_email.return_value = mock_user    

    service = AuthService(repo=mock_repo)
    data = RegisterRequest(
        name="Test User",
        email="test@example.com",
        password="secret123",
        tax_id="12346789",
        address="123 Example St",
    )

    with pytest.raises(HTTPException) as exc:
        service.register(data)

    assert exc.value.status_code == 400

def test_register_missing_fields_returns_422(client):
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422

def test_login_success_returns_token_and_user(mock_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.role = "customer"
    mock_user.password_hash = pwd_context.hash("secret123")

    mock_repo.get_by_email.return_value = mock_user

    service = AuthService(repo=mock_repo)
    data = LoginRequest(email="test@example.com", password="secret123")

    token, user = service.login(data)

    assert isinstance(token, str)
    assert len(token) > 0
    assert user.email == "test@example.com"

def test_login_wrong_password_raises_401(mock_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.role = "customer"
    mock_user.password_hash = pwd_context.hash("secret123")

    mock_repo.get_by_email.return_value = mock_user

    service = AuthService(repo=mock_repo)
    data = LoginRequest(email="test@example.com", password="wrong_password_input")

    with pytest.raises(HTTPException) as exc:
        service.login(data)

    assert exc.value.status_code == 401

def test_login_user_not_found_raises_401(mock_repo):
    mock_repo.get_by_email.return_value = None

    service = AuthService(repo=mock_repo)
    data = LoginRequest(email="ghost@test.com", password="whatever_the_password_is")

    with pytest.raises(HTTPException) as exc:
        service.login(data)

    assert exc.value.status_code == 401

def test_login_sets_httponly_cookie(client):
    mock_user = UserModel(
        id=1,
        name="Test User",
        email="test@example.com",
        password_hash=pwd_context.hash("secret123"),
        role="customer",
    )

    mock_db = MagicMock()

    # get_db normally opens a real PostgreSQL session via SQLAlchemy.
    # We override it here so FastAPI injects a MagicMock instead,
    # keeping this test fully in-memory with no database connection.
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    with patch("modules.auth.router.UserRepository") as MockRepo:
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = mock_user
        MockRepo.return_value = mock_repo_instance

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "secret123"}
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "access_token" in response.cookies