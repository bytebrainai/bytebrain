from typing import Optional

import langchain

from core.callbacks import StreamingLLMCallbackHandler

langchain.verbose = True
# langchain.debug=True
import asyncio

from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.schema import BaseRetriever

from fastapi import WebSocket
from core.upgrade_sqlite import upgrade_sqlite_version

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
doc_retriever = vectorstore.as_retriever()

llm = OpenAI()


def qa_with_stuffed_docs_chain(websocket: Optional[WebSocket], template: Optional[str] = None):
    qa_with_stuffed_docs_template = template or """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Helpful Answer:"""

    QA_WITH_STUFFED_DOCS_TEMPLATE = PromptTemplate(
        template=qa_with_stuffed_docs_template, input_variables=["context", "question"]
    )

    chain = load_qa_chain(
        llm,
        chain_type="stuff",
        verbose=True,
        prompt=QA_WITH_STUFFED_DOCS_TEMPLATE,
        callbacks=[(StreamingLLMCallbackHandler(websocket))] if websocket is not None else [],
    )
    return chain


def condense_question_chain():
    condense_chat_history_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(condense_chat_history_template),
        verbose=True,
        callbacks=[StdOutCallbackHandler()],
    )
    return chain


def get_chat_history(chat_history) -> str:
    return "\n\n".join(chat_history)


def make_qa_with_stuffed_docs_chain(document_retriever: BaseRetriever, websocket: Optional[WebSocket] = None,
                                    stuff_template: Optional[str] = None):
    qa = ConversationalRetrievalChain(
        retriever=document_retriever,
        combine_docs_chain=qa_with_stuffed_docs_chain(websocket, stuff_template),
        question_generator=condense_question_chain(),
        get_chat_history=get_chat_history,
        callbacks=[StdOutCallbackHandler()],
        return_source_documents=True,
        max_tokens_limit=3700,
    )
    return qa

question = 'What is ZIO JSON'

qa = make_qa_with_stuffed_docs_chain(document_retriever=doc_retriever)


async def run_qa():
    result = await qa._acall(
        {'question': question, 'chat_history': ''})
    print(result)
    print("Hello")


if __name__ == "__main__":
    asyncio.run(run_qa(), debug=True)
