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
        
        .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 10px; }
        .panel { background: var(--panel); border: 1px solid #222; border-radius: 8px; padding: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); position: relative; }
        .panel h2 { margin: 0 0 15px 0; font-size: 14px; text-transform: uppercase; color: #888; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between; border-bottom: 1px dashed #333; padding-bottom: 10px; }
        
        /* 2D 캔버스 뷰포트 */
        .floor-plan-container { position: relative; width: 100%; height: 500px; background: #000; border: 1px solid #333; border-radius: 4px; overflow: hidden; }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* 툴팁 */
        #tooltip { position: absolute; background: rgba(0,0,0,0.9); border: 1px solid var(--neon-blue); color: #fff; padding: 10px; font-family: 'JetBrains Mono'; font-size: 12px; pointer-events: none; display: none; z-index: 10; border-radius: 4px; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
        
        /* 범례 (Legend) */
        .legend { position: absolute; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); border: 1px solid #333; padding: 10px; font-family: 'JetBrains Mono'; font-size: 11px; color: #888; }
        .color-bar { width: 150px; height: 10px; background: linear-gradient(90deg, #38bdf8 0%, #10b981 40%, #f59e0b 70%, #ef4444 100%); margin-top: 5px; }

        .kill-btn { width: 100%; background: transparent; border: 2px solid var(--neon-red); color: var(--neon-red); padding: 15px; font-weight: 900; font-size: 18px; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .kill-btn:hover { background: var(--neon-red); color: #000; box-shadow: 0 0 20px var(--neon-red); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="brand">dcim<span>.kr</span></h1>
            <div style="font-family: 'JetBrains Mono'; color: #00ff41; border: 1px solid #00ff41; padding: 5px 15px; border-radius: 20px;">
                AIR-GAPPED OOB NETWORK SECURE
            </div>
            <a href="/logout" style="color: #64748b; text-decoration: none; font-size: 14px; font-family: 'JetBrains Mono';">[LOGOUT]</a>
        </div>

        <div class="main-grid">
            <div class="panel">
                <h2><span>🔥 2D Data Center Floor Plan (Live Heatmap)</span> <span id="cooling-status" style="color:var(--neon-blue); display:none;">CRAC PRE-COOLING ACTIVE</span></h2>
                <div class="floor-plan-container">
                    <canvas id="floorCanvas"></canvas>
                    <div id="tooltip"></div>
                    <div class="legend">
                        Temperature Map
                        <div class="color-bar"></div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px;"><span>20°C</span><span>80°C</span></div>
                    </div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="panel">
                    <h2><span>⚡ AI Workload Power Prediction</span></h2>
                    <div style="height: 200px;"><canvas id="thermalChart"></canvas></div>
                </div>
                
                <div class="panel" style="border-color: #333; flex: 1;">
                    <h2><span style="color:var(--neon-red)">⚠️ SUPER SOVEREIGN COMMAND</span></h2>
                    <div style="text-align: center; font-family: 'JetBrains Mono'; font-size: 12px; margin-top: 30px; color: #888;">
                        Target Rack: <span style="color:#fff;">A-Row (AI Cluster)</span><br><br>
                        SDR Sensor: No Threats Detected<br>
                        eFuse Crypto Keys: INTACT
                    </div>
                    <button class="kill-btn" onclick="alert('eFuse 물리적 자폭 프로토콜이 가동됩니다.');">INITIATE CRYPTO-SHREDDING</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ------------------------------------------------------------
        // 1. 2D Floor Plan 렌더링 엔진 (Vanilla JS + HTML5 Canvas)
        // ------------------------------------------------------------
        const canvas = document.getElementById('floorCanvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        
        // 캔버스 사이즈 조정
        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // 랙(Rack) 데이터 구조 생성 (4열, 각 10개 랙)
        const racks = [];
        const rows = 4;
        const cols = 10;
        const rackWidth = 40;
        const rackHeight = 60;
        const spacingX = 15;
        const spacingY = 80; // Cold Aisle 통로
        
        let startX = (canvas.width - (cols * (rackWidth + spacingX))) / 2;
        let startY = 50;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                racks.push({
                    id: `RACK-${String.fromCharCode(65 + r)}-${(c+1).toString().padStart(2, '0')}`,
                    x: startX + c * (rackWidth + spacingX),
                    y: startY + r * (rackHeight + spacingY),
                    w: rackWidth,
                    h: rackHeight,
                    temp: 22, // 기본 온도
                    isAI: (r === 1 || r === 2) // 중앙 2개 열은 AI 클러스터(고밀도)로 가정
                });
            }
        }

        // 온도에 따른 색상 계산 함수 (파랑 -> 초록 -> 노랑 -> 빨강)
        function getColorForTemp(temp) {
            if (temp < 25) return '#38bdf8'; // Blue
            if (temp < 40) return '#10b981'; // Green
            if (temp < 60) return '#f59e0b'; // Yellow/Orange
            return '#ef4444'; // Red (Critical)
        }

        // 화면 그리기 루프
        function drawFloorPlan() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 통로(Aisle) 텍스트 그리기
            ctx.fillStyle = '#333';
            ctx.font = 'bold 16px JetBrains Mono';
            ctx.fillText('COLD AISLE 01', startX + 150, startY + rackHeight + 45);
            ctx.fillText('HOT AISLE 01', startX + 150, startY + rackHeight*2 + spacingY*1 + 45);
            ctx.fillText('COLD AISLE 02', startX + 150, startY + rackHeight*3 + spacingY*2 + 45);

            // 랙 그리기
            racks.forEach(rack => {
                // 그림자 효과
                ctx.shadowColor = getColorForTemp(rack.temp);
                ctx.shadowBlur = rack.temp > 60 ? 15 : 0;
                
                ctx.fillStyle = getColorForTemp(rack.temp);
                ctx.fillRect(rack.x, rack.y, rack.w, rack.h);
                
                // 테두리 및 디테일
                ctx.shadowBlur = 0;
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.strokeRect(rack.x, rack.y, rack.w, rack.h);
                
                // 랙 내부 줄무늬 (서버 장착 모양)
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                for(let i=5; i<rack.h; i+=10) {
                    ctx.fillRect(rack.x + 2, rack.y + i, rack.w - 4, 2);
                }
            });
        }

        // 마우스 호버 처리 (툴팁)
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
                        Type: ${rack.isAI ? 'NPU High-Density' : 'Storage/Network'}<br>
                        Temp: <span style="color:${getColorForTemp(rack.temp)}">${rack.temp.toFixed(1)} °C</span><br>
                        Power: ${(rack.temp * 0.4).toFixed(1)} kW
                    `;
                    hovered = true;
                }
            });
            if (!hovered) tooltip.style.display = 'none';
        });

        canvas.addEventListener('mouseleave', () => tooltip.style.display = 'none');


        // ------------------------------------------------------------
        // 2. 동적 데이터 시뮬레이션 및 차트 
        // ------------------------------------------------------------
        const chartCtx = document.getElementById('thermalChart').getContext('2d');
        const thermalChart = new Chart(chartCtx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{ label: 'Total Power (kW)', data: Array(20).fill(100), borderColor: '#00ff41', backgroundColor: 'rgba(0, 255, 65, 0.1)', borderWidth: 2, fill: true, pointRadius: 0 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, animation: false,
                scales: { y: { min: 80, max: 250, grid: { color: '#222' } }, x: { grid: { display: false } } },
                plugins: { legend: { display: false } }
            }
        });

        // 1초마다 백엔드(app.py)에서 데이터를 받아와서 상면도와 차트를 업데이트
        async function updateDashboard() {
            try {
                // (실제 연결 시 /api/v1/metrics 호출)
                const t = Date.now() / 1000;
                const aiLoad = (Math.sin(t / 4) + 1) / 2; // 0 ~ 1 사이 부하율
                
                // 각 랙 온도 업데이트 로직
                let totalPower = 0;
                racks.forEach(rack => {
                    if(rack.isAI) {
                        // AI 랙은 부하에 따라 온도가 85도까지 치솟음
                        rack.temp = 25 + (aiLoad * 60) + (Math.random() * 2);
                    } else {
                        // 일반 랙은 22~28도 유지
                        rack.temp = 22 + (Math.random() * 5);
                    }
                    totalPower += rack.temp * 0.4;
                });

                // 80도 돌파 시 사전 냉각 경고 표시
                if (aiLoad > 0.8) {
                    document.getElementById('cooling-status').style.display = 'inline';
                } else {
                    document.getElementById('cooling-status').style.display = 'none';
                }

                drawFloorPlan(); // 화면 다시 그리기

                // 차트 업데이트
                thermalChart.data.datasets[0].data.push(totalPower);
                thermalChart.data.datasets[0].data.shift();
                thermalChart.update();

            } catch (e) { console.error(e); }
        }

        setInterval(updateDashboard, 1000);
        drawFloorPlan();
    </script>
</body>
</html>
"""