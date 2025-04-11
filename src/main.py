from fastapi import FastAPI

from src.auth.router import router as auth_router


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0"
    )
app.include_router(auth_router)

@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}
