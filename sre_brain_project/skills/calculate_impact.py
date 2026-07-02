def calculate_downtime_cost(elapsed_seconds: int, scenario_key: str) -> float:
    """
    Day 3 Portable Agent Skill.
    Estimates downtime cost in dollars based on elapsed seconds and business sector metrics.
    """
    # Financial rates per minute of system failure
    rates_per_minute = {
        "checkout_storm": 8500.0,   # Black Friday transaction rate loss
        "dns_cascade": 4000.0,      # DNS routing complete traffic drop loss
        "latency_loop": 3200.0      # Partial checkout blockage thread delay loss
    }
    
    rate = rates_per_minute.get(scenario_key, 1500.0) # default custom lab rate
    elapsed_minutes = elapsed_seconds / 60.0
    
    total_cost = elapsed_minutes * rate
    return round(total_cost, 2)
