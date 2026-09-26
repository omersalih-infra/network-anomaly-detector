# AI-Assisted Network Anomaly Detector

Project 2 in a portfolio of AI-assisted networking tools. Extends the hybrid
deterministic-detection + LLM-reporting architecture from a companion project
(an [AI-assisted network compliance auditor](https://github.com/omersalih-infra/network-compliance-auditor))
into dynamic, behavioural anomaly detection over SNMP-polled interface metrics.

A locally hosted LLM (Qwen 2.5 7B, via Ollama) is used **only** to explain
already-determined findings — never to perform detection itself. All anomaly
detection is deterministic: an Isolation Forest model and an independent
statistical threshold method are compared side by side, plus a dedicated
reachability check for total SNMP outages.

## Architecture

1. **Metric Collector** (`collector_snmp.py`) — polls interface traffic,
   error counters, and operational status via SNMP (`snmpget`) across four
   Cisco IOS devices in a GNS3 lab, appending results to CSV.
2. **Detection layer** — two independent, deterministic methods:
   - `detect_anomalies.py` / `detect_flood_test.py` — Isolation Forest
     (scikit-learn) on interface counter deltas.
   - `detect_threshold.py` — flags any delta exceeding 10x a device's own
     historical median for that metric.
3. **Reachability checker** (`detect_reachability.py`) — flags polls where a
   device returns no SNMP data at all (as opposed to a single interface
   going down).
4. **AI reporting layer** (`generate_incident_report.py`) — sends the
   combined structured findings (`combine_findings.py`) to a local Qwen 2.5
   model to produce a narrative Markdown report.

## Key finding

The threshold-based method achieved 100% recall on a real traffic-flood
fault-injection test, versus 40% for Isolation Forest under a fixed
contamination-rate assumption. The LLM reporting layer, evaluated across two
prompt iterations, reproducibly inverted the underlying data even after
explicit correction — direct evidence that LLM narrative output must never
be treated as authoritative over deterministic detection results. Full
methodology, all three fault-injection tests, and the AI-reliability
evaluation are written up in the accompanying project report.

## Setup

```bash
pip install -r requirements.txt
cp config.example.py config.py   # fill in your real device IPs and SNMP community
python collector_snmp.py         # start polling
python detect_anomalies.py       # run Isolation Forest detection
python detect_threshold.py       # run threshold detection
python detect_reachability.py    # run reachability check
python combine_findings.py       # merge all findings into one JSON
python generate_incident_report.py  # generate the AI narrative report
```

`config.py` is gitignored — never commit real device IPs or SNMP community
strings.

## Repo contents

- `collector_snmp.py`, `detect_*.py`, `combine_findings.py`,
  `generate_incident_report.py` — the pipeline
- `config.example.py` — template config (documentation-range IPs, placeholder
  community string)
- `data/` — sample SNMP poll CSVs from the four test runs (baseline, flood,
  duplex-mismatch, link-flap)
- `sample_output/` — example detection results (JSON) and generated incident
  reports (Markdown) from two prompt iterations

## Lab environment

Reuses the five-device GNS3 topology and Ubuntu AI server from the companion
compliance-auditor project. See the full project report for topology
details, fault-injection methodology, and the complete evaluation.

## Limitations

- Cisco IOU (used for the lab switches) does not emulate physical-layer
  error counters, so duplex-mismatch faults produce no SNMP-visible signal —
  a documented platform limitation, not a detection failure.
- Each fault type was tested once; reported detection rates reflect single
  trials, not statistically robust long-run rates.
- The AI reporting layer's factual-reliability issues were evaluated
  qualitatively across two prompt versions on one model (Qwen 2.5 7B).
