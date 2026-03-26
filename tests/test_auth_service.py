from unittest.mock import MagicMock

from modules.auth.schema import RegisterRequest
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
