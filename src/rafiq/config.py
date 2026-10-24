"""Paths and defaults. Override the repo location with RAFIQ_HOME if needed."""
import os
from pathlib import Path

REPO_ROOT = Path(os.environ.get("RAFIQ_HOME", Path(__file__).resolve().parents[2]))
SKILLS_DIR = REPO_ROOT / "skills"
CONFIG_DIR = REPO_ROOT / "config"
SOURCES_FILE = REPO_ROOT / "data" / "approved_sources.json"

DEFAULT_MODEL = os.environ.get("RAFIQ_MODEL", "gemini-2.5-flash")

# Skills the conversational model sees. 01_safety is enforced in code, not prompted;
# 04_hadith is disabled by config/policy.yaml until rights + reviewer approval.
PROMPT_SKILLS = [
    "00_rafiq_core.md", "02_sources.md", "03_quran.md", "05_fiqh.md",
    "06_companion.md", "07_memory.md", "08_followups.md", "09_privacy.md",
]
