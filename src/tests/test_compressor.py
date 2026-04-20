from memory.models import Memory
from memory.enums import Scope, Layer
from compressor import LLMCompressor
from tests.mocks import MockLLM


def _hot(content: str) -> Memory:
    return Memory(agent=None, scope=Scope.GLOBAL, layer=Layer.HOT, content=content)


def test_compress_returns_llm_content():
    llm = MockLLM(content="summary")
    compressor = LLMCompressor(llm=llm)

    result = compressor.compress([_hot("msg_0"), _hot("msg_1")])

    assert result == "summary"


def test_compress_calls_llm_once():
    llm = MockLLM()
    compressor = LLMCompressor(llm=llm)

    compressor.compress([_hot("msg")])

    assert len(llm.calls) == 1


def test_compress_includes_all_memory_contents_in_prompt():
    llm = MockLLM()
    compressor = LLMCompressor(llm=llm)

    compressor.compress([_hot("alpha"), _hot("beta"), _hot("gamma")])

    sent = llm.calls[0]
    combined = "\n".join(m.content for m in sent)
    assert "alpha" in combined
    assert "beta" in combined
    assert "gamma" in combined


def test_compress_uses_custom_system_prompt():
    llm = MockLLM()
    compressor = LLMCompressor(llm=llm, system_prompt="You are a custom summarizer")

    compressor.compress([_hot("msg")])

    sent = llm.calls[0]
    combined = "\n".join(m.content for m in sent)
    assert "You are a custom summarizer" in combined
