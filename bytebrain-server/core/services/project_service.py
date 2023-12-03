from typing import Optional, List

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

    def delete_project(self, project_id: str):
        self.resource_service.delete_resources_by_project_id(project_id)
        self.project_dao.delete_project(project_id)

    def create_project(self, name: str) -> Project:
        project = Project.create(name)
        self.project_dao.create_project(project)
        return project

    def get_all_projects(self) -> list[Project]:
        projects = self.project_dao.get_all_projects()

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
