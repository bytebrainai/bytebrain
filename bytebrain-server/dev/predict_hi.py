from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

llm = OpenAI()
chat_model = ChatOpenAI()

r1 = llm.predict("Hello!")
print(r1)

print("----------------")

r2 = chat_model.predict("Hello!")
print(r2)