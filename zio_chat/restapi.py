import os
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
      <title>Chat</title>
      <style>
        form {
          margin-left: 20px;
          margin-right: 20px;
        }
      </style>
      <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    </head>
    <body>
        <h1>ZIO Chat</h1>
        <div id='messages'></div>
        <form action="" onsubmit="sendMessage(event)">
            <textarea id="messageText" name="userInput" autocomplete="off" rows="2" cols="100"></textarea>
            <button>Send</button>
        </form>
        <script>
            var ws = new WebSocket("ws://localhost:8081/chat");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                console.log(event)
                var content = marked.parse(JSON.parse(event.data).result)
                messages.innerHTML += "<h3>ZIO: </h3>"
                messages.innerHTML += content
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                var messages = document.getElementById("messages")
                messages.innerHTML += "<h3>User: </h3>"
                messages.innerHTML +=  "<p>" + input.value + "</p>"
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
docsearch = Chroma(persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"], embedding_function=embeddings)
qa: RetrievalQA = RetrievalQA.from_chain_type(llm=OpenAI(max_tokens=500), chain_type="stuff",
                                              retriever=docsearch.as_retriever(search_type="similarity",
                                                                               search_kwargs={"k": 2}))
qa.set_verbose(verbose=True)

@app.get("/old")
async def get():
    return HTMLResponse(html)

app.mount("/", StaticFiles(directory="./zio_chat/static/", html = True), name="site")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        result: dict[str, Any] = await qa.acall(data)
        await websocket.send_json(result)


def start():
    uvicorn.run("zio_chat.restapi:app", host="0.0.0.0", port=8081, reload=True)
