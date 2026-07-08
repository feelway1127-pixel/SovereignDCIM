from flask import Flask, jsonify, render_template, request
import random
import time
import math
import os

app = Flask(__name__)

# 시스템 가동 이후 쌓이는 마스터 로그 버퍼
SYSTEM_LOGS = [
    {"timestamp": int(time.time()) - 60, "level": "INFO", "message": "DCIM Core Engine Initialized."},
    {"timestamp": int(time.time()) - 30, "level": "INFO", "message": "Modbus TCP Gateway Link Established."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/telemetry', methods=['GET'])
def get_telemetry():
    current_time = time.time()
    load_factor = (math.sin(current_time / 8) + 1) / 2
    
    rack_metrics = []
    total_it_power = 0.0
    
    for row_idx in range(4):
        row_letter = chr(65 + row_idx)
        for col_idx in range(1, 13):
            is_hpc = row_idx in [1, 2]
            base_temp = 26.5 if is_hpc else 21.0
            noise = random.uniform(-0.3, 0.3)
            
            calculated_temp = base_temp + (load_factor * 54.0 if is_hpc else random.uniform(0, 2.5)) + noise
            calculated_power = calculated_temp * 0.415
            total_it_power += calculated_power
            
            rack_metrics.append({
                "id": f"RACK-{row_letter}-{col_idx:02d}",
                "node_class": "HPC_ACCELERATOR" if is_hpc = r in [1, 2] else "STANDARD_STORAGE",
                "temperature_c": round(calculated_temp, 2),
                "power_consumption_kw": round(calculated_power, 3),
                "status": "CRITICAL" if calculated_temp > 75 else "ONLINE"
            })
            
    # 고온 경고 로그 실시간 강제 인젝션
    if load_factor > 0.85 and len(SYSTEM_LOGS) < 10:
        SYSTEM_LOGS.append({
            "timestamp": int(current_time),
            "level": "WARN",
            "message": f"High thermal threshold exceeded on HPC Cluster. Load: {round(load_factor*100, 1)}%"
        })

    # 상용 필수 지표: PUE 및 총 전력 공급량 수식 계산
    cooling_power = total_it_power * 0.35 + (load_factor * 25.0)
    total_facility_power = total_it_power + cooling_power
    pue = total_facility_power / total_it_power if total_it_power > 0 else 1.0
    
    return jsonify({
        "status": "synchronized",
        "timestamp": int(current_time),
        "summary": {
            "load_factor": round(load_factor, 4),
            "it_power_kw": round(total_it_power, 2),
            "total_power_kw": round(total_facility_power, 2),
            "pue": round(pue, 2)
        },
        "assets": rack_metrics,
        "logs": SYSTEM_LOGS[-6:] # 최신 6개 로그만 전송
    })

@app.route('/api/v1/control/purge', methods=['POST'])
def purge_node():
    """ 제어 옵션 검증을 위한 비동기 엔드포인트 """
    current_time = int(time.time())
    SYSTEM_LOGS.append({
        "timestamp": current_time,
        "level": "CRITICAL",
        "message": "Manual Purge Signal Injected by Administrator."
    })
    return jsonify({"status": "acknowledged", "purged_at": current_time})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)