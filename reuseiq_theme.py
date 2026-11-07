"""
ReUseIQ visual theme: glass top navigation, cinematic hero, feature cards.
Pure presentation layer. No business logic, routes or AI code lives here.
"""

import streamlit as st

NAV_KEY = "nav_page_radio"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _flat(html: str) -> str:
    """Strip indentation/blank lines so Streamlit's markdown never treats HTML as code."""
    return "".join(line.strip() for line in html.splitlines())


def _kc(key: str):
    """Keyed container (Streamlit >= 1.39). Falls back to a plain container."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _go(page: str):
    st.session_state[NAV_KEY] = page


# ---------------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------------
_LOGO = """
<svg viewBox="0 0 100 100" width="34" height="34" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#86efac"/><stop offset="1" stop-color="#10b981"/></linearGradient></defs>
<g stroke="url(#lg)" stroke-width="9" stroke-linecap="round" fill="url(#lg)">
<g><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5" stroke-width="2"/></g>
<g transform="rotate(120 50 50)"><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5" stroke-width="2"/></g>
<g transform="rotate(240 50 50)"><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5" stroke-width="2"/></g>
</g></svg>
"""

BRAND_HTML = '<div class="brand">' + _LOGO + "<span>ReUseIQ Advisor</span></div>"

_ARROWS = """
<g><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5"/></g>
<g transform="rotate(120 50 50)"><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5"/></g>
<g transform="rotate(240 50 50)"><path d="M50 16 A34 34 0 0 1 77 31" fill="none"/><polygon points="85.5,29.5 84.4,41.7 73.3,36.5"/></g>
"""

HERO_VISUAL = (
    """
<div class="hero-visual">
<svg viewBox="0 0 600 580" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
<defs>
<linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bbf7d0"/><stop offset=".5" stop-color="#34d399"/><stop offset="1" stop-color="#047857"/></linearGradient>
<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#10b981" stop-opacity=".55"/><stop offset="1" stop-color="#10b981" stop-opacity="0"/></radialGradient>
<linearGradient id="bin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#10211b"/><stop offset="1" stop-color="#050a08"/></linearGradient>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<circle class="halo" cx="300" cy="235" r="250" fill="url(#halo)"/>
<g class="float" filter="url(#glow)">
<g transform="translate(300 225) scale(3.5) translate(-50 -50)" stroke="url(#hg)" fill="url(#hg)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">
"""
    + _ARROWS
    + """
</g>
<g transform="translate(300 225) scale(3.5) translate(-50 -50)" stroke="#03120c" fill="none" stroke-width="3.4" stroke-dasharray="1 5.5" stroke-linecap="round" opacity=".75">
<path d="M50 16 A34 34 0 0 1 77 31"/><path transform="rotate(120 50 50)" d="M50 16 A34 34 0 0 1 77 31"/><path transform="rotate(240 50 50)" d="M50 16 A34 34 0 0 1 77 31"/>
</g>
</g>
<g stroke="rgba(255,255,255,.16)" stroke-width="1.5" fill="#0b1512">
<rect x="170" y="412" width="46" height="84" rx="9" transform="rotate(-20 193 454)"/>
<rect x="245" y="420" width="104" height="66" rx="6" transform="rotate(7 297 453)"/>
<rect x="372" y="408" width="68" height="90" rx="8" transform="rotate(16 406 453)"/>
<rect x="318" y="438" width="40" height="40" rx="5" transform="rotate(-8 338 458)" stroke="rgba(52,211,153,.5)"/>
<rect x="215" y="436" width="34" height="50" rx="5" transform="rotate(24 232 461)"/>
</g>
<g stroke="rgba(52,211,153,.55)" stroke-width="1.5" fill="none" stroke-linecap="round">
<path d="M150 478 C190 440 215 470 250 452"/><path d="M350 462 C390 430 420 470 465 440"/><path d="M265 470 C285 445 305 478 330 452"/>
</g>
<path d="M118 470 H482 L458 556 H142 Z" fill="url(#bin)" stroke="rgba(52,211,153,.45)" stroke-width="2"/>
<rect x="104" y="452" width="392" height="24" rx="10" fill="#0c1914" stroke="rgba(52,211,153,.7)" stroke-width="2"/>
<g stroke="rgba(52,211,153,.18)" stroke-width="2"><path d="M200 482 L208 548"/><path d="M300 482 V550"/><path d="M400 482 L392 548"/></g>
<ellipse cx="300" cy="566" rx="220" ry="9" fill="#10b981" opacity=".22"/>
<g fill="#6ee7b7">
<circle class="pt" cx="210" cy="400" r="2.4" style="animation-delay:0s"/>
<circle class="pt" cx="260" cy="380" r="1.8" style="animation-delay:1.4s"/>
<circle class="pt" cx="340" cy="395" r="2.6" style="animation-delay:2.6s"/>
<circle class="pt" cx="400" cy="385" r="1.9" style="animation-delay:.8s"/>
<circle class="pt" cx="300" cy="410" r="2.2" style="animation-delay:3.4s"/>
<circle class="pt" cx="450" cy="410" r="1.6" style="animation-delay:2s"/>
</g>
</svg>
</div>
"""
)

HERO_COPY = """
<div class="hero-copy">
<div class="eyebrow"><span class="dot"></span>Symbolic AI &middot; Decision Support</div>
<div class="hero-title"><span class="accent">ReUseIQ:</span> Intelligent E-Waste Reuse &amp; Recycling Advisor</div>
<div class="hero-sub">Symbolic AI Decision Support for Sustainable Electronics Lifecycle Management</div>
<p class="hero-desc">Electronic waste is the fastest-growing solid waste stream in the world. ReUseIQ is an expert decision-support system built entirely on Classical Symbolic AI principles, evaluating devices with formal logic, safety constraints, fuzzy logic, probabilistic uncertainty and multi-criteria decision theory.</p>
</div>
"""

_ICON_BRAIN = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#34d399" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v16"/><path d="M12 6c-1-2.4-4.4-2.4-5.2 0-2.2 0-3.2 2.2-2.2 4.2-1.2 1.1-1.2 3.2.8 4.1 0 2.3 2.4 3.4 4.4 2.3"/><path d="M12 6c1-2.4 4.4-2.4 5.2 0 2.2 0 3.2 2.2 2.2 4.2 1.2 1.1 1.2 3.2-.8 4.1 0 2.3-2.4 3.4-4.4 2.3"/><path d="M8 10h2M14 10h2M8 14h2M14 14h2"/></svg>'
_ICON_FUZZY = '<svg viewBox="0 0 100 100" width="30" height="30" fill="none" stroke="#34d399" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M50 16 A34 34 0 0 1 77 31"/><path transform="rotate(120 50 50)" d="M50 16 A34 34 0 0 1 77 31"/><path transform="rotate(240 50 50)" d="M50 16 A34 34 0 0 1 77 31"/><polyline points="78,22 80,36 68,34"/><polyline transform="rotate(120 50 50)" points="78,22 80,36 68,34"/><polyline transform="rotate(240 50 50)" points="78,22 80,36 68,34"/></svg>'
_ICON_SCALE = '<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="#34d399" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 7a3.5 3.5 0 0 0 6 0L5 7zM19 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7z"/></svg>'


def _card(icon, title, body, delay):
    return (
        f'<div class="feat-card" style="animation-delay:{delay}s"><div class="feat-ico">{icon}</div>'
        f'<div class="feat-title">{title}</div><p>{body}</p></div>'
    )


FEATURES = (
    '<div id="features" class="feat-grid">'
    + _card(_ICON_BRAIN, "Symbolic Knowledge &amp; Rules",
            "Encodes domain knowledge using <b>first-order predicate logic</b> and <b>IF-THEN rules</b>. Evaluates device safety, spare parts availability, data privacy requirements, and repair economics.", .15)
    + _card(_ICON_FUZZY, "Fuzzy &amp; Probabilistic Reasoning",
            "Uses <b>triangular fuzzy membership</b> to model vague concepts like damage severity and repairability. Applies <b>Bayesian probability updating</b> to model repair uncertainty.", .3)
    + _card(_ICON_SCALE, "Multi-Criteria Utility Theory",
            "Compares 5 actions (<b>Repair, Refurbish, Component Recovery, Direct Reuse, Recycle</b>) balancing economic feasibility, environmental impact, and device life extension.", .45)
    + "</div>"
)

_CHIP_TEXT = [
    "No ML / DL / NLP", "Pure Symbolic AI", "Forward Chaining Rules", "Backward Chaining Proofs",
    "Fuzzy Logic (Triangular)", "Bayesian Uncertainty", "Expected Utility Scoring", "W3C OWL 2 Ontology",
]
CHIPS = (
    '<div class="chip-label">Architecture Highlights</div><div class="chips">'
    + "".join(f'<span class="chip">{t}</span>' for t in _CHIP_TEXT)
    + "</div>"
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root{--g:#34d399;--g2:#10b981;--bg:#050807;--card:rgba(255,255,255,.035);--line:rgba(255,255,255,.09);--mut:#9fb0aa;}
html{scroll-behavior:smooth}
[data-testid="stMain"],section.main{scroll-behavior:smooth}
.stApp,.stApp p,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp label,.stApp button,.stApp input,.stApp textarea{font-family:'Inter',system-ui,sans-serif}
.stApp{background:
 radial-gradient(1100px 560px at 88% 4%,rgba(16,185,129,.16),transparent 60%),
 radial-gradient(800px 480px at 4% 0%,rgba(16,185,129,.06),transparent 60%),var(--bg);color:#e8f1ee}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer{display:none!important}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
.block-container{max-width:1280px;padding-top:6.4rem;padding-bottom:4rem}
hr{border-color:var(--line)!important}
h1,h2,h3{letter-spacing:-.02em}

/* ---------- glass top nav ---------- */
.st-key-topnav{position:fixed;top:14px;left:50%;transform:translateX(-50%);width:min(1240px,calc(100% - 28px));z-index:1000;
 background:rgba(10,16,14,.55);backdrop-filter:blur(18px) saturate(150%);-webkit-backdrop-filter:blur(18px) saturate(150%);
 border:1px solid var(--line);border-radius:999px;padding:.3rem 1.1rem;box-shadow:0 10px 40px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.05);
 animation:navIn .7s cubic-bezier(.2,.8,.2,1) both}
.st-key-topnav [data-testid="stHorizontalBlock"]{align-items:center;flex-wrap:nowrap!important;gap:.5rem}
.st-key-topnav [data-testid="stColumn"],.st-key-topnav [data-testid="column"]{min-width:0!important}
.st-key-topnav [data-testid="stElementContainer"],.st-key-topnav .stMarkdown{margin:0}
.brand{display:flex;align-items:center;gap:.6rem;white-space:nowrap}
.brand span{font-weight:700;font-size:1.05rem;color:#fff;letter-spacing:-.01em}
.st-key-topnav div[role="radiogroup"]{gap:.15rem;justify-content:flex-end;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}
.st-key-topnav div[role="radiogroup"]::-webkit-scrollbar{display:none}
.st-key-topnav label[data-baseweb="radio"]{position:relative;margin:0;padding:.6rem .85rem;border-radius:999px;cursor:pointer;transition:background .25s;white-space:nowrap}
.st-key-topnav label[data-baseweb="radio"]>div:first-child{display:none}
.st-key-topnav label[data-baseweb="radio"] p{margin:0;font-size:.84rem;font-weight:500;color:var(--mut);transition:color .25s}
.st-key-topnav label[data-baseweb="radio"]:hover{background:rgba(255,255,255,.05)}
.st-key-topnav label[data-baseweb="radio"]:hover p{color:#fff}
.st-key-topnav label[data-baseweb="radio"]:has(input:checked) p{color:#fff;font-weight:600}
.st-key-topnav label[data-baseweb="radio"]:has(input:checked)::after{content:"";position:absolute;left:.85rem;right:.85rem;bottom:.18rem;height:2px;border-radius:2px;background:var(--g);box-shadow:0 0 12px var(--g)}

/* ---------- hero ---------- */
.st-key-hero{position:relative;overflow:hidden;border-radius:32px;border:1px solid var(--line);padding:3.2rem 2.6rem 2.2rem;min-height:620px;
 background:radial-gradient(700px 500px at 78% 45%,rgba(16,185,129,.18),transparent 65%),linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,0) 40%),#060b09;
 animation:fadeUp .9s cubic-bezier(.2,.8,.2,1) both}
.st-key-hero::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.35;
 background-image:linear-gradient(rgba(52,211,153,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(52,211,153,.07) 1px,transparent 1px);background-size:56px 56px;
 -webkit-mask-image:radial-gradient(ellipse at 75% 40%,#000 0%,transparent 70%);mask-image:radial-gradient(ellipse at 75% 40%,#000 0%,transparent 70%)}
.hero-copy{position:relative;padding-top:1.2rem;animation:fadeUp .9s .15s cubic-bezier(.2,.8,.2,1) both}
.eyebrow{display:inline-flex;align-items:center;gap:.5rem;padding:.35rem .85rem;border:1px solid rgba(52,211,153,.35);border-radius:999px;background:rgba(16,185,129,.08);color:#a7f3d0;font-size:.74rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--g);box-shadow:0 0 10px var(--g);animation:pulse 2s ease-in-out infinite}
.hero-title{margin:1.3rem 0 1rem;font-size:clamp(2.3rem,4.4vw,4rem);line-height:1.07;font-weight:700;letter-spacing:-.03em;color:#fff}
.hero-title .accent{background:linear-gradient(90deg,#4ade80,#34d399 60%,#10b981);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-sub{font-size:clamp(1.05rem,1.6vw,1.4rem);font-weight:400;line-height:1.35;color:#d5e2dd;max-width:30rem;margin-bottom:1rem}
.hero-desc{color:var(--mut);font-size:.98rem;line-height:1.65;max-width:32rem;margin-bottom:1.6rem}
.hero-visual{position:relative;width:100%;animation:fadeUp 1.1s .25s cubic-bezier(.2,.8,.2,1) both}
.hero-visual svg{width:100%;height:auto;max-height:540px;display:block}
.hero-visual .float{animation:float 6s ease-in-out infinite}
.hero-visual .halo{animation:pulse 5s ease-in-out infinite;transform-origin:300px 235px}
.hero-visual .pt{animation:rise 6s linear infinite;opacity:0}

/* ---------- buttons ---------- */
.stApp .stButton>button,.stApp .stFormSubmitButton>button,.stApp .stDownloadButton>button{border-radius:999px;border:1px solid rgba(52,211,153,.4);background:rgba(16,185,129,.08);color:#d1fae5;font-weight:600;transition:all .25s}
.stApp .stButton>button:hover,.stApp .stFormSubmitButton>button:hover,.stApp .stDownloadButton>button:hover{background:rgba(16,185,129,.2);border-color:var(--g);color:#fff;transform:translateY(-1px);box-shadow:0 8px 24px rgba(16,185,129,.2)}
.stApp .st-key-cta_explore button{height:46px;padding:0 1.6rem;border:none;background:linear-gradient(135deg,#6ee7b7,#34d399 55%,#10b981);color:#03150e;font-weight:700;box-shadow:0 8px 30px rgba(52,211,153,.35)}
.stApp .st-key-cta_explore button:hover{background:linear-gradient(135deg,#86efac,#4ade80 55%,#34d399);color:#03150e;transform:translateY(-2px);box-shadow:0 12px 38px rgba(52,211,153,.5)}
.ghost-btn{display:inline-flex;align-items:center;height:46px;padding:0 1.6rem;border-radius:999px;border:1px solid rgba(255,255,255,.35);color:#fff!important;text-decoration:none!important;font-weight:600;font-size:.95rem;transition:all .25s}
.ghost-btn:hover{background:rgba(255,255,255,.1);border-color:#fff;transform:translateY(-2px)}

/* ---------- feature cards & chips ---------- */
.feat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.1rem;margin:1.4rem 0 1.6rem;scroll-margin-top:90px}
.feat-card{position:relative;padding:1.5rem 1.5rem 1.3rem;border-radius:22px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(8px);
 transition:transform .3s,border-color .3s,box-shadow .3s,background .3s;animation:fadeUp .8s both cubic-bezier(.2,.8,.2,1)}
.feat-card:hover{transform:translateY(-6px);border-color:rgba(52,211,153,.55);background:rgba(16,185,129,.07);box-shadow:0 18px 50px rgba(16,185,129,.14)}
.feat-ico{width:54px;height:54px;border-radius:16px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(52,211,153,.3);background:rgba(16,185,129,.09);margin-bottom:1rem;transition:transform .3s}
.feat-card:hover .feat-ico{transform:scale(1.08) rotate(-4deg)}
.feat-title{font-size:1.08rem;font-weight:600;color:#fff;margin-bottom:.5rem}
.feat-card p{margin:0;color:var(--mut);font-size:.9rem;line-height:1.6}
.feat-card b{color:#d1fae5;font-weight:600}
.chip-label{color:var(--mut);font-size:.78rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;margin:.4rem 0 .7rem}
.chips{display:flex;flex-wrap:wrap;gap:.55rem}
.chip{padding:.45rem .95rem;border-radius:999px;border:1px solid var(--line);background:var(--card);color:#cfe0da;font-size:.82rem;font-weight:500;transition:all .25s}
.chip:hover{border-color:var(--g);color:#fff;background:rgba(16,185,129,.12);transform:translateY(-2px)}

/* ---------- shared widgets on the other pages ---------- */
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1rem 1.2rem;transition:border-color .25s,transform .25s}
[data-testid="stMetric"]:hover{border-color:rgba(52,211,153,.5);transform:translateY(-2px)}
[data-testid="stAlert"]{border-radius:16px;border:1px solid var(--line)}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:16px!important;background:var(--card)}
[data-testid="stForm"]{border:1px solid var(--line);border-radius:22px;background:var(--card);padding:1.4rem}
.stTabs [data-baseweb="tab-highlight"]{background:var(--g)}
.stTabs [aria-selected="true"]{color:#fff}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]{border-radius:12px!important}

/* ---------- keyframes ---------- */
@keyframes navIn{from{opacity:0;transform:translate(-50%,-18px)}to{opacity:1;transform:translate(-50%,0)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes pulse{0%,100%{opacity:.75;transform:scale(1)}50%{opacity:1;transform:scale(1.05)}}
@keyframes rise{0%{transform:translateY(0);opacity:0}20%{opacity:.9}100%{transform:translateY(-130px);opacity:0}}

/* ---------- responsive ---------- */
@media(max-width:900px){
 .brand span{display:none}
 .st-key-hero{padding:2rem 1.2rem 1.4rem;min-height:0;border-radius:24px}
 .hero-visual svg{max-height:380px}
 .block-container{padding-top:5.6rem;padding-left:1rem;padding-right:1rem}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""

# ---------------------------------------------------------------------------
# public API used by app.py
# ---------------------------------------------------------------------------
def inject_global_css():
    st.markdown(_flat_css(GLOBAL_CSS), unsafe_allow_html=True)


def _flat_css(css: str) -> str:
    return "\n".join(line.strip() for line in css.splitlines() if line.strip())


def render_top_nav(pages):
    """Glass top navigation bar. Returns the selected page name (same contract as the old sidebar radio)."""
    with _kc("topnav"):
        c_brand, c_nav = st.columns([1.2, 5])
        c_brand.markdown(_flat(BRAND_HTML), unsafe_allow_html=True)
        with c_nav:
            return st.radio(
                "Navigation", pages, horizontal=True,
                label_visibility="collapsed", key=NAV_KEY,
            )


def render_home_hero():
    """Cinematic hero + feature cards + architecture chips for the Home page."""
    with _kc("hero"):
        left, right = st.columns([1.05, 1], gap="large")
        with left:
            st.markdown(_flat(HERO_COPY), unsafe_allow_html=True)
            b1, b2, _spare = st.columns([1.3, 1, 1])
            b1.button("Explore Dashboard  →", key="cta_explore", on_click=_go, args=("Device Inventory",))
            b2.markdown('<a class="ghost-btn" href="#features" target="_self">Learn More</a>', unsafe_allow_html=True)
        with right:
            st.markdown(_flat(HERO_VISUAL), unsafe_allow_html=True)
    st.markdown(_flat(FEATURES), unsafe_allow_html=True)
    st.markdown(_flat(CHIPS), unsafe_allow_html=True)
    