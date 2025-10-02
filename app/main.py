# 지오코딩 결과, 후보 수, Top-3 점수 로그
import os, uuid
from fastapi import FastAPI, HTTPException
from app.models import ParseRequest, ParsedParams, FindCourseRequest, FindCourseResponse, RouteItem, LatLng
from app.llm import parse_running_query, explain_route
from app.geo import geocode_location, snap_with_kakao_directions
from app.routegen import generate_loop_candidates
from app.utils import encode_linestring_to_polyline, estimate_features, badges_from_features
from app.scoring import beginner_score
'''
FastAPI 엔드포인트 → LLM 파싱 → 루프 생성 → 스코어 → 응답
'''

app = FastAPI(title="Running RecSys (MVP)")

@app.post("/parse", response_model=ParsedParams)
async def parse(req: ParseRequest):
    return parse_running_query(req.text)

@app.post("/find_course", response_model=FindCourseResponse)
async def find_course(req: FindCourseRequest):
    p = req.params
    if not p.location:
        raise HTTPException(400, "location is required")

    # 1) 지오코딩
    start = await geocode_location(p.location)
    if not start:
        raise HTTPException(404, "location not found")

    # 2) OSMnx 루프 후보
    cands = generate_loop_candidates(start)

    if not cands:
        # 폴백: out&back 1.5km 왕복 등으로 대체 가능
        raise HTTPException(503, "no loop candidate found")

    # 3) 각 후보 피처/스코어 계산
    routes_json = []
    target_km = p.distance_km or float(os.getenv("TARGET_DISTANCE_KM", "3.0"))
    is_night = (p.time == "night")

    for idx, c in enumerate(cands):
        feats = estimate_features(c["length_m"], is_night=is_night)
        score = beginner_score(feats, target_km, is_night=is_night)
        poly = encode_linestring_to_polyline(c["geom"])
        item = RouteItem(
            route_id=f"loop_{idx}_{uuid.uuid4().hex[:6]}",
            name=f"{p.location} 루프 #{idx+1}",
            start=start,
            polyline=poly,
            features=feats,
            scores={"beginner": score},
            badges=badges_from_features(feats)
        )
        routes_json.append(item)

    # 4) 상위 3개만 정렬
    routes_json.sort(key=lambda r: r.scores["beginner"], reverse=True)
    routes_json = routes_json[:3]

    # 5) 카카오 Directions로 polyline/시간 스냅 정교화
    # for i, r in enumerate(routes_json):
    #     snap = await snap_with_kakao_directions(start, [])  # TODO: waypoint 넣기
    #     # r.polyline = snap["polyline"]; r.features["duration_min_est"] = snap["duration_s"]/60

    return FindCourseResponse(routes=routes_json)
