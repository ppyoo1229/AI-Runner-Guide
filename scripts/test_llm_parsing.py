#!/usr/bin/env python3
# LLM 파싱 통합 테스트

import sys
sys.path.insert(0, '.')

from app.llm import parse_running_query, _infer_time, _to_km_from_text, _fallback_keywords
from app.models import FindCourseRequest, ParsedParams

print("=== LLM 파싱 규칙 기반 테스트 (LLM 서버 불필요) ===\n")

# LLM 서버 없이도 작동하는 fallback 함수 테스트
text1 = "강남역 근처에서 3km 야간 러닝"
print(f"입력: {text1}")
print(f"  - 시간 추론: {_infer_time(text1)}")
print(f"  - 거리 추출: {_to_km_from_text(text1)}km")
print(f"  - 키워드: {_fallback_keywords(text1)}\n")

text2 = "한강공원에서 30분 코스"
print(f"입력: {text2}")
print(f"  - 시간 추론: {_infer_time(text2)}")
print(f"  - 거리 추출: {_to_km_from_text(text2)}km (30분 ÷ 9분/km)")
print(f"  - 키워드: {_fallback_keywords(text2)}\n")

print("=== LLM 파싱 전체 테스트 (fallback 모드) ===\n")
try:
    # LLM 서버 없으면 자동으로 fallback 사용
    parsed = parse_running_query(text1)
    print(f"✅ Fallback 파싱 성공:")
    print(f"  - location: {parsed.location}")
    print(f"  - distance_km: {parsed.distance_km}")
    print(f"  - time: {parsed.time}")
    print(f"  - keywords: {parsed.keywords}\n")
except Exception as e:
    print(f"⚠️  에러: {e}\n")

print("=== FindCourseRequest 모델 테스트 ===\n")

# 방법 1: text 사용 (자연어 - /find_course에서 자동 파싱)
req1 = FindCourseRequest(text="강남역 근처 3km 공원 루트")
print(f"✅ 방법 1 - text 필드:")
print(f"   {req1.text}")

# 방법 2: params 사용 (구조화된 데이터)
params = ParsedParams(location="강남역", distance_km=3.0, time="night", keywords=["공원","하천"])
req2 = FindCourseRequest(params=params)
print(f"\n✅ 방법 2 - params 필드:")
print(f"   location={req2.params.location}, time={req2.params.time}")

print("\n" + "="*60)
print("🎉 LLM 파싱 통합 완료!")
print("="*60)
print("\n📌 주요 기능:")
print("  1. /parse 엔드포인트: 자연어 → ParsedParams")
print("  2. /find_course 엔드포인트:")
print("     - 'text' 전달 시 → 자동으로 LLM 파싱")
print("     - 'params' 전달 시 → 파싱 없이 바로 사용")
print("\n📌 Fallback 메커니즘:")
print("  - LLM 서버 없으면 규칙 기반 파싱 사용")
print("  - 시간: '밤/야간/저녁' → night, '낮/아침' → day")
print("  - 거리: 정규식으로 km/분 추출")
print("  - 키워드: 기본값 ['공원','하천','산책로','운동장','트랙']")
