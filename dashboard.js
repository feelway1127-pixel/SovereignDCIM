// --- Chart.js 초기화 ---
Chart.defaults.color = '#64748b';
Chart.defaults.font.family = 'Inter';
const ctxChart = document.getElementById('trendChart').getContext('2d');
const trendChart = new Chart(ctxChart, {
    type: 'line',
    data: { 
        labels: Array(20).fill(''), 
        datasets: [
            { label: 'IT Power', data: Array(20).fill(0), borderColor: '#3b82f6', borderWidth: 2, pointRadius: 0, tension: 0.2 },
            { label: 'Cooling Power', data: Array(20).fill(0), borderColor: '#10b981', borderWidth: 2, pointRadius: 0, tension: 0.2 }
        ]
    },
    options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display: false }, y: { grid: { color: '#1e293b' } } }, plugins: { legend: { display: false } } }
});

// --- 2D Canvas 초기화 ---
const canvas = document.getElementById('floorCanvas');
const ctx = canvas.getContext('2d');
function resizeCanvas() { 
    if(canvas.parentElement) { 
        canvas.width = canvas.parentElement.clientWidth; 
        canvas.height = canvas.parentElement.clientHeight; 
    } 
}
window.addEventListener('resize', resizeCanvas); 
resizeCanvas();

function drawFloorPlan(load) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const rows = 3; const cols = 10;
    const w = Math.min(40, (canvas.width - 100) / cols); 
    const h = 60; const spX = 10; const spY = 50;
    const startX = (canvas.width - (cols * (w + spX))) / 2;
    const startY = 30;

    for(let r=0; r<rows; r++) {
        ctx.fillStyle = '#475569'; ctx.font = '600 11px Inter';
        if(r===0) ctx.fillText('ZONE A: STORAGE', startX - 10, startY - 10);
        if(r===1) ctx.fillText('ZONE B: HIGH-DENSITY NPU', startX - 10, startY + h + spY - 10);

        for(let c=0; c<cols; c++) {
            let isAI = (r===1 || r===2);
            let temp = isAI ? 22 + (load * 60) + (Math.random()*4-2) : 21 + Math.random()*2;
            let rx = startX + c * (w + spX); let ry = startY + r * (h + spY);
            
            let color = temp < 28 ? '#3b82f6' : temp < 50 ? '#10b981' : temp < 70 ? '#f59e0b' : '#ef4444';
            ctx.fillStyle = color; ctx.fillRect(rx, ry, w, h);
            ctx.strokeStyle = '#0f111a'; ctx.lineWidth = 2; ctx.strokeRect(rx, ry, w, h);
        }
    }
}

// --- API 통신 및 데이터 갱신 ---
function setWorkload(load) {
    document.querySelectorAll('.card-header .btn').forEach(b => b.classList.remove('active'));
    event.currentTarget.classList.add('active');
    fetch('/api/v1/control/workload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ target_workload: load })
    });
}

async function fetchState() {
    try {
        const res = await fetch('/api/v1/state');
        const data = await res.json();
        
        // 1. 기본 메트릭 업데이트
        document.getElementById('val-power').innerHTML = `${data.it_power_kw} <span style="font-size:14px; color:var(--text-muted);">kW</span>`;
        document.getElementById('val-cooling').innerHTML = `${data.cooling_power_kw} <span style="font-size:14px; color:var(--text-muted);">kW</span>`;
        document.getElementById('val-pue').innerText = data.pue;

        // 2. AI 인사이트 (ai_engine.py 결과) 매핑
        const ai = data.ai_insights;
        if(ai) {
            // 전력 예측 및 Z-Score (이상 탐지)
            const powerBadge = document.getElementById('ai-power-badge');
            powerBadge.innerText = `+30s: ${ai.it_power_forecast_30s || '--'} kW`;
            if(ai.it_power_anomaly.is_anomaly) {
                powerBadge.classList.add('anomaly');
                powerBadge.innerText = `! SPIKE DETECTED (Z:${ai.it_power_anomaly.z_score})`;
            } else {
                powerBadge.classList.remove('anomaly');
            }
            // PUE 트렌드
            document.getElementById('ai-pue-badge').innerText = `Trend: ${ai.pue_trend.toUpperCase()}`;
        }

        // 3. 차트 및 상면도 업데이트
        trendChart.data.datasets[0].data.push(data.it_power_kw); trendChart.data.datasets[0].data.shift();
        trendChart.data.datasets[1].data.push(data.cooling_power_kw); trendChart.data.datasets[1].data.shift();
        trendChart.update();
        drawFloorPlan(data.workload);

    } catch (err) { console.error("상태 로드 실패", err); }
}

async function fetchAuditLog() {
    try {
        const res = await fetch('/api/v1/audit');
        if(!res.ok) return; // 운영자(Operator)는 권한이 없을 수 있으므로 무시
        const data = await res.json();
        const container = document.getElementById('audit-container');
        container.innerHTML = data.entries.map(e => `
            <div class="audit-entry">
                <span style="color:#3b82f6">[${e.timestamp.split('T')[1].slice(0,-1)}]</span> 
                <span style="color:#10b981">${e.user}</span>: 
                <span style="color:#e2e8f0">${e.action}</span> 
                <span style="color:#94a3b8">${e.detail}</span>
            </div>
        `).join('');
    } catch(err) {}
}

// 초기화 및 주기적 갱신
setInterval(fetchState, 1000);
setInterval(fetchAuditLog, 2000);
fetchAuditLog();

// --- 보안 제어 (Re-auth & Zeroization) ---
async function executePurge() {
    const pw = document.getElementById('reauth-pw').value;
    const res = await fetch('/api/v1/control/purge', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ password: pw, target: 'ALL_NPU_NODES' })
    });
    
    if(res.ok) {
        document.getElementById('reauth-modal').classList.remove('active');
        alert("성공: 하드웨어 암호학적 파기 명령이 전송되었습니다. (시뮬레이션)");
        fetchAuditLog();
    } else {
        document.getElementById('reauth-error').style.display = 'block';
    }
}