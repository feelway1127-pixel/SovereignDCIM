# Sovereign-DCIM: Cyber-Physical Security (CPS) Architecture Design

**Author:** System Architect  
**Project Link:** https://dcim.kr / GitHub Repository  

---

## 1. Executive Summary
This project (Sovereign-DCIM) is an advanced Cyber-Physical Security (CPS) integrated architecture designed to counter sophisticated supply chain attacks and physical takeover threats targeting sovereign AI data centers.

Moving beyond mere software-level defenses, it fuses Linux kernel telemetry with hardware (ASIC) control to prove (PoC) a zero-tolerance security philosophy: **"Even if the OS is fully compromised, the system's Root of Trust must be physically guaranteed."**

---

## 2. Core Security Architecture (Threat Model Defense Strategy)

This system establishes a three-stage defense logic against adversary penetration scenarios.

* **Stage 1: eBPF-based Kernel Transparency (Evasion Prevention)**
    * Traditional agent-based monitoring can be terminated or tampered with by attackers. This system establishes a lockless eBPF pipeline operating at the kernel level, collecting stealthy and robust telemetry that attackers cannot detect or bypass.
* **Stage 2: Thermal-Inertia Aware AI Engine (Anomaly Workload Detection)**
    * Rather than relying on simple CPU thresholds, it applies a lightweight AI engine (linear regression and Z-score anomaly detection) that models the physical power consumption and cooling dynamics of the data center. This instantly identifies malicious workload spikes (e.g., DoS attacks).
* **Stage 3: TCG OPAL 2.0 Hardware Zeroization (The Kill Switch)**
    * In the worst-case scenario where a system takeover is imminent, rather than performing OS-level file deletion, it dispatches direct IOCTL commands to the NVMe disk controller. This triggers a Crypto Erase, physically and irreversibly destroying the hardware encryption keys.

---

## 3. Directory & Module Breakdown

To minimize the attack surface, the architecture strictly separates the 'Control Dashboard (Web)' from the 'Hardware Control Unit'.

### 3.1. Core Security & Kernel Modules (C/eBPF)
*The deepest layer controlling hardware and the kernel.*
* **`core/nvme_opal_purge.c` (Hardware Zeroization Module)**
    * The ultimate kill switch activated upon root compromise. Compliant with TCG OPAL 2.0, it sends hardware-level purge commands directly to NVMe SED chipsets, making data permanently irrecoverable.
* **`kernel/dcim_telemetry.bpf.c` (Kernel Telemetry Pipeline)**
    * An eBPF program utilizing an $\mathcal{O}(1)$ lockless ring-buffer structure. It monitors system states with zero context-switching overhead, virtually eliminating resource waste during high-load operations.

### 3.2. Central Control & AI Brain (Python)
*Analyzes collected data and safely visualizes it for administrators.*
* **`app.py` (API Gateway & Routing)**
    * The core web server engine powering the control room. It acts as a hub, strictly separating backend logic from the frontend.
* **`auth.py` (Dynamic Salt Authentication)**
    * Security authorization module. It blocks pre-computed dictionary and rainbow table attacks by applying PBKDF2 hashing with unique, dynamic random salts (Dynamic Salt) for each user.
* **`audit.py` (Immutable Audit Trail)**
    * The audit log recording all critical system activities. Designed as an 'Append-only' local record to prevent attackers from covering their tracks, ensuring strict forensic integrity.
* **`ai_engine.py` (Anomaly Detection Engine)**
    * A lightweight AI analyzer that processes IoT telemetry (IT Power, PUE) using linear regression and Z-scores to predict physical states 30 seconds ahead and flag anomalies in real-time.

---

## 4. Future Work (Roadmap)
For future deployment in national networks and enterprise environments, the following enhancements are planned:
1.  **SIEM Integration:** Establishing a forwarding pipeline to transmit the locally preserved audit logs (`audit.py`) in real-time to centralized security monitoring systems like ELK Stack or Splunk.
2.  **Multi-Signature Authorization:** Introducing a workflow that requires cryptographic approval and OTP 2FA from two or more administrators, rather than a single user, to trigger the hardware zeroization (`nvme_opal_purge.c`).