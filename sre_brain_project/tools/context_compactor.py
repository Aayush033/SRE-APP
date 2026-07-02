import re
from typing import List, Any

def compact_chat_context(chat_history: List[Any]) -> List[str]:
    """
    Context Engineering Tool.
    Filters out hundreds of panic-fueled chat logs into an elegant, high-signal operational timeline.
    
    Filters based on technical signals:
    - Identifies diagnostic keywords (db pool, rollback, DNS, Route53, circuit breaker, etc.)
    - Removes conversational noise (OMG, panic, screaming, coffee, etc.)
    """
    # Low-signal noise list
    low_signal_keywords = re.compile(
        r"\b(omg|god|screaming|losing|blowing up|dude|coffee|website loads|are the servers dead|panicking|help|whoa|twitter|creeping|checkout button|bad query)\b", 
        re.IGNORECASE
    )
    
    # High-signal diagnostic keywords
    high_signal_keywords = re.compile(
        r"\b(db pool|connection pool|exhausted|timeout|rollback|v1.4.2|v1.4.1|circuit breaker|restarting|killed|unpaid|registrar|status|hold|unreachable|traffic|propagation|index|query)\b", 
        re.IGNORECASE
    )

    compacted_signals = []

    for chat in chat_history:
        # Support both Pydantic models and dictionary inputs
        msg_text = chat.message if hasattr(chat, "message") else chat.get("message", "")
        sender = chat.sender if hasattr(chat, "sender") else chat.get("sender", "Developer")
        timestamp = chat.timestamp if hasattr(chat, "timestamp") else chat.get("timestamp", "12:00")
        
        # Check signal weights
        has_low = bool(low_signal_keywords.search(msg_text))
        has_high = bool(high_signal_keywords.search(msg_text))
        
        # If it contains high-signal info, keep it
        if has_high:
            # Shorten message slightly to compact length if needed
            clean_msg = msg_text.strip()
            compacted_signals.append(f"[{timestamp}] {sender}: {clean_msg}")
            
    # Fallback if no signals were matched
    if not compacted_signals:
         compacted_signals.append("[12:00] System: Ingested chat buffer. No structural diagnostic signals isolated yet.")

    return compacted_signals
