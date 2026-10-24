# Safety first (hard gate; not merely a prompt)

This module is executed by backend for ALL inbound messages before conversation/memory/religious retrieval, and again on outbound content.

- Detect imminent self-harm/suicide risk, threats to others, abuse, severe disorientation, or urgent medical danger across Arabic/English dialects and indirect language.
- Use a separately evaluated classifier + rules + escalation thresholds; model self-reported `risk_level` is never the only signal.
- If immediate risk suspected, suspend normal companion coaching, Quran/hadith recommendations, routine habit follow-ups and guilt-inducing content. Use a tested human-help response and verified locale emergency information; encourage contacting emergency services or a trusted person right now where appropriate.
- No method details for self-harm/violence. Do not suggest prayer or verses as substitutes for urgent care.
- Do not proactively notify a contact or authorities without a defined, lawful consent/emergency policy; no unverified hotline numbers.
- If uncertain, choose a conservative supportive response and escalate for review where available.
- Mark safety status separately from ordinary memory; minimize sensitive logs and do not retain raw crisis messages in analytics.
- This starter does NOT implement a crisis classifier. No pilot with vulnerable users until independently tested with human review.
