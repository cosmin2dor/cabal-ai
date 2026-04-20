from sqlmodel import Session, col, select

from memory.enums import Layer, Scope
from memory.models import Memory


def add_hot(session: Session, scope: Scope, agent: str | None, content: str) -> None:
    memory = Memory(
        agent=agent,
        scope=scope,
        layer=Layer.HOT,
        content=content,
    )

    session.add(memory)


def get_all_hot(session: Session, scope: Scope, agent: str | None) -> list[Memory]:
    return list(
        session.exec(
            select(Memory)
            .where(Memory.scope == scope)
            .where(Memory.agent == agent)
            .where(Memory.layer == Layer.HOT)
            .order_by(col(Memory.created_at).desc())
        ).all()
    )


def get_last_n_hot(session: Session, scope: Scope, agent: str | None, n: int) -> list[Memory]:
    return list(
        session.exec(
            select(Memory)
            .where(Memory.scope == scope)
            .where(Memory.agent == agent)
            .where(Memory.layer == Layer.HOT)
            .order_by(col(Memory.created_at).desc())
            .limit(n)
        ).all()
    )


def count_hot(session: Session, scope: Scope, agent: str | None) -> int:
    return len(
        session.exec(
            select(Memory)
            .where(Memory.scope == scope)
            .where(Memory.agent == agent)
            .where(Memory.layer == Layer.HOT)
        ).all()
    )


def clear_hot(session: Session, scope: Scope, agent: str | None) -> None:
    hot_memories = session.exec(
        select(Memory)
        .where(Memory.scope == scope)
        .where(Memory.agent == agent)
        .where(Memory.layer == Layer.HOT)
    ).all()

    for memory in hot_memories:
        session.delete(memory)


def get_cold(session: Session, scope: Scope, agent: str | None) -> Memory | None:
    return session.exec(
        select(Memory)
        .where(Memory.scope == scope)
        .where(Memory.agent == agent)
        .where(Memory.layer == Layer.COLD)
        .order_by(col(Memory.created_at).desc())
    ).first()


def set_cold(session: Session, scope: Scope, agent: str | None, content: str) -> None:
    cold_memory = get_cold(session, scope, agent)

    if cold_memory:
        cold_memory.content = content
    else:
        cold_memory = Memory(
            agent=agent,
            scope=scope,
            layer=Layer.COLD,
            content=content,
        )

    session.add(cold_memory)
