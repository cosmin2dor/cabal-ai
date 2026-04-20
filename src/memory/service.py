from compressor import Compressor
from memory import repository, Memory
from memory.strategy import Strategy
from sqlmodel import Session

from memory.enums import Scope
from typing import Optional, Tuple, List


class MemoryService:
    def __init__(self, strategy: Strategy, compressor: Compressor):
        self.strategy = strategy
        self.compressor = compressor

    """
    Stores new content
    """

    def record(
        self, session: Session, scope: Scope, agent: Optional[str], content: str
    ):
        repository.add_hot(session, scope, agent, content)

        if self.strategy.should_rebuild(session, scope, agent):
            self.rebuild(session, scope, agent)

    """
    Compress hot → cold, clear hot. The compression flow.
    """

    def rebuild(
        self,
        session: Session,
        scope: Scope,
        agent: Optional[str],
    ):
        hot = self.strategy.read(session, scope, agent)
        cold = self.compressor.compress(hot)

        repository.set_cold(session, scope, agent, cold)
        repository.clear_hot(session, scope, agent)

    """
    Called when building an LLM prompt
    """

    def build_context(
        self, session: Session, scope: Scope, agent: Optional[str]
    ) -> Tuple[List[Memory], Optional[Memory]]:
        return (
            self.strategy.read(session, scope, agent),
            repository.get_cold(session, scope, agent),
        )
