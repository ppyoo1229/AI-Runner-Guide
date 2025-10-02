# app/geo.py
# 지오코딩 히트 수 로그
import httpx, os, logging
from typing import Optional, Dict, Any
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
