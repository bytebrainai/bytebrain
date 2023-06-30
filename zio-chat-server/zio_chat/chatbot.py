from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT)
from langchain.chains.question_answering import load_qa_chain
from zio_chat.dev.custom_conversational_chain import ConversationalRetrievalChainWithCustomPrompt
from zio_chat.callbacks import StreamingLLMCallbackHandler
from fastapi import WebSocket
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma


def make_doc_search(persistent_dir: str):
    return Chroma(
        persist_directory=persistent_dir,
        embedding_function=OpenAIEmbeddings()
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


def make_combine_docs_chain(websocket: WebSocket):
    return load_qa_chain(
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


def make_question_answering_chatbot(websocket: WebSocket, persistent_dir: str):
    return ConversationalRetrievalChainWithCustomPrompt(
        combine_docs_chain=make_combine_docs_chain(websocket),
        retriever=make_doc_search(persistent_dir).as_retriever(),
        question_generator=question_generator,
        get_chat_history=get_chat_history,
        return_source_documents=False,
        prompt_refactor_template=refactor_prompt_template
    )


def refactor_prompt_template(query: str) -> str:
    return f"""Please refactor your answer to the User's Query based on given REFACTOR RULES. 
    If user asked you to write a code, please explain that code also.

    ----- 
    REFACTOR RULES: 
    If USER asked you to write code, you shouldn't use ZIO 1.x APIs in your generated response, instead you should only 
    use ZIO 2.x APIs.
    To make sure that your code is compatible with ZIO 2.x API, use the following migration table from ZIO 1.x to ZIO 2.x

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


def get_chat_history(chat_history) -> str:
    return "\n".join(chat_history)
