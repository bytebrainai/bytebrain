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

import langchain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.vectorstores import FAISS

langchain.verbose = True
# langchain.debug=True
import asyncio

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

from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain

qa = load_qa_with_sources_chain(llm=OpenAI(), verbose=True)

question = 'what is the zio chat bot?'


async def run_qa():
    result = await qa._acall({'question': question, 'input_documents': retriever.get_relevant_documents(question)})
    print(result)
    print("Hello")


if __name__ == "__main__":
    asyncio.run(run_qa(), debug=True)
