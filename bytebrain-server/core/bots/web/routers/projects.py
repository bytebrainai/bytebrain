from typing import Any

from fastapi import APIRouter
from pydantic.main import BaseModel
from starlette.responses import JSONResponse

from core.bots.web.auth import *
from core.bots.web.dependencies import project_service
from core.dao.project_dao import Project
from core.dao.user_dao import User
from core.services.project_service import ProjectService

projects_router = router = APIRouter()


class ProjectCreation(BaseModel):
    name: str


@router.post("/projects/", response_model=Project, response_model_exclude_none=True, tags=["Projects"])
async def create_project(project: ProjectCreation,
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         project_service: Annotated[ProjectService, Depends(project_service)]):
    return project_service.create_project(name=project.name, user_id=current_user.id)


@router.delete("/projects/{project_id}", status_code=204, tags=["Projects"])
async def delete_project(
        project_id,
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    project_service.delete_project(project_id, current_user.email)


@router.delete("/projects/", status_code=204, tags=["Projects"])
async def delete_all_project(
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    project_service.delete_projects_owned_by(current_user.email)


@router.get("/projects/", response_model=list[Project], tags=["Projects"])
# TODO: exclude resources when its empty
async def get_all_projects(current_user: Annotated[User, Depends(get_current_active_user)],
                           project_service: Annotated[ProjectService, Depends(project_service)]) -> Any:
    return project_service.get_all_projects(current_user.email)


@router.get("/projects/{project_id}", tags=["Projects"])
async def get_project_by_id(project_id: str, current_user: Annotated[User, Depends(get_current_active_user)],
                            project_service: Annotated[ProjectService, Depends(project_service)]):
    project = project_service.get_project_by_id(project_id)
    if project.user_id == current_user.id:
        if project:
            return project
        else:
            return JSONResponse({"message": f"Project not found!", "project_id": project_id})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to this project!"
        )
