# Retrospective

What we built here, what worked, what didn't, and what we would do differently. Written after
[Hacktoberfest Hack Day Istanbul × Hadith Tech](https://www.mlh.com/events/hacktoberfest-hack-day-istanbul-x-hadith-tech)
(24 October 2026).

## Context

Our team had one day to build a **friend-like AI companion**: a chat that feels human and warm, works in
Arabic and English, and can share Islamic guidance without inventing verses, hadith or fatwas.

We tried three approaches in parallel. This repo is one of them: Streamlit in front, a Python pipeline in the
middle, and Gemma 4 on the Gemini API behind it. A different attempt gave better conversations and became our
submission: [rfyq-wjht-mvp.replit.app](https://rfyq-wjht-mvp.replit.app).

## What this repo does

- **Skills as product rules** ([`skills/`](../skills)): ten Markdown files for core persona, safety, sources,
  Quran, hadith (disabled), fiqh, companionship, memory, follow-ups and privacy. Most go into the prompt;
  safety and source rules are also enforced in code.
- **Backend guardrails** ([`src/rafiq/engine.py`](../src/rafiq/engine.py), [`safety.py`](../src/rafiq/safety.py)):
  - a crisis input gate that skips the model entirely;
  - source-ID validation, so the model can only point at reviewed records and the backend renders the exact
    Arabic text;
  - an output gate with one corrective retry and a safe fallback.
- **Consent-aware features:** separate toggles for faith guidance, memory and check-ins, plus `/mydata`,
  `/pause` and `/forget`.
- **Streaming UI** with an animated mascot, built mobile-first ([`src/rafiq/brand.py`](../src/rafiq/brand.py),
  [`docs/brand/`](brand)).
- **Tests** for the pipeline and the safety rules (`pytest`).

## What worked

- **Keeping religious text out of the model's hands.** Making the model cite IDs, never quote text, held up
  well. Validation in code catches made-up IDs.
- **Writing skills as Markdown.** Non-developers on the team could read and edit the rules.
- **The crisis path.** It is deterministic and testable, and it never depends on the model.

## What didn't

| Problem | What we saw | Why we think it happened |
|---|---|---|
| Robotic replies | Short, formulaic, "assistant-like" answers instead of a friend talking | The prompt piles rules on top of the persona, and a strict output format and a length cap push towards safe, generic text |
| Speed and reliability | Long waits; frequent `500 INTERNAL` from Gemma 4 | A large model, a long prompt every turn, no caching, and Gemma on the Gemini API lacks system instructions and JSON mode |
| Arabic quality | Arabic, especially dialects, clearly weaker than English | Most of the prompt is in English; there are no Arabic examples and no dialect-specific evaluation |
| UI/UX | Works, but feels like a demo rather than an app | Streamlit reruns the whole script on every interaction, and custom chat UI has to fight its components and CSS |
| Thin architecture | Quality depends almost entirely on one prompt | No retrieval, no conversation state beyond the transcript, no evaluation loop, no per-turn control of the model |

## Lessons

1. **A companion is a product, not a prompt.** Human-like conversation needs state, memory and evaluation
   that a system prompt can't provide.
2. **Enforce in code, inspire in the prompt.** Safety and sources belong in code (this worked). Personality
   belongs in a short prompt with examples, not in a long list of rules.
3. **Test the target language first.** We should have built an Arabic evaluation set on day one.
4. **Pick the UI stack for the experience.** For a mobile chat, a real frontend (web or native) talking to an
   API backend beats a Python dashboard framework.

## What we would do next

If someone continues from this repo:

- **Backend service** (e.g. FastAPI) with sessions, a conversation-state machine (listen → reflect → suggest),
  and per-turn model settings.
- **Retrieval** over reviewed sources instead of putting the whole catalog in the prompt.
- **Evaluation:** a fixed set of Arabic and English conversations (see
  [`tests/scenarios/TEST_CASES.md`](../tests/scenarios/TEST_CASES.md)), scored for warmth, safety and accuracy
  on every change.
- **A proper classifier** for crisis detection instead of keywords, reviewed by professionals.
- **A real chat frontend** (React or Flutter), keeping the brand identity in `docs/brand/`.
- **Model choice by measurement:** compare latency and Arabic quality across models before choosing one.
