from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

import core.models  # noqa: E402, F401
from modules.auth.router import router as auth_router  # noqa: E402
from modules.cart.router import router as cart_router  # noqa: E402
from modules.categories.router import router as categories_router  # noqa: E402
from modules.invoices.router import router as invoices_router  # noqa: E402
from modules.orders.router import admin_router as orders_admin_router  # noqa: E402
from modules.orders.router import router as orders_router  # noqa: E402
from modules.products.router import admin_router as products_admin_router  # noqa: E402
from modules.products.router import router as products_router  # noqa: E402
from modules.wishlist.router import router as wishlist_router  # noqa: E402

app = FastAPI(title="SUpplements Store")
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(products_router)
app.include_router(products_admin_router)
app.include_router(orders_admin_router)
app.include_router(categories_router)
app.include_router(orders_router)
app.include_router(invoices_router)
app.include_router(wishlist_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
