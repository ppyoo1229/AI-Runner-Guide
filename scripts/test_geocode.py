# scripts/test_geocode.py
# 단일 테스트 스크립트

import asyncio, os
from dotenv import load_dotenv
load_dotenv()

from app.geo import geocode_location

async def main():
    loc = await geocode_location("강남역")
    print(loc)

if __name__ == "__main__":
    asyncio.run(main())