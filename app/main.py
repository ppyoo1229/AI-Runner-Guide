'''
FastAPI 엔드포인트 → LLM 파싱 → 루프 생성 → 스코어 → 응답
'''
import os, uuid, logging
from fastapi import FastAPI, HTTPException
from app.models import ParseRequest, ParsedParams, FindCourseRequest, FindCourseResponse, RouteItem, LatLng
from app.llm import parse_running_query, explain_route
from app.geo import geocode_location, search_anchors
from app.routegen import generate_loop_candidates
from app.utils import encode_linestring_to_polyline, estimate_features, badges_from_features
from app.utils import load_lamps_csv, lighting_index_for_route
from app.scoring import beginner_score

log = logging.getLogger("api")
app = FastAPI(title="Running RecSys (MVP)")

@app.on_event("startup")
def _load_resources():
    csv_path = os.getenv("LAMPS_CSV", "/mnt/data/서울시 가로등 위치 정보.csv")
    try:
        load_lamps_csv(csv_path, lon_col="경도", lat_col="위도") 
        log.info(f"[startup] lamps loaded: {csv_path}")
    except Exception as e:
        log.warning(f"[startup] lamps load failed: {e}")

@app.post("/parse", response_model=ParsedParams)
async def parse(req: ParseRequest):
    return parse_running_query(req.text)

@app.post("/find_course", response_model=FindCourseResponse)
async def find_course(req: FindCourseRequest):
    p = req.params
    if not p.location:
        raise HTTPException(400, "location is required")

    # 1) 지오코딩
    center = await geocode_location(p.location)
    if not center:
        raise HTTPException(404, "location not found")

    # 2) 앵커 탐색
    keywords = p.keywords or ["공원","하천","산책로","운동장","트랙"]
    anchors = await search_anchors(center.lng, center.lat, keywords, radius=int(os.getenv("DEFAULT_RADIUS_M","2000")))
    if not anchors:
        anchors = [{"name": p.location, "lat": center.lat, "lng": center.lng, "address": center.address or ""}]

    routes_json = []
    target_km = p.distance_km or float(os.getenv("TARGET_DISTANCE_KM", "3.0"))
    is_night = (p.time == "night")

    # 3) 앵커별 루프 생성 → 조명지수 덮어쓰기 → 스코어
    for anc in anchors[:3]:  # 상위 몇 개만
        start = LatLng(lat=anc["lat"], lng=anc["lng"], name=anc.get("name"), address=anc.get("address"))
        cands = generate_loop_candidates(start)
        for idx, c in enumerate(cands):
            feats = estimate_features(c["length_m"], is_night=is_night)
            try:
                li, lamps_pk = lighting_index_for_route(c["geom"])
                feats["lighting_index"] = li
                feats["lamps_per_km"] = lamps_pk
            except Exception as e:
                log.debug(f"[lighting] skip: {e}")
            score = beginner_score(feats, target_km, is_night=is_night)
            poly = encode_linestring_to_polyline(c["geom"])
            item = RouteItem(
                route_id=f"loop_{idx}_{uuid.uuid4().hex[:6]}",
                name=f"{(anc.get('name') or p.location)} 루프 #{idx+1}",
                start=start,
                polyline=poly,
                features=feats,
                scores={"beginner": score},
                badges=badges_from_features(feats)
            )
            routes_json.append(item)

    if not routes_json:
        raise HTTPException(503, "no loop candidate found")

    routes_json.sort(key=lambda r: r.scores["beginner"], reverse=True)
    return FindCourseResponse(routes=routes_json[:3])
