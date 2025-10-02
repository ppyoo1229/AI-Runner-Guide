# 초보자 적합도 스코어
from typing import Dict
import math

DEFAULT_W = dict(w1=25, w2=20, w3=15, w4=10, w5=20, w6=10)

def beginner_score(features: Dict, target_km: float, is_night: bool) -> float:
    w = DEFAULT_W.copy()
    if is_night:
        w["w5"] += 10  # 조명 가중 강화

    dist_pen = abs(features["dist_km"] - target_km)
    sc = 100 \
        - w["w1"] * dist_pen \
        - w["w2"] * features["elev_gain_norm"] \
        - w["w3"] * features["intersections_per_km"] \
        - w["w4"] * features["signals_per_km"] \
        + w["w5"] * features["lighting_index"] \
        + w["w6"] * features["water_park_ratio"]
    return max(0.0, min(100.0, sc))
