from abc import ABC, abstractmethod
from typing import List

from memory.models import Memory


class Compressor(ABC):

    @abstractmethod
    def compress(self, items: List[Memory]) -> str:
        pass
