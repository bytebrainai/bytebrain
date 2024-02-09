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

from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import config
from core.utils.upgrade_sqlite import upgrade_sqlite_version

cfg = config.load_config()
upgrade_sqlite_version()
embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
chroma = Chroma(embedding_function=embeddings, persist_directory=cfg.db_dir)
retrievalQA = RetrievalQA.from_llm(llm=OpenAI(), retriever=chroma.as_retriever(), verbose=True)


async def main():
    result = await retrievalQA.acall({'query': 'What is Unsafe.unsafe'})
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
