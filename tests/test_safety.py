import pytest

from rafiq import safety


@pytest.mark.parametrize("text", ["I want to kill myself", "thinking about suicide", "بدي موت", "أريد أن أموت"])
def test_input_gate_flags_crisis(text):
    assert safety.input_gate(text) == "crisis"


@pytest.mark.parametrize("text", ["I'm stressed about exams", "كيف حالك؟", "this exam is killing me slowly"])
def test_input_gate_passes_ordinary_messages(text):
    assert safety.input_gate(text) == "ok"


def test_output_gate_blocks_unsourced_hadith():
    assert "unsourced_religious_quote" in safety.output_gate("The Prophet said be patient. Narrated by Muslim.")


def test_output_gate_blocks_attachment_language():
    assert "attachment_language" in safety.output_gate("Don't go, I need you.")


def test_output_gate_passes_supportive_reply():
    assert safety.output_gate("That sounds hard. What feels heaviest right now?") == []


@pytest.mark.parametrize("text,lang", [("hello there", "en"), ("مرحبا كيف حالك", "ar")])
def test_detect_language(text, lang):
    assert safety.detect_language(text) == lang
