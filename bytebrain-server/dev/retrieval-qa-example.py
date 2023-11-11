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
