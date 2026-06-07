from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator


class UserCreate(BaseModel):
    username: str
    password: str
    repeat_password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, username: str) -> str:
        value = username.strip()
        if not value:
            raise ValueError("Username must not be empty.")
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters.")
        return value

    """
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Password must be at least 3 characters.")
        return v
    """
    @field_validator("password")
    @classmethod
    def password_strength(cls, password: str) -> str:
        if len(password) < 3:
            raise ValueError("Password must be at least 3 characters.")
        return password

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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id_user: int
    username: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, name: str) -> str:
        value = name.strip()
        if not value:
            raise ValueError("Project name not be empty")
        return value


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            value = name.strip()
            if not value:
                raise ValueError("Project name not be empty.")
        return value


class DocumentOut(BaseModel):
    id_document: int
    name: str
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


class DocumentCreate(BaseModel):
    name: str
    id_project2: int

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, name: str) -> str:
        value = name.strip()
        if not value:
            raise ValueError("Document name must not be empty.")
        return value


class DocumentUpdate(BaseModel):
    name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            value = name.strip()
            if not value:
                raise ValueError("Document name not be empty.")
        return value