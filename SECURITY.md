# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security or safety problems. Report privately through GitHub: [Report a vulnerability](https://github.com/nhussein2026/Rafiq-ai/security/advisories/new), with:

- a description of the issue and its impact,
- steps to reproduce,
- any suggested fix.

We aim to reply within 7 days.

## In scope

- Bypasses of the safety gates (`src/rafiq/safety.py`) or the source allow-list.
- Prompt injection that makes Rafiq fabricate scripture, hadith or fatwas.
- Leaks of API keys or user data.

Reports about crisis handling should describe the *pattern* of the bypass, not detailed harmful content.
