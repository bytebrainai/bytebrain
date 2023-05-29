import json
import os
from abc import ABC
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT)
from langchain.chains.question_answering import load_qa_chain

embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

docsearch = Chroma(
    persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"],
    embedding_function=embeddings
)


class StreamingLLMCallbackHandler(AsyncCallbackHandler, ABC):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        print(token, end="")
        resp = {"token": token, "completed": False}
        await self.websocket.send_json(resp)

    async def on_llm_end(self, response, **kwargs) -> None:
        await self.websocket.send_json({"token": "", "completed": True})


def get_chat_history(chat_history) -> str:
    return "\n".join(chat_history)


app = FastAPI()


@app.websocket("/chat_")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    streaming_handler = StreamingLLMCallbackHandler(websocket)
    llm = ChatOpenAI(client=OpenAI, streaming=True, callbacks=[streaming_handler], temperature=0)
    qa: RetrievalQA = \
        RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 2}
            )
        )
    qa.set_verbose(verbose=True)
    while True:
        data = await websocket.receive_text()
        print("Question Received: {}".format(data))
        result = await qa.acall(data)
        print("OpenAI Result: {}".format(result))


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    combine_docs_chain = load_qa_chain(
        ChatOpenAI(
            client=OpenAI,
            streaming=True,
            callbacks=[(StreamingLLMCallbackHandler(websocket))],
            temperature=0,
            verbose=False
        ),
        chain_type="stuff",
        verbose=False
    )
    question_generator = LLMChain(
        llm=ChatOpenAI(
            client=OpenAI,
            streaming=False,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=0,
            verbose=False
        ),
        prompt=CONDENSE_QUESTION_PROMPT,
        verbose=False
    )
    qa = ConversationalRetrievalChain(
        combine_docs_chain=combine_docs_chain,
        retriever=docsearch.as_retriever(),
        question_generator=question_generator,
        get_chat_history=get_chat_history,
        return_source_documents=False
    )
    while True:
        raw_data = await websocket.receive_text()
        obj = json.loads(raw_data)
        print("Question Received: {}".format(obj))
        print("\n\n")
        result = await qa.acall(
            {
                "question": obj["question"],
                "project_name": "ZIO",
                "chat_history": obj["history"]
            },
            return_only_outputs=True
        )
        print("\n\n")
        print("OpenAI Result: {}".format(result))


def start():
    uvicorn.run("zio_chat.main:app", host="0.0.0.0", port=8081, reload=True)
