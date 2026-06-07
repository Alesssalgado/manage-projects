
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import UserRole
import app.crud_postgresql as crud
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import TokenData
from app.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bearer_scheme = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _require_project_access(project_id: int, current_user: TokenData, db: Session):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    link = crud.get_project_user(db, project_id, current_user.id_user)
    if not link:
        raise HTTPException(status_code=403, detail="You do not have access to this project")
    return project, link


def _require_owner(link, action: str = "administrator"):
    if link.TypeUser != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail=f"Only the project owner(admin) can {action}.",
        )
    

def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(id_user=int(payload["sub"]), username=payload["username"])
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired")
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid token.")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    return decode_access_token(credentials.credentials)