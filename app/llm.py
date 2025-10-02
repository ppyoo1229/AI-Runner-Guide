# LLM interaction stubs
from app.models import ParsedParams

def parse_running_query(text: str) -> ParsedParams:
    # TODO: Implement LLM parsing
    return ParsedParams(location="서울숲", distance_km=3.0, time="day")

def explain_route(route_data: dict) -> str:
    # TODO: Implement route explanation
    return "This is a beginner-friendly running route."
