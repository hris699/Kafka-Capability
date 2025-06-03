from sqlalchemy.orm import sessionmaker
from app.models.order import Base
from sqlalchemy import create_engine

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:3306/order_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
