import json

combined = {
    "traffic_flood_test": {
        "isolation_forest": [],
        "threshold_based": []
    },
    "interface_error_test": {
        "note": "No SNMP-detectable errors occurred despite a genuine duplex mismatch being applied for ~7.5 minutes with active traffic. This is a documented platform limitation: Cisco IOU does not emulate physical-layer error counters.",
        "findings": []
    },
    "link_flap_test": {
        "findings": []
    }
}

try:
    with open("anomaly_results.json") as f:
        combined["traffic_flood_test"]["isolation_forest"] = json.load(f)
except FileNotFoundError:
    pass

try:
    with open("anomaly_results_threshold.json") as f:
        combined["traffic_flood_test"]["threshold_based"] = json.load(f)
except FileNotFoundError:
    pass

try:
    with open("anomaly_results_reachability.json") as f:
        combined["link_flap_test"]["findings"] = json.load(f)
except FileNotFoundError:
    pass

with open("combined_findings.json", "w") as f:
    json.dump(combined, f, indent=2, default=str)

print("Combined findings written to combined_findings.json")
