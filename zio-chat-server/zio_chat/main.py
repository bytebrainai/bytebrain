import os
import json
import pprint

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
        result = await qa.acall(
            {
                "question": obj["question"],
                "project_name": "ZIO",
                "chat_history": obj["history"]
            },
            return_only_outputs=True
        )
        print("\n\n")
        print("OpenAI Result: {}".format(pprint.pformat(result)))


def start():
    uvicorn.run("zio_chat.main:app", host="0.0.0.0", port=8081, reload=True)
