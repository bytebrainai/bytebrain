from typing import Optional, List

from langchain.document_loaders import GitLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

from core.utils import calculate_md5_checksum


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
