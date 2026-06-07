
from sqlalchemy.orm import Session
from app.models import UserRole
import app.crud_postgresql as crud

from fastapi import (
    Depends, APIRouter, HTTPException, Query,
    status,
)

from app.schemas import (
    ProjectCreate, ProjectOut, ProjectUpdate,
    TokenData,
)

from app.dependecies import (
    _require_project_access,
    get_db,
    _require_owner,
    get_current_user,

)

router = APIRouter(
    tags=["projects"]
)

@router.post(
    "/projects",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
async def create_project(
    data: ProjectCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = crud.create_project(db, data.name, data.description, current_user.id_user)
    return project


@router.get(
    "/projects",
    response_model=list[ProjectOut],
    summary="List all projects",
)
async def list_projects(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_projects_for_user(db, current_user.id_user)


@router.get(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    summary="Get project details",
)
async def get_project_info(
    project_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project, _ = _require_project_access(project_id, current_user, db)
    return project


@router.put(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    summary="Update info",
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


@router.delete(
    "/project/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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


@router.post(
    "/project/{project_id}/invite",
    status_code=status.HTTP_200_OK,
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
