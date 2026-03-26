from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI(title="SUpplements Store")

@app.get("/")
def health_check():
    return {"status": "ok"}