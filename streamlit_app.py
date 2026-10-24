"""Rafiq demo UI. Run: streamlit run app.py"""
import json
import os
from datetime import datetime, timedelta

import streamlit as st

from rafiq import RafiqEngine, __version__
from rafiq.config import DEFAULT_MODEL

st.set_page_config(page_title="Rafiq · رفيق", page_icon="🌙", layout="wide")

ss = st.session_state
ss.setdefault("consented", False)
ss.setdefault("messages", [])        # [{role, content, turn?}]
ss.setdefault("memories", [])        # approved facts (session-only)
ss.setdefault("pending_memory", [])  # model proposals awaiting user approval
ss.setdefault("followups", [])       # simulated scheduled check-ins
ss.setdefault("paused", False)

ABOUT = (
    "**Rafiq** is an AI companion — not a human, scholar, mufti, therapist or doctor. "
    "Islamic content is shown only from approved, reviewed source records; anything else "
    "is declined. Your messages are sent to **Google's Gemini API** to generate replies. "
    "In this demo, memory and check-ins live only in this browser session."
)


# ---------- Consent screen (skills/09_privacy.md) ----------
if not ss.consented:
    st.title("🌙 Rafiq · رفيق")
    st.info(ABOUT)
    adult = st.checkbox("I am 18 or older")
    api = st.checkbox("I understand my messages are sent to Google's Gemini API")
    if st.button("Start", disabled=not (adult and api), type="primary"):
        ss.consented = True
        st.rerun()
    st.stop()


# ---------- Sidebar: settings, memory, follow-ups ----------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API key", type="password",
                            value=os.environ.get("GEMINI_API_KEY", ""))
    model = st.text_input("Model", value=DEFAULT_MODEL,
                          help="e.g. gemini-2.5-flash, gemma-3-27b-it")
    settings = {
        "faith": st.toggle("Faith guidance (Quran from approved catalog)", value=True),
        "memory": st.toggle("Personal memory", value=False),
        "followups": st.toggle("Proactive check-ins", value=False),
    }
    show_debug = st.toggle("Show backend pipeline", value=True)

    st.divider()
    st.subheader("🧠 Memory")
    for i, m in enumerate(list(ss.pending_memory)):
        st.caption(f"Proposed ({m.get('kind', 'context')}): {m['summary']}")
        c1, c2 = st.columns(2)
        if c1.button("Save", key=f"mem_ok_{i}"):
            ss.memories.append(m["summary"])
            ss.pending_memory.pop(i)
            st.rerun()
        if c2.button("Discard", key=f"mem_no_{i}"):
            ss.pending_memory.pop(i)
            st.rerun()
    for i, fact in enumerate(list(ss.memories)):
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {fact}")
        if c2.button("✕", key=f"mem_del_{i}"):
            ss.memories.pop(i)
            st.rerun()
    if not ss.memories and not ss.pending_memory:
        st.caption("Nothing saved.")

    st.subheader("⏰ Check-ins (simulated)")
    for f in ss.followups:
        st.write(f"• {f['when']}: {f['topic']}")
    if not ss.followups:
        st.caption("None scheduled.")
    if ss.paused:
        st.warning("Paused — no check-ins will be sent.")

    st.divider()
    st.caption("Commands: /about · /mydata · /pause · /resume · /forget")
    st.caption(f"Rafiq v{__version__}")


# ---------- Chat ----------
st.title("🌙 Rafiq · رفيق")
st.caption(f"AI companion · not a scholar, mufti or therapist · v{__version__}")


def render_turn_extras(turn: dict):
    for src in turn.get("sources", []):
        with st.container(border=True):
            st.markdown(
                f"<div dir='rtl' style='font-size:1.5rem;text-align:center'>"
                f"{src['arabic_exact_text']}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"{src['source_name']} · {src['quran_verse_id']} · "
                       f"[tanzil.net]({src['source_url']})")
    if show_debug:
        with st.expander("Backend pipeline"):
            st.write(f"**Mode:** {turn['mode']}  ·  **Language:** {turn['lang']}")
            if turn["gate_flags"]:
                st.write(f"**Safety gate flags:** {turn['gate_flags']}")
            if turn["rejected_source_ids"]:
                st.write(f"**Rejected source IDs:** {turn['rejected_source_ids']}")
            if turn.get("raw"):
                st.code(json.dumps(turn["raw"], ensure_ascii=False, indent=2), language="json")


for msg in ss.messages:
    with st.chat_message(msg["role"], avatar="🌙" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])
        if msg.get("turn"):
            render_turn_extras(msg["turn"])


def system_note(text: str):
    ss.messages.append({"role": "assistant", "content": text})


def handle_command(cmd: str) -> bool:
    if cmd == "/about":
        system_note(ABOUT)
    elif cmd == "/mydata":
        system_note("**Your data in this session**\n\n```json\n" + json.dumps(
            {"memories": ss.memories, "followups": ss.followups,
             "messages_stored": len(ss.messages), "paused": ss.paused},
            ensure_ascii=False, indent=2) + "\n```")
    elif cmd == "/pause":
        ss.paused = True
        system_note("Check-ins are paused. Type /resume anytime.")
    elif cmd == "/resume":
        ss.paused = False
        system_note("Check-ins resumed.")
    elif cmd == "/forget":
        ss.messages, ss.memories, ss.pending_memory, ss.followups = [], [], [], []
        system_note("Deleted your messages, memories and scheduled check-ins from this session.")
    else:
        return False
    return True


if prompt := st.chat_input("Write in Arabic or English… / اكتب بالعربية أو الإنجليزية…"):
    if prompt.strip().lower() in {"/about", "/mydata", "/pause", "/resume", "/forget"}:
        handle_command(prompt.strip().lower())
        st.rerun()

    if not api_key:
        st.error("Add a Gemini API key in the sidebar (or GEMINI_API_KEY env var).")
        st.stop()

    ss.messages.append({"role": "user", "content": prompt})
    history = [{"role": m["role"], "content": m["content"]} for m in ss.messages]

    with st.spinner("…"):
        try:
            turn = RafiqEngine(api_key=api_key, model=model).respond(history, settings, ss.memories)
        except Exception as e:  # show API/parse errors instead of crashing the demo
            ss.messages.pop()
            st.error(f"Model call failed: {e}")
            st.stop()

    t = turn.__dict__
    ss.messages.append({"role": "assistant", "content": turn.reply, "turn": t})
    ss.pending_memory.extend(turn.memory_proposals)
    if turn.followup_proposal and not ss.paused:
        when = datetime.now() + timedelta(days=int(turn.followup_proposal.get("suggested_delay_days", 1)))
        ss.followups.append({"topic": turn.followup_proposal["topic"],
                             "when": when.strftime("%a %d %b, 18:00")})
    st.rerun()
