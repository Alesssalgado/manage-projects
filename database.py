from sqlalchemy  import create_engine
from sqlalchemy.orm import  sessionmaker
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






