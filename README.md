# SRE-Brain 🧠⚡

> **Multi-Agent AI System for Chaos Mitigation & Automated Post-Mortem Generation**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-orange?logo=google)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-9%20Suites-brightgreen)](#testing)

---

## 🎯 What Is SRE-Brain?

SRE-Brain is an **AI-powered Site Reliability Engineering (SRE) platform** that automatically detects, triages, communicates, and documents infrastructure outages — designed to detect simulated incident scenarios in under 30 seconds, measured through the included benchmark suite and preventing tens of thousands of dollars in losses per incident.

**A 5-minute Black Friday checkout outage = $42,500 in lost revenue.** SRE-Brain cuts that window dramatically.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      LIVE INFRASTRUCTURE                         │
│  Server Logs  │  Slack Chat  │  Metrics (Latency, CPU, DB)      │
└───────┬───────┴──────┬───────┴──────────────┬───────────────────┘
        │              │                       │
        ▼              ▼                       ▼
┌───────────────────────────────────────────────────────────────┐
│                    SRE-BRAIN AGENT GRAPH                       │
│                                                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐  │
│  │  TelemetryTriage    │───▶│     CommsSyncAgent          │  │
│  │  Agent              │    │                             │  │
│  │  • Z-Score Anomaly  │    │  • Context Compaction       │  │
│  │    Detection        │    │  • 3-Tone Email Drafting    │  │
│  │  • Timeline Builder │    │    (Calm / Technical /      │  │
│  │  • Gemini RCA       │    │     Crisis)                 │  │
│  │    Hypothesis       │    │                             │  │
│  └─────────────────────┘    └─────────────┬───────────────┘  │
│                                           │                   │
│                            ┌──────────────▼──────────────┐   │
│                            │  Resolved? (Router Node)    │   │
│                            └──────┬──────────────────────┘   │
│                                   │ YES                       │
│                    ┌──────────────▼──────────────┐            │
│                    │  PostMortemAgent             │            │
│                    │  • GitHub MCP (Root Cause)   │            │
│                    │  • Financial Impact Calc     │            │
│                    │  • Gemini Lessons Learned    │            │
│                    │  • Markdown Report Output    │            │
│                    └──────────────────────────────┘            │
└───────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-Agent Architecture** | 3 specialized agents with cyclic graph execution |
| 📊 **Statistical Anomaly Detection** | Z-score analysis with sliding window baselines |
| 💬 **Slack Context Compaction** | Filters panic noise, extracts diagnostic signals |
| 📧 **3-Tone Auto-Drafting** | Calm / Technical / Crisis executive emails |
| 💸 **Financial Impact Calculator** | Real-time dollar loss per second per scenario |
| 📝 **Automated Post-Mortems** | Full regulatory markdown reports with RCA |
| 🧠 **Gemini AI Integration** | LLM-powered root cause hypothesis & lessons learned |
| 🔗 **Integration Layer** | GitHub PR context and Slack digest adapters with mock and live modes |
| 📈 **Eval Benchmark Suite** | Precision/Recall/F1, MTTD, financial accuracy |

---

## 📁 Project Structure

```
SRE_app/
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container deployment
├── .env.example           
│
└── sre_brain_project/
    ├── agent.yaml              # Agent configuration manifest
    ├── agents/
    │   ├── telemetry_agent.py  # Log triage + Gemini RCA hypothesis
    │   ├── comms_agent.py      # Slack compaction + email drafting
    │   └── post_mortem_agent.py# Report generation + Gemini lessons
    ├── core/
    │   ├── graph.py            # Cyclic agent execution graph
    │   ├── session.py          # Shared incident state session
    │   └── states.py           # Pydantic data models
    ├── tools/
    │   ├── anomaly_detector.py # Z-score statistical anomaly detection
    │   ├── context_compactor.py# Slack signal filtering
    │   └── mock_telemetry.py   # Realistic incident scenario database
    ├── skills/
    │   ├── calculate_impact.py # Financial impact skill
    │   ├── mcp_github.py       # GitHub MCP tool (PR context)
    │   └── mcp_slack.py        # Slack MCP tool
    └── eval/
    │   ├── test_eval.py        # 9-suite pytest evaluation
    │   └── benchmark.py        # Quantitative benchmark suite
    └── ui/
        ├── dashboard.py        # Frontend code using streamlit
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sre-brain.git
cd sre-brain
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional — for Gemini AI)

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 4. Run the Dashboard

```bash
streamlit run sre_brain_project/ui/dashboard.py
```

### 5. Run with Docker

```bash
docker build -t sre-brain .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key sre-brain
```

---

## 🧪 Testing & Evaluation

### Unit Test Suite (9 test classes)

```bash
cd sre_brain_project
python -m pytest eval/test_eval.py -v --tb=short
```

### Quantitative Benchmark Suite

```bash
python sre_brain_project/eval/benchmark.py
```

The benchmark measures:
- **Alert Detection**: Precision, Recall, F1-score vs ground truth labels
- **MTTD**: Mean Time To Detect — seconds from incident start to first alert
- **Financial Accuracy**: Cost calculation error percentage
- **Anomaly Detector**: Z-score validation against healthy/critical snapshots
- **Graph Pipeline**: End-to-end correctness and execution time

---

## 📊 Incident Scenarios

| Scenario | Description | Cost/Minute |
|---|---|---|
| **checkout_storm** | Black Friday database connection pool exhaustion | $8,500/min |
| **dns_cascade** | DNS registrar ClientHold suspension | $4,000/min |
| **latency_loop** | Promotions service synchronous timeout cascade | $3,200/min |

---

## 🧠 Gemini AI Integration

When a `GOOGLE_API_KEY` is configured:

1. **TelemetryTriageAgent** generates a natural-language root-cause hypothesis from detected events using `gemini-1.5-flash`
2. **PostMortemAgent** generates 3 personalized "Lessons Learned" bullets tailored to the specific incident scenario and financial impact

Both fall back to rule-based logic if no API key is provided — ensuring the system works in any environment.

---

## 🔬 Anomaly Detection

The `SlidingWindowDetector` uses statistical Z-score analysis:

```
Z = |value - baseline_mean| / baseline_std

Z >= 2.0 → WARNING
Z >= 3.5 → CRITICAL
```

Baselines are defined per metric (latency, CPU, DB connections, error rate, request rate) and are also adaptively computed from recent observations in streaming mode.

---

## 🎥 Demo

Watch the 3-minute demo: [YouTube link][https://youtu.be/S7yNnyBQDe0]

The demo shows a checkout outage progressing through anomaly detection, AI-assisted triage, stakeholder communication, financial-impact estimation, and automated post-mortem generation.

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgements

Built with:
- [OpenAI Codex](https://openai.com/codex/) — Used with GPT‑5.6 to design, build, test, and refine SRE-Brain
- [Google Gemini AI](https://aistudio.google.com) — Runtime LLM reasoning for RCA hypotheses and lessons learned
- [Streamlit](https://streamlit.io) — Dashboard UI
- [Pydantic](https://docs.pydantic.dev) — Data validation
- [Altair](https://altair-viz.github.io) — Data visualization

---
