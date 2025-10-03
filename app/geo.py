# app/geo.py
# 지오코딩 히트 수 로그
import httpx, os, logging
from typing import Optional, Dict, Any, List
from app.models import LatLng

log = logging.getLogger("geo")
KAKAO_KEY = os.getenv("KAKAO_REST_API_KEY")
HEADERS = {"Authorization": f"KakaoAK {KAKAO_KEY}"}


async def geocode_location(query: str) -> Optional[LatLng]:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    params = {"query": query, "size": 1}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params, headers=HEADERS)
        r.raise_for_status()
        docs = r.json().get("documents", [])
        log.info(f"[geocode] query={query}, hits={len(docs)}")
        if not docs:
            return None
        d = docs[0]
        return LatLng(
            lat=float(d["y"]), lng=float(d["x"]),
            place_id=d.get("id"), name=d.get("place_name"),
            address=d.get("road_address_name") or d.get("address_name")
        )
    
    
async def search_anchors(center_lng: float, center_lat: float,
                         keywords: List[str], radius: int = 3000, size: int = 10) -> List[Dict[str, Any]]:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    anchors=[]
    async with httpx.AsyncClient(timeout=10) as client:
        for kw in keywords[:7]:
            params = {"query": kw, "x": center_lng, "y": center_lat, "radius": radius, "size": size, "page": 1}
            r = await client.get(url, params=params, headers=HEADERS)
            r.raise_for_status()
            for d in r.json().get("documents", []):
                anchors.append({
                    "name": d.get("place_name"),
                    "lat": float(d["y"]),
                    "lng": float(d["x"]),
                    "address": d.get("road_address_name") or d.get("address_name"),
                    "place_id": d.get("id"),
                    "keyword": kw
                })
    # 좌표 근접 중복 제거
    seen=set(); dedup=[]
    for a in anchors:
        k=(round(a["lat"],5), round(a["lng"],5))
        if k in seen: continue
        seen.add(k); dedup.append(a)
    log.info(f"[anchors] kw={keywords} -> {len(dedup)}")
    return dedup