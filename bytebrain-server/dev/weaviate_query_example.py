import langchain
import weaviate

langchain.verbose = True

# .with_additional({"uuid":"045c50ce-0fd5-5420-80f8-86d864ff76fe"})

if __name__ == "__main__":
    client = weaviate.Client(url="http://127.0.0.1:8080")
    result = client.query.get("Zio", ['text', 'uuid', 'source']).with_additional(['id']).do()
    # result = client.query.get("Zio", ['text', 'uuid']).with_where().do()
    print(result)