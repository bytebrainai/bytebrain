import json
import sqlite3
from enum import Enum
from typing import Optional, List

from pydantic.main import BaseModel


class ResourceType(str, Enum):
    Website = 'website'


class ResourceState(Enum):
    Pending = 'Pending'
    Loading = "Loading"
    Indexing = 'Indexing'
    Finished = 'Finished'


class Resource(BaseModel):
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    metadata: dict = None


class ResourceService:
    def __init__(self, resources_db):
        self.db_path = resources_db
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = f'''
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    resource_name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    metadata JSON,
                    status TEXT DEFAULT '{ResourceState.Pending}'
                )
            '''
            cursor.execute(query)
            connection.commit()

    def get_by_id(self, resource_id: str):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                SELECT * FROM resources
                WHERE id = ?
            '''
            cursor.execute(query, (resource_id,))
            row = cursor.fetchone()

            if row:
                resource = Resource(
                    resource_id=row[0],
                    resource_name=row[1],
                    resource_type=ResourceType(row[2]),
                    metadata=json.loads(row[3]) if row[3] else None
                )
                return resource
            else:
                return None

    def get_resources_of_type(self, resource_type: ResourceType) -> List[Resource]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                SELECT * FROM resources WHERE resource_type = ?
            '''
            cursor.execute(query, (resource_type.value,))
            rows = cursor.fetchall()

            resources = []
            for row in rows:
                resource = Resource(resource_id=row[0], resource_name=row[1], resource_type=ResourceType(row[2]),
                                    metadata=json.loads(row[3]))
                resources.append(resource)

            return resources

    def get_resource_state(self, resource_id) -> Optional[ResourceState]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = 'SELECT status FROM resources WHERE id = ?'
            cursor.execute(query, (resource_id,))
            result = cursor.fetchone()

            if result:
                return ResourceState(result[0])
            else:
                return None

    def add_resource(self, resource):
        if not isinstance(resource.resource_type, ResourceType):
            raise ValueError("Invalid resource type")

        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = 'INSERT INTO resources (id, resource_name, resource_type, metadata) VALUES (?, ?, ?, ?)'
            values = (
                resource.resource_id,
                resource.resource_name,
                resource.resource_type.value,
                json.dumps(resource.metadata) if resource.metadata else None
            )
            cursor.execute(query, values)
            connection.commit()

    def delete_resource(self, resource_id):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            resource_query = 'DELETE FROM resources WHERE id = ?'
            resource_values = (resource_id,)
            cursor.execute(resource_query, resource_values)

            connection.commit()

    def set_state(self, resource_id, state: ResourceState):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            query = '''
                UPDATE resources
                SET status = ?
                WHERE id = ?
            '''
            cursor.execute(query, (state.value, resource_id))

            connection.commit()
