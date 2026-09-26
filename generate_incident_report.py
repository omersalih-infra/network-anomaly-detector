import json
import requests

with open("combined_findings.json") as f:
    findings = json.load(f)

prompt = f"""
You are a network operations analyst reviewing results from CONTROLLED, DELIBERATE
fault-injection tests on a lab network. Every event described below was intentionally
caused by the test operator as part of a planned evaluation — these are NOT unexplained
production incidents, and no root-cause investigation is needed. Your job is only to
explain and summarize what was detected.

IMPORTANT DATA NOTES:
- The "threshold_based" list contains ONLY events that already exceeded their detection
  threshold. Every single entry in that list is a confirmed anomaly by definition — do
  not state that any entry "did not exceed threshold," since that would contradict the
  data itself.
- The "isolation_forest" list contains a separate, smaller set of anomalies flagged by a
  different statistical method (Isolation Forest) on the same underlying data. Compare
  its coverage against the threshold-based list explicitly: how many of the same
  timestamps did it catch, and how many did it miss?
- The link_flap_test findings represent a KNOWN, DELIBERATE interface shutdown performed
  by the test operator, causing temporary SNMP unreachability. Do not recommend
  "investigating the root cause" — the root cause is already known and stated.

For EACH test, individually, list every device and timestamp involved, and explain in
plain language what this pattern would mean if observed in a real production network.

Then write a short executive summary (3-5 sentences) comparing the coverage of the
Isolation Forest method versus the threshold-based method on the same flood event.

Findings data:
{json.dumps(findings, indent=2)}
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }
)

report = response.json()["response"]

with open("incident_report.md", "w") as f:
    f.write(report)

print(report)
