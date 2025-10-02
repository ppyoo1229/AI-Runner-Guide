# 인코딩/피처 집계 스텁
import polyline as pl
from shapely.geometry import LineString
from typing import Dict

def encode_linestring_to_polyline(ls: LineString) -> str:
    coords = list(ls.coords)
    # coords are (x=lon, y=lat)
    latlngs = [(y, x) for (x, y) in coords]
    return pl.encode(latlngs, 5)

def estimate_features(length_m: float, is_night: bool=False) -> Dict:
    # MVP: 진짜 계산이 어려운 값(elev/intersection/lighting)은 0~1 사이 랜덤/상수로 시작,
    # 이후 가로등, OSM 태그, DEM 고도 합치면서 교체.
    dist_km = length_m / 1000
    elev_gain_norm = 0.1    # TODO: DEM 합치기
    intersections_per_km = 0.6  # TODO: OSM nodes classify
    signals_per_km = 0.2        # TODO: OSM highway=traffic_signals
    lighting_index = 0.7 if is_night else 0.5  # TODO: 가로등 공간조인
    water_park_ratio = 0.5      # TODO: 수변/공원 버퍼 overlap
    pace_min_per_km = 9.0       # 초보 조깅 pace 가정
    duration_min_est = dist_km * pace_min_per_km

    return dict(
        dist_km=dist_km,
        duration_min_est=duration_min_est,
        elev_gain_m=0.0,
        elev_gain_norm=elev_gain_norm,
        intersections_per_km=intersections_per_km,
        signals_per_km=signals_per_km,
        lighting_index=lighting_index,
        water_park_ratio=water_park_ratio
    )

def badges_from_features(f: Dict):
    badges=[]
    if f["lighting_index"] >= 0.6: badges.append("조명좋음")
    if f["intersections_per_km"] <= 0.7: badges.append("교차로적음")
    if f["elev_gain_norm"] <= 0.2: badges.append("평탄")
    return badges or ["기본"]
