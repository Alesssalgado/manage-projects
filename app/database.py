from sqlalchemy  import create_engine
from sqlalchemy.orm import  sessionmaker
from app.config import settings
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()







