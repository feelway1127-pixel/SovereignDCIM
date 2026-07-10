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


# Sovereign AI DCIM (dcim.kr)

국가 주권 AI 데이터센터를 위한 사이버-물리 보안(Cyber-Physical Security) 아키텍처 PoC 및 통합 관제 대시보드입니다. (IEEE TDSC / arXiv 투고 논문 구현체)

**Live Demo:** https://dcim.kr

## 주요 구현체
본 리포지토리는 웹 대시보드(Facade)뿐만 아니라, 논문에서 제안한 커널 및 하드웨어 레벨의 핵심 모듈을 포함하고 있습니다.

- `kernel/dcim_telemetry.bpf.c`: eBPF 및 Atomic Memory Barrier를 이용한 O(1) Lockless 텔레메트리 파이프라인.
- `core/nvme_opal_purge.c`: TCG OPAL 2.0 SED 대상 NVMe IOCTL 기반 하드웨어 파쇄(Crypto Erase).
- `ai_engine.py`: 열 관성(Thermal-Inertia) 인지 및 Z-score 기반 이상탐지 엔진.
- `auth.py` & `audit.py`: 동적 Salt 기반 PBKDF2 인증 및 Append-only 로컬 감사 로그.

## 실행 방법

```bash
# 1. 의존성 패키지 설치
$ pip install -r requirements.txt

# 2. 보안 환경 변수 설정 (필수)
$ export DCIM_ADMIN_PASSWORD="your_admin_password"
$ export DCIM_OPERATOR_PASSWORD="your_operator_password"
$ export DCIM_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# 3. 서버 실행
$ python app.py
