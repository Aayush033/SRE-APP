from core.states import IncidentState
from core.session import IncidentSession
from agents.telemetry_agent import run_telemetry_agent
from agents.comms_agent import run_comms_agent
from agents.post_mortem_agent import run_post_mortem_agent

class IncidentGraph:
    """
    SRE-Brain ADK 2.0 Graph Definition.
    
    Models the cyclic workflow:
    [Start] -> Telemetry Agent -> Comms Agent -> Is Resolved?
                                                    |
                                          (No) -----+ (Yes)
                                          |           |
                                    [Loop Node]  Post-Mortem Agent -> [End]
    """
    
    def __init__(self):
        self.nodes = {
            "telemetry": run_telemetry_agent,
            "comms": run_comms_agent,
            "post_mortem": run_post_mortem_agent
        }

    def execute_step(self) -> IncidentState:
        """
        Executes a single step of the graph cycle. 
        Usually triggered in real-time by incoming logs or telemetry events.
        """
        state = IncidentSession.get_state()
        
        # Guard if already completed
        if state.status == "RESOLVED" and state.post_mortem_report:
            return state

        # Trace execution start
        IncidentSession.add_reasoning_log(
            "Graph Engine", "info", 
            f"Initializing execution step. Current incident status: {state.status}"
        )

        # 1. Execute Telemetry Triage node
        IncidentSession.add_reasoning_log("Graph Engine", "info", "Routing to TelemetryAgent...")
        state = self.nodes["telemetry"](state)
        IncidentSession.set_state(state)

        # 2. Execute Comms Sync node
        IncidentSession.add_reasoning_log("Graph Engine", "info", "Routing to CommsSyncAgent...")
        state = self.nodes["comms"](state)
        IncidentSession.set_state(state)

        # 3. Router check: Is resolved?
        if state.status == "RESOLVED":
            IncidentSession.add_reasoning_log("Graph Engine", "success", "Incident resolved condition: TRUE. Routing to PostMortemAgent.")
            state = self.nodes["post_mortem"](state)
            IncidentSession.set_state(state)
            IncidentSession.add_reasoning_log("Graph Engine", "success", "Graph execution completed successfully.")
        else:
            # Cyclic path
            IncidentSession.add_reasoning_log(
                "Graph Engine", "warning", 
                "Incident resolved condition: FALSE. Loop back to standby state. Awaiting next telemetry tick."
            )
            
        return state

    def execute_full_run(self, max_cycles: int = 50) -> IncidentState:
        """
        Runs the cyclic execution engine sequentially for simulation tests.
        Continuously loops processing telemetry logs until incident resolves.
        """
        state = IncidentSession.get_state()
        cycle = 0
        
        while state.status != "RESOLVED" and cycle < max_cycles:
            cycle += 1
            IncidentSession.add_reasoning_log("Graph Engine", "info", f"Executing automatic cycle iteration #{cycle}")
            state = self.execute_step()
            
        return state
