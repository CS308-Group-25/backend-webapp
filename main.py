from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from modules.refunds.router import admin_router as refunds_admin_router  # noqa: E402
from modules.refunds.router import router as refunds_router  # noqa: E402
from modules.reviews.router import admin_router as reviews_admin_router  # noqa: E402
from modules.reviews.router import router as reviews_router  # noqa: E402
from modules.wishlist.router import router as wishlist_router  # noqa: E402

app = FastAPI(title="SUpplements Store")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(products_router)
app.include_router(products_admin_router)
app.include_router(orders_admin_router)
app.include_router(categories_router)
app.include_router(orders_router)
app.include_router(invoices_router)
app.include_router(reviews_router)
app.include_router(reviews_admin_router)
app.include_router(refunds_router)
app.include_router(refunds_admin_router)
app.include_router(wishlist_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
