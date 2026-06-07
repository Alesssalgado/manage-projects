from sqlalchemy import String, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from app.database import Base
from pydantic import BaseModel, field_validator, model_validator
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    participant = "participant"


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0))

    projects: Mapped[List["ProjectUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id_user={self.id_user!r}, username={self.username!r})"


class Project(Base):
    __tablename__ = "projects"

    id_project: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0))

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
    filepath: Mapped[str] = mapped_column(Text, nullable=False)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now().replace(second=0, microsecond=0))
    id_project2: Mapped[int] = mapped_column(ForeignKey("projects.id_project"))

    project: Mapped["Project"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"Document(id_document={self.id_document!r}, name={self.name!r})"


