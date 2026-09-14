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

import sqlite3
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.dao.resource_dao import Resource


class Project(BaseModel):
    id: str
    name: str
    user_id: str
    resources: Optional[list[Resource]] = None  # TODO: we can use simple type: list[Resource]
    created_at: datetime
    description: str

    @classmethod
    def create(cls, name: str, user_id: str, description: str):
        # Use uuid4 to generate a random UUID
        return cls(id=str(uuid.uuid4()),
                   name=name,
                   user_id=user_id,
                   created_at=datetime.now().replace(microsecond=0),
                   description=description)


class ProjectDao:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    description TEXT
                )
            ''')
            conn.commit()

    def create_project(self, project: Project):  # TODO: rename to save_project
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (id, name, user_id, description)
                VALUES (?, ?, ?, ?)
            ''', (project.id, project.name, project.user_id, project.description))
            conn.commit()

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, user_id, created_at, description FROM projects WHERE id = ?
            ''', (project_id,))
            result = cursor.fetchone()

            if result:
                return Project(id=result[0], name=result[1], user_id=result[2],
                               created_at=datetime.strptime(result[3], '%Y-%m-%d %H:%M:%S'),
                               description=result[4])
            else:
                return None

    def get_all_projects(self, user_id: str) -> list[Project]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, user_id, created_at, description FROM projects
                    WHERE user_id = ?
            ''', (user_id,))
            results = cursor.fetchall()

            return [Project(id=result[0], name=result[1], user_id=result[2],
                            created_at=datetime.strptime(result[3], '%Y-%m-%d %H:%M:%S'),
                            description=result[4]) for result in results]

    def get_all_projects_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM projects
            ''')
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 0

    def update_project(self, project: Project):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects SET name = ? WHERE id = ?
            ''', (project.name, project.id))
            conn.commit()

    def delete_project(self, project_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM projects WHERE id = ?
            ''', (project_id,))
            conn.commit()
