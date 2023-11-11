from core.docs.document_loader import load_source_code
from core.db import upsert_docs


def load_saved_ids():
    with open("ids.txt", "r") as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]
    return lines


def start():
    ids, docs = load_source_code("/home/milad/sources/scala/zio", "series/2.x", "github.com/zio/zio")
    upsert_docs(ids[0:9], docs[0:9], "./mynewdb")


if __name__ == "__main__":
    start()
