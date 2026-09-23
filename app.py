import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #dce6f2;
}

.stApp {
    background: #05070d;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(40,110,255,0.16) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(20,60,180,0.14) 0%, transparent 55%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── GitHub icon (top-right) ── */
.github-corner {
    position: fixed;
    top: 1.2rem;
    right: 1.5rem;
    z-index: 9999;
}
.github-corner svg {
    width: 28px;
    height: 28px;
    fill: #8b9bb4;
    transition: fill 0.2s, transform 0.2s;
}
.github-corner:hover svg {
    fill: #4d94ff;
    transform: scale(1.1);
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #4d94ff;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #eef3fb;
    margin: 0 0 1rem;
}
.hero h1 span {
    color: #4d94ff;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #8b9bb4;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(77,148,255,0.35), transparent);
    margin: 2rem 0;
}

/* ── Input card (real container, targeted via st.container(key=...)) ── */
.st-key-input_card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(77,148,255,0.18);
    border-radius: 16px;
    padding: 2rem 2.5rem 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(77,148,255,0.3) !important;
    border-radius: 10px !important;
    color: #eef3fb !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4d94ff !important;
    box-shadow: 0 0 0 3px rgba(77,148,255,0.15) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #4d94ff !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #2f6dff 0%, #0f3ecf 100%) !important;
    color: #eef3fb !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(47,109,255,0.35) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(47,109,255,0.45) !important;
    opacity: 0.95 !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.step-card.active {
    border-color: rgba(77,148,255,0.45);
    background: rgba(77,148,255,0.05);
}
.step-card.done {
    border-color: rgba(60,200,180,0.3);
    background: rgba(60,200,180,0.04);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #4d94ff; }
.step-card.done::before   { background: #3cc8b4; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #4d94ff;
    opacity: 0.75;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #eef3fb;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
}
.status-waiting  { color: #4a5568; }
.status-running  { color: #4d94ff; }
.status-done     { color: #3cc8b4; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4d94ff;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(77,148,255,0.18);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #c3cee0;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(77,148,255,0.25);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(60,200,180,0.25);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.blue {
    color: #4d94ff;
    border-bottom: 1px solid rgba(77,148,255,0.18);
}
.panel-label.teal {
    color: #3cc8b4;
    border-bottom: 1px solid rgba(60,200,180,0.18);
}

/* ── Progress text ── */
.stSpinner > div { color: #4d94ff !important; }

/* ── Expander ── */
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #8b9bb4 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #eef3fb;
    margin: 2rem 0 1rem;
}

/* ── Example chips (clickable buttons) ── */
.chip-row-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #4a5568;
    letter-spacing: 0.1em;
    padding-top: 0.45rem;
    white-space: nowrap;
}
.st-key-chip_row .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
    padding: 0.25rem 0.7rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    letter-spacing: normal !important;
    color: #8b9bb4 !important;
    box-shadow: none !important;
    width: auto !important;
    white-space: nowrap;
}
.st-key-chip_row .stButton > button:hover {
    background: rgba(77,148,255,0.12) !important;
    border-color: rgba(77,148,255,0.35) !important;
    color: #cfe0ff !important;
    transform: none !important;
    box-shadow: none !important;
}
.st-key-chip_row .stButton > button:active {
    transform: none !important;
}

/* ── Toast-style notice ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #4a5568;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
.notice a {
    color: #4d94ff;
    text-decoration: none;
}
.notice a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)


# ── GitHub icon (fixed, top-right corner) ─────────────────────────────────────
st.markdown("""
<a href="https://github.com/Abhik004" target="_blank" class="github-corner" title="View on GitHub">
    <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
        0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
        -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07
        -1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82
        .64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12
        .51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
        0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
    </svg>
</a>
""", unsafe_allow_html=True)


# ── Helper: build a step card's HTML (returned, not drawn directly, so it can
#            be pushed into a st.empty() placeholder and updated live) ────────
def step_card_html(num: str, title: str, state: str, desc: str = "") -> str:
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    return f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#5f6f8a;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """


STEP_META = [
    ("search", "01", "Search Agent",  "Gathers recent web information"),
    ("reader", "02", "Reader Agent",  "Scrapes & extracts deep content"),
    ("writer", "03", "Writer Chain",  "Drafts the full research report"),
    ("critic", "04", "Critic Chain",  "Reviews & scores the report"),
]


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    # st.container(key=...) is a REAL DOM wrapper (unlike a raw markdown div
    # split across separate st calls), so the CSS actually wraps the widgets
    # inside it instead of floating as an empty box above them.
    with st.container(key="input_card"):
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Quantum computing breakthroughs in 2025",
            key="topic_input",
            label_visibility="visible",
        )
        run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)

    # Example chips — clickable; each one fills the Research Topic field.
    # Using on_click (a callback) is what makes this safe: callbacks run
    # BEFORE the script reruns, so session_state["topic_input"] gets set
    # ahead of the text_input widget being (re)created above.
    def _set_topic_from_chip(value: str):
        st.session_state["topic_input"] = value

    chip_examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]

    with st.container(key="chip_row"):
        chip_cols = st.columns([0.6, 1.4, 1.7, 1.9], gap="small")
        chip_cols[0].markdown('<div class="chip-row-label">TRY →</div>', unsafe_allow_html=True)
        for i, ex in enumerate(chip_examples):
            chip_cols[i + 1].button(
                ex,
                key=f"chip_{i}",
                on_click=_set_topic_from_chip,
                args=(ex,),
            )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    # One st.empty() slot per step. Because these are real placeholders, we
    # can push fresh HTML into them *during* the pipeline run below and the
    # UI updates immediately — no need to wait for a full script rerun.
    pipeline_slots = {key: st.empty() for key, *_ in STEP_META}

    def render_step(key: str, state: str):
        for k, num, title, desc in STEP_META:
            if k == key:
                pipeline_slots[k].markdown(step_card_html(num, title, state, desc), unsafe_allow_html=True)
                return

    def render_pipeline_from_results():
        """Paint all 4 cards based on whatever is currently in session_state."""
        r = st.session_state.results
        running = st.session_state.running
        seen_running = False
        for k, num, title, desc in STEP_META:
            if k in r:
                state = "done"
            elif running and not seen_running:
                state = "running"
                seen_running = True
            else:
                state = "waiting"
            pipeline_slots[k].markdown(step_card_html(num, title, state, desc), unsafe_allow_html=True)

    render_pipeline_from_results()


# ── Trigger pipeline ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

# ── Run pipeline (executes on the rerun triggered above) ────────────────────
if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    render_step("search", "running")
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
    render_step("search", "done")

    # ── Step 2: Reader ──
    render_step("reader", "running")
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)
    render_step("reader", "done")

    # ── Step 3: Writer ──
    render_step("writer", "running")
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)
    render_step("writer", "done")

    # ── Step 4: Critic ──
    render_step("critic", "running")
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)
    render_step("critic", "done")

    st.session_state.running = False
    st.session_state.done = True
    # No st.rerun() needed here — the pipeline cards were already updated live
    # via render_step() above, and execution just falls through to the
    # Results section below in this same script run.


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label blue">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label teal">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    Made by <a href="https://github.com/Abhik004" target="_blank">Abhik</a>
    · ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)