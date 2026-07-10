# Sovereign AI DCIM (dcim.kr)

A Cyber-Physical Security (CPS) architecture Proof-of-Concept (PoC) and integrated control dashboard for Sovereign AI Data Centers. (Implementation of the architecture submitted to IEEE TDSC / arXiv)

**Live Demo:** https://dcim.kr

## Core Implementations
This repository contains not only the web dashboard (Facade) but also the core hardware and kernel-level modules proposed in the paper.

- `kernel/dcim_telemetry.bpf.c`: O(1) Lockless telemetry pipeline utilizing eBPF and Atomic Memory Barriers.
- `core/nvme_opal_purge.c`: NVMe IOCTL-based hardware Crypto Erase targeting TCG OPAL 2.0 SEDs.
- `ai_engine.py`: Thermal-Inertia aware and Z-score based anomaly detection engine.
- `auth.py` & `audit.py`: Dynamic Salt-based PBKDF2 authentication and Append-only local audit log.

## Quick Start

```bash
# 1. Install dependencies
$ pip install -r requirements.txt

# 2. Set environment variables for security (Required)
$ export DCIM_ADMIN_PASSWORD="your_admin_password"
$ export DCIM_OPERATOR_PASSWORD="your_operator_password"
$ export DCIM_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# 3. Run the server
$ python app.py
