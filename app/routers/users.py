from sqlalchemy.orm import Session
from app.auth import create_access_token
import app.crud_postgresql as crud
from app.dependecies import get_db
from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    status,
)

from app.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserOut,
)


router = APIRouter(tags=["users"])


@router.post(
    "/auth",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, data.username, data.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(user.id_user, user.username)
    return {"access_token": token, "token_type": "bearer"}
