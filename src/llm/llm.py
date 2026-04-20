from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List, Literal


@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class Completion:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLM(ABC):
    @abstractmethod
    def complete(self, messages: List[Message]) -> Completion:
        pass
