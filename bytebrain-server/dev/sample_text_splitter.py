import hashlib
from typing import Optional, List, Dict, Any, Tuple

from langchain.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain.schema import Document


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


def identify_removed_snippets(original: Dict[str, List[str]], new: Dict[str, List[str]]) -> List[str]:
    removed_files: List[str] = []
    for file_path, hashes in original.items():
        if file_path not in new:
            removed_files.append(file_path)
    return removed_files


def identify_changed_snippets(original: Dict[str, List[str]], new: Dict[str, List[str]]) -> List[str]:
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


def create_dict_of_sources(ids: List[str]) -> Dict[str, List[str]]:
    snippets: Dict[str, List[str]] = {}

    for id in ids:
        parts = id.rsplit(':', 1)
        file_path = parts[0]
        hash_value = parts[1]

        if file_path in snippets:
            snippets[file_path].append(hash_value)
        else:
            snippets[file_path] = [hash_value]

    return snippets


def load_source_code(repo_path: str, branch: Optional[str],
                     source_identifier: str) -> (List[str], List[Document]):
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


def remove_docs(ids: List[str]):
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
    # db.from_documents(docs)


def filter_documents_by_id(documents: List[Document], ids: List[str]):
    docs = zip(documents, ids)


def create_dict_of_files_to_docs_and_hashes(ids, docs) -> Dict[str, List[Tuple[Document, str]]]:
    """Creates a dictionary of IDs and documents from two lists of IDs and documents.

  Args:
    ids: A list of IDs.
    docs: A list of documents.

  Returns:
    A dictionary of IDs and documents.
  """
    id_doc_dict = {}
    for i in range(len(ids)):
        if ids[i].rsplit(':', 1)[0] in id_doc_dict:
            current_value = id_doc_dict[ids[i].rsplit(':', 1)[0]]
            current_value.append((docs[i], ids[i].rsplit(':', 1)[1]))
            id_doc_dict[ids[i].rsplit(':', 1)[0]] = current_value
        else:
            id_doc_dict[ids[i].rsplit(':', 1)[0]] = [(docs[i], ids[i].rsplit(':', 1)[1])]
    return id_doc_dict


def extract_info_from_id(id: str) -> (str, str, str):
    r = id.split(':')
    return r[0], r[1], r[2]


def upsert_docs(ids: List[str], docs: List[Document], db_dir: str, doc_type: str = "source_code",
                source_identifier: str = "github.com/zio/zio"):
    new_files_to_docs_and_hashes_dicts: Dict[str, List[Tuple[Document, str]]] = create_dict_of_files_to_docs_and_hashes(
        ids, docs)
    new_files_to_hash_dicts: Dict[str, List[str]] = {key: [item[1] for item in value] for key, value in
                                                     new_files_to_docs_and_hashes_dicts.items()}

    indexed_docs_ids: List[str] = get_original_ids(db_dir, doc_type, source_identifier)
    indexed_file_to_hash_dict: Dict[str, List[str]] = create_dict_of_sources(indexed_docs_ids)

    changed_files: List[str] = identify_changed_snippets(indexed_file_to_hash_dict, new_files_to_hash_dicts)

    changed_docs_ids: List[str] = []
    changed_docs: List[Document] = []
    for file in changed_files:
        if file in new_files_to_docs_and_hashes_dicts:
            d = new_files_to_docs_and_hashes_dicts[file]
            for x in d:
                changed_docs.append(x[0])
                changed_docs_ids.append(file + ':' + x[1])
        else:
            print(file)

    removed_files: List[str] = list(
        set(identify_removed_snippets(indexed_file_to_hash_dict, new_files_to_hash_dicts) + changed_files))
    removed_docs_ids: List[str] = []
    for file in removed_files:
        if file in indexed_file_to_hash_dict:
            hashes = indexed_file_to_hash_dict[file]
            for h in hashes:
                removed_docs_ids.append(file + ':' + h)
    if len(removed_docs_ids) != 0:
        remove_docs(removed_docs_ids)

    assert (len(changed_docs) == len(changed_docs))

    if len(changed_docs_ids)  != 0:
        index_docs(changed_docs_ids, changed_docs)


def start():
    ids, docs = load_source_code("/home/milad/sources/scala/zio", "series/2.x", "github.com/zio/zio")
    # index_docs(ids[0:9], docs[0:9])
    upsert_docs(ids[0:9], docs[0:9], "./mynewdb")


if __name__ == "__main__":
    start()
    # ids = get_original_ids("./mynewdb", "source_code", "github.com/zio/zio")
    # print(ids)
    # dict = create_dict_of_sources(ids)
    # print(dict)
    # # start()


def test():
    # ids, _ = load_source_code("/home/milad/sources/scala/zio", "series/2.x", "github.com/zio/zio")

    # with open("ids.txt", "w") as file:
    #     for id in ids:
    #         file.write(id + "\n")

    original_ids = load_saved_ids()
    original_dict = create_dict_of_sources(original_ids)
    new_ids, _ = load_source_code("/home/milad/sources/scala/zio", "series/2.x", "github.com/zio/zio")
    new_dict = create_dict_of_sources(new_ids)
    changes = identify_changed_snippets(original_dict, new_dict)
