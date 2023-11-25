import json
import sqlite3
import threading
import time
import uuid
from enum import Enum
from typing import Optional, List

from pydantic.main import BaseModel
from structlog import getLogger

from core.docs.db.vectorstore_service import VectorStoreService
from core.docs.document_loader import load_docs_from_site
from core.docs.metadata_service import DocumentMetadataService

log = getLogger()


class ResourceType(str, Enum):
    Website = 'website'


class ResourceState(Enum):
    Pending = 'pending'
    Loading = "loading"
    Indexing = 'indexing'
    Finished = 'finished'


class Resource(BaseModel):
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    metadata: dict = None


class ResourceService:
    WEBSITE_ID_NAMESPACE = uuid.UUID('f6eea9d5-8b70-11ee-b7b1-6c02e09469ba')

    def __init__(self, resources_db, vectorstore_service: VectorStoreService,
                 metadata_service: DocumentMetadataService):
        self.db_path = resources_db
        self.vectorstore_service = vectorstore_service
        self.metadata_service = metadata_service
        self._create_table()
        self._create_daemon()

    def _create_daemon(self):
        background_thread = threading.Thread(target=self._index_pending_resources, daemon=True)
        background_thread.start()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            query = f'''
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    resource_name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    metadata JSON,
                    status TEXT DEFAULT '{ResourceState.Pending.value}'
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

    def submit_website_index(self, name: str, url: str) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.WEBSITE_ID_NAMESPACE, name=url))
        if self.get_by_id(resource_id):
            return None
        else:
            self.add_resource(
                Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Website,
                         metadata={"url": url}))
            return resource_id

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

    def get_pending_resources(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT id, resource_name, resource_type, metadata, status FROM resources WHERE status=?',
            ('pending',))
        pending_jobs = cursor.fetchall()

        conn.close()
        return pending_jobs

    def index_website(self, resource_id, name: str, url: str):
        resource = Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Website,
                            metadata={"url": url})
        # self.add_resource(resource)
        self.set_state(resource_id, ResourceState.Loading)
        ids, docs = load_docs_from_site(doc_source_id=resource_id,
                                        doc_source_type=resource.resource_type.value,
                                        url=resource.metadata['url'])
        self.set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self.set_state(resource_id, ResourceState.Finished)

    def _index_pending_resources(self):
        while True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            pending_resources = self.get_pending_resources()

            for resource_id, resource_name, resource_type, metadata, status in pending_resources:
                cursor.execute('UPDATE resources SET status=? WHERE id=?', ('running', resource_id,))
                conn.commit()

                match resource_type:
                    case "gitrepo":
                        log.info(f"added git repo: {resource_name}")
                    case "website":
                        print(resource_id, resource_name, json.loads(metadata)['url'])
                        self.index_website(resource_id=resource_id, name=resource_name, url=json.loads(metadata)['url'])
                        log.info(f"New website added {resource_name}")

            conn.close()
            time.sleep(2)

    def delete_resource_from_table(self, resource_id):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            resource_query = 'DELETE FROM resources WHERE id = ?'
            resource_values = (resource_id,)
            cursor.execute(resource_query, resource_values)

            connection.commit()

    def delete_resource(self, resource_id: str):
        ids = self.metadata_service.get_docs_ids_by_source_id(resource_id)
        self.vectorstore_service.delete_docs(ids)
        self.metadata_service.delete_docs_by_resource_id(resource_id)
        self.delete_resource_from_table(resource_id)

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
