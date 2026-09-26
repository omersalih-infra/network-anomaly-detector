# Copy this file to config.py and fill in your real lab values.
# config.py is gitignored and must never be committed.

COMMUNITY = "CHANGE_ME"

DEVICES = [
    {"name": "Edge-RTR", "ip": "203.0.113.5",  "has_cpu": True},
    {"name": "Core-SW",  "ip": "203.0.113.10", "has_cpu": False},
    {"name": "Dist-SW1", "ip": "203.0.113.11", "has_cpu": False},
    {"name": "Dist-SW2", "ip": "203.0.113.12", "has_cpu": False},
]
