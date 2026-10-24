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
LLM (Gemma 4 via Gemini API), streamed:  reply text  <<<META>>>  JSON metadata (config/response.schema.json)
   │            └─ output_gate checks streamed text (80-char look-ahead) before it is shown
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
| 09 privacy | AI / third-party API notice on the welcome view + `/about /mydata /pause /resume /forget` (no age check in the demo) |

## Model notes

The model writes the reply first and the metadata after a `<<<META>>>` line, so the reply can stream. Gemma on the Gemini API has no system instructions, so the skills go in as the first user turn, followed by a primed model turn that shows the format. Other Gemini models get the skills as a system instruction. `parse_output` also accepts a whole-JSON answer as a fallback.
