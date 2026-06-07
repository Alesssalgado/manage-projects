from typing import Optional
from pathlib import Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user
from database import engine
from models import Base,  UserRole
import crud_postgresql as crud
from .routers import users

from fastapi import (
    Depends, FastAPI, File, Form, HTTPException, Query,
    UploadFile, status,
)

from schemas import (
    ProjectCreate, ProjectOut, ProjectUpdate,
    Token, TokenData,
    UserCreate, UserLogin, UserOut,
)

from dependecies import(
    _require_project_access,
    get_db,
    _require_owner,
    get_current_user,

)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management")

app.include_router(users.router)

@app.post(
    "/projects",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project"],
    summary="Create a project",
)
async def create_project(
    data: ProjectCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = crud.create_project(db, data.name, data.description, current_user.id_user)
    return project


@app.get(
    "/projects",
    response_model=list[ProjectOut],
    tags=["Project"],
    summary="List all projects",
)
async def list_projects(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_projects_for_user(db, current_user.id_user)


@app.get(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    tags=["Project"],
    summary="Get project details",
)
async def get_project_info(
    project_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, _ = _require_project_access(project_id, current_user, db)
    return project


@app.put(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    tags=["Project"],
    summary="Update project name/description",
)
async def update_project_info(
    project_id: int,
    data: ProjectUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, _ = _require_project_access(project_id, current_user, db)
    if data.name is None and data.description is None:
        raise HTTPException(status_code=422, detail="Provide at least one field to update.")
    project = crud.update_project(db, project, data.name, data.description)
    return project


@app.delete(
    "/project/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project"],
    summary="Delete a project",
)
async def delete_project(
    project_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, link = _require_project_access(project_id, current_user, db)
    _require_owner(link, "delete this project")
    crud.delete_project(db, project)


@app.post(
    "/project/{project_id}/invite",
    status_code=status.HTTP_200_OK,
    tags=["Project"],
    summary="Invite a user to the project",
)
async def invite_user(
    project_id: int,
    user: str = Query(..., description="Username of the user to invite"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _, link = _require_project_access(project_id, current_user, db)
    _require_owner(link, "invite users")

    target = crud.get_user_by_username(db, user)
    if not target:
        raise HTTPException(status_code=404, detail=f"User '{user}' not found.")

    try:
        crud.invite_user_to_project(db, project_id, target.id_user, UserRole.participant)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "message": f"User '{user}' now participant access to project {project_id}."
    }


@app.get(
    "/project/{project_id}/documents",
    response_model=list[DocumentOut],
    tags=["Document"],
    summary="List all documents in a project",
)
async def list_documents(
    project_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_project_access(project_id, current_user, db)
    return crud.get_documents_for_project(db, project_id)


@app.post(
    "/project/{project_id}/documents",
    response_model=list[DocumentOut],
    status_code=status.HTTP_201_CREATED,
    tags=["Document"],
    summary="Upload one or more documents to a project",
)
async def upload_documents(
    project_id: int,
    files: list[UploadFile] = File(..., description="One or more files to upload"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    _require_project_access(project_id, current_user, db)
    created = []

    for upload in files:
        file_ext = Path(upload.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Don't support: {file_ext}. Only allow PDF and DOCX"
            )
        
        doc_name = upload.filename if upload.filename else "untitled"
        doc = crud.create_document(db, project_id, doc_name, upload)
        created.append(doc)
    
    return created


@app.get(
    "/document/{document_id}",
    tags=["Document"],
    summary="Download a document",
)
async def download_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    _require_project_access(doc.id_project2, current_user, db)

    filepath = Path(doc.filepath)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found on server.")

    return FileResponse(
        path=str(filepath),
        filename=doc.filename,
        media_type="application/octet-stream",
    )


@app.put(
    "/document/{document_id}",
    response_model=DocumentOut,
    tags=["Document"],
    summary="Update document",
)
async def update_document(
    document_id: int,
    name: Optional[str] = Form(None, description="New name for the document"),
    file: Optional[UploadFile] = File(None, description="Replacement file (optional)"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    _require_project_access(doc.id_project2, current_user, db)

    if name is None and file is None:
        raise HTTPException(status_code=422, detail="Provide a new name and/or a replacement file.")

    if name is not None:
        name = name.strip()
        if not name:
            raise HTTPException(status_code=422, detail="Document name  not be empty.")

    doc = crud.update_document(db, doc, name, file)
    return doc


@app.delete(
    "/document/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Document"],
    summary="Delete a document (admin only)",
)
async def delete_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    _, link = _require_project_access(doc.id_project2, current_user, db)
    _require_owner(link, "delete documents")
    crud.delete_document(db, doc)