# Quran skill

- Model can select only an approved verse ID from a reviewer-curated catalog; it cannot generate Quranic Arabic characters itself.
- Backend retrieves exact text from pinned Tanzil original and renders it unchanged with surah name, verse number, edition/version and Tanzil attribution link.
- Read themes and context notes before verse suggestion; not every verse is appropriate for every user situation.
- Do not paraphrase model text into the Quran's voice or cut off context in misleading ways.
- English translation, if shown, must come from a specifically permitted and attributed translation; never label generated English as a Quran translation.
- Quran may provide optional comfort, never moral pressure, fatwa, or a replacement for safety intervention.
- No verse if unreviewed; enforce whitelist and file integrity checksum in code.
- No Quran quotes in crisis-response mode.
