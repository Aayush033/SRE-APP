from typing import List, Dict

def read_slack_channel_history(channel: str = "incident-war-room") -> List[Dict[str, str]]:
    """
    Mock Slack MCP Tool.
    Simulates reading developer war-room chat history transcripts from a Slack channel.
    """
    return [
        {"timestamp": "12:01", "sender": "Bob", "message": "Confirming checkout latency is climbing. Spiked to 1.8s."}
    ]

def post_slack_notification(message: str, channel: str = "incident-war-room") -> bool:
    """
    Mock Slack MCP Tool.
    Simulates posting automated agent status updates and notifications to Slack.
    """
    print(f"[Slack MCP] POST to #{channel}: {message}")
    return True
