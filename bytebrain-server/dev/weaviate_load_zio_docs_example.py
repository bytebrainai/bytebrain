import asyncio

import langchain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Weaviate

langchain.verbose = True

from langchain.schema import Document

# ids, docs = load_zio_website_docs(os.environ["ZIOCHAT_DOCS_DIR"], use_uuid=True)

texts = [
    "Scala is a functional Programming Language",
    "I love functional programming",
    "fp is too simple an is not hard to understand",
    "women must adore their husbands",
    "ZIO is a good library for writing fp apps",
    "Feminism is the belief that all genders should have equal rights and opportunities.",
    "This movement is about making the world a better place for everyone",
    "The purpose of ZIO Chat Bot is to provide list of ZIO Projects",
    "I've got a cold and I've sore throat",
    "ZIO chat bot is an open source project."
]

# docs = [Document(page_content=t, metadata={"source": i}) for i, t in enumerate(texts)]

embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

from langchain.storage import LocalFileStore
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings

underlying_embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

fs = LocalFileStore("./cache/")
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings, fs, namespace=underlying_embeddings.model
)

import weaviate

client = weaviate.Client(url="http://127.0.0.1:8080")
vector_store: Weaviate = Weaviate(client, index_name='Zio', text_key="text", attributes=['source'],
                                  embedding=cached_embedder, by_text=False)

# vector_store = vector_store.from_documents(docs,index_name="Zoo", embedding=cached_embedder,
#                                            weaviate_url="http://127.0.0.1:8080")

retriever = vector_store.as_retriever()

retrievalQA = RetrievalQAWithSourcesChain.from_llm(llm=OpenAI(verbose=True), retriever=retriever)

from core.utils.utils import async_measure_execution_time


@async_measure_execution_time
async def run_qa():
    result = await retrievalQA.acall({'question': "What is ZIO?"})
    print(result)


if __name__ == "__main__":
    asyncio.run(run_qa())
