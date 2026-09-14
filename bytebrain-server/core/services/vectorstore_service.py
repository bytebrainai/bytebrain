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

from typing import List, Dict, Optional
from uuid import UUID

from langchain.schema import Document
from langchain.vectorstores import VectorStore

from core.docs.document_loader import generate_uuid
from core.utils.utils import create_dict_from_keys_and_values
from core.utils.utils import identify_changed_files


class VectorStoreService:
    def __init__(self, weaviate: VectorStore, weaviate_client, embedder, index_name, text_key):
        self.weaviate = weaviate
        self.embedder = embedder
        self.weaviate_client = weaviate_client
        self.index_name = index_name
        self.text_key = text_key

    def delete_docs(self, ids: List[UUID]):
        # TODO: use batch operations like delete_objects if possible!
        # self.weaviate_client.batch.delete_objects('Zio', where=???)
        for id in ids:
            if self.weaviate_client.data_object.exists(id, class_name=self.index_name):
                self.weaviate_client.data_object.delete(id, class_name=self.index_name)

    def index_docs(self, uuids: List[UUID], docs: List[Document]):
        # self.weaviate_client.schema.add_class_tenants(class_name=self.index_name, tenants=[Tenant(tenant)])
        self.weaviate.from_documents(
            documents=docs,
            embedding=self.embedder,
            index_name=self.index_name,
            text_key=self.text_key,
            uuids=uuids,
        )

    @staticmethod
    def map_metadata_to_paths(metadata: List[Dict[any, any]]) -> List[str]:
        return [m['doc_path'] for m in metadata]

    @staticmethod
    def map_metadata_to_hashes(metadata: List[Dict[any, any]]) -> List[str]:
        return [d['doc_hash'] for d in metadata]

    def upsert_docs(self, ids: List[UUID], docs: List[Document], old_metadata_list: List[Dict[any, any]]):
        assert (len(ids) == len(docs))

        doc_source_type = docs[0].metadata['doc_source_type']
        doc_source_id = docs[0].metadata['doc_source_id']

        metadata_list: list[dict] = [d.metadata for d in docs]
        new_paths: List[str] = self.map_metadata_to_paths(metadata_list)
        new_hashes: List[str] = self.map_metadata_to_hashes(metadata_list)
        new_file_path_to_docs: Dict[str, list[Document]] = create_dict_from_keys_and_values(new_paths, docs)
        new_file_path_to_hash: Dict[str, List[str]] = create_dict_from_keys_and_values(new_paths, new_hashes)
        if old_metadata_list is None:
            return self.index_docs(ids, docs)
        old_paths: List[str] = self.map_metadata_to_paths(old_metadata_list)
        old_hashes: List[str] = self.map_metadata_to_hashes(old_metadata_list)
        old_file_path_to_hash: Dict[str, List[str]] = create_dict_from_keys_and_values(old_paths, old_hashes)

        changed_files_paths: List[str] = identify_changed_files(
            old_file_path_to_hash,
            new_file_path_to_hash
        )

        changed_docs_ids: List[UUID] = []
        changed_docs: List[Document] = []
        for file_path in changed_files_paths:
            if file_path in new_file_path_to_docs:
                for d in new_file_path_to_docs[file_path]:
                    changed_docs.append(d)
                    changed_docs_ids.append(d.metadata['doc_uuid'])
        from core.utils.utils import identify_removed_snippets
        removed_files: List[str] = list(
            set(
                identify_removed_snippets(
                    old_file_path_to_hash, new_file_path_to_hash
                ) + changed_files_paths
            )
        )
        removed_docs_ids: List[UUID] = []
        for file_path in removed_files:
            if file_path in old_file_path_to_hash:
                for h in old_file_path_to_hash[file_path]:
                    removed_docs_ids.append(
                        generate_uuid(doc_source_type, doc_source_type, doc_source_id, file_path, h)
                    )

        if len(removed_docs_ids) != 0:
            self.delete_docs(removed_docs_ids)

        assert (len(changed_docs) == len(changed_docs))

        if len(changed_docs_ids) != 0:
            self.index_docs(changed_docs_ids, changed_docs)
