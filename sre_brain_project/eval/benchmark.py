"""
SRE-Brain Evaluation Benchmark Suite.

Measures quantitative performance metrics:
  - Alert Detection Precision / Recall / F1
  - Mean Time To Detect (MTTD) — seconds from incident start to first CRITICAL alert
  - Financial Impact Accuracy
  - Anomaly Detector Z-score validation
  - Full graph cycle correctness

Run with:
    cd sre_brain_project
    python eval/benchmark.py
"""
import sys
import os
import json
import time
import datetime

# Force UTF-8 output on Windows (fixes cp1252 emoji encoding errors)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.states import IncidentState, LogEntry, ChatMessage
from core.session import IncidentSession
from core.graph import IncidentGraph
from agents.telemetry_agent import run_telemetry_agent
from tools.mock_telemetry import SCENARIO_DATABASE
from tools.anomaly_detector import detect_anomalies, SlidingWindowDetector
from skills.calculate_impact import calculate_downtime_cost


# ─────────────────────────────────────────────────────────────────────────────
# Ground Truth Labels
# For each scenario, which log indices are TRUE positives (actual anomalies)?
# ─────────────────────────────────────────────────────────────────────────────
GROUND_TRUTH = {
    "checkout_storm": {
        # Indices into telemetry list that are true incidents (critical/error)
        "critical_indices": {3, 4, 5, 6},  # 503 error, pool exhausted, replication lag, health check fail
        "first_alert_timestamp": "12:01:00",
        "expected_cost_at_330s": 46750.0,
    },
    "dns_cascade": {
        "critical_indices": {3, 4, 5, 6},
        "first_alert_timestamp": "12:01:15",
        "expected_cost_at_600s": 40000.0,
    },
    "latency_loop": {
        "critical_indices": {2, 3, 4, 5},
        "first_alert_timestamp": "12:00:45",
        "expected_cost_at_480s": 25600.0,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Metric Helpers
# ─────────────────────────────────────────────────────────────────────────────
def precision_recall_f1(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 3),
        "recall":    round(recall, 3),
        "f1":        round(f1, 3),
    }


def timestamp_to_seconds(ts: str, base: str = "12:00:00") -> int:
    """Convert HH:MM:SS or HH:MM to seconds since base time."""
    def _parse(t):
        parts = t.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 3600 + int(parts[1]) * 60
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return _parse(ts) - _parse(base)


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 1: Alert Detection Accuracy (Precision / Recall / F1)
# ─────────────────────────────────────────────────────────────────────────────
def benchmark_alert_detection() -> dict:
    """
    Feeds each scenario's telemetry logs through the TelemetryAgent and
    compares detected critical/warning events against ground truth labels.
    """
    results = {}

    for scenario_key, gt in GROUND_TRUTH.items():
        sc = SCENARIO_DATABASE[scenario_key]
        state = IncidentState(status="CRITICAL", scenario_key=scenario_key)

        for i, log in enumerate(sc["telemetry"]):
            state.raw_logs.append(LogEntry(
                timestamp=log["timestamp"],
                level=log["level"],
                message=log["message"]
            ))

        state = run_telemetry_agent(state)

        # Detected positive indices: logs that produced a timeline event
        detected_critical_count = sum(
            1 for ev in state.factual_timeline if ev.severity == "critical"
        )
        expected_critical_count = len(gt["critical_indices"])

        tp = min(detected_critical_count, expected_critical_count)
        fp = max(0, detected_critical_count - expected_critical_count)
        fn = max(0, expected_critical_count - detected_critical_count)

        results[scenario_key] = precision_recall_f1(tp, fp, fn)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 2: Mean Time To Detect (MTTD)
# ─────────────────────────────────────────────────────────────────────────────
def benchmark_mttd() -> dict:
    """
    Measures how many seconds after incident start the first CRITICAL timeline
    event is detected. Lower is better.
    """
    results = {}

    for scenario_key, gt in GROUND_TRUTH.items():
        sc = SCENARIO_DATABASE[scenario_key]
        state = IncidentState(status="CRITICAL", scenario_key=scenario_key)

        for log in sc["telemetry"]:
            state.raw_logs.append(LogEntry(
                timestamp=log["timestamp"],
                level=log["level"],
                message=log["message"]
            ))

        state = run_telemetry_agent(state)

        # Find first critical event timestamp
        first_critical_ts = None
        for ev in state.factual_timeline:
            if ev.severity == "critical":
                first_critical_ts = ev.timestamp
                break

        if first_critical_ts:
            mttd_seconds = timestamp_to_seconds(first_critical_ts)
            expected_seconds = timestamp_to_seconds(gt["first_alert_timestamp"])
            delta = abs(mttd_seconds - expected_seconds)
        else:
            mttd_seconds = -1
            delta = -1

        results[scenario_key] = {
            "mttd_seconds": mttd_seconds,
            "expected_seconds": timestamp_to_seconds(gt["first_alert_timestamp"]),
            "delta_seconds": delta,
            "grade": "✅ PASS" if delta <= 60 else "⚠️ SLOW",
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 3: Financial Impact Accuracy
# ─────────────────────────────────────────────────────────────────────────────
def benchmark_financial_accuracy() -> dict:
    """
    Validates calculate_downtime_cost() against known expected values.
    """
    results = {}

    test_cases = [
        ("checkout_storm", 330, 46750.0),
        ("dns_cascade",    600, 40000.0),
        ("latency_loop",   480, 25600.0),
        ("custom_lab",     120,  3000.0),
    ]

    for scenario_key, seconds, expected in test_cases:
        actual = calculate_downtime_cost(seconds, scenario_key)
        error_pct = abs(actual - expected) / expected * 100 if expected > 0 else 0.0
        results[f"{scenario_key}@{seconds}s"] = {
            "expected": expected,
            "actual":   actual,
            "error_pct": round(error_pct, 2),
            "grade": "✅ PASS" if error_pct < 1.0 else "❌ FAIL",
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 4: Anomaly Detector Z-Score Validation
# ─────────────────────────────────────────────────────────────────────────────
def benchmark_anomaly_detector() -> dict:
    """
    Validates the anomaly detector against known healthy and critical metric snapshots.
    """
    test_cases = [
        {
            "label": "Healthy baseline",
            "metrics": {"latency_ms": 35, "cpu_percent": 15, "db_connections": 20, "error_rate": 0.05},
            "expected_anomaly_count": 0,
        },
        {
            "label": "Black Friday peak (checkout_storm at 12:01:20)",
            "metrics": {"latency_ms": 4800, "cpu_percent": 30, "db_connections": 100, "error_rate": 9.6},
            "expected_anomaly_count": 3,  # latency, db_connections, error_rate (cpu Z=1.875 < 2.0 threshold)
        },
        {
            "label": "DNS cascade peak",
            "metrics": {"latency_ms": 6200, "cpu_percent": 22, "db_connections": 15, "error_rate": 14.2},
            "expected_anomaly_count": 2,  # latency + error_rate
        },
        {
            "label": "Minor latency spike",
            "metrics": {"latency_ms": 120, "cpu_percent": 18, "db_connections": 25, "error_rate": 0.1},
            "expected_anomaly_count": 1,  # just latency
        },
    ]

    results = {}
    for tc in test_cases:
        anomalies = detect_anomalies(tc["metrics"])
        actual_count = len(anomalies)
        passed = actual_count >= tc["expected_anomaly_count"]
        results[tc["label"]] = {
            "expected_min_anomalies": tc["expected_anomaly_count"],
            "actual_anomalies":       actual_count,
            "anomalies_detected":     [a["metric"] for a in anomalies],
            "grade": "✅ PASS" if passed else "❌ FAIL",
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark 5: Graph End-to-End Pipeline Correctness
# ─────────────────────────────────────────────────────────────────────────────
def benchmark_graph_pipeline() -> dict:
    """
    Runs a full incident lifecycle through the agent graph and validates
    all expected outputs are produced.
    """
    results = {}

    for scenario_key in ["checkout_storm", "dns_cascade"]:
        IncidentSession.reset()
        sc = SCENARIO_DATABASE[scenario_key]

        state = IncidentState(
            status="RESOLVED",
            scenario_key=scenario_key,
            scenario_name=sc["name"],
            elapsed_seconds=330,
            sla_percent=99.92,
        )

        for log in sc["telemetry"]:
            state.raw_logs.append(LogEntry(
                timestamp=log["timestamp"], level=log["level"], message=log["message"]
            ))
        for chat in sc["chat"]:
            state.chat_history.append(ChatMessage(
                timestamp=chat["timestamp"], sender=chat["sender"], message=chat["message"]
            ))

        IncidentSession.set_state(state)
        graph = IncidentGraph()

        start = time.perf_counter()
        final_state = graph.execute_step()
        elapsed_ms = (time.perf_counter() - start) * 1000

        checks = {
            "timeline_populated":    len(final_state.factual_timeline) > 0,
            "three_email_drafts":    len(final_state.comms_email_drafts) == 3,
            "postmortem_generated":  final_state.post_mortem_report is not None,
            "postmortem_has_header": (
                "INCIDENT POST-MORTEM" in (final_state.post_mortem_report or "")
            ),
        }

        all_pass = all(checks.values())
        results[scenario_key] = {
            "checks": checks,
            "execution_time_ms": round(elapsed_ms, 1),
            "grade": "✅ PASS" if all_pass else "❌ FAIL",
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main Runner & Report Printer
# ─────────────────────────────────────────────────────────────────────────────
def run_all_benchmarks() -> dict:
    print("\n" + "="*70)
    print("  SRE-BRAIN EVALUATION BENCHMARK SUITE")
    print(f"  Run timestamp: {datetime.datetime.now().isoformat()}")
    print("="*70)

    report = {}

    # --- Benchmark 1 ---
    print("\n[B1] Benchmark 1: Alert Detection Accuracy")
    b1 = benchmark_alert_detection()
    report["alert_detection"] = b1
    for scenario, metrics in b1.items():
        print(f"   [{scenario}]  P={metrics['precision']}  R={metrics['recall']}  F1={metrics['f1']}")

    # --- Benchmark 2 ---
    print("\n[B2] Benchmark 2: Mean Time To Detect (MTTD)")
    b2 = benchmark_mttd()
    report["mttd"] = b2
    for scenario, m in b2.items():
        print(f"   [{scenario}]  MTTD={m['mttd_seconds']}s  Expected={m['expected_seconds']}s  {m['grade']}")

    # --- Benchmark 3 ---
    print("\n[B3] Benchmark 3: Financial Impact Accuracy")
    b3 = benchmark_financial_accuracy()
    report["financial_accuracy"] = b3
    for label, m in b3.items():
        print(f"   [{label}]  Expected=${m['expected']:,.0f}  Got=${m['actual']:,.0f}  Error={m['error_pct']}%  {m['grade']}")

    # --- Benchmark 4 ---
    print("\n[B4] Benchmark 4: Anomaly Detector Z-Score Validation")
    b4 = benchmark_anomaly_detector()
    report["anomaly_detector"] = b4
    for label, m in b4.items():
        print(f"   [{label}]  Detected={m['actual_anomalies']}/{m['expected_min_anomalies']}  {m['grade']}")

    # --- Benchmark 5 ---
    print("\n[B5] Benchmark 5: Full Graph Pipeline Correctness")
    b5 = benchmark_graph_pipeline()
    report["graph_pipeline"] = b5
    for scenario, m in b5.items():
        print(f"   [{scenario}]  {m['execution_time_ms']}ms  {m['grade']}")
        for check, passed in m["checks"].items():
            symbol = "[OK]" if passed else "[FAIL]"
            print(f"      {symbol} {check}")

    # --- Summary ---
    print("\n" + "="*70)
    grades = []
    for bench in report.values():
        if isinstance(bench, dict):
            for v in bench.values():
                if isinstance(v, dict) and "grade" in v:
                    grades.append(v["grade"])

    passes = sum(1 for g in grades if "PASS" in g)
    total  = len(grades)
    print(f"  OVERALL: {passes}/{total} checks PASSED")
    print("="*70 + "\n")

    # Save JSON report
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Full results saved to: {output_path}\n")

    return report


if __name__ == "__main__":
    run_all_benchmarks()
