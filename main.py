from dotenv import load_dotenv
from fastapi import FastAPI

from modules.auth.router import router as auth_router
from modules.cart.router import router as cart_router

load_dotenv()

app = FastAPI(title="SUpplements Store")
app.include_router(auth_router)
app.include_router(cart_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
