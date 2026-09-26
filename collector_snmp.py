import subprocess
import csv
import time
import os
from datetime import datetime, timezone

from config import COMMUNITY, DEVICES

INTERFACES = [1, 2, 3, 4]

OID_IN_OCTETS  = "1.3.6.1.2.1.2.2.1.10"
OID_OUT_OCTETS = "1.3.6.1.2.1.2.2.1.16"
OID_IN_ERRORS  = "1.3.6.1.2.1.2.2.1.14"
OID_IF_STATUS  = "1.3.6.1.2.1.2.2.1.8"
OID_CPU        = "1.3.6.1.4.1.9.9.109.1.1.1.1.7.1"

def snmp_get(ip, oid):
    try:
        result = subprocess.run(
            ["snmpget", "-v2c", "-c", COMMUNITY, "-Ovq", ip, oid],
            capture_output=True, text=True, timeout=5
        )
        value = result.stdout.strip()
        return value if value else None
    except Exception:
        return None

def poll_device(dev):
    row = {"timestamp": datetime.now(timezone.utc).isoformat(), "device": dev["name"]}
    for idx in INTERFACES:
        row[f"if{idx}_in_octets"] = snmp_get(dev["ip"], f"{OID_IN_OCTETS}.{idx}")
        row[f"if{idx}_out_octets"] = snmp_get(dev["ip"], f"{OID_OUT_OCTETS}.{idx}")
        row[f"if{idx}_in_errors"] = snmp_get(dev["ip"], f"{OID_IN_ERRORS}.{idx}")
        row[f"if{idx}_status"] = snmp_get(dev["ip"], f"{OID_IF_STATUS}.{idx}")
    if dev["has_cpu"]:
        row["cpu"] = snmp_get(dev["ip"], OID_CPU)
    return row

def main(poll_interval=30, duration_minutes=None, output_file="data/metrics.csv"):
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.isfile(output_file) and os.path.getsize(output_file) > 0

    start = time.time()
    with open(output_file, "a", newline="") as f:
        writer = None
        while True:
            for dev in DEVICES:
                row = poll_device(dev)
                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    if not file_exists:
                        writer.writeheader()
                writer.writerow(row)
                print(f"[{row['timestamp']}] Polled {dev['name']}")
            f.flush()
            if duration_minutes and (time.time() - start) > duration_minutes * 60:
                break
            time.sleep(poll_interval)

if __name__ == "__main__":
    main(poll_interval=30, duration_minutes=None)
