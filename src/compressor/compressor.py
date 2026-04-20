from abc import ABC, abstractmethod
from typing import List

from memory.models import Memory
from llm import LLM

from llm import Message


class Compressor(ABC):

    @abstractmethod
    def compress(self, items: List[Memory]) -> str:
        pass


class LLMCompressor(Compressor):

    def __init__(
        self,
        llm: LLM,
        system_prompt: str = "Summarize the following context into one single summary that captures signal and discards noise.",
    ):
        self.llm = llm
        self.system_prompt = system_prompt

    def compress(self, items: List[Memory]) -> str:

        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content="\n".join(m.content for m in items)),
        ]

        return self.llm.complete(messages).content
