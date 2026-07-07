import json
import os
import sqlite3
from datetime import datetime

class SovereignCore:
    def __init__(self, config_path="config.json", db_path="dcim_metrics.db"):
        self.config_path = config_path
        self.db_path = db_path
        self.registry = {}
        self.load_config()
        self.init_database()

    def load_config(self):
        """config.json 파일을 읽어와 하드웨어 레지스트리를 동적으로 로드"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"❌ 설정을 찾을 수 없습니다: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            self.registry = config_data.get("HARDWARE_REGISTRY", {})
            print(f"✅ 하드웨어 레지스트리 로드 완료: {len(self.registry)}개 장비 매핑됨.")

    def init_database(self):
        """타임머신 로그 저장을 위한 SQLite 데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 데이터 정합성을 위해 타임스탬프와 장비 ID, 정제된 값을 기록하는 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS infrastructure_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hardware_id TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("✅ 타임머신 데이터베이스(SQLite) 초기화 완료.")

    def parse_and_log_metrics(self, raw_data):
        """원시 데이터를 정제하고, 그 결과를 DB에 꼼꼼하게 적재 (타임머신 엔진)"""
        processed_metrics = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for hw_id, hardware_info in self.registry.items():
            raw_value = raw_data.get(hw_id, 0)
            calculated_value = round(raw_value * hardware_info["scale_factor"], 2)
            
            # 1. 메모리 상의 리턴 데이터 구조 형성
            processed_metrics[hw_id] = {
                "port": hardware_info["port"],
                "value": calculated_value,
                "unit": hardware_info["unit"],
                "description": hardware_info["description"],
                "timestamp": timestamp
            }
            
            # 2. 🛡️ 타임머신 DB에 0.1초의 오차도 없이 꼼꼼하게 적재
            cursor.execute("""
                INSERT INTO infrastructure_logs (timestamp, hardware_id, value, unit)
                VALUES (?, ?, ?, ?)
            """, (timestamp, hw_id, calculated_value, hardware_info["unit"]))
            
        conn.commit()
        conn.close()
        return processed_metrics

    def get_historical_logs(self, limit=20):
        """과거 기록을 추적하는 타임머신 쿼리 엔진"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, hardware_id, value, unit 
            FROM infrastructure_logs 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{"timestamp": r[0], "hardware_id": r[1], "value": r[2], "unit": r[3]} for r in rows]