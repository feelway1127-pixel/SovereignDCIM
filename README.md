# dcim.kr — Sovereign AI DCIM (포트폴리오 데모)

국정원 AI DCIM 관련 채용/제안 포트폴리오용 데모 애플리케이션입니다.
데이터센터의 2D/3D 현황, 랙 실장도(U-Level), 네트워크 토폴로지를 AI 워크로드(예: LLM 학습)에 따라
실시간으로 시각화하고, 예측/이상탐지를 수행하는 경량 AI 엔진과 보안 통제(인증/인가/감사로그)를 포함합니다.

## 실행 방법

```bash
pip install -r requirements.txt

# 운영 계정 비밀번호는 반드시 환경변수로 지정하세요 (미지정 시 데모 기본값 사용 — 실배포 금지)
export DCIM_ADMIN_PASSWORD="원하는 관리자 비밀번호"
export DCIM_OPERATOR_PASSWORD="원하는 운영자 비밀번호"
export DCIM_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

python app.py
```

`http://localhost:5000` 접속 → `admin` 또는 `operator` 계정으로 로그인.

> `FLASK_DEBUG=1`을 명시적으로 설정하지 않는 한 디버그 모드는 항상 꺼져 있습니다
> (이전 버전은 `debug=True`로 고정되어 있어 원격 코드 실행 위험이 있었습니다 — 수정됨).

## 이번 개선에서 반영한 것

| 영역 | 이전 상태 | 개선 내용 |
|---|---|---|
| 보안 | `debug=True` 고정, 인증 없음 | `debug` 기본 비활성화, 세션 기반 로그인 + RBAC(`admin`/`operator`) |
| 고위험 작업 | 제로화 버튼이 JS `confirm()`만으로 실행 | 관리자 권한 + **비밀번호 재인증(reauth)** 없이는 서버에서 거부 |
| 감사 추적 | 없음 | 로그인/로그아웃/워크로드 변경/제로화 등 전 작업을 서버측 감사 로그에 기록, 관리자 화면에서 조회 가능 |
| AI 요소 | 온도/전력이 전부 `Math.random()` | 서버측 `ai_engine.py`가 최근 텔레메트리에 대해 **선형회귀 기반 예측**과 **Z-score 이상탐지**를 실제로 계산하여 API로 제공 |
| 투명성 | 시뮬레이션임을 밝히지 않음 | 대시보드 상단에 SIMULATION MODE 배너, 제로화 응답에도 "실제 하드웨어 미변경" 명시 |
| 코드 구조 | 단일 파일(HTML+JS+CSS+Python 혼재) | `app.py` / `auth.py` / `ai_engine.py` / `audit.py` + `templates/` + `static/` 분리 |
| UX/보안 오인 요소 | 우클릭 차단, 개발자도구 단축키 차단 | 제거 (우회가 쉬워 실효성이 없고, 오히려 아마추어적으로 보일 수 있음) |
| 동시성 | 전역 변수 무잠금 변경 | `threading.Lock`으로 상태 변경 보호 |

## 아키텍처 메모

- **관심사 분리**: `update_dcim_physics()`는 지금은 수학적 시뮬레이션이지만, 실제 배포 시에는
  이 함수만 SNMP/BACnet/Redfish/Modbus 폴러로 교체하면 됩니다. 그 아래 AI 엔진(`ai_engine.py`)과
  API 계층은 텔레메트리의 출처를 몰라도 되도록 설계했습니다.
- **AI 엔진**: 지금은 의존성 최소화를 위해 순수 파이썬 선형회귀 + Z-score를 사용합니다. 실제 정밀도가
  필요하면 `TimeSeriesBuffer` 클래스 내부만 statsmodels(ARIMA)나 경량 LSTM으로 교체하면 되고,
  외부 인터페이스(`push`, `forecast`, `anomaly_score`)는 유지됩니다.
- **감사 로그**: 데모는 프로세스 메모리(`collections.deque`)에 저장합니다. 실배포 시에는
  위변조 방지(append-only + 해시체인)가 되는 저장소, 또는 SIEM으로의 실시간 전송이 필요합니다.

## 알려진 한계 (제안서/면접에서 정직하게 언급할 부분)

1. **텔레메트리가 시뮬레이션입니다.** 실제 센서/BMS 연동이 아직 없습니다. (로드맵: SNMP/BACnet/Redfish 폴러)
2. **감사 로그가 휘발성입니다.** 프로세스 재시작 시 소실됩니다. (로드맵: DB 영구 저장 + SIEM 연동)
3. **비밀번호 저장 방식이 데모 수준입니다.** PBKDF2를 쓰지만 정적 솔트를 기본값으로 둡니다. 실배포 시
   사용자별 랜덤 솔트, 혹은 사내 LDAP/SSO(OIDC/SAML) 연동이 필요합니다.
4. **MFA 미구현.** 공공기관 과제 특성상 관리자 계정은 최소 OTP 기반 2단계 인증이 필요합니다.
5. **제로화 승인이 1인 승인입니다.** 되돌릴 수 없는 작업이므로 실제로는 2인 승인(권한 분리) 워크플로우를
   권장합니다.
6. **컴플라이언스 매핑 문서 없음.** ISMS-P, CC인증(공통평가기준), 국정원 보안 지침과의 매핑표는 별도
   작성이 필요합니다 (이 README에는 포함하지 않았습니다).

## 프로젝트 구조

```
dcim-sovereign/
├── app.py              # Flask 앱 진입점, 라우트
├── auth.py             # 세션 인증 + RBAC 데코레이터
├── ai_engine.py         # 시계열 예측 / 이상탐지
├── audit.py             # 감사 로그
├── requirements.txt
├── templates/
│   ├── login.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/dashboard.js
```
