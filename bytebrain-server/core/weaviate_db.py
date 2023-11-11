import os
from typing import List, Dict
from uuid import UUID

from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.storage import LocalFileStore
from langchain.vectorstores import Weaviate
from weaviate import Client

from core.document_loader import generate_uuid
from core.docs.stored_docs import get_metadata_list
from core.utils import create_dict_from_keys_and_values
from core.utils import identify_changed_files


class WeaviateDatabase:
    def __init__(self, url: str, embeddings_dir: str):
        self.index_name = "zio"
        self.text_key = "text"
        os.environ['WEAVIATE_URL'] = url
        self.embeddings_dir = embeddings_dir
        self.weaviate_client = Client(url=url)
        underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
        fs = LocalFileStore(self.embeddings_dir)
        self.cached_embedder = CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings, fs, namespace=underlying_embeddings.model
        )
        self.weaviate = Weaviate(self.weaviate_client, index_name="Zio", text_key="text", attributes=['source'],
                                 embedding=self.cached_embedder,
                                 by_text=False)

    def delete_docs(self, ids: List[UUID]):
        for id in ids:
            if self.weaviate_client.data_object.exists(id):
                self.weaviate_client.data_object.delete(id)

    def index_docs(self, uuids: List[UUID], docs: List[Document]):
        self.weaviate.from_documents(
            documents=docs,
            embedding=self.cached_embedder,
            index_name=self.index_name,
            text_key=self.text_key,
            uuids=uuids
        )

    @staticmethod
    def map_metadata_to_paths(metadata: List[Dict[any, any]]) -> List[str]:
        return [m['doc_path'] for m in metadata]

    @staticmethod
    def map_metadata_to_hashes(metadata: List[Dict[any, any]]) -> List[str]:
        return [d['doc_hash'] for d in metadata]

    def upsert_docs(self, ids: List[UUID], docs: List[Document]):
        assert (len(ids) == len(docs))

        doc_source_type = docs[0].metadata['doc_source_type']
        doc_source_id = docs[0].metadata['doc_source_id']

        metadata_list: list[dict] = [d.metadata for d in docs]
        new_paths: List[str] = self.map_metadata_to_paths(metadata_list)
        new_hashes: List[str] = self.map_metadata_to_hashes(metadata_list)
        new_file_path_to_docs: Dict[str, list[Document]] = create_dict_from_keys_and_values(new_paths, docs)
        new_file_path_to_hash: Dict[str, List[str]] = create_dict_from_keys_and_values(new_paths, new_hashes)
        old_metadata_list: List[Dict[any, any]] = get_metadata_list(doc_source_type, doc_source_id)
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
        from core.utils import identify_removed_snippets
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
