from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class LogEntry(BaseModel):
    timestamp: str
    level: str  # info, warning, error, critical, success, system
    message: str

class ChatMessage(BaseModel):
    timestamp: str
    sender: str
    message: str
    is_panic: bool = False

class TimelineEvent(BaseModel):
    timestamp: str
    severity: str  # critical, warning, success
    title: str
    message: str

class EmailDraft(BaseModel):
    subject: str
    body: str
    tone: str  # calm, technical, crisis

class IncidentState(BaseModel):
    incident_id: str = "INC-000"
    scenario_key: str = "checkout_storm"
    scenario_name: str = "Nominal System Operations"
    status: str = "HEALTHY"  # HEALTHY, CRITICAL, MITIGATING, RESOLVED
    
    # Simulation Clock
    elapsed_seconds: int = 0
    
    # Live Vitals Metrics
    latency_ms: int = 24
    cpu_percent: int = 8
    db_connections: int = 12
    error_rate: float = 0.05
    req_rate: float = 900.0
    sla_percent: float = 99.99
    is_sla_breached: bool = False
    total_financial_loss: float = 0.0
    
    # Logging Data Sources
    raw_logs: List[LogEntry] = []
    chat_history: List[ChatMessage] = []
    
    # Agent Output Stores
    factual_timeline: List[TimelineEvent] = []
    comms_email_drafts: Dict[str, EmailDraft] = {}  # keyed by tone name
    post_mortem_report: Optional[str] = None
    
    # Internal agent reasoning logs
    agent_reasoning_logs: List[Dict[str, str]] = []  # dict with 'agent', 'level', 'message', 'timestamp'
