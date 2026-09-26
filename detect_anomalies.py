import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import json

df = pd.read_csv("data/metrics.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

COUNTER_COLS = [c for c in df.columns if ("octets" in c or "errors" in c)]

results = []

for device in df["device"].unique():
    dev_df = df[df["device"] == device].copy().sort_values("timestamp").reset_index(drop=True)

    for col in COUNTER_COLS:
        dev_df[col] = pd.to_numeric(dev_df[col], errors="coerce")
        # Convert cumulative counter -> delta since previous poll (rate proxy)
        delta_col = col.replace("octets", "delta").replace("errors", "err_delta")
        dev_df[delta_col] = dev_df[col].diff()
        dev_df[delta_col] = dev_df[delta_col].clip(lower=0)  # handle counter resets/wraps

    delta_cols = [c for c in dev_df.columns if "delta" in c]
    if "cpu" in dev_df.columns:
        dev_df["cpu"] = pd.to_numeric(dev_df["cpu"], errors="coerce")
        delta_cols.append("cpu")

    model_df = dev_df[delta_cols].dropna(axis=1, how="all").iloc[1:]  # drop first row (no prior delta)
    model_df = model_df.fillna(0)

    if model_df.shape[0] < 5 or model_df.shape[1] == 0:
        continue

    model = IsolationForest(contamination=0.05, random_state=42)
    predictions = model.fit_predict(model_df)

    dev_df = dev_df.iloc[1:].reset_index(drop=True)
    dev_df["anomaly"] = predictions

    anomalies = dev_df[dev_df["anomaly"] == -1]
    for _, row in anomalies.iterrows():
        results.append({
            "device": device,
            "timestamp": str(row["timestamp"]),
            "metrics": {col: row[col] for col in model_df.columns}
        })

with open("anomaly_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Baseline built from {len(df)} total samples across {df['device'].nunique()} devices.")
print(f"Anomalies detected: {len(results)}")
