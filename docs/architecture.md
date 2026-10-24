# Architecture

```
user message
   │
   ▼
safety.input_gate ──crisis──► fixed human-help reply (no LLM, no verses)
   │ ok
   ▼
build_system_prompt  ← skills/*.md + runtime context (toggles, approved catalog, memories)
   │
   ▼
LLM (Gemini / Gemma) → JSON proposal (config/response.schema.json)
   │
   ▼
_validate: source_ids ∈ approved catalog? memory/follow-up allowed by toggles?
   │
   ▼
safety.output_gate ──flagged──► one corrective retry ──still flagged──► safe fallback
   │ pass
   ▼
UI renders reply + exact Arabic from data/ + pending memory / simulated check-in
```

## Where each skill lives

| Skill | Enforcement |
|---|---|
| 00 core, 05 fiqh, 06 companion | Loaded into the system prompt |
| 01 safety | Code: `src/rafiq/safety.py` (keyword-based; not a validated classifier) |
| 02 sources / 03 quran | Prompt + code: only IDs from `data/approved_sources.json` are rendered; others rejected |
| 04 hadith | Disabled (`config/policy.yaml`) |
| 07 memory | Model proposes; user approves in the sidebar; session-only |
| 08 follow-ups | Only when toggled on; simulated, nothing is sent |
| 09 privacy | Consent screen + `/about /mydata /pause /resume /forget` |

## Model notes

Gemini models get the skills as a system instruction and use JSON mode. Gemma models on the Gemini API support neither, so the skills are sent as the first user turn and JSON is parsed from text.
