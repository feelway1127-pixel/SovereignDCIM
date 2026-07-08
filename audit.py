"""
audit.py — 감사 로그(Audit Trail)
--------------------------------------------------
데모에서는 프로세스 메모리(list)에 저장합니다.
실배포 시에는 반드시 다음으로 교체해야 합니다:
  - 위변조 방지를 위한 append-only 저장소 (예: DB의 INSERT-only 테이블 + 해시체인,
    혹은 별도 로그 수집 서버로의 실시간 전송)
  - SIEM/보안관제 시스템으로의 실시간 포워딩 (Syslog, Filebeat 등)
  - 최소 1년 이상 보존 (관련 보안 지침 기준)
"""
from datetime import datetime, timezone
from collections import deque

_MAX_ENTRIES = 500
_log = deque(maxlen=_MAX_ENTRIES)


def record(user: str, action: str, detail: str = "", result: str = "success"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "user": user,
        "action": action,
        "detail": detail,
        "result": result,
    }
    _log.append(entry)
    return entry


def all_entries():
    return list(reversed(_log))
