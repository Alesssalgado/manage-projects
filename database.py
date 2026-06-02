import os
from sqlalchemy  import (String, Boolean, ForeignKey, DateTime,
                         create_engine, Text,)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
relationship, sessionmaker,)
from sqlalchemy.sql.ddl import CreateTable
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from config import settings
from sqlalchemy.ext.declarative import declarative_base






DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


#Base.metadata.create_all(engine)

#print(CreateTable(User.__table__).compile(engine))


#user = User(username="Fabio", password="fabio_password")

#session.add(user)
#session.commit()
#session.close()






