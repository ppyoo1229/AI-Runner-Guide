# Pydantic models placeholder
from pydantic import BaseModel
from typing import Optional, List, Dict

class LatLng(BaseModel):
    lat: float
    lng: float
    place_id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None

class ParseRequest(BaseModel):
    text: str

class ParsedParams(BaseModel):
    location: Optional[str] = None
    distance_km: Optional[float] = None
    time: Optional[str] = None
    keywords: Optional[List[str]] = None 

class FindCourseRequest(BaseModel):
    params: Optional[ParsedParams] = None
    text: Optional[str] = None  # 자연어 쿼리 (params 대신 사용 가능)

class RouteItem(BaseModel):
    route_id: str
    name: str
    start: LatLng
    polyline: str
    features: Dict
    scores: Dict[str, float]
    badges: List[str]

class FindCourseResponse(BaseModel):
    routes: List[RouteItem]
