"""Rafiq visual identity (docs/brand/visual-identity-ar.md, palette option A).

Tokens, the mascot as inline SVG, and the Streamlit CSS layer. Phone layout is the
default; wider screens are progressive enhancements.
"""
import base64

from .config import ASSETS_DIR

# Palette A: sage. Hex values come from section 3 of the identity guide.
COLORS = {
    "primary": "#2D6255",
    "mascot_shell": "#D5E3D6",
    "mascot_face": "#F2DDC3",
    "background": "#FAF8F3",
    "surface": "#FFFFFF",
    "text": "#263B33",
    "text_secondary": "#58685E",
    "control_outline": "#748579",
    "divider": "#D8DED6",
    "warm_accent": "#E7B6A3",
    "error": "#A43737",
    "warning": "#85520D",
}

# Expression states from section 7. The shell, face and colours never change between states.
# thinking=A, warm=B, listening=D, encouraging=E, calm=F. (C, the paternal tone, is user-chosen
# and not wired into the demo yet.)
_TILT = {"thinking": -4, "warm": 0, "listening": 4, "encouraging": 0, "calm": 0}

_BROWS = {
    "thinking": "M38 47 Q45 42 52 45 M68 49 Q75 48 82 49",
    "warm": "M38 49 Q45 46 52 48 M68 48 Q75 46 82 49",
    "listening": "M38 47 Q45 45 52 47 M68 47 Q75 45 82 47",
    "encouraging": "M38 47 Q45 44 52 46 M68 46 Q75 44 82 47",
    "calm": "M38 50 Q45 49 52 50 M68 50 Q75 49 82 50",
}


def _eyes(state: str, ink: str) -> str:
    if state == "calm":  # closed lids
        return (f'<path d="M41 58 Q45 61 50 58 M70 58 Q75 61 79 58" stroke="{ink}" '
                'stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    if state == "encouraging":  # happy closed-eye arcs
        return (f'<path d="M41 59 Q45 54 50 59 M70 59 Q75 54 79 59" stroke="{ink}" '
                'stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    dx = -1.5 if state == "thinking" else 0  # gaze to the side while thinking
    return (f'<ellipse cx="{45.5 + dx}" cy="57" rx="3.4" ry="4.4" fill="{ink}"/>'
            f'<ellipse cx="{74.5 + dx}" cy="57" rx="3.4" ry="4.4" fill="{ink}"/>'
            f'<circle cx="{46.6 + dx}" cy="55.4" r="1" fill="#fff" opacity=".7"/>'
            f'<circle cx="{75.6 + dx}" cy="55.4" r="1" fill="#fff" opacity=".7"/>')


# Thinking loop: a soft bob, eyes glancing side to side, an occasional blink. CSS inside the SVG
# still runs when it is shown as an <img>; reduced-motion users get the still pose.
_ANIMATION = """<style>
.bob { animation: bob 1.8s ease-in-out infinite; transform-origin: 60px 110px; }
.look { animation: look 3.6s ease-in-out infinite; }
.blink { animation: blink 3.6s infinite; transform-box: fill-box; transform-origin: center; }
@keyframes bob { 0%, 100% { transform: translateY(0) rotate(-2deg); }
  50% { transform: translateY(-4px) rotate(2deg); } }
@keyframes look { 0%, 20% { transform: translateX(0); } 35%, 55% { transform: translateX(-3px); }
  70%, 90% { transform: translateX(3px); } 100% { transform: translateX(0); } }
@keyframes blink { 0%, 60%, 66%, 100% { transform: scaleY(1); } 63% { transform: scaleY(.1); } }
@media (prefers-reduced-motion: reduce) { .bob, .look, .blink { animation: none; } }
</style>"""


def mascot_svg(state: str = "warm", size: int = 120, tail: bool = False, animated: bool = False) -> str:
    """Rafiq mascot: rounded sage shell, cream face inset, small dark eyes.

    `tail=True` adds the speech-bubble tail used for the compact icon (section 5).
    `animated=True` adds the thinking loop, used while a reply is on its way.
    """
    c = COLORS
    ink = c["text"]
    mouth = {
        "thinking": "M56 71 Q60 72.5 64 71",
        "encouraging": "M52 69 Q60 77 68 69",
    }.get(state, "M54 70 Q60 74.5 66 70")
    tail_path = (f'<path d="M92 92 L108 110 L84 100 Z" fill="{c["mascot_shell"]}" '
                 f'stroke="#BFD0C2" stroke-width="1.5" stroke-linejoin="round"/>') if tail else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="{size}" height="{size}" \
role="img" aria-label="Rafiq">{_ANIMATION if animated else ""}
<g class="bob"><g transform="rotate({_TILT.get(state, 0)} 60 64)">
{tail_path}
<path d="M60 6 C90 6 106 28 108 58 C111 88 110 113 60 114 C10 113 9 88 12 58 C14 28 30 6 60 6 Z"
 fill="{c["mascot_shell"]}" stroke="#BFD0C2" stroke-width="1.5"/>
<path d="M22 40 C26 26 40 16 56 14" stroke="#fff" stroke-width="3" opacity=".45" fill="none"
 stroke-linecap="round"/>
<rect x="24" y="28" width="72" height="54" rx="24" fill="{c["mascot_face"]}"/>
<g transform="translate(0 -5)">
<path d="{_BROWS.get(state, _BROWS["warm"])}" stroke="{ink}" stroke-width="1.8" fill="none"
 stroke-linecap="round"/>
<g class="look"><g class="blink">{_eyes(state, ink)}</g></g>
<ellipse cx="38" cy="67" rx="5" ry="3" fill="{c["warm_accent"]}" opacity=".55"/>
<ellipse cx="82" cy="67" rx="5" ry="3" fill="{c["warm_accent"]}" opacity=".55"/>
<ellipse cx="60" cy="64" rx="2.2" ry="1.5" fill="#E2C7A8"/>
<path d="{mouth}" stroke="{ink}" stroke-width="2" fill="none" stroke-linecap="round"/>
</g></g></g></svg>"""


def user_avatar_svg(size: int = 40) -> str:
    """Neutral avatar for the user: quiet sage disc, no face, so Rafiq stays the only character."""
    c = COLORS
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="{size}" height="{size}" \
role="img" aria-label="You">
<circle cx="20" cy="20" r="20" fill="{c["divider"]}"/>
<circle cx="20" cy="16" r="6.5" fill="{c["text_secondary"]}"/>
<path d="M8 33 C10 25 30 25 32 33 Z" fill="{c["text_secondary"]}"/></svg>"""


def asset_img(name: str, width: int, alt: str = "Rafiq", cls: str = "") -> str:
    """A PNG from assets/ as an <img> data URI (brand board crops: mascot.png, icon.png)."""
    data = base64.b64encode((ASSETS_DIR / name).read_bytes()).decode()
    return f'<img class="rafiq-mascot {cls}" src="data:image/png;base64,{data}" width="{width}" alt="{alt}">'


def mascot_img(state: str = "warm", size: int = 120, tail: bool = False, cls: str = "",
               animated: bool = False) -> str:
    """Mascot as an <img> data URI; Streamlit's HTML sanitizer strips inline <svg>."""
    data = base64.b64encode(mascot_svg(state, size, tail, animated).encode()).decode()
    return (f'<img class="rafiq-mascot {cls}" src="data:image/svg+xml;base64,{data}" '
            f'width="{size}" height="{size}" alt="Rafiq">')


def css() -> str:
    c = COLORS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600&display=swap');

:root {{
  --r-primary: {c["primary"]}; --r-shell: {c["mascot_shell"]}; --r-face: {c["mascot_face"]};
  --r-bg: {c["background"]}; --r-surface: {c["surface"]}; --r-text: {c["text"]};
  --r-text-2: {c["text_secondary"]}; --r-outline: {c["control_outline"]};
  --r-divider: {c["divider"]}; --r-accent: {c["warm_accent"]};
  --r-error: {c["error"]}; --r-warning: {c["warning"]};
}}

html, body, .stApp, .stMarkdown, input, textarea, button {{
  font-family: "Noto Sans Arabic", "Segoe UI", Tahoma, system-ui, sans-serif;
}}
[data-testid="stIconMaterial"] {{ font-family: "Material Symbols Rounded" !important; }}
.stApp {{ background: var(--r-bg); color: var(--r-text); }}
[data-testid="stSidebar"] {{ background: var(--r-surface); border-inline-end: 1px solid var(--r-divider); }}
#MainMenu, [data-testid="stDecoration"], footer {{ display: none !important; }}
/* Streamlit's own toolbar (Share, star, edit, GitHub, deploy): keep only the sidebar toggle */
[data-testid="stToolbarActions"], [data-testid="stAppDeployButton"],
[data-testid="stMainMenu"] {{ display: none !important; }}
/* Streamlit's top bar overlays the page; keep it short and pad the content below it */
[data-testid="stHeader"] {{ background: var(--r-bg); height: 48px; min-height: 48px; }}

/* ---------- Phone first (base) ---------- */
.block-container {{
  max-width: 720px; padding: 52px 16px calc(96px + env(safe-area-inset-bottom)) !important;
}}
html, body {{ overflow-x: hidden; }}

/* Type scale 24 / 20 / 16 / 14; inputs stay 16px so iOS does not zoom on focus */
h1 {{ font-size: 24px !important; font-weight: 600 !important; color: var(--r-text) !important; }}
h2, h3 {{ font-size: 20px !important; font-weight: 500 !important; color: var(--r-text) !important; }}
.stMarkdown p, .stMarkdown li {{ font-size: 16px; line-height: 1.7; overflow-wrap: anywhere; }}
input, textarea {{ font-size: 16px !important; }}
[data-testid="stCaptionContainer"] {{ color: var(--r-text-2) !important; font-size: 14px; }}

/* Messages mirror the user's language direction */
[data-testid="stChatMessage"] {{ background: transparent; padding: 8px 0; gap: 10px; }}
[data-testid="stChatMessage"] .stMarkdown, [data-testid="stChatMessage"] .stMarkdown p {{
  unicode-bidi: plaintext; text-align: start;
}}
[data-testid="stChatMessage"] img {{ border-radius: 0; }}
[data-testid="stChatMessage"] pre {{ white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; }}

/* Touch targets >= 48px */
.stButton > button, .stFormSubmitButton > button {{
  width: 100%; min-height: 48px; border-radius: 12px; border: 1px solid var(--r-outline);
  background: var(--r-surface); color: var(--r-text); font-weight: 500;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
  box-shadow: 0 2px 0 var(--r-divider);
}}
.stButton > button:hover {{ border-color: var(--r-primary); color: var(--r-primary); }}
.stButton > button:active {{ transform: translateY(1px) scale(.98); box-shadow: none; }}
.stButton > button[kind="primary"] {{
  background: var(--r-primary); color: #fff; border-color: #234D43; box-shadow: 0 2px 0 #1E433A;
}}
.stButton > button[kind="primary"]:hover {{ background: #275649; color: #fff; }}
.stButton > button:disabled {{ opacity: .45; }}
.stButton > button:focus-visible {{ outline: 3px solid var(--r-primary); outline-offset: 2px; }}
.stCheckbox label, [data-testid="stWidgetLabel"] {{ min-height: 48px; display: flex; align-items: center; }}

/* Chat input pinned above the home indicator */
[data-testid="stBottom"] > div {{ background: var(--r-bg); }}
[data-testid="stBottomBlockContainer"] {{
  padding: 8px 16px calc(12px + env(safe-area-inset-bottom)) !important;
}}
[data-testid="stChatInput"] {{ border-radius: 16px; border: 1px solid var(--r-outline); background: var(--r-surface);
  overflow: hidden; }}
[data-testid="stChatInput"] > div {{ border: 0 !important; border-radius: 16px; background: transparent; }}
[data-testid="stChatInput"]:focus-within {{ border-color: var(--r-primary); box-shadow: 0 0 0 1px var(--r-primary); }}
[data-testid="stChatInput"] textarea {{ unicode-bidi: plaintext; text-align: start; }}

/* Contained areas: 16px radius */
[data-testid="stExpander"] details {{ border-radius: 16px; border: 1px solid var(--r-divider);
  background: var(--r-surface); }}
[data-testid="stAlert"] {{ border-radius: 16px; }}

/* Header: compact app bar */
.rafiq-header {{ display: flex; align-items: center; gap: 10px;
  padding: 8px 0; margin-bottom: 4px; border-bottom: 1px solid var(--r-divider); }}
.rafiq-header .rafiq-wordmark {{ font-size: 20px; }}
.rafiq-header .rafiq-wordmark small {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 52vw; }}
.rafiq-wordmark {{ font-size: 24px; font-weight: 600; color: var(--r-text); line-height: 1.2; min-width: 0; }}
.rafiq-wordmark small {{ display: block; font-size: 12px; font-weight: 400; color: var(--r-text-2); }}
.rafiq-version {{ margin-inline-start: auto; font-size: 12px; color: var(--r-text-2); flex-shrink: 0;
  border: 1px solid var(--r-divider); border-radius: 999px; padding: 2px 10px; }}
.rafiq-mascot {{ display: block; flex-shrink: 0; }}
.rafiq-icon {{ border-radius: 10px; }}

@keyframes rafiq-settle {{ from {{ transform: translateY(6px) rotate(-3deg); opacity: 0; }}
  to {{ transform: none; opacity: 1; }} }}

/* Religious content card: plain, clear Arabic, visible reference, no mascot (section 6) */
.rafiq-verse {{ background: var(--r-surface); border: 1px solid var(--r-divider); border-radius: 16px;
  padding: 16px 12px 10px; margin: 8px 0; }}
.rafiq-verse .ar {{ direction: rtl; text-align: center; font-size: 22px; line-height: 2; color: var(--r-text); }}
.rafiq-verse .ref {{ display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap;
  border-top: 1px solid var(--r-divider); margin-top: 10px; padding-top: 8px; font-size: 13px;
  color: var(--r-text-2); }}
.rafiq-verse .ref a {{ color: var(--r-primary); min-height: 24px; }}

/* Typing indicator while a reply is on its way */
.rafiq-typing {{ display: inline-flex; align-items: center; gap: 10px; min-height: 40px;
  color: var(--r-text-2); font-size: 14px; }}
.rafiq-typing .rafiq-mascot {{ width: 56px; height: 56px; }}
/* While thinking, the larger animated Rafiq stands in for the small avatar */
[data-testid="stChatMessage"]:has(.rafiq-typing) > :first-child {{ display: none; }}
.rafiq-typing .dots {{ display: inline-flex; gap: 4px; padding: 10px 12px; border-radius: 16px;
  background: var(--r-surface); border: 1px solid var(--r-divider); }}
.rafiq-typing .dots i {{ width: 7px; height: 7px; border-radius: 50%; background: var(--r-primary);
  opacity: .35; animation: rafiq-dot 1.2s ease-in-out infinite; }}
.rafiq-typing .dots i:nth-child(2) {{ animation-delay: .15s; }}
.rafiq-typing .dots i:nth-child(3) {{ animation-delay: .3s; }}
@keyframes rafiq-dot {{ 0%, 60%, 100% {{ transform: translateY(0); opacity: .35; }}
  30% {{ transform: translateY(-4px); opacity: 1; }} }}

/* Mode chip shown on special turns (text, not colour alone) */
.rafiq-chip {{ display: inline-block; font-size: 12px; border-radius: 999px; padding: 2px 10px;
  border: 1px solid var(--r-outline); color: var(--r-text-2); margin-bottom: 4px; }}
.rafiq-chip.crisis {{ border-color: var(--r-error); color: var(--r-error); }}
.rafiq-chip.corrected {{ border-color: var(--r-warning); color: var(--r-warning); }}

/* Empty chat: greeting plus starter prompts */
.rafiq-empty {{ text-align: center; padding: 24px 0 8px; }}
.rafiq-empty .rafiq-mascot {{ margin: 0 auto 8px; height: auto; animation: rafiq-settle 450ms ease-out; }}
.rafiq-empty p {{ color: var(--r-text-2); margin: 4px 0; }}
.rafiq-empty .greet {{ font-size: 20px; font-weight: 500; color: var(--r-text); }}
.rafiq-empty .note {{ font-size: 13px; line-height: 1.6; max-width: 520px; margin: 12px auto 16px; }}

.rafiq-side-brand {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}

/* ---------- Tablet / desktop enhancements ---------- */
@media (min-width: 640px) {{
  .block-container {{ padding: 64px 24px 112px !important; }}
  [data-testid="stBottomBlockContainer"] {{ max-width: 720px; padding: 8px 24px 16px !important; }}
  .rafiq-header .rafiq-wordmark {{ font-size: 24px; }}
  .rafiq-wordmark small {{ font-size: 14px; }}
  .rafiq-header .rafiq-wordmark small {{ max-width: none; }}
  .rafiq-verse .ar {{ font-size: 26px; }}
  .stButton > button {{ width: auto; min-width: 120px; }}
  [data-testid="stSidebar"] .stButton > button {{ width: 100%; min-width: 0; }}
  .rafiq-empty {{ padding-top: 48px; }}
  .rafiq-empty .rafiq-mascot {{ width: 150px; }}
  /* Starter prompts sit side by side, equal width */
  .block-container:has(.rafiq-empty) [data-testid="stColumn"] .stButton,
  .block-container:has(.rafiq-empty) [data-testid="stColumn"] [data-testid="stElementContainer"] {{
    width: 100% !important; }}
  .block-container:has(.rafiq-empty) [data-testid="stColumn"] .stButton > button {{ width: 100%; min-width: 0; }}
  .block-container:has(.rafiq-empty) [data-testid="stColumn"] .stButton > button p {{
    white-space: normal; overflow: visible; text-overflow: clip; }}
  .rafiq-empty .greet {{ font-size: 24px; }}
}}

/* ---------- Large screens: pointer users, denser sidebar ---------- */
@media (min-width: 1024px) {{
  [data-testid="stSidebar"] .stCheckbox label,
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{ min-height: 32px; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}
</style>
"""
