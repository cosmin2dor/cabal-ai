from abc import ABC, abstractmethod

from sqlmodel import Session

from memory.models import Memory
from memory.enums import Scope
from memory.repository import get_last_n_hot, count_hot
from typing import Optional, List


class Strategy(ABC):

    @abstractmethod
    def read(
        self, session: Session, scope: Scope, agent: Optional[str]
    ) -> List[Memory]:
        pass

    @abstractmethod
    def should_rebuild(
        self, session: Session, scope: Scope, agent: Optional[str]
    ) -> bool:
        pass


class MaxN(Strategy):

    def __init__(self, n: int):
        self.n = n

    def read(
        self, session: Session, scope: Scope, agent: Optional[str]
    ) -> List[Memory]:

        return get_last_n_hot(session, scope, agent, self.n)

    def should_rebuild(
        self, session: Session, scope: Scope, agent: Optional[str]
    ) -> bool:

        return count_hot(session, scope, agent) >= self.n
