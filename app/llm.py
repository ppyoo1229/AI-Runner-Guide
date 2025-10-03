# LLM interaction stubs
# app/llm.py
# app/llm.py
import json, os, httpx, re
from typing import List
from app.models import ParsedParams

HF_ENDPOINT = os.getenv("HF_TGI_URL", "http://localhost:8080")
MODEL_ID = os.getenv("KANANA_MODEL", "kakaocorp/kanana-1.5-8b-instruct-2505")

BASE_KEYWORDS = [
    "공원","하천","산책로","운동장","트랙","둘레길","강변","호수공원","체육공원","수변","강","천","호수"
]

INSTRUCTIONS = """당신은 러닝 코스 추천 시스템의 파라미터 파서입니다.
사용자 한국어 문장에서 다음 JSON을 '반드시' 출력하세요. 추가 텍스트를 절대 붙이지 마세요.

{
  "location": string|null,           // 출발 지점 또는 중심 지명 (예: 한강공원 잠원지구, 서울숲, 강남역). 없으면 null
  "distance_km": number|null,        // 희망 거리(km). 범위 표현(3~5km)은 평균값으로. 분 단위는 9 min/km 가정으로 km 환산. 없으면 null
  "time": "day"|"night"|null,        // 낮/밤 선호. 새벽/저녁/밤=night, 아침/낮=day. 언급 없으면 null
  "keywords": string[]               // 러닝 코스 검색용 한국어 키워드 배열 (예: ["공원","하천","산책로","운동장","트랙"]). 3~7개
}

규칙:
- JSON만 출력합니다.
- '새벽, 저녁, 밤'은 night로, '아침, 낮, 점심'은 day로 매핑합니다.
- '걷기, 산책' 의도라도 러닝 코스 탐색을 위해 위 키워드 후보군을 포함하세요.
- 불필요한 서술을 금지하고, null이 필요하면 null을 사용하세요.
- 예시 거리 표현: "3km", "3~5km", "약 5km", "30분", "한 바퀴", "짧게".
  - "3~5km" → 4.0
  - "30분" → 30/9 ≈ 3.3
"""

def _post_tgi(payload):
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{HF_ENDPOINT}/generate", json=payload)
        r.raise_for_status()
        data = r.json()
        # TGI: "generated_text" 또는 "outputs"[0]["text"] 계열 구현체가 다를 수 있어 보정
        if "generated_text" in data:
            return data["generated_text"]
        if "outputs" in data and data["outputs"]:
            return data["outputs"][0].get("text", "")
        return ""

def _to_km_from_text(txt: str):
    # 3~5km, 3-5km, 3.5km, 30분, 45 min 등 처리
    txt = txt.strip()
    # 범위 → 평균
    m = re.search(r'(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)(?=\s*(?:km|킬로|km/h|k m|$))', txt, re.I)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return round((a + b) / 2.0, 1)
    # 단일 수치 + 단위
    m = re.search(r'(\d+(?:\.\d+)?)\s*(km|킬로|분|minute|min)\b', txt, re.I)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit in ["km","킬로"]:
        return val
    if unit in ["분","minute","min"]:
        return round(val / 9.0, 1)  # 9 min/km 가정
    return None

def _infer_time(text: str):
    t = text.lower()
    if any(k in t for k in ["밤","야간","저녁","새벽","night"]):
        return "night"
    if any(k in t for k in ["낮","아침","점심","day","오전","정오"]):
        return "day"
    return None

def _fallback_keywords(text: str) -> List[str]:
    # 간단 휴리스틱: 러닝/걷기/트랙/강/공원 등 단어 있으면 가중치 부여 가능
    # 우선은 기본 후보에서 5개 고정 반환 (LLM 실패 대비 가용성 보장)
    return ["공원","하천","산책로","운동장","트랙"]

def _normalize_keywords(arr) -> List[str]:
    if not isinstance(arr, list):
        return _fallback_keywords("")
    # 중복/불용어 제거 + 화이트리스트 중심 정리
    picked = []
    for s in arr:
        if not isinstance(s, str):
            continue
        t = s.strip()
        if not t:
            continue
        # 화이트리스트 매칭
        # (LLM이 엉뚱한 키워드 뱉어도 방어적으로 필터)
        for base in BASE_KEYWORDS:
            if base in t and base not in picked:
                picked.append(base)
    if not picked:
        picked = _fallback_keywords("")
    # 과도하게 많으면 상위 5개만
    return picked[:7]

def parse_running_query(text: str) -> ParsedParams:
    """
    자연어 쿼리를 ParsedParams로 변환
    - LLM 서버가 있으면 사용
    - 없으면 규칙 기반 fallback 사용
    """
    prompt = f"{INSTRUCTIONS}\n\n사용자:\n{text}\n\nJSON:"
    try:
        out = _post_tgi({
            "model": MODEL_ID,
            "inputs": prompt,
            "parameters": {
                "temperature": 0.1,          # 파싱은 낮은 온도로 안정화
                "max_new_tokens": 256,
                "stop": ["\n\n", "\n}"],     # JSON 조기 종료 유도
            },
        })
    except Exception as e:
        # LLM 서버 연결 실패 시 규칙 기반 fallback
        import logging
        logging.getLogger("llm").debug(f"LLM fallback (서버 연결 실패): {e}")
        return ParsedParams(
            location=None,
            distance_km=_to_km_from_text(text),
            time=_infer_time(text),
            keywords=_fallback_keywords(text),
        )

    # JSON 안전 파싱
    jtxt = out.strip()
    m = re.search(r'\{.*\}', jtxt, re.S)
    if m:
        jtxt = m.group(0)
    try:
        data = json.loads(jtxt)
    except Exception:
        # 완전 실패 시 규칙 기반 백업
        return ParsedParams(
            location=None,
            distance_km=_to_km_from_text(text),
            time=_infer_time(text),
            keywords=_fallback_keywords(text),
        )

    # 후처리/보정
    loc = data.get("location")
    if isinstance(loc, str):
        loc = loc.strip() or None

    dist = data.get("distance_km")
    if dist is None:
        dist = _to_km_from_text(text)
    elif isinstance(dist, str):
        # 혹시 문자열로 오면 변환 시도
        dist2 = _to_km_from_text(dist)
        dist = dist2 if dist2 is not None else None

    tval = data.get("time")
    if tval not in ("day", "night", None):
        tval = _infer_time(text)

    keywords = _normalize_keywords(data.get("keywords"))

    return ParsedParams(location=loc, distance_km=dist, time=tval, keywords=keywords)

def explain_route(route_data: dict) -> str:
    f = route_data.get("features", {})
    badges = route_data.get("badges", [])
    msg = f"{f.get('dist_km', 0):.1f}km · 예상 {int(f.get('duration_min_est',0))}분 · " \
          f"{' / '.join(badges) if badges else '기본 코스'}"
    return msg
