import os
import threading
from flask import Flask, jsonify, render_template, request, session, redirect, url_for

from auth import verify_credentials, verify_password_only, login_required, admin_required
from ai_engine import DcimAiEngine
import audit

app = Flask(__name__)

# --------------------------------------------------------------------
# 보안 설정
#   - SECRET_KEY는 반드시 환경변수로 주입 (미설정 시 매 프로세스 재시작마다
#     랜덤 생성되어 기존 세션이 모두 무효화됨 — 데모에서는 안전한 기본값)
#   - SESSION_COOKIE_* 옵션으로 쿠키 탈취/사이트 간 요청 위험 최소화
# --------------------------------------------------------------------
app.config.update(
    SECRET_KEY=os.environ.get("DCIM_SECRET_KEY", os.urandom(32)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("DCIM_FORCE_HTTPS", "0") == "1",
    PERMANENT_SESSION_LIFETIME=1800,  # 30분 유휴 시 세션 만료
)

# =========================================================
# 🧠 DCIM 코어 시뮬레이션 엔진
#
# ⚠️ SIMULATION DISCLOSURE (포트폴리오 명시사항):
# 아래 물리량(온도/전력)은 실제 센서 텔레메트리가 아니라 시연을 위한
# 수학적 모델입니다. 실제 배포 시에는 이 블록만 SNMP/BACnet/Redfish/Modbus
# 폴러로 교체하면 되고, 그 아래 AI 엔진과 API 레이어는 변경할 필요가
# 없도록 의도적으로 분리했습니다 (관심사 분리).
# =========================================================
_state_lock = threading.Lock()
SIM_STATE = {"workload": 0.1, "target_workload": 0.1}
ai_engine = DcimAiEngine()


def update_dcim_physics():
    with _state_lock:
        diff = SIM_STATE["target_workload"] - SIM_STATE["workload"]
        SIM_STATE["workload"] += diff * 0.2
        load = SIM_STATE["workload"]

    it_power = (load * 3000) + 500
    cooling_power = (load * 1000) + 200
    pue = (it_power + cooling_power) / it_power
    ai_engine.ingest(it_power, cooling_power, pue)
    return load, it_power, cooling_power, pue


# =========================================================
# 인증 라우트
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user = verify_credentials(username, password)

    if not user:
        audit.record(username or "(unknown)", "LOGIN_FAILED", result="failure")
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다."), 401

    session.clear()
    session["username"] = username
    session["role"] = user["role"]
    session["display_name"] = user["display_name"]
    session.permanent = True
    audit.record(username, "LOGIN_SUCCESS")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    if "username" in session:
        audit.record(session["username"], "LOGOUT")
    session.clear()
    return redirect(url_for("login"))


# =========================================================
# 대시보드
# =========================================================
@app.route("/")
@login_required
def index():
    return render_template(
        "dashboard.html",
        display_name=session.get("display_name", "사용자"),
        role=session.get("role", "operator"),
    )


# =========================================================
# API — 상태 / AI 인사이트
# =========================================================
@app.route("/api/v1/state", methods=["GET"])
@login_required
def get_state():
    load, it_power, cooling_power, pue = update_dcim_physics()
    return jsonify({
        "workload": load,
        "it_power_kw": round(it_power, 1),
        "cooling_power_kw": round(cooling_power, 1),
        "pue": round(pue, 2),
        "ai_insights": ai_engine.insights(),
    })


@app.route("/api/v1/control/workload", methods=["POST"])
@login_required
def control_workload():
    data = request.get_json(silent=True) or {}
    if "target_workload" not in data:
        return jsonify({"error": "target_workload 필드가 필요합니다."}), 400
    try:
        target = float(data["target_workload"])
    except (TypeError, ValueError):
        return jsonify({"error": "target_workload는 숫자여야 합니다."}), 400
    target = max(0.0, min(1.0, target))  # 0~1 범위로 클램프

    with _state_lock:
        SIM_STATE["target_workload"] = target
    audit.record(session["username"], "WORKLOAD_CHANGE", detail=f"target={target}")
    return jsonify({"status": "accepted", "target_workload": target})


# =========================================================
# API — Sovereign Protocol (고위험 작업: 관리자 + 재인증 필수)
# =========================================================
@app.route("/api/v1/control/purge", methods=["POST"])
@login_required
@admin_required
def purge_node():
    """
    ⚠️ 데모 한계 명시:
    실제 하드웨어 제로화(NIST SP 800-88)는 BMC/OOB 네트워크를 통한
    물리 계층 명령이 필요하며, 이 데모에서는 그 시퀀스를 흉내만 냅니다.
    실제로는 아래를 반드시 만족해야 합니다:
      1) 관리자 권한 (충족: @admin_required)
      2) 재인증(reauth) — 세션이 있어도 비밀번호 재확인 (충족: 아래 로직)
      3) 변경 불가능한 감사 로그 기록 (충족: audit.record, 단 저장소는 데모용)
      4) 되돌릴 수 없는 작업이므로 승인자 2인 이상(권한 분리) 등 추가 통제 권장 (미충족 — 로드맵)
    """
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not verify_password_only(session["username"], password):
        audit.record(session["username"], "PURGE_REAUTH_FAILED", result="failure")
        return jsonify({"error": "재인증 실패: 비밀번호가 올바르지 않습니다."}), 403

    target = data.get("target", "unspecified")
    audit.record(session["username"], "HARDWARE_PURGE_EXECUTED", detail=f"target={target}", result="simulated")
    return jsonify({"status": "simulated_zeroized", "note": "이 응답은 시뮬레이션입니다. 실제 하드웨어는 변경되지 않았습니다."})


# =========================================================
# API — 감사 로그 (관리자 전용)
# =========================================================
@app.route("/api/v1/audit", methods=["GET"])
@login_required
@admin_required
def get_audit_log():
    return jsonify({"entries": audit.all_entries()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"  # 기본값: 프로덕션 안전 모드
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
