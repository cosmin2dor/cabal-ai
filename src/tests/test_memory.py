import pytest

from uuid import UUID

from sqlmodel import select

from memory.models import Memory
from memory.enums import Scope, Layer
from memory.repository import get_cold, count_hot
from memory.service import MemoryService
from memory.strategy import MaxN
from tests.seeders import seed_memories
from tests.mocks import MockCompressor


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

    seed_memories(session, agent=None, scope=Scope.GLOBAL, layer=Layer.HOT, count=3)
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


@pytest.fixture()
def compressor():
    return MockCompressor(output="compressed_summary")


@pytest.fixture()
def service(compressor):
    return MemoryService(strategy=MaxN(n=3), compressor=compressor)


def test_rebuild_compresses_hot_and_stores_cold(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)

    service.rebuild(session, Scope.AGENT, "test_agent")

    cold = get_cold(session, Scope.AGENT, "test_agent")
    assert cold is not None
    assert cold.content == "compressed_summary"


def test_rebuild_clears_hot_after_storing_cold(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)

    service.rebuild(session, Scope.AGENT, "test_agent")

    assert count_hot(session, Scope.AGENT, "test_agent") == 0


def test_rebuild_passes_hot_contents_to_compressor(session, service, compressor):
    seed_memories(
        session, "test_agent", Scope.AGENT, Layer.HOT, 3, content_prefix="msg"
    )

    service.rebuild(session, Scope.AGENT, "test_agent")

    assert len(compressor.calls) == 1
    passed = compressor.calls[0]
    assert len(passed) == 3
    assert all(c.content.startswith("msg") for c in passed)


def test_rebuild_does_not_affect_other_agent(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)
    seed_memories(session, "other_agent", Scope.AGENT, Layer.HOT, 3)

    service.rebuild(session, Scope.AGENT, "test_agent")

    assert count_hot(session, Scope.AGENT, "other_agent") == 3
    assert get_cold(session, Scope.AGENT, "other_agent") is None


def test_rebuild_does_not_affect_other_scope(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)

    service.rebuild(session, Scope.AGENT, "test_agent")

    assert count_hot(session, Scope.GLOBAL, None) == 3
    assert get_cold(session, Scope.GLOBAL, None) is None


def test_record_adds_hot_row(session, service):
    service.record(session, Scope.AGENT, "test_agent", "new content")

    assert count_hot(session, Scope.AGENT, "test_agent") == 1


def test_record_triggers_rebuild_at_threshold(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 2)

    service.record(session, Scope.AGENT, "test_agent", "trigger")

    cold = get_cold(session, Scope.AGENT, "test_agent")
    assert cold is not None
    assert count_hot(session, Scope.AGENT, "test_agent") == 0


def test_record_does_not_rebuild_below_threshold(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 1)

    service.record(session, Scope.AGENT, "test_agent", "below threshold")

    assert get_cold(session, Scope.AGENT, "test_agent") is None


def test_record_does_not_affect_other_agent(session, service):
    seed_memories(session, "other_agent", Scope.AGENT, Layer.HOT, 2)

    service.record(session, Scope.AGENT, "test_agent", "isolated")

    assert count_hot(session, Scope.AGENT, "other_agent") == 2
    assert get_cold(session, Scope.AGENT, "other_agent") is None


def test_build_context_returns_hot_rows_and_cold(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)
    service.rebuild(session, Scope.AGENT, "test_agent")

    seed_memories(
        session, "test_agent", Scope.AGENT, Layer.HOT, 1, content_prefix="new"
    )

    hot, cold = service.build_context(session, Scope.AGENT, "test_agent")

    assert len(hot) == 1
    assert cold is not None
    assert cold.content == "compressed_summary"


def test_build_context_does_not_bleed_across_agents(session, service):
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)
    service.rebuild(session, Scope.AGENT, "test_agent")

    seed_memories(session, "other_agent", Scope.AGENT, Layer.HOT, 1)

    hot, cold = service.build_context(session, Scope.AGENT, "other_agent")

    assert len(hot) == 1
    assert cold is None


# --- GLOBAL scope ---


def test_rebuild_global_stores_cold_with_agent_none(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)

    service.rebuild(session, Scope.GLOBAL, None)

    cold = get_cold(session, Scope.GLOBAL, None)
    assert cold is not None
    assert cold.agent is None
    assert cold.content == "compressed_summary"


def test_rebuild_global_clears_hot(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)

    service.rebuild(session, Scope.GLOBAL, None)

    assert count_hot(session, Scope.GLOBAL, None) == 0


def test_record_global_adds_hot_row(session, service):
    service.record(session, Scope.GLOBAL, None, "global content")

    assert count_hot(session, Scope.GLOBAL, None) == 1


def test_record_global_triggers_rebuild_at_threshold(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 2)

    service.record(session, Scope.GLOBAL, None, "trigger")

    cold = get_cold(session, Scope.GLOBAL, None)
    assert cold is not None
    assert count_hot(session, Scope.GLOBAL, None) == 0


def test_rebuild_global_does_not_affect_agent_scope(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)
    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 3)

    service.rebuild(session, Scope.GLOBAL, None)

    assert count_hot(session, Scope.AGENT, "test_agent") == 3
    assert get_cold(session, Scope.AGENT, "test_agent") is None


def test_build_context_global_returns_hot_and_cold(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)
    service.rebuild(session, Scope.GLOBAL, None)

    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 1, content_prefix="new")

    hot, cold = service.build_context(session, Scope.GLOBAL, None)

    assert len(hot) == 1
    assert cold is not None
    assert cold.content == "compressed_summary"


def test_build_context_global_does_not_bleed_into_agent_scope(session, service):
    seed_memories(session, None, Scope.GLOBAL, Layer.HOT, 3)
    service.rebuild(session, Scope.GLOBAL, None)

    seed_memories(session, "test_agent", Scope.AGENT, Layer.HOT, 1)

    hot, cold = service.build_context(session, Scope.AGENT, "test_agent")

    assert len(hot) == 1
    assert cold is None
