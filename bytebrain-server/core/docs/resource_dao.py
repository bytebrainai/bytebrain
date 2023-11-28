import json
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class ResourceType(str, Enum):
    Website = 'website'
    Webpage = 'webpage'
    Youtube = 'youtube'
    GitHub = "github"


class ResourceState(str, Enum):
    Pending = 'pending'
    Loading = "loading"
    Indexing = 'indexing'
    Finished = 'finished'


class Resource(BaseModel):
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    metadata: dict
    status: ResourceState
    created_at: datetime
    last_updated_at: datetime


class ResourceDao:
    def __init__(self, resource_db):
        self.db_path = resource_db
        self._create_table()

    def add_resource(self, resource: Resource) -> Optional[str]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                INSERT OR IGNORE INTO resources (id, resource_name, resource_type, metadata, created_at, last_updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            values = (
                resource.resource_id,
                resource.resource_name,
                resource.resource_type.value,
                json.dumps(resource.metadata) if resource.metadata else None,
                resource.created_at,
                resource.last_updated_at
            )
            cursor.execute(query, values)
            connection.commit()

            if cursor.rowcount > 0:  # Check if a new row was inserted
                return resource.resource_id
            else:
                return None

    def delete_resource_from_table(self, resource_id):
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
                SET status = ?,
                    last_updated_at = (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                WHERE id = ?
            '''
            cursor.execute(query, (state.value, resource_id))

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
                resource = Resource(resource_id=row[0], resource_name=row[1], resource_type=ResourceType(row[2]),
                                    metadata=json.loads(row[3]),
                                    status=ResourceState(row[4]),
                                    created_at=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
                                    last_updated_at=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S'))
                return resource
            else:
                return None

    def _create_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = f'''
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    resource_name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    metadata JSON,
                    status TEXT DEFAULT '{ResourceState.Pending.value}',
                    created_at TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                    last_updated_at TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                )
            '''
            cursor.execute(query)
            connection.commit()

    def get_all_resources(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = '''
                SELECT * FROM resources
            '''
            cursor.execute(query)
            rows = cursor.fetchall()

            resources = []
            for row in rows:
                resource = Resource(resource_id=row[0], resource_name=row[1], resource_type=ResourceType(row[2]),
                                    metadata=json.loads(row[3]),
                                    status=ResourceState(row[4]),
                                    created_at=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
                                    last_updated_at=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S'))
                resources.append(resource)

            return resources

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
                                    metadata=json.loads(row[3]),
                                    status=ResourceState(row[4]),
                                    created_at=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S'),
                                    last_updated_at=datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S'))
                resources.append(resource)

            return resources

    def get_resource_status(self, resource_id) -> Optional[ResourceState]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = 'SELECT status FROM resources WHERE id = ?'
            cursor.execute(query, (resource_id,))
            result = cursor.fetchone()

            if result:
                return ResourceState(result[0])
            else:
                return None

    def get_pending_resources_by_id(self, resource_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT id, resource_name, resource_type, metadata, status FROM resources WHERE id=?',
            (resource_id,))
        resource = cursor.fetchall()

        conn.close()
        return resource

    def get_last_updated_at(self, resource_id: str) -> Optional[datetime]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = 'SELECT last_updated_at FROM resources WHERE id = ?'
            cursor.execute(query, (resource_id,))
            result = cursor.fetchone()

            if result:
                return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            else:
                return None

    def get_unfinished_resources(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT id, resource_name, resource_type, metadata, status FROM resources WHERE status != ?',
            (ResourceState.Finished.value,))
        unfinished_resources = cursor.fetchall()

        conn.close()
        return unfinished_resources
