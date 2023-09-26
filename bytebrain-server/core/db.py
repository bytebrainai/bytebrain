from typing import List, Dict, Optional
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.schema import Document

from core.utils import create_dict_from_keys_and_values, identify_changed_files, identify_removed_snippets


def map_ids_to_paths(ids: List[str]) -> List[str]:
    return [id.split(':')[2] for id in ids]


def map_ids_to_hashes(ids: List[str]) -> List[str]:
    return [id.split(':')[3] for id in ids]


def get_original_ids(db_dir: str, docs_type: str, source_identifier: str) -> List[str]:
    import sqlite3
    con = sqlite3.connect(db_dir + "/chroma.sqlite3")
    cur = con.cursor()
    sql_query = f"""
      SELECT embedding_id
      FROM embeddings e 
      WHERE embedding_id LIKE '{docs_type}:{source_identifier}:%'
      ORDER BY id Desc 
      """
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        return [item[0] for item in result]
    except sqlite3.Error as e:
        print("sqlite error: ", e)


def delete_docs(ids: List[str], db_dir: str):
    from langchain.vectorstores import Chroma
    chroma = Chroma(persist_directory=db_dir)
    chroma.delete(ids)


def index_docs(ids: List[str], docs: List[Document], db_dir: str):
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import Chroma

    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(
        ids=ids,
        documents=docs,
        embedding=embeddings,
        persist_directory=db_dir
    )


def update_db(ids: List[str], texts: list[Document], db_dir: str):
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(texts, embeddings, ids=ids, persist_directory=db_dir)


def upsert_docs(ids: List[str], docs: List[Document], db_dir: str):
    assert (len(ids) == len(docs))
    parts = ids[0].split(':')
    doc_type = parts[0]
    source_identifier = parts[1]

    new_paths: List[str] = map_ids_to_paths(ids)
    new_hashes: List[str] = map_ids_to_hashes(ids)
    new_file_path_to_docs: Dict[str, list[Document]] = create_dict_from_keys_and_values(new_paths, docs)
    new_file_path_to_hash: Dict[str, List[str]] = create_dict_from_keys_and_values(new_paths, new_hashes)

    old_doc_ids: List[str] = get_original_ids(db_dir, doc_type, source_identifier)
    old_paths: List[str] = map_ids_to_paths(old_doc_ids)
    old_hashes: List[str] = map_ids_to_hashes(old_doc_ids)
    old_file_path_to_hash: Dict[str, List[str]] = create_dict_from_keys_and_values(old_paths, old_hashes)

    changed_files_paths: List[str] = identify_changed_files(
        old_file_path_to_hash,
        new_file_path_to_hash
    )

    changed_docs_ids: List[str] = []
    changed_docs: List[Document] = []
    for file_path in changed_files_paths:
        if file_path in new_file_path_to_docs:
            for d in new_file_path_to_docs[file_path]:
                changed_docs.append(d)
            for h in new_file_path_to_hash[file_path]:
                changed_docs_ids.append(doc_type + ':' + source_identifier + ':' + file_path + ':' + h)

    removed_files: List[str] = list(
        set(
            identify_removed_snippets(
                old_file_path_to_hash, new_file_path_to_hash
            ) + changed_files_paths
        )
    )
    removed_docs_ids: List[str] = []
    for file_path in removed_files:
        if file_path in old_file_path_to_hash:
            for h in old_file_path_to_hash[file_path]:
                removed_docs_ids.append(doc_type + ':' + source_identifier + ':' + file_path + ':' + h)

    if len(removed_docs_ids) != 0:
        delete_docs(removed_docs_ids, db_dir)

    assert (len(changed_docs) == len(changed_docs))

    if len(changed_docs_ids) != 0:
        index_docs(changed_docs_ids, changed_docs, db_dir)
