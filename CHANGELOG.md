# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-24

First public release (Hacktoberfest 2026).

### Added
- Rafiq skills (`skills/00`–`09`): core persona, safety, sources, Quran, hadith, fiqh, companion, memory, follow-ups, privacy.
- `config/policy.yaml` and JSON schemas for responses and source records.
- Streamlit demo app with Gemini/Gemma support via the Gemini API.
- Backend pipeline: keyword safety input gate (crisis bypasses the LLM), output gate with one corrective retry, approved source-ID validation with backend-rendered Quran text.
- Consent screen (18+, third-party API disclosure), toggles for faith guidance, memory and check-ins, and `/about` `/mydata` `/pause` `/resume` `/forget` commands.
- Three demo Quran records from Tanzil (reviewer marked `DEMO_PLACEHOLDER`).
- pytest suite, GitHub Actions CI and tag-based release workflow.
- Contributor docs: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue and PR templates.

### Known limitations
- Safety gate is keyword-based, not a validated classifier.
- Memory and follow-ups are session-only and simulated.
- Hadith and scholar (Islamweb) sources are disabled.

[Unreleased]: https://github.com/OWNER/Rafiq-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/Rafiq-ai/releases/tag/v0.1.0
