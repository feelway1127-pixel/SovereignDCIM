from flask import Flask, jsonify, render_template_string
from core_engine import SovereignCore

app = Flask(__name__)
core = SovereignCore()

# 가상의 인프라 원시 데이터 스트림
mock_raw_stream = {
    "SAMSUNG_PDU_01": 2200,
    "VERTIV_UPS_02": 1,
    "CUSTOM_SENSOR_99": 26.5
}

# 메인 화면 UI (실시간 데이터 카드 + 하단 타임머신 실시간 로그 테이블 추가)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Sovereign DCIM - Core Console</title>
    <style>
        body { background-color: #0d0e15; color: #00ff66; font-family: 'Courier New', monospace; padding: 30px; }
        .container { max-width: 900px; margin: 0 auto; border: 1px solid #00ff66; padding: 20px; box-shadow: 0 0 15px #00ff66; }
        h1 { text-align: center; color: #ff0055; text-shadow: 0 0 8px #ff0055; }
        .grid { display: flex; gap: 15px; justify-content: space-between; }
        .metric-card { background: #161925; border-left: 5px solid #00ff66; padding: 15px; flex: 1; }
        .value { font-size: 24px; color: #ffffff; font-weight: bold; }
        .history-section { margin-top: 30px; border-top: 1px dashed #00ff66; padding-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background-color: #161925; color: #ff0055; }
        tr:nth-child(even) { background-color: #11131c; }
    </style>
    <script>
        setInterval(function() { debugger; }, 500); // 안티 디버깅
        console.log = function() { console.clear(); };
    </script>
</head>
<body>
    <div class="container">
        <h1>SOVEREIGN DCIM CORE</h1>
        <p style="text-align: center;">[ SYSTEM STATUS: SECURE / TIMEMACHINE ENGINE: ACTIVE ]</p>
        
        <div class="grid" id="metrics-display">
            </div>

        <div class="history-section">
            <h2>⏳ INFRASTRUCTURE TIMEMACHINE LOGS (최신 10개 적재 데이터)</h2>
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
        async function updateDashboard() {
            try {
                // 1. 실시간 데이터 가져오기
                const resMetrics = await fetch('/api/v1/metrics');
                const dataMetrics = await resMetrics.json();
                let metricsHtml = '';
                for (const [key, info] of Object.entries(dataMetrics)) {
                    metricsHtml += `
                        <div class="metric-card">
                            <small style="color: #ff0055;">${key}</small>
                            <h3>${info.description}</h3>
                            <div class="value">${info.value} ${info.unit}</div>
                        </div>
                    `;
                }
                document.getElementById('metrics-display').innerHTML = metricsHtml;

                // 2. 타임머신 로그 데이터 가져오기
                const resHistory = await fetch('/api/v1/history');
                const dataHistory = await resHistory.json();
                let historyHtml = '';
                dataHistory.forEach(row => {
                    historyHtml += `
                        <tr>
                            <td>${row.timestamp}</td>
                            <td style="color: #00ffbb;">${row.hardware_id}</td>
                            <td>${row.value}</td>
                            <td style="color: #888;">${row.unit}</td>
                        </tr>
                    `;
                });
                document.getElementById('history-display').innerHTML = historyHtml;

            } catch (e) {
                // 실시간 스트림 단절 제어
            }
        }
        setInterval(updateDashboard, 2000); // 2초 주기 동기화
        updateDashboard();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/metrics')
def get_metrics():
    # 원시 데이터를 파싱함과 동시에 데이터베이스에 자동 기록
    processed_data = core.parse_and_log_metrics(mock_raw_stream)
    return jsonify(processed_data)

@app.route('/api/v1/history')
def get_history():
    # 데이터베이스에서 최근 10개의 타임머신 데이터를 추출하여 리턴
    logs = core.get_historical_logs(limit=10)
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)