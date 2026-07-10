"""
auth.py — 세션 기반 인증/인가 모듈 (Dynamic Salting 적용)
--------------------------------------------------
"""
import os
import hmac
import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

def _hash_password(password: str, salt: str) -> str:
    # 사용자 고유의 동적 솔트를 사용하여 PBKDF2 해싱 수행
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()

# 서버 구동 시 계정별 고유 Random Salt 생성 (실무 권장 방식)
ADMIN_SALT = secrets.token_hex(16)
OPERATOR_SALT = secrets.token_hex(16)

USERS = {
    "admin": {
        "salt": ADMIN_SALT,
        "password_hash": _hash_password(os.environ.get("DCIM_ADMIN_PASSWORD", "1147"), ADMIN_SALT),
        "role": "admin",
        "display_name": "총괄 관리자",
    },
    "operator": {
        "salt": OPERATOR_SALT,
        "password_hash": _hash_password(os.environ.get("DCIM_OPERATOR_PASSWORD", "operator123"), OPERATOR_SALT),
        "role": "operator",
        "display_name": "운영자",
    },
}

def verify_credentials(username: str, password: str):
    user = USERS.get(username)
    if not user: return None
    
    # 해당 유저의 고유 솔트를 가져와서 입력된 비밀번호 검증
    if hmac.compare_digest(user["password_hash"], _hash_password(password, user["salt"])): 
        return user
    return None

def verify_password_only(username: str, password: str) -> bool:
    return verify_credentials(username, password) is not None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403
        return view(*args, **kwargs)
    return wrapped