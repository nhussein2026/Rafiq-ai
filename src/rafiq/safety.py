"""Demo-only safety gates (skills/01_safety.md).

These are keyword rules, NOT a validated crisis classifier. They exist so the
demo shows the pipeline shape: input gate before the LLM, output gate after.
"""
import re

# Imminent self-harm / harm indicators (EN + AR, incl. some dialect forms).
_CRISIS_PATTERNS = [
    r"\bkill (myself|me)\b", r"\bsuicid", r"\bend (my|it all|my life)\b",
    r"\bwant to die\b", r"\bdon'?t want to (live|be alive)\b", r"\bhurt myself\b",
    r"\bself[- ]?harm\b", r"\bcut myself\b", r"\bno reason to live\b",
    r"\bkill (him|her|them|someone)\b",
    r"انتحر", r"انتحار", r"اقتل نفسي", r"أقتل نفسي", r"أنهي حياتي", r"انهي حياتي",
    r"بدي موت", r"ابغى اموت", r"أبغى أموت", r"اريد ان اموت", r"أريد أن أموت",
    r"نفسي اموت", r"ما بدي عيش", r"أؤذي نفسي", r"اذي نفسي", r"أجرح نفسي",
]
_CRISIS_RE = re.compile("|".join(_CRISIS_PATTERNS), re.IGNORECASE)

CRISIS_REPLY = {
    "en": (
        "I'm really glad you told me. What you're feeling sounds very heavy, and you "
        "deserve support from a real person right now. If you might act on these "
        "thoughts or are in danger, please contact your local emergency number "
        "immediately, or go to the nearest emergency department. If you can, reach "
        "out to someone you trust and tell them what's happening. I'm an AI and can't "
        "keep you safe on my own. Is there someone near you that you could contact now?"
    ),
    "ar": (
        "أنا ممتن أنك أخبرتني. ما تشعر به يبدو ثقيلًا جدًا، وتستحق دعمًا من شخص حقيقي الآن. "
        "إذا كنت قد تؤذي نفسك أو كنت في خطر، فاتصل برقم الطوارئ المحلي فورًا أو توجّه إلى أقرب قسم طوارئ. "
        "وإن استطعت، تواصل مع شخص تثق به وأخبره بما يحدث. أنا ذكاء اصطناعي ولا أستطيع حمايتك وحدي. "
        "هل يوجد شخص قريب منك يمكنك التواصل معه الآن؟"
    ),
}

# Output gate: religious claims that must come only from approved records.
_UNSOURCED_RELIGIOUS_PATTERNS = [
    r"قال (الله|تعالى)", r"قال رسول الله", r"قال النبي", r"عن النبي ﷺ",
    r"رواه (البخاري|مسلم|الترمذي|أبو داود|النسائي|ابن ماجه|أحمد)",
    r"\b(prophet|messenger)\b[^.]{0,40}\bsaid\b", r"\bnarrated by\b",
    r"\b(sahih|sunan) [a-z]+ \d+", r"\bfatwa (no\.?|number|#)\s*\d+",
    r"رقم الفتوى", r"\bsurah\b[^.]{0,30}\d+:\d+", r"\(\d{1,3}:\d{1,3}\)",
]
_UNSOURCED_RE = re.compile("|".join(_UNSOURCED_RELIGIOUS_PATTERNS), re.IGNORECASE)
# Long fully-vowelled Arabic runs usually mean the model is quoting scripture itself.
_DIACRITIC_RUN_RE = re.compile(r"(?:[ء-ي][ً-ْ]+){8,}")
_EXCLUSIVE_RE = re.compile(
    r"\bI need you\b|\bI miss you\b|\bonly one who understands\b|\bI love you\b|"
    r"أحتاجك|اشتقت لك|الوحيد الذي يفهمك|أحبك",
    re.IGNORECASE,
)


def detect_language(text: str) -> str:
    arabic = len(re.findall(r"[؀-ۿ]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "ar" if arabic > latin else "en"


def input_gate(text: str) -> str:
    """Return 'crisis' or 'ok'."""
    return "crisis" if _CRISIS_RE.search(text) else "ok"


def output_gate(reply: str) -> list[str]:
    """Return a list of violation labels (empty means pass)."""
    problems = []
    if input_gate(reply) == "crisis":
        problems.append("harm_content")
    if _UNSOURCED_RE.search(reply) or _DIACRITIC_RUN_RE.search(reply):
        problems.append("unsourced_religious_quote")
    if _EXCLUSIVE_RE.search(reply):
        problems.append("attachment_language")
    return problems
