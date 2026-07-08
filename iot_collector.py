"""
iot_collector.py — 데이터센터 사우스바운드(Southbound) IoT 수집기
--------------------------------------------------
실제 장비(서버, PDU, 항온항습기)와 통신하는 레이어입니다.
장비가 연결되면 DEMO_MODE를 False로 변경하고 실제 IP를 입력합니다.
"""
import time
import random
import threading
import requests  # Redfish API 통신용
# from pymodbus.client import ModbusTcpClient  # 실제 배포 시 주석 해제

class IoTCollector:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        self.state_lock = threading.Lock()
        
        # 수집된 최신 상태 버퍼
        self.latest_metrics = {
            "workload_factor": 0.1,
            "it_power_kw": 0.0,
            "cooling_power_kw": 0.0,
            "pue": 1.0,
            "rack_temperatures": []
        }
        self.target_workload = 0.1

    def set_target_workload(self, target):
        with self.state_lock:
            self.target_workload = target

    def _poll_redfish_servers(self, load):
        """[서버/GPU 통신] Redfish REST API를 통한 온도 및 전력 수집"""
        if not self.demo_mode:
            # 실제 Redfish 통신 예제 코드 (장비 연결 시 작동)
            # try:
            #     res = requests.get("https://10.0.0.15/redfish/v1/Chassis/1/Thermal", verify=False)
            #     return res.json()['Temperatures'][0]['ReadingCelsius']
            # except: pass
            pass
            
        # 데모 모드: 부하에 따른 정밀한 온도 시뮬레이션
        racks = []
        for r in range(3):
            for c in range(12):
                is_ai = (r == 1 or r == 2)
                base_temp = 22.0
                if is_ai:
                    temp = base_temp + (load * 65.0) + random.uniform(-1.5, 1.5)
                else:
                    temp = base_temp + random.uniform(-0.5, 2.0)
                racks.append({"id": f"R-{r}-{c}", "temp": round(temp, 1), "is_ai": is_ai})
        return racks

    def _poll_modbus_crac_ups(self, load):
        """[기반설비 통신] Modbus TCP를 통한 공조기(CRAC) 및 전력(UPS) 수집"""
        if not self.demo_mode:
            # 실제 Modbus 통신 예제 코드
            # client = ModbusTcpClient('10.0.1.50')
            # client.connect()
            # result = client.read_holding_registers(address=100, count=2)
            # client.close()
            pass
            
        # 데모 모드: 전력량 시뮬레이션
        it_power = (load * 3500) + 400 + random.uniform(-10, 10)
        cooling_power = (load * 1200) + 150 + random.uniform(-5, 5)
        pue = (it_power + cooling_power) / it_power if it_power > 0 else 1.0
        return it_power, cooling_power, pue

    def start_polling_loop(self, ai_engine_callback):
        """백그라운드에서 1초마다 센서를 긁어오는 무한 루프"""
        while True:
            with self.state_lock:
                # 관성을 가진 워크로드 시뮬레이션
                diff = self.target_workload - self.latest_metrics["workload_factor"]
                current_load = self.latest_metrics["workload_factor"] + (diff * 0.2)
                self.latest_metrics["workload_factor"] = current_load

            # 1. 하위 장비 폴링 (Redfish, Modbus)
            rack_temps = self._poll_redfish_servers(current_load)
            it_pwr, cool_pwr, pue = self._poll_modbus_crac_ups(current_load)

            with self.state_lock:
                self.latest_metrics["it_power_kw"] = round(it_pwr, 1)
                self.latest_metrics["cooling_power_kw"] = round(cool_pwr, 1)
                self.latest_metrics["pue"] = round(pue, 2)
                self.latest_metrics["rack_temperatures"] = rack_temps

            # 2. 수집된 데이터를 상위 AI 엔진으로 푸시
            if ai_engine_callback:
                ai_engine_callback(it_pwr, cool_pwr, pue)

            time.sleep(1.0) # 1초 주기 폴링