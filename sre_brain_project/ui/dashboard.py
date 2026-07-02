"""
SRE-Brain: Chaos Mitigation & Post-Mortem Dashboard
A Streamlit-based Command Center for real-time SRE incident simulation.
"""
import sys
import os
import time
import datetime
import pandas as pd
import altair as alt
import streamlit as st

# Add project root to path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.states import IncidentState, LogEntry, ChatMessage
from core.session import IncidentSession
from core.graph import IncidentGraph
from tools.mock_telemetry import SCENARIO_DATABASE
from skills.calculate_impact import calculate_downtime_cost

# ──────────────────────────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SRE-Brain: Chaos Mitigation Center",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────
# Inject Custom CSS for premium dark theme
# ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global background */
.stApp { background-color: #080a14; }

/* Sidebar */
section[data-testid="stSidebar"] { background-color: #0f1225; border-right: 1px solid rgba(255,255,255,0.08); }

/* Headings */
h1 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important;
     background: linear-gradient(to right, #ffffff, #b388ff); -webkit-background-clip: text;
     -webkit-text-fill-color: transparent; }
h2, h3, h4 { font-family: 'Outfit', sans-serif !important; color: #f1f3f9 !important; }

/* Metric Cards */
div[data-testid="stMetric"] { background: #0f1225; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
div[data-testid="stMetric"] label { font-family: 'Outfit', sans-serif !important;
    font-size: 0.75rem !important; text-transform: uppercase; color: #8d96b0 !important; }

/* Terminal blocks */
code, pre { font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important; }

/* Status badge shimmer */
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
.status-badge { display: inline-block; padding: 4px 14px; border-radius: 20px; font-weight: 700;
    font-size: 0.8rem; letter-spacing: 1px; font-family: 'JetBrains Mono', monospace; }
.status-healthy { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
.status-critical { background: rgba(255,23,68,0.15); color: #ff1744; border: 1px solid rgba(255,23,68,0.3);
    animation: shimmer 2s infinite linear; background-size: 200% 100%;
    background-image: linear-gradient(90deg, rgba(255,23,68,0.15) 0%, rgba(255,23,68,0.3) 50%, rgba(255,23,68,0.15) 100%); }
.status-mitigating { background: rgba(255,145,0,0.15); color: #ff9100; border: 1px solid rgba(255,145,0,0.3); }
.status-resolved { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }

/* Chat log styles */
.chat-msg { border-left: 3px solid #7c4dff; padding: 6px 12px; margin-bottom: 10px; border-radius: 0 4px 4px 0;
    background: rgba(124,77,255,0.04); }
.chat-msg.panic { border-left-color: #ff1744; background: rgba(255,23,68,0.04); }
.chat-sender { font-weight: 700; font-size: 0.8rem; color: #c5a3ff; }
.chat-time { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #8d96b0; float: right; }
.chat-text { font-size: 0.82rem; color: #e2e5f0; }

/* Timeline events */
.tl-item { border-left: 3px solid #7c4dff; padding: 8px 14px; margin-bottom: 12px; border-radius: 0 6px 6px 0; }
.tl-item.crit { border-left-color: #ff1744; background: rgba(255,23,68,0.04); }
.tl-item.warn { border-left-color: #ff9100; background: rgba(255,145,0,0.04); }
.tl-item.ok   { border-left-color: #00e676; background: rgba(0,230,118,0.04); }
.tl-time { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #00e5ff; }
.tl-title { font-size: 0.85rem; font-weight: 700; color: #fff; }
.tl-desc { font-size: 0.75rem; color: #8d96b0; }

/* Agent log console */
.agent-log { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; padding: 3px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04); }
.agent-log .ts  { color: #8d96b0; }
.agent-log .ag  { color: #00e5ff; }
.agent-log .msg { color: #f1f3f9; }
.agent-log.err .msg { color: #ff1744; }
.agent-log.warn .msg { color: #ff9100; }
.agent-log.ok .msg { color: #00e676; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "sim_running": False,
        "sim_phase": "HEALTHY",
        "log_idx": 0,
        "chat_idx": 0,
        "elapsed": 0,
        "sla": 99.99,
        "metrics_history": [],
        "scenario_key": "checkout_storm",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Always reset the singleton session object from session_state
    IncidentSession.reset()

init_session()


# ──────────────────────────────────────────────────────────────────
# Helper: Load Scenario Into State
# ──────────────────────────────────────────────────────────────────
def load_scenario(key: str):
    sc = SCENARIO_DATABASE[key]
    state = IncidentState(
        incident_id=f"INC-{key.upper()}-{datetime.date.today()}",
        scenario_key=key,
        scenario_name=sc["name"],
        status="CRITICAL",
    )
    # Load ALL telemetry and chat into the state so agents can process them
    for log in sc["telemetry"]:
        state.raw_logs.append(LogEntry(timestamp=log["timestamp"], level=log["level"], message=log["message"]))
    for chat in sc["chat"]:
        import re
        is_panic = bool(re.search(r"\b(omg|god|screaming|losing|dead|fail|error)\b", chat["message"], re.I))
        state.chat_history.append(ChatMessage(
            timestamp=chat["timestamp"], sender=chat["sender"],
            message=chat["message"], is_panic=is_panic
        ))
    IncidentSession.set_state(state)
    return state


# ──────────────────────────────────────────────────────────────────
# Helper: Run Full Graph Cycle
# ──────────────────────────────────────────────────────────────────
def run_full_simulation(key: str):
    """Loads a scenario, runs the cyclic graph, and returns final state."""
    state = load_scenario(key)
    sc = SCENARIO_DATABASE[key]

    # Simulate metric progression
    metrics_history = []
    for i, m in enumerate(sc["metrics"]):
        metrics_history.append({
            "step": i, "Latency (ms)": m["latency"], "CPU (%)": m["cpu"],
            "DB Connections": m["db"], "Error Rate (%)": m["errors"], "Requests/s": m["reqs"]
        })
    st.session_state["metrics_history"] = metrics_history

    # Simulate elapsed time
    state.elapsed_seconds = len(sc["telemetry"]) * 15
    state.latency_ms = sc["metrics"][-1]["latency"]
    state.cpu_percent = sc["metrics"][-1]["cpu"]
    state.db_connections = sc["metrics"][-1]["db"]
    state.error_rate = sc["metrics"][-1]["errors"]
    state.req_rate = sc["metrics"][-1]["reqs"]

    # Degrade SLA during crisis
    state.sla_percent = 99.99 - (len([m for m in sc["metrics"] if m["errors"] > 1.0]) * 0.008)
    if state.sla_percent < 99.90:
        state.is_sla_breached = True

    # Mark as resolved so graph proceeds to post-mortem
    state.status = "RESOLVED"
    IncidentSession.set_state(state)

    # Execute the graph (Telemetry -> Comms -> Resolved? -> Post-Mortem)
    graph = IncidentGraph()
    state = graph.execute_step()

    # Compute financial loss
    state.total_financial_loss = calculate_downtime_cost(state.elapsed_seconds, key)
    IncidentSession.set_state(state)

    st.session_state["sim_running"] = True
    st.session_state["sim_phase"] = "RESOLVED"
    st.session_state["elapsed"] = state.elapsed_seconds
    st.session_state["sla"] = state.sla_percent


# ──────────────────────────────────────────────────────────────────
# Sidebar: Incident Command
# ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🖥️ Incident Command")
    scenario = st.selectbox(
        "Select Simulation Scenario",
        options=list(SCENARIO_DATABASE.keys()),
        format_func=lambda k: SCENARIO_DATABASE[k]["name"],
        key="scenario_key_select",
    )

    if st.button("⚡ Trigger Incident & Run Full Simulation", type="primary", use_container_width=True):
        run_full_simulation(scenario)
        st.session_state["scenario_key"] = scenario

    if st.button("🔄 Reset Dashboard", use_container_width=True):
        for k in ["sim_running", "sim_phase", "log_idx", "chat_idx", "elapsed", "sla", "metrics_history"]:
            if k in st.session_state:
                del st.session_state[k]
        IncidentSession.reset()
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. Select a scenario and **Trigger Incident**
    2. The **cyclic graph** executes:
       - `Telemetry Agent` → `Comms Agent` → Resolved? 
       - If No → Loop. If Yes → `Post-Mortem Agent`
    3. View timeline, executive emails, and auto-generated post-mortem report
    """)


# ──────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────
st.markdown("# 🔥 SRE-Brain: Chaos Mitigation & Post-Mortem Center")

state = IncidentSession.get_state()
phase = st.session_state.get("sim_phase", "HEALTHY")

# Status badge
badge_class = {"HEALTHY": "status-healthy", "CRITICAL": "status-critical",
               "MITIGATING": "status-mitigating", "RESOLVED": "status-resolved"}.get(phase, "status-healthy")
st.markdown(f'<span class="status-badge {badge_class}">SYSTEM STATUS: {phase}</span>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# Top Metrics Row
# ──────────────────────────────────────────────────────────────────
if st.session_state.get("sim_running"):
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Incident Clock", f"{state.elapsed_seconds // 60}m {state.elapsed_seconds % 60}s")
    m2.metric("Latency", f"{state.latency_ms}ms")
    m3.metric("CPU", f"{state.cpu_percent}%")
    m4.metric("Error Rate", f"{state.error_rate}%")
    m5.metric("SLA", f"{state.sla_percent:.4f}%")
    m6.metric("💰 Est. Loss", f"${state.total_financial_loss:,.0f}")

    # ──────────────────────────────────────────────────────────────
    # Telemetry Charts
    # ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 System Telemetry Vitals")
    metrics_df = pd.DataFrame(st.session_state.get("metrics_history", []))
    if not metrics_df.empty:
        ch1, ch2 = st.columns(2)
        with ch1:
            latency_chart = alt.Chart(metrics_df).mark_area(
                line={"color": "#00e5ff", "strokeWidth": 2},
                color=alt.Gradient(gradient="linear", stops=[
                    alt.GradientStop(color="rgba(0,229,255,0.3)", offset=0),
                    alt.GradientStop(color="rgba(0,229,255,0.0)", offset=1)
                ], x1=0, x2=0, y1=0, y2=1)
            ).encode(
                x=alt.X("step:Q", title="Time Step", axis=alt.Axis(grid=False)),
                y=alt.Y("Latency (ms):Q", title="Latency (ms)")
            ).properties(height=220, title="API Latency")
            st.altair_chart(latency_chart, use_container_width=True)

        with ch2:
            error_chart = alt.Chart(metrics_df).mark_area(
                line={"color": "#ff1744", "strokeWidth": 2},
                color=alt.Gradient(gradient="linear", stops=[
                    alt.GradientStop(color="rgba(255,23,68,0.3)", offset=0),
                    alt.GradientStop(color="rgba(255,23,68,0.0)", offset=1)
                ], x1=0, x2=0, y1=0, y2=1)
            ).encode(
                x=alt.X("step:Q", title="Time Step", axis=alt.Axis(grid=False)),
                y=alt.Y("Error Rate (%):Q", title="Error Rate (%)")
            ).properties(height=220, title="Error Rate")
            st.altair_chart(error_chart, use_container_width=True)

    # ──────────────────────────────────────────────────────────────
    # Main Content: 3-Column Layout
    # ──────────────────────────────────────────────────────────────
    st.markdown("---")
    col_left, col_center, col_right = st.columns([1, 1, 1])

    # LEFT: Raw Telemetry + Chat
    with col_left:
        st.markdown("### 📟 Raw Telemetry Stream")
        log_html = ""
        for log in state.raw_logs:
            color = {"critical": "#ff1744", "error": "#ff1744", "warning": "#ff9100",
                     "success": "#00e676", "info": "#e2e5f0"}.get(log.level, "#8d96b0")
            log_html += f'<div style="font-family: JetBrains Mono, monospace; font-size:0.72rem; color:{color}; margin-bottom:4px;"><span style="color:#8d96b0">[{log.timestamp}]</span> {log.message}</div>'
        st.markdown(f'<div style="background:#030408; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px; max-height:400px; overflow-y:auto;">{log_html}</div>', unsafe_allow_html=True)

        st.markdown("### 💬 Developer War Room Chat")
        chat_html = ""
        for msg in state.chat_history:
            cls = "panic" if msg.is_panic else ""
            chat_html += f'<div class="chat-msg {cls}"><span class="chat-time">{msg.timestamp}</span><div class="chat-sender">{msg.sender}</div><div class="chat-text">{msg.message}</div></div>'
        st.markdown(f'<div style="background:#0d0f1b; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px; max-height:400px; overflow-y:auto;">{chat_html}</div>', unsafe_allow_html=True)

    # CENTER: Triage Timeline + Comms Email
    with col_center:
        st.markdown("### 🔍 Triage Timeline")
        if state.factual_timeline:
            tl_html = ""
            for ev in state.factual_timeline:
                cls = {"critical": "crit", "warning": "warn", "success": "ok"}.get(ev.severity, "")
                tl_html += f'<div class="tl-item {cls}"><div class="tl-time">{ev.timestamp}</div><div class="tl-title">{ev.title}</div><div class="tl-desc">{ev.message}</div></div>'
            st.markdown(f'<div style="max-height:400px; overflow-y:auto;">{tl_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Waiting for telemetry triage data...")

        st.markdown("### 📧 Executive Email (Comms Agent)")
        tone = st.selectbox("Email Tone", ["calm", "technical", "crisis"], key="email_tone")
        if tone in state.comms_email_drafts:
            email = state.comms_email_drafts[tone]
            st.markdown(f"**Subject:** {email.subject}")
            st.markdown(f'<div style="background:#0d0f1b; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:16px; font-size:0.82rem; color:#e2e5f0; white-space:pre-wrap; max-height:350px; overflow-y:auto;">{email.body}</div>', unsafe_allow_html=True)
        else:
            st.info("Comms Sync Agent has not generated emails yet.")

    # RIGHT: Post-Mortem Report
    with col_right:
        st.markdown("### 📝 Post-Mortem Report")
        if state.post_mortem_report:
            st.markdown(state.post_mortem_report)
            st.download_button(
                "⬇️ Download Markdown Report",
                data=state.post_mortem_report,
                file_name=f"SRE_PostMortem_{state.scenario_key}_{datetime.date.today()}.md",
                mime="text/markdown",
            )
        else:
            st.info("Post-Mortem Writer will activate when the incident resolves.")

    # ──────────────────────────────────────────────────────────────
    # Agent Reasoning Console
    # ──────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🤖 Agent Thought Stream & Reasoning Protocol", expanded=False):
        if state.agent_reasoning_logs:
            log_html = ""
            for entry in state.agent_reasoning_logs:
                lvl_cls = {"error": "err", "warning": "warn", "success": "ok"}.get(entry.get("level", ""), "")
                log_html += f'<div class="agent-log {lvl_cls}"><span class="ts">[{entry["timestamp"]}]</span> <span class="ag">[{entry["agent"]}]</span> <span class="msg">{entry["message"]}</span></div>'
            st.markdown(f'<div style="background:#030408; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px; max-height:350px; overflow-y:auto;">{log_html}</div>', unsafe_allow_html=True)
        else:
            st.caption("Agent reasoning logs will appear here during incident processing.")
else:
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:3rem; margin-bottom:16px;">🖥️</div>
        <h3 style="color:#8d96b0;">SRE-Brain Incident Simulator</h3>
        <p style="color:#8d96b0; font-size:0.9rem; max-width:500px; margin:0 auto;">
            Select a corporate emergency scenario from the sidebar and click 
            <strong>Trigger Incident</strong> to watch the multi-agent system mitigate chaos in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)
