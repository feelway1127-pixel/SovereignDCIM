from flask import Flask, jsonify, render_template_string, request
import time
import math
import random
import os

app = Flask(__name__)

# =========================================================
# 🧠 DCIM 코어 시뮬레이션 엔진
# =========================================================
SIM_STATE = {"workload": 0.1, "target_workload": 0.1, "chws_temp": 10.0}

def update_dcim_physics():
    global SIM_STATE
    diff = SIM_STATE["target_workload"] - SIM_STATE["workload"]
    SIM_STATE["workload"] += diff * 0.2

# =========================================================
# 초격차 엔터프라이즈 UI (킬스위치 UI 은닉화)
# =========================================================
ENTERPRISE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - Ultimate Sovereign DCIM</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { 
            --bg: #0f111a; --panel: #161925; --border: #2a2d3d; 
            --text-main: #e2e8f0; --text-muted: #94a3b8;
            --blue: #3b82f6; --green: #10b981; --orange: #f59e0b; --red: #ef4444; 
        }
        body { margin: 0; font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text-main); height: 100vh; display: flex; overflow: hidden; user-select: none; }
        
        /* Sidebar Navigation */
        .sidebar { width: 250px; background: #0b0d14; border-right: 1px solid var(--border); display: flex; flex-direction: column; z-index: 10; }
        .logo { padding: 20px; font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -1px; border-bottom: 1px solid var(--border); }
        .logo span { color: var(--blue); }
        .menu-group { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; padding: 20px 20px 5px 20px; }
        .nav-item { padding: 10px 20px 10px 30px; color: var(--text-muted); cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
        .nav-item:hover { background: rgba(255,255,255,0.03); color: var(--text-main); }
        .nav-item.active { background: rgba(59, 130, 246, 0.1); color: var(--blue); border-left-color: var(--blue); font-weight: 600; }
        
        /* 🚨 수정된 킬스위치 탭 (은밀하고 작게) */
        .nav-item.critical { 
            color: var(--text-muted); 
            font-size: 11px; 
            margin-top: auto; 
            border-top: 1px solid var(--border); 
            padding: 15px 20px 15px 30px; 
            opacity: 0.5; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        .nav-item.critical:hover { 
            color: var(--red); 
            opacity: 1; 
            background: transparent; 
            border-left-color: transparent; 
        }

        /* Main Workspace */
        .main-wrapper { flex: 1; display: flex; flex-direction: column; background: var(--bg); position: relative; }
        .topbar { height: 55px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: var(--panel); }
        .topbar-title { font-size: 15px; font-weight: 600; }
        
        .view-section { display: none; padding: 20px; height: calc(100vh - 55px); overflow-y: auto; box-sizing: border-box; }
        .view-section.active { display: block; animation: fadeIn 0.2s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 20px; margin-bottom: 20px; }
        .panel-title { font-size: 14px; font-weight: 600; margin: 0 0 15px 0; color: #fff; display: flex; justify-content: space-between; align-items: center; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

        .btn-group { display: flex; gap: 10px; }
        .btn { padding: 8px 15px; background: transparent; border: 1px solid var(--border); color: var(--text-muted); font-size: 12px; font-weight: 600; cursor: pointer; border-radius: 4px; transition: 0.2s; }
        .btn:hover { border-color: var(--blue); color: var(--blue); }
        .btn.active { background: rgba(59, 130, 246, 0.1); border-color: var(--blue); color: var(--blue); }

        /* Floor Plan */
        .canvas-container { width: 100%; height: 400px; background: #000; border: 1px solid var(--border); border-radius: 4px; position: relative; overflow: hidden; perspective: 1000px; }
        canvas { display: block; width: 100%; height: 100%; transition: transform 0.5s ease; }
        .canvas-3d canvas { transform: rotateX(45deg) rotateZ(-15deg) scale(0.9); box-shadow: 0 20px 50px rgba(0,0,0,0.8); }
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); border: 1px solid var(--blue); padding: 10px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 11px; display: none; z-index: 100; pointer-events: none; }

        /* Rack Elevation */
        .rack-container { display: flex; gap: 30px; justify-content: center; background: #0b0d14; padding: 20px; border: 1px solid var(--border); border-radius: 6px; }
        .rack { width: 220px; background: #1a1d2d; border: 2px solid #334155; border-radius: 4px; padding: 5px; display: flex; flex-direction: column-reverse; gap: 2px; position: relative; }
        .rack-title { text-align: center; color: #fff; font-weight: bold; margin-bottom: 10px; font-size: 13px; }
        .u-slot { height: 16px; background: #0f111a; border: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between; padding: 0 5px; font-family: 'JetBrains Mono'; font-size: 9px; color: #475569; position: relative; cursor: pointer; }
        .u-slot:hover { border-color: var(--blue); }
        .u-server { background: #3b82f6; border-color: #2563eb; color: #fff; }
        .u-network { background: #10b981; border-color: #059669; color: #fff; }
        .u-storage { background: #f59e0b; border-color: #d97706; color: #fff; }
        .u-hot { background: #ef4444; border-color: #dc2626; color: #fff; animation: pulse 1s infinite alternate; }
        @keyframes pulse { from { opacity: 0.8; } to { opacity: 1; box-shadow: 0 0 10px rgba(239,68,68,0.8); } }

        /* Topology */
        .topo-container { width: 100%; height: 400px; background: #0b0d14; border: 1px solid var(--border); border-radius: 6px; position: relative; overflow: hidden; }
        .node { position: absolute; background: var(--panel); border: 2px solid var(--border); border-radius: 6px; padding: 10px; width: 120px; text-align: center; font-size: 11px; font-weight: 600; cursor: pointer; z-index: 2; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .node:hover { border-color: var(--blue); }
        .node.core { top: 30px; left: calc(50% - 70px); border-color: var(--orange); }
        .node.spine1 { top: 150px; left: 20%; border-color: var(--green); }
        .node.spine2 { top: 150px; left: 60%; border-color: var(--green); }
        .node.leaf { top: 280px; border-color: var(--blue); }
        .topo-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
        .link { stroke: #334155; stroke-width: 2; fill: none; }
        .link.active { stroke: var(--blue); stroke-width: 3; animation: dash 1s linear infinite; stroke-dasharray: 5, 5; }
        .link.hot { stroke: var(--red); stroke-width: 3; }
        @keyframes dash { to { stroke-dashoffset: -10; } }

        /* Security Modal */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 1000; justify-content: center; align-items: center; }
        .modal-overlay.active { display: flex; }
        .modal { background: #0b0d14; border: 1px solid var(--red); width: 600px; border-radius: 6px; padding: 25px; }
        .term-log { margin-top: 20px; height: 200px; overflow-y: auto; font-family: 'JetBrains Mono'; font-size: 13px; color: var(--text-main); background: #000; padding: 15px; border: 1px solid var(--border); }
    </style>
</head>
<body>

    <div class="modal-overlay" id="zero-modal">
        <div class="modal">
            <h2 style="color: var(--red); margin-top: 0; font-family: 'Inter'; font-weight: 800; letter-spacing: -1px;">Hardware Zeroization Sequence</h2>
            <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">OOB Network executing NIST SP 800-88 purge to bare-metal hardware. All cryptographic keys will be physically destroyed.</p>
            <div class="term-log" id="wipe-logs"></div>
        </div>
    </div>

    <div class="sidebar">
        <div class="logo">dcim<span>.kr</span></div>
        
        <div class="menu-group">Dashboard</div>
        <div class="nav-item active" onclick="switchTab('floorplan', '2D/3D 현황관리 (AI 열화상)')">2D/3D 현황관리</div>
        <div class="nav-item" onclick="switchTab('elevation', '랙/실장도 관리 (U-Level)')">랙/실장도 관리</div>
        <div class="nav-item" onclick="switchTab('topology', '네트워크/포트 연결도')">네트워크(포트) 관리</div>
        
        <div class="menu-group">Assets & Maintenance</div>
        <div class="nav-item">IT자산 관리 (Inventory)</div>
        <div class="nav-item">장비 반출입 관리</div>
        <div class="nav-item">S/W 라이선스 관리</div>
        
        <div class="nav-item critical" onclick="executeCryptoErase()">
            <span style="font-size:14px;">🔒</span> 
            <span>Sovereign Protocol (Admin Only)</span>
        </div>
    </div>

    <div class="main-wrapper">
        <div class="topbar">
            <div class="topbar-title" id="topbar-title">2D/3D 현황관리 (AI 열화상)</div>
            <div style="font-size: 12px; font-family: 'JetBrains Mono'; color: var(--green); border: 1px solid var(--green); padding: 4px 8px; border-radius: 4px; background: rgba(16,185,129,0.1);">OOB NETWORK SECURE</div>
        </div>

        <div id="view-floorplan" class="view-section active">
            <div class="panel">
                <div class="panel-title">
                    <span>AI Predictive Thermal Map</span>
                    <div class="btn-group">
                        <button class="btn" id="btn-3d" onclick="toggle3D()">Toggle 3D View</button>
                    </div>
                </div>
                
                <div class="control-group" style="margin-bottom: 15px;">
                    <button class="btn active" onclick="setWorkload(0.1, this)">IDLE (일반 운영)</button>
                    <button class="btn" onclick="setWorkload(0.9, this)">LLM TRAINING (초고밀도 학습)</button>
                </div>
                
                <div class="canvas-container" id="canvas-wrapper">
                    <canvas id="floorCanvas"></canvas>
                    <div id="tooltip"></div>
                </div>
            </div>

            <div class="grid-2">
                <div class="panel">
                    <div class="panel-title">Power Trend (IT vs Cooling)</div>
                    <div style="height: 180px;"><canvas id="trendChart"></canvas></div>
                </div>
                <div class="panel">
                    <div class="panel-title">Facility Core Metrics</div>
                    <div style="display:flex; flex-direction:column; gap:15px; font-size:13px;">
                        <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:8px;">
                            <span style="color:var(--text-muted)">Total IT Power</span>
                            <strong id="val-power" style="font-family:'JetBrains Mono'; font-size:16px;">0.0 kW</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:8px;">
                            <span style="color:var(--text-muted)">Real-time PUE</span>
                            <strong id="val-pue" style="font-family:'JetBrains Mono'; font-size:16px; color:var(--blue);">1.00</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:8px;">
                            <span style="color:var(--text-muted)">AI Pre-Cooling Status</span>
                            <strong id="val-cool" style="color:var(--text-muted);">AUTO: 22°C</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="view-elevation" class="view-section">
            <div class="panel">
                <div class="panel-title">U-Level Rack Elevation (열화상 융합 실장도)</div>
                <p style="font-size:12px; color:var(--text-muted); margin-top:-5px; margin-bottom:20px;">각 U(유닛)별 장착 상태와 실시간 AI 부하/발열 상태를 연동하여 보여줍니다.</p>
                
                <div class="rack-container" id="rack-container"></div>
                
                <div style="display:flex; gap:20px; justify-content:center; margin-top:20px; font-size:11px; font-family:'JetBrains Mono'; color:var(--text-muted);">
                    <span style="display:flex; align-items:center; gap:5px;"><div style="width:12px; height:12px; background:var(--blue);"></div> Compute Node</span>
                    <span style="display:flex; align-items:center; gap:5px;"><div style="width:12px; height:12px; background:var(--green);"></div> Network Switch</span>
                    <span style="display:flex; align-items:center; gap:5px;"><div style="width:12px; height:12px; background:var(--orange);"></div> Storage Array</span>
                    <span style="display:flex; align-items:center; gap:5px;"><div style="width:12px; height:12px; background:var(--red);"></div> Thermal Warning</span>
                </div>
            </div>
        </div>

        <div id="view-topology" class="view-section">
            <div class="panel">
                <div class="panel-title">Dynamic Network Topology (트래픽/발열 연동 포트 맵)</div>
                <p style="font-size:12px; color:var(--text-muted); margin-top:-5px; margin-bottom:20px;">AI 학습 시 스위치 간 발생하는 병목과 포트 발열을 실시간 토폴로지로 시각화합니다.</p>
                
                <div class="topo-container">
                    <svg class="topo-svg" id="topo-svg"></svg>
                    <div class="node core">CORE-RTR-01<br><span style="font-weight:normal; color:var(--text-muted);">100G / OK</span></div>
                    <div class="node spine1">SPINE-SW-01<br><span style="font-weight:normal; color:var(--text-muted);">40G / Active</span></div>
                    <div class="node spine2">SPINE-SW-02<br><span style="font-weight:normal; color:var(--text-muted);">40G / Active</span></div>
                    <div class="node leaf" style="left: 10%;">LEAF-A01 (Storage)<br><span style="font-weight:normal; color:var(--text-muted);">Eth1/1</span></div>
                    <div class="node leaf" style="left: 35%;" id="leaf-ai1">LEAF-B01 (AI NPU)<br><span style="font-weight:normal; color:var(--text-muted);">Eth1/2</span></div>
                    <div class="node leaf" style="left: 60%;" id="leaf-ai2">LEAF-C01 (AI NPU)<br><span style="font-weight:normal; color:var(--text-muted);">Eth1/3</span></div>
                    <div class="node leaf" style="left: 85%;">LEAF-D01 (Web)<br><span style="font-weight:normal; color:var(--text-muted);">Eth1/4</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.onkeydown = function(e) { if(e.keyCode==123 || (e.ctrlKey&&e.shiftKey&&(e.keyCode==73||e.keyCode==67||e.keyCode==74)) || (e.ctrlKey&&e.keyCode==85)) return false; };

        function switchTab(tabId, title) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById('topbar-title').innerText = title;
            
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            document.getElementById('view-' + tabId).classList.add('active');
            
            if(tabId === 'floorplan') resizeCanvas();
        }

        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const wrapper = document.getElementById('canvas-wrapper');
        let is3D = false;

        function resizeCanvas() { if(canvas.parentElement) { canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; } }
        window.addEventListener('resize', resizeCanvas); resizeCanvas();

        function toggle3D() {
            is3D = !is3D;
            wrapper.classList.toggle('canvas-3d', is3D);
            document.getElementById('btn-3d').classList.toggle('active', is3D);
        }

        let racks = [];
        function drawFloorPlan(load) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 1;
            for(let i=0; i<canvas.width; i+=30) { ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }
            for(let i=0; i<canvas.height; i+=30) { ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(canvas.width,i); ctx.stroke(); }

            const rows = 3; const cols = 12;
            const w = Math.min(35, (canvas.width - 150) / cols); 
            const h = 55; const spX = 10; const spY = 50;
            const startX = (canvas.width - (cols * (w + spX))) / 2;
            const startY = 40;

            racks = [];
            for(let r=0; r<rows; r++) {
                ctx.fillStyle = '#64748b'; ctx.font = '600 12px Inter';
                if(r===0) ctx.fillText('ZONE A: STORAGE', startX - 20, startY - 15);
                if(r===1) ctx.fillText('ZONE B: HIGH-DENSITY NPU', startX - 20, startY + h + spY - 15);

                for(let c=0; c<cols; c++) {
                    let isAI = (r===1 || r===2);
                    let temp = isAI ? 22 + (load * 60) + (Math.random()*4-2) : 21 + Math.random()*2;
                    let rx = startX + c * (w + spX); let ry = startY + r * (h + spY);
                    
                    let color = temp < 28 ? '#3b82f6' : temp < 50 ? '#10b981' : temp < 70 ? '#f59e0b' : '#ef4444';
                    
                    ctx.shadowColor = color; ctx.shadowBlur = temp > 65 ? 15 : 0;
                    ctx.fillStyle = color; ctx.fillRect(rx, ry, w, h);
                    
                    ctx.shadowBlur = 0; ctx.fillStyle = 'rgba(0,0,0,0.5)';
                    for(let u=5; u<h; u+=8) ctx.fillRect(rx+2, ry+u, w-4, 4);
                    
                    ctx.strokeStyle = '#0f111a'; ctx.lineWidth = 2; ctx.strokeRect(rx, ry, w, h);
                    racks.push({ id: `R-${r}-${c}`, x: rx, y: ry, w: w, h: h, temp: temp });
                }
            }
        }

        function initRackElevation() {
            const container = document.getElementById('rack-container');
            container.innerHTML = '';
            const rackNames = ['RACK A-01 (Storage)', 'RACK B-01 (NPU-Master)', 'RACK B-02 (NPU-Worker)'];
            
            rackNames.forEach((name, idx) => {
                let rackHtml = `<div class="rack"><div class="rack-title">${name}</div>`;
                for(let u=1; u<=42; u++) {
                    let typeClass = ''; let label = '';
                    if(idx === 0 && u > 10 && u < 30) { typeClass = 'u-storage'; label = `SAN-DS-${u}`; }
                    else if(idx > 0 && u > 5 && u < 38) { typeClass = 'u-server'; label = `NPU-NODE-${u}`; }
                    else if(u === 40 || u === 41) { typeClass = 'u-network'; label = `TOR-SW-${u}`; }
                    
                    rackHtml += `<div class="u-slot ${typeClass}" id="u-${idx}-${u}"><span>${u}U</span> <span>${label}</span></div>`;
                }
                rackHtml += `</div>`;
                container.innerHTML += rackHtml;
            });
        }
        initRackElevation();

        function updateElevation(load) {
            for(let u=6; u<38; u++) {
                let el1 = document.getElementById(`u-1-${u}`);
                let el2 = document.getElementById(`u-2-${u}`);
                if(el1 && el2) {
                    if(load > 0.8 && Math.random() > 0.7) {
                        el1.classList.add('u-hot'); el2.classList.add('u-hot');
                    } else {
                        el1.classList.remove('u-hot'); el2.classList.remove('u-hot');
                    }
                }
            }
        }

        function drawTopology(load) {
            const svg = document.getElementById('topo-svg');
            const links = [
                {x1:50, y1:15, x2:25, y2:40}, {x1:50, y1:15, x2:65, y2:40},
                {x1:25, y1:40, x2:15, y2:75}, {x1:25, y1:40, x2:40, y2:75},
                {x1:65, y1:40, x2:65, y2:75}, {x1:65, y1:40, x2:90, y2:75}
            ];
            
            let svgHtml = '';
            links.forEach((l, i) => {
                let linkClass = 'link';
                if ((i === 3 || i === 4) && load > 0.2) linkClass = 'link active';
                if ((i === 3 || i === 4) && load > 0.8) linkClass = 'link hot';
                svgHtml += `<path d="M${l.x1}% ${l.y1}% C${l.x1}% ${l.y1+10}%, ${l.x2}% ${l.y2-10}%, ${l.x2}% ${l.y2}%" class="${linkClass}" />`;
            });
            svg.innerHTML = svgHtml;
            
            let ai1 = document.getElementById('leaf-ai1');
            let ai2 = document.getElementById('leaf-ai2');
            if(load > 0.8) { ai1.style.borderColor = 'var(--red)'; ai2.style.borderColor = 'var(--red)'; }
            else { ai1.style.borderColor = 'var(--blue)'; ai2.style.borderColor = 'var(--blue)'; }
        }

        const trendChart = new Chart(document.getElementById('trendChart').getContext('2d'), {
            type: 'line',
            data: { labels: Array(20).fill(''), datasets: [
                { label: 'IT Power', data: Array(20).fill(0), borderColor: '#3b82f6', borderWidth: 2, pointRadius: 0, tension: 0.3 },
                { label: 'Cooling Power', data: Array(20).fill(0), borderColor: '#10b981', borderWidth: 2, pointRadius: 0, tension: 0.3 }
            ]},
            options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display: false }, y: { grid: { color: '#2a2d3d' } } }, plugins: { legend: { display: false } } }
        });

        function setWorkload(load, btnElement) {
            document.querySelectorAll('.control-group .btn').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');
            fetch('/api/v1/control/workload', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ target_workload: load }) });
        }

        async function fetchState() {
            try {
                const res = await fetch('/api/v1/state');
                const data = await res.json();
                const load = data.workload;
                
                let itPower = (load * 3000) + 500;
                let coolingPower = (load * 1000) + 200;
                let pue = (itPower + coolingPower) / itPower;

                document.getElementById('val-power').innerText = itPower.toFixed(1) + " kW";
                document.getElementById('val-pue').innerText = pue.toFixed(2);
                
                let cStatus = document.getElementById('val-cool');
                if(load > 0.8) { cStatus.innerText = "PRE-COOLING: 18°C"; cStatus.style.color = "var(--blue)"; }
                else { cStatus.innerText = "AUTO: 22°C"; cStatus.style.color = "var(--text-muted)"; }

                drawFloorPlan(load);
                updateElevation(load);
                drawTopology(load);
                
                trendChart.data.datasets[0].data.push(itPower); trendChart.data.datasets[0].data.shift();
                trendChart.data.datasets[1].data.push(coolingPower); trendChart.data.datasets[1].data.shift();
                trendChart.update();
            } catch(e) {}
        }
        setInterval(fetchState, 1000);

        function executeCryptoErase() {
            if(!confirm("⚠️ 보안 확인: 하드웨어 암호화 키 파기 프로토콜을 가동합니까?")) return;
            document.getElementById('zero-modal').classList.add('active');
            let logs = document.getElementById('wipe-logs');
            logs.innerHTML = "";
            let msgs = [
                "[AUTH] Biometric signature confirmed. Clearance: Admin.",
                "[OOB] Accessing BMC via out-of-band management network...",
                "[PWR] Applying 12V direct current to TPM/eFuse enclaves.",
                "[MEM] Executing NIST SP 800-88 Purge on NVMe SED drives...",
                "[SYS] Disconnecting all physical network interfaces...",
                "--------------------------------------------------",
                "[SUCCESS] SILICON DESTROYED. DATA UNRECOVERABLE."
            ];
            let i = 0;
            let intv = setInterval(() => { 
                logs.innerHTML += `<div><span style="color:var(--text-muted)">[${new Date().toISOString().split('T')[1].slice(0,-1)}]</span> <span style="color:#fff">${msgs[i]}</span></div>`; 
                logs.scrollTop = logs.scrollHeight;
                i++; 
                if(i >= msgs.length) { clearInterval(intv); setTimeout(() => { location.reload(); }, 4000); }
            }, 700);
            fetch('/api/v1/control/purge', { method: 'POST' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(ENTERPRISE_HTML)

@app.route('/api/v1/state', methods=['GET'])
def get_state():
    update_dcim_physics()
    return jsonify({"workload": SIM_STATE["workload"]})

@app.route('/api/v1/control/workload', methods=['POST'])
def control_workload():
    data = request.json
    if 'target_workload' in data:
        SIM_STATE["target_workload"] = float(data['target_workload'])
    return jsonify({"status": "Accepted"})

@app.route('/api/v1/control/purge', methods=['POST'])
def purge_node():
    return jsonify({"status": "Zeroized"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)