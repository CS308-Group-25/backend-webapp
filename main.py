from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI(title="CS308 Online Store")

@app.get("/")
def health_check():
    return {"status": "ok"}