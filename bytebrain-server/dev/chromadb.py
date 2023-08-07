from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings


def run():
    doc = Document(page_content="something very very new")
    embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
    # Chroma.from_documents(documents=[doc], embedding=embeddings, ids=["s1"], persist_directory="./mydb")
    chroma = Chroma(embedding_function=embeddings, persist_directory="./mydb")
    try:
        chroma.update_document(document=doc, document_id="x")
    except ValueError:
        chroma.add_documents(documents=[doc])
    print("done!")

    import pandas as pd

    # Provide the path to the Parquet file
    parquet_file_path = './mydb/chroma-embeddings.parquet'

    # Read the Parquet file into a pandas DataFrame
    data_frame = pd.read_parquet(parquet_file_path)

    # Now you can work with the data in the DataFrame
    print(data_frame)


