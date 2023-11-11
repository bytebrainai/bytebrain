from typing import Optional

from fastapi import WebSocket
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.llm import BaseLanguageModel
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from langchain.vectorstores import Chroma
from langchain.vectorstores.base import VectorStore

from core.llm.callbacks import StreamingLLMCallbackHandler
from core.utils.upgrade_sqlite import upgrade_sqlite_version


def qa_with_stuffed_docs_chain(
        websocket: Optional[WebSocket],
        template: Optional[str] = None):
    qa_with_stuffed_docs_template = template or """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Helpful Answer:"""

    QA_WITH_STUFFED_DOCS_TEMPLATE = PromptTemplate(
        template=qa_with_stuffed_docs_template, input_variables=["context", "question"]
    )

    chain = load_qa_chain(
        ChatOpenAI(
            client=OpenAI,
            streaming=True,
            callbacks=[(StreamingLLMCallbackHandler(websocket))] if websocket is not None else [],
            temperature=0,
            verbose=False
        ),
        chain_type="stuff",
        verbose=True,
        prompt=QA_WITH_STUFFED_DOCS_TEMPLATE,
    )
    return chain


def condense_question_chain(
        llm: BaseLanguageModel
):
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
    llm = ChatOpenAI(
        client=OpenAI,
        streaming=False,
        callbacks=[StreamingStdOutCallbackHandler()],
        temperature=0,
        verbose=True
    )
    qa = ConversationalRetrievalChain(
        retriever=document_retriever,
        combine_docs_chain=qa_with_stuffed_docs_chain(websocket, stuff_template),
        question_generator=condense_question_chain(llm),
        get_chat_history=get_chat_history,
        callbacks=[StdOutCallbackHandler()],
        return_source_documents=True,
        max_tokens_limit=3750,
    )
    return qa


def make_doc_search(persistent_dir: str):
    upgrade_sqlite_version()
    return Chroma(
        persist_directory=persistent_dir,
        embedding_function=OpenAIEmbeddings()
    )


def make_question_answering_chatbot(
        websocket: Optional[WebSocket],
        vector_store: VectorStore,
        prompt_template: str):
    document_retriever = vector_store.as_retriever(
        # TODO: Find the best options for retrieving docs
        # search_type="similarity_score_threshold",
        # search_kwargs={'score_threshold': 0.8}
        # or
        # search_type="mmr",
        # search_kwargs={
        #     'k': 10,
        #     'fetch_k': 30
        # }
    )
    return make_qa_with_stuffed_docs_chain(document_retriever=document_retriever, websocket=websocket,
                                           stuff_template=prompt_template)


def generate_prompt(prompt_template: str, query: str) -> str:
    return prompt_template.replace("{query}", query)


def get_chat_history(chat_history) -> str:
    return "\n\n".join(chat_history)
