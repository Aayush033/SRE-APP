from core.states import IncidentState
from typing import Optional

class IncidentSession:
    _instance: Optional['IncidentSession'] = None
    _state: IncidentState = IncidentState()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IncidentSession, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_state(cls) -> IncidentState:
        return cls._state

    @classmethod
    def set_state(cls, new_state: IncidentState) -> None:
        cls._state = new_state

    @classmethod
    def reset(cls) -> None:
        cls._state = IncidentState()

    @classmethod
    def add_reasoning_log(cls, agent: str, level: str, message: str) -> None:
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        cls._state.agent_reasoning_logs.append({
            "timestamp": timestamp,
            "agent": agent,
            "level": level,
            "message": message
        })
