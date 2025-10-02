# scripts/test_loop.py
# 루프만 단독 테스트

import asyncio, os
from dotenv import load_dotenv
load_dotenv()

from app.geo import geocode_location
from app.routegen import generate_loop_candidates

async def main():
    start = await geocode_location("강남역")
    print("[geocode]", start)
    cands = generate_loop_candidates(start)
    for i, c in enumerate(cands):
        print(f"cand#{i+1} length_m={c['length_m']:.1f}")
    if not cands:
        print("❌ 후보 없음: .env의 DEFAULT_RADIUS_M를 2500~3000으로 올려보세요.")

if __name__ == "__main__":
    asyncio.run(main())

'''
length_m ~ 3000m 후보가 1개 이상 나오면 통과
없으면 .env에서 DEFAULT_RADIUS_M=2500 또는 3000으로 올리고 재시도
'''