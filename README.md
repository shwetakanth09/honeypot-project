<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/213910842-5a320d6b-e48f-4d41-a901-0e6a357e8dae.gif" width="900" height="auto"/>
</div>

<br>

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212257454-16e3712e-945a-4ca2-b238-408ad0bf87e6.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257472-08e52665-c503-4bd9-aa20-f5a4dae769b5.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257468-1e9a91f1-b626-4baa-b15d-5c385dfa7ed2.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257465-7ce8d493-cac5-494e-982a-5a9deb852c4b.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257463-4d082cb4-7483-4eaf-bc25-6dde2628aabd.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257460-738ff738-247f-4445-a718-cdd0ca76e2db.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212257467-871d32b7-e401-42e8-a166-fcfd7baa4c6b.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212280805-9bcb336b-8c55-46a8-abf8-ff286ab55472.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212281763-e6ecd7ef-c4aa-45b6-a97c-f33f6bb592bd.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212281775-b468df30-4edc-4bf8-a4ee-f52e1aaddc86.gif" width="80"/>
  <img src="https://user-images.githubusercontent.com/74038190/212281780-0afd9616-8310-46e9-a898-c4f5269f1387.gif" width="80"/>
</div>

<br>

<h1 align="center">Kuromi — SSH Honeypot with 3D Cyberpunk Dashboard</h1>

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-00f0ff)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-7000ff)](https://docker.com)
[![MIT License](https://img.shields.io/badge/license-MIT-ff0080)](LICENSE)
[![Windows](https://img.shields.io/badge/windows-ready-00ff87)](https://github.com)
[![Linux](https://img.shields.io/badge/linux-ready-00f0ff)](https://github.com)

</div>

> **Kuromi** — A real-time SSH honeypot with a cyberpunk 3D dashboard. Catch attackers, visualize attacks in 3D, and analyze their tools. Works on Windows & Linux.

<p align="center">
  <img src="assets/screenshot.png" width="900"/>
</p>

---

## Quick Start

### 🐳 Using Docker (recommended — works on any OS)

```bash
git clone https://github.com/shwetakanth09/honeypot-project.git
cd honeypot-project/docker
docker compose up -d
```

Open **http://localhost:5000** — the 3D dashboard is live!

### 🪟 Windows (without Docker)

```powershell
cd honeypot-project
python dashboard\app.py
```

Open **http://127.0.0.1:5000**

### 🐧 Linux (without Docker)

```bash
cd honeypot-project
python3 dashboard/app.py
```

Open **http://127.0.0.1:5000**

---

## What It Does

| Step | What happens |
|------|-------------|
| 1 | Cowrie honeypot listens on port **2222** for SSH attacks |
| 2 | Every connection, login attempt, and command is logged to `cowrie.json` |
| 3 | Flask dashboard reads the log and serves a **3D cyberpunk UI** |
| 4 | Stats update every 5 seconds — attackers, passwords, commands, timeline |

---

## 3D Dashboard Features

- **Torus knot** — Central animated 3D shape with pulsing emissive glow
- **Wireframes** — Dual counter-rotating wireframe overlays
- **Orbiters** — 5 icosahedrons orbiting at different speeds and radii
- **Constellation** — 500 particles with dynamic connecting lines (edge detection)
- **Glow rings** — 8 glowing rings at varying angles
- **Stars** — 2000 background stars for depth
- **Mouse parallax** — Camera follows cursor smoothly
- **Chart.js timeline** — Attack event timeline graph
- **Stats cards** — Sessions, failed logins, compromised, commands, downloads
- **Tables** — Top attackers, top usernames with bar indicators

---

## Project Structure

```
honeypot-project/
├── docker/                  # Docker deployment
│   ├── docker-compose.yml   # Cowrie + Dashboard services
│   └── cowrie/              # Cowrie config and logs
├── dashboard/               # Flask web dashboard
│   ├── app.py               # Flask backend (API + serve HTML)
│   ├── Dockerfile           # Container build file
│   └── templates/index.html # 3D cyberpunk UI with Three.js
├── scripts/                 # Python analysis tools
│   ├── log_analyzer.py      # Attack report generator
│   ├── simulate_attacks.py  # Generate test attack data
│   └── dump_logs.py         # Raw log viewer
├── tests/                   # Unit tests
├── assets/                  # Screenshots
└── .github/workflows/       # CI pipeline
```

---

## Commands

```bash
# Analyze captured attacks (terminal report)
python scripts/log_analyzer.py

# View raw logs
python scripts/dump_logs.py

# Generate simulated SSH attacks (requires paramiko)
pip install paramiko
python scripts/simulate_attacks.py

# Docker: view live logs
cd docker
docker compose logs -f dashboard
docker compose logs -f cowrie

# Docker: rebuild after code changes
docker compose build dashboard
docker compose up -d
```

---

## Architecture

```
Attacker ──SSH :2222──> Cowrie (honeypot) ──logs──> cowrie.json ──reads──> Dashboard (Flask) ──> Browser 3D UI
```

- Cowrie runs in a hardened container: read-only FS, no capabilities, no privilege escalation
- Dashboard container shares the log volume via bind mount
- Works cross-platform: all paths auto-detect from script location

---

## License

MIT
