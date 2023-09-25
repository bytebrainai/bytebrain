import hashlib
from typing import Optional, List, Dict

from langchain.document_loaders import GitLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language


def calculate_md5_checksum(text):
    data = text.encode('utf-8')
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    md5_checksum = md5_hash.hexdigest()
    return md5_checksum


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


def identify_removed_snippets(
        old: Dict[str, List[str]],
        new: Dict[str, List[str]]
) -> List[str]:
    removed_files: List[str] = []
    for file_path, hashes in old.items():
        if file_path not in new:
            removed_files.append(file_path)
    return removed_files


def identify_changed_files(
        original: Dict[str, List[str]],
        new: Dict[str, List[str]]) -> List[str]:
    changed_files: List[str] = []
    for file_path, hashes in new.items():
        if file_path not in original:
            changed_files.append(file_path)
        else:
            original_hashes = original[file_path]
            if len(hashes) != len(original_hashes):
                changed_files.append(file_path)
            elif set(hashes) != set(original_hashes):
                changed_files.append(file_path)
    return changed_files


def load_source_code(
        repo_path: str,
        branch: Optional[str],
        source_identifier: str
) -> (List[str], List[Document]):
    loader = GitLoader(
        repo_path=repo_path,
        branch=branch,
        file_filter=lambda file_path: file_path.endswith(".scala")
    )
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.SCALA)

    snippets = splitter.transform_documents(docs)

    ids: List[str] = []
    for snippet in snippets:
        path = snippet.metadata['file_path']
        hash = calculate_md5_checksum(snippet.page_content)
        id = f"source_code:{source_identifier}:{path}:{hash}"
        ids.append(id)

    assert (len(ids) == len(snippets))
    return ids, snippets


def load_saved_ids():
    with open("ids.txt", "r") as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]
    return lines


def delete_docs(ids: List[str]):
    from langchain.vectorstores import Chroma
    chroma = Chroma(persist_directory="./mynewdb")
    chroma.delete(ids)


def index_docs(ids: List[str], docs: List[Document]):
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import Chroma

    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    Chroma.from_documents(
        ids=ids,
        documents=docs,
        embedding=embeddings,
        persist_directory="./mynewdb"
    )


from typing import Dict, List, TypeVar

T = TypeVar('T')


def create_dict_from_keys_and_values(keys: List[str], values: List[T]) -> Dict[str, List[T]]:
    assert (len(keys) == len(values))

    id_doc_dict = {}

    if len(keys) == 0:
        return id_doc_dict

    for i, file_path in enumerate(keys):
        if file_path in id_doc_dict:
            id_doc_dict[file_path].append(values[i])
        else:
            id_doc_dict[file_path] = [values[i]]
    return id_doc_dict


def map_ids_to_paths(ids: List[str]) -> List[str]:
    return [id.split(':')[2] for id in ids]


def map_ids_to_hashes(ids: List[str]) -> List[str]:
    return [id.split(':')[3] for id in ids]


def upsert_docs(ids: List[str], docs: List[Document], db_dir: str, doc_type: str, source_identifier: str):
    assert (len(ids) == len(docs))

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
        delete_docs(removed_docs_ids)

    assert (len(changed_docs) == len(changed_docs))

    if len(changed_docs_ids) != 0:
        index_docs(changed_docs_ids, changed_docs)


def start():
    ids, docs = load_source_code("/home/milad/sources/scala/zio", "series/2.x", "github.com/zio/zio")
    # index_docs(ids[0:9], docs[0:9])
    upsert_docs(ids[0:9], docs[0:9], "./mynewdb", "source_code", "github.com/zio/zio")


if __name__ == "__main__":
    start()
