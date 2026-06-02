from sqlalchemy import String, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from database import Base
from pydantic import BaseModel, field_validator, model_validator
import enum


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    participant = "participant"


# ──────────────────────────────────────────────
# SQLAlchemy ORM Models
# ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    projects: Mapped[List["ProjectUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id_user={self.id_user!r}, username={self.username!r})"


class Project(Base):
    __tablename__ = "projects"

    id_project: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    users: Mapped[List["ProjectUser"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Project(id_project={self.id_project!r}, name={self.name!r})"


class ProjectUser(Base):
    __tablename__ = "project_users"

    id_project1: Mapped[int] = mapped_column(ForeignKey("projects.id_project"), primary_key=True)
    id_user1: Mapped[int] = mapped_column(ForeignKey("users.id_user"), primary_key=True)
    TypeUser: Mapped[str] = mapped_column(
        SAEnum(UserRole, name="userrole"), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return f"ProjectUser(id_project1={self.id_project1!r}, id_user1={self.id_user1!r}, TypeUser={self.TypeUser!r})"


class Document(Base):
    __tablename__ = "documents"

    id_document: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)   # stored filename on disk
    filepath: Mapped[str] = mapped_column(Text, nullable=False)   # full path on disk
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    id_project2: Mapped[int] = mapped_column(ForeignKey("projects.id_project"))

    project: Mapped["Project"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"Document(id_document={self.id_document!r}, name={self.name!r})"


# ──────────────────────────────────────────────
# Pydantic Schemas
# ──────────────────────────────────────────────

# --- Auth ---

class UserCreate(BaseModel):
    username: str
    password: str
    repeat_password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username must not be empty.")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Password must be at least 3 characters.")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id_user: int
    username: str
    date_at: datetime

    model_config = {"from_attributes": True}


# --- Token ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id_user: int
    username: str


# --- Project ---

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name must not be empty.")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Project name must not be empty.")
        return v


class DocumentOut(BaseModel):
    id_document: int
    name: str
    filename: str
    date_at: datetime
    id_project2: int

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id_project: int
    name: str
    description: Optional[str]
    date_at: datetime
    documents: List[DocumentOut] = []

    model_config = {"from_attributes": True}


# --- Document ---

class DocumentCreate(BaseModel):
    name: str
    id_project2: int

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Document name must not be empty.")
        return v


class DocumentUpdate(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Document name must not be empty.")
        return v