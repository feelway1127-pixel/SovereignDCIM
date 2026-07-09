"""
iot_collector.py — 데이터센터 사우스바운드(Southbound) IoT 수집기
--------------------------------------------------
"""
import time
import random
import threading

class IoTCollector:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        self.state_lock = threading.Lock()
        self.latest_metrics = {
            "workload_factor": 0.1,
            "it_power_kw": 0.0,
            "cooling_power_kw": 0.0,
            "pue": 1.0
        }
        self.target_workload = 0.1

    def set_target_workload(self, target):
        with self.state_lock:
            self.target_workload = target

    def _poll_sensors(self, load):
        # 데모 모드: 전력 및 PUE 시뮬레이션
        it_power = (load * 3000) + 500 + random.uniform(-10, 10)
        cooling_power = (load * 1000) + 200 + random.uniform(-5, 5)
        pue = (it_power + cooling_power) / it_power if it_power > 0 else 1.0
        return it_power, cooling_power, pue

    def start_polling_loop(self, ai_engine_callback):
        while True:
            with self.state_lock:
                diff = self.target_workload - self.latest_metrics["workload_factor"]
                current_load = self.latest_metrics["workload_factor"] + (diff * 0.15)
                self.latest_metrics["workload_factor"] = current_load

            it_pwr, cool_pwr, pue = self._poll_sensors(current_load)

            with self.state_lock:
                self.latest_metrics["it_power_kw"] = round(it_pwr, 1)
                self.latest_metrics["cooling_power_kw"] = round(cool_pwr, 1)
                self.latest_metrics["pue"] = round(pue, 2)

            if ai_engine_callback:
                ai_engine_callback(it_pwr, cool_pwr, pue)

            time.sleep(1.0)