"""Kuromi Dashboard — Cyberpunk attack telemetry visualization."""

import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_PATH = Path(os.environ.get(
    "COWRIE_LOG",
    _PROJECT_ROOT / "docker" / "cowrie" / "var" / "log" / "cowrie" / "cowrie.json"
))


def load_events():
    if not LOG_PATH.exists():
        return []
    events = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def analyze():
    events = load_events()
    if not events:
        return {"error": "No attack data captured yet"}

    sessions = {}
    for evt in events:
        session = evt.get("session")
        if session:
            sessions.setdefault(session, []).append(evt)

    auth_success = 0
    auth_failed = 0
    connections = 0
    commands = []
    downloads = 0
    ip_counter = Counter()
    username_counter = Counter()
    password_counter = Counter()
    hourly_counter = Counter()

    for evt in events:
        eid = evt.get("eventid", "")

        if eid == "cowrie.session.connect":
            connections += 1
            ip = evt.get("src_ip")
            if ip:
                ip_counter[ip] += 1

        elif eid == "cowrie.login.success":
            auth_success += 1
            user = evt.get("username", "")
            pwd = evt.get("password", "")
            if user:
                username_counter[user] += 1
            if pwd:
                password_counter[pwd] += 1

        elif eid == "cowrie.login.failed":
            auth_failed += 1
            user = evt.get("username", "")
            pwd = evt.get("password", "")
            if user:
                username_counter[user] += 1
            if pwd:
                password_counter[pwd] += 1

        elif "command" in eid:
            cmd = evt.get("input", "")
            if cmd:
                commands.append(cmd)

        elif eid == "cowrie.session.file_download":
            downloads += 1

        ts = evt.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hour_key = dt.strftime("%Y-%m-%d %H:00")
                hourly_counter[hour_key] += 1
            except ValueError:
                pass

    command_counter = Counter(commands)
    total_auth = auth_success + auth_failed
    auth_rate = round((auth_success / max(total_auth, 1)) * 100, 1)

    return {
        "stats": {
            "total_events": len(events),
            "sessions": len(sessions),
            "connections": connections,
            "auth_success": auth_success,
            "auth_failed": auth_failed,
            "commands": len(commands),
            "unique_commands": len(command_counter),
            "downloads": downloads,
            "unique_ips": len(ip_counter),
            "unique_usernames": len(username_counter),
            "unique_passwords": len(password_counter),
            "auth_rate": auth_rate,
        },
        "top_ips": [
            {"ip": ip, "count": c, "bar": c}
            for ip, c in ip_counter.most_common(10)
        ],
        "top_usernames": [
            {"username": u, "count": c, "bar": c}
            for u, c in username_counter.most_common(10)
        ],
        "top_passwords": [
            {"password": p, "count": c, "bar": c}
            for p, c in password_counter.most_common(10)
        ],
        "top_commands": [
            {"command": cmd, "count": c, "bar": c}
            for cmd, c in command_counter.most_common(10)
        ],
        "timeline": [
            {"hour": h.split(" ")[1], "count": c}
            for h, c in sorted(hourly_counter.items())
        ],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    return jsonify(analyze())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
