from abc import ABC, abstractmethod

from llm import LLM, Message
from memory.models import Memory


class Compressor(ABC):
    @abstractmethod
    def compress(self, items: list[Memory]) -> str:
        pass


class LLMCompressor(Compressor):
    def __init__(
        self,
        llm: LLM,
        system_prompt: str = "Summarize the following context into one single summary that captures"
        " signal and discards noise.",
    ):
        self.llm = llm
        self.system_prompt = system_prompt

    def compress(self, items: list[Memory]) -> str:

        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content="\n".join(m.content for m in items)),
        ]

        return self.llm.complete(messages).content
