import pandas as pd
import json

df = pd.read_csv("data/metrics_flap_test.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

results = []

for device in df["device"].unique():
    dev_df = df[df["device"] == device].copy().sort_values("timestamp").reset_index(drop=True)
    status_cols = [c for c in dev_df.columns if "status" in c]

    # A poll is "unreachable" if every status column came back NaN
    dev_df["unreachable"] = dev_df[status_cols].isna().all(axis=1)

    outages = dev_df[dev_df["unreachable"]]
    for _, row in outages.iterrows():
        results.append({
            "device": device,
            "timestamp": str(row["timestamp"]),
            "event": "SNMP polling failure \u2014 device unreachable (all interface metrics missing)"
        })

with open("anomaly_results_reachability.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Reachability outages detected: {len(results)}")
for r in results:
    print(f"{r['device']:10s} {r['timestamp']}  {r['event']}")
