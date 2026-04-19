from memory.enums import Layer, Scope
from memory.models import Memory
from sqlmodel import Session, select

from typing import Optional


def add_hot(session: Session, scope: Scope, agent: Optional[str], content: str):
    memory = Memory(
        agent=agent,
        scope=scope,
        layer=Layer.HOT,
        content=content,
    )

    session.add(memory)


def get_all_hot(session: Session, scope: Scope, agent: Optional[str]) -> list[Memory]:
    return session.exec(
        select(Memory)
        .where(Memory.scope == scope)
        .where(Memory.agent == agent)
        .where(Memory.layer == Layer.HOT)
        .order_by(Memory.created_at.desc())
    ).all()


def get_last_n_hot(
    session: Session, scope: Scope, agent: Optional[str], n: int
) -> list[Memory]:
    return session.exec(
        select(Memory)
        .where(Memory.scope == scope)
        .where(Memory.agent == agent)
        .where(Memory.layer == Layer.HOT)
        .order_by(Memory.created_at.desc())
        .limit(n)
    ).all()


def count_hot(session: Session, scope: Scope, agent: Optional[str]) -> int:
    return len(
        session.exec(
            select(Memory)
            .where(Memory.scope == scope)
            .where(Memory.agent == agent)
            .where(Memory.layer == Layer.HOT)
        ).all()
    )


def set_cold(session: Session, scope: Scope, agent: Optional[str], content: str):
    memory = Memory(
        agent=agent,
        scope=scope,
        layer=Layer.COLD,
        content=content,
    )

    session.add(memory)
