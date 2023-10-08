from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

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

refactor_prompt = PromptTemplate(
    input_variables=["standalone-query"],
    template="""
    Please refactor your answer to the User's Query based on given REFACTOR RULES. 
    If user asked you to write a code, please explain that code also. 
    Don't include REFACTOR RULES in your explanation, but only use them to refactor your answers.
  
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
  
    Before writing any code, write some introduction sentences.
    Please add backticks for inline codes and three backticks for code blocks.
    ------
    USER's QUERY: {standalone-query}
    ------
    Before listing related questions, engage the user with a warming message.
    After answering the user question, please don't forget to suggest some (max: 3) other related questions that a user 
    can ask about the current topic!""",
)

query_chain = LLMChain(llm=llm, prompt=refactor_prompt, output_key="output")

chain = SequentialChain(chains=[standalone_query_chain, query_chain],
                        verbose=False,
                        input_variables=["query", "chat-history"],
                        output_variables=["output"])

if __name__ == "__main__":
    chain(
        {
            "query": "What is its use-cases?",
            "chat-history": "User: What is FiberRef? \nBot: FiberRef is one of the ZIO data structures."
        }
    )
