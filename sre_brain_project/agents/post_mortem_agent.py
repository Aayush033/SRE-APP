from core.states import IncidentState
from skills.calculate_impact import calculate_downtime_cost
from skills.mcp_github import get_recent_pr_context
import datetime
import os

# ─────────────────────────────────────────────────────────────────────────────
# Optional Gemini AI Integration
# ─────────────────────────────────────────────────────────────────────────────
_gemini_available = False
try:
    import google.generativeai as genai
    _api_key = os.environ.get("GOOGLE_API_KEY", "")
    if _api_key:
        genai.configure(api_key=_api_key)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        _gemini_available = True
except ImportError:
    pass


def _generate_lessons_learned(scenario_name: str, rca_description: str, cost: float) -> str:
    """
    Uses Gemini to generate a personalized 'Lessons Learned' section.
    Returns a static fallback if Gemini is unavailable.
    """
    if not _gemini_available:
        return (
            "- Apply the Five Whys methodology to all future Severity-1 incidents.\n"
            "- Schedule a blameless post-mortem review within 48 hours of resolution.\n"
            "- Update runbooks with detection and remediation steps from this incident."
        )
    try:
        prompt = (
            f"You are a senior SRE writing an incident post-mortem.\n"
            f"Incident: {scenario_name}\n"
            f"Root cause: {rca_description}\n"
            f"Financial loss: ${cost:,.2f}\n\n"
            f"Write exactly 3 concise, actionable 'Lessons Learned' bullet points "
            f"that engineering teams should implement to prevent recurrence. "
            f"Each bullet should start with a dash and be on its own line."
        )
        response = _gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return (
            "- Apply the Five Whys methodology to all future Severity-1 incidents.\n"
            "- Schedule a blameless post-mortem review within 48 hours of resolution.\n"
            "- Update runbooks with detection and remediation steps from this incident."
        )

def run_post_mortem_agent(state: IncidentState) -> IncidentState:
    """
    Assembles the final incident timeline, root cause analysis, 
    and estimated financial costs into a formal Markdown report.
    """
    state.agent_reasoning_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Post-Mortem Writer",
        "level": "info",
        "message": "Incident resolution verified. Starting report draft pipeline."
    })

    # 1. Calculate financial impact using portable skill
    total_cost = calculate_downtime_cost(state.elapsed_seconds, state.scenario_key)
    state.total_financial_loss = total_cost
    
    state.agent_reasoning_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Post-Mortem Writer",
        "level": "info",
        "message": f"Calculated financial damage using impact calculator skill: ${total_cost:,.2f}"
    })

    # 2. Extract commit details / PR records from Github MCP
    state.agent_reasoning_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Post-Mortem Writer",
        "level": "info",
        "message": "Invoking GitHub MCP Server to fetch recent pull requests..."
    })
    github_pr_info = get_recent_pr_context(state.scenario_key)
    
    state.agent_reasoning_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Post-Mortem Writer",
        "level": "success",
        "message": f"Isolated root-cause code modifications: '{github_pr_info['pr_title']}' merged by {github_pr_info['author']}."
    })

    # 3. Compile report markdown content
    report_markdown = compile_report_md(state, total_cost, github_pr_info)
    state.post_mortem_report = report_markdown

    state.agent_reasoning_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Post-Mortem Writer",
        "level": "success",
        "message": "Post-Mortem markdown draft compiled successfully."
    })

    return state

def compile_report_md(state: IncidentState, cost: float, github_info: dict) -> str:
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    downtime_str = f"{state.elapsed_seconds // 60}m {state.elapsed_seconds % 60}s"
    
    # Render timeline lines
    timeline_rows = ""
    for ev in state.factual_timeline:
        level_badge = "🔴 CRITICAL" if ev.severity == "critical" else ("🟡 WARNING" if ev.severity == "warning" else "🟢 SUCCESS")
        timeline_rows += f"| {ev.timestamp} | {level_badge} | **{ev.title}**: {ev.message} |\n"

    # Preventions checklist
    preventions_list = ""
    if state.scenario_key == "checkout_storm":
        preventions = [
            "Ensure database connections are closed using proper context managers (try-finally).",
            "Establish automated capacity alerts on connection pool utilization.",
            "Test new feature deployment under realistic high-load simulations before major sales events."
        ]
    elif state.scenario_key == "dns_cascade":
        preventions = [
            "Migrate secondary domain properties to centralized enterprise registries with multi-year renewals.",
            "Deploy external synthetic domain watchers that alert immediately on DNS resolution failures.",
            "Establish secondary billing pathways for registrars with backup credit limits."
        ]
    else:
        preventions = [
            "Implement strict socket request timeout durations on all downstream client configurations.",
            "Integrate dynamic circuit breakers that drop slow auxiliary dependencies automatically.",
            "Scale API container pods based on thread pool occupancy parameters."
        ]

    for p in preventions:
        preventions_list += f"- [ ] {p}\n"

    md = f"""# INCIDENT POST-MORTEM

**Document ID:** PM-{state.scenario_key.upper()}-{date_str}
**Status:** DRAFT APPROVED
**Incident Level:** Severity 1 (SLA Breaching outage)
**Date of Incident:** {date_str}
**Total Downtime:** {downtime_str}
**Financial Loss Impact:** ${cost:,.2f} USD
**SLA Retention Metric:** {state.sla_percent:.4f}%

---

## 1. Executive Summary
On {date_str}, our e-commerce operations experienced a major outage classified as *{state.scenario_name}*. Core checkout and payment flows were compromised, resulting in transaction failures for customers globally. SRE-Brain triggered active monitoring and automated triaging nodes. Systems were stabilized in {downtime_str} via engineering hotfix deployments.

---

## 2. Root Cause Diagnostics (RCA)
> [!IMPORTANT]
> **Primary Cause & Trigger:**
> The outage was triggered by pull request **#{github_info['pr_id']}** ("*{github_info['pr_title']}*") merged by **{github_info['author']}** into production code. 
> 
> *Technical Detail:* 
> {github_info['rca_description']}

---

## 3. Incident Timeline
| Timestamp | Event Level | Action / Telemetry Log Entry |
| :--- | :--- | :--- |
{timeline_rows}
---

## 4. Remediation & Recovery Steps
The following corrective actions were applied to restore systems to normal operations:
"""

    if state.scenario_key == "checkout_storm":
        md += """1. Dynamically scaled database active connection limit allocations from 100 to 200.
2. Executed cleanup scripts killing hanging locks on the coupons table.
3. Initiated container cluster rollbacks, reinstating release `checkout-v1.4.1` and purging leaked sessions."""
    elif state.scenario_key == "dns_cascade":
        md += """1. Logged into Registrar Console to pay outstanding billing invoices.
2. Verified WHOIS lock lifted and domain state active.
3. Cleared local DNS resolver parameters on CDN caching edges to accelerate zone propagation."""
    else:
        md += """1. Triggered configurations opening promotions-service circuit breakers.
2. Restarted checkout API container pods to purge dead socket socket loops.
3. DBA implemented database index adjustments for analytics queries."""

    md += f"""

---

## 5. Preventative Action Items
To prevent recurrences of this incident, we have scheduled the following deliverables:
{preventions_list}
---

## 6. Lessons Learned
{'> [!NOTE]' if _gemini_available else ''}
{'> **AI-Generated by Gemini (google/gemini-1.5-flash)**' if _gemini_available else ''}
{_generate_lessons_learned(state.scenario_name, github_info['rca_description'], cost)}

---
*Auto-drafted by **SRE-Brain: Post-Mortem Writer Agent**.*
{'*Lessons Learned section enhanced by Google Gemini AI.*' if _gemini_available else ''}"""

    return md
