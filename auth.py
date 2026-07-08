"""
auth.py — 세션 기반 인증/인가 모듈
--------------------------------------------------
데모(포트폴리오) 목적의 최소 구현입니다. 실제 배포 시에는:
  - 사용자 저장소를 DB(PostgreSQL 등) 또는 사내 LDAP/SSO(SAML, OIDC)로 교체
  - 비밀번호는 bcrypt/argon2 등 전용 KDF 사용 (여기서는 의존성 최소화를 위해 PBKDF2 사용)
  - 세션은 Redis 등 외부 스토어에 저장, 다중 인스턴스 환경 대응
  - MFA(OTP/생체) 연동 — 국정원 등 공공기관 과제는 사실상 필수 요건
을 권장합니다.
"""
import os
import hmac
import hashlib
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

_DEFAULT_SALT = os.environ.get("DCIM_PASSWORD_SALT", "dcim-kr-static-salt-change-me")


def _hash_password(password: str, salt: str = _DEFAULT_SALT) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


# 실서비스 전환 시 DB로 교체할 사용자 테이블
USERS = {
    "admin": {
        "password_hash": _hash_password(os.environ.get("DCIM_ADMIN_PASSWORD", "ChangeMe!2026")),
        "role": "admin",
        "display_name": "관리자",
    },
    "operator": {
        "password_hash": _hash_password(os.environ.get("DCIM_OPERATOR_PASSWORD", "Operator!2026")),
        "role": "operator",
        "display_name": "운영자",
    },
}


def verify_credentials(username: str, password: str):
    """자격 증명 검증. 성공 시 사용자 dict, 실패 시 None."""
    user = USERS.get(username)
    if not user:
        return None
    if hmac.compare_digest(user["password_hash"], _hash_password(password)):
        return user
    return None


def verify_password_only(username: str, password: str) -> bool:
    """중요 작업 재인증(reauth)용 — 현재 로그인된 사용자의 비밀번호만 재확인."""
    return verify_credentials(username, password) is not None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized", "message": "로그인이 필요합니다."}), 401
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "forbidden", "message": "관리자 권한이 필요합니다."}), 403
        return view(*args, **kwargs)
    return wrapped
