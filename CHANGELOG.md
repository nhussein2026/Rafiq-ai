# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API key from Streamlit secrets (`GEMINI_API_KEY`).
- Live preview on Streamlit Community Cloud: https://rafiq-ai-elpr2wxpebscy9wrsbywom.streamlit.app/

### Changed
- Opens straight into the chat: the 18+ / consent screen is gone; the AI and Gemini API notice now sits on the empty-chat welcome.
- Large-screen layout: sidebar opens by default on desktop, header no longer hidden under the top bar, chat input aligned with the content column, starter prompts on the empty chat.
- Gemini 5xx/429 errors are retried with backoff and shown as plain-language messages.
- A failed reply keeps the user's message on screen with a **Try again** button; Rafiq "thinks" inside its own chat bubble.
- Sidebar: model is a picker limited to `gemma-4-31b-it` (default) and `gemma-4-26b-a4b-it`, key and model grouped under **Model & API key**, tighter spacing on desktop.
- New tagline on the welcome screen: «رفيق عن رفيق بيفرق».

### Security
- The deployer's API key is no longer prefilled into the sidebar password field, where any visitor could reveal it.

## [0.1.0] - 2026-10-24

First public release (Hacktoberfest 2026).

### Added
- Rafiq skills (`skills/00`–`09`): core persona, safety, sources, Quran, hadith, fiqh, companion, memory, follow-ups, privacy.
- `config/policy.yaml` and JSON schemas for responses and source records.
- Streamlit demo app with Gemini/Gemma support via the Gemini API.
- Backend pipeline: keyword safety input gate (crisis bypasses the LLM), output gate with one corrective retry, approved source-ID validation with backend-rendered Quran text.
- Consent screen (18+, third-party API disclosure), toggles for faith guidance, memory and check-ins, and `/about` `/mydata` `/pause` `/resume` `/forget` commands.
- Rafiq visual identity (palette A, sage): mascot drawn as SVG with five expression states
  (warm, thinking, listening, encouraging, calm), Noto Sans Arabic, brand tokens in `rafiq.brand`.
- Mobile-first layout: phone is the default view, tested at 320, 390 and 1280px with no horizontal
  scroll; 48px touch targets, safe-area padding, RTL-aware messages, reduced-motion support.
- Three demo Quran records from Tanzil (reviewer marked `DEMO_PLACEHOLDER`).
- pytest suite, GitHub Actions CI and tag-based release workflow.
- Contributor docs: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue and PR templates.

### Known limitations
- Safety gate is keyword-based, not a validated classifier.
- Memory and follow-ups are session-only and simulated.
- Hadith and scholar (Islamweb) sources are disabled.

[Unreleased]: https://github.com/nhussein2026/Rafiq-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nhussein2026/Rafiq-ai/releases/tag/v0.1.0
