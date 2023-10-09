import os
from typing import Optional, List, Dict

import yaml
from langchain.document_loaders import GitLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain.document_transformers.html2text import Html2TextTransformer
from langchain.schema import Document
from langchain.text_splitter import Language, MarkdownTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.utils import calculate_md5_checksum


def load_zio_website_docs(directory: str) -> (List[str], List[Document]):
    def extract_metadata(md_file_path: str) -> Dict[str, str]:
        with open(md_file_path, 'r') as file:
            content = file.read()

        # Parse YAML front matter
        try:
            _, yaml_content, _ = content.split('---', 2)
            metadata = yaml.safe_load(yaml_content)
            return {"id": metadata.get('id'), "title": metadata.get("title")}
        except ValueError:
            file_name = os.path.basename(md_file_path)
            return {"id": file_name, "title": file_name}

    documents: list[Document] = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_path = os.path.join(root, filename)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                metadata: dict[str, str] = extract_metadata(md_path)
                for index, doc in enumerate(docs):
                    doc.metadata["doc_path"] = doc.metadata.pop("source").split("/zio/website/docs/")[1]
                    doc.metadata.setdefault("doc_source", "zio.dev")
                    doc.metadata.setdefault("doc_id", root.split("/zio/website/docs/")[1] + '/' + metadata["id"])
                    doc.metadata.setdefault("doc_title", metadata["title"])
                documents.extend(docs)

    fragmented_docs = MarkdownTextSplitter().split_documents(documents)

    ids: List[str] = []
    for d in fragmented_docs:
        hash = calculate_md5_checksum(d.page_content)
        doc_type = "documentation"
        source_identifier = "github.com/zio/zio"
        id = f"{doc_type}:{source_identifier}:{d.metadata['doc_path']}:{hash}"
        ids.append(id)

    assert (len(ids) == len(fragmented_docs))
    return ids, fragmented_docs


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


def load_zionomicon_docs(directory: str) -> (List[str], List[Document]):
    documents: list[Document] = []

    chapters = {
        "05-integrating-with-zio.md": "Essentials: Integrating With ZIO",
        "22-advanced-stm.md": "Software Transactional Memory: Advanced STM",
        "34-assertions.md": "Testing: Assertions",
        "21-stm-data-structures.md": "Software Transaction Memory: STM Data Structures",
        "07-concurrency-operators.md": "Parallelism And Concurrency: Concurrency Operators",
        "24-debugging.md": "Advanced Error Management: Debugging",
        "33-basic-testing.md": "Testing: Basic Testing",
        "40-reporting.md": "Testing: Reporting",
        "02-first-steps-with-zio.md": "Essentials: First Steps With ZIO",
        "48-applications-spark.md": "Applications: Spark",
        "13-hub-broadcasting.md": "Concurrent Structures: Hub - Broadcasting",
        "49-appendix-a-the-scala-type-system.md": "Appendix: The Scala Type System",
        "30-combining-streams.md": "Streaming: Combining Streams",
        "03-testing-zio-programs.md": "Essentials: Testing ZIO Programs",
        "29-transforming-streams.md": "Streaming: Transforming Streams",
        "26-first-steps-with-zstream.md": "Streaming: First Steps With ZStream",
        "39-test-annotations.md": "Testing: Test Annotations",
        "38-property-based-testing.md": "Testing: Property Based Testing",
        "32-sinks.md": "Streaming: Sinks",
        "10-references-functional-descriptions-of-mutable-state.md": "Concurrent Structures: Ref - Shared State",
        "11-promise-work-synchronization.md": "Concurrent Structures: Promise - Work Synchronization",
        "41-applications-parallel-web-crawler.md": "Applications: Parallel Web Crawler",
        "08-fiber-supervision-in-depth.md": "Parallelism And Concurrency: Fiber Supervision In Depth",
        "06-the-fiber-model.md": "Parallelism And Concurrency: The Fiber Model",
        "25-best-practices.md": "Advanced Error Management: Best Practices",
        "47-applications-graphql-api.md": "Applications: GraphQL API",
        "14-semaphore-work-limiting.md": "Concurrent Structures: Semaphore - Work Limiting",
        "31-pipelines.md": "Streaming: Pipelines",
        "45-applications-grpc-microservices.md": "Applications: gRPC Microservices",
        "44-applications-kafka-stream-processor.md": "Applications: Kafka Stream Processor",
        "28-channels.md": "Channels: Unifying Streams, Sinks, and Pipelines",
        "20-stm-composing-atomicity.md": "Software Transactional Memory: Composing Atomicity",
        "36-test-aspects.md": "Testing: Test Aspects",
        "16-scope-composable-resources.md": "Resource Handling: Scope - Composable Resources",
        "42-applications-file-processing.md": "Applications: File Processing",
        "46-applications-rest-api.md": "Applications: REST API",
        "43-applications-command-line-interface.md": "Applications: Command Line Interface",
        "27-next-steps-with-zstream.md": "Streaming: Next Steps With ZStream",
        "01-foreword.md": "Foreword by John A. De Goes",
        "50-appendix-b-mastering-variance.md": "Appendix: Mastering Variance",
        "15-acquire-release-safe-resource-handling-for-asynchronous-code.md": "Resource Handling: Acquire Release - Safe Resource Handling",
        "23-retries.md": "Advanced Error Management: Retries",
        "12-queue-work-distribution.md": "Concurrent Structures: Queue - Work Distribution",
        "35-the-test-environment.md": "Testing: The Test Environment",
        "04-the-zio-error-model.md": "Essentials: The ZIO Error Model",
        "09-interruption-in-depth.md": "Parallelism And Concurrency: Interruption In Depth",
        "19-advanced-dependency-injection.md": "Dependency Injection: Advanced Dependency Injection",
        "18-dependency-injection-essentials.md": "Dependency Injection: Essentials",
        "37-using-resources-in-tests.md": "Testing: Using Resources In Tests",
        "17-advanced-scopes.md": "Resource Handling: Advanced Scopes",
    }

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.md'):
                md_path = os.path.join(root, file_name)
                docs: list[Document] = UnstructuredMarkdownLoader(md_path).load()
                for index, doc in enumerate(docs):
                    doc.metadata.setdefault("doc_source", "zionomicon")
                    doc.metadata.setdefault("doc_path", doc.metadata.pop('source').split("/zionomicon/docs/")[1])
                    doc.metadata.setdefault("doc_chapter", chapters[file_name])
                documents.extend(docs)

    fragmented_docs = MarkdownTextSplitter().split_documents(documents)

    ids: List[str] = []
    for d in fragmented_docs:
        hash = calculate_md5_checksum(d.page_content)
        doc_type = "documentation"
        source_identifier = "github.com/zivergetech/zionomicon"
        id = f"{doc_type}:{source_identifier}:{d.metadata['doc_path']}:{hash}"
        ids.append(id)

    assert (len(ids) == len(fragmented_docs))
    return ids, fragmented_docs


def load_youtube_docs(video_id: str):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=False)
    docs: list[Document] = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(docs)
    for index, doc in enumerate(splitted_docs):
        doc.metadata.pop("source")
        doc.metadata.setdefault("doc_source", "youtube.com")
        doc.metadata.setdefault("doc_url", video_url)
    ids = [f"video_transcript:youtube.com/@Ziverge:{video_id}:{calculate_md5_checksum(c.page_content)}" for c in
           splitted_docs]
    assert (len(ids) == len(splitted_docs))
    return ids, splitted_docs


def load_docs_from_site(source_identifier: str, **kwargs):
    # Set default values
    default_loader_params = {
        "max_depth": None,
        "use_async": True,
        "extractor": None,
        "exclude_dirs": None,
        "timeout": None,
        "prevent_outside": True
    }

    # Update default values with user-specified values
    loader_params = {**default_loader_params, **kwargs}

    # Instantiate RecursiveUrlLoader with the specified parameters
    loader = RecursiveUrlLoader(**loader_params)

    docs = loader.load()

    from langchain.text_splitter import MarkdownTextSplitter

    text_docs = Html2TextTransformer(ignore_images=True).transform_documents(docs)

    for index, doc in enumerate(text_docs):
        doc.metadata.setdefault("doc_source", source_identifier)
        doc.metadata.setdefault("doc_url", doc.metadata.pop("source"))

    splitted_docs = MarkdownTextSplitter().transform_documents(text_docs)

    ids: List[str] = []
    for doc in splitted_docs:
        content_hash = calculate_md5_checksum(doc.page_content)
        doc_type = "website"
        id = f"{doc_type}:{source_identifier}:{content_hash}"
        ids.append(id)

    assert (len(ids) == len(splitted_docs))
    return ids, splitted_docs
