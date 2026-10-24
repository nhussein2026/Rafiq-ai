# Proactive check-ins

- Follow-ups must be separately opted into and user-configured; conversation alone does not authorize messaging.
- LLM proposes topic and date/time, backend checks all permissions, user timezone, user-selected windows, quiet hours, max 2 proactive messages per local day, and pause/delete status.
- Back off after unanswered reminders; no shame, alarmism, religious guilt, urgency or attachment language.
- Example: "You mentioned a goal you're working on. Would you like to share how it's going? No pressure."
- For habits, do not mention sensitive details in notification preview without opt-in.
- Safety follow-ups must be governed by explicit safety policy, not normal engagement scheduling.
- Deduplicate with idempotent worker jobs; persist schedule independent of active chat/LLM availability.
- Stop on /pause and cancel pending jobs on /forget.
