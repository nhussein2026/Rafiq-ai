# 🌙 Rafiq · رفيق

[![CI](https://github.com/nhussein2026/Rafiq-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/nhussein2026/Rafiq-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rafiq-ai-elpr2wxpebscy9wrsbywom.streamlit.app/)
[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-orange)](https://hacktoberfest.com)

**Rafiq** (Arabic for *companion*) is an open-source AI wellbeing companion for Arabic and English speakers. It listens, supports reflection and small habits, and — only when the user opts in — shares **verified** Sunni Islamic guidance from reviewed sources.

Rafiq is an AI. It is **not** a human, scholar, mufti, therapist or doctor.

**🔗 Live preview:** [rafiq-ai-elpr2wxpebscy9wrsbywom.streamlit.app](https://rafiq-ai-elpr2wxpebscy9wrsbywom.streamlit.app/)

> ⚠️ **Status: demo / MVP.** The safety gate is keyword-based, not a validated crisis classifier. Do not use with vulnerable users.

<p align="center"><img src="assets/mascot.png" width="160" alt="Rafiq mascot"></p>

Rafiq is designed **phone-first**: it is headed for a mobile app, and this Streamlit demo is built and tested for phone screens before desktop.

## Why Rafiq is different

Most chatbots answer religious questions from model memory, which leads to fabricated verses, hadith and fatwas. Rafiq instead enforces rules in the **backend**:

- 🛡️ **Safety first:** crisis messages skip the LLM and get a fixed human-help response with no verses.
- 📖 **No fabricated scripture:** the model can only cite IDs from an approved catalog; the backend renders the exact Arabic text.
- 🚫 **No autonomous fatwa:** individual rulings are referred to a qualified scholar.
- 🔒 **Privacy by design:** third-party API disclosure on the welcome screen, separate toggles for faith guidance, memory and check-ins, and `/mydata` `/pause` `/forget` commands.

## Quick start

```bash
git clone https://github.com/nhussein2026/Rafiq-ai.git && cd Rafiq-ai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env    # add your key from https://aistudio.google.com/apikey
set -a && source .env && set +a
streamlit run streamlit_app.py
```

Run tests: `pytest` · Lint: `ruff check .`

### Gemini API key

1. Open <https://aistudio.google.com/apikey>, sign in with a Google account and click **Create API key**.
2. **Local:** put it in `.env` as `GEMINI_API_KEY=...` (never commit `.env`).
3. **Streamlit Community Cloud:** app **⋮ → Settings → Secrets**, add `GEMINI_API_KEY = "..."` and save. The key stays on the server and is never shown in the UI.
4. Visitors can also paste their own key in the sidebar; it is used only for their session.

A `500 INTERNAL` or `503` error comes from Google's side, not your key: the app retries automatically, and if it persists wait a minute or switch between `gemma-4-31b-it` and `gemma-4-26b-a4b-it` in the sidebar.

## Project structure

```
Rafiq-ai/
├── streamlit_app.py        # Streamlit UI (entry point)
├── src/rafiq/              # Python package
│   ├── engine.py           #   pipeline: gates → LLM → source validation
│   ├── safety.py           #   input/output safety gates
│   ├── brand.py            #   visual identity: colours, mascot SVG, mobile-first CSS
│   └── config.py           #   paths and defaults
├── skills/                 # Behaviour rules (Markdown) loaded into the prompt
├── config/                 # policy.yaml + JSON schemas
├── data/                   # approved, reviewed source records
├── tests/                  # pytest suite + scenarios/TEST_CASES.md
├── docs/                   # architecture, demo script, skills overview, brand/
└── .github/                # CI, issue & PR templates
```

See [docs/architecture.md](docs/architecture.md) for how a message flows through the system, and [docs/demo-script.md](docs/demo-script.md) for a live demo walkthrough.

## 🎃 Hacktoberfest 2026

We welcome contributions! Look for issues labelled `hacktoberfest` and `good first issue`. Read [CONTRIBUTING.md](CONTRIBUTING.md) first — especially the rules on religious content, which **must not** be AI-generated.

Good areas to contribute: tests for `tests/scenarios/TEST_CASES.md`, Arabic dialect coverage in the safety gate, UI/RTL polish, docs and translations.

## Sources & rights

Quran text: [Tanzil](https://tanzil.net/docs/Text_License) (verbatim, with attribution). Islamweb, Sunnah.com, Dorar and Quran Foundation content is **not** bundled; do not scrape them. See [docs/skills-overview.md](docs/skills-overview.md).

## License

Code: [MIT](LICENSE). Third-party religious texts keep their own licenses.
