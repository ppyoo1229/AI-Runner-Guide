# app/routegen.py
# OSMnx 루프 후보 생성
# 로깅/ 파라미터 표시 추가
# 중심, 반경, 타깃거리, 생성된 후보 수/시도 횟수 로그
import math, os, random, uuid, logging
import osmnx as ox
import networkx as nx
from shapely.geometry import LineString
from typing import List, Dict, Any
from app.models import LatLng

log = logging.getLogger("routegen")
TARGET_KM = float(os.getenv("TARGET_DISTANCE_KM", "3.0"))
TOL = float(os.getenv("LOOP_TOLERANCE", "0.10"))
RADIUS_M = int(os.getenv("DEFAULT_RADIUS_M", "2000"))

def _nearest_node(G, lat, lng):
    return ox.distance.nearest_nodes(G, X=lng, Y=lat)

def generate_loop_candidates(center: LatLng, n_candidates: int = 6) -> List[Dict[str, Any]]:
    ox.settings.use_cache = True
    log.info(f"[routegen] center=({center.lat},{center.lng}) R={RADIUS_M} target={TARGET_KM}km tol={TOL}")
    G = ox.graph_from_point((center.lat, center.lng),
                            dist=RADIUS_M, network_type="walk", simplify=True)
    G = ox.add_edge_lengths(G)

    target_m = TARGET_KM * 1000
    low, high = target_m * (1 - TOL), target_m * (1 + TOL)
    ring_r = target_m / (2*math.pi)
    start = _nearest_node(G, center.lat, center.lng)

    candidates = []
    trials = 0
    while len(candidates) < n_candidates and trials < n_candidates*5:
        trials += 1
        # 2~3개 waypoint
        k = random.choice([2, 3])
        wps = []
        for i in range(k):
            theta = random.random()*2*math.pi
            lat_off = (ring_r*math.cos(theta))/111111
            lng_off = (ring_r*math.sin(theta))/ (111111*math.cos(math.radians(center.lat)))
            node = _nearest_node(G, center.lat+lat_off, center.lng+lng_off)
            wps.append(node)

        path = [start]
        total_m = 0.0
        ok = True
        for node in wps + [start]:
            try:
                seg = nx.shortest_path(G, path[-1], node, weight="length")
            except nx.NetworkXNoPath:
                ok = False; break
            for u, v in zip(seg[:-1], seg[1:]):
                data = G.get_edge_data(u, v)
                # MultiEdge 안전 처리
                length = data[0]["length"] if 0 in data else list(data.values())[0]["length"]
                total_m += length
            path = seg if len(path)==1 else path + seg[1:]

        if ok and low <= total_m <= high:
            xs = [G.nodes[n]["x"] for n in path]
            ys = [G.nodes[n]["y"] for n in path]
            geom = LineString(list(zip(xs, ys)))
            candidates.append({
                "node_path": path,
                "length_m": total_m,
                "geom": geom
            })

    log.info(f"[routegen] candidates={len(candidates)} (trials={trials})")
    return candidates
