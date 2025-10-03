# LLM 파싱 통합 가이드

## 🎯 개요

사용자의 자연어 쿼리를 구조화된 파라미터로 자동 변환하는 기능이 통합되었습니다.

## 📋 사용 방법

### 방법 1: 자연어 직접 사용 (권장)

```bash
curl -X POST http://localhost:8000/find_course \
  -H "Content-Type: application/json" \
  -d '{
    "text": "강남역 근처에서 3km 야간 러닝 코스 추천해줘"
  }'
```

**작동 방식:**
1. `/find_course`가 `text` 필드를 받음
2. 자동으로 `parse_running_query()` 호출
3. 파싱된 params로 루트 생성

### 방법 2: 구조화된 데이터 사용 (이전 방식)

```bash
curl -X POST http://localhost:8000/find_course \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "location": "강남역",
      "distance_km": 3.0,
      "time": "night",
      "keywords": ["공원", "하천"]
    }
  }'
```

### 방법 3: 파싱만 테스트

```bash
curl -X POST http://localhost:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "한강공원에서 30분 러닝"}'
```

**응답 예시:**
```json
{
  "location": null,
  "distance_km": 3.3,
  "time": null,
  "keywords": ["공원", "하천", "산책로", "운동장", "트랙"]
}
```

## 🧠 LLM 파싱 엔진

### 구성 요소

**1. LLM 기반 파싱** (우선)
- 모델: `kakaocorp/kanana-1.5-8b-instruct-2505`
- 엔드포인트: `HF_TGI_URL` (환경변수)
- 프롬프트: [app/llm.py:15-33](app/llm.py#L15-L33)

**2. 규칙 기반 Fallback** (LLM 서버 없을 때)
- 시간 추론: `_infer_time()` - "밤/야간" → `night`
- 거리 추출: `_to_km_from_text()` - 정규식으로 km/분 파싱
- 키워드: 기본값 반환

### 환경 변수 설정

```bash
# .env 파일
HF_TGI_URL=http://localhost:8080        # LLM 서버 주소 (선택)
KANANA_MODEL=kakaocorp/kanana-1.5-8b-instruct-2505
```

**LLM 서버 없이도 작동:** 규칙 기반 fallback 자동 사용

## 📊 파싱 예시

| 입력 | location | distance_km | time | keywords |
|------|----------|-------------|------|----------|
| "강남역 3km 야간 러닝" | null | 3.0 | night | [공원, 하천, ...] |
| "한강공원 30분 코스" | null | 3.3 | null | [공원, 하천, ...] |
| "서울숲에서 5-7km 아침에" | null | 6.0 | day | [공원, 하천, ...] |

**참고:** 
- LLM이 있으면 `location` 추출도 가능
- Fallback 모드에서는 `location=null` (사용자가 직접 지정 필요)

## 🔧 코드 변경사항

### 1. FindCourseRequest 모델 업데이트

**이전:**
```python
class FindCourseRequest(BaseModel):
    params: ParsedParams
```

**변경:**
```python
class FindCourseRequest(BaseModel):
    params: Optional[ParsedParams] = None
    text: Optional[str] = None  # 자연어 쿼리
```

### 2. /find_course 엔드포인트 로직

**[app/main.py:31-42](app/main.py#L31-L42)**
```python
@app.post("/find_course")
async def find_course(req: FindCourseRequest):
    # 자연어 쿼리가 있으면 먼저 파싱
    if req.text:
        log.info(f"[find_course] parsing text: {req.text}")
        p = parse_running_query(req.text)
    elif req.params:
        p = req.params
    else:
        raise HTTPException(400, "Either 'text' or 'params' is required")
    
    if not p.location:
        raise HTTPException(400, "location is required")
    ...
```

### 3. LLM 파싱 함수 개선

**[app/llm.py:101-127](app/llm.py#L101-L127)**
```python
def parse_running_query(text: str) -> ParsedParams:
    try:
        # LLM 서버 호출 시도
        out = _post_tgi({...})
    except Exception as e:
        # 연결 실패 시 규칙 기반 fallback
        logging.debug(f"LLM fallback: {e}")
        return ParsedParams(
            location=None,
            distance_km=_to_km_from_text(text),
            time=_infer_time(text),
            keywords=_fallback_keywords(text),
        )
    # JSON 파싱 및 후처리
    ...
```

## 🧪 테스트

```bash
# LLM 파싱 테스트 (fallback 포함)
source runenv/bin/activate
python scripts/test_llm_parsing.py
```

**출력:**
```
✅ Fallback 파싱 성공:
  - location: None
  - distance_km: 3.0
  - time: night
  - keywords: ['공원', '하천', '산책로', '운동장', '트랙']
```

## 🚀 실전 사용 예시

### Python 클라이언트

```python
import httpx

# 자연어 쿼리
response = httpx.post("http://localhost:8000/find_course", json={
    "text": "강남역에서 5km 저녁에 뛸 만한 곳"
})

routes = response.json()["routes"]
for route in routes:
    print(f"{route['name']}: {route['scores']['beginner']:.1f}점")
```

### 프론트엔드 (React 예시)

```javascript
const findCourses = async (userQuery) => {
  const response = await fetch('http://localhost:8000/find_course', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ text: userQuery })
  });
  
  const data = await response.json();
  return data.routes;
};

// 사용
const routes = await findCourses("한강공원 3km 야간 코스");
```

## ⚠️ 제약사항

### Fallback 모드 (LLM 서버 없을 때)
- `location` 추출 불가 → 사용자가 직접 지정 필요
- 복잡한 의도 파악 어려움
- 키워드는 기본값만 사용

### LLM 모드
- LLM 서버 필요 (`HF_TGI_URL`)
- 응답 속도: 1-3초 추가
- 모델 의존성

## 📈 향후 개선

- [ ] location 추출 개선 (NER/지명 사전)
- [ ] 문맥 기억 (대화형 인터페이스)
- [ ] 다국어 지원
- [ ] 선호도 학습 (개인화)

## 🔗 관련 파일

- [app/llm.py](app/llm.py) - LLM 파싱 로직
- [app/main.py:31-42](app/main.py#L31-L42) - /find_course 통합
- [app/models.py:21-23](app/models.py#L21-L23) - FindCourseRequest 모델
- [scripts/test_llm_parsing.py](scripts/test_llm_parsing.py) - 테스트 스크립트

## 💡 팁

**LLM 서버 설정 (선택):**
```bash
# HuggingFace TGI 실행 예시
docker run -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id kakaocorp/kanana-1.5-8b-instruct-2505
```

**없어도 됨:** Fallback이 자동으로 작동합니다!
