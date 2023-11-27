import json
import sqlite3
import threading
import uuid
from enum import Enum
from typing import Optional, List

from pydantic.main import BaseModel
from structlog import getLogger

from core.docs.db.vectorstore_service import VectorStoreService
from core.docs.document_loader import load_docs_from_site, load_docs_from_webpage, load_youtube_docs, \
    load_sourcecode_from_git_repo
from core.docs.metadata_service import DocumentMetadataService

log = getLogger()


class ResourceType(str, Enum):
    Website = 'website'
    Webpage = 'webpage'
    Youtube = 'youtube'
    GitHub = "github"


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
    WEBPAGE_ID_NAMESPACE = uuid.UUID('a715a944-5eab-4293-9de5-d5c7989eb1fc')
    YOUTUBE_ID_NAMESPACE = uuid.UUID('05980ffd-3506-4b2d-af0c-7c0afdbfe57e')
    GITHUB_ID_NAMESPACE = uuid.UUID('b734ee40-169b-4c9e-9dd0-6bede6e6dfa3')

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

    def submit_website_resource(self, name: str, url: str) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.WEBSITE_ID_NAMESPACE, name=url))
        if self.get_by_id(resource_id):
            return None
        else:
            self._add_resource(
                Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Website,
                         metadata={"url": url}))
            return resource_id

    def submit_webpage_resource(self, name: str, url: str) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.WEBPAGE_ID_NAMESPACE, name=url))
        if self.get_by_id(resource_id):
            return None
        else:
            self._add_resource(
                Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Webpage,
                         metadata={"url": url}))
            return resource_id

    def submit_youtube_resource(self, name: str, url: str) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.YOUTUBE_ID_NAMESPACE, name=url))
        if self.get_by_id(resource_id):
            return None
        else:
            self._add_resource(
                Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Youtube,
                         metadata={"url": url}))
            return resource_id

    def submit_github_resource(self,
                               name: str,
                               language: str,
                               clone_url: str,
                               filter_regex: str,
                               branch: Optional[str]) -> Optional[str]:
        resource_id = str(uuid.uuid5(self.GITHUB_ID_NAMESPACE, name=clone_url + language))
        if self.get_by_id(resource_id):
            return None
        else:
            self._add_resource(
                Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.GitHub,
                         metadata={"language": language,
                                   "clone_url": clone_url,
                                   "filter_regex": filter_regex,
                                   "branch": branch}))
            return resource_id

    def _add_resource(self, resource):
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
        self._create_daemon()

    def _get_pending_resources(self):
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
        self._set_state(resource_id, ResourceState.Loading)
        ids, docs = load_docs_from_site(doc_source_id=resource_id,
                                        doc_source_type=resource.resource_type.value,
                                        url=resource.metadata['url'])
        self._set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self._set_state(resource_id, ResourceState.Finished)

    def index_webpage(self, resource_id, name: str, url: str):
        resource = Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Webpage,
                            metadata={"url": url})
        self._set_state(resource_id, ResourceState.Loading)
        ids, docs = load_docs_from_webpage(url=resource.metadata['url'],
                                           doc_source_id=resource_id,
                                           doc_source_type=resource.resource_type.value)
        self._set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self._set_state(resource_id, ResourceState.Finished)
        print(len(docs), len(ids))

    def index_youtube(self, resource_id, name: str, url: str):
        resource = Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.Youtube,
                            metadata={"url": url})
        self._set_state(resource_id, ResourceState.Loading)
        ids, docs = load_youtube_docs(url=resource.metadata['url'],
                                      doc_source_id=resource_id,
                                      doc_source_type=resource.resource_type.value)
        self._set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self._set_state(resource_id, ResourceState.Finished)

    def index_github(self, resource_id, name: str, clone_url: str, language: str, filter_regex: str,
                     branch: Optional[str]):
        resource = Resource(resource_id=resource_id, resource_name=name, resource_type=ResourceType.GitHub,
                            metadata={"language": language, "clone_url": clone_url, "filter_regex": filter_regex,
                                      "branch": branch})
        self._set_state(resource_id, ResourceState.Loading)
        ids, docs = load_sourcecode_from_git_repo(clone_url=resource.metadata['clone_url'],
                                                  doc_source_id=resource_id,
                                                  doc_source_type=resource.resource_type.value,
                                                  language=language,
                                                  branch=branch,
                                                  regex_pattern=filter_regex)
        self._set_state(resource_id, ResourceState.Indexing)
        self.vectorstore_service.index_docs(ids, docs)
        self.metadata_service.save_docs_metadata(docs)  # TODO: do not pass docs, instead pass metadata
        self._set_state(resource_id, ResourceState.Finished)

    def _index_pending_resources(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        pending_resources = self._get_pending_resources()

        for resource_id, resource_name, resource_type, metadata, status in pending_resources:
            cursor.execute('UPDATE resources SET status=? WHERE id=?', ('running', resource_id,))
            conn.commit()

            match resource_type:
                case "gitrepo":
                    log.info(f"added git repo: {resource_name}")
                case ResourceType.Website.value:
                    self.index_website(resource_id=resource_id, name=resource_name, url=json.loads(metadata)['url'])
                    log.info(f"New website added {resource_name}")
                case ResourceType.Webpage.value:
                    self.index_webpage(resource_id=resource_id, name=resource_name, url=json.loads(metadata)['url'])
                    log.info(f"New webpage added {resource_name}")
                case ResourceType.Youtube.value:
                    self.index_youtube(resource_id=resource_id, name=resource_name, url=json.loads(metadata)['url'])
                    log.info(f"New youtube video added {resource_name}")
                case ResourceType.GitHub.value:
                    self.index_github(resource_id=resource_id,
                                      name=resource_name,
                                      clone_url=json.loads(metadata)['clone_url'],
                                      language=json.loads(metadata)['language'],
                                      filter_regex=json.loads(metadata)['filter_regex'],
                                      branch=json.loads(metadata)['branch'])
                    log.info(f"New GitHub source was added: {resource_name, json.loads(metadata)['language']}")

        conn.close()

    def _delete_resource_from_table(self, resource_id):
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
        self._delete_resource_from_table(resource_id)

    def _set_state(self, resource_id, state: ResourceState):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            query = '''
                UPDATE resources
                SET status = ?
                WHERE id = ?
            '''
            cursor.execute(query, (state.value, resource_id))

            connection.commit()
