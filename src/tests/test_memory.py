from uuid import UUID

from sqlmodel import select

from memory.models import Memory
from memory.enums import Scope, Layer
from memory.strategy import MaxN
from tests.seeders import seed_memories


def test_save_model_persists_fields(session):

    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.COLD, count=1
    )

    memory = session.exec(select(Memory)).one()

    assert isinstance(memory.id, UUID)
    assert memory.created_at is not None
    assert memory.updated_at is not None
    assert memory.agent == "test_agent"
    assert memory.scope == Scope.AGENT
    assert memory.layer == Layer.COLD
    assert memory.content == "test_content_0"


def test_max_n_read_returns_last_n_ordered_desc(session):

    # Create 5 hot memories for the same agent and scope
    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.HOT, count=5
    )

    # Create 2 cold memories for the same agent and scope
    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.COLD, count=2
    )

    strategy = MaxN(n=3)

    memories = strategy.read(session, Scope.AGENT, "test_agent")

    assert len(memories) == 3
    assert memories[0].content == "test_content_4" and memories[0].layer == Layer.HOT
    assert memories[1].content == "test_content_3" and memories[1].layer == Layer.HOT
    assert memories[2].content == "test_content_2" and memories[2].layer == Layer.HOT


def test_max_n_read_returns_empty_list_if_no_hot_memories(session):

    # Create 2 cold memories for the same agent and scope
    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.COLD, count=2
    )

    strategy = MaxN(n=3)

    memories = strategy.read(session, Scope.AGENT, "test_agent")

    assert len(memories) == 0


def test_max_n_should_rebuild_returns_true_when_exactly_n_hot_memories(session):

    strategy = MaxN(n=3)

    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.HOT, count=3
    )
    assert strategy.should_rebuild(session, Scope.AGENT, "test_agent") is True


def test_max_n_should_rebuild_returns_true_when_more_than_n_hot_memories(session):

    strategy = MaxN(n=3)

    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.HOT, count=5
    )
    assert strategy.should_rebuild(session, Scope.AGENT, "test_agent") is True


def test_max_n_should_rebuild_returns_false_if_less_than_n_hot_memories(session):

    strategy = MaxN(n=3)

    # Create 2 hot memories for the same agent and scope
    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.HOT, count=2
    )
    assert strategy.should_rebuild(session, Scope.AGENT, "test_agent") is False


def test_max_n_should_rebuild_returns_false_if_no_hot_memories(session):

    strategy = MaxN(n=3)

    # Create 10 cold memories for the same agent and scope
    seed_memories(
        session, agent="test_agent", scope=Scope.AGENT, layer=Layer.COLD, count=10
    )
    assert strategy.should_rebuild(session, Scope.AGENT, "test_agent") is False


def test_max_n_read_does_not_leak_across_agents(session):

    seed_memories(
        session,
        agent="coach",
        scope=Scope.AGENT,
        layer=Layer.HOT,
        count=3,
        content_prefix="coach",
    )
    seed_memories(
        session,
        agent="cto",
        scope=Scope.AGENT,
        layer=Layer.HOT,
        count=3,
        content_prefix="cto",
    )

    strategy = MaxN(n=10)
    memories = strategy.read(session, Scope.AGENT, "coach")

    assert len(memories) == 3
    assert all(m.agent == "coach" for m in memories)
    assert all(m.content.startswith("coach") for m in memories)


def test_max_n_read_does_not_leak_across_scopes(session):

    seed_memories(
        session,
        agent="coach",
        scope=Scope.AGENT,
        layer=Layer.HOT,
        count=3,
        content_prefix="agent",
    )
    seed_memories(
        session,
        agent=None,
        scope=Scope.GLOBAL,
        layer=Layer.HOT,
        count=3,
        content_prefix="global",
    )

    strategy = MaxN(n=10)
    memories = strategy.read(session, Scope.AGENT, "coach")

    assert len(memories) == 3
    assert all(m.scope == Scope.AGENT for m in memories)
    assert all(m.content.startswith("agent") for m in memories)


def test_max_n_read_returns_global_rows_when_scope_is_global(session):

    seed_memories(
        session,
        agent=None,
        scope=Scope.GLOBAL,
        layer=Layer.HOT,
        count=3,
        content_prefix="global",
    )

    strategy = MaxN(n=10)
    memories = strategy.read(session, Scope.GLOBAL, None)

    assert len(memories) == 3
    assert all(m.scope == Scope.GLOBAL for m in memories)
    assert all(m.agent is None for m in memories)


def test_max_n_should_rebuild_works_for_global_scope(session):

    strategy = MaxN(n=3)

    seed_memories(
        session, agent=None, scope=Scope.GLOBAL, layer=Layer.HOT, count=3
    )
    assert strategy.should_rebuild(session, Scope.GLOBAL, None) is True


def test_max_n_should_rebuild_isolates_counts_per_agent(session):

    strategy = MaxN(n=3)

    seed_memories(
        session,
        agent="coach",
        scope=Scope.AGENT,
        layer=Layer.HOT,
        count=2,
        content_prefix="coach",
    )
    seed_memories(
        session,
        agent="cto",
        scope=Scope.AGENT,
        layer=Layer.HOT,
        count=5,
        content_prefix="cto",
    )

    assert strategy.should_rebuild(session, Scope.AGENT, "coach") is False
    assert strategy.should_rebuild(session, Scope.AGENT, "cto") is True
