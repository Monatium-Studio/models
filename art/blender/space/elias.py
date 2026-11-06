"""툰 화풍 행성 엘리아스 (1막 로딩 영상 1의 궤도 첫 컷: 궤도 → 모나티엄 일대 → 도심으로 끊어 들어가는 줌의 시작).

[원작] 엘리아스는 세계수 엘드르가 가운데 선 땅이고, 숲 너머는 안개로 둘러싸여 있다. 모나티엄은 엘리아스 동부
       (정령산·에르피엔 접경)의 엘프 도시다. (docs/art/interlude-elias.md, monatium-city.md 1장)
       요정 왕국의 수도 에르피엔은 세계수를 한가운데 모시고 둘레를 두른다(이중 성벽): 궤도에서는 수관 둘레의 흰 시가 고리.
[오리지널] 엘리아스를 '행성(구)'으로 그린 것과 그 지리 전체: 큰 대륙 하나와 작은 대륙·섬, 대륙 가운데 엘드르의
       방사형 수관(궤도에서 보이는 짙은 초록 원판), 알려진 땅을 두른 옅은 안개 띠(안개 경계), 정령산 산줄기, 호수,
       숲, 구름 띠, 동부의 작은 회색 도시 얼룩 모나티엄(옅은 시안 빛무리). 실제 지구 자료는 쓰지 않는다(전부 절차 노이즈).

파이프라인은 earth.py와 같다: 반지름 100 UV 구 + 절차 텍스처를 PNG로 구움(UNLIT) + 대기 껍질 2겹.
로컬 좌표: +Z = 북극, 경도 0° = -Y, 동경 90° = +X (space_kit.uv_sphere).
태양(구운 낮 방향): 모나티엄 쪽에서 보아 앞-왼쪽(서쪽)·조금 위. 원판 오른쪽(동쪽)에 부드러운 낮밤 경계가 생긴다.

루트 속성
  radius = 100
  monatium = "x,y,z"  중심 → 모나티엄 단위 벡터, three.js 좌표 (x = bx, y = bz, z = -by)
  monatiumLocal (Blender), monatiumLatLon, eldrLatLon, eldr (three.js), hazeDeg (안개 경계 반지름, 도)
  sunLocal = 구운 태양 방향 (Blender, earth.py와 같은 규약), sunThree (three.js), sunLatLon
자식 빈 오브젝트: MARK_monatium, MARK_eldr (표면 점. 구를 돌려도 따라 돎)

npm run model -- art/blender/space/elias.py
npm run shot -- space/elias.glb --views front,34
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import space_kit as sk  # noqa: E402
import earth as E  # noqa: E402  (노이즈·팽창·흐림·대기 껍질을 같이 씀)

RADIUS = 100.0
W, H = 2048, 1024
SS = 2
TEX_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "combatium_space_tex")

CONT = (4.0, 15.0)          # 큰 대륙 중심 (경도, 위도)
ELDR = (2.0, 17.0)          # 세계수 엘드르
MONATIUM = (26.0, 12.0)     # 모나티엄 (대륙 동부)
HAZE_DEG = 39.0             # 안개 경계 반지름 (엘드르 중심, 도)

PAL = {
    "ocean": (0x2f, 0x6c, 0xb4), "ocean_deep": (0x28, 0x5a, 0xa2), "shelf": (0x5a, 0xa2, 0xd4),
    "coast": (0x1f, 0x3c, 0x6c), "lake": (0x62, 0xaa, 0xda),
    "grass": (0x8f, 0xc0, 0x6c), "grass_l": (0xa6, 0xcc, 0x78), "forest": (0x5c, 0x96, 0x56),
    "forest_d": (0x48, 0x82, 0x4c), "dry": (0xc9, 0xc0, 0x80), "tundra": (0xa9, 0xb5, 0x96), "ice": (0xf1, 0xf5, 0xf7),
    "rock": (0x8f, 0x85, 0x76), "snow": (0xf2, 0xf4, 0xf6),
    "canopy": (0x2f, 0x62, 0x35), "canopy_l": (0x44, 0x80, 0x45), "canopy_c": (0x22, 0x4a, 0x29),
    "glade": (0xa8, 0xd6, 0x80),
    "erp_city": (0xe4, 0xda, 0xcd), "erp_roof": (0xc8, 0x76, 0x62), "erp_roof_t": (0x5f, 0xa8, 0x92),
    "erp_road": (0xf6, 0xf0, 0xe6),
    "city": (0xa8, 0xa7, 0xae), "city_l": (0xcc, 0xcb, 0xd0), "cyan": (0x7f, 0xf0, 0xea),
    "haze": (0xee, 0xf2, 0xf4),
    "cloud": (0xfb, 0xfd, 0xff), "cloud_sh": (0xcf, 0xdc, 0xec),
    "night": (0x12, 0x1b, 0x3a), "dusk": (0xff, 0x9a, 0x7a), "lights": (0xff, 0xd8, 0x86),
}


def Ccol(k):
    return np.array(PAL[k], dtype=np.float32) / 255.0


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def uvec(lon, lat):
    return E.unit(np.float32(lon), np.float32(lat)).astype(np.float32)


def ang(N, c):
    """각거리 (도)."""
    return np.degrees(np.arccos(np.clip((N * c).sum(-1), -1.0, 1.0)))


def tangent(c_lon, c_lat):
    lo, la = math.radians(c_lon), math.radians(c_lat)
    east = np.array([math.cos(lo), math.sin(lo), 0.0], dtype=np.float32)
    north = np.array([-math.sin(la) * math.sin(lo), math.sin(la) * math.cos(lo), math.cos(la)], dtype=np.float32)
    return east, north


def sun_dir():
    """모나티엄 쪽에서 보아 앞(바깥)·왼쪽(서)·조금 위(북)에서 오는 빛."""
    M = uvec(*MONATIUM)
    east, north = tangent(*MONATIUM)
    s = 0.70 * M - 0.62 * east + 0.22 * north
    return (s / np.linalg.norm(s)).astype(np.float32)


def bake_texture():
    global W, H
    W0, H0 = W, H
    W, H = W0 * SS, H0 * SS
    try:
        rgb, sun = _bake()
    finally:
        W, H = W0, H0
    small = rgb.astype(np.float32).reshape(H0, SS, W0, SS, 3).mean(axis=(1, 3))
    return np.clip(small + 0.5, 0, 255).astype(np.uint8), sun


def _bake():
    lon, lat = E.lonlat_grid(W, H)
    N = E.unit(lon, lat).astype(np.float32)
    nz = E.Noise3(19)
    nz2 = E.Noise3(23)
    print("[elias] land…")
    # ---- 땅: 큰 대륙(중심 각거리 + 왜곡 노이즈) + 작은 대륙 셋 + 섬
    warp = np.stack([nz.fbm(N * 1.6 + o, 3) - 0.5 for o in (3.0, 7.0, 13.0)], axis=-1)
    Nw = N + warp * 0.35
    th = ang(N, uvec(*CONT))
    field = (1.0 - th / 40.0) + 0.62 * (nz.fbm(Nw * 2.0, 4) - 0.5) + 0.22 * (nz2.fbm(N * 6.5, 3) - 0.5)
    for (clon, clat, rr) in ((142.0, -24.0, 20.0), (-118.0, 34.0, 15.0), (-158.0, -42.0, 10.0), (88.0, 48.0, 8.0)):
        t2 = ang(N, uvec(clon, clat))
        field = np.maximum(field, (1.0 - t2 / rr) + 0.5 * (nz.fbm(Nw * 2.6 + clon * 0.01, 4) - 0.5))
    isl = (nz2.fbm(N * 9.0 + 5.0, 3) - 0.62) * 3.0
    field = np.maximum(field, isl)
    land = field > 0.0
    sea = ~land
    # ---- 바다 색 + 얕은 띠 + 해안선
    sea_col = np.empty((H, W, 3), dtype=np.float32)
    sea_col[:] = Ccol("ocean")
    sea_col[nz.fbm(N * 3.0, 3) > 0.57] = Ccol("ocean_deep")
    sea_col[E.dilate(land, 5 * SS) & sea] = Ccol("shelf")
    sea_col[E.dilate(land, SS) & sea] = Ccol("coast")
    # ---- 땅 생태 (위도·노이즈)
    col = np.empty((H, W, 3), dtype=np.float32)
    col[:] = Ccol("grass")
    gl = nz.fbm(N * 7.0 + 2.0, 3)
    col[gl > 0.6] = Ccol("grass_l")
    fo = nz2.fbm(Nw * 4.2 + 1.0, 4)
    col[fo > 0.53] = Ccol("forest")
    col[fo > 0.63] = Ccol("forest_d")
    sw = ang(N, uvec(-24.0, -6.0))
    col[(sw < 14.0 + 6.0 * (gl - 0.5) * 2) & (fo < 0.55)] = Ccol("dry")
    col[(np.abs(lat) + 6 * (gl - 0.5) > 56)] = Ccol("tundra")
    col[(np.abs(lat) + 5 * (gl - 0.5) > 71)] = Ccol("ice")
    # ---- 정령산 산줄기 (모나티엄 북서쪽 호) + 남쪽 작은 산줄기
    print("[elias] mountains…")

    def chain(pts, width, gain, seed):
        """굽은 산줄기: 경로 위 점마다 둥근 봉우리 덩어리를 겹치고 능선 노이즈로 깎는다."""
        r = np.zeros(N.shape[:2], dtype=np.float32)
        rs = np.random.default_rng(seed)
        P = np.array(pts, dtype=np.float32)
        n = 16
        for k in range(n):
            t = k / (n - 1)
            # 2차 베지에 (가운데 점이 휨을 만든다)
            q = (1 - t) ** 2 * P[0] + 2 * (1 - t) * t * P[1] + t ** 2 * P[2]
            w = width * rs.uniform(0.75, 1.25) * (0.7 + 0.6 * math.sin(math.pi * t))
            r = np.maximum(r, np.exp(-(ang(N, uvec(float(q[0]), float(q[1]))) / w) ** 2) * gain)
        rough = 1.0 - np.abs(nz.fbm(N * 26.0 + seed, 3) - 0.5) * 2.0
        return r * (0.45 + 0.75 * rough)
    mtn = np.maximum(chain([(12.5, 33.5), (21.0, 29.0), (22.5, 18.0)], 2.1, 1.0, 3),
                     chain([(-12.0, -6.0), (-4.0, -14.0), (7.0, -12.0)], 1.7, 0.8, 7))
    mtn = mtn * land
    col[(mtn > 0.3) & (mtn <= 0.45)] = Ccol("forest_d")
    col[mtn > 0.45] = Ccol("rock")
    col[(mtn > 0.74) & (nz2.fbm(N * 40.0, 2) > 0.45)] = Ccol("snow")
    # ---- 호수
    for (llon, llat, rr) in ((-9.0, 27.0, 2.2), (13.0, 4.0, 1.6), (-16.0, 7.0, 2.6), (31.0, 24.0, 1.3),
                             (9.0, 31.0, 1.8), (-2.0, 0.0, 1.2)):
        t3 = ang(N, uvec(llon, llat)) + 0.8 * (nz2.fbm(N * 20.0, 2) - 0.5)
        lk = (t3 < rr) & land
        col[E.dilate(lk, SS) & ~lk & land] = Ccol("coast")
        col[lk] = Ccol("lake")
    # ---- 세계수 엘드르: 둘레 밝은 풀밭 + 방사형 짙은 수관 + 수관 그림자
    print("[elias] eldr…")
    e_east, e_north = tangent(*ELDR)
    te = ang(N, uvec(*ELDR))
    az = np.arctan2((N * e_north).sum(-1), (N * e_east).sum(-1))
    rt = 5.6 * (1.0 + 0.11 * np.sin(9 * az) + 0.05 * np.sin(17 * az + 1.0)) + 0.7 * (nz.fbm(N * 18.0, 2) - 0.5)
    sun = sun_dir()
    s_t = sun - (sun @ uvec(*ELDR)) * uvec(*ELDR)
    s_t /= np.linalg.norm(s_t)
    sh_c = uvec(*ELDR) - s_t * math.radians(2.6)
    sh_c /= np.linalg.norm(sh_c)
    shadow = (ang(N, sh_c) < 6.2) & (te >= rt)
    # 에르피엔: 수관 둘레를 두른 왕도 (흰 시가 고리 + 고리 길 셋 + 방사형 큰길 여섯 + 바깥 성벽), 그 밖의 밝은 풀밭
    er_out = rt + 1.5
    col[(te < er_out + 1.6) & (te >= er_out) & land] = Ccol("glade")
    ering = (te >= rt) & (te < er_out) & land
    col[ering] = Ccol("erp_city")
    speck = nz2.fbm(N * 140.0, 2)
    col[ering & (speck > 0.6)] = Ccol("erp_roof")
    col[ering & (speck < 0.36)] = Ccol("erp_roof_t")
    u = (te - rt) / (er_out - rt)
    col[ering & ((np.abs(u - 0.34) < 0.05) | (np.abs(u - 0.68) < 0.05) | (u > 0.93)
                 | (np.abs(np.sin(3.0 * (az - 0.4))) < 0.05))] = Ccol("erp_road")
    col[shadow & land] = col[shadow & land] * 0.72
    canopy = te < rt
    cc = np.empty((H, W, 3), dtype=np.float32)
    cc[:] = Ccol("canopy")
    clump = nz2.fbm(N * 55.0, 2)
    spokes = 0.5 + 0.5 * np.sin(az * 13.0 + te * 1.4)
    cc[(clump > 0.56) | ((spokes > 0.82) & (te > 1.4))] = Ccol("canopy_l")
    cc[te < 1.1] = Ccol("canopy_c")
    col[canopy] = cc[canopy]
    # ---- 모나티엄: 작은 회색 얼룩 + 밝은 도심 + 옅은 시안 빛무리
    tm = ang(N, uvec(*MONATIUM)) + 0.25 * (nz2.fbm(N * 40.0, 2) - 0.5)
    city = (tm < 1.7) & land
    col[city] = Ccol("city")
    col[(tm < 0.6) & land] = Ccol("city_l")
    # 합성
    a = land.astype(np.float32)[..., None]
    rgb = sea_col * (1 - a) + col * a
    glow = (0.42 * np.exp(-(np.maximum(tm - 1.0, 0.0) / 2.2) ** 2))[..., None]
    rgb = rgb * (1 - glow) + Ccol("cyan") * glow
    # ---- 안개 경계: 엘드르를 두른 옅은 띠 (바깥으로 흩날림)
    print("[elias] haze…")
    hr = HAZE_DEG + 2.5 * (nz.fbm(N * 3.5 + 9.0, 3) - 0.5) * 2
    band = np.exp(-((te - hr) / 3.2) ** 2)
    wisp = np.exp(-np.maximum(te - hr, 0) / 6.0) * (te > hr) * (nz2.fbm(N * 7.0 + 3.0, 4) > 0.5) * 0.45
    hz = np.clip((band * (0.55 + 0.5 * nz.fbm(N * 9.0, 3)) + wisp) * 0.85, 0, 0.82)[..., None]
    rgb = rgb * (1 - hz) + Ccol("haze") * hz
    # ---- 구름 (엘드르·모나티엄 위는 걷음)
    print("[elias] clouds…")
    Pz = N * np.array([1.0, 1.0, 2.4], dtype=np.float32)
    cw = np.stack([nz2.fbm(Pz * 1.8 + o, 3) - 0.5 for o in (11.0, 23.0, 37.0)], axis=-1)
    Pw = Pz + cw * 0.95
    cn = nz2.fbm(Pw * 2.5 + 3.1, 5) * 0.72 + nz.fbm(Pw * 8.0 - 1.7, 3) * 0.28
    bands = 0.08 * np.cos(np.radians(lat - 4) * 4.6) + 0.06 * np.exp(-((np.abs(lat) - 50) / 11) ** 2)
    clear = 0.22 * np.exp(-(te / 11.0) ** 2) + 0.2 * np.exp(-(tm / 6.0) ** 2) + 0.06 * np.exp(-(te / 26.0) ** 2)
    polar = np.clip((np.abs(lat) - 70.0) / 12.0, 0, 1)
    cv = cn + bands - clear - 0.25 * polar
    c_hi = cv > 0.62
    c_lo = (cv > 0.575) & ~c_hi
    rgb[c_lo] = Ccol("cloud_sh")
    rgb[c_hi] = Ccol("cloud")
    # ---- 조명 굽기: 부드러운 낮밤 경계
    print("[elias] lighting…")
    d = (N * sun).sum(-1) + (nz.fbm(N * 6.0, 2) - 0.5) * 0.03
    day = sstep(-0.10, 0.16, d)[..., None]
    lit = rgb * (0.80 + 0.20 * sstep(0.12, 0.62, d))[..., None]
    duskw = (0.75 * np.exp(-((d - 0.01) / 0.07) ** 2))[..., None]
    lit = lit * (1 - duskw * 0.35) + Ccol("dusk") * duskw * 0.22
    lum = rgb.mean(-1, keepdims=True)
    night = Ccol("night") + lum * np.array([0.10, 0.12, 0.20], dtype=np.float32)
    out = night * (1 - day) + lit * day
    # 밤 쪽 마을 불빛 (드문드문)
    rng = np.random.default_rng(5)
    pts = []
    while len(pts) < 70:
        plon, plat = rng.uniform(-180, 180), rng.uniform(-60, 60)
        jj = int((90 - plat) / 180 * H)
        ii = int((plon + 180) / 360 * W) % W
        if land[jj, ii] and not canopy[jj, ii]:
            pts.append((plon, plat))
    nightm = (d < -0.08)
    for (plon, plat) in pts:
        tq = ang(N, uvec(plon, plat))
        m = (tq < rng.uniform(0.25, 0.6)) & nightm & land & ~c_hi
        out[m] = Ccol("lights")
    return np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8), sun


def three(v):
    return (float(v[0]), float(v[2]), float(-v[1]))


def build(name="elias"):
    rgb, sun = bake_texture()
    os.makedirs(TEX_DIR, exist_ok=True)
    png = sk.save_png(os.path.join(TEX_DIR, f"{name}_toon.png"), rgb)
    print(f"[elias] texture {W}x{H} png {os.path.getsize(png) // 1024} KB")
    root = cb.empty(name, size=RADIUS * 0.2)
    ball = sk.uv_sphere(f"{name}_surface", RADIUS, 64, 32)
    ball.data.materials.append(sk.image_material(f"{name}_surface", png, unlit=True))
    ball["collider"] = 0
    ball.parent = root
    sunv = tuple(float(v) for v in sun)
    for o in (E.atmosphere(f"{name}_atmo_in", RADIUS * 1.026, 0.85, sunv, ("#b6eeff", "#ffbcae", "#37528f")),
              E.atmosphere(f"{name}_atmo_out", RADIUS * 1.065, 0.32, sunv, ("#76c2ff", "#e690a6", "#23366d"))):
        o.parent = root
    M = uvec(*MONATIUM)
    Ed = uvec(*ELDR)
    for nm, v in (("MARK_monatium", M), ("MARK_eldr", Ed)):
        e = cb.empty(nm, loc=tuple(float(c) * RADIUS for c in v), parent=root, size=1.0)
        e["latLon"] = f"{MONATIUM[1] if nm.endswith('monatium') else ELDR[1]},{MONATIUM[0] if nm.endswith('monatium') else ELDR[0]}"
    lat_s = math.degrees(math.asin(sunv[2]))
    lon_s = math.degrees(math.atan2(sunv[0], -sunv[1]))
    root["radius"] = RADIUS
    root["monatium"] = ",".join(f"{c:.5f}" for c in three(M))
    root["monatiumLocal"] = ",".join(f"{float(c):.5f}" for c in M)
    root["monatiumLatLon"] = f"{MONATIUM[1]},{MONATIUM[0]}"
    root["eldr"] = ",".join(f"{c:.5f}" for c in three(Ed))
    root["eldrLatLon"] = f"{ELDR[1]},{ELDR[0]}"
    root["hazeDeg"] = HAZE_DEG
    root["sunLocal"] = ",".join(f"{v:.5f}" for v in sunv)
    root["sunThree"] = ",".join(f"{c:.5f}" for c in three(sunv))
    root["sunLatLon"] = f"{lat_s:.2f},{lon_s:.2f}"
    root["collider"] = 0
    root["noOutline"] = 1
    print(f"[elias] monatium three {root['monatium']}  sunLocal {root['sunLocal']}")
    return root


if __name__ == "__main__":
    cb.reset()
    root = build()
    sk.export_glb("space/elias.glb", root=root)
