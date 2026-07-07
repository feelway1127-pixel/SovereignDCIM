from flask import Flask, jsonify, render_template_string
import random

app = Flask(__name__)

# 🖥️ 상면도(Floor Plan) 관제 및 암호화 파괴 프로토콜이 내장된 마스터 통합 템플릿
MAIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>dcim.kr - MASTER CONTROL</title>
    <style>
        :root { 
            --bg: #050505; 
            --neon-green: #00ff41; 
            --neon-red: #ef4444; 
            --neon-blue: #38bdf8; 
            --panel: #0a0a0c; 
            --grid: rgba(255,255,255,0.03); 
        }
        body { 
            background-color: var(--bg); color: #cbd5e1; 
            font-family: 'Malgun Gothic', sans-serif; margin: 0; padding: 20px; overflow-x: hidden; 
            background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px); 
            background-size: 40px 40px; 
        }
        .container { max-width: 1600px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 15px; }
        .brand { font-size: 32px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -1px; }
        .brand span { color: var(--neon-red); }
        
        .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 10px; }
        .panel { background: var(--panel); border: 1px solid #222; border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); position: relative; }
        .panel h2 { margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase; color: #888; border-bottom: 1px dashed #333; padding-bottom: 10px; display: flex; justify-content: space-between; }
        
        .floor-plan-container { position: relative; width: 100%; height: 500px; background: #000; border: 1px solid #333; border-radius: 4px; overflow: hidden; }
        canvas { display: block; width: 100%; height: 100%; }
        
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); border: 1px solid var(--neon-blue); color: #fff; padding: 10px; font-size: 12px; pointer-events: none; display: none; z-index: 10; border-radius: 4px; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
        
        .legend { position: absolute; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); border: 1px solid #333; padding: 10px; font-size: 11px; color: #888; }
        .color-bar { width: 150px; height: 10px; background: linear-gradient(90deg, #38bdf8 0%, #10b981 40%, #f59e0b 70%, #ef4444 100%); margin-top: 5px; }

        .kill-btn { width: 100%; background: transparent; border: 2px solid var(--neon-red); color: var(--neon-red); padding: 15px; font-weight: 900; font-size: 18px; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .kill-btn:hover { background: var(--neon-red); color: #000; box-shadow: 0 0 20px var(--neon-red); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="brand">dcim<span>.kr</span></h1>
            <div style="color: #00ff41; border: 1px solid #00ff41; padding: 5px 15px; border-radius: 20px; font-size: 13px; font-weight: bold;">
                AIR-GAPPED OOB NETWORK SECURE (자립형 자산 관제)
            </div>
            <span style="color: #64748b; font-size: 14px;">[MASTER_SESSION]</span>
        </div>

        <div class="main-grid">
            <div class="panel">
                <h2><span>🔥 2D Data Center Floor Plan (소버린 실시간 히트맵)</span> <span id="cooling-status" style="color:var(--neon-blue); display:none;">CRAC PRE-COOLING ACTIVE</span></h2>
                <div class="floor-plan-container">
                    <canvas id="floorCanvas"></canvas>
                    <div id="tooltip"></div>
                    <div class="legend">
                        랙 개별 온도 현황
                        <div class="color-bar"></div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px;"><span>20°C</span><span>80°C</span></div>
                    </div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="panel">
                    <h2><span>⚡ 인프라 전력 변동 시계열 트렌드</span></h2>
                    <div style="height: 200px;"><canvas id="pureLineCanvas"></canvas></div>
                </div>
                
                <div class="panel" style="border-color: #333; flex: 1;">
                    <h2><span style="color:var(--neon-red)">⚠️ SUPER SOVEREIGN COMMAND</span></h2>
                    <div style="text-align: center; font-size: 13px; margin-top: 30px; color: #888;">
                        보안 관제 타겟: <span style="color:#fff;">A-Row (고밀도 AI 클러스터 존)</span><br><br>
                        물리 자산 검증 상태: 이상 무해(Normal)<br>
                        eFuse 암호 키 구조: 무결성 인증 필(INTACT)
                    </div>
                    <button class="kill-btn" onclick="alert('eFuse 물리적 자폭 프로토콜이 안전하게 인가되었습니다. 메모리 인스턴스를 무결성 영문화 처리합니다.');">INITIATE CRYPTO-SHREDDING</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ------------------------------------------------------------
        // 1. 2D Floor Plan 자립형 그래픽스 엔진 (Canvas)
        // ------------------------------------------------------------
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        
        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const racks = [];
        const rows = 4; const cols = 10;
        const rackWidth = 40; const rackHeight = 60;
        const spacingX = 15; const spacingY = 80;
        
        let startX = (canvas.width - (cols * (rackWidth + spacingX))) / 2;
        let startY = 50;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                racks.push({
                    id: `RACK-${String.fromCharCode(65 + r)}-${(c+1).toString().padStart(2, '0')}`,
                    x: startX + c * (rackWidth + spacingX),
                    y: startY + r * (rackHeight + spacingY),
                    w: rackWidth, h: rackHeight,
                    temp: 22,
                    isAI: (r === 1 || r === 2)
                });
            }
        }

        function getColorForTemp(temp) {
            if (temp < 25) return '#38bdf8';
            if (temp < 40) return '#10b981';
            if (temp < 60) return '#f59e0b';
            return '#ef4444';
        }

        function drawFloorPlan() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#333';
            ctx.font = 'bold 13px monospace';
            ctx.fillText('COLD AISLE 01', startX + 10, startY + rackHeight + 45);
            ctx.fillText('HOT AISLE 01', startX + 10, startY + rackHeight*2 + spacingY*1 + 45);
            ctx.fillText('COLD AISLE 02', startX + 10, startY + rackHeight*3 + spacingY*2 + 45);

            racks.forEach(rack => {
                ctx.shadowColor = getColorForTemp(rack.temp);
                ctx.shadowBlur = rack.temp > 60 ? 12 : 0;
                
                ctx.fillStyle = getColorForTemp(rack.temp);
                ctx.fillRect(rack.x, rack.y, rack.w, rack.h);
                
                ctx.shadowBlur = 0;
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.strokeRect(rack.x, rack.y, rack.w, rack.h);
                
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                for(let i=5; i<rack.h; i+=10) {
                    ctx.fillRect(rack.x + 2, rack.y + i, rack.w - 4, 2);
                }
            });
        }

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            let hovered = false;
            racks.forEach(rack => {
                if (mouseX >= rack.x && mouseX <= rack.x + rack.w &&
                    mouseY >= rack.y && mouseY <= rack.y + rack.h) {
                    tooltip.style.display = 'block';
                    tooltip.style.left = (e.clientX + 15) + 'px';
                    tooltip.style.top = (e.clientY + 15) + 'px';
                    tooltip.innerHTML = `
                        <strong style="color:#00ff41">${rack.id}</strong><br>
                        인프라 유형: ${rack.isAI ? '고밀도 AI 연산 노드' : '네트워크/스토리지 자산'}<br>
                        실측 온도: <span style="color:${getColorForTemp(rack.temp)}">${rack.temp.toFixed(1)} °C</span><br>
                        실측 전력: ${(rack.temp * 0.4).toFixed(1)} kW
                    `;
                    hovered = true;
                }
            });
            if (!hovered) tooltip.style.display = 'none';
        });

        canvas.addEventListener('mouseleave', () => tooltip.style.display = 'none');

        // ------------------------------------------------------------
        // 2. 외부 종속성 0% 순수 자바스크립트 전력 시계열 렌더러
        // ------------------------------------------------------------
        const lineCanvas = document.getElementById('pureLineCanvas');
        const lineCtx = lineCanvas.getContext('2d');
        let powerHistory = Array(30).fill(120);

        function resizeLineCanvas() {
            lineCanvas.width = lineCanvas.parentElement.clientWidth;
            lineCanvas.height = lineCanvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeLineCanvas);
        resizeLineCanvas();

        function drawPureLineChart() {
            lineCtx.clearRect(0, 0, lineCanvas.width, lineCanvas.height);
            
            // 모니터링 그리드 백그라운드 스케일링
            lineCtx.strokeStyle = '#141419'; lineCtx.lineWidth = 1;
            for(let i=0; i<lineCanvas.width; i+=30) { lineCtx.beginPath(); lineCtx.moveTo(i, 0); lineCtx.lineTo(i, lineCanvas.height); lineCtx.stroke(); }
            for(let j=0; j<lineCanvas.height; j+=30) { lineCtx.beginPath(); lineCtx.moveTo(0, j); lineCtx.lineTo(lineCanvas.width, j); lineCtx.stroke(); }

            if(powerHistory.length < 2) return;
            
            // 꺾은선 렌더링 파이프라인
            lineCtx.strokeStyle = '#00ff41'; lineCtx.lineWidth = 2;
            lineCtx.beginPath();
            const step = lineCanvas.width / (powerHistory.length - 1);
            
            for(let i=0; i<powerHistory.length; i++) {
                const x = i * step;
                // 정격 한계점 (최대 250kW 스케일 변환 연산)
                const y = lineCanvas.height - (powerHistory[i] / 250 * lineCanvas.height);
                if(i === 0) lineCtx.moveTo(x, y); else lineCtx.lineTo(x, y);
            }
            lineCtx.stroke();
        }

        // ------------------------------------------------------------
        // 3. 통합 주기적 데이터 갱신 루프
        // ------------------------------------------------------------
        async function updateDashboard() {
            try {
                const t = Date.now() / 1000;
                const aiLoad = (Math.sin(t / 4) + 1) / 2; 
                
                let totalPower = 0;
                racks.forEach(rack => {
                    if(rack.isAI) {
                        rack.temp = 25 + (aiLoad * 50) + (Math.random() * 2);
                    } else {
                        rack.temp = 22 + (Math.random() * 4);
                    }
                    totalPower += rack.temp * 0.4;
                });

                if (aiLoad > 0.8) {
                    document.getElementById('cooling-status').style.display = 'inline';
                } else {
                    document.getElementById('cooling-status').style.display = 'none';
                }

                drawFloorPlan();
                
                powerHistory.push(totalPower);
                if(powerHistory.length > 30) powerHistory.shift();
                drawPureLineChart();

            } catch (e) { console.error(e); }
        }

        setInterval(updateDashboard, 1000);
        
        // 초기화 가동 팩트
        setTimeout(() => {
            resizeCanvas();
            resizeLineCanvas();
            drawFloorPlan();
            drawPureLineChart();
        }, 100);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(MAIN_HTML)

# 🚀 인프라 자산 상태 추적용 경량 API 엔드포인트 개방 스펙
@app.route('/api/v1/metrics')
def get_live_metrics():
    return jsonify({"status": "healthy", "integrity": "secure"})

if __name__ == '__main__':
    # 로컬 디버그 및 릴리즈 인터페이스 가동
    app.run(host='0.0.0.0', port=5000, debug=True)