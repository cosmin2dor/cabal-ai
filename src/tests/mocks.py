from compressor import Compressor
from typing import List

from memory.models import Memory


class MockCompressor(Compressor):

    def __init__(self, output: str = "compressed_summary"):
        self.output = output
        self.calls: List[List[Memory]] = []

    def compress(self, items: List[Memory]) -> str:
        self.calls.append(items)
        return self.output
