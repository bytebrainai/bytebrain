import asyncio

from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.embeddings import FakeEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.vectorstores import Weaviate

# langchain.verbose = True

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

docs = [Document(page_content=t, metadata={"source": i}) for i, t in enumerate(texts)]

# embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
embeddings = FakeEmbeddings(size=1000)
# weaviate_url="http://localhost:8080"
import weaviate
from weaviate import EmbeddedOptions

w = Weaviate(client=weaviate.Client(embedded_options=EmbeddedOptions()),
             index_name="myindex", text_key="mytextkey")
vector_store = w.from_documents(docs, embedding=embeddings, weaviate_url = "http://127.0.0.1:6666")

# vector_store = FAISS.from_documents(documents=docs, embedding=embeddings)

retriever = vector_store.as_retriever()

retrievalQA = RetrievalQAWithSourcesChain.from_llm(llm=OpenAI(verbose=True), retriever=retriever)


async def run_qa():
    result = await retrievalQA.acall({'question': 'what is the zio chat bot?'})
    print(result)
    print("Hello")


if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()
    asyncio.run(run_qa())
