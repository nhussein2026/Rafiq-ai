# Hadith and Sunnah skill

- Only use pre-reviewed hadith records from an allowed repository; MVP may leave this entire module disabled until data rights and reviewer approval are complete.
- Each record must include `hadith_id`, exact verified text, collection name, reliable locator, authenticity assessment, attribution of the grading scholar, source URL, review status and rights.
- Backend—not LLM—renders exact quoted text. Any `hadith_id` not in allowed approved records is rejected.
- Distinguish sahih, hasan, da'if, fabricated and disputed status as actually recorded; do not flatten disagreements.
- MVP allow only approved `sahih` and `hasan` entries where provenance is resolved; don't manufacture graded statements from semantic similarity.
- Do not build a legal ruling from isolated hadith without context and reviewed Sunni interpretation.
- If source is missing or uncertain, say hadith verification is unavailable and omit it.
