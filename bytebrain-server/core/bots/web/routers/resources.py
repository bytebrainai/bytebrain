from enum import Enum

from fastapi import APIRouter
from pydantic.main import BaseModel
from starlette.responses import JSONResponse

from core.bots.web.auth import *
from core.bots.web.dependencies import project_service, resource_service
from core.dao.user_dao import User
from core.services.project_service import ProjectService
from core.services.resource_service import ResourceService

resources_router = router = APIRouter()


class WebsiteResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


# TODO: use resource_type instead of separate apis for each resource
@router.post("/resources/website", tags=["Resources"])
async def submit_new_website_resource(resource: WebsiteResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)],
                                      project_service: Annotated[ProjectService, Depends(project_service)],
                                      resource_service: Annotated[ResourceService, Depends(resource_service)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.user_id == current_user.id:
            resource_id = resource_service.submit_website_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class WebpageResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


@router.post("/resources/webpage", tags=["Resources"])
async def submit_new_webpage_resource(resource: WebpageResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)],
                                      project_service: Annotated[ProjectService, Depends(project_service)],
                                      resource_service: Annotated[ResourceService, Depends(resource_service)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.user_id == current_user.id:
            resource_id = resource_service.submit_webpage_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class YoutubeResourceRequest(BaseModel):
    name: str
    url: str
    project_id: str


@router.post("/resources/youtube", tags=["Resources"])
async def submit_new_youtube_resource(resource: YoutubeResourceRequest,
                                      current_user: Annotated[User, Depends(get_current_active_user)],
                                      project_service: Annotated[ProjectService, Depends(project_service)],
                                      resource_service: Annotated[ResourceService, Depends(resource_service)]):
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.user_id == current_user.id:
            resource_id = resource_service.submit_youtube_resource(resource.name, resource.url, resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to the specified project!"
            )
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class Language(str, Enum):
    CPP = "cpp"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    JS = "js"
    TS = "ts"
    PHP = "php"
    PROTO = "proto"
    PYTHON = "python"
    RST = "rst"
    RUBY = "ruby"
    RUST = "rust"
    SCALA = "scala"
    SWIFT = "swift"
    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"
    SOL = "sol"
    CSHARP = "csharp"


class GithubResourceRequest(BaseModel):
    name: str
    language: Language
    clone_url: str
    paths: Optional[str]
    branch: str = "main"
    project_id: str


@router.post("/resources/github", tags=["Resources"])
async def submit_new_github_resource(resource: GithubResourceRequest,
                                     current_user: Annotated[User, Depends(get_current_active_user)],
                                     project_service: Annotated[ProjectService, Depends(project_service)],
                                     resource_service: Annotated[ResourceService, Depends(resource_service)]):
    paths = resource.paths if resource.paths is not None else "*"
    project = project_service.get_project_by_id(resource.project_id)
    if project is not None:
        if project.user_id == current_user.id:
            resource_id = resource_service.submit_github_resource(resource.name,
                                                                  resource.language.value,
                                                                  resource.clone_url,
                                                                  paths,
                                                                  resource.branch,
                                                                  resource.project_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add resource to specified project!"
            )
    else:
        return JSONResponse({"message": "This project_id does not exist!", "project_id": resource.project_id},
                            status_code=404)
    if resource_id:
        return JSONResponse({"resource_id": resource_id, "status": "pending"}, status_code=202)
    else:
        return JSONResponse({"message": "This resource is already submitted"}, status_code=409)


class UpdateRequest(BaseModel):
    request_id: str


@router.put("/resources/{resource_id}", tags=["Resources"])
async def update_resource(
        resource_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        project_service: Annotated[ProjectService, Depends(project_service)],
        resource_service: Annotated[ResourceService, Depends(resource_service)]):
    resource = resource_service.get_resource_by_id(resource_id)
    project = project_service.get_project_by_id(resource.project_id)
    if project.user_id == current_user.id:
        if resource_service.submit_resource_update(resource_id):
            return JSONResponse({
                "resource_id": resource_id,
                "message": "The update request has been submitted successfully."
            })
        else:
            return JSONResponse({
                "resource_id": resource_id,
                "message": f"Update request is forbidden. Last update was less than 24 hours ago."
            }, status_code=403)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to update this resource!"
        )


@router.delete("/resources/{resource_id}", status_code=204, tags=["Resources"])
async def delete_resource(resource_id: str,
                          current_user: Annotated[User, Depends(get_current_active_user)],
                          project_service: Annotated[ProjectService, Depends(project_service)],
                          resource_service: Annotated[ResourceService, Depends(resource_service)]):
    resource = resource_service.get_resource_by_id(resource_id)
    if resource is not None:
        project = project_service.get_project_by_id(resource.project_id)
        if project is not None:
            if project.user_id == current_user.id:
                resource_service.delete_resource(resource_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to delete the resource!"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found!"
        )
