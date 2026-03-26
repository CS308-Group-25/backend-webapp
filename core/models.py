# core/models.py
# Import all models here so Alembic can discover them.
# Add new models here as they are created each sprint.

from modules.auth.model import User  # noqa: F401
from modules.cart.model import Cart, CartItem  # noqa: F401
