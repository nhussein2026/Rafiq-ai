"""Rafiq demo UI. Run: streamlit run streamlit_app.py"""
import json
import os
from datetime import datetime, timedelta

import streamlit as st

from rafiq import RafiqEngine, __version__
from rafiq.brand import asset_img, css, mascot_svg, user_avatar_svg
from rafiq.config import ASSETS_DIR, DEFAULT_MODEL

st.set_page_config(page_title="Rafiq · رفيق", page_icon=str(ASSETS_DIR / "icon-128.png"), layout="centered",
                   initial_sidebar_state="auto")  # open on desktop, collapsed on phones
st.markdown(css(), unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("messages", [])        # [{role, content, turn?}]
ss.setdefault("memories", [])        # approved facts (session-only)
ss.setdefault("pending_memory", [])  # model proposals awaiting user approval
ss.setdefault("followups", [])       # simulated scheduled check-ins
ss.setdefault("paused", False)
ss.setdefault("pending", False)      # last user message is waiting for a reply
ss.setdefault("error", None)         # last model failure, shown with a Retry button

MODELS = ["gemma-4-31b-it", "gemma-4-26b-a4b-it"]

ABOUT = (
    "**Rafiq** is an AI companion — not a human, scholar, mufti, therapist or doctor. "
    "Islamic content is shown only from approved, reviewed source records; anything else "
    "is declined. Your messages are sent to **Google's Gemini API** to generate replies. "
    "In this demo, memory and check-ins live only in this browser session."
)


def server_api_key() -> str:
    """The deployer's key: Streamlit secrets (Cloud) first, then the environment (local .env)."""
    try:
        return st.secrets.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    except Exception:  # no secrets.toml
        return os.environ.get("GEMINI_API_KEY", "")


def model_error_message(e: Exception) -> str:
    code = getattr(e, "code", None)
    if code in (500, 502, 503, 504):
        return ("Gemini is having a temporary problem on Google's side. Wait a moment and send "
                "your message again, or switch model in the sidebar.")
    if code == 429:
        return "The Gemini API key has hit its rate or free-tier limit. Wait a minute and try again."
    if code in (400, 401, 403) and "key" in str(e).lower():
        return ("The Gemini API key was rejected. Create a new one at https://aistudio.google.com/apikey "
                "and paste it in the sidebar.")
    if code == 404:
        return "That model name was not found. Pick one from the list in the sidebar."
    return f"Model call failed: {e}"


def md_bold(text: str) -> str:
    """Tiny **bold** -> <b> for text placed inside raw HTML blocks."""
    parts = text.split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


STARTERS = [
    "I'm stressed about my exams",
    "أشعر بالوحدة هذه الأيام",
    "Help me build a small daily habit",
]


def avatar_state(turn: dict | None) -> str:
    """Pick a mascot expression (identity guide section 7) for an assistant message."""
    if not turn:
        return "calm" if ss.paused else "warm"
    if turn["mode"] == "crisis":
        return "listening"
    if turn["mode"] == "corrected":
        return "thinking"
    if turn.get("memory_proposals") or turn.get("followup_proposal"):
        return "encouraging"
    return "warm"


# ---------- Sidebar: settings, memory, follow-ups ----------
with st.sidebar:
    st.markdown(
        f'<div class="rafiq-side-brand">{asset_img("icon-128.png", 40, cls="rafiq-icon")}'
        f'<div class="rafiq-wordmark" style="font-size:20px">رفيق</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Settings")
    settings = {
        "faith": st.toggle("Faith guidance (Quran from approved catalog)", value=True),
        "memory": st.toggle("Personal memory", value=False),
        "followups": st.toggle("Proactive check-ins", value=False),
    }

    # Never prefill the deployer's key: a password field can be revealed by any visitor.
    has_server_key = bool(server_api_key())
    with st.expander("Model & API key", expanded=not has_server_key):
        api_key = st.text_input(
            "Gemini API key", type="password",
            placeholder="Using the app's key (optional)" if has_server_key else "Paste your key",
            help="Free key: https://aistudio.google.com/apikey · used only for this session",
        ) or server_api_key()
        model = st.selectbox(
            "Model", MODELS, index=MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in MODELS else 0,
            accept_new_options=True,
            help="Gemma 4 via the Gemini API. If one is busy, try the other.",
        )
        show_debug = st.toggle("Show backend pipeline", value=True)

    st.divider()
    st.subheader("Memory")
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

    st.subheader("Check-ins (simulated)")
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
st.markdown(
    f"""<div class="rafiq-header">{asset_img("icon-128.png", 44, cls="rafiq-icon")}
    <div class="rafiq-wordmark">رفيق <small>AI companion · not a scholar or therapist</small></div>
    <span class="rafiq-version">v{__version__}</span></div>""",
    unsafe_allow_html=True,
)


MODE_CHIPS = {"crisis": "Safety mode · وضع الأمان", "corrected": "Checked by safety gate"}


def render_turn_extras(turn: dict):
    for src in turn.get("sources", []):
        st.markdown(
            f"""<div class="rafiq-verse"><div class="ar">{src['arabic_exact_text']}</div>
            <div class="ref"><span>{src['source_name']} · {src['quran_verse_id']}</span>
            <a href="{src['source_url']}" target="_blank">tanzil.net</a></div></div>""",
            unsafe_allow_html=True,
        )
    if show_debug:
        with st.expander("Backend pipeline"):
            st.write(f"**Mode:** {turn['mode']}  ·  **Language:** {turn['lang']}")
            if turn["gate_flags"]:
                st.write(f"**Safety gate flags:** {turn['gate_flags']}")
            if turn["rejected_source_ids"]:
                st.write(f"**Rejected source IDs:** {turn['rejected_source_ids']}")
            if turn.get("raw"):
                st.code(json.dumps(turn["raw"], ensure_ascii=False, indent=2), language="json")


if not ss.messages:
    st.markdown(
        f"""<div class="rafiq-empty">{asset_img("mascot.png", 120)}
        <p class="greet">أهلاً، أنا رفيق · Hi, I'm Rafiq</p>
        <p>رفيق عن رفيق بيفرق</p>
        <p class="note">{md_bold(ABOUT)}</p></div>""",
        unsafe_allow_html=True,
    )
    for col, text in zip(st.columns(len(STARTERS)), STARTERS, strict=True):
        if col.button(text, key=f"starter_{text}"):
            ss.starter = text
            st.rerun()

for msg in ss.messages:
    turn = msg.get("turn")
    avatar = mascot_svg(avatar_state(turn), size=40) if msg["role"] == "assistant" else user_avatar_svg()
    with st.chat_message(msg["role"], avatar=avatar):
        if turn and turn["mode"] in MODE_CHIPS:
            st.markdown(f'<span class="rafiq-chip {turn["mode"]}">{MODE_CHIPS[turn["mode"]]}</span>',
                        unsafe_allow_html=True)
        st.markdown(msg["content"])
        if turn:
            render_turn_extras(turn)


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


# A failed reply keeps the user's message on screen and offers a retry.
if ss.error and ss.messages and ss.messages[-1]["role"] == "user":
    st.error(ss.error)
    if st.button("Try again", type="primary", key="retry"):
        ss.error, ss.pending = None, True
        st.rerun()

if prompt := st.chat_input("اكتب رسالتك · Message Rafiq") or ss.pop("starter", None):
    if prompt.strip().lower() in {"/about", "/mydata", "/pause", "/resume", "/forget"}:
        handle_command(prompt.strip().lower())
        st.rerun()

    if not api_key:
        st.error("Add a Gemini API key under **Model & API key** in the sidebar "
                 "(free at https://aistudio.google.com/apikey).")
        st.stop()

    # Show the message first, then reply on the next run so it never disappears behind a spinner.
    if ss.error and ss.messages and ss.messages[-1]["role"] == "user":
        ss.messages.pop()  # replace the unanswered message instead of stacking it
    ss.messages.append({"role": "user", "content": prompt})
    ss.error, ss.pending = None, True
    st.rerun()

if ss.pending:
    ss.pending = False
    history = [{"role": m["role"], "content": m["content"]} for m in ss.messages]
    with st.chat_message("assistant", avatar=mascot_svg("thinking", size=40)):
        with st.spinner("رفيق يفكر… · Rafiq is thinking…"):
            try:
                turn = RafiqEngine(api_key=api_key, model=model).respond(history, settings, ss.memories)
            except Exception as e:  # show API/parse errors instead of crashing the demo
                ss.error = model_error_message(e)
                st.rerun()

    t = turn.__dict__
    ss.messages.append({"role": "assistant", "content": turn.reply, "turn": t})
    ss.pending_memory.extend(turn.memory_proposals)
    if turn.followup_proposal and not ss.paused:
        when = datetime.now() + timedelta(days=int(turn.followup_proposal.get("suggested_delay_days", 1)))
        ss.followups.append({"topic": turn.followup_proposal["topic"],
                             "when": when.strftime("%a %d %b, 18:00")})
    st.rerun()
