import json
import sys
from pathlib import Path

log_path = (
    Path(__file__).resolve().parent.parent
    / "docker" / "cowrie" / "var" / "log" / "cowrie" / "cowrie.json"
)

if not log_path.exists():
    print(f"Log file not found: {log_path}")
    sys.exit(1)

lines = log_path.read_text().strip().split("\n")
print(f"Total log entries: {len(lines)}\n")

for line in lines:
    try:
        evt = json.loads(line)
        eid = evt.get("eventid", "")
        ts = evt.get("timestamp", "")
        msg = evt.get("message", "")

        if "connect" in eid:
            print(f"[{ts}] CONNECT: {evt.get('src_ip')}:{evt.get('src_port')}")
        elif "auth" in eid:
            username = evt.get("username", "")
            password = evt.get("password", "")
            success = evt.get("success", "")
            print(f"[{ts}] AUTH: {username}:{password} -> {success}")
        elif "command" in eid:
            print(f"[{ts}] CMD: {evt.get('input', '')}")
        elif "client.version" in eid:
            print(f"[{ts}] CLIENT: {evt.get('version', '')}")
        elif "closed" in eid:
            print(f"[{ts}] CLOSED: {evt.get('duration_ms')}ms")
        elif "kex" in eid:
            continue  # skip verbose key exchange
        else:
            print(f"[{ts}] {eid.split('.')[-1]}: {msg[:100]}")
    except json.JSONDecodeError:
        print(f"Bad JSON: {line[:100]}")
