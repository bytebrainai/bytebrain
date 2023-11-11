import os
from core.llm.custom_conversational_chain import ConversationalRetrievalChainWithCustomPrompt
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from langchain.chains.question_answering import load_qa_chain

llm = OpenAI(streaming=True,
             callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]),
             verbose=True,
             temperature=1.0,
             max_tokens=-1)

generate_standalone_query = PromptTemplate(
    input_variables=["query", "chat_history"],
    template="""Given the following CHAT HISTORY and the follow up QUERY, rephrase the QUERY to be a STANDALONE QUERY.
    -----
    CHAT HISTORY: {chat_history}
    -----
    QUERY: {query} 
    -----
    STANDALONE QUERY:"""
)

standalone_query_chain = LLMChain(llm=llm, prompt=generate_standalone_query, output_key="standalone_query")

load_docs_chain = load_qa_chain(llm=llm, chain_type="stuff", verbose=False)

docsearch = Chroma(
    persist_directory=os.environ["ZIOCHAT_CHROMA_DB_DIR"],
    embedding_function=OpenAIEmbeddings()
)

def get_chat_history(chat_history) -> str:
    return "\n".join(chat_history)


def template(query: str) -> str:
    return f"""Please refactor your answer to the User's Query based on given REFACTOR RULES.

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
    ------
    USER's QUERY: {query}
    ------
    YOUR ANSWER:"""


qa_chain = ConversationalRetrievalChainWithCustomPrompt(
    combine_docs_chain=load_docs_chain,
    retriever=docsearch.as_retriever(),
    question_generator=standalone_query_chain,
    get_chat_history=get_chat_history,
    return_source_documents=True,
    verbose=False,
    callbacks=[StreamingStdOutCallbackHandler()],
    prompt_refactor_template=template,
    max_tokens_limit=-1
)


def run():
    # r = qa_chain({"question": "what is zio?", "chat_history": []})
    # pprint.pprint(r)
    # qa_chain({"question": "please write a simple ZIO application?", "chat_history": []})
    qa_chain({"question": "Write an example of ZIO app that get two numbers and print sum of them?", "chat_history": []})
    # chain({"query": "use console", "chat-history": "Please write a ZIO application that takes two numbers from user and print sum of them"})
    # chain({"query": "What are the use-cases for ZIO?", "chat-history": ""})
    # chain({"query": "Write hello world Restful service with zhttp", "chat-history": ""})
    # chain({"query": "Write a ZIO App which get 10 url from user in console and the fetch all those urls concurrently", "chat-history": ""})
    # chain({"query": "Please write a zio application with an arbitrary logic.", "chat-history": ""})
    # a: dict[str, Any] = chain({"query": "write fib function using fibers", "chat-history": ""})
    # print(a)
    # chain({"query": "Please write a bubble sort with ZIO", "chat-history": ""})
