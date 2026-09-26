import pandas as pd
import json
df = pd.read_csv("data/metrics_flap_test.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

COUNTER_COLS = [c for c in df.columns if "octets" in c or "errors" in c]
THRESHOLD_MULTIPLIER = 10  # flag if delta > 10x the device's median delta for that metric

results = []

for device in df["device"].unique():
    dev_df = df[df["device"] == device].copy().sort_values("timestamp").reset_index(drop=True)

    delta_cols = []
    for col in COUNTER_COLS:
        dev_df[col] = pd.to_numeric(dev_df[col], errors="coerce")
        delta_col = col + "_delta"
        dev_df[delta_col] = dev_df[col].diff().clip(lower=0)
        delta_cols.append(delta_col)

    dev_df = dev_df.iloc[1:].reset_index(drop=True)  # drop first row, no prior delta

    for col in delta_cols:
        median_val = dev_df[col].median()
        if median_val <= 0:
            continue
        threshold = median_val * THRESHOLD_MULTIPLIER
        flagged = dev_df[dev_df[col] > threshold]
        for _, row in flagged.iterrows():
            results.append({
                "device": device,
                "timestamp": str(row["timestamp"]),
                "metric": col,
                "value": row[col],
                "device_median": median_val,
                "threshold": threshold
            })

with open("anomaly_results_threshold.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Threshold-based anomalies detected: {len(results)}")
for r in results:
    print(f"{r['device']:10s} {r['timestamp']}  {r['metric']:20s} value={r['value']:.0f}  (median={r['device_median']:.0f}, threshold={r['threshold']:.0f})")
