from datetime import datetime, timedelta, timezone
from typing import Optional

from memory.enums import Scope, Layer
from memory.models import Memory


def seed_memories(
    session,
    agent: Optional[str],
    scope: Scope,
    layer: Layer,
    count: int,
    content_prefix: str = "test_content",
):
    base_time = datetime.now(timezone.utc)
    for i in range(count):
        memory = Memory(
            agent=agent,
            scope=scope,
            layer=layer,
            content=f"{content_prefix}_{i}",
            created_at=base_time + timedelta(microseconds=i + 1),
        )
        session.add(memory)
