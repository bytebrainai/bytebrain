import langchain
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import Document
from langchain.vectorstores import FAISS

from core.llm.custom_conversational_chain import ConversationalRetrievalChainWithCustomPrompt

langchain.verbose = True
langchain.debug=True

from core.utils.upgrade_sqlite import upgrade_sqlite_version

upgrade_sqlite_version()
embeddings: OpenAIEmbeddings = OpenAIEmbeddings()

texts = [
    "Scala is a functional Programming Language",
    "I love functional programming",
    "fp is too simple an is not hard to understand",
    "women must adore their husbands",
    "ZIO is a good library for writing fp apps",
    "Feminism is the belief that all genders should have equal rights and opportunities.",
    "This movement is about making the world a better place for everyone",
    "The purpose of ZIO Chat Bot is to provide list of ZIO Projects",
    "I've got a cold and I've sore throat",
    "ZIO chat bot is an open source project."
]

docs = [Document(page_content=t, metadata={"source": i}) for i, t in enumerate(texts)]

vectorstore = FAISS.from_documents(documents=docs, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

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

load_docs_chain = load_qa_chain(llm=llm, chain_type="stuff", verbose=False)


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


standalone_query_chain = LLMChain(llm=llm, prompt=generate_standalone_query, output_key="standalone_query")

qa_chain = ConversationalRetrievalChainWithCustomPrompt(
    combine_docs_chain=load_docs_chain,
    retriever=retriever,
    question_generator=standalone_query_chain,
    get_chat_history=get_chat_history,
    return_source_documents=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    prompt_refactor_template=template,
    max_tokens_limit=-1
)

if __name__ == "__main__":
    qa_chain(
        {"question": "Write an example of ZIO app that get two numbers and print sum of them?", "chat_history": []})
