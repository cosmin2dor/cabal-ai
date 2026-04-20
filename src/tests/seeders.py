from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from memory.enums import Layer, Scope
from memory.models import Memory


def seed_memories(
    session: Session,
    agent: str | None,
    scope: Scope,
    layer: Layer,
    count: int,
    content_prefix: str = "test_content",
) -> None:
    base_time = datetime.now(UTC)
    for i in range(count):
        memory = Memory(
            agent=agent,
            scope=scope,
            layer=layer,
            content=f"{content_prefix}_{i}",
            created_at=base_time + timedelta(microseconds=i + 1),
        )
        session.add(memory)
