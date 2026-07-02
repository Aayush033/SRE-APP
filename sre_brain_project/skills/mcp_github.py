def get_recent_pr_context(scenario_key: str) -> dict:
    """
    Mock Github MCP Tool. 
    Queries commit history and recent pull request diffs to isolate root cause code changes.
    """
    database = {
        "checkout_storm": {
            "pr_id": 4821,
            "pr_title": "Optimize coupon lookup cache and validation workflows",
            "author": "Dave (Frontend Dev)",
            "merged_at": "11:45:12",
            "files_changed": ["services/checkout/handlers.py", "db/coupons.sql"],
            "rca_description": "Pull request #4821 introduced coupon loading optimizations. However, the database session handler did not include a try-finally block with session.close(), leading to unreleased database active sessions on high coupon lookups. Under Black Friday stress, this exhausted the 100 connection pool limit, locking checkout APIs."
        },
        "dns_cascade": {
            "pr_id": 4610,
            "pr_title": "Deprecate legacy API route mappings and registrar records",
            "author": "Alice (DevOps SRE)",
            "merged_at": "09:12:00",
            "files_changed": ["infra/dns/zone_config.json"],
            "rca_description": "Domain zone configurations were moved. However, registry auto-renewal configurations for secondary payment gateways were not consolidated in Route53 registrar profiles, leading to registrar-level payment expiry and WHOIS ClientHold suspensions."
        },
        "latency_loop": {
            "pr_id": 4799,
            "pr_title": "Integrate marketing promotions validation checks into core items query",
            "author": "Dave (Frontend Dev)",
            "merged_at": "11:30:00",
            "files_changed": ["services/promotions/routes.py", "services/checkout/client.go"],
            "rca_description": "Promotions validations were added directly in synchronous request chains. Because checkout client configurations omitted timeout limits, downstream DB read stalls on promotions-db locked checkout thread limits at 500 max."
        }
    }

    return database.get(scenario_key, {
        "pr_id": 9999,
        "pr_title": "Custom user-defined system script run",
        "author": "Operator",
        "merged_at": "12:00:00",
        "files_changed": ["unknown.py"],
        "rca_description": "A custom user simulation script injected logging updates and traffic spikes, verified in the local lab."
    })
