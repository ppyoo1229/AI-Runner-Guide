# Running RecSys MVP

초보 러너를 위한 러닝 코스 추천 시스템

## 📁 프로젝트 구조

```
running-recsys/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI 엔드포인트
│   ├── models.py       # Pydantic 데이터 모델
│   ├── geo.py          # 지오코딩 (Kakao API)
│   ├── routegen.py     # OSMnx 루프 생성
│   ├── scoring.py      # 초보자 적합도 스코어링
│   ├── utils.py        # 피처 추정 & 유틸리티
│   └── llm.py          # LLM 쿼리 파싱 (stub)
├── scripts/
│   ├── test_geocode.py # 지오코딩 테스트
│   ├── test_loop.py    # 루프 생성 테스트
│   └── quick_map.py    # 결과 시각화
├── .env                # 환경 변수
├── requirements.txt    # Python 의존성
└── README.md
```

## 🚀 설치 & 실행

### 1. 가상환경 활성화
```bash
source runenv/bin/activate
```

### 2. 환경 변수 설정
`.env` 파일에 Kakao REST API 키 설정:
```
KAKAO_REST_API_KEY=your_key_here
TARGET_DISTANCE_KM=3.0
LOOP_TOLERANCE=0.10
DEFAULT_RADIUS_M=2000
```

### 3. 테스트 스크립트 실행
```bash
# 지오코딩 테스트
PYTHONPATH=. python scripts/test_geocode.py

# 루프 생성 테스트
PYTHONPATH=. python scripts/test_loop.py
```

### 4. FastAPI 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API 엔드포인트

### POST /find_course
러닝 코스 찾기

**Request:**
```json
{
  "params": {
    "location": "강남역",
    "distance_km": 3.0,
    "time": "day"
  }
}
```

**Response:**
```json
{
  "routes": [
    {
      "route_id": "loop_0_a1b2c3",
      "name": "강남역 루프 #1",
      "start": {
        "lat": 37.498,
        "lng": 127.027,
        "name": "강남역",
        "address": "서울 강남구..."
      },
      "polyline": "encoded_polyline_string",
      "features": {
        "dist_km": 3.1,
        "duration_min_est": 27.9,
        "lighting_index": 0.7,
        "intersections_per_km": 0.6
      },
      "scores": {
        "beginner": 85.5
      },
      "badges": ["조명좋음", "교차로적음"]
    }
  ]
}
```

## 🔧 주요 컴포넌트

### 루프 생성 알고리즘 (routegen.py)
- OSMnx로 보행 가능한 도로망 로드
- 원형 링 위에 랜덤 waypoint 생성
- 최단 경로 계산 & 거리 필터링
- 목표 거리 ±10% 이내 후보 반환

### 스코어링 (scoring.py)
초보자 적합도 = 100점 기준:
- **거리 차이** (25점): 목표 거리와의 차이
- **고도 상승** (20점): 경사도 페널티
- **교차로** (15점): 교차로 빈도 페널티
- **신호등** (10점): 신호등 빈도 페널티  
- **조명** (20점): 가로등 밀도 보너스 (야간 30점)
- **수변/공원** (10점): 수변/공원 근접도 보너스

## 📝 TODO

현재 MVP 단계로, 다음 기능들이 stub/상수로 처리됨:

- [ ] **DEM 고도 데이터** 통합 (utils.py:15)
- [ ] **OSM 교차로/신호등** 실제 집계 (utils.py:16-17)
- [ ] **가로등 공간 조인** (utils.py:18)
- [ ] **수변/공원 버퍼 overlap** (utils.py:19)
- [ ] **LLM 파싱** 구현 (llm.py)
- [ ] **Kakao Directions** 경로 정교화 (main.py:66)

## ⚠️ 알려진 이슈

1. **Kakao API 403 에러**: API 키가 만료되었거나 잘못된 경우
   - [Kakao Developers](https://developers.kakao.com/)에서 키 재발급
   
2. **OSMnx 후보 없음**: 반경이 작아서 루프를 못 만드는 경우
   - `.env`에서 `DEFAULT_RADIUS_M=2500` 또는 `3000`으로 증가

3. **PYTHONPATH**: 스크립트 실행 시 `PYTHONPATH=.` 필요
   - 또는 패키지 설치: `pip install -e .`

## 📊 데이터 흐름

```
사용자 쿼리
  ↓
[FastAPI] /find_course
  ↓
[geo.py] 지오코딩 → LatLng
  ↓
[routegen.py] OSMnx 루프 생성 (6개 후보)
  ↓
[utils.py] 각 루프의 피처 추정
  ↓
[scoring.py] 초보자 스코어 계산
  ↓
상위 3개 정렬 & 반환
```

## 🛠️ 개발 가이드

### 새로운 스코어링 모델 추가
1. `scoring.py`에 함수 추가 (예: `intermediate_score`)
2. `main.py:50`에서 스코어 계산 추가
3. `RouteItem.scores`에 추가

### 새로운 피처 추가
1. `utils.py:estimate_features`에 계산 로직 추가
2. 반환 dict에 키 추가
3. `scoring.py`에서 가중치 반영
4. `utils.py:badges_from_features`에 뱃지 조건 추가

## 📄 라이선스

MIT
