# Testing Guide

## ✅ 테스트 체크리스트

### 1. 모듈 임포트 테스트
```bash
source runenv/bin/activate
python -c "from app.models import LatLng; print('✓ models')"
python -c "from app.scoring import beginner_score; print('✓ scoring')"
python -c "from app.utils import estimate_features; print('✓ utils')"
python -c "from app.routegen import generate_loop_candidates; print('✓ routegen')"
python -c "from app.geo import geocode_location; print('✓ geo')"
```

### 2. 스코어링 로직 테스트 (API 불필요)
```bash
source runenv/bin/activate
python scripts/test_scoring.py
```

**Expected output:**
```
주간 스코어: 100.00/100
야간 스코어: 100.00/100
5km 코스 (목표 3km): 52.00/100 ← 거리 페널티
✅ 스코어링 시스템 정상 작동
```

### 3. 지오코딩 테스트 (Kakao API 필요)
```bash
source runenv/bin/activate
PYTHONPATH=. python scripts/test_geocode.py
```

**Expected output:**
```python
LatLng(lat=37.498, lng=127.027, name='강남역', ...)
```

**가능한 에러:**
- `403 Forbidden`: Kakao API 키 만료/잘못됨 → `.env` 파일 확인
- `ModuleNotFoundError: app`: `PYTHONPATH=.` 추가 필요

### 4. 루프 생성 테스트 (OSMnx + Kakao API)
```bash
source runenv/bin/activate
PYTHONPATH=. python scripts/test_loop.py
```

**Expected output:**
```
[geocode] LatLng(lat=37.498, lng=127.027, ...)
[routegen] center=(37.498, 127.027) R=2000 target=3.0km tol=0.10
cand#1 length_m=2750.5
cand#2 length_m=3100.2
cand#3 length_m=2950.8
...
```

**가능한 에러:**
- `❌ 후보 없음`: `.env`에서 `DEFAULT_RADIUS_M=2500` 또는 `3000`으로 증가
- OSMnx 다운로드 느림: 첫 실행시 정상 (캐시됨)

### 5. FastAPI 서버 테스트
```bash
source runenv/bin/activate
uvicorn app.main:app --reload --port 8000
```

브라우저에서 http://localhost:8000/docs 접속 → Swagger UI 확인

**API 테스트 (curl):**
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

### 6. 시각화 테스트
1. `/find_course` 응답을 `response.json`에 저장
2. `scripts/quick_map.py`의 8번 줄에 응답 붙여넣기
3. 실행:
```bash
source runenv/bin/activate
PYTHONPATH=. python scripts/quick_map.py
```
4. `quick_map.html` 브라우저에서 확인

## 🐛 트러블슈팅

### Kakao API 403 에러
1. [Kakao Developers Console](https://developers.kakao.com/) 접속
2. 내 애플리케이션 → 앱 키 → REST API 키 복사
3. `.env` 파일 업데이트:
   ```
   KAKAO_REST_API_KEY=새로운_키
   ```

### OSMnx 후보 없음
```bash
# .env 파일 수정
DEFAULT_RADIUS_M=3000  # 2000 → 3000으로 증가
LOOP_TOLERANCE=0.15    # 0.10 → 0.15로 증가 (±15%)
```

### PYTHONPATH 에러
옵션 1: 매번 `PYTHONPATH=.` 추가
```bash
PYTHONPATH=. python scripts/test_geocode.py
```

옵션 2: 패키지로 설치 (권장)
```bash
# setup.py 생성 후
pip install -e .
```

### Import 에러
```bash
# 가상환경 활성화 확인
source runenv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

## 📊 성능 벤치마크

| 테스트 | 예상 시간 | 비고 |
|--------|----------|------|
| 모듈 임포트 | < 1초 | |
| 스코어링 로직 | < 0.1초 | API 불필요 |
| 지오코딩 | 0.5-2초 | Kakao API 호출 |
| 루프 생성 | 5-15초 | OSMnx 첫 로드시 느림 |
| /find_course | 10-20초 | 지오코딩 + 루프 생성 |

## 🎯 CI/CD 체크리스트

- [ ] `scripts/test_scoring.py` 통과 (API 불필요)
- [ ] 모든 모듈 임포트 성공
- [ ] Python 3.10+ 호환성
- [ ] `requirements.txt` 최신 버전
- [ ] `.env.example` 파일 제공 (키 제외)
- [ ] README.md 최신 상태

## 📝 테스트 결과 예시

```
✅ test_scoring.py: PASSED
✅ imports: PASSED
⚠️  test_geocode.py: SKIPPED (API key required)
⚠️  test_loop.py: SKIPPED (API key required)
```
