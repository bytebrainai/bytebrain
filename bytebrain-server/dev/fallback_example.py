from unittest.mock import patch
from openai.error import RateLimitError
from langchain.chat_models import ChatOpenAI, ChatAnthropic


# openai_llm = ChatOpenAI(max_retries=0)
# anthropic_llm = ChatAnthropic()
# llm = openai_llm.with_fallbacks([anthropic_llm])


def foo():
    return "Hello"


with patch('core.foo') as mock_foo:
    mock_foo.return_value = "Goodbye!"
