# Now lets create a chain with the normal OpenAI model
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

prompt_template = """Instructions: You should always include a compliment in your response.

Question: Why did the {animal} cross the road?"""
prompt = PromptTemplate.from_template(prompt_template)
llm = OpenAI()
good_chain = prompt | llm

result = good_chain.invoke({"animal": "turtle"})
print(result)