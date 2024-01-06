from typing import Optional, List

from fastapi import HTTPException
from fastapi import status

from core.dao.project_dao import ProjectDao, Project
from core.dao.resource_dao import Resource
from core.services.resource_service import ResourceService


class ProjectNotFound(Exception):
    def __init__(self, project_id):
        super().__init__(f"Project not found with ID: {project_id}")
        self.project_id = project_id


class ProjectService:
    def __init__(self, project_dao: ProjectDao, resource_service: ResourceService):
        self.project_dao = project_dao
        self.resource_service = resource_service

    def delete_projects_owned_by(self, user_id: str):
        projects_to_delete = self.project_dao.get_all_projects(user_id)
        for project in projects_to_delete:
            self.delete_project(project.id, user_id)

    def delete_project(self, project_id: str, user_id: str):
        project_to_delete = self.project_dao.get_project_by_id(project_id)
        if project_to_delete is not None:
            if project_to_delete.user_id == user_id:
                self.resource_service.delete_resources_by_project_id(project_id)
                self.project_dao.delete_project(project_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to delete the project!"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found!"
            )

    def create_project(self, name: str, user_id: str, description: str) -> Project:
        project = Project.create(name, user_id, description)
        self.project_dao.create_project(project)
        return project

    def get_all_projects(self, user_id: str) -> list[Project]:
        projects = self.project_dao.get_all_projects(user_id)

        def get_project_with_resources(project):
            project.resources = self.resource_service.get_resources_by_project_id(project.id)
            return project

        return [get_project_with_resources(p) for p in projects]

    def get_project_by_id(self, project_id) -> Optional[Project]:
        project: Optional[Project] = self.project_dao.get_project_by_id(project_id)
        if project is None:
            return None
        resources: List[Resource] = self.resource_service.get_resources_by_project_id(project_id)
        project.resources = resources

        return project
