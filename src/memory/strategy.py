from abc import ABC, abstractmethod

from sqlmodel import Session

from memory.enums import Scope
from memory.models import Memory
from memory.repository import count_hot, get_last_n_hot


class Strategy(ABC):
    @abstractmethod
    def read(self, session: Session, scope: Scope, agent: str | None) -> list[Memory]:
        pass

    @abstractmethod
    def should_rebuild(self, session: Session, scope: Scope, agent: str | None) -> bool:
        pass


class MaxN(Strategy):
    def __init__(self, n: int):
        self.n = n

    def read(self, session: Session, scope: Scope, agent: str | None) -> list[Memory]:

        return get_last_n_hot(session, scope, agent, self.n)

    def should_rebuild(self, session: Session, scope: Scope, agent: str | None) -> bool:

        return count_hot(session, scope, agent) >= self.n
