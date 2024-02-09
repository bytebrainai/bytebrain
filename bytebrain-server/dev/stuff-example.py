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

from langchain.chains import LLMChain
from langchain.chains import StuffDocumentsChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.schema import Document

import langchain

langchain.debug = True
texts = [
    "Scala is a functional Programming Language",
    "I love functional programming",
    "fp is too simple an is not hard to understand",
    "women must adore their husbands",
    "ZIO is a good library for writing fp apps",
    "Feminism is the belief that all genders should have equal rights and opportunities.",
    "This movement is about making the world a better place for everyone",
    "The purpose of ZIO Chat Bot is to provide list of ZIO Projects",
    "I've got a cold and I've sore throat"
]

vectorstore = FAISS.from_texts(texts=texts, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()
query = "What is the remedy of sore throat?"
docs: list[Document] = retriever.get_relevant_documents(query=query)

chain = StuffDocumentsChain(
    llm_chain=LLMChain(llm=OpenAI(), prompt=PromptTemplate.from_template(
        "SYSTEM: Answer the user question based on given context. "
        # "If you don't know the answer based on the given context, please say a phrase which means you don't know the answer."
        "If there is no related words in the given context, please say a phrase which means you don't know the answer."
        "\n"
        "Context: {context}"
        "\n"
        f"Question: {query}"
    ), verbose=True),
    document_prompt=PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    ),
    document_variable_name="context",
    verbose=True
)

result = chain.run({"input_documents": docs})
print(type(result))
print(result)

# model = ChatOpenAI()
# template = """Answer the question based only on the following context:
# {context}
#
# Question: {question}
# """
# prompt = ChatPromptTemplate.from_template(template)
#
# retrieval_chain = (
#         {"context": retriever, "question": RunnablePassthrough()}
#         | prompt
#         | model
#         | StrOutputParser()
# )
#
# import langchain
#
# langchain.debug = True
# langchain.verbose = True
# result = retrieval_chain.invoke("where did harrison work?")
#
# print(result)
