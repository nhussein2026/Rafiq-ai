"""Rafiq demo pipeline:

inbound -> safety input gate -> LLM proposal (JSON) -> source-ID validation
-> output safety gate -> render verified sources -> pending memory/follow-up
"""
import json
import os
import re
from dataclasses import dataclass, field

from . import safety
from .config import CONFIG_DIR, DEFAULT_MODEL, PROMPT_SKILLS, SKILLS_DIR, SOURCES_FILE

FALLBACK_REPLY = {
    "en": "I want to be careful here. I can't verify that from the approved sources, "
          "so I won't quote it. A qualified scholar can help with the details. "
          "How are you feeling about it?",
    "ar": "أريد أن أكون حذرًا هنا. لا أستطيع التحقق من ذلك من المصادر المعتمدة، لذلك لن أقتبسه. "
          "يمكن لعالم مؤهل أن يساعدك في التفاصيل. كيف تشعر حيال ذلك؟",
}


def load_sources() -> dict:
    records = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    return {r["id"]: r for r in records if r.get("review_status") == "approved"}


def build_system_prompt(settings: dict, sources: dict, memories: list[str]) -> str:
    parts = [(SKILLS_DIR / name).read_text(encoding="utf-8") for name in PROMPT_SKILLS]
    schema = (CONFIG_DIR / "response.schema.json").read_text(encoding="utf-8")

    if settings["faith"]:
        catalog = "\n".join(
            f"- {sid} ({r['kind']} {r.get('quran_verse_id', '')}): {r['reviewed_context_summary']}"
            for sid, r in sources.items()
        )
        faith_block = (
            "Faith guidance: ENABLED by user.\n"
            "Approved source catalog (you may ONLY cite these IDs in `source_ids`; "
            "never write the verse text yourself, the backend renders it):\n" + catalog
        )
    else:
        faith_block = (
            "Faith guidance: DISABLED by user. Do not cite sources or bring up religious "
            "content unless the user asks; if they ask, say faith guidance is turned off."
        )

    runtime = f"""
# Runtime context (from backend)

{faith_block}

Hadith skill: DISABLED (no approved hadith records). Never quote or grade hadith.
Scholar/Islamweb records: NONE approved. Never attribute content to Islamweb or cite fatwa numbers.
Personal memory: {"ENABLED" if settings["memory"] else "DISABLED - memory_proposals must be []"}.
Proactive follow-ups: {"ENABLED" if settings["followups"] else "DISABLED - followup_proposal must be null"}.
Approved memories about this user: {json.dumps(memories, ensure_ascii=False) if memories else "none"}

# Output format
Respond with ONLY a JSON object matching this schema, no markdown fences:
{schema}
The `reply` field is what the user sees. Keep it short (2-5 sentences),
in the user's language, with at most one question.
"""
    return "\n\n".join(parts) + "\n" + runtime


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


@dataclass
class Turn:
    reply: str
    lang: str
    mode: str = "normal"  # normal | crisis | corrected
    sources: list[dict] = field(default_factory=list)
    rejected_source_ids: list[str] = field(default_factory=list)
    memory_proposals: list[dict] = field(default_factory=list)
    followup_proposal: dict | None = None
    gate_flags: list[str] = field(default_factory=list)
    raw: dict | None = None


class RafiqEngine:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model or DEFAULT_MODEL
        self.sources = load_sources()
        self._client = None

    def _call_model(self, system_prompt: str, history: list[dict]) -> dict:
        from google import genai
        from google.genai import types

        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        contents = [
            types.Content(role="user" if m["role"] == "user" else "model",
                          parts=[types.Part(text=m["content"])])
            for m in history
        ]
        if self.model.startswith("gemma"):
            # Gemma on the Gemini API supports neither system instructions nor JSON mode.
            contents.insert(0, types.Content(role="user", parts=[types.Part(text=system_prompt)]))
            contents.insert(1, types.Content(role="model", parts=[types.Part(text='{"reply": "Understood."}')]))
            config = types.GenerateContentConfig(temperature=0.6)
        else:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.6,
            )
        resp = self._client.models.generate_content(model=self.model, contents=contents, config=config)
        return _parse_json(resp.text)

    def respond(self, history: list[dict], settings: dict, memories: list[str]) -> Turn:
        user_text = history[-1]["content"]
        lang = safety.detect_language(user_text)

        # 1. Independent input gate: crisis bypasses the LLM entirely.
        if safety.input_gate(user_text) == "crisis":
            return Turn(reply=safety.CRISIS_REPLY[lang], lang=lang, mode="crisis",
                        gate_flags=["input_crisis"])

        system_prompt = build_system_prompt(settings, self.sources, memories)
        data = self._call_model(system_prompt, history)
        turn = self._validate(data, settings, lang)

        # 2. Output gate: one corrective retry, then a safe fallback.
        if turn.gate_flags:
            retry_history = history + [
                {"role": "model", "content": json.dumps(data, ensure_ascii=False)},
                {"role": "user", "content": (
                    "[BACKEND] Your reply was blocked for: " + ", ".join(turn.gate_flags) +
                    ". Rewrite it without quoting scripture, hadith or fatwas yourself and "
                    "without attachment language. Cite only approved source_ids. JSON only."
                )},
            ]
            data = self._call_model(system_prompt, retry_history)
            flags = turn.gate_flags
            turn = self._validate(data, settings, lang)
            if turn.gate_flags:
                turn.reply = FALLBACK_REPLY[lang]
                turn.sources = []
            turn.mode = "corrected"
            turn.gate_flags = flags + [f"retry:{f}" for f in turn.gate_flags]
        return turn

    def _validate(self, data: dict, settings: dict, lang: str) -> Turn:
        reply = str(data.get("reply", "")).strip() or FALLBACK_REPLY[lang]
        turn = Turn(reply=reply, lang=lang, raw=data)

        for sid in data.get("source_ids") or []:
            if settings["faith"] and sid in self.sources:
                turn.sources.append(self.sources[sid])
            else:
                turn.rejected_source_ids.append(sid)

        if settings["memory"]:
            turn.memory_proposals = [
                m for m in (data.get("memory_proposals") or [])
                if isinstance(m, dict) and m.get("summary")
            ]
        fu = data.get("followup_proposal")
        if settings["followups"] and isinstance(fu, dict) and fu.get("topic"):
            turn.followup_proposal = fu

        turn.gate_flags = safety.output_gate(reply)
        return turn
