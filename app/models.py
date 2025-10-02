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

class FindCourseRequest(BaseModel):
    params: ParsedParams

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
