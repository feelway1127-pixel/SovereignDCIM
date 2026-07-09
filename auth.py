"""
auth.py — 세션 기반 인증/인가 모듈
--------------------------------------------------
"""
import os
import hmac
import hashlib
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

_DEFAULT_SALT = os.environ.get("DCIM_PASSWORD_SALT", "dcim-kr-static-salt")

def _hash_password(password: str, salt: str = _DEFAULT_SALT) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()

# 🚨 관리자 비밀번호 1147 기본 세팅
USERS = {
    "admin": {
        "password_hash": _hash_password(os.environ.get("DCIM_ADMIN_PASSWORD", "1147")),
        "role": "admin",
        "display_name": "총괄 관리자",
    },
    "operator": {
        "password_hash": _hash_password(os.environ.get("DCIM_OPERATOR_PASSWORD", "operator123")),
        "role": "operator",
        "display_name": "운영자",
    },
}

def verify_credentials(username: str, password: str):
    user = USERS.get(username)
    if not user: return None
    if hmac.compare_digest(user["password_hash"], _hash_password(password)): return user
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