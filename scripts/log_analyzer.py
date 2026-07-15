"""Analyze Cowrie JSON logs and produce summary reports."""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def load_logs(log_path: str) -> list[dict]:
    path = Path(log_path)
    if not path.exists():
        print(f"Error: Log file not found: {path}")
        sys.exit(1)

    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping malformed JSON line: {e}", file=sys.stderr)
    return events


class CowrieAnalyzer:
    def __init__(self, events: list[dict]):
        self.events = events
        self.sessions: dict[str, list[dict]] = defaultdict(list)
        self._group_by_session()

    def _group_by_session(self):
        for evt in self.events:
            session = evt.get("session")
            if session:
                self.sessions[session].append(evt)

    def summary(self) -> dict:
        total_connections = 0
        total_auth_success = 0
        total_auth_failed = 0
        total_commands = 0
        total_downloads = 0
        unique_ips: set = set()
        unique_usernames: set = set()
        unique_passwords: set = set()

        for evt in self.events:
            eid = evt.get("eventid", "")

            if eid == "cowrie.session.connect":
                total_connections += 1
                src_ip = evt.get("src_ip")
                if src_ip:
                    unique_ips.add(src_ip)

            elif eid == "cowrie.login.success":
                total_auth_success += 1
                username = evt.get("username")
                password = evt.get("password")
                if username:
                    unique_usernames.add(username)
                if password:
                    unique_passwords.add(password)

            elif eid == "cowrie.login.failed":
                total_auth_failed += 1
                username = evt.get("username")
                password = evt.get("password")
                if username:
                    unique_usernames.add(username)
                if password:
                    unique_passwords.add(password)

            elif "cowrie.command" in eid:
                total_commands += 1

            elif eid == "cowrie.session.file_download":
                total_downloads += 1

        total_auth = total_auth_success + total_auth_failed
        auth_rate = (total_auth_success / total_auth * 100) if total_auth > 0 else 0.0

        return {
            "total_events": len(self.events),
            "total_sessions": len(self.sessions),
            "total_connections": total_connections,
            "auth_success": total_auth_success,
            "auth_failed": total_auth_failed,
            "total_commands": total_commands,
            "total_downloads": total_downloads,
            "unique_ips": len(unique_ips),
            "unique_usernames": len(unique_usernames),
            "unique_passwords": len(unique_passwords),
            "auth_rate": auth_rate,
        }

    def top_ips(self, n: int = 10) -> list[tuple[str, int]]:
        ip_counter: Counter = Counter()
        for evt in self.events:
            if evt.get("eventid") == "cowrie.session.connect":
                ip = evt.get("src_ip")
                if ip:
                    ip_counter[ip] += 1
        return ip_counter.most_common(n)

    def top_usernames(self, n: int = 10) -> list[tuple[str, int]]:
        username_counter: Counter = Counter()
        for evt in self.events:
            eid = evt.get("eventid", "")
            if "login" in eid:
                username = evt.get("username")
                if username:
                    username_counter[username] += 1
        return username_counter.most_common(n)

    def top_passwords(self, n: int = 10) -> list[tuple[str, int]]:
        password_counter: Counter = Counter()
        for evt in self.events:
            eid = evt.get("eventid", "")
            if "login" in eid:
                password = evt.get("password")
                if password:
                    password_counter[password] += 1
        return password_counter.most_common(n)

    def commands_per_session(self) -> list[dict]:
        result = []
        for session_id, events in self.sessions.items():
            commands = []
            ip = "unknown"
            username = "unknown"
            timestamp = ""

            for evt in events:
                eid = evt.get("eventid", "")
                if "command" in eid:
                    commands.append(evt.get("input", ""))
                elif eid == "cowrie.session.connect":
                    ip = evt.get("src_ip", "unknown")
                    timestamp = evt.get("timestamp", "")
                elif "login" in eid:
                    username = evt.get("username", "unknown")

            if commands:
                result.append(
                    {
                        "session_id": session_id,
                        "ip": ip,
                        "username": username,
                        "timestamp": timestamp,
                        "commands": commands,
                        "command_count": len(commands),
                    }
                )
        return sorted(result, key=lambda x: x.get("timestamp", ""), reverse=True)

    def timeline(self) -> list[dict]:
        """Events per hour for charting."""
        hourly = Counter()
        for evt in self.events:
            ts = evt.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    hour_key = dt.strftime("%Y-%m-%d %H:00")
                    hourly[hour_key] += 1
                except ValueError:
                    pass
        return [{"hour": k, "count": v} for k, v in sorted(hourly.items())]

    def protocol_breakdown(self) -> list[dict]:
        proto_counter: Counter = Counter()
        for evt in self.events:
            proto = evt.get("protocol", "unknown")
            proto_counter[proto] += 1
        return [{"protocol": k, "count": v} for k, v in proto_counter.most_common()]

    def auth_rate(self) -> float:
        return self.summary()["auth_rate"]


def print_report(analyzer: CowrieAnalyzer):
    s = analyzer.summary()

    print("=" * 60)
    print("  COWRIE HONEYPOT - LOG ANALYSIS REPORT")
    print("=" * 60)
    print(f"\n  Total log events : {s['total_events']}")
    print(f"  Total sessions   : {s['total_sessions']}")
    print(f"  Connections       : {s['total_connections']}")
    print(f"  Auth successes    : {s['auth_success']}")
    print(f"  Auth failures     : {s['auth_failed']}")
    print(f"  Commands executed : {s['total_commands']}")
    print(f"  File downloads    : {s['total_downloads']}")
    print(f"  Unique IPs        : {s['unique_ips']}")
    print(f"  Unique usernames  : {s['unique_usernames']}")
    print(f"  Unique passwords  : {s['unique_passwords']}")
    print(f"  Auth success rate : {analyzer.auth_rate():.1f}%")

    print(f"\n{'-' * 60}")
    print("  TOP ATTACKER IPs")
    print(f"{'-' * 60}")
    for ip, count in analyzer.top_ips(5):
        print(f"  {ip:20s} : {count} connections")

    print(f"\n{'-' * 60}")
    print("  TOP USERNAMES")
    print(f"{'-' * 60}")
    for username, count in analyzer.top_usernames(10):
        print(f"  {username:20s} : {count} attempts")

    print(f"\n{'-' * 60}")
    print("  TOP PASSWORDS")
    print(f"{'-' * 60}")
    for pwd, count in analyzer.top_passwords(10):
        display = pwd if len(pwd) <= 30 else pwd[:27] + "..."
        print(f"  {display:30s} : {count} attempts")

    print(f"\n{'-' * 60}")
    print("  COMMANDS EXECUTED (most recent first)")
    print(f"{'-' * 60}")
    for session in analyzer.commands_per_session()[:5]:
        print(f"\n  Session: {session['session_id'][:12]}...")
        print(f"  IP     : {session['ip']}")
        print(f"  User   : {session['username']}")
        print(f"  Time   : {session['timestamp']}")
        for cmd in session["commands"]:
            print(f"    $ {cmd}")

    print(f"\n{'-' * 60}")
    print("  PROTOCOL BREAKDOWN")
    print(f"{'-' * 60}")
    for proto, count in analyzer.protocol_breakdown():
        print(f"  {proto:20s} : {count}")

    print(f"\n{'-' * 60}")
    print("  EVENT TIMELINE (hourly)")
    print(f"{'-' * 60}")
    for point in analyzer.timeline()[:10]:
        print(f"  {point['hour']} : {point['count']} events")

    print(f"\n{'=' * 60}\n")


def main():
    default_log = str(
        Path(__file__).resolve().parent.parent
        / "docker" / "cowrie" / "var" / "log" / "cowrie" / "cowrie.json"
    )
    log_path = sys.argv[1] if len(sys.argv) > 1 else default_log

    events = load_logs(log_path)
    analyzer = CowrieAnalyzer(events)
    print_report(analyzer)


if __name__ == "__main__":
    main()
