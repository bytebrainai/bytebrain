from abc import ABC
from typing import Any

from fastapi import WebSocket
from langchain.callbacks.base import AsyncCallbackHandler


class StreamingLLMCallbackHandler(AsyncCallbackHandler, ABC):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        print(token, end="")
        resp = {"token": token, "completed": False}
        await self.websocket.send_json(resp)
