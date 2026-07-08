"""
ai_engine.py — 경량 시계열 예측 & 이상탐지 엔진
--------------------------------------------------
설계 의도:
  이 모듈은 텔레메트리의 "출처"에 무관하게 동작합니다. 즉, 지금은
  시뮬레이션 워크로드에서 값을 받지만, 실제 배포 시 BMS/PDU/BMC 센서
  텔레메트리로 입력만 교체하면 동일한 인터페이스(push/forecast/anomaly_score)로
  그대로 동작합니다 — 시뮬레이션과 실물 연동 사이의 전환 비용을 최소화하기 위한 구조입니다.

알고리즘:
  - 예측: 최근 N개 샘플에 대한 단순최소제곱 선형회귀로 향후 시점 값 추정
    (실제 정밀 예측이 필요하면 statsmodels ARIMA, Prophet, 혹은 LSTM으로 대체 가능하도록
     클래스 인터페이스만 유지한 채 내부 구현을 교체하면 됩니다)
  - 이상탐지: 이동평균/표준편차 대비 Z-score. |z| > 2.5 를 이상치로 간주.
    실제 운영에서는 계절성(주/야간, 요일)을 반영한 STL 분해 후 잔차 기반 탐지 권장.
"""
from collections import deque
import statistics

HISTORY_LEN = 120  # 최근 N개 샘플 보관


class TimeSeriesBuffer:
    """단일 지표(예: IT 전력, 온도)에 대한 롤링 윈도우 + 예측/이상탐지."""

    def __init__(self, maxlen: int = HISTORY_LEN):
        self.values = deque(maxlen=maxlen)

    def push(self, value: float) -> None:
        self.values.append(float(value))

    def _linear_regression(self):
        n = len(self.values)
        if n < 5:
            return None, None
        xs = range(n)
        ys = list(self.values)
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs) or 1e-9
        slope = num / den
        intercept = y_mean - slope * x_mean
        return slope, intercept

    def forecast(self, steps_ahead: int = 30):
        """steps_ahead 샘플 이후의 예측값 (샘플 간격 = 폴링 주기, 기본 1초 가정)."""
        slope, intercept = self._linear_regression()
        if slope is None:
            return None
        n = len(self.values)
        predicted = intercept + slope * (n - 1 + steps_ahead)
        return round(predicted, 2)

    def anomaly_score(self):
        if len(self.values) < 10:
            return {"is_anomaly": False, "z_score": 0.0}
        current = self.values[-1]
        history = list(self.values)[:-1]
        mean = statistics.mean(history)
        stdev = statistics.pstdev(history) or 1e-6
        z = (current - mean) / stdev
        return {"is_anomaly": bool(abs(z) > 2.5), "z_score": round(z, 2)}

    def trend(self) -> str:
        slope, _ = self._linear_regression()
        if slope is None:
            return "stable"
        if slope > 0.5:
            return "rising"
        if slope < -0.5:
            return "falling"
        return "stable"


class DcimAiEngine:
    """대시보드에 필요한 모든 지표를 한 번에 관리하는 파사드."""

    def __init__(self):
        self.buffers = {
            "it_power": TimeSeriesBuffer(),
            "cooling_power": TimeSeriesBuffer(),
            "pue": TimeSeriesBuffer(),
        }

    def ingest(self, it_power: float, cooling_power: float, pue: float):
        self.buffers["it_power"].push(it_power)
        self.buffers["cooling_power"].push(cooling_power)
        self.buffers["pue"].push(pue)

    def insights(self):
        it = self.buffers["it_power"]
        cooling = self.buffers["cooling_power"]
        pue = self.buffers["pue"]
        return {
            "it_power_forecast_30s": it.forecast(30),
            "it_power_trend": it.trend(),
            "it_power_anomaly": it.anomaly_score(),
            "cooling_power_forecast_30s": cooling.forecast(30),
            "pue_trend": pue.trend(),
            "pue_anomaly": pue.anomaly_score(),
        }
