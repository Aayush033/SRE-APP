from core.states import IncidentState, EmailDraft
from tools.context_compactor import compact_chat_context

def run_comms_agent(state: IncidentState) -> IncidentState:
    """
    Ingests developer slack chat transcripts, filters panic,
    and drafts executive updates in Calm, Technical, and Crisis tones.
    """
    if not state.chat_history:
        return state
        
    last_chat = state.chat_history[-1]
    
    # Track reasoning steps
    state.agent_reasoning_logs.append({
        "timestamp": last_chat.timestamp,
        "agent": "Comms Sync",
        "level": "info",
        "message": f"Ingested developer message from {last_chat.sender}. Executing context compaction..."
    })

    # Run compaction
    compacted_signals = compact_chat_context(state.chat_history)
    
    # Print compaction summary to agent logs
    state.agent_reasoning_logs.append({
        "timestamp": last_chat.timestamp,
        "agent": "Comms Sync",
        "level": "success",
        "message": f"Context Compactor compressed {len(state.chat_history)} chat records into {len(compacted_signals)} high-signal SRE alerts. Low-signal chatter removed."
    })

    # Draft emails based on the current compacted context
    state.comms_email_drafts["calm"] = draft_calm_email(state, compacted_signals)
    state.comms_email_drafts["technical"] = draft_technical_email(state, compacted_signals)
    state.comms_email_drafts["crisis"] = draft_crisis_email(state, compacted_signals)

    return state

def draft_calm_email(state: IncidentState, signals: list[str]) -> EmailDraft:
    scenario = state.scenario_name
    is_mitigating = state.status == "MITIGATING"
    is_resolved = state.status == "RESOLVED"
    
    subject = f"UPDATE: {state.status} - Operational Status Update on E-Commerce Infrastructure"
    
    status_text = "Triage In Progress"
    if is_resolved:
        status_text = "Incident Fully Resolved"
    elif is_mitigating:
        status_text = "Mitigation Steps In Progress. System Metrics Normalizing."

    bullets = "\n".join([f"* {sig}" for sig in signals])

    body = f"""Dear Leadership Team,

We are responding to an infrastructure anomaly. Below is an update on the current status and our remediation pipeline.

**Current Incident Status:** {status_text}
**Target Scenario:** {scenario}
**Active Duration:** {state.elapsed_seconds // 60} minutes

**Key Diagnostic Signals (Compacted):**
{bullets}

**Operations Actions Taken:**
* The engineering war room has been established to stabilize active requests.
* Edge resolvers and server resources are currently being balanced.
{"* System performance has normalized. We are verifying post-incident reliability." if is_resolved else "* Engineering teams are continuing work towards full baseline resolution."}

We will send a complete post-mortem report once root cause analyses are validated.

Sincerely,
SRE-Brain Comms Sync Agent"""

    return EmailDraft(subject=subject, body=body, tone="calm")

def draft_technical_email(state: IncidentState, signals: list[str]) -> EmailDraft:
    subject = f"TECHNICAL UPDATE: {state.status} | {state.scenario_key.upper()} outage event"
    bullets = "\n".join([f"- {sig}" for sig in signals])
    
    body = f"""TECHNICAL INCIDENT STATUS UPDATE:
Status: {state.status}
Incident Timer: {state.elapsed_seconds}s
Vitals: Latency={state.latency_ms}ms, DB_Connections={state.db_connections}, Error_Rate={state.error_rate}%, SLA={state.sla_percent:.4f}%

**Extracted Diagnostic Timeline Signals:**
{bullets}

**Engineering Log Analytics:**
- System metrics indicate CPU consumption at {state.cpu_percent}% capacity.
- Database active capacity running at {state.db_connections} slots.
- Service level compliance currently calculated at {state.sla_percent:.4f}%: {"[BREACHED]" if state.is_sla_breached else "[NOMINAL]"}.

**Mitigation Node Details:**
- Circuit breakers: {"ENGAGED" if state.status in ["MITIGATING", "RESOLVED"] else "NOMINAL"}
- Cluster deployment: {"ROLLBACK VERIFIED" if state.status in ["MITIGATING", "RESOLVED"] and state.scenario_key == "checkout_storm" else "STABLE RELEASE"}
"""
    return EmailDraft(subject=subject, body=body, tone="technical")

def draft_crisis_email(state: IncidentState, signals: list[str]) -> EmailDraft:
    subject = f"🚨 ALERT: CRITICAL INFRASTRUCTURE CRISIS - {state.status} (SEV-1)"
    bullets = "\n".join([f"• {sig}" for sig in signals])
    
    body = f"""⚠️ CRITICAL INCIDENT ALERT ⚠️
An active infrastructure breakdown is currently impacting transactional workflows.

**Current Outage Vitals:**
* SLA Compliance: {state.sla_percent:.4f}% (Warning: SLA contract breach {"ACTIVE" if state.is_sla_breached else "IMMINENT"})
* HTTP Error Rates: {state.error_rate}%
* API Response Time: {state.latency_ms}ms

**Incident Path Events:**
{bullets}

**Immediate Actions:**
All operations staff are on high alert. Triage efforts are currently working to release system thread lockouts. Next update will be issued in 10 minutes.
"""
    return EmailDraft(subject=subject, body=body, tone="crisis")
