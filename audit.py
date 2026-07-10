"""
audit.py — 감사 로그(Audit Trail) 영구 저장 모듈
--------------------------------------------------
"""
import json
from datetime import datetime, timezone
from collections import deque

_MAX_ENTRIES = 500
_log = deque(maxlen=_MAX_ENTRIES)
AUDIT_LOG_FILE = "dcim_audit.log"

def record(user: str, action: str, detail: str = "", result: str = "success"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "user": user,
        "action": action,
        "detail": detail,
        "result": result,
    }
    
    # 1. API 빠른 응답을 위한 In-memory 큐 저장
    _log.append(entry)
    
    # 2. 영구 보존 및 SIEM 연동을 위한 로컬 파일 Append-only 기록 (위변조 방지 기초)
    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[-] Audit log file write failed: {e}")
        
    return entry

def all_entries():
    return list(reversed(_log))