# Kuromi — Architecture

## System Overview

```mermaid
graph TB
    A[Attacker] -->|SSH :2222| B[Kuromi Engine]
    B -->|JSON events| C[(cowrie.json)]
    C --> D[Log Analyzer]
    C --> E[Kuromi Dashboard]
    E --> F[Browser UI]

    subgraph Docker Container
        B
        G[read-only FS]
        H[cap_drop ALL]
        I[tmpfs /tmp]
        J[no-new-privileges]
    end

    style A fill:#ff2d95,color:#fff
    style B fill:#1a1a2e,color:#fff,stroke:#7c3aed
    style C fill:#16213e,color:#fff,stroke:#00d4ff
    style D fill:#1a1a2e,color:#fff,stroke:#ff2d95
    style E fill:#1a1a2e,color:#fff,stroke:#7c3aed
    style F fill:#0f3460,color:#fff,stroke:#00d4ff
```

## Data Flow

1. **Attacker** connects to port 2222 (SSH) or 2223 (Telnet)
2. **Kuromi (Cowrie)** accepts the connection, presents a fake Ubuntu shell
3. Every interaction is logged as JSON events to `cowrie.json`
4. **Log Analyzer** reads the JSON and produces statistics
5. **Kuromi Dashboard** serves the cyberpunk web UI with real-time charts

## Security

| Layer | Protection |
|-------|-----------|
| **Capabilities** | `cap_drop: ALL` — No kernel capabilities |
| **Filesystem** | `read_only: true` — Container FS is immutable |
| **Privileges** | `no-new-privileges:true` — Can't run setuid |
| **Temp Space** | `tmpfs` — RAM only, wiped on restart |
| **Network** | Outbound disabled, isolated subnet 172.20.0.0/24 |
| **Config** | Config mounted `:ro` (read-only) |

## File Reference

| Path | Purpose |
|------|---------|
| `docker/docker-compose.yml` | Container orchestration |
| `docker/cowrie/etc/cowrie.cfg` | Cowrie configuration |
| `docker/cowrie/var/log/cowrie/` | Log storage |
| `scripts/log_analyzer.py` | Log analysis engine |
| `scripts/simulate_attacks.py` | Attack simulation tool |
| `dashboard/app.py` | Kuromi Flask dashboard |
| `tests/test_analyzer.py` | Unit tests |
