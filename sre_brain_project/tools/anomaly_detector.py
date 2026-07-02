"""
SRE-Brain Anomaly Detector
Statistical anomaly detection using Z-score analysis and sliding window baselines.
Detects infrastructure anomalies before they become full outages.
"""
import math
from collections import deque
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Baseline Profiles (healthy system fingerprints per metric)
# ─────────────────────────────────────────────────────────────────────────────
HEALTHY_BASELINES = {
    "latency_ms":     {"mean": 35.0,   "std": 12.0},
    "cpu_percent":    {"mean": 15.0,   "std": 8.0},
    "db_connections": {"mean": 20.0,   "std": 10.0},
    "error_rate":     {"mean": 0.05,   "std": 0.08},
    "req_rate":       {"mean": 1000.0, "std": 200.0},
}

# Z-score thresholds for alert classification
THRESHOLD_WARNING  = 2.0   # 2 sigma deviation → WARNING
THRESHOLD_CRITICAL = 3.5   # 3.5 sigma deviation → CRITICAL


def z_score(value: float, mean: float, std: float) -> float:
    """Compute the Z-score (number of standard deviations from the mean)."""
    if std == 0:
        return 0.0
    return abs(value - mean) / std


def classify_anomaly(z: float) -> str:
    """Map Z-score to severity label."""
    if z >= THRESHOLD_CRITICAL:
        return "CRITICAL"
    elif z >= THRESHOLD_WARNING:
        return "WARNING"
    return "NOMINAL"


def detect_anomalies(metrics: dict) -> list[dict]:
    """
    Run Z-score anomaly detection over a dict of current metric values.

    Args:
        metrics: dict with keys matching HEALTHY_BASELINES
                 e.g. {"latency_ms": 4800, "cpu_percent": 32, ...}

    Returns:
        List of anomaly dicts: [{metric, value, z_score, severity, description}]
    """
    anomalies = []

    for metric, value in metrics.items():
        if metric not in HEALTHY_BASELINES:
            continue

        baseline = HEALTHY_BASELINES[metric]
        z = z_score(value, baseline["mean"], baseline["std"])
        severity = classify_anomaly(z)

        if severity != "NOMINAL":
            anomalies.append({
                "metric": metric,
                "value": value,
                "baseline_mean": baseline["mean"],
                "z_score": round(z, 2),
                "severity": severity,
                "description": _describe_anomaly(metric, value, baseline["mean"], severity),
            })

    return anomalies


def _describe_anomaly(metric: str, value: float, mean: float, severity: str) -> str:
    """Generate a human-readable description for an anomaly."""
    descriptions = {
        "latency_ms": (
            f"API latency at {value:.0f}ms is {value/mean:.1f}x above the healthy baseline of {mean:.0f}ms."
        ),
        "cpu_percent": (
            f"CPU utilization at {value:.0f}% exceeds normal operating range (baseline: {mean:.0f}%)."
        ),
        "db_connections": (
            f"Database connection pool at {value:.0f} active connections "
            f"({value/mean:.1f}x baseline). Risk of pool exhaustion."
        ),
        "error_rate": (
            f"HTTP error rate at {value:.2f}% — {value/max(mean, 0.01):.1f}x above normal. "
            f"Users are experiencing failures."
        ),
        "req_rate": (
            f"Request rate at {value:.0f} req/s. Significant traffic deviation from baseline {mean:.0f} req/s."
        ),
    }
    return descriptions.get(metric, f"{metric} anomaly: {value} (baseline: {mean})")


# ─────────────────────────────────────────────────────────────────────────────
# Sliding Window Detector (for real-time streaming scenarios)
# ─────────────────────────────────────────────────────────────────────────────
class SlidingWindowDetector:
    """
    Maintains a rolling window of metric observations and computes
    adaptive baselines from recent history (no fixed baseline required).

    Useful for streaming telemetry where healthy baselines shift over time.
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.windows: dict[str, deque] = {}

    def _get_window(self, metric: str) -> deque:
        if metric not in self.windows:
            self.windows[metric] = deque(maxlen=self.window_size)
        return self.windows[metric]

    def _adaptive_stats(self, metric: str) -> Optional[tuple[float, float]]:
        """Return (mean, std) from the current window, or None if insufficient data."""
        window = self._get_window(metric)
        if len(window) < 3:
            return None
        n = len(window)
        mean = sum(window) / n
        variance = sum((x - mean) ** 2 for x in window) / n
        std = math.sqrt(variance)
        return mean, std

    def push(self, metrics: dict) -> list[dict]:
        """
        Push a new metrics snapshot into the sliding windows and
        return any anomalies detected using adaptive baselines.
        """
        anomalies = []
        for metric, value in metrics.items():
            window = self._get_window(metric)
            stats = self._adaptive_stats(metric)

            if stats is not None:
                mean, std = stats
                # Fallback to fixed baseline std if window std is near zero
                if std < 0.5 and metric in HEALTHY_BASELINES:
                    std = HEALTHY_BASELINES[metric]["std"]

                z = z_score(value, mean, std)
                severity = classify_anomaly(z)

                if severity != "NOMINAL":
                    anomalies.append({
                        "metric": metric,
                        "value": value,
                        "adaptive_mean": round(mean, 2),
                        "z_score": round(z, 2),
                        "severity": severity,
                        "description": _describe_anomaly(metric, value, mean, severity),
                    })

            # Add the new observation to the window AFTER anomaly check
            window.append(value)

        return anomalies

    def compute_anomaly_score(self, metrics: dict) -> float:
        """
        Returns a composite 0–100 anomaly score representing overall system health.
        0 = fully healthy, 100 = extreme anomaly across all metrics.
        """
        anomalies = detect_anomalies(metrics)
        if not anomalies:
            return 0.0

        max_z = max(a["z_score"] for a in anomalies)
        # Normalize: z=0 → 0, z=5 → 100
        score = min(100.0, (max_z / 5.0) * 100.0)
        return round(score, 1)
