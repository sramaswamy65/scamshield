"""ScamShield — a presentation-ready Streamlit application."""

from __future__ import annotations

import html
import time
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_explainer import generate_explanation
from database import history_dataframe, save_analysis, seed_demo_data
from message_analyzer import analyze_message


st.set_page_config(
    page_title="ScamShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


SAMPLES = {
    "Bank Account Warning": (
        "URGENT: Your First National Bank account will be suspended today. "
        "Verify your security code and bank account at "
        "https://example.com/secure/verify immediately."
    ),
    "Package Delivery Scam": (
        "Your package is waiting for delivery. Confirm your address at "
        "https://example.com/parcel/confirm to avoid a return."
    ),
    "IRS / Tax Scam": (
        "This is the IRS. Your tax refund is on hold. Pay the processing fee "
        "within 24 hours at https://example.com/tax/claim."
    ),
    "Prize Winner Scam": (
        "Congratulations, you are a prize winner! Claim your reward by paying "
        "a small processing fee at https://example.com/reward/claim."
    ),
    "Safe Message": (
        "Hi Suresh, our project meeting tomorrow is still scheduled for 10:00 AM. "
        "See you then."
    ),
}

PAGES = [
    "Dashboard",
    "Analyze Message",
    "AI Risk Analysis",
    "Investigation",
    "Recommended Action",
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
          --ink: #e9f2f5;
          --muted: #8ba1ab;
          --panel: #10232b;
          --panel-strong: #122b35;
          --line: rgba(140, 190, 199, 0.16);
          --cyan: #48d9d1;
          --green: #67e8a4;
          --amber: #f5c76b;
          --red: #ff6d77;
        }
        html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
        .stApp {
          background:
            radial-gradient(circle at 85% 0%, rgba(39, 118, 127, .18), transparent 32rem),
            linear-gradient(135deg, #07141a 0%, #081c23 52%, #07151c 100%);
          color: var(--ink);
        }
        [data-testid="stHeader"] { background: rgba(7, 20, 26, .74); }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0a1d25 0%, #07151b 100%);
          border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
        .block-container { padding: 2.1rem 3.3rem 3rem; max-width: 1500px; }
        h1, h2, h3, h4 { letter-spacing: -.04em; color: var(--ink); }
        h1 { font-weight: 800; font-size: clamp(2rem, 4vw, 3.65rem); line-height: 1; }
        h2 { font-weight: 800; }
        p, li, label { color: var(--muted); }
        .brand-lockup { display: flex; align-items: center; gap: .75rem; margin-bottom: 2.3rem; }
        .brand-mark {
          width: 38px; height: 38px; display: grid; place-items: center;
          border-radius: 12px; color: #06151a; background: var(--cyan);
          font-size: 1.2rem; font-weight: 800; box-shadow: 0 0 22px rgba(72,217,209,.22);
        }
        .brand-name { color: var(--ink); font-weight: 800; font-size: 1rem; }
        .brand-tag { color: var(--muted); font-size: .66rem; letter-spacing: .16em; text-transform: uppercase; }
        .eyebrow { color: var(--cyan); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .15em; text-transform: uppercase; }
        .subhead { max-width: 680px; font-size: 1rem; line-height: 1.7; color: var(--muted); }
        .status-pill { display: inline-flex; align-items: center; gap: .42rem; padding: .38rem .7rem; border-radius: 999px; background: rgba(103,232,164,.08); color: var(--green); border: 1px solid rgba(103,232,164,.2); font: 500 .68rem 'DM Mono', monospace; letter-spacing: .06em; text-transform: uppercase; }
        .status-dot { width: 7px; height: 7px; background: var(--green); border-radius: 50%; box-shadow: 0 0 10px var(--green); }
        .panel {
          background: linear-gradient(140deg, rgba(18,43,53,.96), rgba(12,31,39,.9));
          border: 1px solid var(--line); border-radius: 18px; padding: 1.35rem 1.45rem;
          box-shadow: 0 18px 60px rgba(0,0,0,.12);
        }
        .kpi-label { color: var(--muted); font-size: .73rem; letter-spacing: .06em; text-transform: uppercase; }
        .kpi-value { color: var(--ink); font-size: 2.1rem; font-weight: 800; letter-spacing: -.06em; margin-top: .35rem; }
        .kpi-foot { color: var(--muted); font-size: .75rem; margin-top: .25rem; }
        .risk-low { color: var(--green) !important; }
        .risk-medium { color: var(--amber) !important; }
        .risk-high { color: var(--red) !important; }
        .risk-badge { display: inline-block; border-radius: 999px; padding: .35rem .65rem; font: 700 .7rem 'DM Mono', monospace; letter-spacing: .08em; }
        .badge-low { color: var(--green); background: rgba(103,232,164,.1); border: 1px solid rgba(103,232,164,.25); }
        .badge-medium { color: var(--amber); background: rgba(245,199,107,.1); border: 1px solid rgba(245,199,107,.25); }
        .badge-high { color: var(--red); background: rgba(255,109,119,.1); border: 1px solid rgba(255,109,119,.25); }
        .section-title { margin: 1.9rem 0 .9rem; display:flex; align-items:center; justify-content:space-between; }
        .section-title h3 { margin: 0; font-size: 1.15rem; }
        .section-kicker { color: var(--muted); font-size: .78rem; }
        .hero-score { padding: 1.6rem; border-radius: 22px; background: radial-gradient(circle at 75% 50%, rgba(72,217,209,.09), transparent 28rem), rgba(12,31,39,.9); border: 1px solid var(--line); }
        .score-number { font-size: clamp(4rem, 10vw, 7rem); font-weight: 800; letter-spacing: -.1em; line-height: .95; }
        .score-caption { color: var(--muted); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .15em; text-transform: uppercase; }
        .score-track { height: 8px; border-radius: 8px; background: #1c343c; overflow: hidden; margin-top: 1.25rem; }
        .score-fill { height: 100%; border-radius: inherit; }
        .indicator-card { min-height: 112px; padding: 1rem; border-radius: 14px; background: rgba(12,31,39,.82); border: 1px solid var(--line); }
        .indicator-card h4 { margin: 0 0 .55rem; font-size: .85rem; letter-spacing: -.02em; }
        .indicator-state { font: 500 .7rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
        .workflow-card { min-height: 180px; padding: 1.15rem; border-radius: 16px; background: rgba(12,31,39,.9); border: 1px solid rgba(103,232,164,.2); position: relative; }
        .workflow-index { color: var(--cyan); font: 500 .7rem 'DM Mono', monospace; }
        .workflow-check { color: var(--green); float: right; font-weight: 800; }
        .workflow-card h4 { margin: .7rem 0 .45rem; font-size: 1rem; }
        .workflow-card p { font-size: .78rem; line-height: 1.55; margin: 0; }
        .action-hero { padding: 1.65rem; border-radius: 20px; border: 1px solid rgba(255,109,119,.3); background: linear-gradient(120deg, rgba(98,31,42,.72), rgba(25,28,39,.86)); }
        .action-hero.medium { border-color: rgba(245,199,107,.3); background: linear-gradient(120deg, rgba(96,71,28,.62), rgba(25,28,39,.86)); }
        .action-hero.low { border-color: rgba(103,232,164,.3); background: linear-gradient(120deg, rgba(25,82,70,.55), rgba(25,28,39,.86)); }
        .action-hero h2 { margin: .55rem 0 .4rem; }
        .message-box { padding: 1.15rem 1.25rem; border: 1px solid var(--line); border-radius: 14px; background: #081a21; color: #c9d9dd; line-height: 1.7; font-size: .92rem; white-space: pre-wrap; }
        mark { background: rgba(245,199,107,.24); color: #ffe7a7; padding: .1rem .25rem; border-radius: 4px; }
        .sidebar-stat { padding: .8rem 0; border-top: 1px solid var(--line); }
        .sidebar-stat strong { color: var(--ink); display:block; font-size: 1.2rem; }
        .sidebar-stat span { color: var(--muted); font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; }
        div[data-testid="stButton"] > button {
          border-radius: 10px; font-weight: 700; min-height: 2.7rem; transition: all .2s ease;
          border: 1px solid rgba(72,217,209,.3); background: rgba(72,217,209,.08); color: var(--ink);
        }
        div[data-testid="stButton"] > button:hover { border-color: var(--cyan); color: var(--cyan); transform: translateY(-1px); }
        div[data-testid="stButton"] > button[kind="primary"] { background: var(--cyan); color: #06151a; border-color: var(--cyan); }
        div[data-testid="stTextArea"] textarea { background: #081a21; border: 1px solid var(--line); border-radius: 14px; color: var(--ink); line-height: 1.6; }
        div[data-testid="stTextArea"] textarea:focus { border-color: var(--cyan); box-shadow: 0 0 0 1px var(--cyan); }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
        .stProgress > div > div > div > div { background: var(--cyan); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_color(level: str) -> str:
    return {"LOW": "#67e8a4", "MEDIUM": "#f5c76b", "HIGH": "#ff6d77"}.get(
        level, "#48d9d1"
    )


def badge(level: str) -> str:
    return f'<span class="risk-badge badge-{level.lower()}">{level} RISK</span>'


def render_sidebar(history: pd.DataFrame) -> str:
    st.sidebar.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark">S</div>
          <div><div class="brand-name">ScamShield</div><div class="brand-tag">Threat intelligence, simplified</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    current_page = st.sidebar.radio(
        "Workspace",
        PAGES,
        index=PAGES.index(st.session_state.get("page", "Dashboard")),
        label_visibility="collapsed",
    )
    st.session_state["page"] = current_page

    total = len(history)
    high_count = int((history["risk_level"] == "HIGH").sum()) if total else 0
    st.sidebar.markdown(
        f"""
        <div style="margin: 1.4rem 0 1.1rem;"><span class="status-pill"><span class="status-dot"></span> Engine online</span></div>
        <div class="sidebar-stat"><strong>{total}</strong><span>Messages analyzed</span></div>
        <div class="sidebar-stat"><strong>{high_count}</strong><span>High-risk findings</span></div>
        <div class="sidebar-stat"><strong>Local-first</strong><span>Scoring mode</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div style="margin-top:2rem; font-size:.72rem; line-height:1.6; color:#8ba1ab;">URLs are inspected as untrusted text only. ScamShield never opens links supplied in messages.</div>',
        unsafe_allow_html=True,
    )
    return current_page


def page_header(eyebrow: str, title: str, description: str) -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="subhead">{description}</div>', unsafe_allow_html=True)


def render_dashboard(history: pd.DataFrame) -> None:
    page_header(
        "Security operations / overview",
        "Know before you click.",
        "ScamShield combines transparent risk signals with an AI-assisted safety advisor to help you slow down, verify, and stay in control.",
    )
    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
    if st.button("Analyze a Message", type="primary", width="content"):
        st.session_state["page"] = "Analyze Message"
        st.rerun()

    total = len(history)
    high_count = int((history["risk_level"] == "HIGH").sum()) if total else 0
    avg_score = round(float(history["risk_score"].mean())) if total else 0
    common = (
        history["scam_category"].value_counts().index[0]
        if total
        else "No data"
    )
    st.markdown('<div class="section-title"><h3>Signal snapshot</h3><span class="section-kicker">Live from SQLite history</span></div>', unsafe_allow_html=True)
    cards = [
        ("Messages Analyzed", str(total), "Across this workspace"),
        ("High Risk Messages", str(high_count), "Requires immediate caution"),
        ("Average Risk Score", f"{avg_score}%", "Deterministic engine output"),
        ("Most Common Scam Type", common, "Detected category"),
    ]
    columns = st.columns(4)
    for column, (label, value, foot) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="panel"><div class="kpi-label">{label}</div><div class="kpi-value">{html.escape(value)}</div><div class="kpi-foot">{foot}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown('<div class="section-title"><h3>Risk distribution</h3><span class="section-kicker">All analyzed messages</span></div>', unsafe_allow_html=True)
        counts = (
            history["risk_level"].value_counts()
            .reindex(["LOW", "MEDIUM", "HIGH"])
            .fillna(0)
            .rename_axis("Risk level")
            .reset_index(name="Messages")
        )
        chart = px.bar(
            counts,
            x="Risk level",
            y="Messages",
            color="Risk level",
            color_discrete_map={"LOW": "#67e8a4", "MEDIUM": "#f5c76b", "HIGH": "#ff6d77"},
        )
        chart.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8ba1ab",
            showlegend=False,
            margin=dict(l=10, r=10, t=15, b=10),
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor="rgba(140,190,199,.12)", title=None),
        )
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    with right:
        st.markdown('<div class="section-title"><h3>How the score works</h3><span class="section-kicker">Transparent by design</span></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel" style="height:300px;">
              <div style="font:500 .72rem 'DM Mono',monospace;color:#48d9d1;letter-spacing:.1em;">SIGNAL → WEIGHT → SCORE</div>
              <p style="margin-top:1.1rem;line-height:1.65;">The risk engine looks for pressure tactics, credential requests, financial asks, impersonation, and suspicious URL structure.</p>
              <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-top:1.2rem;">
                <span class="risk-badge badge-low">0–29 LOW</span>
                <span class="risk-badge badge-medium">30–69 MEDIUM</span>
                <span class="risk-badge badge-high">70–100 HIGH</span>
              </div>
              <p style="font-size:.75rem;margin-top:1.2rem;">Generative AI may improve the wording of the explanation, but it never controls the numeric score.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title"><h3>Recent analyses</h3><span class="section-kicker">Newest first</span></div>', unsafe_allow_html=True)
    recent = history.head(8).copy()
    if not recent.empty:
        recent["timestamp"] = recent["timestamp"].dt.strftime("%b %d, %H:%M")
        recent = recent.rename(
            columns={
                "timestamp": "Time",
                "message_excerpt": "Message",
                "risk_score": "Score",
                "risk_level": "Risk",
                "scam_category": "Category",
                "indicators": "Indicators",
            }
        )
        st.dataframe(
            recent[["Time", "Message", "Score", "Risk", "Category", "Indicators"]],
            width="stretch",
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score", min_value=0, max_value=100, format="%d%%"
                )
            },
        )


def render_analyze_page() -> None:
    page_header(
        "Message intake / safe by default",
        "Analyze a suspicious message.",
        "Paste the message exactly as you received it. ScamShield reads the text, inspects visible URL patterns, and never visits a supplied link.",
    )
    st.markdown('<div class="section-title"><h3>Try a demo message</h3><span class="section-kicker">Fictional examples · safe domains only</span></div>', unsafe_allow_html=True)
    sample_columns = st.columns(5)
    for column, label in zip(sample_columns, SAMPLES):
        with column:
            if st.button(label, key=f"sample_{label}", width="stretch"):
                st.session_state["message_input"] = SAMPLES[label]
                st.session_state["selected_sample"] = label
                st.rerun()

    st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
    message = st.text_area(
        "Message to inspect",
        key="message_input",
        height=230,
        placeholder="Paste an email, SMS, WhatsApp message, or suspicious message below.",
        label_visibility="collapsed",
    )
    selected = st.session_state.get("selected_sample")
    if selected:
        st.caption(f"Loaded demo: {selected}")

    if st.button("Analyze Message", type="primary", width="stretch"):
        if not message.strip():
            st.error("Paste a message or choose one of the demo examples first.")
            return
        with st.status("Running ScamShield analysis", expanded=True) as status:
            steps = [
                "Reading message...",
                "Checking suspicious language...",
                "Inspecting URLs...",
                "Calculating risk...",
                "Generating recommendation...",
            ]
            for step in steps:
                st.write(step)
                time.sleep(0.16)
            result = analyze_message(message)
            explanation, source = generate_explanation(message, result)
            result["explanation"] = explanation
            result["explanation_source"] = source
            save_analysis(result)
            st.session_state["latest_result"] = result
            st.session_state["page"] = "AI Risk Analysis"
            status.update(label="Analysis complete", state="complete", expanded=False)
        st.rerun()


def highlighted_message(message: str, evidence: list[str]) -> str:
    safe = html.escape(message)
    for phrase in sorted(set(evidence), key=len, reverse=True):
        escaped_phrase = html.escape(phrase)
        safe = safe.replace(escaped_phrase, f"<mark>{escaped_phrase}</mark>")
    return safe


def render_risk_page(result: dict[str, Any] | None) -> None:
    page_header(
        "AI risk analysis / evidence",
        "The signal is clear.",
        "A transparent risk readout that separates deterministic evidence from optional generative explanation.",
    )
    if not result:
        st.info("Analyze a message first to see its risk analysis.")
        if st.button("Go to Analyze Message", type="primary"):
            st.session_state["page"] = "Analyze Message"
            st.rerun()
        return

    level = result["level"]
    color = risk_color(level)
    st.markdown(
        f"""
        <div class="hero-score" style="margin-top:1.5rem;">
          <div class="score-caption">SCAM RISK SCORE</div>
          <div style="display:flex;align-items:end;gap:1.2rem;margin-top:.7rem;">
            <div class="score-number" style="color:{color};">{result['score']}<span style="font-size:2.2rem;letter-spacing:-.05em;">%</span></div>
            <div style="padding-bottom:.5rem;">{badge(level)}<div style="color:#8ba1ab;font-size:.78rem;margin-top:.6rem;">{html.escape(result['category'])}</div></div>
          </div>
          <div class="score-track"><div class="score-fill" style="width:{result['score']}%;background:{color};box-shadow:0 0 16px {color};"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    indicator_data = [
        ("Urgency Detected", result["indicator_status"]["urgency"], "Pressure tactics"),
        ("Credential Request", result["indicator_status"]["credentials"], "Passwords or codes"),
        ("Suspicious Link", result["indicator_status"]["suspicious_link"], "URL structure"),
        ("Financial Request", result["indicator_status"]["financial"], "Money or payment"),
        ("Impersonation", result["indicator_status"]["impersonation"], "Claimed identity"),
        ("Scam Category", result["category"], "Classification"),
    ]
    st.markdown('<div class="section-title"><h3>Signal indicators</h3><span class="section-kicker">What the engine found</span></div>', unsafe_allow_html=True)
    indicator_columns = st.columns(3)
    for index, (title, value, note) in enumerate(indicator_data):
        with indicator_columns[index % 3]:
            if isinstance(value, bool):
                state = "Detected" if value else "Not detected"
                state_class = "risk-high" if value else "risk-low"
            else:
                state = str(value)
                state_class = "risk-medium"
            st.markdown(
                f'<div class="indicator-card"><h4>{title}</h4><div class="indicator-state {state_class}">{html.escape(state)}</div><div style="color:#8ba1ab;font-size:.7rem;margin-top:.5rem;">{note}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title"><h3>Message evidence</h3><span class="section-kicker">Suspicious phrases highlighted</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="message-box">{highlighted_message(result["message"], result.get("evidence", []))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title"><h3>Why ScamShield flagged this message</h3><span class="section-kicker">Safety advisor</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="panel"><p style="color:#c9d9dd;line-height:1.75;margin:0;">{html.escape(result["explanation"])}</p><div style="margin-top:1rem;color:#8ba1ab;font-size:.7rem;font-family:DM Mono,monospace;">SOURCE: {html.escape(result["explanation_source"])}</div></div>',
        unsafe_allow_html=True,
    )
    if result.get("urls"):
        st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
        st.caption("URL inspection is text-only; no link was opened.")
        for item in result["urls"]:
            url_status = "Suspicious structure detected" if item["suspicious"] else "No structural flags"
            st.markdown(
                f'<div style="padding:.6rem 0;border-bottom:1px solid rgba(140,190,199,.12);font-size:.78rem;"><span style="color:#c9d9dd;">{html.escape(item["url"])}</span><span style="float:right;color:{color};">{url_status}</span></div>',
                unsafe_allow_html=True,
            )


def render_investigation_page(result: dict[str, Any] | None) -> None:
    page_header(
        "Investigation / agent trace",
        "See the investigation unfold.",
        "Four focused components turn an untrusted message into a clear, actionable safety decision.",
    )
    if not result:
        st.info("Analyze a message first to populate the investigation trace.")
        if st.button("Go to Analyze Message", type="primary"):
            st.session_state["page"] = "Analyze Message"
            st.rerun()
        return

    workflow = [
        (
            "01",
            "Message Analyzer",
            "Analyzes urgency, threats, credential requests, and suspicious language.",
            [signal["label"] for signal in result["rule_signals"][:3]] or ["No language flags"],
        ),
        (
            "02",
            "URL Inspector",
            "Finds URLs and evaluates suspicious URL characteristics without opening them.",
            [signal["label"] for signal in result["url_signals"]] or ["No URL flags"],
        ),
        (
            "03",
            "Risk Engine",
            "Combines security indicators and calculates the deterministic risk score.",
            [f"{result['score']}% {result['level']} RISK", result["category"]],
        ),
        (
            "04",
            "Safety Advisor",
            "Generates a calm recommendation explaining what the user should do next.",
            ["Recommendation ready", result["explanation_source"]],
        ),
    ]
    columns = st.columns(4, gap="medium")
    for column, (number, title, description, indicators) in zip(columns, workflow):
        with column:
            chips = "".join(
                f'<div style="padding:.35rem .5rem;margin-top:.35rem;border-radius:7px;background:rgba(72,217,209,.07);color:#b8d4d7;font-size:.68rem;">{html.escape(indicator)}</div>'
                for indicator in indicators
            )
            st.markdown(
                f'<div class="workflow-card"><span class="workflow-index">{number} / COMPONENT</span><span class="workflow-check">Completed ✓</span><h4>{title}</h4><p>{description}</p><div style="margin-top:1rem;">{chips}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="panel"><div class="eyebrow">Investigation summary</div><p style="color:#c9d9dd;line-height:1.7;margin:.7rem 0 0;">The pipeline completed all four checks and returned <strong style="color:{risk_color(result["level"])};">{result["score"]}% {result["level"]} RISK</strong>. The numeric result is reproducible from the visible indicators above.</p></div>',
        unsafe_allow_html=True,
    )


def render_action_page(result: dict[str, Any] | None) -> None:
    page_header(
        "Recommended action / next step",
        "Take the safe next step.",
        "When a message creates pressure, the safest response is to pause and verify through a known official channel.",
    )
    if not result:
        st.info("Analyze a message first to receive a recommendation.")
        if st.button("Go to Analyze Message", type="primary"):
            st.session_state["page"] = "Analyze Message"
            st.rerun()
        return

    level = result["level"]
    if level == "HIGH":
        title = "DO NOT RESPOND OR CLICK LINKS"
        intro = "This message has multiple high-confidence scam indicators. Treat it as untrusted."
        actions = [
            "Do not click links in the message.",
            "Do not provide passwords or verification codes.",
            "Do not provide financial information.",
            "Contact the organization through its official website, app, or known phone number.",
            "Block the sender if appropriate.",
            "Report the message as phishing or spam.",
        ]
    elif level == "MEDIUM":
        title = "VERIFY BEFORE TAKING ACTION"
        intro = "Some suspicious patterns were detected. Pause and confirm the request independently."
        actions = [
            "Do not use contact details or links provided in the message.",
            "Look up the organization through a trusted source.",
            "Ask whether the request is expected before sharing information.",
            "Keep passwords, codes, and payment details private.",
        ]
    else:
        title = "NO MAJOR SCAM INDICATORS DETECTED"
        intro = "The message looks routine based on the signals ScamShield checks, but stay alert to context."
        actions = [
            "If the request feels unexpected, verify it through a known channel.",
            "Keep personal information private.",
            "Remember that a low risk score does not guarantee legitimacy.",
        ]

    st.markdown(
        f'<div class="action-hero {level.lower()}"><div class="eyebrow">{level} risk response</div><h2>{title}</h2><p style="color:#c9d9dd;margin:0;line-height:1.6;">{intro}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title"><h3>Recommended checklist</h3><span class="section-kicker">Stay in control</span></div>', unsafe_allow_html=True)
    for action in actions:
        st.markdown(
            f'<div class="panel" style="margin:.55rem 0;padding:.85rem 1rem;"><span style="color:{risk_color(level)};font-weight:800;margin-right:.7rem;">✓</span><span style="color:#c9d9dd;font-size:.86rem;">{action}</span></div>',
            unsafe_allow_html=True,
        )
    if level == "LOW":
        st.warning("A low risk score does not guarantee that a message is legitimate.")
    st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        if st.button("Analyze Another Message", type="primary", width="stretch"):
            st.session_state["page"] = "Analyze Message"
            st.session_state["message_input"] = ""
            st.session_state["selected_sample"] = None
            st.rerun()
    with right:
        if st.button("Return to Dashboard", width="stretch"):
            st.session_state["page"] = "Dashboard"
            st.rerun()


def main() -> None:
    seed_demo_data()
    inject_styles()
    history = history_dataframe()
    page = render_sidebar(history)
    result = st.session_state.get("latest_result")

    if page == "Dashboard":
        render_dashboard(history)
    elif page == "Analyze Message":
        render_analyze_page()
    elif page == "AI Risk Analysis":
        render_risk_page(result)
    elif page == "Investigation":
        render_investigation_page(result)
    else:
        render_action_page(result)


if __name__ == "__main__":
    main()