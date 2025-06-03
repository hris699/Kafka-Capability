from sqlalchemy.orm import sessionmaker
from app.models.order import Base
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1:3306/order_db"
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print("Error creating engine:", e)
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
