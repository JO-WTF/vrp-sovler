from fastapi import FastAPI

from backend.api.routes import router as api_router
from backend.api.websocket import router as ws_router

app = FastAPI(title="VRP Lab")
app.include_router(api_router)
app.include_router(ws_router)
