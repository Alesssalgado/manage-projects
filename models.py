import os
from sqlalchemy import (String, Boolean, ForeignKey, DateTime,
                         create_engine, Text,)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
relationship, sessionmaker,)
from sqlalchemy.sql.ddl import CreateTable
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    projects: Mapped[List["ProjectUser"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return (
            f"User(id_user={self.id_user!r}," 
            f"username={self.username!r},"
            f"password={self.password!r},"
            f"date_at={self.date_at!r})"
        )


class UserCreate(BaseModel):
    username: str
    password: str


class Project(Base):
    __tablename__ = "projects"

    id_project: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    invite: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    users: Mapped[List["ProjectUser"]] = relationship(back_populates="project")
    documents: Mapped[List["Document"]] = relationship(back_populates="project")

    def __repr__(self) -> str:
        return (
            f"Project(id_project={self.id_project!r},"
            f"name={self.name!r},"
            f"description={self.description!r},"
            f"date_at={self.date_at!r},"
            f"invite={self.invite!r})"
        )


class ProjectUser(Base):
    __tablename__ = "project_users"

    id_project1: Mapped[int] = mapped_column(ForeignKey("projects.id_project"), primary_key=True)
    id_user1: Mapped[int] = mapped_column(ForeignKey("users.id_user"), primary_key=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return (
            f"ProjectUser(id_project1={self.id_project1!r},"
            f"id_user1={self.id_user1!r})"
        )


class Document(Base):
    __tablename__ = "documents"

    id_document: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    date_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    id_project2: Mapped[int] = mapped_column(ForeignKey("projects.id_project"))

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return (
            f"Document(id_document={self.id_document!r},"
            f"name={self.name!r},"
            f"date_at={self.date_at!r},"
            f"id_project2={self.id_project2!r})"
        )


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    invite: str | None = None


class DocumentCreate(BaseModel):
    name: str
    id_project2: int