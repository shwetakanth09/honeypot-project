"""Unit tests for the Cowrie log analyzer."""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from log_analyzer import CowrieAnalyzer


SAMPLE_EVENTS = [
    {
        "eventid": "cowrie.session.connect",
        "src_ip": "10.0.0.1",
        "src_port": 12345,
        "dst_ip": "10.0.0.2",
        "dst_port": 2222,
        "session": "abc123",
        "protocol": "ssh",
        "timestamp": "2026-07-14T14:20:52.948928Z",
    },
    {
        "eventid": "cowrie.client.version",
        "version": "SSH-2.0-OpenSSH_8.9",
        "session": "abc123",
        "timestamp": "2026-07-14T14:20:52.956020Z",
    },
    {
        "eventid": "cowrie.login.success",
        "username": "root",
        "password": "toor",
        "session": "abc123",
        "src_ip": "10.0.0.1",
        "timestamp": "2026-07-14T14:20:53.000000Z",
    },
    {
        "eventid": "cowrie.command.input",
        "input": "whoami",
        "session": "abc123",
        "timestamp": "2026-07-14T14:20:54.000000Z",
    },
    {
        "eventid": "cowrie.command.input",
        "input": "cat /etc/passwd",
        "session": "abc123",
        "timestamp": "2026-07-14T14:20:55.000000Z",
    },
    {
        "eventid": "cowrie.session.file_download",
        "url": "http://malware.example.com/bot.sh",
        "session": "abc123",
        "timestamp": "2026-07-14T14:20:56.000000Z",
    },
    {
        "eventid": "cowrie.session.closed",
        "duration_ms": 5000,
        "session": "abc123",
        "timestamp": "2026-07-14T14:20:57.000000Z",
    },
    {
        "eventid": "cowrie.session.connect",
        "src_ip": "10.0.0.2",
        "src_port": 54321,
        "dst_ip": "10.0.0.2",
        "dst_port": 2222,
        "session": "def456",
        "protocol": "ssh",
        "timestamp": "2026-07-14T14:21:00.000000Z",
    },
    {
        "eventid": "cowrie.login.failed",
        "username": "admin",
        "password": "admin123",
        "session": "def456",
        "src_ip": "10.0.0.2",
        "timestamp": "2026-07-14T14:21:01.000000Z",
    },
]


def test_load_events():
    """Test that events are correctly loaded from a JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        for evt in SAMPLE_EVENTS:
            f.write(json.dumps(evt) + "\n")
        tmp_path = f.name

    try:
        from log_analyzer import load_logs

        events = load_logs(tmp_path)
        assert len(events) == len(SAMPLE_EVENTS)
        assert events[0]["eventid"] == "cowrie.session.connect"
    finally:
        Path(tmp_path).unlink()


def test_summary():
    """Test that summary statistics are correct."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    s = analyzer.summary()

    assert s["total_events"] == 9
    assert s["total_sessions"] == 2
    assert s["total_connections"] == 2
    assert s["auth_success"] == 1
    assert s["auth_failed"] == 1
    assert s["total_commands"] == 2
    assert s["total_downloads"] == 1
    assert s["unique_ips"] == 2
    assert s["unique_usernames"] == 2
    assert s["unique_passwords"] == 2


def test_top_ips():
    """Test that IPs are ranked correctly."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    top = analyzer.top_ips(5)
    assert len(top) == 2
    assert top[0][0] == "10.0.0.1"
    assert top[0][1] == 1


def test_top_usernames():
    """Test that username ranking is correct."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    top = analyzer.top_usernames(5)
    assert len(top) == 2
    assert top[0][0] == "root"
    assert top[1][0] == "admin"


def test_top_passwords():
    """Test that password ranking is correct."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    top = analyzer.top_passwords(5)
    assert len(top) == 2
    assert top[0][0] == "toor"
    assert top[1][0] == "admin123"


def test_commands_per_session():
    """Test that commands are grouped by session correctly."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    sessions = analyzer.commands_per_session()
    assert len(sessions) == 1  # only one session had commands

    session = sessions[0]
    assert session["ip"] == "10.0.0.1"
    assert session["username"] == "root"
    assert session["command_count"] == 2
    assert session["commands"] == ["whoami", "cat /etc/passwd"]


def test_auth_rate():
    """Test authentication success rate calculation."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    rate = analyzer.auth_rate()
    assert rate == 50.0


def test_empty_logs():
    """Test that analyzer handles empty event list."""
    analyzer = CowrieAnalyzer([])
    s = analyzer.summary()
    assert s["total_events"] == 0
    assert s["auth_rate"] == 0.0
    assert analyzer.top_ips() == []
    assert analyzer.top_usernames() == []


def test_timeline():
    """Test timeline generation."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    timeline = analyzer.timeline()
    assert len(timeline) > 0
    assert "hour" in timeline[0]
    assert "count" in timeline[0]


def test_protocol_breakdown():
    """Test protocol breakdown."""
    analyzer = CowrieAnalyzer(SAMPLE_EVENTS)
    breakdown = analyzer.protocol_breakdown()
    assert len(breakdown) > 0
