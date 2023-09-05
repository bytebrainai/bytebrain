import chromadb

from langchain.embeddings.openai import OpenAIEmbeddings

chroma_client = chromadb.Client(
    chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./test",
    )
)
embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
collection = chroma_client.create_collection(name="my_collection", embedding_function=embeddings.embed_documents)
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id1", "id2"]
)

results = collection.query(
    query_texts=["This is a query document"],
    n_results=2
)

collection.update(ids="id2", documents=["Hello!"])

collection.delete(ids=[])
chroma_client.persist()

import pandas as pd
embeddings_df = pd.read_parquet('./test/chroma-embeddings.parquet')
collections_df = pd.read_parquet('./test/chroma-collections.parquet')
