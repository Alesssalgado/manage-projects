from fastapi import FastAPI, Depends, HTTPException
from models import Base, UserCreate
from crud_posgresql import (create_user, get_user,
                             get_user_by_username, authenticate_user,)
from sqlalchemy.orm import Session
from database import SessionLocal, engine
#from config import settings

#SECRET_KEY = settings.SECRET_KEY
#ALGORITHM = settings.ALGORITHM


app = FastAPI()



Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/user/{user_id}")
async def get_user_db(user_id: int, db: Session = (Depends(get_db))):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    #return {"message": "Hello World"}


@app.post("/auth")
async def create_user_db(
    data_user: UserCreate,
    db: Session = (Depends(get_db))):
   
   if data_user.password != data_user.password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
   
   user = create_user(db, data_user.username, data_user.password)
   return {
       "user_id": user.user_id,
       "username": user.username,
       "message": "User created successfully"
   }


@app.post("/login/")
def login(login_data: LoginRequest, db: Session = (Depends(get_db))):
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(401, "Invalid username or password")
    
    return {
        "message": "Login successful",
        "user_id": user.user_id,
        "username": user.username
    }
                  


"""
@app.get("/user/")
async def create_user(username: str, password: str, db: Session):
    return create_user(db, username, password)

"""