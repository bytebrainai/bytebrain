import langchain
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.vectorstores import FAISS

langchain.verbose=True
# langchain.debug=True
import asyncio

import config
from core.utils.upgrade_sqlite import upgrade_sqlite_version

cfg = config.load_config()
upgrade_sqlite_version()
embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

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

vectorstore = FAISS.from_documents(documents=docs, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

retrievalQA = RetrievalQAWithSourcesChain.from_llm(llm=OpenAI(verbose=True), retriever=retriever)


async def run_qa():
    result = await retrievalQA._acall({'question': 'what is the zio chat bot?'})
    print(result)
    print("Hello")


if __name__ == "__main__":
    asyncio.run(run_qa(), debug=True)
