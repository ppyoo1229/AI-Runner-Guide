# 설치 및 실행 가이드 (한국어)

## ✅ 해결됨: 패키지 설치 완료

`pip install -e .` 실행으로 **어디서든** 스크립트 실행 가능:

```bash
# scripts/ 디렉토리에서도 실행 가능
cd scripts/
python test_geocode.py  # ✅ PYTHONPATH 불필요
```

## 🔑 카카오 API 키 설정 (필수)

현재 `.env`의 API 키가 만료되어 403 에러 발생 중입니다.

### 1. 카카오 개발자 계정 생성
https://developers.kakao.com/

### 2. 애플리케이션 등록
1. "내 애플리케이션" 클릭
2. "애플리케이션 추가하기"
3. 앱 이름 입력 (예: "러닝코스추천")

### 3. REST API 키 복사
1. 생성한 앱 클릭
2. "앱 키" 탭에서 **REST API 키** 복사
3. `.env` 파일 업데이트:

```bash
KAKAO_REST_API_KEY=여기에_새_키_붙여넣기
TARGET_DISTANCE_KM=3.0
LOOP_TOLERANCE=0.10
DEFAULT_RADIUS_M=2000
```

### 4. 플랫폼 설정 (선택)
- "플랫폼" 탭 → "Web 플랫폼 등록" → `http://localhost:8000` 추가

## 🧪 테스트

### 1. API 없이 테스트 (바로 가능)
```bash
source runenv/bin/activate
python scripts/test_scoring.py
```

**출력 예시:**
```
주간 스코어: 100.00/100
야간 스코어: 100.00/100
5km 코스 (목표 3km): 52.00/100 ← 거리 페널티
✅ 스코어링 시스템 정상 작동
```

### 2. 지오코딩 테스트 (API 키 필요)
```bash
python scripts/test_geocode.py
```

**성공 시 출력:**
```python
LatLng(
    lat=37.49794338310295, 
    lng=127.02768515763585,
    place_id='11561968',
    name='강남역',
    address='서울 강남구 역삼동 735'
)
```

### 3. 루프 생성 테스트 (API 키 + OSMnx)
```bash
python scripts/test_loop.py
```

**성공 시 출력:**
```
[geocode] LatLng(lat=37.498, lng=127.027, ...)
[routegen] center=(37.498,127.027) R=2000 target=3.0km tol=0.10
cand#1 length_m=2750.5
cand#2 length_m=3100.2
cand#3 length_m=2950.8
...
```

**주의:** 첫 실행시 OSMnx가 서울 도로망 다운로드 (30초~1분 소요)

### 4. FastAPI 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```

브라우저에서 http://localhost:8000/docs 접속

## 📡 API 사용 예시

### curl 테스트
```bash
curl -X POST http://localhost:8000/find_course \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "location": "강남역",
      "distance_km": 3.0,
      "time": "day"
    }
  }'
```

### Python 테스트
```python
import httpx

response = httpx.post("http://localhost:8000/find_course", json={
    "params": {
        "location": "강남역",
        "distance_km": 3.0,
        "time": "night"  # 야간 → 조명 가중치 증가
    }
})

routes = response.json()["routes"]
for route in routes:
    print(f"{route['name']}: {route['scores']['beginner']:.1f}점")
    print(f"배지: {', '.join(route['badges'])}")
```

## 🐛 문제 해결

### ImportError: No module named 'app'
```bash
# pip install -e . 완료
# 재설치 필요시:
pip install -e .
```

### 403 Forbidden (카카오 API)
- `.env` 파일에서 `KAKAO_REST_API_KEY` 확인
- 키가 유효한지 확인 (카카오 개발자 콘솔)
- 플랫폼 설정 확인

### OSMnx 후보 없음
```bash
# .env 파일 수정
DEFAULT_RADIUS_M=3000  # 2000 → 3000으로 증가
LOOP_TOLERANCE=0.15    # 0.10 → 0.15로 증가
```

### 느린 응답 속도
- 첫 실행: OSMnx 캐시 생성 중 (정상)
- 이후 실행: 캐시 사용으로 빠름

## 📂 프로젝트 구조

```
running-recsys/
├── app/                # 메인 애플리케이션
│   ├── main.py        # FastAPI 엔드포인트
│   ├── models.py      # 데이터 모델
│   ├── geo.py         # 카카오 지오코딩
│   ├── routegen.py    # OSMnx 루프 생성
│   ├── scoring.py     # 스코어링
│   └── utils.py       # 유틸리티
├── scripts/           # 테스트 스크립트
│   ├── test_scoring.py   # ✅ API 불필요
│   ├── test_geocode.py   # 카카오 API 필요
│   └── test_loop.py      # 카카오 + OSMnx
├── .env               # 환경 변수 (API 키)
├── setup.py           # 패키지 설정
└── README.md          # 영문 문서
```

## 🎯 다음 단계

1. ✅ 패키지 설치 완료
2. ⏳ 카카오 API 키 발급 ← **지금 여기**
3. 테스트 실행
4. 서버 실행
5. 프론트엔드 연동 또는 추가 기능 개발

## 💡 팁

**개발 모드로 설치했으므로:**
- 코드 수정 시 자동 반영 (재설치 불필요)
- 어디서든 `from app.xxx import yyy` 가능
- `uvicorn --reload`로 서버 자동 재시작

**API 키 없이 개발하려면:**
- `test_scoring.py` 사용 (스코어링 로직만 테스트)
- `app/geo.py`의 `geocode_location`을 mock으로 대체
- `app/routegen.py`에 하드코딩된 좌표 사용

