import json
import os

class SovereignCore:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.registry = {}
        self.load_config()

    def load_config(self):
        """config.json 파일을 읽어와 하드웨어 레지스트리를 동적으로 로드"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"❌ 설정을 찾을 수 없습니다: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            self.registry = config_data.get("HARDWARE_REGISTRY", {})
            print(f"✅ 하드웨어 레지스트리 로드 완료: {len(self.registry)}개 장비 매핑됨.")

    def parse_metrics(self, raw_data):
        """원시 데이터를 수집하여 config에 정의된 계수(scale_factor)대로 꼼꼼하게 정제"""
        processed_metrics = {}
        
        for hw_id, hardware_info in self.registry.items():
            # 수집된 원시 데이터 스트림에서 해당 장비 값 추출 (없으면 0)
            raw_value = raw_data.get(hw_id, 0)
            
            # 꼼꼼한 데이터 정합성 처리 (보정치 계산)
            calculated_value = round(raw_value * hardware_info["scale_factor"], 2)
            
            processed_metrics[hw_id] = {
                "port": hardware_info["port"],
                "value": calculated_value,
                "unit": hardware_info["unit"],
                "description": hardware_info["description"]
            }
            
        return processed_metrics

# 모듈 단독 테스트 코드
if __name__ == "__main__":
    # 가상의 인프라 원시 데이터 (Raw 수치)
    mock_raw_stream = {
        "SAMSUNG_PDU_01": 2200,      # 2200 * 0.1 = 220.0 kW
        "VERTIV_UPS_02": 1,          # 1 * 1.0 = 1.0 Status
        "CUSTOM_SENSOR_99": 26.5     # 26.5 * 1.0 = 26.5 °C
    }
    
    # 엔진 가동 테스트
    try:
        core = SovereignCore()
        result = core.parse_metrics(mock_raw_stream)
        print("\n=== [정제된 실시간 인프라 데이터] ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"🚨 엔진 가동 실패: {e}")