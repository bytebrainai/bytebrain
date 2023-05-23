import os
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

docsearch = Chroma(
    persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"],
    embedding_function=embeddings
)


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
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


app = FastAPI()


@app.websocket("/chat")
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


def start():
    uvicorn.run("zio_chat.restapi:app", host="0.0.0.0", port=8081, reload=True)
