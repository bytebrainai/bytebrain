from typing import Dict, Any

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = OpenAI(streaming=True,
             callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]),
             verbose=True,
             temperature=1.0,
             max_tokens=-1)

generate_standalone_query = PromptTemplate(
    input_variables=["query", "chat-history"],
    template="""Given the following CHAT HISTORY and the follow up QUERY, rephrase the QUERY to be a STANDALONE QUERY.
    -----
    CHAT HISTORY: {chat-history}
    -----
    QUERY: {query} 
    -----
    STANDALONE QUERY:"""
)

standalone_query_chain = LLMChain(llm=llm, prompt=generate_standalone_query, output_key="standalone-query")

# query_prompt = PromptTemplate(
#     input_variables=["standalone-query"],
#     template="{standalone-query}"
# )
#
# query_chain = LLMChain(llm=llm, prompt=query_prompt, output_key="text")

refactor_prompt = PromptTemplate(
    input_variables=["standalone-query"],
    template="""Please refactor your answer to the User's Query based on given REFACTOR RULES.

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
    
    Also remove these package imports: import zio.console.Console
    ------
    USER's QUERY: {standalone-query}
    ------
    YOUR ANSWER:""",
)

query_chain = LLMChain(llm=llm, prompt=refactor_prompt, output_key="output")

# from langchain.chains import ConversationalRetrievalChain
#
# refactor_chain = ConversationalRetrievalChain(
#     combine_docs_chain=combine_docs_chain,
#     llm=llm,
#     prompt=refactor_prompt,
#     output_key="output"
# )

chain = SequentialChain(chains=[standalone_query_chain, query_chain],
                        verbose=False,
                        input_variables=["query", "chat-history"],
                        output_variables=["output"])

def run():
    # chain({"query": "use console", "chat-history": "Please write a ZIO application that takes two numbers from user and print sum of them"})
    # chain({"query": "What are the use-cases for ZIO?", "chat-history": ""})
    # chain({"query": "Write hello world Restful service with zhttp", "chat-history": ""})
    chain({"query": "Write a ZIO App which get 10 url from user in console and the fetch all those urls concurrently", "chat-history": ""})
    # chain({"query": "Please write a zio application with an arbitrary logic.", "chat-history": ""})
    # a: dict[str, Any] = chain({"query": "write fib function using fibers", "chat-history": ""})
    # print(a)
    # chain({"query": "Please write a bubble sort with ZIO", "chat-history": ""})
