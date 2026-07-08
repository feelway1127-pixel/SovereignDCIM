from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for
from core_engine import SovereignCore
import time
import math
import random
import os

app = Flask(__name__)
# Render 환경 세션 유지용 시크릿 키
app.secret_key = os.urandom(24)

# ★★★ 대표님 전용 클리어런스 암호 ★★★
MASTER_PASSWORD = "sovereign2026!"

# 백엔드 엔진 연동 (SQLite DB 타임머신)
core = SovereignCore()

# =========================================================
# 1. 철통 보안 로그인 화면 UI (F12 차단 포함)
# =========================================================
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - RESTRICTED ACCESS</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #050505; color: #00ff41; font-family: 'JetBrains Mono', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; user-select: none; }
        .login-box { border: 1px solid #00ff41; padding: 40px; box-shadow: 0 0 30px rgba(0,255,65,0.3); text-align: center; width: 400px; background: rgba(0,0,0,0.9); }
        h1 { margin-top: 0; font-size: 32px; letter-spacing: 2px; }
        h1 span { color: #ff003c; }
        input[type="password"] { width: 100%; padding: 12px; margin-top: 20px; background: transparent; border: 1px solid #333; color: #00ff41; font-size: 16px; font-family: 'JetBrains Mono'; text-align: center; outline: none; }
        input[type="password"]:focus { border-color: #00ff41; }
        button { margin-top: 20px; width: 100%; padding: 14px; background: transparent; border: 1px solid #00ff41; color: #00ff41; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
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
    <script>
        // 🛡️ FRONT-END LOCKDOWN: F12, 우클릭, 소스보기 원천 차단
        document.addEventListener('contextmenu', event => event.preventDefault());
        document.onkeydown = function(e) {
            if (e.keyCode == 123 || (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) || (e.ctrlKey && e.keyCode == 85)) {
                return false;
            }
        };
    </script>
</body>
</html>
"""

# =========================================================
# 2. 궁극의 마스터 대시보드 UI (고충 해결 + 킬스위치 + F12 차단)
# =========================================================
MAIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - MASTER CONTROL</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --bg: #050505; --panel: #111; --text: #cbd5e1; --accent: #00ff41; --danger: #ef4444; --blue: #38bdf8; --border: #222; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; overflow-x: hidden; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 40px 40px; user-select: none; }
        .container { max-width: 1600px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
        .brand { font-size: 32px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -1px; }
        .brand span { color: var(--danger); }
        .llm-bar { flex: 1; margin: 0 40px; background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 10px 20px; display: flex; gap: 10px; }
        .llm-bar input { flex: 1; background: transparent; border: none; color: var(--blue); font-size: 14px; outline: none; font-family: 'JetBrains Mono'; }
        
        /* KPI 통계 (고충 1, 10번 해결) */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 5px; }
        .kpi-card { background: rgba(0,0,0,0.5); border: 1px solid var(--border); padding: 15px; border-radius: 6px; text-align: center; }
        .kpi-value { font-size: 26px; font-weight: 900; color: #fff; font-family: 'JetBrains Mono'; margin: 5px 0; }
        .kpi-label { font-size: 11px; color: #888; font-weight: bold; letter-spacing: 1px; }
        
        .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 15px; }
        .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); position: relative; }
        .panel h2 { margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase; color: #888; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between; border-bottom: 1px dashed var(--border); padding-bottom: 10px; }
        
        /* 2D 상면도 (고충 12번 해결) */
        .floor-plan { width: 100%; height: 320px; background: #000; border: 1px solid var(--border); position: relative; border-radius: 4px; overflow: hidden; }
        canvas#floorCanvas { width: 100%; height: 100%; display: block; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); border: 1px solid var(--blue); color: #fff; padding: 10px; font-family: 'JetBrains Mono'; font-size: 11px; display: none; z-index: 100; pointer-events: none; }
        
        /* 액침냉각 & 킬스위치 (고충 5, 21번 해결) */
        .turbidity-ring { width: 70px; height: 70px; border-radius: 50%; border: 5px solid var(--blue); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: #fff; margin: 0 auto; transition: 0.3s; }
        .diode-animation { width: 100%; height: 3px; background: #222; margin: 10px 0; position: relative; overflow: hidden; }
        .diode-beam { position: absolute; top: 0; left: -50px; width: 50px; height: 100%; background: var(--blue); box-shadow: 0 0 10px var(--blue); animation: diode 2s infinite linear; }
        @keyframes diode { to { left: 100%; } }
        
        .kill-btn { width: 100%; background: rgba(239, 68, 68, 0.1); border: 2px solid var(--danger); color: var(--danger); padding: 15px; font-weight: 900; font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 15px; }
        .kill-btn:hover { background: var(--danger); color: #000; box-shadow: 0 0 20px var(--danger); }
        
        /* 락다운 비상 화면 */
        .lockdown { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,5,5,0.95); z-index: 9999; flex-direction: column; justify-content: center; align-items: center; color: var(--danger); }
        .lockdown.active { display: flex; animation: bg-flash 0.5s infinite alternate; }
        @keyframes bg-flash { from { background: rgba(5,5,5,0.95); } to { background: rgba(30,0,0,0.95); } }
        
        /* 타임머신 테이블 */
        table { width: 100%; border-collapse: collapse; font-size: 11px; font-family: 'JetBrains Mono'; }
        th, td { border-bottom: 1px solid var(--border); padding: 6px; text-align: left; }
        th { color: #888; }
    </style>
</head>
<body>
    <div class="lockdown" id="lockdown-screen">
        <div style="font-size: 60px; font-weight: 900; font-family: 'Inter'; letter-spacing: 5px;">HARDWARE ZEROIZED</div>
        <div id="wipe-logs" style="margin-top: 30px; font-family: 'JetBrains Mono'; font-size: 14px; color: #fff; width: 600px; border: 1px solid #333; padding: 20px; background: #000;"></div>
    </div>

    <div class="container">
        <div class="header">
            <h1 class="brand">dcim<span>.kr</span></h1>
            <div class="llm-bar">
                <span style="color:#64748b;">🤖 LLM></span>
                <input type="text" id="llm-input" placeholder="명령어를 입력하세요 (예: 심야 요금제 맞춰서 3번 랙 VPP 세팅)" onkeypress="handleLLM(event)">
            </div>
            <a href="/logout" style="color: #64748b; text-decoration: none; font-size: 12px; font-family: 'JetBrains Mono';">[LOGOUT]</a>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">REAL-TIME PUE</div><div class="kpi-value" id="kpi-pue" style="color:var(--blue)">1.00</div></div>
            <div class="kpi-card"><div class="kpi-label">TOTAL IT POWER (kW)</div><div class="kpi-value" id="kpi-power">0.0</div></div>
            <div class="kpi-card"><div class="kpi-label">AI WORKLOAD LOAD</div><div class="kpi-value" id="kpi-load">0%</div></div>
            <div class="kpi-card"><div class="kpi-label">VPP REVENUE (KRW/h)</div><div class="kpi-value" id="kpi-vpp" style="color:var(--accent)">0</div></div>
        </div>

        <div class="main-grid">
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div class="panel">
                    <h2><span>🔥 2D Floor Plan Heatmap (고밀도 AI 랙 핫스팟)</span> <span id="cooling-badge" style="color:var(--blue); display:none;">❄️ PRE-COOLING ENGAGED</span></h2>
                    <div class="floor-plan">
                        <canvas id="floorCanvas"></canvas>
                        <div id="tooltip"></div>
                    </div>
                </div>
                <div class="panel">
                    <h2><span>⚡ AI Workload Power Prediction (전력 스파이크)</span></h2>
                    <div style="height: 150px;"><canvas id="trendChart"></canvas></div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div class="panel">
                    <h2><span>💧 Liquid Vision & Air-Gap</span></h2>
                    <div style="display:flex; justify-content:space-around; align-items:center;">
                        <div>
                            <div class="turbidity-ring" id="turb-val">0%</div>
                            <div style="text-align:center; font-size:10px; color:#888; margin-top:10px;">탁도 / 미세기포 분석</div>
                        </div>
                        <div style="flex:1; margin-left:20px; font-family:'JetBrains Mono'; font-size:11px; color:#888; text-align:center;">
                            OPTICAL DATA DIODE [TX]<br>
                            <div class="diode-animation"><div class="diode-beam"></div></div>
                            RF/Acoustic: <span style="color:var(--accent)">SECURE</span>
                        </div>
                    </div>
                </div>

                <div class="panel" style="flex: 1;">
                    <h2><span>⏳ INFRASTRUCTURE TIMEMACHINE LOGS</span></h2>
                    <table>
                        <thead><tr><th>TIME</th><th>HARDWARE ID</th><th>VALUE</th></tr></thead>
                        <tbody id="log-table"></tbody>
                    </table>
                </div>

                <div class="panel" style="border-color: var(--danger);">
                    <h2><span style="color:var(--danger)">⚠️ SUPER SOVEREIGN COMMAND</span></h2>
                    <div style="text-align:center; font-family:'JetBrains Mono'; font-size:11px; color:#888; margin-top:5px;">
                        Target: NPU Cluster (Row B)<br>Method: eFuse Crypto-Shredding
                    </div>
                    <button class="kill-btn" onclick="executeKillSwitch()">INITIATE HARDWARE ZEROIZATION</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ---------------------------------------------------------
        // 🛡️ FRONT-END LOCKDOWN: F12, 우클릭, 소스보기 원천 차단
        // ---------------------------------------------------------
        document.addEventListener('contextmenu', event => event.preventDefault());
        document.onkeydown = function(e) {
            if (e.keyCode == 123 || (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) || (e.ctrlKey && e.keyCode == 85)) {
                return false;
            }
        };

        // ---------------------------------------------------------
        // UI 로직 (캔버스, 차트, 데이터 연동)
        // ---------------------------------------------------------
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        
        function resizeCanvas() { canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; }
        window.addEventListener('resize', resizeCanvas); resizeCanvas();

        let racks = [];
        
        function drawFloorPlan(rackData) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const rows = 4; const cols = 12;
            const w = 30; const h = 45; const spX = 10; const spY = 50;
            const startX = (canvas.width - (cols * (w + spX))) / 2;
            const startY = 40;

            ctx.fillStyle = '#334155'; ctx.font = 'bold 12px Inter';
            ctx.fillText('COLD AISLE 1 (Storage)', startX + 150, startY + h + 30);
            ctx.fillText('HOT AISLE (AI NPU ZONE)', startX + 150, startY + h*2 + spY + 30);

            racks = rackData.map((data, i) => {
                let r = Math.floor(i / cols); let c = i % cols;
                let rx = startX + c * (w + spX); let ry = startY + r * (h + spY);
                
                let color = data.temp < 25 ? '#38bdf8' : data.temp < 45 ? '#00ff41' : data.temp < 70 ? '#f59e0b' : '#ef4444';
                
                ctx.shadowColor = color; ctx.shadowBlur = data.temp > 65 ? 10 : 0;
                ctx.fillStyle = color; ctx.fillRect(rx, ry, w, h);
                ctx.shadowBlur = 0; ctx.strokeStyle = '#000'; ctx.lineWidth = 1; ctx.strokeRect(rx, ry, w, h);
                
                return { ...data, x: rx, y: ry, w: w, h: h, color: color };
            });
        }

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            let mouseX = e.clientX - rect.left; let mouseY = e.clientY - rect.top;
            let hovered = false;
            for(let rack of racks) {
                if (mouseX >= rack.x && mouseX <= rack.x + rack.w && mouseY >= rack.y && mouseY <= rack.y + rack.h) {
                    tooltip.style.display = 'block'; tooltip.style.left = (e.clientX + 15) + 'px'; tooltip.style.top = (e.clientY + 15) + 'px';
                    tooltip.innerHTML = `<strong style="color:var(--accent)">${rack.id}</strong><br>Type: ${rack.type}<br>Temp: <span style="color:${rack.color}">${rack.temp.toFixed(1)} °C</span><br>Power: ${rack.power.toFixed(1)} kW`;
                    hovered = true; break;
                }
            }
            if (!hovered) tooltip.style.display = 'none';
        });
        canvas.addEventListener('mouseleave', () => tooltip.style.display = 'none');

        const trendChart = new Chart(document.getElementById('trendChart').getContext('2d'), {
            type: 'line',
            data: { labels: Array(20).fill(''), datasets: [
                { label: 'Total Power (kW)', data: Array(20).fill(0), borderColor: '#00ff41', borderWidth: 2, fill: true, backgroundColor: 'rgba(0, 255, 65, 0.1)', pointRadius: 0 },
                { label: 'Predicted (+45m)', data: Array(20).fill(0), borderColor: '#ef4444', borderDash: [5,5], borderWidth: 2, pointRadius: 0 }
            ]},
            options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display: false }, y: { grid: { color: '#222' } } }, plugins: { legend: { display: false } } }
        });

        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/v1/metrics');
                const data = await res.json();
                
                // KPI 업데이트
                document.getElementById('kpi-pue').innerText = data.summary.pue.toFixed(2);
                document.getElementById('kpi-power').innerText = data.summary.total_power_kw.toFixed(1);
                document.getElementById('kpi-load').innerText = (data.summary.load_factor * 100).toFixed(1) + "%";
                document.getElementById('kpi-vpp').innerText = "+" + Math.floor(data.db_data.VPP_GRID_POWER * 142).toLocaleString();
                document.getElementById('cooling-badge').style.display = data.db_data.THERMAL_PREDICT > 75 ? 'inline' : 'none';

                drawFloorPlan(data.racks);

                trendChart.data.datasets[0].data.push(data.summary.total_power_kw); trendChart.data.datasets[0].data.shift();
                trendChart.data.datasets[1].data.push(data.summary.total_power_kw * 1.2); trendChart.data.datasets[1].data.shift();
                trendChart.update();

                let turbidity = data.db_data.LIQUID_TURBIDITY;
                let turbEl = document.getElementById('turb-val');
                turbEl.innerText = turbidity.toFixed(1) + "%";
                turbEl.style.borderColor = turbidity > 9 ? "#f59e0b" : "#38bdf8";

                // 타임머신 로그 (core_engine 연동)
                document.getElementById('log-table').innerHTML = data.db_logs.map(log => 
                    `<tr><td>${log.timestamp.split(' ')[1]}</td><td style="color:var(--accent)">${log.hardware_id}</td><td>${log.value} ${log.unit}</td></tr>`
                ).join('');

            } catch(e) {}
        }
        setInterval(fetchTelemetry, 1500);

        function handleLLM(e) {
            if(e.key === 'Enter') {
                e.target.value = "> KEPCO 프로파일 분석 완료. VPP 수익 창출 모드로 자동 전환되었습니다.";
                e.target.style.color = "#00ff41";
                setTimeout(() => { e.target.value = ""; e.target.style.color = "#38bdf8"; }, 2500);
            }
        }

        function executeKillSwitch() {
            if(!confirm("⚠️ 치명적 경고: NPU 암호화 키를 하드웨어 레벨에서 물리적으로 파기합니다. (복구 확률 0%) 진행하시겠습니까?")) return;
            document.getElementById('lockdown-screen').classList.add('active');
            let logs = document.getElementById('wipe-logs');
            let msgs = ["[SYSTEM] BIOMETRIC AUTH ACCEPTED.", "[HARDWARE] INITIATING NIST SP 800-88 CRYPTO-SHREDDING...", "[BMC] Applying 12V Overvoltage to eFuse array...", "[STORAGE] NVMe SecureErase complete. DEK destroyed.", "[PDU] Physical power relays FORCED OPEN.", "DATA EXFILTRATION PREVENTED. SILICON DESTROYED."];
            let i = 0;
            let intv = setInterval(() => { logs.innerHTML += `> ${msgs[i]}<br>`; i++; if(i >= msgs.length) clearInterval(intv); }, 800);
            fetch('/api/v1/control/purge', { method: 'POST' });
            setTimeout(() => { location.reload(); }, 6000);
        }
    </script>
</body>
</html>
"""

# =========================================================
# 3. 플라스크 라우팅 및 백엔드 로직
# =========================================================
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(MAIN_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == MASTER_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template_string(LOGIN_HTML, error=True)
    return render_template_string(LOGIN_HTML, error=False)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/v1/metrics')
def get_metrics():
    """
    1. core_engine.py 의 config.json 규칙에 맞춘 센서 데이터를 DB에 적재합니다.
    2. 프론트엔드의 2D 상면도(48개 랙)에 뿌려질 디테일한 시뮬레이션 데이터도 같이 리턴합니다.
    """
    current_time = time.time()
    ai_workload = (math.sin(current_time / 6.0) + 1) / 2
    
    # [A] core_engine.py (DB 적재용) 데이터 생성
    avg_hot_temp = 25.0 + (ai_workload * 50) + random.uniform(-1, 1)
    predicted_temp = avg_hot_temp + (math.cos(current_time / 6.0) * 15)
    turbidity = 5.0 + (ai_workload * 6) + random.uniform(0, 1)
    
    live_data_for_db = {
        "VPP_GRID_POWER": round(3500 * ai_workload, 2),
        "THERMAL_CURRENT": round(avg_hot_temp, 2),
        "THERMAL_PREDICT": round(predicted_temp, 2),
        "LIQUID_TURBIDITY": round(turbidity, 2),
        "EFUSE_STATUS": 1
    }
    # 엔진을 호출하여 DB에 타임머신 로그 적재!
    processed_db_data = core.parse_and_log_metrics(live_data_for_db)
    
    # [B] 프론트엔드 UI용 48개 랙 상세 데이터 시뮬레이션
    rack_metrics = []
    total_it_power = 0.0
    for row_idx in range(4):
        row_letter = chr(65 + row_idx)
        for col_idx in range(1, 13):
            is_hpc = row_idx in [1, 2] # B, C열은 고밀도 AI NPU 랙
            base_temp = 24.0 if is_hpc else 21.0
            calc_temp = base_temp + (ai_workload * 55.0 if is_hpc else random.uniform(0, 3.0)) + random.uniform(-0.5, 0.5)
            calc_power = calc_temp * 0.45
            total_it_power += calc_power
            
            rack_metrics.append({
                "id": f"RACK-{row_letter}-{col_idx:02d}",
                "type": "NPU_ACCELERATOR" if is_hpc else "STANDARD_STORAGE",
                "temp": calc_temp,
                "power": calc_power
            })
            
    cooling_power = total_it_power * 0.4 + (ai_workload * 150.0)
    total_power = total_it_power + cooling_power
    pue = total_power / total_it_power if total_it_power > 0 else 1.0

    # UI가 요구하는 통합 JSON 응답
    return jsonify({
        "summary": {
            "load_factor": ai_workload,
            "total_power_kw": total_power,
            "pue": pue
        },
        "racks": rack_metrics,
        "db_data": {
            "VPP_GRID_POWER": live_data_for_db["VPP_GRID_POWER"],
            "THERMAL_PREDICT": predicted_temp,
            "LIQUID_TURBIDITY": turbidity
        },
        # core_engine 에서 과거 로그 5개 긁어오기
        "db_logs": core.get_historical_logs(limit=5)
    })

@app.route('/api/v1/control/purge', methods=['POST'])
def purge_node():
    return jsonify({"status": "acknowledged", "message": "Zeroization Initiated"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)