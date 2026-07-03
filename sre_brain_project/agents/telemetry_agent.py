from core.states import IncidentState, TimelineEvent
from typing import List
import os

# ─────────────────────────────────────────────────────────────────────────────
# Optional Gemini AI Integration
# Set GOOGLE_API_KEY env var to enable LLM-powered root cause hypothesis.
# Falls back gracefully to rule-based analysis if key is not present.
# ─────────────────────────────────────────────────────────────────────────────
_gemini_available = False
try:
    # UPDATED: Import from the new genai SDK
    from google import genai
    _api_key = os.environ.get("GOOGLE_API_KEY", "")
    if _api_key:
        # UPDATED: Initialize the Client instead of global configure
        _gemini_client = genai.Client(api_key=_api_key)
        _gemini_available = True
except ImportError:
    pass


def _generate_rca_hypothesis(timeline_summary: str, scenario_key: str) -> str:
    """
    Uses Gemini to generate a concise root-cause hypothesis from detected events.
    Returns an empty string if Gemini is unavailable.
    """
    if not _gemini_available:
        return ""
    try:
        prompt = (
            f"You are an expert Site Reliability Engineer (SRE).\n"
            f"Scenario: {scenario_key}\n"
            f"Detected incident timeline:\n{timeline_summary}\n\n"
            f"In 2-3 sentences, provide a concise root cause hypothesis "
            f"explaining why this outage occurred and what the likely trigger was."
        )
        # UPDATED: Use client.models.generate_content and pass both model and contents
        response = _gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        # Optional: Print or log 'e' here if you want to debug silent failures later
        return ""

def run_telemetry_agent(state: IncidentState) -> IncidentState:
    """
    Scans the latest raw log entries, detects errors, and updates the timeline.
    """
    # Track which lines have already been triage parsed by checking timeline counts
    parsed_count = len(state.factual_timeline)
    current_logs = state.raw_logs
    
    if len(current_logs) <= parsed_count:
        # No new logs to process
        return state

    new_logs = current_logs[parsed_count:]
    state.agent_reasoning_logs.append({
        "timestamp": state.raw_logs[-1].timestamp if state.raw_logs else "12:00:00",
        "agent": "Telemetry Triage",
        "level": "info",
        "message": f"Processing {len(new_logs)} new telemetry log streams."
    })

    for log in new_logs:
        timeline_event = None
        
        # Parse error patterns
        msg_lower = log.message.lower()
        if "critical" in msg_lower or "fatal" in msg_lower:
            timeline_event = TimelineEvent(
                timestamp=log.timestamp,
                severity="critical",
                title="Infrastructure Critical Error",
                message=log.message
            )
            state.agent_reasoning_logs.append({
                "timestamp": log.timestamp,
                "agent": "Telemetry Triage",
                "level": "error",
                "message": f"CRITICAL alert signatures matched: '{log.message}'. Appending to timeline coordinates."
            })
            
        elif "error" in msg_lower or "503" in msg_lower or "504" in msg_lower:
            timeline_event = TimelineEvent(
                timestamp=log.timestamp,
                severity="critical",
                title="API Service Failure",
                message=log.message
            )
            state.agent_reasoning_logs.append({
                "timestamp": log.timestamp,
                "agent": "Telemetry Triage",
                "level": "error",
                "message": f"ERROR signature isolated: '{log.message}'. Target node: API Gateway boundary."
            })
            
        elif "warning" in msg_lower or "exceeded" in msg_lower or "limit" in msg_lower:
            timeline_event = TimelineEvent(
                timestamp=log.timestamp,
                severity="warning",
                title="Latency / Capacity Warning",
                message=log.message
            )
            state.agent_reasoning_logs.append({
                "timestamp": log.timestamp,
                "agent": "Telemetry Triage",
                "level": "warning",
                "message": f"RESOURCE WARNING detected: '{log.message}'. Queue scaling might be required."
            })
            
        elif "mitigat" in msg_lower or "terminat" in msg_lower or "restart" in msg_lower:
            timeline_event = TimelineEvent(
                timestamp=log.timestamp,
                severity="success",
                title="Mitigation Action Executed",
                message=log.message
            )
            state.agent_reasoning_logs.append({
                "timestamp": log.timestamp,
                "agent": "Telemetry Triage",
                "level": "info",
                "message": f"MITIGATION SIGNATURE logged: '{log.message}'."
            })
            
        elif "success" in msg_lower or "nominal" in msg_lower or "stabilized" in msg_lower or "resolved" in msg_lower:
            timeline_event = TimelineEvent(
                timestamp=log.timestamp,
                severity="success",
                title="Service Normalization Verified",
                message=log.message
            )
            state.agent_reasoning_logs.append({
                "timestamp": log.timestamp,
                "agent": "Telemetry Triage",
                "level": "success",
                "message": f"RECOVERY SIGNATURE verified: '{log.message}'. Normal status returning."
            })

        if timeline_event:
            state.factual_timeline.append(timeline_event)

    # ── Gemini AI: Root Cause Hypothesis ─────────────────────────────────────
    if _gemini_available and state.factual_timeline:
        timeline_summary = "\n".join(
            f"[{ev.timestamp}] {ev.severity.upper()}: {ev.title} — {ev.message}"
            for ev in state.factual_timeline[-6:]  # Last 6 events for context window
        )
        hypothesis = _generate_rca_hypothesis(timeline_summary, state.scenario_key)
        if hypothesis:
            state.agent_reasoning_logs.append({
                "timestamp": state.raw_logs[-1].timestamp if state.raw_logs else "12:00:00",
                "agent": "Telemetry Triage [Gemini AI]",
                "level": "info",
                "message": f"🤖 AI Root Cause Hypothesis: {hypothesis}"
            })

    return state