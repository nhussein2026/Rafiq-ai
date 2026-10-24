"""Rafiq demo pipeline:

inbound -> safety input gate -> LLM proposal (reply text + JSON metadata) -> source-ID validation
-> output safety gate -> render verified sources -> pending memory/follow-up

The reply is written before the metadata so it can be streamed; the output gate checks the
streamed text as it arrives (see ReplyStream).
"""
import json
import os
import re
import time
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


# The model writes the reply, then this marker on its own line, then the JSON metadata.
META_MARK = "<<<META>>>"
# Streamed text lags this many characters behind the model so the output gate sees a pattern's
# following context before any of it is displayed.
STREAM_HOLDBACK = 80
# Yielded by ReplyStream when text already shown must be withdrawn (gate tripped or rewritten).
RESET = object()
RETRYABLE = (429, 500, 502, 503, 504)
EMPTY_META = '{"source_ids": [], "memory_proposals": [], "followup_proposal": null}'

_CLIENTS: dict[str, object] = {}  # one HTTP client per API key, reused across messages


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
First write the reply the user sees, as plain text: short (2-5 sentences), in the user's
language, with at most one question.
Then write {META_MARK} on its own line, followed by ONLY a JSON object (no markdown fences)
with every field of this schema except `reply`:
{schema}
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


def parse_output(text: str) -> dict:
    """Split model output into the reply and its metadata; tolerate a whole-JSON answer too."""
    text = text.strip()
    if META_MARK in text:
        reply, meta = text.split(META_MARK, 1)
        try:
            data = _parse_json(meta)
        except json.JSONDecodeError:
            data = {}
        data = data if isinstance(data, dict) else {}
        data["reply"] = reply.strip()
        return data
    try:
        data = _parse_json(text)
        if isinstance(data, dict) and "reply" in data:
            return data
    except json.JSONDecodeError:
        pass
    return {"reply": text}


def _format_output(data: dict) -> str:
    """Inverse of parse_output, for replaying a model turn in the history."""
    meta = {k: v for k, v in data.items() if k != "reply"}
    return f"{data.get('reply', '')}\n{META_MARK}\n{json.dumps(meta, ensure_ascii=False)}"


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

    @property
    def _client(self):
        from google import genai

        if self.api_key not in _CLIENTS:
            _CLIENTS[self.api_key] = genai.Client(api_key=self.api_key)
        return _CLIENTS[self.api_key]

    def _request(self, system_prompt: str, history: list[dict]):
        from google.genai import types

        contents = [
            types.Content(role="user" if m["role"] == "user" else "model",
                          parts=[types.Part(text=m["content"])])
            for m in history
        ]
        # Short replies plus metadata; the cap stops a slow model from rambling.
        config = types.GenerateContentConfig(temperature=0.6, max_output_tokens=1024)
        if self.model.startswith("gemma"):
            # Gemma on the Gemini API has no system instructions: send the prompt as the first turn.
            primer = f"Understood.\n{META_MARK}\n{EMPTY_META}"
            contents.insert(0, types.Content(role="user", parts=[types.Part(text=system_prompt)]))
            contents.insert(1, types.Content(role="model", parts=[types.Part(text=primer)]))
        else:
            config.system_instruction = system_prompt
        return contents, config

    def _call_model(self, system_prompt: str, history: list[dict]) -> dict:
        """Retry Gemini's transient failures (5xx, 429) with a short backoff."""
        from google.genai import errors

        contents, config = self._request(system_prompt, history)
        for attempt in range(3):
            try:
                resp = self._client.models.generate_content(model=self.model, contents=contents, config=config)
                return parse_output(resp.text or "")
            except errors.APIError as e:
                if e.code not in RETRYABLE or attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    def _stream_model(self, system_prompt: str, history: list[dict]):
        """Yield raw text chunks; transient failures are retried only before the first chunk."""
        from google.genai import errors

        contents, config = self._request(system_prompt, history)
        for attempt in range(3):
            started = False
            try:
                for chunk in self._client.models.generate_content_stream(
                        model=self.model, contents=contents, config=config):
                    if chunk.text:
                        started = True
                        yield chunk.text
                return
            except errors.APIError as e:
                if started or e.code not in RETRYABLE or attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    def _crisis_turn(self, user_text: str) -> Turn | None:
        """Independent input gate: crisis bypasses the LLM entirely."""
        if safety.input_gate(user_text) != "crisis":
            return None
        lang = safety.detect_language(user_text)
        return Turn(reply=safety.CRISIS_REPLY[lang], lang=lang, mode="crisis", gate_flags=["input_crisis"])

    def respond(self, history: list[dict], settings: dict, memories: list[str]) -> Turn:
        if crisis := self._crisis_turn(history[-1]["content"]):
            return crisis
        system_prompt = build_system_prompt(settings, self.sources, memories)
        data = self._call_model(system_prompt, history)
        return self._finish(data, system_prompt, history, settings)

    def stream(self, history: list[dict], settings: dict, memories: list[str]) -> "ReplyStream":
        return ReplyStream(self, history, settings, memories)

    def _finish(self, data: dict, system_prompt: str, history: list[dict], settings: dict) -> Turn:
        lang = safety.detect_language(history[-1]["content"])
        turn = self._validate(data, settings, lang)

        # 2. Output gate: one corrective retry, then a safe fallback.
        if turn.gate_flags:
            retry_history = history + [
                {"role": "model", "content": _format_output(data)},
                {"role": "user", "content": (
                    "[BACKEND] Your reply was blocked for: " + ", ".join(turn.gate_flags) +
                    ". Rewrite it without quoting scripture, hadith or fatwas yourself and "
                    "without attachment language. Cite only approved source_ids. Same format: reply, "
                    f"then {META_MARK}, then the JSON."
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


class ReplyStream:
    """Iterate for reply text as it arrives; `turn` holds the validated Turn afterwards.

    Text is checked by the output gate before it is shown. If the gate trips, RESET is
    yielded and the reply goes through the same corrective retry as a non-streamed one.
    """

    def __init__(self, engine: RafiqEngine, history: list[dict], settings: dict, memories: list[str]):
        self.engine, self.history, self.settings, self.memories = engine, history, settings, memories
        self.turn: Turn | None = None

    def __iter__(self):
        eng = self.engine
        if crisis := eng._crisis_turn(self.history[-1]["content"]):
            self.turn = crisis
            yield crisis.reply
            return

        system_prompt = build_system_prompt(self.settings, eng.sources, self.memories)
        raw, shown = "", ""
        chunks = eng._stream_model(system_prompt, self.history)
        for chunk in chunks:
            raw += chunk
            reply = raw.split(META_MARK, 1)[0].lstrip()
            if safety.output_gate(reply):
                chunks.close()
                if shown:  # withdraw it now; the rewrite below can take a few seconds
                    yield RESET
                    shown = ""
                break
            if reply[:1] in "{`":  # model ignored the format and wrote JSON: show it once parsed
                continue
            safe = reply.rstrip() if META_MARK in raw else reply[:max(0, len(reply) - STREAM_HOLDBACK)]
            if len(safe) > len(shown):
                yield safe[len(shown):]
                shown = safe

        self.turn = eng._finish(parse_output(raw), system_prompt, self.history, self.settings)
        final = self.turn.reply
        if final.startswith(shown):
            if final[len(shown):]:
                yield final[len(shown):]
        else:
            yield RESET
            yield final
