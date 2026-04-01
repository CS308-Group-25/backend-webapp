# core/models.py
# Import all models here so Alembic can discover them.
# Add new models here as they are created each sprint.

import modules.categories.model  # noqa: E402, F401
import modules.products.model  # noqa: E402, F401
from modules.auth.model import User  # noqa: F401
from modules.categories.model import Category  # noqa: F401
from modules.products.model import Product  # noqa: F401
from modules.cart.model import Cart, CartItem  # noqa: F401
