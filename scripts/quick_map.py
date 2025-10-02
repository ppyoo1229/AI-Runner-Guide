# scripts/quick_map.py
import json, webbrowser
import folium, polyline

# 1) 위에서 받은 /find_course 응답을 여기에 붙이거나 파일에서 읽기
# 예: response_json = json.load(open("response.json","r",encoding="utf-8"))
# 여기서는 간단히 수동으로 붙였다고 가정
response_json = {
  # ... 실제 응답 붙이기 ...
}

routes = response_json["routes"]
# 중심은 첫 코스 시작점
c0 = routes[0]["start"]
m = folium.Map(location=[c0["lat"], c0["lng"]], zoom_start=14)

for i, r in enumerate(routes, start=1):
    coords = polyline.decode(r["polyline"])
    folium.PolyLine(coords, weight=5, opacity=0.8, tooltip=f"{i}) {r['name']}").add_to(m)
    folium.Marker([c0["lat"], c0["lng"]], popup=f"Start: {c0.get('name','Start')}").add_to(m)

out = "quick_map.html"
m.save(out)
print(f"saved: {out}")
webbrowser.open(out)
