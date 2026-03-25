from fastapi import FastAPI

app = FastAPI(title="CS308 Online Store")

@app.get("/")
def health_check():
    return {"status": "ok"}