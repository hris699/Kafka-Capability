from fastapi import FastAPI
from app.routes.routes import router
from app.db import engine
from sqlalchemy import text

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def test_db_connection():
    try:
        print("Database connection successful at startup.")
    except Exception as e:
        print("Database connection failed at startup:", e)
