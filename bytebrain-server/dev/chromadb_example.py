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

from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings


# def run():
# doc = Document(page_content="something very very new")
# embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
# Chroma.from_documents(documents=[doc], embedding=embeddings, ids=["s1"], persist_directory="./mydb")
# chroma = Chroma(embedding_function=embeddings, persist_directory='./db-discord')
# try:
#     chroma.update_document(document=doc, document_id="x")
# except ValueError:
#     chroma.add_documents(documents=[doc])
# print("done!")

import pandas as pd

# Provide the path to the Parquet file
parquet_file_path = './db-discord/chroma-embeddings.parquet'

# Read the Parquet file into a pandas DataFrame
data_frame = pd.read_parquet(parquet_file_path)

    # Now you can work with the data in the DataFrame


