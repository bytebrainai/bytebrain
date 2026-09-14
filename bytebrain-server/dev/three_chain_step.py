# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = OpenAI(streaming=True,
             callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]),
             verbose=True,
             temperature=1.0)

generate_standalone_query = PromptTemplate(
    input_variables=["query", "chat-history"],
    template="""Given the following CHAT HISTORY and the follow up QUERY, rephrase the follow up query to be a STANDALONE QUERY?
    -----
    CHAT HISTORY: {chat-history}
    -----
    QUERY: {query} 
    -----
    STANDALONE QUERY:
    """
)

standalone_query_chain = LLMChain(llm=llm, prompt=generate_standalone_query, output_key="standalone-query")

query_prompt = PromptTemplate(
    input_variables=["standalone-query"],
    template="{standalone-query}"
)

query_chain = LLMChain(llm=llm, prompt=query_prompt, output_key="text")

refactor_prompt = PromptTemplate(
    input_variables=["text"],
    template="""GIVEN CODE:
    {text}
    
    -----
    Please act as a code reviewer and refactor this code. 
    Please keep in mind that ZIO has two different versions ZIO 1.x and ZIO 2.x.
    The code should not have any ZIO 1.x terms, instead you should refactor the code to have equivalent terms in ZIO 2.x.
    Here is list of tuples of "deprecated terms" and "their equivalent terms", please use this list to remove any ZIO 1.x from your code:
    ["putStrLn" -> "Console.printLine", "getStrLn" -> "Console.readLine", "zio.App" -> "zio.ZIOAppDefault",
     "extends zio.ZIOApp" -> "extends ZIOAppDefault", "extends App" -> "extends ZIOAppDefault",
     "def run(args: List[String])" -> "def run = ", "ZIO.effect" -> "ZIO.attempt",
     "yield ExitCode.success" -> "yield ()", "ZIO.effectTotal" -> "ZIO.succeed",
     "console.putStrLn" -> "Console.printLine", 
     "override def run(args: List[String])" -> "def run = ",
    ]
    
    Remove Console, Clock, Random from ZIO environment. 
    e.g. The `ZIO[Console with ServiceA, _, _]` should be refactored to `ZIO[ServiceA, _, _]`. 
    e.g. The `ZIO[Console, _, _]` should be refactored to `ZIO[Any, _, _]`
    
    Remove `ZIO#fold` from final app logic.
    
    Don't include any terms in the following deprecated list in your generated code
    deprecated list = [ZEnv, , ExitCode.success, ExitCode, ZIOApp, Has]
    
    Do not import any of following import statements in your generated code: [import zio.console._, import zio.console.Console]
    """,
)

refactor_chain = LLMChain(llm=llm, prompt=refactor_prompt, output_key="output")

chain = SequentialChain(chains=[standalone_query_chain, query_chain ,refactor_chain],
                        verbose=False,
                        input_variables=["query", "chat-history"],
                        output_variables=["text", "output"])


def run():
    # chain({"question": "use console", "chat-history": "Please write a ZIO application that takes two numbers from user and print sum of them"})
    # chain({"question": "What is ZIO good for?", "chat-history": ""})
    # chain({"question": "Write hello world Restful service with zhttp", "chat-history": ""})
    # chain({"question": "Write a ZIO App which get 10 url from user in console and the fetch all those urls concurrently", "chat-history": ""})
    chain({"query": "Write a zio application with a arbitrarty logic. Please write that application at least in 100 lines of code", "chat-history": ""})
