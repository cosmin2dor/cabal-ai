from compressor import Compressor
from typing import List

from memory.models import Memory
from llm import LLM, Message, Completion


class MockCompressor(Compressor):

    def __init__(self, output: str = "compressed_summary"):
        self.output = output
        self.calls: List[List[Memory]] = []

    def compress(self, items: List[Memory]) -> str:
        self.calls.append(items)
        return self.output


class MockLLM(LLM):

    def __init__(
        self,
        content: str = "mock response",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ):
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.calls: List[List[Message]] = []

    def complete(self, messages: List[Message]) -> Completion:
        self.calls.append(messages)
        return Completion(
            content=self.content,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.prompt_tokens + self.completion_tokens,
        )
