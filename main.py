from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

import core.models  # noqa: E402, F401
from modules.auth.router import router as auth_router  # noqa: E402
from modules.cart.router import router as cart_router  # noqa: E402

app = FastAPI(title="SUpplements Store")
app.include_router(auth_router)
app.include_router(cart_router)

from modules.products.router import router as products_router

app.include_router(products_router, prefix="/api/v1/admin")


@app.get("/")
def health_check():
    return {"status": "ok"}
