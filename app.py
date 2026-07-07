from flask import Flask, jsonify, render_template_string, request
from core_engine import SovereignCore

app = Flask(__name__)
core = SovereignCore()

# 가상의 인프라 원시 데이터 스트림 (실제로는 센서나 SNMP에서 긁어오는 값)
mock_raw_stream = {
    "SAMSUNG_PDU_01": 2200,
    "VERTIV_UPS_02": 1,
    "CUSTOM_SENSOR_99": 26.5
}

# 🔐 보안용 기만 데이터 (샌드박스 매트릭스)
honeypot_fake_stream = {
    "SAMSUNG_PDU_01": {"value": 9999.9, "unit": "kW", "description": "⚠️ 기만용 더미 노드 A"},
    "VERTIV_UPS_02": {"value": 0, "unit": "CRITICAL", "description": "⚠️ 기만용 더미 노드 B"},
    "CUSTOM_SENSOR_99": {"value": -99.9, "unit": "°C", "description": "⚠️ 기만용 더미 노드 C"}
}

# 메인 화면 UI (사이버펑크 스타일 대시보드 + 안티 디버깅 스크립트 내장)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Sovereign DCIM - Core Console</title>
    <style>
        body { background-color: #0d0e15; color: #00ff66; font-family: 'Courier New', monospace; padding: 30px; }
        .container { max-width: 800px; margin: 0 auto; border: 1px solid #00ff66; padding: 20px; box-shadow: 0 0 15px #00ff66; }
        h1 { text-align: center; color: #ff0055; text-shadow: 0 0 8px #ff0055; }
        .metric-card { background: #161925; border-left: 5px solid #00ff66; margin: 15px 0; padding: 15px; }
        .value { font-size: 24px; color: #ffffff; font-weight: bold; }
    </style>
    <script>
        // 🛡️ 핵심 기만 무기: 개발자 도구(F12) 탐지 및 콘솔 무력화
        setInterval(function() {
            // 무한 루프 디버거를 걸어 정상적인 검사 차단
            debugger; 
        }, 100);

        // 콘솔 창을 강제로 계속 초기화하여 패킷 스니핑 방해
        console.log = function() { console.clear(); };
    </script>
</head>
<body>
    <div class="container">
        <h1>SOVEREIGN DCIM CORE</h1>
        <hr style="border-color: #00ff66;">
        <p style="text-align: center;">[ SYSTEM STATUS: SECURE / NOISE LEVEL: MINIMAL ]</p>
        
        <div id="metrics-display">
            </div>
    </div>

    <script>
        // 데이터 실시간 로드 함수
        async function fetchMetrics() {
            try {
                const response = await fetch('/api/v1/metrics');
                const data = await response.json();
                let html = '';
                for (const [key, info] of Object.entries(data)) {
                    html += `
                        <div class="metric-card">
                            <h3>${info.description} (${key})</h3>
                            <div class="value">${info.value} ${info.unit}</div>
                            <small style="color: #888;">PORT: ${info.port}</small>
                        </div>
                    `;
                }
                document.getElementById('metrics-display').innerHTML = html;
            } catch (e) {
                console.error("Data Stream Interrupted");
            }
        }
        setInterval(fetchMetrics, 2000); // 2초마다 꼼꼼하게 갱신
        fetchMetrics();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/metrics')
def get_metrics():
    # 비인가자 또는 특정 자동화 스캔 봇(User-Agent 검증 등) 판단 로직 적용 가능
    # 여기서는 데모를 위해 정상 데이터를 파싱해서 보내주되, 
    # 해커가 직접 API 주소만 무단으로 긁어가려고 할 때 조건부 기만 데이터를 보낼 수 있는 구조를 만듦
    is_suspicious = False # 탐지 로직 발동 조건 (추후 확장)
    
    if is_suspicious:
        return jsonify(honeypot_fake_stream)
    
    # 정상 흐름일 때 코어 엔진 작동
    processed_data = core.parse_metrics(mock_raw_stream)
    return jsonify(processed_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)