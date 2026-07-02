// SRE-Brain: Core Simulation & Agent Engine

// ==========================================================================
// Scenarios Database
// ==========================================================================
const SCENARIOS = {
  checkout_storm: {
    name: "Black Friday Checkout Storm (Database Lockout)",
    rootCause: "A coupon code lookup query introduced in deployment checkout-v1.4.2 lacked database session closing blocks, leading to connection exhaustion under heavy Black Friday loads.",
    preventions: [
      "Wrap database session declarations in try-finally blocks to ensure session.close() is always invoked.",
      "Implement connection pool usage alerting inside PagerDuty.",
      "Deploy code changes behind feature flags during high-traffic windows."
    ],
    telemetry: [
      { time: "12:00:10", type: "system", msg: "API Gateway traffic load surging: 4,800 req/sec (baseline: 900 req/sec)." },
      { time: "12:00:25", type: "warning", msg: "Checkout API service response latency exceeded 500ms warning threshold (Current: 850ms)." },
      { time: "12:00:40", type: "warning", msg: "Warning: checkout-db connection pool occupancy reached 85% (85/100 active connections)." },
      { time: "12:01:00", type: "error", msg: "API Gateway reports HTTP 503 Service Unavailable on POST /checkout (Error Rate: 6.4%)." },
      { time: "12:01:20", type: "critical", msg: "CRITICAL: Database connection pool fully exhausted (100/100). Threads waiting in queue: 194." },
      { time: "12:01:45", type: "critical", msg: "CRITICAL: Database replication lag exceeds SLA threshold of 10s (Current lag: 22s)." },
      { time: "12:02:10", type: "error", msg: "Checkout microservice replica checkout-api-3b failed health check. Disabling node in Load Balancer." },
      { time: "12:03:00", type: "info", msg: "[Mitigation Started] DBA scaling connection limits from 100 to 200 dynamically." },
      { time: "12:03:30", type: "info", msg: "Database configuration update applied. Max connection limits boosted to 200." },
      { time: "12:04:00", type: "info", msg: "[Mitigation Active] Terminating active hanging query tasks holding locks on coupons table." },
      { time: "12:04:30", type: "success", msg: "Active leaked connection threads terminated. Pool occupancy dropped to 45/200." },
      { time: "12:05:00", type: "success", msg: "API Gateway checkout latency dropped to baseline (38ms). HTTP 503 errors resolved (0.00% error rate)." },
      { time: "12:05:30", type: "system", msg: "Telemetry nominal. Traffic stabilized at 3,600 req/sec. Incident fully resolved." }
    ],
    chat: [
      { time: "12:00", sender: "Alice (DevOps)", msg: "Traffic is spiking hard! Black Friday traffic is hitting the gate." },
      { time: "12:00", sender: "Bob (SRE)", msg: "PagerDuty alert just fired. Checkout API latency is blowing past 1.5 seconds." },
      { time: "12:01", sender: "Alice (DevOps)", msg: "CPU utilization across the nodes is sitting low, only 30%. This isn't a compute bottleneck." },
      { time: "12:01", sender: "Charlie (DBA)", msg: "Guys, checkout-db is locking up. We are at 85/100 connections in the pool and they aren't releasing." },
      { time: "12:01", sender: "Dave (Dev)", msg: "Oh, users on Twitter are screaming. 'Can't pay!' they are getting error screens." },
      { time: "12:02", sender: "Bob (SRE)", msg: "Yep, HTTP 503 errors are peaking on the gateway. The checkouts are failing. We are losing $8,500 every minute." },
      { time: "12:02", sender: "Charlie (DBA)", msg: "Database connection pool is completely dead. 100/100. All slots locked. Transactions are piling up on the coupons database." },
      { time: "12:02", sender: "Bob (SRE)", msg: "Did we deploy anything in the last 30 minutes?" },
      { time: "12:02", sender: "Dave (Dev)", msg: "Uh, I merged checkout-v1.4.2 about 15 minutes ago. It just optimized the coupon code loading check." },
      { time: "12:03", sender: "Charlie (DBA)", msg: "Dave, does that query close the session? I'm seeing connections hang on 'SELECT * FROM coupon_codes WHERE active = true'." },
      { time: "12:03", sender: "Dave (Dev)", msg: "Oh no... I wrapped it in a transaction but forgot the session.close() call in the handler callback. It leaks a connection on every attempt!" },
      { time: "12:03", sender: "Bob (SRE)", msg: "OK, let's roll back checkout-v1.4.2 immediately. Charlie, can we expand the database connection capacity to buy us time?" },
      { time: "12:03", sender: "Charlie (DBA)", msg: "Yes, scaling the pool to max 200 in the config. Deploying the update now." },
      { time: "12:03", sender: "Dave (Dev)", msg: "Rolling back checkout-v1.4.2 to checkout-v1.4.1 now. Build started." },
      { time: "12:04", sender: "Bob (SRE)", msg: "Pool is 200 now, but the 100 leaked queries from the old code are still holding locks. Charlie, kill those transactions." },
      { time: "12:04", sender: "Charlie (DBA)", msg: "Running script to force kill all active connections associated with v1.4.2 coupon codes query." },
      { time: "12:04", sender: "Dave (Dev)", msg: "Rollback container build complete. Pushing checkout-v1.4.1 to cluster." },
      { time: "12:04", sender: "Charlie (DBA)", msg: "Transactions killed. DB pool connections dropped. Active is 45/200." },
      { time: "12:05", sender: "Bob (SRE)", msg: "Latency is dropping. Checkouts are completing. Gateway graphs are turning back to green." },
      { time: "12:05", sender: "Alice (DevOps)", msg: "Rollback deployment is fully rolled out. Let's do a sanity check." },
      { time: "12:05", sender: "Dave (Dev)", msg: "I verified it on staging. Latency is back to 40ms. I'll rewrite the query with proper context closing and open a hotfix PR." },
      { time: "12:05", sender: "Bob (SRE)", msg: "Awesome work. Let's keep the pool at 200 for now. Incident resolved. Let's write up the post-mortem." }
    ],
    // Vitals simulation mapping
    metrics: [
      { time: 0, latency: 25, cpu: 8, db: 12, errors: 0.05, reqs: 900 },
      { time: 10, latency: 120, cpu: 15, db: 35, errors: 0.1, reqs: 2100 },
      { time: 25, latency: 850, cpu: 28, db: 85, errors: 1.5, reqs: 4800 },
      { time: 40, latency: 1900, cpu: 32, db: 98, errors: 4.8, reqs: 4950 },
      { time: 60, latency: 4800, cpu: 30, db: 100, errors: 9.6, reqs: 2400 },
      { time: 80, latency: 5000, cpu: 35, db: 100, errors: 12.8, reqs: 1800 },
      { time: 100, latency: 3800, cpu: 42, db: 145, errors: 10.4, reqs: 2200 },
      { time: 120, latency: 1200, cpu: 48, db: 180, errors: 5.1, reqs: 3100 },
      { time: 140, latency: 220, cpu: 36, db: 65, errors: 0.8, reqs: 3500 },
      { time: 160, latency: 42, cpu: 22, db: 45, errors: 0.04, reqs: 3600 },
      { time: 180, latency: 24, cpu: 12, db: 15, errors: 0.02, reqs: 3650 }
    ]
  },
  dns_cascade: {
    name: "The DNS Expiry Cascade (Traffic Dropped)",
    rootCause: "The secondary domain registrar account auto-renewal credit card expired, leading to domain suspension and failure of all DNS queries resolving API Gateway routes.",
    preventions: [
      "Consolidate domain registrations under enterprise registrar accounts with multi-year renewals.",
      "Implement multi-point external synthetic health checkers that query DNS directly and alarm on DNS resolution failures.",
      "Setup registrar billing alerts routed directly to SRE and accounting mailing lists."
    ],
    telemetry: [
      { time: "12:00:10", type: "system", msg: "API Gateway traffic load dropping: 220 req/sec (baseline: 2,400 req/sec)." },
      { time: "12:00:30", type: "warning", msg: "External synthetic checker: API endpoints failed connection. Curl error: (6) Could not resolve host." },
      { time: "12:00:45", type: "warning", msg: "Internal system logs show database replication functioning. CPU load: 1%. Reqs: 0." },
      { time: "12:01:00", type: "error", msg: "External load balancer health check counts dropped to zero. API gateway routes unreachable." },
      { time: "12:01:30", type: "critical", msg: "CRITICAL: Global traffic volume zeroed out. SLA degradation active." },
      { time: "12:02:00", type: "info", msg: "[Mitigation Started] SRE verifying DNS resolution at root level. WHOIS lookup returning 'ClientHold' status." },
      { time: "12:02:40", type: "info", msg: "[Mitigation Active] Registrar invoice paid. Triggering domain status reactivation." },
      { time: "12:03:15", type: "info", msg: "Domain status updated at registrar registry. DNS zone propagation initialized." },
      { time: "12:04:00", type: "info", msg: "[Mitigation Active] Flushing local DNS resolvers cache on edge locations." },
      { time: "12:04:45", type: "success", msg: "DNS queries resolving. Edge traffic re-entering gateway (1,200 req/sec)." },
      { time: "12:05:15", type: "success", msg: "Gateway request rates nominal (2,350 req/sec). Error rates: 0.00%." },
      { time: "12:05:40", type: "system", msg: "DNS propagation finished globally. Telemetry fully restored." }
    ],
    chat: [
      { time: "12:00", sender: "Alice (DevOps)", msg: "What is going on? Why did traffic just drop to zero? Are the servers dead?" },
      { time: "12:00", sender: "Bob (SRE)", msg: "Checking AWS Console. CPU is normal, systems are healthy. But gateway request logs are completely blank." },
      { time: "12:01", sender: "Dave (Dev)", msg: "Wait, the corporate website loads for me, but the API endpoints are returning 'DNS_PROBE_FINISHED_NXDOMAIN'." },
      { time: "12:01", sender: "Bob (SRE)", msg: "Oh no. I can't resolve api.corporation.com either. Let me do a dig +trace." },
      { time: "12:01", sender: "Alice (DevOps)", msg: "Wait, did we change the Route53 records today? No deployment was scheduled." },
      { time: "12:02", sender: "Bob (SRE)", msg: "Route53 looks correct. But dig @8.8.8.8 returns NXDOMAIN. The domain itself is not resolving. Let me check the WHOIS registry." },
      { time: "12:02", sender: "Charlie (DBA)", msg: "Internal databases are running fine. It seems traffic is not even getting to the CDN." },
      { time: "12:02", sender: "Bob (SRE)", msg: "WHOIS registry check came back. Domain status: ClientHold. The registrar suspended our domain!" },
      { time: "12:02", sender: "Alice (DevOps)", msg: "Registrar? We use Namecheap for that secondary gateway domain. Who has the credentials?" },
      { time: "12:03", sender: "Bob (SRE)", msg: "I think procurement has the corporate credit card tied to that account. Let me contact accounting. " },
      { time: "12:03", sender: "Alice (DevOps)", msg: "The credit card on that account probably expired. I'll login with the team credentials and check the invoice page." },
      { time: "12:03", sender: "Alice (DevOps)", msg: "Yes! Invoice unpaid from yesterday. The auto-renew failed because the backup card expired." },
      { time: "12:03", sender: "Bob (SRE)", msg: "I'll get a temporary card from the emergency SRE ledger. Alice, pay the invoice now." },
      { time: "12:03", sender: "Alice (DevOps)", msg: "Unpaid invoice paid! Status is updated to active in the registrar panel. They said the hold is lifted." },
      { time: "12:04", sender: "Bob (SRE)", msg: "Perfect, domain hold is off. Now we wait for DNS propagation. It can take up to 2 hours, but let's flush our Cloudflare resolvers." },
      { time: "12:04", sender: "Alice (DevOps)", msg: "Flushing edge DNS cache now..." },
      { time: "12:04", sender: "Dave (Dev)", msg: "I'm starting to get API responses in the terminal. Traffic is trickling back." },
      { time: "12:05", sender: "Bob (SRE)", msg: "Yes! Traffic graphs are spiking back to 2,400 req/sec. Edge caches are resolving the paths correctly." },
      { time: "12:05", sender: "Alice (DevOps)", msg: "Resolved. The registrar hold is fully released. Let's make sure we move this domain to our primary enterprise registrar next week so this never happens again." }
    ],
    metrics: [
      { time: 0, latency: 18, cpu: 12, db: 8, errors: 0.01, reqs: 2400 },
      { time: 10, latency: 0, cpu: 2, db: 5, errors: 99.8, reqs: 400 },
      { time: 25, latency: 0, cpu: 1, db: 1, errors: 100, reqs: 10 },
      { time: 40, latency: 0, cpu: 1, db: 0, errors: 100, reqs: 0 },
      { time: 60, latency: 0, cpu: 1, db: 0, errors: 100, reqs: 0 },
      { time: 80, latency: 0, cpu: 1, db: 0, errors: 100, reqs: 0 },
      { time: 100, latency: 12, cpu: 5, db: 2, errors: 64.2, reqs: 1200 },
      { time: 120, latency: 18, cpu: 10, db: 6, errors: 4.5, reqs: 2100 },
      { time: 140, latency: 19, cpu: 12, db: 8, errors: 0.02, reqs: 2450 }
    ]
  },
  latency_loop: {
    name: "Cascading Latency Loop (Microservice Exhaustion)",
    rootCause: "A slow database read query on the promotions-service caused thread pool exhaustion on the checkout-service. Because of missing request timeouts on checkout client requests, checkout threads sat waiting, cascading the block up to the API Gateway.",
    preventions: [
      "Enforce strict client-side request timeouts on all internal microservice API calls.",
      "Implement circuit breakers on dependencies that are not critical to core checkout functions.",
      "Add horizontal pod autoscaling to checkout-service based on concurrent thread occupancy."
    ],
    telemetry: [
      { time: "12:00:10", type: "system", msg: "API Gateway reporting latency increase on GET /cart/items." },
      { time: "12:00:25", type: "warning", msg: "Warning: checkout-service HTTP client thread utilization at 90%." },
      { time: "12:00:45", type: "warning", msg: "Warning: promotions-service database query latency spiked to 6.2s (Threshold: 200ms)." },
      { time: "12:01:10", type: "error", msg: "Gateway timeouts: 504 on POST /checkout. Average latency: 10,200ms." },
      { time: "12:01:30", type: "critical", msg: "CRITICAL: checkout-service pool exhausted. Concurrency limit reached (500 threads max)." },
      { time: "12:02:00", type: "critical", msg: "CRITICAL: Thread lockout cascade. Front-end gateway dropping incoming checkouts." },
      { time: "12:02:30", type: "info", msg: "[Mitigation Started] DevOps enabling circuit breaker policy on promotions-service dependency." },
      { time: "12:03:00", type: "info", msg: "Circuit breaker status: OPEN. Bypassing promotions checking dynamically." },
      { time: "12:03:30", type: "info", msg: "[Mitigation Active] Force restarting checkout-service pods to release blocked HTTP client threads." },
      { time: "12:04:10", type: "info", msg: "Checkout-service nodes restarted. Active threads: 24/500." },
      { time: "12:04:45", type: "success", msg: "Checkout API latency returning to nominal. Current average: 110ms." },
      { time: "12:05:15", type: "success", msg: "Error rates resolved. Traffic flowing through API Gateway. SLA stable." },
      { time: "12:05:40", type: "system", msg: "Incident cleared. Circuit breaker remains open for promotions-service." }
    ],
    chat: [
      { time: "12:00", sender: "Alice (DevOps)", msg: "I'm seeing latency warnings. The front-end checkout button is taking 10+ seconds to respond." },
      { time: "12:00", sender: "Bob (SRE)", msg: "Confirming. Grafana dashboard shows checkout-service latency has spiked to 10 seconds. Error rates starting to creep up." },
      { time: "12:01", sender: "Dave (Dev)", msg: "Wait, did database queries spike on checkout? Let's check DB performance." },
      { time: "12:01", sender: "Charlie (DBA)", msg: "No, checkout-db CPU is only 5%. Latency on checkout-db is under 5ms. The issue is somewhere else." },
      { time: "12:01", sender: "Alice (DevOps)", msg: "Looking at microservice logs. The checkout-service is calling the promotions-service to apply discounts." },
      { time: "12:02", sender: "Dave (Dev)", msg: "Ah, the promotions-db! Charlie, can you look at that?" },
      { time: "12:02", sender: "Charlie (DBA)", msg: "Yes. promotions-db is locked up. A marketing campaign query is scanning 40 million rows without an index." },
      { time: "12:02", sender: "Bob (SRE)", msg: "Because of that, promotions-service is responding in 6+ seconds. But why does that kill the checkout service?" },
      { time: "12:02", sender: "Dave (Dev)", msg: "Oh, checkout-service calls promotions-service synchronously, and we didn't specify a request timeout on that HTTP client! The threads are waiting forever." },
      { time: "12:03", sender: "Bob (SRE)", msg: "Ah, thread exhaustion cascade. The 500 thread limit on checkout-service is maxed out waiting for promotions. Let's disconnect the promotions service." },
      { time: "12:03", sender: "Alice (DevOps)", msg: "Can we activate the circuit breaker for promotions? We have a config flag for that." },
      { time: "12:03", sender: "Bob (SRE)", msg: "Yes, open the circuit breaker. We can bypass coupon verification temporarily. Better to check out without coupons than fail entirely." },
      { time: "12:03", sender: "Alice (DevOps)", msg: "Setting circuit-breaker.promotions.enabled = false in ConfigMap. Triggering hot reload." },
      { time: "12:03", sender: "Bob (SRE)", msg: "Okay, the breaker is open. But the existing 500 threads on checkout-service are still stuck waiting for timeouts that won't happen for hours." },
      { time: "12:03", sender: "Alice (DevOps)", msg: "Let me trigger a rolling restart of the checkout-service pods. That will kill the hanging threads." },
      { time: "12:04", sender: "Alice (DevOps)", msg: "Rolling restart active. New pods are spin-up. Active threads: 15." },
      { time: "12:04", sender: "Bob (SRE)", msg: "Excellent. Latency is dropping immediately. Back to 100ms." },
      { time: "12:05", sender: "Charlie (DBA)", msg: "I killed the bad query on promotions-db and I'm adding the missing index now." },
      { time: "12:05", sender: "Bob (SRE)", msg: "Nice. We are fully nominal. Checkouts are completing, bypassed promotions are handled gracefully. Let's start the post-mortem writeup." }
    ],
    metrics: [
      { time: 0, latency: 32, cpu: 15, db: 14, errors: 0.08, reqs: 1500 },
      { time: 10, latency: 450, cpu: 22, db: 25, errors: 0.8, reqs: 1800 },
      { time: 25, latency: 1900, cpu: 45, db: 48, errors: 2.5, reqs: 1920 },
      { time: 40, latency: 6200, cpu: 85, db: 92, errors: 8.9, reqs: 1200 },
      { time: 60, latency: 10200, cpu: 99, db: 100, errors: 16.5, reqs: 450 },
      { time: 80, latency: 10400, cpu: 99, db: 100, errors: 18.2, reqs: 310 },
      { time: 100, latency: 8200, cpu: 65, db: 80, errors: 12.4, reqs: 750 },
      { time: 120, latency: 850, cpu: 42, db: 35, errors: 2.1, reqs: 1250 },
      { time: 140, latency: 124, cpu: 20, db: 16, errors: 0.08, reqs: 1520 },
      { time: 160, latency: 34, cpu: 14, db: 12, errors: 0.04, reqs: 1550 }
    ]
  }
};

// ==========================================================================
// Simulation State Variables
// ==========================================================================
let currentScenarioKey = "checkout_storm";
let customScenarioData = null;

let simulationActive = false;
let simulationState = "HEALTHY"; // HEALTHY, CRITICAL, MITIGATING, RESOLVED
let elapsedSeconds = 0;
let logIndex = 0;
let chatIndex = 0;
let speedMultiplier = 1;
let simInterval = null;
let databaseConnections = 12;

// Charts buffers
let telemetryDataHistory = Array(30).fill(25); // Latency
let connectionDataHistory = Array(30).fill(12); // DB connections
let cpuDataHistory = Array(30).fill(8); // CPU usage

// Timeline logs generated by agents
let parsedTimelineItems = [];
let agentLogs = [];
let incidentStartTimeStamp = null;

// SLA tracker
let currentSLA = 99.99;
let isSLABreaching = false;

// UI Elements caching
const elSystemStatusIndicator = document.getElementById("system-status-indicator");
const elSystemStatusText = document.getElementById("system-status-text");
const elIncidentTimer = document.getElementById("incident-timer");
const elScenarioSelect = document.getElementById("scenario-select");
const elBtnTrigger = document.getElementById("btn-trigger");
const elBtnResolve = document.getElementById("btn-resolve");
const elBtnReset = document.getElementById("btn-reset");
const elTelemetryLogStream = document.getElementById("telemetry-log-stream");
const elSlackChatStream = document.getElementById("slack-chat-stream");
const elTriageTimelineOutput = document.getElementById("triage-timeline-output");
const elCommsEmailOutput = document.getElementById("comms-email-output");
const elCommsEmailWrapper = document.getElementById("comms-email-wrapper");
const elEmailHeader = document.getElementById("email-header");
const elEmailSubject = document.getElementById("email-subject");
const elCommsTone = document.getElementById("comms-tone");
const elPostMortemReportOutput = document.getElementById("postmortem-report-output");
const elDrawerConsole = document.getElementById("drawer-console");
const elDrawerToggle = document.getElementById("drawer-toggle");
const elDrawerChevron = document.getElementById("drawer-chevron");
const elAppDrawer = document.querySelector(".app-drawer");
const elThinkingPulse = document.getElementById("thinking-pulse");
const elChatActiveCount = document.getElementById("chat-active-count");

// Dashboard card references (for visual crisis mode styling)
const elCards = document.querySelectorAll(".card");

// Speed selectors
const elSpeedButtons = document.querySelectorAll(".btn-speed");

// Actions container elements
const elCommsActionButtons = document.getElementById("comms-actions-buttons");
const elPostmortemActionButtons = document.getElementById("postmortem-actions-buttons");
const elBtnCopyEmail = document.getElementById("btn-copy-email");
const elBtnSendEmail = document.getElementById("btn-send-email");
const elBtnDownloadReport = document.getElementById("btn-download-report");
const elBtnCopyReport = document.getElementById("btn-copy-report");
const elCopyEmailToast = document.getElementById("copy-email-toast");
const elCopyReportToast = document.getElementById("copy-report-toast");

// Agent stats selectors
const elStatusTriage = document.getElementById("status-agent-triage");
const elStatusComms = document.getElementById("status-agent-comms");
const elStatusPostmortem = document.getElementById("status-agent-postmortem");

// Metric vitals
const elMetricLatency = document.getElementById("metric-latency");
const elMetricDb = document.getElementById("metric-db");
const elValErrorRate = document.getElementById("val-error-rate");
const elValReqs = document.getElementById("val-reqs");
const elValSla = document.getElementById("val-sla");

// Modal Elements
const elLabModal = document.getElementById("lab-modal");
const elBtnCloseModal = document.getElementById("btn-close-modal");
const elCustomScenarioName = document.getElementById("custom-scenario-name");
const elCustomTelemetryInput = document.getElementById("custom-telemetry-input");
const elCustomChatInput = document.getElementById("custom-chat-input");
const elBtnSaveCustom = document.getElementById("btn-save-custom");

// ==========================================================================
// Charting Engine (HTML5 Canvas 2D)
// ==========================================================================
function initCharts() {
  drawVitalsChart("chart-telemetry", telemetryDataHistory, cpuDataHistory, 5000, 100, "Latency", "CPU");
  drawConnectionsChart("chart-connections", connectionDataHistory, 200, "DB Active Connections");
}

function updateCharts() {
  const currentScenario = getActiveScenario();
  
  // Calculate current point in metrics mapping
  let activeLatency = 24;
  let activeCPU = 8;
  let activeDB = 12;
  let activeErrorRate = "0.05%";
  let activeReqs = "1.2k/s";

  if (simulationState === "HEALTHY") {
    // Inject subtle noise
    activeLatency = Math.round(20 + Math.random() * 8);
    activeCPU = Math.round(6 + Math.random() * 4);
    activeDB = Math.round(10 + Math.random() * 4);
    activeErrorRate = "0.05%";
    activeReqs = "1.2k/s";
    currentSLA = 99.99;
  } else {
    // Extract interpolation values from scenario metrics array based on progress
    const metricsArr = currentScenario.metrics;
    
    // Total steps depends on number of items in timeline
    const totalLines = currentScenario.telemetry.length;
    // Map current log index to index in metrics array
    const progressRatio = logIndex / totalLines;
    const metricIndexFloat = progressRatio * (metricsArr.length - 1);
    const indexLow = Math.floor(metricIndexFloat);
    const indexHigh = Math.ceil(metricIndexFloat);
    const weight = metricIndexFloat - indexLow;

    const mLow = metricsArr[indexLow];
    const mHigh = metricsArr[indexHigh];

    if (mLow && mHigh) {
      activeLatency = Math.round(mLow.latency + (mHigh.latency - mLow.latency) * weight);
      activeCPU = Math.round(mLow.cpu + (mHigh.cpu - mLow.cpu) * weight);
      activeDB = Math.round(mLow.db + (mHigh.db - mLow.db) * weight);
      
      const rawErrors = mLow.errors + (mHigh.errors - mLow.errors) * weight;
      activeErrorRate = rawErrors.toFixed(2) + "%";

      const rawReqs = mLow.reqs + (mHigh.reqs - mLow.reqs) * weight;
      activeReqs = (rawReqs / 1000).toFixed(1) + "k/s";
    }

    // Degrading SLA during active incident
    if (simulationState === "CRITICAL") {
      currentSLA -= (Math.random() * 0.015);
      if (currentSLA < 99.9) {
        isSLABreaching = true;
      }
    } else if (simulationState === "MITIGATING") {
      // SLA recovery slows down or stops falling
      currentSLA -= (Math.random() * 0.002);
      if (currentSLA < 95.0) currentSLA = 95.0; // cap floor
    }
  }

  // Update vitals elements
  elMetricLatency.textContent = `${activeLatency}ms / ${activeCPU}% CPU`;
  elMetricDb.textContent = `${activeDB} / ${simulationState === "MITIGATING" || simulationState === "RESOLVED" && currentScenarioKey === "checkout_storm" ? 200 : 100} max`;
  elValErrorRate.textContent = activeErrorRate;
  elValReqs.textContent = activeReqs;
  
  elValSla.textContent = currentSLA.toFixed(4) + "%";
  if (currentSLA < 99.9) {
    elValSla.className = "metric-val text-critical";
    elValErrorRate.className = "metric-val text-critical";
  } else if (currentSLA < 99.95) {
    elValSla.className = "metric-val text-mitigating";
    elValErrorRate.className = "metric-val text-mitigating";
  } else {
    elValSla.className = "metric-val text-healthy";
    elValErrorRate.className = "metric-val text-healthy";
  }

  // Add to buffers
  telemetryDataHistory.shift();
  telemetryDataHistory.push(activeLatency);

  cpuDataHistory.shift();
  cpuDataHistory.push(activeCPU);

  connectionDataHistory.shift();
  connectionDataHistory.push(activeDB);

  // Redraw
  const maxLatency = Math.max(...telemetryDataHistory, 1000);
  drawVitalsChart("chart-telemetry", telemetryDataHistory, cpuDataHistory, maxLatency, 100, "Latency", "CPU");
  
  const maxDBLimit = currentScenarioKey === "checkout_storm" ? 200 : 100;
  drawConnectionsChart("chart-connections", connectionDataHistory, maxDBLimit, "DB Active Connections");
}

function drawVitalsChart(canvasId, latencyData, cpuData, maxLatency, maxCPU, label1, label2) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  
  ctx.clearRect(0, 0, w, h);
  
  // Draw Grid Lines
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  for (let i = 1; i < 4; i++) {
    const y = (h / 4) * i;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  
  // Render CPU Data (Orange Line, lower profile)
  ctx.beginPath();
  ctx.strokeStyle = "rgba(255, 145, 0, 0.35)";
  ctx.lineWidth = 1.5;
  for (let i = 0; i < cpuData.length; i++) {
    const x = (w / (cpuData.length - 1)) * i;
    const valRatio = cpuData[i] / maxCPU;
    const y = h - (valRatio * h * 0.8) - 5;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Render Latency Data (Cyan Line, main focus, smooth gradient fill)
  const points = [];
  for (let i = 0; i < latencyData.length; i++) {
    const x = (w / (latencyData.length - 1)) * i;
    const valRatio = latencyData[i] / maxLatency;
    const y = h - (valRatio * h * 0.75) - 8;
    points.push({ x, y });
  }

  // Draw Gradient Fill
  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  const colorPulse = simulationState === "CRITICAL" ? "rgba(255, 23, 68, 0.1)" : "rgba(0, 229, 255, 0.1)";
  gradient.addColorStop(0, colorPulse);
  gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
  
  ctx.beginPath();
  ctx.moveTo(0, h);
  points.forEach((p, idx) => {
    if (idx === 0) ctx.lineTo(p.x, p.y);
    else ctx.lineTo(p.x, p.y);
  });
  ctx.lineTo(w, h);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  // Draw Neon Stroke Line
  ctx.beginPath();
  ctx.strokeStyle = simulationState === "CRITICAL" ? "var(--color-critical)" : "var(--color-info)";
  ctx.lineWidth = 2.5;
  points.forEach((p, idx) => {
    if (idx === 0) ctx.moveTo(p.x, p.y);
    else ctx.lineTo(p.x, p.y);
  });
  ctx.stroke();

  // Draw end point indicator
  if (points.length > 0) {
    const lastP = points[points.length - 1];
    ctx.beginPath();
    ctx.arc(lastP.x, lastP.y, 4, 0, 2 * Math.PI);
    ctx.fillStyle = simulationState === "CRITICAL" ? "var(--color-critical)" : "var(--color-info)";
    ctx.fill();
  }
}

function drawConnectionsChart(canvasId, dbData, maxVal, label) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  
  ctx.clearRect(0, 0, w, h);
  
  // Draw Grid Lines
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  for (let i = 1; i < 4; i++) {
    const y = (h / 4) * i;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Draw DB Connection line (Neon Purple / Hot Pink)
  const points = [];
  for (let i = 0; i < dbData.length; i++) {
    const x = (w / (dbData.length - 1)) * i;
    const valRatio = dbData[i] / maxVal;
    const y = h - (valRatio * h * 0.8) - 5;
    points.push({ x, y });
  }

  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  gradient.addColorStop(0, "rgba(124, 77, 255, 0.08)");
  gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
  
  ctx.beginPath();
  ctx.moveTo(0, h);
  points.forEach((p, idx) => {
    ctx.lineTo(p.x, p.y);
  });
  ctx.lineTo(w, h);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  ctx.beginPath();
  ctx.strokeStyle = "var(--color-primary)";
  ctx.lineWidth = 2;
  points.forEach((p, idx) => {
    if (idx === 0) ctx.moveTo(p.x, p.y);
    else ctx.lineTo(p.x, p.y);
  });
  ctx.stroke();

  // End node
  if (points.length > 0) {
    const lastP = points[points.length - 1];
    ctx.beginPath();
    ctx.arc(lastP.x, lastP.y, 3, 0, 2 * Math.PI);
    ctx.fillStyle = "var(--color-primary)";
    ctx.fill();
  }
}

// ==========================================================================
// Context Compaction / Agent Intelligence Models (Pseudo-LLM Engines)
// ==========================================================================

// Agent Log Drawer printing utility
function writeAgentLog(agentName, level, message) {
  const timestamp = new Date().toLocaleTimeString();
  const consoleClass = agentName.toLowerCase().replace(" ", "") + "-line";
  
  let lineContent = `<span class="system-line">[${timestamp}] [${agentName}]</span> `;
  if (level === "error") {
    lineContent += `<span class="text-critical">${message}</span>`;
  } else if (level === "warning") {
    lineContent += `<span class="text-mitigating">${message}</span>`;
  } else {
    lineContent += `<span class="text-main">${message}</span>`;
  }

  const elLine = document.createElement("div");
  elLine.className = `console-line ${consoleClass}`;
  elLine.innerHTML = lineContent;
  
  elDrawerConsole.appendChild(elLine);
  elDrawerConsole.scrollTop = elDrawerConsole.scrollHeight;
}

// 1. Telemetry Triage Agent
function runTelemetryTriageAgent(logLine) {
  elStatusTriage.textContent = "Synthesizing...";
  elStatusTriage.className = "agent-status thinking";
  elThinkingPulse.style.display = "inline-flex";

  // Simulate thinking duration delay
  setTimeout(() => {
    writeAgentLog("Telemetry Triage", "info", `Evaluating raw node output payload: "${logLine.msg}"`);
    
    // Evaluate log payload
    let timelineEvent = null;
    
    if (logLine.type === "critical") {
      timelineEvent = {
        time: logLine.time,
        severity: "critical",
        title: "Infrastructure Critical Threshold Breached",
        desc: logLine.msg
      };
      writeAgentLog("Telemetry Triage", "error", `CRITICAL SIGNATURE DETECTED: Mapping timestamp coordinates for incident timeline.`);
    } else if (logLine.type === "error") {
      timelineEvent = {
        time: logLine.time,
        severity: "critical",
        title: "Core Service Errors Spiking",
        desc: logLine.msg
      };
      writeAgentLog("Telemetry Triage", "error", `ERROR SIGNATURE DETECTED: Isolating failure nodes...`);
    } else if (logLine.type === "warning") {
      timelineEvent = {
        time: logLine.time,
        severity: "warning",
        title: "Service Latency Degradation Warning",
        desc: logLine.msg
      };
      writeAgentLog("Telemetry Triage", "warning", `WARNING SIGNATURE DETECTED: Resource limits approaching threshold.`);
    } else if (logLine.type === "success" || logLine.msg.includes("mitigated") || logLine.msg.includes("resolved")) {
      timelineEvent = {
        time: logLine.time,
        severity: "success",
        title: "Mitigation Verified / Normalizing",
        desc: logLine.msg
      };
      writeAgentLog("Telemetry Triage", "success", `RECOVERY SIGNATURE DETECTED: System metrics returning to nominal levels.`);
    }

    if (timelineEvent) {
      parsedTimelineItems.push(timelineEvent);
      renderTimeline();
    }

    elStatusTriage.textContent = "Monitoring";
    elStatusTriage.className = "agent-status complete";
    checkGlobalThinkingStatus();
  }, 300);
}

function renderTimeline() {
  if (parsedTimelineItems.length === 0) {
    elTriageTimelineOutput.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">⏳</span>
        <p>Telemetry Triage Agent is waiting for an active incident.</p>
      </div>`;
    return;
  }

  let html = `<div class="timeline-list">`;
  parsedTimelineItems.forEach(item => {
    const alertClass = `alert-${item.severity}`;
    html += `
      <div class="timeline-item ${alertClass}">
        <span class="timeline-time">${item.time}</span>
        <h5 class="timeline-title">${item.title}</h5>
        <p class="timeline-desc">${item.desc}</p>
      </div>`;
  });
  html += `</div>`;
  elTriageTimelineOutput.innerHTML = html;
  elTriageTimelineOutput.scrollTop = elTriageTimelineOutput.scrollHeight;
}

// 2. Comms Sync Agent: Context Compaction of panic-fueled chat logs
function runCommsSyncAgent(newChatLine) {
  elStatusComms.textContent = "Compacting...";
  elStatusComms.className = "agent-status thinking";
  elThinkingPulse.style.display = "inline-flex";

  setTimeout(() => {
    writeAgentLog("Comms Sync", "info", `Ingesting chat thread: ${newChatLine.sender}: "${newChatLine.msg}"`);
    
    // Evaluate if chat message contains high-signal or low-signal context
    const lowSignalRegex = /\b(omg|god|screaming|losing|blowing up|dude|coffee|website loads|are the servers dead|panicking|help|whoa|twitter|creeping|checkout button|bad query)\b/i;
    const highSignalRegex = /\b(db pool|connection pool|exhausted|timeout|rollback|v1.4.2|v1.4.1|circuit breaker|restarting|killed|unpaid|registrar|status|hold|unreachable|traffic)\b/i;
    
    const isLowSignal = lowSignalRegex.test(newChatLine.msg);
    const isHighSignal = highSignalRegex.test(newChatLine.msg);
    
    if (isLowSignal && !isHighSignal) {
      writeAgentLog("Comms Sync", "warning", `COMPACTION FILTER: Classified message from ${newChatLine.sender} as LOW SIGNAL panic chatter. Filtering out...`);
    } else if (isHighSignal) {
      writeAgentLog("Comms Sync", "success", `COMPACTION FILTER: Classified message from ${newChatLine.sender} as HIGH SIGNAL technical diagnostic. Ingesting into memory...`);
    }

    // Regenerate Executive email update with latest compacted context
    generateExecutiveEmail();

    elStatusComms.textContent = "Comms Synced";
    elStatusComms.className = "agent-status complete";
    checkGlobalThinkingStatus();
  }, 450);
}

function generateExecutiveEmail() {
  const tone = elCommsTone.value;
  const currentScenario = getActiveScenario();
  
  // Base metadata fields
  let subject = "";
  let body = "";
  let activeChatsCount = chatIndex;

  // Perform a local context extraction from the ingested high-signal chats
  const chatSlice = currentScenario.chat.slice(0, chatIndex);
  
  // Extract context variables
  const dbExhaustionDetected = chatSlice.some(c => c.msg.toLowerCase().includes("connection pool") || c.msg.toLowerCase().includes("deadlock"));
  const rollbackInitiated = chatSlice.some(c => c.msg.toLowerCase().includes("roll back") || c.msg.toLowerCase().includes("rolling back"));
  const dnsIssueDetected = chatSlice.some(c => c.msg.toLowerCase().includes("dns") || c.msg.toLowerCase().includes("clienthold") || c.msg.toLowerCase().includes("registrar"));
  
  const recoveryUnderway = simulationState === "MITIGATING";
  const fullyResolved = simulationState === "RESOLVED";

  // Hide the initial empty state
  elEmailHeader.style.display = "block";
  elCommsActionButtons.style.display = "flex";

  if (currentScenarioKey === "checkout_storm") {
    if (tone === "calm") {
      subject = `UPDATE: ${fullyResolved ? "RESOLVED" : (recoveryUnderway ? "MITIGATION IN PROGRESS" : "ACTIVE INCIDENT")} - E-Commerce Checkout Interruption`;
      body = `Dear Leadership Team,

Our SRE and Database engineering teams are actively resolving a transaction congestion event affecting checkout APIs.

${fullyResolved ? 
`**Status: Incident Fully Resolved**
The checkout system has returned to normal operations (latency: 38ms, error rates: 0%). All backlog transactions are completed.` : 
`**Current Status: ${recoveryUnderway ? "Mitigating - System Normalizing" : "Under Active Triage"}**
Customers are currently experiencing payment completion failures (HTTP 503 error screens). Product search and browsing functions remain fully operational.`}

**Actions Taken:**
* System capacity parameters scaled up to process high-traffic queue.
* Running queries causing database session blockages were isolated and cleared.
* ${rollbackInitiated ? "Rolled back recently deployed application patch (v1.4.2) to safe release state (v1.4.1)." : "Isolating code changes merged within last 30 minutes."}

We will provide a formal post-mortem once root-cause checks and verification tasks are finalized.

Sincerely,
SRE-Brain Incident Operations Coordinator`;
    } else if (tone === "technical") {
      subject = `TECH SUMMARY: DB Pool Exhaustion on checkout-db cluster [${fullyResolved ? "RESOLVED" : "SEV-1 ACTIVE"}]`;
      body = `TECHNICAL INCIDENT UPDATE:
Target Area: Database pool lockups (coupons lookup transactions).
State: ${fullyResolved ? "Resolved (Nominal metrics)" : (recoveryUnderway ? "Mitigation active / Rollback verifying" : "Active debugging")}

**Technical Details:**
1. **Symptom:** API Gateway response latency spiked to 4800ms. DB pool occupancy saturated at 100/100 connections.
2. **Root Cause:** Resource leak in checkout-v1.4.2 deployment coupon lookup logic. Missing database session closure blocks.
3. **Mitigations Executed:**
   * Scaled active DB connections pool limit configurations dynamically from 100 to 200.
   * Executed transaction scripts killing leaked threads.
   * ${rollbackInitiated ? "Initiated cluster rollback to checkout-v1.4.1 containers." : "Rollback queued."}
4. **Current Vitals:** Latency: ${fullyResolved ? "38ms" : "Spike pending clearance"} | Active DB connections: ${fullyResolved ? "45/200" : "Saturated"}`;
    } else { // crisis
      subject = `🚨 HIGH PRIORITY ALERT: Black Friday Checkout Service Interruption (SEV-1)`;
      body = `⚠️ CRITICAL SYSTEM FAILURE ALERT ⚠️

**IMPACT WARNING:** Checkout service is currently experiencing connection lockouts. Payments are failing for high volume of visitors. 

**Incident Details:**
* **Incident Clock:** ${elIncidentTimer.textContent}
* **Current Error Rate:** ${elValErrorRate.textContent} (SLA guarantee breached to ${elValSla.textContent})
* **Active Status:** ${simulationState}

**Current Actions:**
DevOps and DBA teams are currently in the war room force-killing hanging database locked queues. Rollback of core API servers is initiated. Emergency bridges are active.

Next update in 15 minutes.`;
    }
  } else if (currentScenarioKey === "dns_cascade") {
    // DNS Cascade Tone Outputs
    if (tone === "calm") {
      subject = `UPDATE: ${fullyResolved ? "RESOLVED" : (recoveryUnderway ? "PROPAGATION ACTIVE" : "ACTIVE INCIDENT")} - Global API Gateway Routing Outage`;
      body = `Dear Leadership Team,

We are addressing a routing incident that temporarily interrupted traffic accessing our customer endpoints.

${fullyResolved ? 
`**Status: Incident Resolved**
External domain resolution has propagated globally. API gateways are receiving full request volumes (2,400 req/sec) and error rates are zero.` : 
`**Current Status: ${recoveryUnderway ? "DNS Cache Propagation active" : "Investigating domain resolution failures"}**
Internal server layers are functional and safe, but clients are experiencing errors connecting to api.corporation.com.`}

**Actions Taken:**
* Identified administrative domain registration lockout status at secondary registrar.
* Successfully settled pending ledger invoices and verified domain reactivated status.
* Cloudflare edge resolvers flushed to accelerate global DNS propagation.

We are monitoring traffic volume recovery closely.

Sincerely,
SRE-Brain Incident Operations Coordinator`;
    } else if (tone === "technical") {
      subject = `TECH SUMMARY: NXDOMAIN ClientHold on Registrar Accounts [${fullyResolved ? "RESOLVED" : "SEV-1 ACTIVE"}]`;
      body = `TECHNICAL INCIDENT UPDATE:
Target Area: Domain Name System (DNS) Edge Resolution.
State: ${fullyResolved ? "Resolved" : (recoveryUnderway ? "DNS Propagation / Flashing Resolvers" : "Active Triage")}

**Technical Details:**
1. **Symptom:** Gateway traffic dropped from 2400 req/s to 0 req/s. External synthetic logs return Curl Error (6).
2. **Root Cause:** Secondary registrar account billing credentials expired, causing automatic registration suspension and WHOIS "ClientHold" status.
3. **Mitigations Executed:**
   * Settled billing accounts invoice in registrar panel.
   * Flushed local DNS caches at Route53 and CDN edges.
4. **Current Vitals:** Traffic: ${fullyResolved ? "2,400 req/s" : "0-400 req/s"} | Gateway connection: ${fullyResolved ? "SUCCESS" : "NXDOMAIN"}`;
    } else {
      subject = `🚨 HIGH PRIORITY ALERT: Core API Gateway Routing Suspended (SEV-1)`;
      body = `⚠️ CRITICAL SYSTEM FAILURE ALERT ⚠️

**IMPACT WARNING:** Global traffic routing is down. All backend endpoints are unreachable from client devices due to DNS resolution failures.

**Incident Details:**
* **Incident Clock:** ${elIncidentTimer.textContent}
* **Current Error Rate:** 100.00% (SLA breach active: ${elValSla.textContent})
* **Active Status:** ${simulationState}

**Current Actions:**
Procurement and SRE leads have completed domain restoration payments. DNS caches are being flushed at edge CDN locations. Wait for local caches to update.

Next update in 15 minutes.`;
    }
  } else {
    // Latency cascade scenario
    if (tone === "calm") {
      subject = `UPDATE: ${fullyResolved ? "RESOLVED" : (recoveryUnderway ? "MITIGATING" : "ACTIVE INCIDENT")} - System Latency Cascade`;
      body = `Dear Leadership Team,

Our engineers are currently stabilizing backend microservice latency loops impacting checkout completions.

${fullyResolved ? 
`**Status: Incident Resolved**
Timeout cascades are resolved and all microservice threads are cleared. Average response time is back to 34ms.` : 
`**Current Status: ${recoveryUnderway ? "Nodes restarting - Latency clearing" : "High Latency Alert - Triage Active"}**
Core browsing is responsive, but checkout and coupon verification steps are experiencing timeouts.`}

**Actions Taken:**
* Enabled emergency circuit breaker parameters to bypass slow dependency responses from promotions-service.
* Initiated rolling restarts of API pods to purge hung HTTP socket threads.
* DBA isolated non-indexed marketing analysis query tasks on databases.

Sincerely,
SRE-Brain Incident Operations Coordinator`;
    } else if (tone === "technical") {
      subject = `TECH SUMMARY: Thread Pool Exhaustion / Cascade latency loop [${fullyResolved ? "RESOLVED" : "SEV-1 ACTIVE"}]`;
      body = `TECHNICAL INCIDENT UPDATE:
Target Area: Thread pool exhaustion (checkout-service API endpoints).
State: ${fullyResolved ? "Nominal" : "Thread deadlock triage"}

**Technical Details:**
1. **Symptom:** Latency climbed to 10.2s. Checkout thread limits saturated (500/500). Gateway timeouts active.
2. **Root Cause:** A slow database read on promotions-db cascaded thread blocks due to missing internal request client timeouts on checkout calls.
3. **Mitigations Executed:**
   * Deployed config update to trigger circuit breaker (OPEN state) on promotions endpoints.
   * Executed rolling pod restarts across checkout service nodes to free hung socket pools.
4. **Current Vitals:** Average Latency: ${fullyResolved ? "34ms" : "10,200ms"}`;
    } else {
      subject = `🚨 HIGH PRIORITY ALERT: Microservice Thread Exhaustion (SEV-1)`;
      body = `⚠️ CRITICAL SYSTEM FAILURE ALERT ⚠️

**IMPACT WARNING:** Checkout transactions are failing due to cascading connection loops. Thread queues are fully saturated.

**Incident Details:**
* **Incident Clock:** ${elIncidentTimer.textContent}
* **Current Average Latency:** ${elMetricLatency.textContent}
* **Active Status:** ${simulationState}

**Current Actions:**
Activating circuit breaker flags to drop dependencies. Rolling container restarts are underway to release thread locks. 

Next update in 15 minutes.`;
    }
  }

  elEmailSubject.textContent = subject;
  elCommsEmailOutput.innerHTML = body.replace(/\n/g, "<br>");
}

// 3. Post-Mortem Writer: Builds and auto-drafts a mandatory incident report
function runPostMortemWriter() {
  elStatusPostmortem.textContent = "Writing...";
  elStatusPostmortem.className = "agent-status thinking";
  elThinkingPulse.style.display = "inline-flex";

  writeAgentLog("Post-Mortem Writer", "info", `Harvesting SRE Incident timeline coordinates...`);
  writeAgentLog("Post-Mortem Writer", "info", `Calculating SLA breach levels: Minimum SLA reached was ${currentSLA.toFixed(4)}%`);
  writeAgentLog("Post-Mortem Writer", "info", `Compiling RCA diagnostics...`);

  setTimeout(() => {
    const reportMarkdown = generatePostMortemMarkdown();
    
    // Render markdown view inside HTML
    renderPostMortemHtml(reportMarkdown);

    // Display actions
    elPostmortemActionButtons.style.display = "flex";

    elStatusPostmortem.textContent = "Draft Complete";
    elStatusPostmortem.className = "agent-status complete";
    checkGlobalThinkingStatus();
    
    writeAgentLog("Post-Mortem Writer", "success", `POST-MORTEM REPORT COMPILATION COMPLETE. Document is ready for executive approval and regulatory download.`);
  }, 1000);
}

function generatePostMortemMarkdown() {
  const currentScenario = getActiveScenario();
  const dateStr = new Date().toISOString().split('T')[0];
  const downtimeSecs = elapsedSeconds;
  const downtimeStr = `${Math.floor(downtimeSecs / 60)} minutes and ${downtimeSecs % 60} seconds`;

  let md = `# INCIDENT POST-MORTEM

**Document Reference ID:** INC-${currentScenarioKey.toUpperCase()}-${dateStr}
**Incident Level:** Severity 1 (SLA Breaching Crisis)
**Date of Incident:** ${dateStr}
**Total Downtime:** ${downtimeStr}
**SLA Metric Impact:** ${currentSLA.toFixed(4)}% (Minimum reached during event)

---

## 1. Executive Summary
On ${dateStr}, a major operational incident affected our production environments. ${currentScenario.name} caused critical failures on primary checkout flows, impacting customer transactions. The multi-agent coordinator SRE-Brain initiated automated triage and comms syncing protocols. Mitigations were initiated and checked, restoring vitals to nominal parameters in ${downtimeStr}.

---

## 2. Root Cause Analysis (RCA)
> [!IMPORTANT]
> **Primary Cause:**
> ${currentScenario.rootCause}

Underlying triggers:
- Lack of diagnostic alerts on secondary system boundaries.
- Tight coupling of third-party features with core user interfaces.

---

## 3. Incident Timeline
| Timestamp | Event Level | Action / Telemetry Log Entry |
| :--- | :--- | :--- |
`;

  // Parse Triage events into Markdown table
  parsedTimelineItems.forEach(item => {
    md += `| ${item.time} | ${item.severity.toUpperCase()} | ${item.desc} |\n`;
  });

  md += `
---

## 4. Mitigations & Recovery Tasks
The following manual and automated mitigations were executed during the event:
`;

  if (currentScenarioKey === "checkout_storm") {
    md += `- Scaled active Database connection pools to 200 slots.
- Executed operational scripts force-terminating locked queries.
- Deployed safe-state release checkout-v1.4.1 to overwrite resource-leaking deployment.`;
  } else if (currentScenarioKey === "dns_cascade") {
    md += `- Settled registry invoices to lift registrar "ClientHold".
- Flushed local edge routing caches.
- Verified DNS resolution globally using network lookups.`;
  } else {
    md += `- Activated config bypass opening circuit breaker.
- Restarted checkout-service nodes releasing blocked socket client threads.
- Added performance index query configurations in databases.`;
  }

  md += `

---

## 5. Preventative Action Items
To prevent recurrence of this incident, the following items are scheduled for immediate development:
`;

  currentScenario.preventions.forEach(item => {
    md += `- [ ] ${item}\n`;
  });

  md += `
---
*Draft auto-generated by **SRE-Brain: Post-Mortem Writer** on behalf of the engineering team.*`;

  return md;
}

function renderPostMortemHtml(markdown) {
  // Simple markdown-to-html renderer
  let html = markdown
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^---$/gim, '<hr>')
    .replace(/> \[\!IMPORTANT\]\n> \*\*Primary Cause:\*\*\n> (.*$)/gim, '<blockquote><strong>Primary Cause:</strong><br>$1</blockquote>')
    .replace(/\*\*Status: (.*$)\*\*/gim, '<strong>Status: $1</strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/- \[\s\] (.*$)/gim, '<li><input type="checkbox" disabled> $1</li>')
    .replace(/- (.*$)/gim, '<li>$1</li>');

  // Table parser helper
  const lines = html.split('\n');
  let inTable = false;
  let tableHtml = "";
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableHtml += '<table class="pm-table"><thead>';
      }
      
      const cells = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
      
      if (line.includes(':---') || line.includes('---:')) {
        // Skip separator line
        continue;
      }
      
      tableHtml += '<tr>';
      cells.forEach(cell => {
        if (tableHtml.includes('<thead>') && !tableHtml.includes('</thead>')) {
          tableHtml += `<th>${cell}</th>`;
        } else {
          tableHtml += `<td>${cell}</td>`;
        }
      });
      tableHtml += '</tr>';
      
      if (tableHtml.includes('<th>') && !tableHtml.includes('</thead>')) {
        tableHtml += '</thead><tbody>';
      }
    } else {
      if (inTable) {
        inTable = false;
        tableHtml += '</tbody></table>';
        lines[i - 1] = tableHtml;
        tableHtml = "";
      }
    }
  }

  // Clean up remaining linebreaks
  html = lines.join('\n')
    .replace(/<\/th>\n<\/tr>/g, '</th></tr>')
    .replace(/<\/td>\n<\/tr>/g, '</td></tr>')
    .replace(/\n\n/g, '<p>')
    .replace(/\n/g, '<br>');

  elPostMortemReportOutput.innerHTML = `<div class="pm-md">${html}</div>`;
  elPostMortemReportOutput.scrollTop = 0;
}

// Check helper to determine if any agent is currently reasoning
function checkGlobalThinkingStatus() {
  const t = elStatusTriage.textContent;
  const c = elStatusComms.textContent;
  const p = elStatusPostmortem.textContent;

  if (t === "Synthesizing..." || c === "Compacting..." || p === "Writing...") {
    elThinkingPulse.style.display = "inline-flex";
  } else {
    elThinkingPulse.style.display = "none";
  }
}

// Helper to check currently selected/custom scenario
function getActiveScenario() {
  if (currentScenarioKey === "custom_lab") {
    return customScenarioData;
  }
  return SCENARIOS[currentScenarioKey];
}

// ==========================================================================
// Simulation Event Loops & Tickers
// ==========================================================================
function startIncidentSimulation() {
  if (simulationActive) return;
  
  // Transition state
  simulationActive = true;
  simulationState = "CRITICAL";
  elapsedSeconds = 0;
  logIndex = 0;
  chatIndex = 0;
  parsedTimelineItems = [];
  incidentStartTimeStamp = new Date().toLocaleTimeString();

  // Clear previous outputs
  elTelemetryLogStream.innerHTML = "";
  elSlackChatStream.innerHTML = "";
  elTriageTimelineOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">⏳</span>
      <p>Telemetry Triage Agent is parsing incoming streams...</p>
    </div>`;
  elCommsEmailOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">📨</span>
      <p>Comms Sync Agent is filtering channel chats...</p>
    </div>`;
  elPostMortemReportOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">📝</span>
      <p>Post-Mortem report will generate upon incident resolution.</p>
    </div>`;

  // UI state resets
  elEmailHeader.style.display = "none";
  elCommsActionButtons.style.display = "none";
  elPostmortemActionButtons.style.display = "none";

  elSystemStatusIndicator.className = "status-indicator status-critical";
  elSystemStatusText.textContent = "SYSTEM STATUS: CRITICAL (SEV-1)";
  elSystemStatusText.className = "status-text text-critical";
  
  // Add crisis borders to cards
  elCards.forEach(c => c.classList.add("card-crisis-active"));

  elBtnTrigger.disabled = true;
  elBtnResolve.disabled = false;
  elScenarioSelect.disabled = true;

  writeAgentLog("System", "error", `[INCIDENT INC-${currentScenarioKey.toUpperCase()}] TRIGGERED. War room bridges active.`);
  
  // Start interval loop
  runTick();
}

function runTick() {
  clearInterval(simInterval);
  
  const tickDelay = 1000 / speedMultiplier;
  
  simInterval = setInterval(() => {
    if (!simulationActive) return;
    
    elapsedSeconds++;
    updateIncidentClock();
    
    const currentScenario = getActiveScenario();
    if (!currentScenario) return;

    // Check if new Telemetry logs need to be printed
    // We space logs out based on index vs elapsed steps
    const stepsPerLog = 15; // frequency
    const logsDue = Math.floor(elapsedSeconds / stepsPerLog);
    
    if (logsDue > logIndex && logIndex < currentScenario.telemetry.length) {
      // Check if we are in mitigation state, and if the log is a mitigation log.
      // If incident is critical, we pause logs that belong to recovery phase (which usually start with [Mitigation...])
      const nextLog = currentScenario.telemetry[logIndex];
      const isMitigationLog = nextLog.msg.includes("Mitigation") || nextLog.type === "success" || nextLog.msg.includes("stabilized");
      
      if (simulationState === "CRITICAL" && isMitigationLog) {
        // Hold logs until user clicks "Mitigate"
        // Simply do nothing, wait for trigger
      } else {
        printTelemetryLog(nextLog);
        runTelemetryTriageAgent(nextLog);
        logIndex++;
      }
    }

    // Check if new Chat messages need to be printed
    const stepsPerChat = 8;
    const chatsDue = Math.floor(elapsedSeconds / stepsPerChat);

    if (chatsDue > chatIndex && chatIndex < currentScenario.chat.length) {
      const nextChat = currentScenario.chat[chatIndex];
      const isMitigationChat = nextChat.msg.includes("ConfigMap") || nextChat.msg.includes("restart") || nextChat.msg.includes("rolled out") || nextChat.msg.includes("nominal");
      
      if (simulationState === "CRITICAL" && isMitigationChat) {
        // Hold chats until user clicks "Mitigate"
      } else {
        printChatLine(nextChat);
        runCommsSyncAgent(nextChat);
        chatIndex++;
      }
    }

    // Update charts & stats metrics
    updateCharts();

    // Check Auto-Resolution criteria:
    // If all logs and chats are processed and state is Mitigating, we transition to Resolved
    const hasLogsFinished = logIndex >= currentScenario.telemetry.length;
    const hasChatsFinished = chatIndex >= currentScenario.chat.length;

    if (simulationState === "MITIGATING" && hasLogsFinished && hasChatsFinished) {
      resolveIncidentSimulation();
    }
    
  }, tickDelay);
}

function resolveIncidentSimulation() {
  simulationState = "RESOLVED";
  clearInterval(simInterval);

  elSystemStatusIndicator.className = "status-indicator status-healthy";
  elSystemStatusText.textContent = "SYSTEM STATUS: NOMINAL";
  elSystemStatusText.className = "status-text text-healthy";

  // Remove red glowing boxes
  elCards.forEach(c => c.classList.remove("card-crisis-active"));

  elBtnResolve.disabled = true;
  elBtnTrigger.disabled = false;
  elScenarioSelect.disabled = false;
  
  writeAgentLog("System", "success", `Incident mitigated. Telemetry metrics verified healthy.`);

  // Fire Post-Mortem Writer Agent
  runPostMortemWriter();
}

function triggerMitigationSequence() {
  if (simulationState !== "CRITICAL") return;
  
  simulationState = "MITIGATING";
  elSystemStatusIndicator.className = "status-indicator status-mitigating";
  elSystemStatusText.textContent = "SYSTEM STATUS: MITIGATING";
  elSystemStatusText.className = "status-text text-mitigating";

  writeAgentLog("System", "warning", `Mitigation procedures initiated by operator. Executing recovery pipelines...`);
}

function updateIncidentClock() {
  const hrs = Math.floor(elapsedSeconds / 3600).toString().padStart(2, "0");
  const mins = Math.floor((elapsedSeconds % 3600) / 60).toString().padStart(2, "0");
  const secs = (elapsedSeconds % 60).toString().padStart(2, "0");
  elIncidentTimer.textContent = `${hrs}:${mins}:${secs}`;
}

function printTelemetryLog(log) {
  const elLine = document.createElement("div");
  let levelClass = "system-line";
  if (log.type === "error") levelClass = "error-line";
  else if (log.type === "critical") levelClass = "critical-line";
  else if (log.type === "warning") levelClass = "warning-line";
  else if (log.type === "success") levelClass = "success-line";
  else if (log.type === "info") levelClass = "info-line";

  elLine.className = `terminal-line ${levelClass}`;
  elLine.innerHTML = `<span class="system-line">[${log.time}]</span> ${log.msg}`;
  elTelemetryLogStream.appendChild(elLine);
  elTelemetryLogStream.scrollTop = elTelemetryLogStream.scrollHeight;
}

function printChatLine(chat) {
  const elMsg = document.createElement("div");
  
  // Highlight chaotic developer chatter styles
  const isPanic = /\b(omg|god|screaming|losing|blowing up|unpaid|dead|lockout|fail|error|hold)\b/i.test(chat.msg);
  const panicClass = isPanic ? "panic-chatter" : "";

  elMsg.className = `chat-message ${panicClass}`;
  elMsg.innerHTML = `
    <span class="message-timestamp">${chat.time}</span>
    <span class="message-sender">${chat.sender}</span>
    <span class="message-content">${chat.msg}</span>`;
    
  elSlackChatStream.appendChild(elMsg);
  elSlackChatStream.scrollTop = elSlackChatStream.scrollHeight;

  // Active devs indicator helper
  const uniqueSenders = new Set(Array.from(elSlackChatStream.querySelectorAll(".message-sender")).map(s => s.textContent));
  elChatActiveCount.textContent = uniqueSenders.size;
}

function resetDashboard() {
  simulationActive = false;
  simulationState = "HEALTHY";
  clearInterval(simInterval);
  elapsedSeconds = 0;
  logIndex = 0;
  chatIndex = 0;
  parsedTimelineItems = [];
  currentSLA = 99.99;
  isSLABreaching = false;

  elIncidentTimer.textContent = "00:00:00";
  elSystemStatusIndicator.className = "status-indicator status-healthy";
  elSystemStatusText.textContent = "SYSTEM STATUS: NOMINAL";
  elSystemStatusText.className = "status-text text-healthy";
  
  elCards.forEach(c => c.classList.remove("card-crisis-active"));

  elBtnTrigger.disabled = false;
  elBtnResolve.disabled = true;
  elScenarioSelect.disabled = false;

  // Clear Panels
  elTelemetryLogStream.innerHTML = `
    <div class="terminal-line system-line">[SYSTEM] Boot sequence initialized... OK</div>
    <div class="terminal-line system-line">[SYSTEM] Healthcheck daemon running... OK</div>
    <div class="terminal-line info-line">[INFO] Latency monitoring started. Limit threshold: 500ms</div>`;
  
  elSlackChatStream.innerHTML = `
    <div class="chat-message system-msg">
      <span class="message-timestamp">${new Date().toLocaleTimeString().slice(0, 5)}</span>
      <span class="message-sender">Slackbot</span>
      <span class="message-content">Welcome to the #incident-war-room channel. Logs generated here are analyzed by SRE-Brain.</span>
    </div>`;

  elTriageTimelineOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">⏳</span>
      <p>Telemetry Triage Agent is waiting for an active incident.</p>
    </div>`;

  elCommsEmailOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">📨</span>
      <p>Comms Sync Agent is waiting for chaotic chatter.</p>
    </div>`;
  elEmailHeader.style.display = "none";
  elCommsActionButtons.style.display = "none";

  elPostMortemReportOutput.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">📝</span>
      <p>Post-Mortem report will generate upon incident resolution.</p>
    </div>`;
  elPostmortemActionButtons.style.display = "none";

  // Re-init chart buffers to flatlines
  telemetryDataHistory = Array(30).fill(25);
  connectionDataHistory = Array(30).fill(12);
  cpuDataHistory = Array(30).fill(8);

  elStatusTriage.textContent = "Idle";
  elStatusTriage.className = "agent-status";
  elStatusComms.textContent = "Idle";
  elStatusComms.className = "agent-status";
  elStatusPostmortem.textContent = "Idle";
  elStatusPostmortem.className = "agent-status";
  elThinkingPulse.style.display = "none";

  elChatActiveCount.textContent = "0";

  initCharts();
  
  writeAgentLog("System", "info", "SRE-Brain Dashboard state has been reset. Ready for next simulation.");
}

// ==========================================================================
// Custom Labs Handler
// ==========================================================================
function loadCustomScenario() {
  const scName = elCustomScenarioName.value;
  const rawLogsText = elCustomTelemetryInput.value;
  const rawChatText = elCustomChatInput.value;

  // Validate input
  if (!scName || !rawLogsText || !rawChatText) {
    alert("Please fill out all custom scenario fields.");
    return;
  }

  // Parse logs text
  const logLines = rawLogsText.split("\n").filter(l => l.trim() !== "");
  const parsedLogs = logLines.map(line => {
    const timeMatch = line.match(/^\[(.*?)\]/);
    const time = timeMatch ? timeMatch[1] : "12:00:00";
    
    let type = "info";
    if (line.includes("[ERROR]")) type = "error";
    else if (line.includes("[CRITICAL]")) type = "critical";
    else if (line.includes("[WARNING]")) type = "warning";
    else if (line.includes("[SUCCESS]")) type = "success";
    else if (line.includes("[SYSTEM]")) type = "system";

    const cleanMsg = line.replace(/^\[.*?\]\s*(\[.*?\])?\s*/, "");

    return { time, type, msg: cleanMsg };
  });

  // Parse chat text
  const chatLines = rawChatText.split("\n").filter(l => l.trim() !== "");
  const parsedChats = chatLines.map(line => {
    const timeMatch = line.match(/^\[(.*?)\]/);
    const time = timeMatch ? timeMatch[1] : "12:00";
    
    const senderMatch = line.match(/\]\s*(.*?):\s*/);
    const sender = senderMatch ? senderMatch[1] : "Developer";
    
    const msg = line.replace(/^\[.*?\]\s*.*?:/, "").trim();

    return { time, sender, msg };
  });

  // Calculate synthetic metrics slope
  const customMetrics = [];
  const totalSteps = 10;
  
  for (let i = 0; i <= totalSteps; i++) {
    const ratio = i / totalSteps;
    let latency = 25;
    let cpu = 10;
    let db = 15;
    let errors = 0.05;
    let reqs = 1500;

    // First half goes up, second half goes down
    if (ratio < 0.6) {
      latency = Math.round(25 + ratio * 1.66 * 3800);
      cpu = Math.round(10 + ratio * 1.66 * 85);
      db = Math.round(15 + ratio * 1.66 * 80);
      errors = Number((0.05 + ratio * 1.66 * 14.5).toFixed(2));
      reqs = Math.round(1500 + ratio * 1.66 * 3000);
    } else {
      const scale = (1 - ratio) / 0.4;
      latency = Math.round(25 + scale * 3800);
      cpu = Math.round(10 + scale * 85);
      db = Math.round(15 + scale * 80);
      errors = Number((0.05 + scale * 14.5).toFixed(2));
      reqs = Math.round(1500 + scale * 3000);
    }

    customMetrics.push({
      time: i * 20,
      latency,
      cpu,
      db,
      errors,
      reqs
    });
  }

  customScenarioData = {
    name: scName,
    rootCause: "A custom user-defined scenario triggered failure parameters on production systems, validated through the Simulation Lab console.",
    preventions: [
      "Improve testing parameters in the custom simulation playground.",
      "Check configurations of user-defined log lines."
    ],
    telemetry: parsedLogs,
    chat: parsedChats,
    metrics: customMetrics
  };

  elLabModal.classList.remove("show");
  writeAgentLog("System", "success", `Successfully loaded custom lab scenario: "${scName}"`);
}

// ==========================================================================
// Event Listeners & Bootstrapping
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  
  // Tabs Navigation
  const tabLinks = document.querySelectorAll(".tab-link");
  const tabContents = document.querySelectorAll(".agent-tab-content");

  tabLinks.forEach(link => {
    link.addEventListener("click", () => {
      const targetTab = link.dataset.tab;
      
      tabLinks.forEach(l => l.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      link.classList.add("active");
      document.getElementById(targetTab).classList.add("active");
    });
  });

  // Collapsible Console Drawer
  elDrawerToggle.addEventListener("click", () => {
    elAppDrawer.classList.toggle("expanded");
  });

  // Speed adjustments
  elSpeedButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      elSpeedButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      speedMultiplier = parseInt(btn.dataset.speed, 10);
      
      if (simulationActive && simulationState !== "RESOLVED") {
        // Re-align ticks with new speed multiplier
        runTick();
      }
      writeAgentLog("System", "info", `Simulation clock speed toggled to ${speedMultiplier}x.`);
    });
  });

  // Scenario Select Change
  elScenarioSelect.addEventListener("change", () => {
    currentScenarioKey = elScenarioSelect.value;
    if (currentScenarioKey === "custom_lab") {
      elLabModal.classList.add("show");
    } else {
      writeAgentLog("System", "info", `Loaded scenario target: "${SCENARIOS[currentScenarioKey].name}"`);
    }
  });

  // Modal actions
  elBtnCloseModal.addEventListener("click", () => {
    elLabModal.classList.remove("show");
    // Fallback selection if custom is closed without saving
    if (!customScenarioData && elScenarioSelect.value === "custom_lab") {
      elScenarioSelect.value = "checkout_storm";
      currentScenarioKey = "checkout_storm";
    }
  });

  elBtnSaveCustom.addEventListener("click", loadCustomScenario);

  // Email Tone select change
  elCommsTone.addEventListener("change", () => {
    if (chatIndex > 0) {
      writeAgentLog("Comms Sync", "warning", `Regenerating email overview based on tone update: "${elCommsTone.value}"`);
      generateExecutiveEmail();
    }
  });

  // Action Triggers
  elBtnTrigger.addEventListener("click", startIncidentSimulation);
  elBtnResolve.addEventListener("click", triggerMitigationSequence);
  elBtnReset.addEventListener("click", resetDashboard);

  // Copy Comms Email
  elBtnCopyEmail.addEventListener("click", () => {
    const subject = elEmailSubject.textContent;
    const body = elCommsEmailOutput.innerText;
    const fullText = `Subject: ${subject}\n\n${body}`;
    
    navigator.clipboard.writeText(fullText).then(() => {
      elCopyEmailToast.classList.add("show");
      setTimeout(() => elCopyEmailToast.classList.remove("show"), 2000);
      writeAgentLog("System", "info", "Compacted Executive Email copied to clipboard.");
    });
  });

  // Copy Post-Mortem Report
  elBtnCopyReport.addEventListener("click", () => {
    const reportText = generatePostMortemMarkdown();
    navigator.clipboard.writeText(reportText).then(() => {
      elCopyReportToast.classList.add("show");
      setTimeout(() => elCopyReportToast.classList.remove("show"), 2000);
      writeAgentLog("System", "info", "Post-Mortem Markdown draft copied to clipboard.");
    });
  });

  // Mock Email Dispatch
  elBtnSendEmail.addEventListener("click", () => {
    writeAgentLog("Comms Sync", "success", "EMAIL SENT: Compacted Executive Summary broadcasted to executive-suite@corporation.com.");
    alert("Compacted Executive update sent to leadership mailboxes.");
  });

  // Download Post-Mortem Markdown Report
  elBtnDownloadReport.addEventListener("click", () => {
    const reportText = generatePostMortemMarkdown();
    const blob = new Blob([reportText], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.href = url;
    a.download = `SRE_PostMortem_${currentScenarioKey}_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    writeAgentLog("System", "success", "Post-Mortem Regulatory Report file generated and downloaded.");
  });

  // Bootstrapping chart charts
  initCharts();
});
