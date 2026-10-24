# Rafiq Sunni-Grounded Skills (MVP starter)

Rafiq is an AI companion, not a human, mufti, therapist or clinician. Islamic advice is grounded only in reviewed Quran, authenticated hadith, and attributed Sunni scholarly material. Conversation can be natural without inventing religious claims.

## Install / use

1. Load `skills/00_rafiq_core.md` as the top-level developer instruction (after platform/system safety instructions).
2. Route each inbound message through `skills/01_safety.md` BEFORE calling the conversational model; repeat output checks before sending.
3. Retrieve verified content from a maintained allowlisted knowledge store. These files DO NOT contain scraped Islamweb fatwas, a hadith database, verified tafsir, or an Islamweb API integration.
4. Provide retrieved citations/IDs to the model; parse its structured proposal; validate each citation and tool request server-side using `config/policy.yaml`.
5. Use `skills/02_sources.md` for religious questions; `03_quran.md`, `04_hadith.md`, `05_fiqh.md` for domain-specific response rules.
6. Use `06_companion.md` for tone, `07_memory.md` for facts, `08_followups.md` for scheduled check-ins, `09_privacy.md` for permission and deletion.
7. Test with AR/EN cases and qualified Sunni scholarly review before production.

## Critical limitations

- Never infer authenticity from an LLM response; hadith need independently recorded source, locator, and grading.
- These instructions and structured output constraints cannot guarantee safe or doctrinally correct behavior without backend checks and human review.
- Islamweb terms prohibit bots/spiders collecting content without explicit permission, and restrict reproducing content for public/commercial use. Obtain authorization before bulk ingestion or redistribution; linking to pages is not permission to scrape.
- Quran Foundation API has specific storage, attribution, and redistribution restrictions. Do not assume API data may be bundled into this open-source project.
- Do not upload confidential user conversations to third-party APIs without explicit disclosure, consent, and a suitable privacy assessment.

## Trusted references (check original pages and terms)

- https://www.islamweb.net/en/index.php?page=aboutus
- https://www.islamweb.net/service_agreement/en.pdf
- https://tanzil.net/docs/Text_License
- https://api-docs.quran.com/legal/developer-terms/
- https://dorar.net/ (hadith research reference; verify text/grading/rights before use)
- https://sunnah.com/ (collection locator reference; verify translation rights before use)

## Example runtime pipeline

`inbound -> independent safety triage -> consent/user context -> permitted knowledge retrieval -> LLM response proposal -> source ID validation + factual/citation verification -> output safety validation -> send -> approved memory updates -> authorized scheduler`

On high-risk crisis messages, normal religious guidance and follow-up encouragement are disabled in favor of immediate safety support.
