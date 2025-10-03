# 변경 사항 (Changelog)

## 🆕 최신 업데이트 - 앵커 기반 탐색 & 실제 가로등 데이터 통합

### 주요 개선사항

#### 1. 앵커 포인트 기반 루프 생성
**이전:** 사용자가 입력한 단일 지점 주변에서만 루프 생성
**변경:** 주변의 **공원, 하천, 산책로** 등을 먼저 검색한 후 해당 지점들을 시작점으로 루프 생성

**장점:**
- 더 다양한 루트 제안
- 러닝에 적합한 장소(공원, 수변) 우선 탐색
- 같은 지역에서도 여러 옵션 제공

**코드:** [app/main.py:41-54](app/main.py#L41-L54)

```python
# 앵커 탐색 예시
keywords = ["공원", "하천", "산책로", "운동장", "트랙"]
anchors = await search_anchors(center.lng, center.lat, keywords, radius=2000)
# → 강남역 주변 "공원" 검색 → "양재천 근린공원", "대치유수지", ...
```

#### 2. 실제 가로등 위치 데이터 통합
**이전:** 조명 지수를 상수(0.5 또는 0.7)로 가정
**변경:** 실제 **서울시 가로등 위치 CSV**를 로드하여 루트 주변 가로등 밀도 계산

**작동 방식:**
1. 앱 시작 시 CSV 파일 로드 ([app/main.py:17-24](app/main.py#L17-L24))
2. 각 루트에 대해 25m 버퍼 내 가로등 개수 집계
3. `lighting_index` = (가로등 개수 / km) / 50 (정규화)

**코드:** [app/utils.py:148-176](app/utils.py#L148-L176)

```python
# 가로등 데이터 로딩
load_lamps_csv("/mnt/data/서울시 가로등 위치 정보.csv")

# 루트 조명 지수 계산
lighting_index, lamps_per_km = lighting_index_for_route(route_geometry)
# 예: 40개/km → index = 0.8 (매우 밝음)
```

#### 3. 키워드 커스터마이징
사용자가 선호하는 장소 유형을 지정 가능

**API 요청 예시:**
```json
{
  "params": {
    "location": "강남역",
    "distance_km": 3.0,
    "time": "night",
    "keywords": ["한강", "공원", "숲길"]
  }
}
```

### 업데이트된 파일

| 파일 | 변경 내용 |
|------|----------|
| [app/main.py](app/main.py) | 앵커 탐색 로직, 가로등 데이터 로딩, 조명지수 덮어쓰기 |
| [app/geo.py](app/geo.py) | `search_anchors()` 함수 추가 (카카오 키워드 검색) |
| [app/utils.py](app/utils.py) | `load_lamps_csv()`, `lighting_index_for_route()` 추가 |
| [app/models.py](app/models.py) | `ParsedParams`에 `keywords` 필드 추가 |

### 데이터 요구사항

**가로등 CSV 파일** (선택사항):
- 경로: `/mnt/data/서울시 가로등 위치 정보.csv`
- 필수 컬럼: `경도`, `위도` (또는 `lon`, `lat`)
- 파일이 없으면 기본값(0.5) 사용

**환경 변수 추가** (.env):
```bash
LAMPS_CSV=/mnt/data/서울시 가로등 위치 정보.csv  # 선택
```

### 성능 영향

| 항목 | 이전 | 변경 후 |
|------|------|---------|
| 루프 생성 시간 | 5-10초 | 5-15초 (앵커 검색 추가) |
| 조명 지수 | 상수 | 실제 계산 (첫 로드 +1초) |
| 루트 다양성 | 1개 시작점 | 최대 3개 앵커 |

### 이전 버전과 호환성

✅ **완전 호환**: `keywords` 필드는 선택사항
- 기존 요청: 기본 키워드 사용 (공원, 하천, 산책로, ...)
- 가로등 CSV 없음: 기본 조명 지수(0.5) 사용

### 테스트

```bash
# 시스템 검증
source runenv/bin/activate
python -c "from app.main import app; print('✓ OK')"

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

**API 테스트:**
```bash
curl -X POST http://localhost:8000/find_course \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "location": "강남역",
      "distance_km": 3.0,
      "time": "night",
      "keywords": ["공원", "한강"]
    }
  }'
```

### 향후 계획

- [ ] 가로등 CSV 자동 다운로드 스크립트
- [ ] 앵커 우선순위 알고리즘 (거리 + 인기도)
- [ ] DEM 고도 데이터 통합
- [ ] OSM 교차로/신호등 실제 집계
- [ ] 수변/공원 버퍼 overlap 계산

### 문의

문제가 발생하면 [SETUP_GUIDE_KR.md](SETUP_GUIDE_KR.md)의 트러블슈팅 섹션 참조
