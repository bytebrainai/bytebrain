import asyncio
import json
import os
import pprint
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket

from zio_chat.chatbot import make_question_answering_chatbot

app = FastAPI()


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    qa = make_question_answering_chatbot(websocket, os.environ["ZIOCHAT_CHROMA_DB_DIR"])
    while True:
        raw_data = await websocket.receive_text()
        obj = json.loads(raw_data)
        print("Question Received: {}".format(obj))
        print("\n\n")
        result: dict[str, Any] = await qa.acall(
            {
                "question": obj["question"],
                "project_name": "ZIO",
                "chat_history": obj["history"]
            },
            return_only_outputs=True
        )
        print("\n\n")
        references: list[dict[str, Any]] = \
            [{"title": metadata["title"], "url": metadata["url"]} for metadata in
             (src_doc.metadata for src_doc in (result["source_documents"]))]

        print("OpenAI Result: {}".format(pprint.pformat(references[:3])))
        await websocket.send_json({"token": "", "completed": True, "references": references[:3]})


@app.websocket("/dummy_chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()

        with open('zio_chat/dummy/chat.md', 'r') as file:
            response = file.read()

        tokens = [{"token": token + " ", "completed": False} for token in response.split(" ")]
        tokens.append(
            {"completed": True,
             "references":
                 [{'title': 'Ref', 'url': 'https://zio.dev/reference/concurrency/ref'},
                  {'title': 'Global Shared State Using Ref',
                   'url': 'https://zio.dev/reference/state-management/global-shared-state'},
                  {'title': 'TRef', 'url': 'https://zio.dev/reference/stm/tref'}]}
        )
        for item in tokens:
            await asyncio.sleep(0.02)
            await websocket.send_json(item)


def start():
    uvicorn.run("zio_chat.main:app", host="0.0.0.0", port=8081, reload=True)
