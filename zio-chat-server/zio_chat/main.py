import json
import os
import pprint
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
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT)
from langchain.chains.question_answering import load_qa_chain
from zio_chat.dev.custom_conversational_chain import ConversationalRetrievalChainWithCustomPrompt

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
    qa = ConversationalRetrievalChainWithCustomPrompt(
        combine_docs_chain=combine_docs_chain,
        retriever=docsearch.as_retriever(),
        question_generator=question_generator,
        get_chat_history=get_chat_history,
        return_source_documents=False,
        prompt_refactor_template=refactor_prompt_template
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
        print("OpenAI Result: {}".format(pprint.pformat(result)))


def refactor_prompt_template(query: str) -> str:
    return f"""Please refactor your answer to the User's Query based on given REFACTOR RULES. 
    If user asked you to write a code, please explain that code also.

    ----- 
    REFACTOR RULES: 
    If USER asked you to write code, you shouldn't use ZIO 1.x APIs in your generated response, instead you should only 
    use ZIO 2.x APIs.
    Because ZIO 1.x API is old and deprecated. Anyway, to make sure that your code compatible with ZIO 2.x API use the 
    following list. This is a list of tuples of "ZIO 1.x API" and "ZIO 2.x API": 

    | ZIO 1.x API | ZIO 2.x API |
    +-------------+-------------+
    | putStrLn | Console.printLine |
    | getStrLn | Console.readLine |
    | zio.App | zio.ZIOAppDefault |
    | extends zio.ZIOApp | extends ZIOAppDefault |
    | extends App | extends ZIOAppDefault |
    | def run(args: List[String]) | def run =  |
    | ZIO.effect | ZIO.attempt |
    | ZIO.effectTotal | ZIO.succeed |
    | console.putStrLn | Console.printLine |
    | override def run(args: List[String]) | def run =  |

    Remove any of following packages from import section: ["zio.console.Console"] 
    
    Please preserve codes inside markdown quotes
    ------
    USER's QUERY: {query}
    ------
    YOUR ANSWER:"""


def start():
    uvicorn.run("zio_chat.main:app", host="0.0.0.0", port=8081, reload=True)
