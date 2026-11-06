"""지구 텍스처용 원본 데이터 만들기: Natural Earth 1:50m (퍼블릭 도메인) → earth_data.py.

Natural Earth: "All versions of Natural Earth raster + vector map data found on this website are in the
public domain." (https://www.naturalearthdata.com/about/terms-of-use/, 2026-11-01 확인)
GeoJSON은 Natural Earth 공식 저장소 nvkelso/natural-earth-vector (LICENSE.md: "Everything here is public domain.")

시스템 파이썬으로 한 번 실행한다 (네트워크 필요, Blender 불필요):
    python3 art/blender/space/earth_data_build.py            # 내려받기 → earth_data.py 다시 쓰기
    python3 art/blender/space/earth_data_build.py <폴더>      # 이미 받아 둔 GeoJSON 폴더를 쓰기

가공: 더글러스-포커 단순화(0.06°), 작은 섬·호수 버림, 좌표를 0.02° 정수로 양자화해
int16 차분 + base64로 저장한다. 텍스처 픽셀(2048 폭 = 0.18°/px)보다 충분히 곱다.
"""
from __future__ import annotations

import base64
import json
import math
import os
import struct
import sys
import tempfile
import urllib.request

BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
LAYERS = {
    "land": "ne_50m_land.geojson",
    "lakes": "ne_50m_lakes.geojson",
    "ice": "ne_50m_glaciated_areas.geojson",
    "shelves": "ne_50m_antarctic_ice_shelves_polys.geojson",
    "regions": "ne_50m_geography_regions_polys.geojson",
    "places": "ne_50m_populated_places_simple.geojson",
}
Q = 50                   # 1° = 50 단위 (0.02°)
EPS = 0.06               # 단순화 허용 오차 (°)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "earth_data.py")


def fetch(folder):
    os.makedirs(folder, exist_ok=True)
    for fn in LAYERS.values():
        p = os.path.join(folder, fn)
        if not os.path.exists(p):
            print("download", fn)
            urllib.request.urlretrieve(BASE + fn, p)
    return folder


def rings_of(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return list(c)
    if t == "MultiPolygon":
        return [r for poly in c for r in poly]
    return []


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-12
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / L if L > 1e-9 else math.hypot(px - ax, py - ay)
            if d > best:
                best, bi = d, i
        if best > eps and bi > 0:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1))) / 2


def encode(r):
    q = [(round(x * Q), round(y * Q)) for x, y in r]
    out = [q[0]]
    for a, b in zip(q, q[1:]):
        if a != b:
            out.append(b)
    buf = struct.pack("<hh", *out[0])
    for a, b in zip(out, out[1:]):
        buf += struct.pack("<hh", b[0] - a[0], b[1] - a[1])
    return base64.b64encode(buf).decode("ascii")


def layer(path, *, min_area=0.0, eps=EPS, pred=None):
    d = json.load(open(path, encoding="utf-8"))
    out, npts = [], 0
    for ft in d["features"]:
        if pred and not pred(ft["properties"]):
            continue
        for r in rings_of(ft["geometry"]):
            if area(r) < min_area:
                continue
            # 닫힌 고리를 반으로 나눠 단순화 (시작점이 고정되도록)
            h = len(r) // 2
            s = rdp(r[: h + 1], eps)[:-1] + rdp(r[h:], eps)
            if len(s) < 4:
                continue
            out.append(encode(s))
            npts += len(s)
    return out, npts


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else fetch(os.path.join(tempfile.gettempdir(), "combatium_ne50m"))
    P = lambda k: os.path.join(folder, LAYERS[k])  # noqa: E731
    land, n1 = layer(P("land"), min_area=0.04)
    lakes, n2 = layer(P("lakes"), min_area=0.25)
    ice, n3 = layer(P("ice"), min_area=0.08)
    shelves, n4 = layer(P("shelves"), min_area=0.3)
    desert, n5 = layer(P("regions"), min_area=0.3, eps=0.12,
                       pred=lambda p: (p.get("FEATURECLA") or p.get("featurecla")) == "Desert")
    pl = json.load(open(P("places"), encoding="utf-8"))
    cities = sorted(((round(f["properties"]["longitude"], 2), round(f["properties"]["latitude"], 2),
                      int(f["properties"].get("pop_max") or 0)) for f in pl["features"]), key=lambda c: -c[2])[:900]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write('"""지구 텍스처 원본 데이터 (자동 생성, 직접 고치지 않는다: earth_data_build.py로 다시 만든다).\n\n')
        fh.write("출처: Natural Earth 1:50m (퍼블릭 도메인, https://www.naturalearthdata.com/about/terms-of-use/)\n")
        fh.write("  land = ne_50m_land, lakes = ne_50m_lakes, ice = ne_50m_glaciated_areas,\n")
        fh.write("  shelves = ne_50m_antarctic_ice_shelves_polys, desert = ne_50m_geography_regions_polys(Desert),\n")
        fh.write("  cities = ne_50m_populated_places_simple (경도, 위도, pop_max) 인구 상위 900곳\n")
        fh.write(f"고리 = base64(int16 LE: 첫 점 (경도·{Q}, 위도·{Q}), 이후 차분). 단순화 {EPS}°.\n")
        fh.write('"""\n')
        fh.write(f"Q = {Q}\n")
        for name, data in (("LAND", land), ("LAKES", lakes), ("ICE", ice), ("SHELVES", shelves),
                           ("DESERT", desert)):
            fh.write(f"{name} = [\n")
            for s in data:
                fh.write(f'    "{s}",\n')
            fh.write("]\n")
        fh.write("CITIES = [\n")
        for i in range(0, len(cities), 6):
            fh.write("    " + " ".join(f"({x}, {y}, {p})," for x, y, p in cities[i:i + 6]) + "\n")
        fh.write("]\n")
    print(f"land {len(land)} rings/{n1} pts, lakes {len(lakes)}/{n2}, ice {len(ice)}/{n3}, "
          f"shelves {len(shelves)}/{n4}, desert {len(desert)}/{n5}, cities {len(cities)}")
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
