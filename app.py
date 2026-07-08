from flask import Flask, jsonify, render_template_string, request
import random
import time
import math
import os

app = Flask(__name__)

# 시스템 가동 이후 누적되는 관제 마스터 로그 버퍼
SYSTEM_LOGS = [
    {"timestamp": int(time.time()) - 60, "level": "INFO", "message": "DCIM Core Engine Initialized."},
    {"timestamp": int(time.time()) - 30, "level": "INFO", "message": "Modbus TCP Gateway Link Established."}
]

# 완전히 결합된 하이테크 UI 마크업 및 자바스크립트 통신 엔진
MAIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>dcim.kr - SOVEREIGN MASTER CONTROL</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-main: #040508;
            --panel-bg: #090b11;
            --border-muted: #161a23;
            --border-glow: #222938;
            --neon-green: #00ff66;
            --neon-blue: #00e5ff;
            --neon-orange: #ff9900;
            --neon-red: #ff2a5f;
            --text-main: #f1f5f9;
            --text-muted: #4f5e75;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: 'Inter', 'Malgun Gothic', sans-serif;
            margin: 0;
            padding: 20px;
            overflow-x: hidden;
            background-image: 
                linear-gradient(rgba(22, 26, 35, 0.3) 1px, transparent 1px),
                linear-gradient(90deg, rgba(22, 26, 35, 0.3) 1px, transparent 1px);
            background-size: 30px 30px;
        }

        .container {
            max-width: 1720px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* 📡 엔터프라이즈 탑 바 헤더 */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--panel-bg);
            border: 1px solid var(--border-muted);
            padding: 14px 24px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        }

        .brand {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -1px;
            margin: 0;
        }

        .brand span {
            color: var(--neon-red);
        }

        .status-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 700;
            color: var(--neon-green);
            background: rgba(0, 255, 102, 0.04);
            border: 1px solid rgba(0, 255, 102, 0.2);
            padding: 6px 16px;
            border-radius: 30px;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.5px;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            background-color: var(--neon-green);
            border-radius: 50%;
            animation: pulse 1.6s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.6); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(0, 255, 102, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0); }
        }

        /* 📈 실시간 PUE 계측기 지표 스트립 */
        .meta-strip {
            display: flex;
            gap: 16px;
        }

        .meta-box {
            background: var(--panel-bg);
            border: 1px solid var(--border-muted);
            padding: 16px 24px;
            border-radius: 10px;
            flex: 1;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }

        .meta-box label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .meta-box span {
            display: block;
            font-size: 24px;
            font-weight: 800;
            color: var(--neon-blue);
            margin-top: 6px;
            font-family: 'JetBrains Mono', monospace;
        }

        /* 📊 관제 레이아웃 메인 그리드 */
        .main-grid {
            display: grid;
            grid-template-columns: 1.55fr 1fr;
            gap: 18px;
        }

        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-muted);
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
        }

        .panel h2 {
            margin: 0 0 16px 0;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-muted);
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-muted);
            padding-bottom: 12px;
        }

        /* 🗺️ 고해상도 2D 평면도 캔버스 컨테이너 */
        .floor-plan-container {
            position: relative;
            width: 100%;
            height: 520px;
            background: #020305;
            border: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 6px;
            overflow: hidden;
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        /* 🎛️ 정밀 인터랙션 툴팁 */
        #tooltip {
            position: absolute;
            background: rgba(7, 9, 15, 0.96);
            border: 1px solid rgba(0, 229, 255, 0.3);
            color: var(--text-main);
            padding: 12px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            line-height: 1.6;
            pointer-events: none;
            display: none;
            z-index: 100;
            border-radius: 6px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.8);
            backdrop-filter: blur(4px);
        }

        .legend {
            position: absolute;
            bottom: 16px;
            left: 16px;
            background: rgba(4, 5,