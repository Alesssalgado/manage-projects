from sqlalchemy.orm import Session
from models import User
from hashlib import sha1

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):

    hashed_password = sha1(password.encode()).hexdigest()
    db_users = User(username=username, password=hashed_password)
    db.add(db_users)
    db.commit()
    db.refresh(db_users)
    return db_users

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha1(plain_password.encode()).hexdigest() == hashed_password

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)

    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    return user

def get_projects():
    pass

#print(CreateTable(User.__table__).compile(engine))


#user = User(username="Fabio", password="fabio_password")
