import os
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

docsearch = Chroma(
    persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"],
    embedding_function=embeddings
)

qa: RetrievalQA = \
    RetrievalQA.from_chain_type(
        llm=OpenAI(max_tokens=500),
        chain_type="stuff",
        retriever=docsearch.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )
    )
qa.set_verbose(verbose=True)

app = FastAPI()

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        result: dict[str, Any] = await qa.acall(data)
        await websocket.send_json(result)


def start():
    uvicorn.run("zio_chat.restapi:app", host="0.0.0.0", port=8081, reload=True)
