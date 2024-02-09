# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List

from fastapi import APIRouter
from pydantic.main import BaseModel
from starlette.responses import JSONResponse

from core.bots.web.auth import *
from core.bots.web.dependencies import project_service
from core.dao.apikey_dao import ApiKey
from core.dao.project_dao import Project
from core.dao.user_dao import User
from core.services.project_service import ProjectService

projects_router = router = APIRouter()


class ProjectCreation(BaseModel):
    name: str
    description: str


@router.post("/projects/", response_model=Project, response_model_exclude_none=True, tags=["Projects"])
async def create_project(project: ProjectCreation,
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         project_service: Annotated[ProjectService, Depends(project_service)]):
    return project_service.create_project(
        name=project.name,
        user_id=current_user.id,
        description=project.description
    )


@router.delete("/projects/{project_id}", status_code=204, tags=["Projects"])
async def delete_project(
        project_id,
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    project_service.delete_project(project_id, current_user.id)


@router.delete("/projects/", status_code=204, tags=["Projects"])
async def delete_all_project(
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    project_service.delete_projects_owned_by(current_user.id)


@router.get("/projects/", response_model=list[Project], tags=["Projects"])
# TODO: exclude resources when its empty
async def get_all_projects(current_user: Annotated[User, Depends(get_current_active_user)],
                           project_service: Annotated[ProjectService, Depends(project_service)]):
    return project_service.get_all_projects(current_user.id)


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


class CreateApiKey(BaseModel):
    name: str
    allowed_domains: List[str]


@router.post("/projects/{project_id}/apikeys",
             response_model=ApiKey,
             response_model_exclude_none=True,
             tags=["Projects", "ApiKey"])
async def generate_apikey(
        project_id: str,
        apikey: CreateApiKey,
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    users_projects = project_service.get_all_projects(current_user.id)
    project_ids = [u.user_id for u in users_projects]
    if current_user.id in project_ids:
        return project_service.generate_apikey(
            project_id=project_id,
            name=apikey.name,
            allowed_domains=apikey.allowed_domains,
        )
    else:
        raise HTTPException(403, "The project does not belong to the user!")


@router.get("/projects/{project_id}/apikeys", response_model=List[ApiKey], tags=["Projects"])
async def get_apikeys(project_id: str, current_user: Annotated[User, Depends(get_current_active_user)],
                      project_service: Annotated[ProjectService, Depends(project_service)]):
    project = project_service.get_project_by_id(project_id)
    if project:
        if project.user_id == current_user.id:
            return project_service.apikey_dao.get_apikeys(project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to this project!"
            )
    else:
        return JSONResponse({"message": f"Project not found!", "project_id": project_id})


@router.delete("/projects/{project_id}/apikeys/{api_key}", status_code=204, tags=["Projects", "ApiKeys"])
async def delete_project(
        project_id,
        api_key,
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)]):
    project_service.delete_apikey(api_key, project_id, current_user.id)
