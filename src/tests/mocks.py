from compressor import Compressor
from llm import LLM, Completion, Message
from memory.models import Memory


class MockCompressor(Compressor):
    def __init__(self, output: str = "compressed_summary"):
        self.output = output
        self.calls: list[list[Memory]] = []

    def compress(self, items: list[Memory]) -> str:
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
        self.calls: list[list[Message]] = []

    def complete(self, messages: list[Message]) -> Completion:
        self.calls.append(messages)
        return Completion(
            content=self.content,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.prompt_tokens + self.completion_tokens,
        )
