import os
import threading
from flask import Flask, jsonify, render_template, request, session, redirect, url_for

from auth import verify_credentials, verify_password_only, login_required, admin_required
from ai_engine import DcimAiEngine
import audit
from iot_collector import IoTCollector

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("DCIM_SECRET_KEY", os.urandom(32)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# 🧠 핵심 모듈 초기화
ai_engine = DcimAiEngine()
collector = IoTCollector(demo_mode=True)

def _run_collector():
    collector.start_polling_loop(ai_engine.ingest)
threading.Thread(target=_run_collector, daemon=True).start()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)
    
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user = verify_credentials(username, password)
    
    if not user:
        audit.record(username or "unknown", "LOGIN_FAILED", result="failure")
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다."), 401

    session.clear()
    session.update({"username": username, "role": user["role"], "display_name": user["display_name"]})
    session.permanent = True
    audit.record(username, "LOGIN_SUCCESS", "System access granted")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if "username" in session: audit.record(session["username"], "LOGOUT", "Session terminated")
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("dashboard.html", display_name=session.get("display_name"), role=session.get("role"))

# --- API Endpoints ---
@app.route("/api/v1/state", methods=["GET"])
@login_required
def get_state():
    with collector.state_lock:
        metrics = dict(collector.latest_metrics)
    
    # 프론트엔드 요구 규격에 맞춰 JSON 반환
    return jsonify({
        "workload": metrics["workload_factor"],
        "it_power_kw": metrics["it_power_kw"],
        "cooling_power_kw": metrics["cooling_power_kw"],
        "pue": metrics["pue"],
        "ai_insights": ai_engine.insights()
    })

@app.route("/api/v1/control/workload", methods=["POST"])
@login_required
def control_workload():
    data = request.get_json(silent=True) or {}
    target = max(0.0, min(1.0, float(data.get("target_workload", 0.1))))
    collector.set_target_workload(target)
    audit.record(session["username"], "WORKLOAD_CHANGED", detail=f"Target: {target*100}%")
    return jsonify({"status": "accepted"})

@app.route("/api/v1/control/purge", methods=["POST"])
@login_required
@admin_required
def purge_node():
    data = request.get_json(silent=True) or {}
    if not verify_password_only(session["username"], data.get("password", "")):
        audit.record(session["username"], "ZEROIZATION_FAILED", result="Invalid Auth Token")
        return jsonify({"error": "비밀번호 불일치"}), 403
    
    audit.record(session["username"], "ZEROIZATION_EXECUTED", detail="NIST SP 800-88 Simulated")
    return jsonify({"status": "zeroized"})

@app.route("/api/v1/audit", methods=["GET"])
@login_required
def get_audit_log():
    return jsonify({"entries": audit.all_entries()})

if __name__ == "__main__":
    print("[*] dcim.kr Enterprise Server Running... (Login: admin / 1147)")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))