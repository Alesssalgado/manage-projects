from typing import Optional
from pathlib import Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import app.crud_postgresql as crud
from app.schemas import DocumentOut, TokenData

from fastapi import (
    Depends, APIRouter, File, Form, HTTPException,
    UploadFile, status,
)

from app.dependecies import (
    _require_project_access,
    get_db,
    _require_owner,
    get_current_user,

)

router = APIRouter(
    tags=["documents"]
)

@router.get(
    "/project/{project_id}/documents",
    response_model=list[DocumentOut],
    summary="List all documents in a project",
)
async def list_documents(
    project_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_project_access(project_id, current_user, db)
    return crud.get_documents_for_project(db, project_id)


@router.post(
    "/project/{project_id}/documents",
    response_model=list[DocumentOut],
    status_code=status.HTTP_201_CREATED,
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


@router.get(
    "/document/{document_id}",
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
        filename=doc.name,
        media_type="application/octet-stream",
    )


@router.put(
    "/document/{document_id}",
    response_model=DocumentOut,
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


@router.delete(
    "/document/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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