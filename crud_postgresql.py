import os
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from models import Document, Project, ProjectUser, User, UserRole

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


# ──────────────────────────────────────────────
# Users
# ──────────────────────────────────────────────

def get_user(db: Session, id_user: int) -> Optional[User]:
    return db.query(User).filter(User.id_user == id_user).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str) -> User:
    hashed = hash_password(password)
    user = User(username=username, password=hashed)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Username '{username}' is already taken.")
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user


# ──────────────────────────────────────────────
# Projects
# ──────────────────────────────────────────────

def create_project(db: Session, name: str, description: Optional[str], owner_id: int) -> Project:
    try:
        project = Project(name=name, description=description)
        db.add(project)
        db.flush()

        link = ProjectUser(
            id_project1=project.id_project,
            id_user1=owner_id,
            TypeUser=UserRole.admin,
        )
        db.add(link)
        db.commit()
        db.refresh(project)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_projects_for_user(db: Session, user_id: int) -> list[Project]:
    """Return all projects the user has access to, with documents eager-loaded."""
    project_ids = (
        db.query(ProjectUser.id_project1)
        .filter(ProjectUser.id_user1 == user_id)
        .scalar_subquery()
    )
    return (
        db.query(Project)
        .options(joinedload(Project.documents))
        .filter(Project.id_project.in_(project_ids))
        .all()
    )


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return (
        db.query(Project)
        .options(joinedload(Project.documents))
        .filter(Project.id_project == project_id)
        .first()
    )


def get_project_user(db: Session, project_id: int, user_id: int) -> Optional[ProjectUser]:
    return (
        db.query(ProjectUser)
        .filter(
            ProjectUser.id_project1 == project_id,
            ProjectUser.id_user1 == user_id,
        )
        .first()
    )


def update_project(
    db: Session,
    project: Project,
    name: Optional[str],
    description: Optional[str],
) -> Project:
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    # Remove all stored files for this project's documents
    for doc in project.documents:
        _delete_file(doc.filepath)
    db.delete(project)
    db.commit()


def invite_user_to_project(
    db: Session,
    project_id: int,
    user_id: int,
    role: UserRole = UserRole.participant,
) -> ProjectUser:
    existing = get_project_user(db, project_id, user_id)
    if existing:
        raise ValueError("User already has access to this project.")
    link = ProjectUser(id_project1=project_id, id_user1=user_id, TypeUser=role)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


# ──────────────────────────────────────────────
# Documents
# ──────────────────────────────────────────────

def _delete_file(filepath: str) -> None:
    try:
        Path(filepath).unlink(missing_ok=True)
    except Exception:
        pass


def create_document(
    db: Session,
    project_id: int,
    name: str,
    upload_file: UploadFile,
) -> Document:
    # Build a unique filename so collisions don't overwrite each other
    suffix = Path(upload_file.filename).suffix if upload_file.filename else ""
    import uuid
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    filepath = UPLOAD_DIR / stored_name

    with filepath.open("wb") as buf:
        shutil.copyfileobj(upload_file.file, buf)

    doc = Document(
        name=name,
        #filename=upload_file.filename or stored_name,
        filepath=str(filepath),
        id_project2=project_id,
    )
    db.add(doc)
    try:
        db.commit()
        db.refresh(doc)
    except SQLAlchemyError as e:
        db.rollback()
        _delete_file(str(filepath))
        raise e
    return doc


def get_document(db: Session, document_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id_document == document_id).first()


def get_documents_for_project(db: Session, project_id: int) -> list[Document]:
    return db.query(Document).filter(Document.id_project2 == project_id).all()


def update_document(
    db: Session,
    doc: Document,
    name: Optional[str],
    upload_file: Optional[UploadFile],
) -> Document:
    if name is not None:
        doc.name = name
    if upload_file is not None:
        _delete_file(doc.filepath)
        suffix = Path(upload_file.filename).suffix if upload_file.filename else ""
        import uuid
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        filepath = UPLOAD_DIR / stored_name
        with filepath.open("wb") as buf:
            shutil.copyfileobj(upload_file.file, buf)
        doc.filename = upload_file.filename or stored_name
        doc.filepath = str(filepath)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: Document) -> None:
    _delete_file(doc.filepath)
    db.delete(doc)
    db.commit()