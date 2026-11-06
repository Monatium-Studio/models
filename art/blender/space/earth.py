"""툰 화풍 지구 (프롤로그 오프닝 1·2, 엔딩 피격 장면의 배경 행성).

[원작] 엘프들은 '50개 별의 가호를 받는 왕국'(미국)을 가장 먼저 공격했다. 목표인 북미가 오프닝에서 보인다.
[오리지널] 툰 행성 표현
  - 대륙·호수·빙하·사막 윤곽: Natural Earth 1:50m (퍼블릭 도메인) → earth_data.py (earth_data_build.py로 생성)
  - 평탄한 색 면 + 해안 먹선(짙은 남청) + 얕은 바다 띠, 위도·내륙 거리로 나눈 툰 식생 띠(열대·초원·건조·침엽·툰드라)
  - 구름: 구면 3D 값 노이즈를 문턱으로 자른 두 단 구름 (흰 + 연한 그림자 테)
  - 낮과 밤: 고정된 태양 방향으로 툰 3단 + 노을 띠 + 밤 면(남색, 도시 불빛)을 텍스처에 굽는다.
    지구 머티리얼은 UNLIT이다(엔진 툰 조명은 밤 면을 0.5 밝기로 남기므로 밤이 안 생김).
  - 대기 테: 안쪽을 보는 구 껍질 2겹(UNLIT 반투명, 단면 컬링). 바깥에서 보면 지구 둘레에만 고리로 보인다.
    면마다 태양 쪽은 밝은 하늘색, 노을 띠는 분홍, 밤 쪽은 짙은 파랑 (정점색).

로컬 좌표: +Z = 북극, 그리니치 = -Y, 동경 90° = +X (space_kit.uv_sphere). 반지름 100 m.
태양(구운 낮 방향): 북위 12°, 서경 128° (태평양 동부). 북미 중부는 오후 2시쯤이고, 대서양에 낮밤 경계가 있다.
루트 속성 sunLocal = 로컬(Blender) 태양 방향, radius = 100. 장면은 이 방향을 회전해 레벨 sun과 맞춘다.

npm run model -- art/blender/space/earth.py
npm run shot -- space/earth.glb --views front,34,side,top
"""
import base64
import math
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import space_kit as sk  # noqa: E402
import earth_data as ED  # noqa: E402
from mathutils import Vector  # noqa: E402

RADIUS = 100.0
SUN_LAT, SUN_LON = 12.0, -128.0
W, H = 2048, 1024
SS = 2                  # 2배 해상도로 합성 후 축소 (안티에일리어싱)
TEX_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "combatium_space_tex")

PAL = {
    "ocean": (0x2f, 0x6c, 0xb4),
    "ocean_deep": (0x2a, 0x5e, 0xa6),
    "shelf": (0x58, 0x9e, 0xd2),
    "coast": (0x1f, 0x3c, 0x6c),
    "lake": (0x5c, 0xa4, 0xd6),
    "grass": (0x86, 0xb8, 0x6a),
    "forest": (0x5f, 0x9b, 0x5a),
    "jungle": (0x4c, 0x8c, 0x52),
    "dry": (0xc9, 0xc0, 0x80),
    "desert": (0xe6, 0xcc, 0x92),
    "tundra": (0xa9, 0xb5, 0x96),
    "ice": (0xf1, 0xf5, 0xf7),
    "cloud": (0xfb, 0xfd, 0xff),
    "cloud_sh": (0xcf, 0xdc, 0xec),
    "night": (0x12, 0x1b, 0x3a),
    "dusk": (0xff, 0x9a, 0x7a),
    "city": (0xff, 0xd8, 0x86),
    "city_hot": (0xff, 0xf6, 0xd8),
}


def C(k):
    return np.array(PAL[k], dtype=np.float32) / 255.0


def lonlat_grid(w, h):
    lon = (np.arange(w, dtype=np.float32) + 0.5) / w * 360.0 - 180.0
    lat = 90.0 - (np.arange(h, dtype=np.float32) + 0.5) / h * 180.0
    return np.meshgrid(lon, lat)


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.sin(lo), -np.cos(la) * np.cos(lo), np.sin(la)], axis=-1)


# ------------------------------------------------------------------ 다각형 → 마스크 (짝홀 스캔라인)

def decode(s):
    b = base64.b64decode(s)
    n = len(b) // 4
    vals = struct.unpack("<" + "h" * (2 * n), b)
    x, y = vals[0], vals[1]
    pts = [(x, y)]
    for i in range(1, n):
        x += vals[2 * i]
        y += vals[2 * i + 1]
        pts.append((x, y))
    a = np.array(pts, dtype=np.float64) / ED.Q
    if not np.allclose(a[0], a[-1]):
        a = np.vstack([a, a[:1]])
    return a


def raster(rings, w, h):
    """경위도 고리 목록 → (h, w) bool 마스크 (짝홀 규칙: 구멍도 처리)."""
    rows_all, xs_all = [], []
    for s in rings:
        a = decode(s)
        x = (a[:, 0] + 180.0) / 360.0 * w
        y = (90.0 - a[:, 1]) / 180.0 * h
        x0, y0, x1, y1 = x[:-1], y[:-1], x[1:], y[1:]
        lo, hi = np.minimum(y0, y1), np.maximum(y0, y1)
        j0 = np.ceil(lo - 0.5).astype(np.int64)
        j1 = np.ceil(hi - 0.5).astype(np.int64)        # 반열린 [j0, j1)
        cnt = np.clip(j1 - j0, 0, None)
        if cnt.sum() == 0:
            continue
        e = np.repeat(np.arange(len(cnt)), cnt)
        off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        j = j0[e] + off
        yc = j + 0.5
        t = (yc - y0[e]) / (y1[e] - y0[e])
        xc = x0[e] + t * (x1[e] - x0[e])
        rows_all.append(j)
        xs_all.append(xc)
    m = np.zeros((h, w), dtype=bool)
    if not rows_all:
        return m
    rows = np.concatenate(rows_all)
    xs = np.concatenate(xs_all)
    ok = (rows >= 0) & (rows < h)
    rows, xs = rows[ok], xs[ok]
    order = np.lexsort((xs, rows))
    rows, xs = rows[order], xs[order]
    # 같은 행 안에서 짝을 지어 채운다
    diff = np.zeros((h, w + 1), dtype=np.int32)
    start = np.r_[0, np.flatnonzero(np.diff(rows)) + 1]
    for k, st0 in enumerate(start):
        en = start[k + 1] if k + 1 < len(start) else len(rows)
        r = rows[st0]
        xr = xs[st0:en]
        for a_, b_ in zip(xr[0::2], xr[1::2]):
            i0 = int(max(0, math.ceil(a_ - 0.5)))
            i1 = int(min(w, math.ceil(b_ - 0.5)))
            if i1 > i0:
                diff[r, i0] += 1
                diff[r, i1] -= 1
    return np.cumsum(diff, axis=1)[:, :w] > 0


def coverage(rings):
    """현재 합성 해상도(W, H)의 마스크 → 0/1 (안티에일리어싱은 bake_texture의 축소가 맡는다)."""
    return raster(rings, W, H).astype(np.float32)


def dilate(m, r):
    """이진 팽창 (경도는 감싸고 위도는 막음)."""
    out = m.copy()
    for _ in range(r):
        n = out.copy()
        n[1:] |= out[:-1]
        n[:-1] |= out[1:]
        n |= np.roll(out, 1, axis=1)
        n |= np.roll(out, -1, axis=1)
        out = n
    return out


def blur(a, r):
    """상자 흐림 r회 (경도 감쌈)."""
    out = a.astype(np.float32)
    for _ in range(r):
        out = (out + np.roll(out, 1, 1) + np.roll(out, -1, 1)) / 3.0
        p = np.pad(out, ((1, 1), (0, 0)), mode="edge")
        out = (p[:-2] + p[1:-1] + p[2:]) / 3.0
    return out


# ------------------------------------------------------------------ 구면 값 노이즈

class Noise3:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.perm = np.concatenate([rng.permutation(256)] * 2).astype(np.int64)
        self.val = rng.random(256).astype(np.float32)

    def _h(self, i, j, k):
        p = self.perm
        return self.val[p[(p[(p[i & 255] + j) & 255] + k) & 255]]

    def __call__(self, P):
        F = np.floor(P)
        I = F.astype(np.int64)
        f = P - F
        u = f * f * (3 - 2 * f)
        out = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    wgt = ((u[..., 0] if dx else 1 - u[..., 0]) * (u[..., 1] if dy else 1 - u[..., 1])
                           * (u[..., 2] if dz else 1 - u[..., 2]))
                    out = out + wgt * self._h(I[..., 0] + dx, I[..., 1] + dy, I[..., 2] + dz)
        return out

    def fbm(self, P, octaves=5, lac=2.03, gain=0.5):
        a, s, tot = 1.0, 0.0, 0.0
        for o in range(octaves):
            s = s + a * self(P * (lac ** o) + o * 17.3)
            tot += a
            a *= gain
        return s / tot


# ------------------------------------------------------------------ 텍스처 굽기

def bake_texture(sun_lat=SUN_LAT, sun_lon=SUN_LON):
    """W×H 텍스처를 SS배 해상도로 합성한 뒤 평균으로 줄인다 (해안선·구름 경계 안티에일리어싱)."""
    global W, H
    W0, H0 = W, H
    W, H = W0 * SS, H0 * SS
    try:
        rgb, sun = _bake(sun_lat, sun_lon)
    finally:
        W, H = W0, H0
    small = rgb.astype(np.float32).reshape(H0, SS, W0, SS, 3).mean(axis=(1, 3))
    return np.clip(small + 0.5, 0, 255).astype(np.uint8), sun


def _bake(sun_lat, sun_lon):
    lon, lat = lonlat_grid(W, H)
    N = unit(lon, lat)
    sun = unit(np.float32(sun_lon), np.float32(sun_lat))
    d = (N * sun).sum(-1)
    print("[earth] rasterizing coastlines…")
    land_c = coverage(ED.LAND)
    lake_c = coverage(ED.LAKES)
    ice_c = np.maximum(coverage(ED.ICE), coverage(ED.SHELVES))
    des_c = coverage(ED.DESERT)
    land = land_c > 0.5
    noise = Noise3(7)
    wob = noise.fbm(N * 6.0, 3) - 0.5                     # 경계 흔들기 (곧은 위도선 방지)

    # 내륙 거리 (바다에서 몇 픽셀)
    sea = ~land
    inland = np.zeros((H, W), dtype=np.float32)
    grown = sea.copy()
    for k in range(1, 26):
        grown = dilate(grown, SS)
        inland[(inland == 0) & land & grown] = k
    inland[(inland == 0) & land] = 26

    # 식생 띠
    alat = np.abs(lat) + wob * 9.0
    col = np.empty((H, W, 3), dtype=np.float32)
    col[:] = C("grass")
    col[(alat < 13)] = C("jungle")
    dryband = (alat > 14) & (alat < 34) & (inland > 9 + wob * 10)
    col[dryband] = C("dry")
    col[(lat + wob * 8 > 47) & (lat + wob * 8 < 62)] = C("forest")
    col[(lat + wob * 6 > 62)] = C("tundra")
    desert = blur(des_c, 2 * SS) > 0.35
    col[desert] = C("desert")
    icemask = (ice_c > 0.5) | (lat < -62)
    col[icemask] = C("ice")

    # 바다: 깊은 바다(위도 노이즈) + 얕은 띠 + 해안선
    sea_col = np.empty_like(col)
    sea_col[:] = C("ocean")
    sea_col[noise.fbm(N * 3.0, 3) > 0.58] = C("ocean_deep")
    near = dilate(land, 5 * SS) & sea
    sea_col[near] = C("shelf")
    coastline = dilate(land, SS) & sea
    sea_col[coastline] = C("coast")
    a = np.clip((land_c - 0.25) / 0.5, 0, 1)[..., None]
    rgb = sea_col * (1 - a) + col * a
    # 호수 (호수 둘레 먹선)
    lk = lake_c > 0.5
    rgb[lk] = C("lake")
    rgb[dilate(lk, SS) & ~lk & land] = C("coast")

    # 구름 (북미 위는 덜: 목표가 보이도록)
    print("[earth] clouds…")
    # 위도 방향으로 눌러 동서로 길쭉하게 + 도메인 왜곡으로 소용돌이
    Pz = N * np.array([1.0, 1.0, 2.3], dtype=np.float32)
    warp = np.stack([noise.fbm(Pz * 1.7 + o, 3) - 0.5 for o in (11.0, 23.0, 37.0)], axis=-1)
    Pw = Pz + warp * 0.9
    cn = noise.fbm(Pw * 2.4 + 3.1, 5) * 0.72 + noise.fbm(Pw * 8.0 - 1.7, 3) * 0.28
    band = (0.08 * np.cos(np.radians(lat - 6) * 4.5) + 0.06 * np.exp(-((np.abs(lat) - 52) / 12) ** 2)
            - 0.05 * np.exp(-((np.abs(lat) - 25) / 8) ** 2))
    us = np.exp(-(((lon + 98) / 22) ** 2 + ((lat - 40) / 12) ** 2))
    polar = np.clip((np.abs(lat) - 70.0) / 12.0, 0, 1)        # 극점 UV 꼬임이 보이지 않게 극 구름을 걷음
    cv = cn + band - 0.10 * us - 0.25 * polar
    cloud_hi = cv > 0.63
    cloud_lo = (cv > 0.585) & ~cloud_hi
    rgb[cloud_lo] = C("cloud_sh")
    rgb[cloud_hi] = C("cloud")

    # 조명 굽기: 낮(1.0) / 중간(0.86, 살짝 푸르게) / 노을 띠 / 밤
    print("[earth] lighting…")
    dd = d + wob * 0.02
    mid = (dd <= 0.40) & (dd > 0.07)
    rgb[mid] = rgb[mid] * np.array([0.84, 0.87, 0.93], dtype=np.float32)
    dusk = (dd <= 0.07) & (dd > -0.05)
    rgb[dusk] = rgb[dusk] * 0.62 + C("dusk") * 0.22
    night = dd <= -0.05
    lum = rgb[night].mean(-1, keepdims=True)
    rgb[night] = C("night") + lum * np.array([0.10, 0.12, 0.20], dtype=np.float32)

    # 도시 불빛 (밤 면 육지)
    print("[earth] city lights…")
    rng = np.random.default_rng(3)
    for (clon, clat, pop) in ED.CITIES:
        if pop < 150000:
            continue
        r = (0.6 + 0.55 * math.log10(max(pop, 1) / 150000.0 + 1.0) * 2.0) * SS
        dots = [(clon, clat, r)]
        for _ in range(int(min(6, pop / 1.5e6))):
            dots.append((clon + rng.normal(0, 0.9) / max(math.cos(math.radians(clat)), 0.3),
                         clat + rng.normal(0, 0.7), r * 0.5))
        for (x_, y_, rr) in dots:
            px = (x_ + 180.0) / 360.0 * W
            py = (90.0 - y_) / 180.0 * H
            rx = rr / max(math.cos(math.radians(y_)), 0.25)
            i0, i1 = int(px - rx - 1), int(px + rx + 2)
            j0, j1 = max(0, int(py - rr - 1)), min(H, int(py + rr + 2))
            for jj in range(j0, j1):
                for ii in range(i0, i1):
                    iw = ii % W
                    if ((ii + 0.5 - px) / rx) ** 2 + ((jj + 0.5 - py) / rr) ** 2 <= 1.0 and night[jj, iw] \
                            and land[jj, iw] and not cloud_hi[jj, iw]:
                        rgb[jj, iw] = C("city_hot") if rr > 1.4 * SS and abs(ii + 0.5 - px) < rx * 0.4 \
                            and abs(jj + 0.5 - py) < rr * 0.4 else C("city")
    return np.clip(rgb * 255.0 + 0.5, 0, 255).astype(np.uint8), sun


# ------------------------------------------------------------------ 대기 껍질

def atmosphere(name, r, alpha, sun, cols):
    """안쪽을 보는 구 껍질 (바깥에서 보면 테두리 고리). cols = (낮, 노을, 밤) sRGB hex."""
    o = sk.uv_sphere(name, r, 36, 18, inward=True)
    me = o.data
    ca = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    S = Vector(sun)
    for p in me.polygons:
        c = p.center.normalized().dot(S)
        hexv = cols[0] if c > 0.08 else (cols[1] if c > -0.12 else cols[2])
        rgb = sk.srgb(hexv)
        for li in p.loop_indices:
            ca.data[li].color_srgb = (*rgb, 1.0)
    me.color_attributes.active_color = ca
    m = sk.vc_material(f"sk_{name}", unlit=True, alpha=alpha, double_sided=False)
    me.materials.append(m)
    o["noOutline"] = 1
    o["collider"] = 0
    return o


def build(sun_lat=SUN_LAT, sun_lon=SUN_LON, *, name="earth"):
    rgb, sun = bake_texture(sun_lat, sun_lon)
    os.makedirs(TEX_DIR, exist_ok=True)
    png = sk.save_png(os.path.join(TEX_DIR, f"{name}_toon.png"), rgb)
    print(f"[earth] texture {W}x{H} png {os.path.getsize(png) // 1024} KB")
    root = cb.empty(name, size=RADIUS * 0.2)
    ball = sk.uv_sphere(f"{name}_surface", RADIUS, 48, 24)
    ball.data.materials.append(sk.image_material(f"{name}_surface", png, unlit=True))
    ball["collider"] = 0
    ball.parent = root
    sunv = tuple(float(v) for v in sun)
    for o in (atmosphere(f"{name}_atmo_in", RADIUS * 1.026, 0.85, sunv, ("#a8ecff", "#ffb6a4", "#35508f")),
              atmosphere(f"{name}_atmo_out", RADIUS * 1.065, 0.32, sunv, ("#62b9ff", "#e58aa0", "#22346c"))):
        o.parent = root
    root["sunLocal"] = ",".join(f"{v:.5f}" for v in sunv)
    root["sunLatLon"] = f"{sun_lat},{sun_lon}"
    root["radius"] = RADIUS
    root["collider"] = 0
    root["noOutline"] = 1
    return root


if __name__ == "__main__":
    cb.reset()
    root = build()
    sk.export_glb("space/earth.glb", root=root)
