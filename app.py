from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for
from core_engine import SovereignCore
import time
import math
import random
import os

app = Flask(__name__)
# Render 환경에서 세션을 유지하기 위한 보안 키
app.secret_key = os.urandom(24)

# ★★★ 대표님 전용 클리어런스 암호 (원하는 대로 변경하세요) ★★★
MASTER_PASSWORD = "sovereign2026!"

core = SovereignCore()

def get_super_sovereign_mock_stream():
    """
    백엔드에서 실시간으로 AI 워크로드 스파이크, 온도 예측, 탁도 데이터를 생성하여
    SovereignCore 엔진(DB)으로 넘겨주는 다이내믹 제너레이터입니다.
    """
    t = time.time()
    ai_workload = (math.sin(t / 8.0) + 1) / 2
    
    current_temp = 25.0 + (ai_workload * 45) + random.uniform(-1, 1)
    predicted_temp = current_temp + (math.cos(t / 8.0) * 15)
    turbidity = 5.0 + (ai_workload * 5) + random.uniform(0, 1)
    
    return {
        "VPP_GRID_POWER": round(3500 * ai_workload, 2),
        "THERMAL_CURRENT": round(current_temp, 2),
        "THERMAL_PREDICT": round(predicted_temp, 2),
        "LIQUID_TURBIDITY": round(turbidity, 2),
        "EFUSE_STATUS": 1 # 1: SECURE, 0: DESTROYED
    }

# --- 1. 철통 보안 로그인 화면 UI ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - RESTRICTED ACCESS</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #050505; color: #00ff41; font-family: 'JetBrains Mono', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { border: 1px solid #00ff41; padding: 40px; box-shadow: 0 0 20px rgba(0,255,65,0.2); text-align: center; width: 400px; background: rgba(0,0,0,0.8); }
        h1 { margin-top: 0; font-size: 28px; letter-spacing: 2px; }
        h1 span { color: #ff003c; }
        input[type="password"] { width: 100%; padding: 10px; margin-top: 20px; background: transparent; border: 1px solid #333; color: #00ff41; font-size: 16px; font-family: 'JetBrains Mono'; text-align: center; outline: none; }
        input[type="password"]:focus { border-color: #00ff41; }
        button { margin-top: 20px; width: 100%; padding: 12px; background: transparent; border: 1px solid #00ff41; color: #00ff41; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #00ff41; color: #000; }
        .error { color: #ff003c; margin-top: 15px; font-size: 14px; display: {% if error %}block{% else %}none{% endif %}; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>dcim<span>.kr</span></h1>
        <p style="font-size: 12px; color: #888;">SUPER SOVEREIGN ENGINE (CLASSIFIED)</p>
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="ENTER CLEARANCE CODE" required autofocus autocomplete="off">
            <button type="submit">AUTHORIZE</button>
        </form>
        <div class="error">ACCESS DENIED. INVALID CLEARANCE CODE.</div>
    </div>
</body>
</html>
"""

# --- 2. 7대 혁신 기능 마스터 대시보드 UI ---
MAIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - MASTER CONTROL</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --bg: #050505; --neon-green: #00ff41; --neon-red: #ef4444; --neon-blue: #38bdf8; --panel: #0a0a0c; --grid: rgba(255,255,255,0.03); }
        body { background-color: var(--bg); color: #cbd5e1; font-family: 'Inter', sans-serif; margin: 0; padding: 20px; overflow-x: hidden; background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px); background-size: 40px 40px; }
        .container { max-width: 1600px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 15px; }
        .brand { font-size: 32px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -1px; }
        .brand span { color: var(--neon-red); }
        
        .llm-bar { flex: 1; margin: 0 40px; background: #111; border: 1px solid #333; border-radius: 8px; padding: 10px 20px; display: flex; align-items: center; gap: 10px; }
        .llm-bar input { flex: 1; background: transparent; border: none; color: var(--neon-blue); font-size: 16px; outline: none; font-family: 'JetBrains Mono'; }
        
        .main-grid { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 15px; }
        .panel { background: var(--panel); border: 1px solid #222; border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); position: relative; }
        .panel h2 { margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase; color: #888; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between; border-bottom: 1px dashed #333; padding-bottom: 10px; }
        
        .chart-wrapper { height: 200px; width: 100%; }
        .vpp-status { font-size: 18px; font-weight: bold; color: var(--neon-green); text-align: center; margin-bottom: 10px; }
        
        .liquid-vision { display: flex; align-items: center; justify-content: center; gap: 30px; margin-top: 10px; }
        .turbidity-circle { width: 100px; height: 100px; border-radius: 50%; border: 6px solid var(--neon-blue); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: #fff; transition: 0.3s; }
        
        .airgap-status { text-align: center; font-family: 'JetBrains Mono'; font-size: 12px; margin-top: 20px; color: #a8a29e; }
        .diode-animation { width: 100%; height: 4px; background: #333; margin: 10px 0; position: relative; overflow: hidden; }
        .diode-beam { position: absolute; top: 0; left: -50px; width: 50px; height: 100%; background: var(--neon-blue); box-shadow: 0 0 10px var(--neon-blue); animation: diode 2s infinite linear; }
        @keyframes diode { to { left: 100%; } }

        .radar-container { width: 120px; height: 120px; border-radius: 50%; border: 1px solid var(--neon-green); margin: 0 auto; position: relative; background: radial-gradient(circle, rgba(0,255,65,0.1) 0%, rgba(0,0,0,1) 70%); }
        .radar-sweep { position: absolute; top: 50%; left: 50%; width: 50%; height: 50%; background: linear-gradient(45deg, rgba(0,255,65,0) 0%, rgba(0,255,65,0.8) 100%); transform-origin: 0 0; animation: sweep 2s infinite linear; }
        @keyframes sweep { to { transform: rotate(360deg); } }
        
        .kill-btn { width: 100%; background: transparent; border: 2px solid var(--neon-red); color: var(--neon-red); padding: 15px; font-weight: 900; font-size: 18px; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .kill-btn:hover { background: var(--neon-red); color: #000; }
        
        .emergency-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,5,5,0.95); z-index: 9999; flex-direction: column; justify-content: center; align-items: center; color: var(--neon-red); }
        .emergency-overlay.active { display: flex; animation: bg-flash 0.5s infinite alternate; }
        @keyframes bg-flash { from { background: rgba(5,5,5,0.95); } to { background: rgba(30,0,0,0.95); } }
        .glitch-text { font-size: 60px; font-weight: 900; font-family: 'Inter'; letter-spacing: 5px; text-shadow: 2px 2px 0px #000; }
        .log-stream { margin-top: 30px; font-family: 'JetBrains Mono'; font-size: 16px; color: #fff; width: 600px; text-align: left; border: 1px solid #333; padding: 20px; background: #000; }
        
        /* 타임머신 테이블 */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 11px; font-family: 'JetBrains Mono'; }
        th, td { border-bottom: 1px solid #222; padding: 8px; text-align: left; }
        th { color: #888; }
    </style>
</head>
<body>
    <div class="emergency-overlay" id="emergency-screen">
        <div class="glitch-text">HARDWARE ZEROIZED</div>
        <div class="log-stream" id="wipe-logs"></div>
    </div>

    <div class="container">
        <div class="header">
            <h1 class="brand">dcim<span>.kr</span></h1>
            <div class="llm-bar">
                <span>🤖 LLM></span>
                <input type="text" id="llm-input" placeholder="명령어를 자연어로 입력하세요. (예: 심야 요금제 맞춰서 3번 랙 VPP 세팅해줘)" onkeypress="handleLLM(event)">
            </div>
            <a href="/logout" style="color: #64748b; text-decoration: none; font-size: 14px; font-family: 'JetBrains Mono';">[LOGOUT]</a>
        </div>

        <div class="main-grid">
            <div class="panel">
                <h2><span>⚡ VPP Arbitrage</span> <span id="vpp-mode" style="color:var(--neon-green)">PROFIT MODE</span></h2>
                <div class="vpp-status" id="vpp-text">ESS -> KEPCO (Selling Grid Power)</div>
                <div style="font-size: 12px; color: #888; text-align: center; margin-bottom: 20px;">
                    실시간 송전량: <span id="vpp-power">0</span> kW | AI Batch Jobs: PAUSED
                </div>
                <h2><span>🔥 45m Predictive Thermal Twin</span></h2>
                <div class="chart-wrapper">
                    <canvas id="thermalChart"></canvas>
                </div>
            </div>

            <div class="panel">
                <h2><span>💧 Immersion Cooling Vision</span></h2>
                <div class="liquid-vision">
                    <div class="turbidity-circle" id="turbidity-display">--%</div>
                    <div style="font-size: 12px; color: #888;">
                        Turbidity / Micro-bubbles<br>
                        <span id="turbidity-status" style="color: var(--neon-blue);">Optimal Fluid State</span>
                    </div>
                </div>
                
                <h2 style="margin-top: 30px;"><span>🛡️ Air-Gap Integrity</span></h2>
                <div class="airgap-status">
                    OPTICAL DATA DIODE [ONE-WAY TX]<br>
                    <div class="diode-animation"><div class="diode-beam"></div></div>
                    RF/Acoustic Side-Channel: SECURE
                </div>
            </div>

            <div class="panel" style="border-color: #333;">
                <h2><span style="color:var(--neon-red)">⚠️ SUPER SOVEREIGN COMMAND</span></h2>
                <div class="radar-container"><div class="radar-sweep"></div></div>
                <div style="text-align: center; font-family: 'JetBrains Mono'; font-size: 11px; margin-top: 15px; color: #888;">
                    EMP/KINETIC THREAT RADAR: CLEAR<br>
                    eFuse Crypto Keys: INTACT
                </div>
                <button class="kill-btn" onclick="activateKillSwitch()">INITIATE CRYPTO-SHREDDING</button>
            </div>
        </div>
        
        <div class="panel">
            <h2><span>⏳ INFRASTRUCTURE TIMEMACHINE LOGS (SQLite Real-time Sync)</span></h2>
            <table>
                <thead>
                    <tr>
                        <th>TIMESTAMP</th>
                        <th>HARDWARE ID</th>
                        <th>VALUE</th>
                        <th>UNIT</th>
                    </tr>
                </thead>
                <tbody id="history-display">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Chart.js 초기화
        const ctx = document.getElementById('thermalChart').getContext('2d');
        const thermalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [
                    { label: 'Current (°C)', data: Array(20).fill(25), borderColor: '#38bdf8', borderWidth: 2, pointRadius: 0 },
                    { label: 'Predicted (+45m)', data: Array(20).fill(25), borderColor: '#ef4444', borderDash: [5, 5], borderWidth: 2, pointRadius: 0 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false, animation: false,
                scales: { y: { min: 20, max: 95, grid: { color: '#222' }, ticks: { color: '#888' } }, x: { grid: { display: false } } },
                plugins: { legend: { display: false } }
            }
        });

        // 백엔드 API 연동 루프
        async function fetchMetrics() {
            try {
                // 1. 실시간 생성 데이터 반영
                const resMetrics = await fetch('/api/v1/metrics');
                const data = await resMetrics.json();
                
                // 차트 업데이트
                thermalChart.data.datasets[0].data.push(data.THERMAL_CURRENT.value);
                thermalChart.data.datasets[0].data.shift();
                thermalChart.data.datasets[1].data.push(data.THERMAL_PREDICT.value);
                thermalChart.data.datasets[1].data.shift();
                thermalChart.update();
                
                // 액침냉각 뷰 업데이트
                const turbidity = data.LIQUID_TURBIDITY.value;
                document.getElementById('turbidity-display').innerText = turbidity + "%";
                if(turbidity > 10) {
                    document.getElementById('turbidity-display').style.borderColor = "#f59e0b";
                    document.getElementById('turbidity-display').style.color = "#fcd34d";
                    document.getElementById('turbidity-status').innerText = "Warning: Filter Replacement Needed";
                    document.getElementById('turbidity-status').style.color = "#f59e0b";
                } else {
                    document.getElementById('turbidity-display').style.borderColor = "#38bdf8";
                    document.getElementById('turbidity-display').style.color = "#fff";
                    document.getElementById('turbidity-status').innerText = "Optimal Fluid State";
                    document.getElementById('turbidity-status').style.color = "#38bdf8";
                }

                // VPP 업데이트
                document.getElementById('vpp-power').innerText = data.VPP_GRID_POWER.value;

                // 2. 타임머신 DB 이력 업데이트
                const resHistory = await fetch('/api/v1/history');
                const dataHistory = await resHistory.json();
                let historyHtml = '';
                dataHistory.forEach(row => {
                    historyHtml += `
                        <tr>
                            <td>${row.timestamp}</td>
                            <td style="color: #00ff41;">${row.hardware_id}</td>
                            <td>${row.value}</td>
                            <td>${row.unit}</td>
                        </tr>
                    `;
                });
                document.getElementById('history-display').innerHTML = historyHtml;

            } catch (error) { console.error("API Fetch Error"); }
        }
        setInterval(fetchMetrics, 1500);

        // LLM 바 시연
        function handleLLM(e) {
            if(e.key === 'Enter') {
                const input = e.target;
                input.value = "> KEPCO 프로파일 분석 완료. VPP 수익 창출 모드로 자동 전환되었습니다.";
                input.style.color = "#00ff41";
                setTimeout(() => { input.value = ""; input.style.color = "#38bdf8"; }, 2500);
            }
        }

        // 킬 스위치 연출
        function activateKillSwitch() {
            if(!confirm("⚠️ 경고: 이 명령은 AI 가속기 내부의 eFuse를 물리적으로 파괴합니다. 복구 절대 불가. 진행하시겠습니까?")) return;
            
            const overlay = document.getElementById('emergency-screen');
            const logs = document.getElementById('wipe-logs');
            overlay.classList.add('active');
            
            const msgSequence = [
                "BIOMETRIC AUTH ACCEPTED.",
                "INITIATING NIST SP 800-88 CRYPTO-SHREDDING...",
                "Applying 12V to cryptographic eFuse array...",
                "NVMe SecureErase executed. DEK destroyed.",
                "PDU Physical relays OPEN. Power cut.",
                "SILICON DESTROYED. DATA EXFILTRATION PREVENTED."
            ];
            
            let i = 0;
            const intv = setInterval(() => {
                logs.innerHTML += `> ${msgSequence[i]}<br>`;
                i++;
                if(i >= msgSequence.length) clearInterval(intv);
            }, 800);
            
            setTimeout(() => { location.reload(); }, 6000);
        }
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    # 세션에 로그인이 안 되어 있으면 /login으로 튕겨냄 (보안 유지)
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(MAIN_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        # 대표님이 설정한 비밀번호와 일치하는지 확인
        if request.form.get('password') == MASTER_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = True
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/v1/metrics')
def get_metrics():
    # 백엔드 엔진에서 동적으로 데이터를 찍어냅니다.
    live_data = get_super_sovereign_mock_stream()
    # 이 데이터를 core_engine으로 보내 타임머신 DB에 자동 기록합니다.
    processed_data = core.parse_and_log_metrics(live_data)
    return jsonify(processed_data)

@app.route('/api/v1/history')
def get_history():
    # SQLite에 기록된 타임머신 데이터를 가져와 UI에 뿌려줍니다.
    logs = core.get_historical_logs(limit=5)
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)