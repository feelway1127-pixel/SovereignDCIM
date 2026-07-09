# dcim-sovereign-core

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)

초고밀도 AI 클러스터(NPU/GPU) 환경을 위한 자율 제어 및 물리 보안 DCIM 코어 엔진입니다.
기존 SNMP 기반 폴링 수집기의 한계를 대체하기 위해 설계된 커널 레벨 텔레메트리 파이프라인과 열역학(Thermodynamics) 기반 상태 공간 제어 모듈을 포함합니다.

## Architecture Overview

본 저장소는 프론트엔드 대시보드(PoC)를 구동하기 위한 통합 서버와 3개의 코어 백엔드 모듈로 구성되어 있습니다.

* `core_digital_twin.py`: Linux `sysfs` 써멀 존 센서 데이터를 기반으로 NPU 섀시의 비열 방정식을 연산하는 MPC(Model Predictive Control) 엔진.
* `kafka_telemetry_broker.py`: REST API 병목을 피하기 위한 In-memory Queue 및 Pub/Sub 스트리밍 버스. (V2.0에서 Kafka 클러스터 연동 예정)
* `openbmc_zeroize.py`: OOB 네트워크를 통한 BMC 펌웨어 제어 및 NVMe SED 하드웨어 기반 Crypto-Erase(NIST SP 800-88 규격) 모듈.

## Prerequisites

* Python 3.14+
* Linux OS (커널 센서 및 블록 디바이스 제어를 위해 Windows/macOS 개발 환경에서는 Mock 모드로 동작함)
* root 권한 (`openbmc_zeroize.py`의 `ioctl` 시스템 콜 및 `os.sync()` 실행 시 필요)

## Getting Started

로컬 테스트 및 PoC 구동 환경 셋업입니다.

```bash
# 1. 의존성 패키지 설치
pip install -r requirements.txt

# 2. 필수 환경 변수 주입 (로컬 테스트용)
export DCIM_ADMIN_PASSWORD="your_secure_password"
export DCIM_SECRET_KEY=$(openssl rand -hex 32)

# 3. 개발 서버 실행
gunicorn --bind 0.0.0.0:5000 wsgi:app
