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

import uuid
from typing import Optional, List

from fastapi import HTTPException
from fastapi import status

from core.dao.apikey_dao import ApiKeyDao, ApiKey
from core.dao.project_dao import ProjectDao, Project
from core.dao.resource_dao import Resource
from core.services.resource_service import ResourceService


class ProjectNotFound(Exception):
    def __init__(self, project_id):
        super().__init__(f"Project not found with ID: {project_id}")
        self.project_id = project_id


class ProjectService:
    def __init__(self, project_dao: ProjectDao, resource_service: ResourceService, apikey_dao: ApiKeyDao):
        self.project_dao = project_dao
        self.resource_service = resource_service
        self.apikey_dao = apikey_dao

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
        if self.project_dao.get_all_projects_count() >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ByteBrain doesn't support multi-project yet!"
            )
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

    def get_project_by_apikey(self, apikey) -> Optional[Project]:
        apikey: Optional[ApiKey] = self.apikey_dao.get_apikey(apikey)
        if apikey is None:
            return None
        project: Optional[Project] = self.project_dao.get_project_by_id(apikey.project_id)
        if project is None:
            return None
        resources: List[Resource] = self.resource_service.get_resources_by_project_id(project.id)
        project.resources = resources

        return project

    def generate_apikey(self, project_id, name: str, allowed_domains: List[str]) -> Optional[ApiKey]:
        project: Optional[Project] = self.project_dao.get_project_by_id(project_id)
        if project is None:
            return None

        apikey = ApiKey(
            apikey=str(uuid.uuid4()),
            name=name,
            allowed_domains=allowed_domains,
            project_id=project_id
        )

        return self.apikey_dao.add_apikey(apikey)

    def delete_apikey(self, apikey: str, project_id: str, user_id: str):
        project = self.project_dao.get_project_by_id(project_id)
        if project.user_id == user_id:
            self.apikey_dao.delete_apikey(apikey)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to delete this apikey!"
            )

    def is_allowed(self, domain, apikey) -> bool:
        allowed_domains = self.apikey_dao.get_apikey(apikey).allowed_domains
        if not allowed_domains:
            return True
        else:
            return domain in allowed_domains
