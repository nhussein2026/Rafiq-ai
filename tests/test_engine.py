import pytest

from rafiq import __version__, engine
from rafiq.engine import RafiqEngine

ALL_ON = {"faith": True, "memory": True, "followups": True}
ALL_OFF = {"faith": False, "memory": False, "followups": False}


class FakeEngine(RafiqEngine):
    """Replays canned model outputs instead of calling the API."""

    def __init__(self, outputs):
        super().__init__(api_key="test", model="gemini-test")
        self.outputs = list(outputs)
        self.calls = 0

    def _call_model(self, system_prompt, history):
        self.calls += 1
        return self.outputs.pop(0)


def ask(eng, text, settings=ALL_ON):
    return eng.respond([{"role": "user", "content": text}], settings, [])


def reply(text, source_ids=(), memory=(), followup=None):
    return {"reply": text, "source_ids": list(source_ids),
            "memory_proposals": list(memory), "followup_proposal": followup}


def test_version_is_semver():
    assert len(__version__.split(".")) == 3


def test_approved_sources_load():
    assert "q-94-5" in engine.load_sources()


def test_crisis_bypasses_model():
    eng = FakeEngine([])
    turn = ask(eng, "I want to kill myself")
    assert turn.mode == "crisis" and eng.calls == 0 and turn.sources == []


def test_unknown_source_id_is_rejected():
    turn = ask(FakeEngine([reply("Here is comfort.", ["q-94-5", "q-999-1"])]), "I'm sad")
    assert [s["id"] for s in turn.sources] == ["q-94-5"]
    assert turn.rejected_source_ids == ["q-999-1"]


def test_sources_rejected_when_faith_disabled():
    turn = ask(FakeEngine([reply("Hi.", ["q-94-5"])]), "I'm sad", ALL_OFF)
    assert turn.sources == [] and turn.rejected_source_ids == ["q-94-5"]


def test_memory_and_followup_dropped_without_consent():
    out = reply("Nice goal!", memory=[{"kind": "goal", "summary": "read daily"}],
                followup={"topic": "reading", "suggested_delay_days": 2})
    turn = ask(FakeEngine([out]), "I want to read daily", ALL_OFF)
    assert turn.memory_proposals == [] and turn.followup_proposal is None


def test_fabricated_hadith_retried_then_falls_back():
    bad = reply("The Prophet said patience is light. Narrated by Muslim.")
    eng = FakeEngine([bad, bad])
    turn = ask(eng, "Tell me a hadith")
    assert eng.calls == 2 and turn.mode == "corrected"
    assert turn.reply == engine.FALLBACK_REPLY["en"]


def test_prompt_respects_disabled_faith():
    prompt = engine.build_system_prompt(ALL_OFF, engine.load_sources(), [])
    assert "Faith guidance: DISABLED" in prompt and "q-94-5" not in prompt


@pytest.mark.parametrize("raw", ['{"reply": "hi"}', '```json\n{"reply": "hi"}\n```', 'Sure! {"reply": "hi"}'])
def test_parse_json_tolerates_wrappers(raw):
    assert engine._parse_json(raw) == {"reply": "hi"}
