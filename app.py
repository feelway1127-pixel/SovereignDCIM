from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for
import time
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ★★★ 대표님 전용 클리어런스 암호 ★★★
MASTER_PASSWORD = "sovereign2026!"

# =========================================================
# 🧠 하이퍼 리얼리티 시뮬레이션 상태 엔진 (Global State)
# =========================================================
# 사용자의 조작(UI)에 따라 값이 변하고, 이 값에 의해 전체 인프라가 반응합니다.
SIM_STATE = {
    "target_workload": 0.1,  # 목표 AI 부하율
    "current_workload": 0.1, # 현재 AI 부하율 (서서히 목표치로 이동)
    "kepco_price": 120.5,    # 실시간 한전 전력 단가 (원/kWh)
    "cooling_mode": "NORMAL",# NORMAL 또는 PRE-COOLING
    "vpp_mode": "IDLE",      # IDLE, BUY(전력망 구매), SELL(수익 창출)
    "efuse_status": "SECURE"
}

def update_simulation_physics():
    """자연스러운 물리/열역학 변화를 시뮬레이션하는 엔진"""
    global SIM_STATE
    
    # 1. 워크로드의 자연스러운 이동 (관성 시뮬레이션)
    diff = SIM_STATE["target_workload"] - SIM_STATE["current_workload"]
    SIM_STATE["current_workload"] += diff * 0.2  # 20%씩 부드럽게 목표치로 접근
    
    # 2. 한전 요금 변동 시뮬레이션
    SIM_STATE["kepco_price"] += random.uniform(-2.0, 2.0)
    if SIM_STATE["kepco_price"] < 80: SIM_STATE["kepco_price"] = 80
    if SIM_STATE["kepco_price"] > 250: SIM_STATE["kepco_price"] = 250
    
    # 3. VPP 및 냉각 AI 자율 판단 로직
    if SIM_STATE["current_workload"] > 0.8:
        SIM_STATE["cooling_mode"] = "PRE-COOLING ENGAGED"
    else:
        SIM_STATE["cooling_mode"] = "NORMAL"

    if SIM_STATE["kepco_price"] > 180 and SIM_STATE["current_workload"] < 0.5:
        SIM_STATE["vpp_mode"] = "SELL (PROFIT)"
    elif SIM_STATE["current_workload"] > 0.8:
        SIM_STATE["vpp_mode"] = "BUY (HIGH LOAD)"
    else:
        SIM_STATE["vpp_mode"] = "IDLE (ESS CHARGING)"

# =========================================================
# 1. 철통 보안 로그인 화면 (F12 완벽 차단)
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
        .login-box { border: 1px solid #00ff41; padding: 40px; box-shadow: 0 0 40px rgba(0,255,65,0.2); text-align: center; width: 400px; background: rgba(0,0,0,0.9); }
        h1 { margin-top: 0; font-size: 36px; letter-spacing: 2px; } h1 span { color: #ff003c; }
        input { width: 100%; padding: 12px; margin-top: 20px; background: transparent; border: 1px solid #333; color: #00ff41; font-size: 16px; font-family: 'JetBrains Mono'; text-align: center; outline: none; transition: 0.3s; }
        input:focus { border-color: #00ff41; box-shadow: 0 0 10px rgba(0,255,65,0.3); }
        button { margin-top: 25px; width: 100%; padding: 14px; background: transparent; border: 1px solid #00ff41; color: #00ff41; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
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
        <div class="error">ACCESS DENIED.</div>
    </div>
    <script>
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.onkeydown = function(e) { if (e.keyCode == 123 || (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 67 || e.keyCode == 74)) || (e.ctrlKey && e.keyCode == 85)) return false; };
    </script>
</body>
</html>
"""

# =========================================================
# 2. 10000% 완벽 인터랙티브 마스터 대시보드
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
        :root { --bg: #050505; --panel: #0d0d0d; --text: #cbd5e1; --accent: #00ff41; --danger: #ef4444; --blue: #38bdf8; --border: #222; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; overflow-x: hidden; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 40px 40px; user-select: none; }
        .container { max-width: 1700px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
        .brand { font-size: 32px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -1px; }
        .brand span { color: var(--danger); }
        .llm-bar { flex: 1; margin: 0 40px; background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 10px 20px; display: flex; gap: 10px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }
        .llm-bar input { flex: 1; background: transparent; border: none; color: var(--blue); font-size: 15px; outline: none; font-family: 'JetBrains Mono'; }
        
        .kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 5px; }
        .kpi-card { background: rgba(0,0,0,0.6); border: 1px solid var(--border); padding: 15px; border-radius: 6px; text-align: center; position: relative; overflow: hidden; }
        .kpi-value { font-size: 28px; font-weight: 900; color: #fff; font-family: 'JetBrains Mono'; margin: 5px 0; }
        .kpi-label { font-size: 11px; color: #888; font-weight: bold; letter-spacing: 1px; }
        
        .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 15px; }
        .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }
        .panel h2 { margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase; color: #888; font-family: 'JetBrains Mono'; border-bottom: 1px dashed var(--border); padding-bottom: 10px; display: flex; justify-content: space-between; }
        
        /* 2D 상면도 */
        .floor-plan { width: 100%; height: 350px; background: #000; border: 1px solid var(--border); position: relative; border-radius: 4px; overflow: hidden; }
        canvas#floorCanvas { width: 100%; height: 100%; display: block; }
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); border: 1px solid var(--blue); color: #fff; padding: 10px; font-family: 'JetBrains Mono'; font-size: 11px; display: none; z-index: 100; pointer-events: none; }
        
        /* K8s 조작 패널 (인터랙티브) */
        .k8s-controls { display: flex; gap: 10px; margin-top: 15px; }
        .btn-control { flex: 1; padding: 10px; background: transparent; border: 1px solid var(--border); color: #888; font-family: 'JetBrains Mono'; font-size: 12px; cursor: pointer; transition: 0.3s; border-radius: 4px; }
        .btn-control:hover { border-color: var(--blue); color: var(--blue); background: rgba(56, 189, 248, 0.1); }
        .btn-control.active { border-color: var(--accent); color: var(--accent); background: rgba(0, 255, 65, 0.1); font-weight: bold; }
        
        /* 비상 락다운 화면 */
        .lockdown { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,5,5,0.95); z-index: 9999; flex-direction: column; justify-content: center; align-items: center; color: var(--danger); }
        .lockdown.active { display: flex; animation: bg-flash 0.5s infinite alternate; }
        @keyframes bg-flash { from { background: rgba(5,5,5,0.95); } to { background: rgba(30,0,0,0.95); } }
        
        .kill-btn { width: 100%; background: rgba(239, 68, 68, 0.05); border: 2px solid var(--danger); color: var(--danger); padding: 15px; font-weight: 900; font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 15px; border-radius: 4px; }
        .kill-btn:hover { background: var(--danger); color: #000; box-shadow: 0 0 20px var(--danger); }
        
        .terminal-log { background: #000; border: 1px solid var(--border); padding: 10px; height: 120px; overflow-y: auto; font-family: 'JetBrains Mono'; font-size: 11px; color: #888; }
        .terminal-log p { margin: 2px 0; }
    </style>
</head>
<body>
    <div class="lockdown" id="lockdown-screen">
        <div style="font-size: 70px; font-weight: 900; font-family: 'Inter'; letter-spacing: 5px; text-shadow: 0 0 20px var(--danger);">HARDWARE ZEROIZED</div>
        <div id="wipe-logs" style="margin-top: 30px; font-family: 'JetBrains Mono'; font-size: 16px; color: #fff; width: 700px; border: 1px solid #333; padding: 20px; background: #000;"></div>
    </div>

    <div class="container">
        <div class="header">
            <h1 class="brand">dcim<span>.kr</span></h1>
            <div class="llm-bar">
                <span style="color:#64748b;">🤖 Zero-UI></span>
                <input type="text" id="llm-input" placeholder="명령어 입력 (예: Llama-3 100B 학습 시작해줘, 전력망 수익모드 켜줘)" onkeypress="handleLLM(event)">
            </div>
            <a href="/logout" style="color: #64748b; text-decoration: none; font-size: 12px; font-family: 'JetBrains Mono';">[LOGOUT]</a>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">REAL-TIME PUE</div><div class="kpi-value" id="kpi-pue" style="color:var(--blue)">1.00</div></div>
            <div class="kpi-card"><div class="kpi-label">TOTAL IT POWER (kW)</div><div class="kpi-value" id="kpi-power">0.0</div></div>
            <div class="kpi-card"><div class="kpi-label">AI WORKLOAD (K8s)</div><div class="kpi-value" id="kpi-load">0%</div></div>
            <div class="kpi-card"><div class="kpi-label">KEPCO PRICE (KRW)</div><div class="kpi-value" id="kpi-kepco" style="color:#f59e0b">0</div></div>
            <div class="kpi-card"><div class="kpi-label">VPP REVENUE/h</div><div class="kpi-value" id="kpi-vpp" style="color:var(--accent)">0</div></div>
        </div>

        <div class="main-grid">
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div class="panel">
                    <h2>
                        <span>🔥 Predictive Thermal Twin (AI 핫스팟 관제)</span>
                        <span id="cooling-badge" style="color:var(--blue); font-weight:bold;">NORMAL</span>
                    </h2>
                    <div class="floor-plan">
                        <canvas id="floorCanvas"></canvas>
                        <div id="tooltip"></div>
                    </div>
                    
                    <div style="margin-top: 15px; border-top: 1px dashed var(--border); padding-top: 15px;">
                        <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #888;">[INTERACTIVE DEMO] K8s WORKLOAD INJECTION</span>
                        <div class="k8s-controls">
                            <button class="btn-control active" onclick="setWorkload(0.1, this)">IDLE (대기)</button>
                            <button class="btn-control" onclick="setWorkload(0.5, this)">BATCH INFERENCE (추론)</button>
                            <button class="btn-control" onclick="setWorkload(0.95, this)" style="color:var(--danger); border-color:var(--danger);">🔥 LLM 100B TRAINING (풀부하 학습)</button>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2><span>⚡ Power Spikes & Thermal Prediction</span></h2>
                    <div style="height: 160px;"><canvas id="trendChart"></canvas></div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div class="panel">
                    <h2><span>📈 VPP Arbitrage Engine</span></h2>
                    <div style="text-align:center; font-family:'JetBrains Mono'; font-size:24px; font-weight:bold; color:var(--accent); margin: 15px 0;" id="vpp-status-text">
                        IDLE
                    </div>
                    <div style="font-size:11px; color:#888; text-align:center;">한전 요금과 AI 부하에 따라 자율 충/방전 및 송전 결정</div>
                </div>

                <div class="panel">
                    <h2><span>🛡️ Sovereign Air-Gap Logs</span></h2>
                    <div class="terminal-log" id="term-box">
                        <p>[SYS] Optical Data Diode Link Established.</p>
                        <p>[SYS] RF/Acoustic Scanners Online. No threats.</p>
                    </div>
                </div>

                <div class="panel" style="border-color: var(--danger); flex: 1; display: flex; flex-direction: column; justify-content: flex-end;">
                    <h2><span style="color:var(--danger)">⚠️ SUPER SOVEREIGN COMMAND</span></h2>
                    <div style="text-align:center; font-family:'JetBrains Mono'; font-size:11px; color:#888; margin-top:5px;">
                        Target: NPU Cluster (Row B & C)<br>Hardware Root of Trust: INTACT
                    </div>
                    <button class="kill-btn" onclick="executeKillSwitch()">INITIATE CRYPTO-SHREDDING (자폭)</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ---------------------------------------------------------
        // 🛡️ FRONT-END LOCKDOWN
        // ---------------------------------------------------------
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.onkeydown = function(e) { if(e.keyCode==123 || (e.ctrlKey&&e.shiftKey&&(e.keyCode==73||e.keyCode==67||e.keyCode==74)) || (e.ctrlKey&&e.keyCode==85)) return false; };

        // ---------------------------------------------------------
        // 워크로드 주입 (Interactive Control)
        // ---------------------------------------------------------
        function setWorkload(load, btnElement) {
            // UI 버튼 스타일 변경
            document.querySelectorAll('.btn-control').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');
            
            // 백엔드 API로 명령 전송
            fetch('/api/v1/control/workload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ target_workload: load })
            });
            
            logTerminal(`[K8s] Workload injection requested: ${load*100}%`);
        }

        // 터미널 로그 추가 함수
        function logTerminal(msg) {
            const term = document.getElementById('term-box');
            const timeStr = new Date().toLocaleTimeString('en-US', {hour12:false});
            term.innerHTML += `<p><span style="color:#00ff41">[${timeStr}]</span> ${msg}</p>`;
            term.scrollTop = term.scrollHeight;
        }

        // ---------------------------------------------------------
        // 2D 캔버스 상면도
        // ---------------------------------------------------------
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        
        function resize() { canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; }
        window.addEventListener('resize', resize); resize();

        let racks = [];
        function drawFloorPlan(data) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const rows = 4; const cols = 12;
            const w = 35; const h = 50; const spX = 12; const spY = 55;
            const startX = (canvas.width - (cols * (w + spX))) / 2;
            const startY = 30;

            ctx.fillStyle = '#334155'; ctx.font = 'bold 12px Inter';
            ctx.fillText('COLD AISLE (STORAGE)', startX + 100, startY + h + 30);
            ctx.fillText('HOT AISLE (AI NPU CLUSTER)', startX + 100, startY + h*2 + spY + 30);

            racks = [];
            for(let r=0; r<rows; r++) {
                for(let c=0; c<cols; c++) {
                    let isAI = (r===1 || r===2);
                    // 중앙 AI 랙은 부하에 따라 열이 치솟음. 일반 랙은 22~25도 유지
                    let temp = isAI ? 25 + (data.summary.load_factor * 60) + (Math.random()*4-2) : 22 + Math.random()*3;
                    
                    let rx = startX + c * (w + spX);
                    let ry = startY + r * (h + spY);
                    
                    let color = temp < 30 ? '#38bdf8' : temp < 55 ? '#00ff41' : temp < 75 ? '#f59e0b' : '#ef4444';
                    
                    ctx.shadowColor = color; ctx.shadowBlur = temp > 70 ? 15 : 0;
                    ctx.fillStyle = color; ctx.fillRect(rx, ry, w, h);
                    ctx.shadowBlur = 0; ctx.strokeStyle = '#000'; ctx.strokeRect(rx, ry, w, h);
                    
                    racks.push({ id: `RACK-${chr(r)}-${c+1}`, x: rx, y: ry, w: w, h: h, temp: temp, type: isAI?'NPU':'Storage' });
                }
            }
        }
        function chr(r) { return String.fromCharCode(65+r); }

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            let mouseX = e.clientX - rect.left; let mouseY = e.clientY - rect.top;
            let hovered = false;
            for(let r of racks) {
                if(mouseX >= r.x && mouseX <= r.x + r.w && mouseY >= r.y && mouseY <= r.y + r.h) {
                    tooltip.style.display = 'block'; tooltip.style.left = (e.clientX + 15) + 'px'; tooltip.style.top = (e.clientY + 15) + 'px';
                    tooltip.innerHTML = `<strong style="color:var(--accent)">${r.id}</strong><br>Type: ${r.type}<br>Temp: ${r.temp.toFixed(1)}°C<br>Power: ${(r.temp*0.4).toFixed(1)}kW`;
                    hovered = true; break;
                }
            }
            if(!hovered) tooltip.style.display = 'none';
        });
        canvas.addEventListener('mouseleave', () => tooltip.style.display = 'none');

        // ---------------------------------------------------------
        // Chart & Data Sync
        // ---------------------------------------------------------
        const trendChart = new Chart(document.getElementById('trendChart').getContext('2d'), {
            type: 'line',
            data: { labels: Array(20).fill(''), datasets: [
                { label: 'Total Power', data: Array(20).fill(0), borderColor: '#00ff41', borderWidth: 2, fill: true, backgroundColor: 'rgba(0,255,65,0.1)', pointRadius: 0 },
                { label: '+45m Predict', data: Array(20).fill(0), borderColor: '#ef4444', borderDash: [5,5], borderWidth: 2, pointRadius: 0 }
            ]},
            options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display: false }, y: { grid: { color: '#222' } } }, plugins: { legend: { display: false } } }
        });

        async function fetchState() {
            try {
                const res = await fetch('/api/v1/state');
                const data = await res.json();
                
                // KPI Update
                document.getElementById('kpi-load').innerText = (data.summary.load_factor * 100).toFixed(1) + "%";
                document.getElementById('kpi-kepco').innerText = "₩" + data.summary.kepco_price.toFixed(1);
                
                let itPower = (data.summary.load_factor * 1200) + 300;
                let coolingPower = (data.summary.load_factor * 400) + 100;
                let totalPower = itPower + coolingPower;
                let pue = totalPower / itPower;
                
                document.getElementById('kpi-power').innerText = totalPower.toFixed(1);
                document.getElementById('kpi-pue').innerText = pue.toFixed(2);
                
                // VPP Revenue Logic
                let vppRev = 0;
                if(data.summary.vpp_mode.includes("SELL")) vppRev = (data.summary.kepco_price * 1500); // 1.5MW 송전 가정
                document.getElementById('kpi-vpp').innerText = vppRev > 0 ? "+₩" + Math.floor(vppRev).toLocaleString() : "0";
                
                document.getElementById('vpp-status-text').innerText = data.summary.vpp_mode;
                document.getElementById('vpp-status-text').style.color = data.summary.vpp_mode.includes("SELL") ? "var(--accent)" : data.summary.vpp_mode.includes("BUY") ? "var(--danger)" : "#888";
                
                let cb = document.getElementById('cooling-badge');
                cb.innerText = "❄️ " + data.summary.cooling_mode;
                cb.style.color = data.summary.cooling_mode.includes("PRE") ? "var(--blue)" : "#888";

                // Draw Map & Chart
                drawFloorPlan(data);
                
                trendChart.data.datasets[0].data.push(totalPower); trendChart.data.datasets[0].data.shift();
                trendChart.data.datasets[1].data.push(totalPower * (1 + (data.summary.load_factor*0.3))); trendChart.data.datasets[1].data.shift();
                trendChart.update();

                // Random security log injection
                if(Math.random() > 0.9) logTerminal("Data Diode Tx verified. Heartbeat OK.");

            } catch(e) {}
        }
        setInterval(fetchState, 1000);

        // ---------------------------------------------------------
        // LLM & Kill Switch
        // ---------------------------------------------------------
        function handleLLM(e) {
            if(e.key === 'Enter') {
                const cmd = e.target.value;
                if(cmd.includes("학습") || cmd.includes("LLM")) {
                    setWorkload(0.95, document.querySelectorAll('.btn-control')[2]);
                    e.target.value = "> K8s 스케줄러에 풀부하 학습 명령을 하달했습니다.";
                } else if(cmd.includes("대기") || cmd.includes("종료")) {
                    setWorkload(0.1, document.querySelectorAll('.btn-control')[0]);
                    e.target.value = "> 작업을 종료하고 IDLE 상태로 전환합니다.";
                } else {
                    e.target.value = "> AI 엔진: 의도를 분석하여 인프라를 최적화 중입니다...";
                }
                e.target.style.color = "var(--accent)";
                setTimeout(() => { e.target.value = ""; e.target.style.color = "var(--blue)"; }, 2500);
            }
        }

        function executeKillSwitch() {
            if(!confirm("⚠️ 치명적 경고: NPU 암호화 키를 하드웨어 레벨에서 파기합니다. 진행하시겠습니까?")) return;
            document.getElementById('lockdown-screen').classList.add('active');
            let logs = document.getElementById('wipe-logs');
            let msgs = ["[SYSTEM] BIOMETRIC AUTH ACCEPTED.", "[HARDWARE] INITIATING NIST SP 800-88 CRYPTO-SHREDDING...", "[BMC] Applying 12V Overvoltage to eFuse array...", "[STORAGE] NVMe SecureErase complete. DEK destroyed.", "[PDU] Physical power relays FORCED OPEN.", "DATA EXFILTRATION PREVENTED. SILICON DESTROYED."];
            let i = 0;
            let intv = setInterval(() => { logs.innerHTML += `> <span style="color:#00ff41">${msgs[i]}</span><br>`; i++; if(i >= msgs.length) clearInterval(intv); }, 800);
            setTimeout(() => { location.reload(); }, 6000);
        }
    </script>
</body>
</html>
"""

# =========================================================
# 플라스크 API 라우팅
# =========================================================
@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
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

@app.route('/api/v1/state', methods=['GET'])
def get_state():
    """프론트엔드에 하이퍼 리얼리티 시뮬레이션 상태를 전달"""
    update_simulation_physics() # 매 요청마다 물리 엔진 업데이트
    
    return jsonify({
        "summary": {
            "load_factor": SIM_STATE["current_workload"],
            "kepco_price": SIM_STATE["kepco_price"],
            "cooling_mode": SIM_STATE["cooling_mode"],
            "vpp_mode": SIM_STATE["vpp_mode"]
        }
    })

@app.route('/api/v1/control/workload', methods=['POST'])
def control_workload():
    """사용자가 프론트엔드에서 버튼/LLM으로 K8s 워크로드를 주입할 때 호출됨"""
    data = request.json
    if 'target_workload' in data:
        SIM_STATE["target_workload"] = float(data['target_workload'])
    return jsonify({"status": "Workload injection accepted."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)