# SRE-Brain incident scenarios data definitions

SCENARIO_DATABASE = {
  "checkout_storm": {
    "name": "Black Friday Checkout Storm (Database Lockout)",
    "root_cause": "A coupon code lookup query introduced in deployment checkout-v1.4.2 lacked database session closing blocks, leading to connection exhaustion under heavy Black Friday loads.",
    "preventions": [
      "Wrap database session declarations in try-finally blocks to ensure session.close() is always invoked.",
      "Implement connection pool usage alerting inside PagerDuty.",
      "Deploy code changes behind feature flags during high-traffic windows."
    ],
    "telemetry": [
      { "timestamp": "12:00:10", "level": "system", "message": "API Gateway traffic load surging: 4,800 req/sec (baseline: 900 req/sec)." },
      { "timestamp": "12:00:25", "level": "warning", "message": "Checkout API service response latency exceeded 500ms warning threshold (Current: 850ms)." },
      { "timestamp": "12:00:40", "level": "warning", "message": "Warning: checkout-db connection pool occupancy reached 85% (85/100 active connections)." },
      { "timestamp": "12:01:00", "level": "error", "message": "API Gateway reports HTTP 503 Service Unavailable on POST /checkout (Error Rate: 6.4%)." },
      { "timestamp": "12:01:20", "level": "critical", "message": "CRITICAL: Database connection pool fully exhausted (100/100). Threads waiting in queue: 194." },
      { "timestamp": "12:01:45", "level": "critical", "message": "CRITICAL: Database replication lag exceeds SLA threshold of 10s (Current lag: 22s)." },
      { "timestamp": "12:02:10", "level": "error", "message": "Checkout microservice replica checkout-api-3b failed health check. Disabling node in Load Balancer." },
      { "timestamp": "12:03:00", "level": "info", "message": "[Mitigation Started] DBA scaling connection limits from 100 to 200 dynamically." },
      { "timestamp": "12:03:30", "level": "info", "message": "Database configuration update applied. Max connection limits boosted to 200." },
      { "timestamp": "12:04:00", "level": "info", "message": "[Mitigation Active] Terminating active hanging query tasks holding locks on coupons table." },
      { "timestamp": "12:04:30", "level": "success", "message": "Active leaked connection threads terminated. Pool occupancy dropped to 45/200." },
      { "timestamp": "12:05:00", "level": "success", "message": "API Gateway checkout latency dropped to baseline (38ms). HTTP 503 errors resolved (0.00% error rate)." },
      { "timestamp": "12:05:30", "level": "system", "message": "Telemetry nominal. Traffic stabilized at 3,600 req/sec. Incident fully resolved." }
    ],
    "chat": [
      { "timestamp": "12:00", "sender": "Alice (DevOps)", "message": "Traffic is spiking hard! Black Friday traffic is hitting the gate." },
      { "timestamp": "12:00", "sender": "Bob (SRE)", "message": "PagerDuty alert just fired. Checkout API latency is blowing past 1.5 seconds." },
      { "timestamp": "12:01", "sender": "Alice (DevOps)", "message": "CPU utilization across the nodes is sitting low, only 30%. This isn't a compute bottleneck." },
      { "timestamp": "12:01", "sender": "Charlie (DBA)", "message": "Guys, checkout-db is locking up. We are at 85/100 connections in the pool and they aren't releasing." },
      { "timestamp": "12:01", "sender": "Dave (Dev)", "message": "Oh, users on Twitter are screaming. 'Can't pay!' they are getting error screens." },
      { "timestamp": "12:02", "sender": "Bob (SRE)", "message": "Yep, HTTP 503 errors are peaking on the gateway. The checkouts are failing. We are losing $8,500 every minute." },
      { "timestamp": "12:02", "sender": "Charlie (DBA)", "message": "Database connection pool is completely dead. 100/100. All slots locked. Transactions are piling up on the coupons database." },
      { "timestamp": "12:02", "sender": "Bob (SRE)", "message": "Did we deploy anything in the last 30 minutes?" },
      { "timestamp": "12:02", "sender": "Dave (Dev)", "message": "Uh, I merged checkout-v1.4.2 about 15 minutes ago. It just optimized the coupon code loading check." },
      { "timestamp": "12:03", "sender": "Charlie (DBA)", "message": "Dave, does that query close the session? I'm seeing connections hang on 'SELECT * FROM coupon_codes WHERE active = true'." },
      { "timestamp": "12:03", "sender": "Dave (Dev)", "message": "Oh no... I wrapped it in a transaction but forgot the session.close() call in the handler callback. It leaks a connection on every attempt!" },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "OK, let's roll back checkout-v1.4.2 immediately. Charlie, can we expand the database connection capacity to buy us time?" },
      { "timestamp": "12:03", "sender": "Charlie (DBA)", "message": "Yes, scaling the pool to max 200 in the config. Deploying the update now." },
      { "timestamp": "12:03", "sender": "Dave (Dev)", "message": "Rolling back checkout-v1.4.2 to checkout-v1.4.1 now. Build started." },
      { "timestamp": "12:04", "sender": "Bob (SRE)", "message": "Pool is 200 now, but the 100 leaked queries from the old code are still holding locks. Charlie, kill those transactions." },
      { "timestamp": "12:04", "sender": "Charlie (DBA)", "message": "Running script to force kill all active connections associated with v1.4.2 coupon codes query." },
      { "timestamp": "12:04", "sender": "Dave (Dev)", "message": "Rollback container build complete. Pushing checkout-v1.4.1 to cluster." },
      { "timestamp": "12:04", "sender": "Charlie (DBA)", "message": "Transactions killed. DB pool connections dropped. Active is 45/200." },
      { "timestamp": "12:05", "sender": "Bob (SRE)", "message": "Latency is dropping. Checkouts are completing. Gateway graphs are turning back to green." },
      { "timestamp": "12:05", "sender": "Alice (DevOps)", "message": "Rollback deployment is fully rolled out. Let's do a sanity check." },
      { "timestamp": "12:05", "sender": "Dave (Dev)", "message": "I verified it on staging. Latency is back to 40ms. I'll rewrite the query with proper context closing and open a hotfix PR." },
      { "timestamp": "12:05", "sender": "Bob (SRE)", "message": "Awesome work. Let's keep the pool at 200 for now. Incident resolved. Let's write up the post-mortem." }
    ],
    "metrics": [
      { "latency": 25, "cpu": 8, "db": 12, "errors": 0.05, "reqs": 900 },
      { "latency": 120, "cpu": 15, "db": 35, "errors": 0.1, "reqs": 2100 },
      { "latency": 850, "cpu": 28, "db": 85, "errors": 1.5, "reqs": 4800 },
      { "latency": 1900, "cpu": 32, "db": 98, "errors": 4.8, "reqs": 4950 },
      { "latency": 4800, "cpu": 30, "db": 100, "errors": 9.6, "reqs": 2400 },
      { "latency": 5000, "cpu": 35, "db": 100, "errors": 12.8, "reqs": 1800 },
      { "latency": 3800, "cpu": 42, "db": 145, "errors": 10.4, "reqs": 2200 },
      { "latency": 1200, "cpu": 48, "db": 180, "errors": 5.1, "reqs": 3100 },
      { "latency": 220, "cpu": 36, "db": 65, "errors": 0.8, "reqs": 3500 },
      { "latency": 42, "cpu": 22, "db": 45, "errors": 0.04, "reqs": 3600 },
      { "latency": 24, "cpu": 12, "db": 15, "errors": 0.02, "reqs": 3650 }
    ]
  },
  "dns_cascade": {
    "name": "The DNS Expiry Cascade (Traffic Dropped)",
    "root_cause": "The secondary domain registrar account auto-renewal credit card expired, leading to domain suspension and failure of all DNS queries resolving API Gateway routes.",
    "preventions": [
      "Consolidate domain registrations under enterprise registrar accounts with multi-year renewals.",
      "Implement multi-point external synthetic health checkers that query DNS directly and alarm on DNS resolution failures.",
      "Setup registrar billing alerts routed directly to SRE and accounting mailing lists."
    ],
    "telemetry": [
      { "timestamp": "12:00:10", "level": "system", "message": "API Gateway traffic load dropping: 220 req/sec (baseline: 2,400 req/sec)." },
      { "timestamp": "12:00:30", "level": "warning", "message": "External synthetic checker: API endpoints failed connection. Curl error: (6) Could not resolve host." },
      { "timestamp": "12:00:45", "level": "warning", "message": "Internal system logs show database replication functioning. CPU load: 1%. Reqs: 0." },
      { "timestamp": "12:01:00", "level": "error", "message": "External load balancer health check counts dropped to zero. API gateway routes unreachable." },
      { "timestamp": "12:01:30", "level": "critical", "message": "CRITICAL: Global traffic volume zeroed out. SLA degradation active." },
      { "timestamp": "12:02:00", "level": "info", "message": "[Mitigation Started] SRE verifying DNS resolution at root level. WHOIS lookup returning 'ClientHold' status." },
      { "timestamp": "12:02:40", "level": "info", "message": "[Mitigation Active] Registrar invoice paid. Triggering domain status reactivation." },
      { "timestamp": "12:03:15", "level": "info", "message": "Domain status updated at registrar registry. DNS zone propagation initialized." },
      { "timestamp": "12:04:00", "level": "info", "message": "[Mitigation Active] Flushing local DNS resolvers cache on edge locations." },
      { "timestamp": "12:04:45", "level": "success", "message": "DNS queries resolving. Edge traffic re-entering gateway (1,200 req/sec)." },
      { "timestamp": "12:05:15", "level": "success", "message": "Gateway request rates nominal (2,350 req/sec). Error rates: 0.00%." },
      { "timestamp": "12:05:40", "level": "system", "message": "DNS propagation finished globally. Telemetry fully restored." }
    ],
    "chat": [
      { "timestamp": "12:00", "sender": "Alice (DevOps)", "message": "What is going on? Why did traffic just drop to zero? Are the servers dead?" },
      { "timestamp": "12:00", "sender": "Bob (SRE)", "message": "Checking AWS Console. CPU is normal, systems are healthy. But gateway request logs are completely blank." },
      { "timestamp": "12:01", "sender": "Dave (Dev)", "message": "Wait, the corporate website loads for me, but the API endpoints are returning 'DNS_PROBE_FINISHED_NXDOMAIN'." },
      { "timestamp": "12:01", "sender": "Bob (SRE)", "message": "Oh no. I can't resolve api.corporation.com either. Let me do a dig +trace." },
      { "timestamp": "12:01", "sender": "Alice (DevOps)", "message": "Wait, did we change the Route53 records today? No deployment was scheduled." },
      { "timestamp": "12:02", "sender": "Bob (SRE)", "message": "Route53 looks correct. But dig @8.8.8.8 returns NXDOMAIN. The domain itself is not resolving. Let me check the WHOIS registry." },
      { "timestamp": "12:02", "sender": "Charlie (DBA)", "message": "Internal databases are running fine. It seems traffic is not even getting to the CDN." },
      { "timestamp": "12:02", "sender": "Bob (SRE)", "message": "WHOIS registry check came back. Domain status: ClientHold. The registrar suspended our domain!" },
      { "timestamp": "12:02", "sender": "Alice (DevOps)", "message": "Registrar? We use Namecheap for that secondary gateway domain. Who has the credentials?" },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "I think procurement has the corporate credit card tied to that account. Let me contact accounting. " },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "The credit card on that account probably expired. I'll login with the team credentials and check the invoice page." },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "Yes! Invoice unpaid from yesterday. The auto-renew failed because the backup card expired." },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "I'll get a temporary card from the emergency SRE ledger. Alice, pay the invoice now." },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "Unpaid invoice paid! Status is updated to active in the registrar panel. They said the hold is lifted." },
      { "timestamp": "12:04", "sender": "Bob (SRE)", "message": "Perfect, domain hold is off. Now we wait for DNS propagation. It can take up to 2 hours, but let's flush our Cloudflare resolvers." },
      { "timestamp": "12:04", "sender": "Alice (DevOps)", "message": "Flushing edge DNS cache now..." },
      { "timestamp": "12:04", "sender": "Dave (Dev)", "message": "I'm starting to get API responses in the terminal. Traffic is trickling back." },
      { "timestamp": "12:05", "sender": "Bob (SRE)", "message": "Yes! Traffic graphs are spiking back to 2,400 req/sec. Edge caches are resolving the paths correctly." },
      { "timestamp": "12:05", "sender": "Alice (DevOps)", "message": "Resolved. The registrar hold is fully released. Let's make sure we move this domain to our primary registrar next week." }
    ],
    "metrics": [
      { "latency": 18, "cpu": 12, "db": 8, "errors": 0.01, "reqs": 2400 },
      { "latency": 0, "cpu": 2, "db": 5, "errors": 99.8, "reqs": 400 },
      { "latency": 0, "cpu": 1, "db": 1, "errors": 100.0, "reqs": 10 },
      { "latency": 0, "cpu": 1, "db": 0, "errors": 100.0, "reqs": 0 },
      { "latency": 0, "cpu": 1, "db": 0, "errors": 100.0, "reqs": 0 },
      { "latency": 0, "cpu": 1, "db": 0, "errors": 100.0, "reqs": 0 },
      { "latency": 12, "cpu": 5, "db": 2, "errors": 64.2, "reqs": 1200 },
      { "latency": 18, "cpu": 10, "db": 6, "errors": 4.5, "reqs": 2100 },
      { "latency": 19, "cpu": 12, "db": 8, "errors": 0.02, "reqs": 2450 }
    ]
  },
  "latency_loop": {
    "name": "Cascading Latency Loop (Microservice Exhaustion)",
    "root_cause": "A slow database read query on the promotions-service caused thread pool exhaustion on the checkout-service. Because of missing request timeouts on checkout client requests, checkout threads sat waiting, cascading the block up to the API Gateway.",
    "preventions": [
      "Enforce strict client-side request timeouts on all internal microservice API calls.",
      "Implement circuit breakers on dependencies that are not critical to core checkout functions.",
      "Add horizontal pod autoscaling to checkout-service based on concurrent thread occupancy."
    ],
    "telemetry": [
      { "timestamp": "12:00:10", "level": "system", "message": "API Gateway reporting latency increase on GET /cart/items." },
      { "timestamp": "12:00:25", "level": "warning", "message": "Warning: checkout-service HTTP client thread utilization at 90%." },
      { "timestamp": "12:00:45", "level": "warning", "message": "Warning: promotions-service database query latency spiked to 6.2s (Threshold: 200ms)." },
      { "timestamp": "12:01:10", "level": "error", "message": "Gateway timeouts: 504 on POST /checkout. Average latency: 10,200ms." },
      { "timestamp": "12:01:30", "level": "critical", "message": "CRITICAL: checkout-service pool exhausted. Concurrency limit reached (500 threads max)." },
      { "timestamp": "12:02:00", "level": "critical", "message": "CRITICAL: Thread lockout cascade. Front-end gateway dropping incoming checkouts." },
      { "timestamp": "12:02:30", "level": "info", "message": "[Mitigation Started] DevOps enabling circuit breaker policy on promotions-service dependency." },
      { "timestamp": "12:03:00", "level": "info", "message": "Circuit breaker status: OPEN. Bypassing promotions checking dynamically." },
      { "timestamp": "12:03:30", "level": "info", "message": "[Mitigation Active] Force restarting checkout-service pods to release blocked HTTP client threads." },
      { "timestamp": "12:04:10", "level": "info", "message": "Checkout-service nodes restarted. Active threads: 24/500." },
      { "timestamp": "12:04:45", "level": "success", "message": "Checkout API latency returning to nominal. Current average: 110ms." },
      { "timestamp": "12:05:15", "level": "success", "message": "Error rates resolved. Traffic flowing through API Gateway. SLA stable." },
      { "timestamp": "12:05:40", "level": "system", "message": "Incident cleared. Circuit breaker remains open for promotions-service." }
    ],
    "chat": [
      { "timestamp": "12:00", "sender": "Alice (DevOps)", "message": "I'm seeing latency warnings. The front-end checkout button is taking 10+ seconds to respond." },
      { "timestamp": "12:00", "sender": "Bob (SRE)", "message": "Confirming. Grafana dashboard shows checkout-service latency has spiked to 10 seconds. Error rates starting to creep up." },
      { "timestamp": "12:01", "sender": "Dave (Dev)", "message": "Wait, did database queries spike on checkout? Let's check DB performance." },
      { "timestamp": "12:01", "sender": "Charlie (DBA)", "message": "No, checkout-db CPU is only 5%. Latency on checkout-db is under 5ms. The issue is somewhere else." },
      { "timestamp": "12:01", "sender": "Alice (DevOps)", "message": "Looking at microservice logs. The checkout-service is calling the promotions-service to apply discounts." },
      { "timestamp": "12:02", "sender": "Dave (Dev)", "message": "Ah, the promotions-db! Charlie, can you look at that?" },
      { "timestamp": "12:02", "sender": "Charlie (DBA)", "message": "Yes. promotions-db is locked up. A marketing campaign query is scanning 40 million rows without an index." },
      { "timestamp": "12:02", "sender": "Bob (SRE)", "message": "Because of that, promotions-service is responding in 6+ seconds. But why does that kill the checkout service?" },
      { "timestamp": "12:02", "sender": "Dave (Dev)", "message": "Oh, checkout-service calls promotions-service synchronously, and we didn't specify a request timeout on that HTTP client! The threads are waiting forever." },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "Ah, thread exhaustion cascade. The 500 thread limit on checkout-service is maxed out waiting for promotions. Let's disconnect the promotions service." },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "Can we activate the circuit breaker for promotions? We have a config flag for that." },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "Yes, open the circuit breaker. We can bypass coupon verification temporarily. Better to check out without coupons than fail entirely." },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "Setting circuit-breaker.promotions.enabled = false in ConfigMap. Triggering hot reload." },
      { "timestamp": "12:03", "sender": "Bob (SRE)", "message": "Okay, the breaker is open. But the existing 500 threads on checkout-service are still stuck waiting for timeouts." },
      { "timestamp": "12:03", "sender": "Alice (DevOps)", "message": "Let me trigger a rolling restart of the checkout-service pods. That will kill the hanging threads." },
      { "timestamp": "12:04", "sender": "Alice (DevOps)", "message": "Rolling restart active. New pods are spin-up. Active threads: 15." },
      { "timestamp": "12:04", "sender": "Bob (SRE)", "message": "Excellent. Latency is dropping immediately. Back to 100ms." },
      { "timestamp": "12:05", "sender": "Charlie (DBA)", "message": "I killed the bad query on promotions-db and I'm adding the missing index now." },
      { "timestamp": "12:05", "sender": "Bob (SRE)", "message": "Nice. We are fully nominal. Checkouts are completing, bypassed promotions are handled gracefully. Let's start the post-mortem writeup." }
    ],
    "metrics": [
      { "latency": 32, "cpu": 15, "db": 14, "errors": 0.08, "reqs": 1500 },
      { "latency": 450, "cpu": 22, "db": 25, "errors": 0.8, "reqs": 1800 },
      { "latency": 1900, "cpu": 45, "db": 48, "errors": 2.5, "reqs": 1920 },
      { "latency": 6200, "cpu": 85, "db": 92, "errors": 8.9, "reqs": 1200 },
      { "latency": 10200, "cpu": 99, "db": 100, "errors": 16.5, "reqs": 450 },
      { "latency": 10400, "cpu": 99, "db": 100, "errors": 18.2, "reqs": 310 },
      { "latency": 8200, "cpu": 65, "db": 80, "errors": 12.4, "reqs": 750 },
      { "latency": 850, "cpu": 42, "db": 35, "errors": 2.1, "reqs": 1250 },
      { "latency": 124, "cpu": 20, "db": 16, "errors": 0.08, "reqs": 1520 },
      { "latency": 34, "cpu": 14, "db": 12, "errors": 0.04, "reqs": 1550 }
    ]
  }
}
