# Kuromi — Honeypot Attack Capture & Analysis

[![MIT License](https://img.shields.io/badge/license-MIT-neonpink.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-ff2d95)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-required-7c3aed)](https://docker.com)
[![Cyber](https://img.shields.io/badge/style-cyberpunk-00d4ff)](https://github.com)

> **Kuromi** — A dark, elegant SSH honeypot platform. Watch attackers in real-time. Learn their tools. Stay ahead.

---

## Architecture

```mermaid
graph TB
    A[Attacker] -->|SSH :2222| B[Kuromi Engine]
    B -->|JSON logs| C[(cowrie.json)]
    C --> D[Log Analyzer]
    C --> E[Kuromi Dashboard]
    E --> F[Browser UI]

    subgraph Container Hardening
        B --> G[read-only FS]
        B --> H[cap_drop: ALL]
        B --> I[tmpfs /tmp]
        B --> J[no-new-privileges]
    end

    style A fill:#ff2d95,color:#fff
    style B fill:#1a1a2e,color:#fff,stroke:#7c3aed,stroke-width:2px
    style C fill:#16213e,color:#fff,stroke:#00d4ff
    style D fill:#1a1a2e,color:#fff,stroke:#ff2d95
    style E fill:#1a1a2e,color:#fff,stroke:#7c3aed
    style F fill:#0f3460,color:#fff,stroke:#00d4ff
```

## Quick Start

```bash
# Start Kuromi
cd docker && docker compose up -d

# Test the trap
ssh root@localhost -p 2222

# Analyze logs
python scripts/log_analyzer.py

# Launch dashboard
python dashboard/app.py
# Open http://127.0.0.1:5000
```

## Features

- **SSH/Telnet honeypot** — Full protocol emulation with realistic fake filesystem
- **Attack telemetry** — Every login, command, and file download captured in JSON
- **Security hardened** — Container with `read_only`, `cap_drop ALL`, `no-new-privileges`
- **Network contained** — Outbound traffic disabled, isolated Docker subnet
- **Log analyzer** — Python tool for attack statistics and session replay
- **Kuromi Dashboard** — Cyberpunk-themed real-time attack visualization
- **Attack simulator** — Generate test data to validate the pipeline

## Project Structure

```
kuromi/
├── docker/              # Container deployment
├── scripts/             # Python analysis tools
├── dashboard/           # Kuromi web dashboard
├── config/              # Shared configuration
├── tests/               # Unit tests (pytest)
├── docs/                # Documentation
├── logs/                # Archived attack data
├── assets/              # Screenshots and diagrams
├── report/              # Analysis reports
└── .github/workflows/   # CI/CD pipeline
```

## Security

| Layer | Protection |
|-------|-----------|
| **Capabilities** | `cap_drop: ALL` — no kernel capabilities |
| **Filesystem** | `read_only: true` — immutable container |
| **Privileges** | `no-new-privileges:true` — no escalation |
| **Temp space** | `tmpfs` — RAM-only, wiped on restart |
| **Network** | Outbound disabled, isolated subnet |
| **Config** | Mounted read-only (`:ro`) |

## License

MIT — See [LICENSE](LICENSE)
