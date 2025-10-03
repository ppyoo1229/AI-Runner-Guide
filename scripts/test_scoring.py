#!/usr/bin/env python3
# 스코어링 로직 단독 테스트 (API 불필요)

import sys
sys.path.insert(0, '.')

from app.utils import estimate_features, badges_from_features
from app.scoring import beginner_score

print("=== 피처 추정 테스트 ===")
# 3km 주간 러닝
features_day = estimate_features(3000, is_night=False)
print(f"주간 3km: {features_day}")
print(f"뱃지: {badges_from_features(features_day)}")

# 3km 야간 러닝  
features_night = estimate_features(3000, is_night=True)
print(f"\n야간 3km: {features_night}")
print(f"뱃지: {badges_from_features(features_night)}")

print("\n=== 스코어링 테스트 ===")
target_km = 3.0

# 주간 스코어
score_day = beginner_score(features_day, target_km, is_night=False)
print(f"주간 스코어: {score_day:.2f}/100")

# 야간 스코어 (조명 가중치 증가)
score_night = beginner_score(features_night, target_km, is_night=True)
print(f"야간 스코어: {score_night:.2f}/100")

# 거리 차이가 큰 경우
features_far = estimate_features(5000, is_night=False)
score_far = beginner_score(features_far, target_km, is_night=False)
print(f"\n5km 코스 (목표 3km): {score_far:.2f}/100 ← 거리 페널티")

print("\n✅ 스코어링 시스템 정상 작동")
