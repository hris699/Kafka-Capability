from fastapi import FastAPI
from app.routes.routes import router
from app.db import engine

app = FastAPI()
app.include_router(router)
