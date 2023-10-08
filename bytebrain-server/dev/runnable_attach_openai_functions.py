from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

functions = [
    {
      "name": "solver",
      "description": "Formulates and solves an equation",
      "parameters": {
        "type": "object",
        "properties": {
          "equation": {
            "type": "string",
            "description": "The algebraic expression of the equation"
          },
          "solution": {
            "type": "string",
            "description": "The solution to the equation"
          }
        },
        "required": ["equation", "solution"]
      }
    }
  ]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Write out the following equation using algebraic symbols then solve it. Use the format\n\nEQUATION:...\nSOLUTION:...\n\n"),
        ("human", "{equation_statement}")
    ]
)
model = ChatOpenAI(model="gpt-4", temperature=0)
runnable = {"equation_statement": RunnablePassthrough()} | prompt | model.bind(function_call={"name": "solver"}, functions=functions)

print(runnable.invoke("x raised to the third plus seven equals 12"))