"""M1 「개판 5분 전」: 모나티엄 남서 교차로 → 상가 거리 → 남서광장역 (D-DAY 06:00, 개전 첫 아침).

npm run model -- art/blender/levels/m1_streets.py   → public/models/levels/m1_streets.glb
npm run shot -- levels/m1_streets.glb --views top,34

[원작] 선언 1주일 뒤 모나티엄에 R41 차원문이 열린다. 교주 측 진압반은 고무탄을 쓴다.
[오리지널] 특수작전부 1분대가 남서 교차로(1선)를 막다가 상가 거리(2선)로, 다시 남서광장역(지하철 서부선)으로 밀려
내려간다. 교차로·상가 거리·남서광장·역 출입구와 대합실 배치는 모두 [오리지널]이다. 차원문 A(남서, 주 유입구)는
위성 브리핑(act1_overview)과 같은 방위다.

좌표 (Blender, m): 원점 = 교차로 중심, +Y = 북쪽(후퇴 방향), -Y = 남쪽(R41 접근).
  y -156..-6    남서대로 4차로 (R41 접근로, VEH_apc1 경로). 남쪽 끝 y=-151 불타는 버스 차단선
  y   -9.6      1선 「교차로」: 바리케이드·모래주머니 줄. 동서 옆길(측면 우회로) x ±58, 서남 모서리는 낮은 소공원
  y  +46        광장로 교차 (습격차 측면 진입로) x ±30
  y  +60        2선 「상가」: 넘어진 화물차 + 진압반 보급 상자. 가운데 5 m는 차량 통로(VEH_apc2)
  y +108..160   남서광장: 바리케이드 호, 칸나의 진압 장갑차 자리, 남서광장역 출입구
                계단 29단(0.15 m) 4.5 m 아래 → 계단참 → 셔터(DOOR_shutter) → 대합실(개찰구)
  차원문 A: 남남서 하늘 (약 250 m, 높이 88 m, 반지름 50), 앞면이 교차로를 향한다
노드 계약: 1막 레벨 계약서 M1 절. 끝에 계약 노드 좌표표를 출력한다.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()
C = mk.City("m1_streets")
rng = random.Random(41)

ZR = -0.15                     # 차도 면 (보도 0)
ROADS = []                     # 차도 사각형 (x0, x1, y0, y1): 마커 높이용
TRIGS = []                     # (이름, 박스)


def gz(x, y):
    """그 자리 바닥 높이 (차도 -0.15, 보도·광장 0)."""
    for (x0, x1, y0, y1) in ROADS:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return ZR
    return 0.0


def road(axis, c, a0, a1, **kw):
    r = mk.road(C, axis, c, a0, a1, **kw)
    if axis == "y":
        ROADS.append((r["road_lo"], r["road_hi"], a0, a1))
    else:
        ROADS.append((a0, a1, r["road_lo"], r["road_hi"]))
    return r


def asphalt(x0, x1, y0, y1):
    C.box("asphalt", x0, x1, y0, y1, ZR - 0.4, ZR)
    C.col(x0, x1, y0, y1, ZR - 0.4, ZR)
    ROADS.append((x0, x1, y0, y1))


def walkway(x0, x1, y0, y1):
    C.box("pave", x0, x1, y0, y1, -0.4, 0.0)
    C.col(x0, x1, y0, y1, -0.4, 0.0)


def trig(tid, x0, x1, y0, y1, z0, z1, **props):
    o = mk._box_obj(f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    TRIGS.append((f"TRIG_{tid}", (x0, x1, y0, y1, z0, z1)))


def col_rot(x, y, hx, hy, yaw, z0, z1, shrink=0.04):
    """회전한 직사각형 발자국(반폭 hx, 반길이 hy)의 돌린 COL 상자. 예전에는 돌린 발자국의 축 정렬 상자라
    비스듬한 차·바리케이드 둘레에 보이지 않는 벽이 남았다 (이동 충돌 감사)."""
    C.ocol((x, y, z0), (2 * (hx - shrink), 2 * (hy - shrink), z1 - z0), yaw)


def face_s(x, y):
    return (x, y - 10.0)


def face_n(x, y):
    return (x, y + 10.0)


# ================================================================== 소품 (이 레벨 전용)

def car(x, y, yaw, key="white", *, z=None, taxi=False, wreck=False, length=3.6, width=1.7):
    """엘프 체격 승용차 (길이 3.6, 높이 1.3). 정면 -Y를 yaw로 돌림. wreck=True면 그을린 잔해 + 불씨."""
    z = gz(x, y) if z is None else z
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    M3 = Mx.to_3x3()
    hl, hwd = length / 2, width / 2
    body = "soot" if wreck else key
    zb = 0.05 if wreck else 0.22
    mk._bm_box(C.bm(body), -hwd, hwd, -hl, hl, zb, zb + 0.56, matrix=Mx)
    # 캐빈: 앞뒤로 기운 사다리꼴 (유리 덩어리 + 차체색 지붕)
    b = C.bm("dark" if wreck else "glass_d", "detail")
    z0, z1 = zb + 0.56, zb + 1.02
    a0, a1 = hwd - 0.1, hwd - 0.2
    P = [(-a0, -0.85, z0), (a0, -0.85, z0), (a0, 0.95, z0), (-a0, 0.95, z0),
         (-a1, -0.35, z1), (a1, -0.35, z1), (a1, 0.62, z1), (-a1, 0.62, z1)]
    v = [b.verts.new(Mx @ Vector(p)) for p in P]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        b.faces.new([v[i] for i in f])
    mk._bm_box(C.bm(body, "detail"), -a1 - 0.02, a1 + 0.02, -0.36, 0.63, z1, z1 + 0.06, matrix=Mx)
    if not wreck:
        bw = C.bm("dark", "detail")
        for sx in (-1, 1):
            for sy in (-1, 1):
                p0 = Mx @ Vector((sx * (hwd - 0.22), sy * (hl - 0.68), 0.27))
                p1 = Mx @ Vector((sx * (hwd + 0.03), sy * (hl - 0.68), 0.27))
                mk._bm_cyl(bw, p0, p1, 0.27, segs=8)
        Nf = M3 @ Vector((0, -1, 0))
        Nb = -Nf
        for sx in (-1, 1):
            C.rect("lamp_off", Mx @ Vector((sx * (hwd - 0.3), -hl, zb + 0.4)), Nf, 0.36, 0.12, lift=0.012)
            C.rect("red", Mx @ Vector((sx * (hwd - 0.28), hl, zb + 0.42)), Nb, 0.3, 0.1, lift=0.012)
        if taxi:
            mk._bm_box(C.bm("white", "detail"), -0.3, 0.3, -0.05, 0.25, z1 + 0.06, z1 + 0.24, matrix=Mx)
    else:
        C.blob("fire", tuple(Mx @ Vector((0.0, -0.5, 0.95))), 0.45, (1.2, 1.6, 0.6), segs=7, rings=4)
    # 차체(바퀴 위 상자, 범퍼까지) + 캐빈(안으로 좁은 유리 덩어리): 통 상자 하나는 보닛·트렁크 위에 보이지 않는 벽이 남았다
    C.lcol(x, y, z, yaw, -hwd, hwd, -hl, hl, 0, zb + 0.56)
    C.ccol([Mx @ Vector((px, py, pz if pz < z1 else z1 + 0.06)) for (px, py, pz) in P])


def bus_wreck(x, y, yaw, *, z=None, length=9.0, width=2.4):
    """불탄 시내버스 (남쪽 차단선)."""
    z = gz(x, y) if z is None else z
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    hl, hwd = length / 2, width / 2
    mk._bm_box(C.bm("soot"), -hwd, hwd, -hl, hl, 0.1, 2.5, matrix=Mx)
    mk._bm_box(C.bm("dark", "detail"), -hwd - 0.02, hwd + 0.02, -hl + 0.4, hl - 0.6, 1.3, 2.1, matrix=Mx)
    mk._bm_box(C.bm("mint", "detail"), -hwd - 0.01, hwd + 0.01, -hl, -hl + 2.2, 0.5, 0.75, matrix=Mx)
    for k in (-2.8, 0.0, 2.6):
        C.blob("fire", tuple(Mx @ Vector((0.0, k, 2.2))), 0.7, (1.1, 1.4, 0.7), segs=7, rings=4)
    col_rot(x, y, hwd, hl, yaw, z, z + 2.5)


def bus_stop(x0, x1, y0, y1):
    """버스 정류장 (뒤판이 +x, 차도 쪽 -x가 앞). 남쪽 끝 광고판은 서서 엄폐(높은 엄폐물)."""
    zt = 2.3
    for (px, py) in ((x0 + 0.1, y0 + 0.1), (x0 + 0.1, y1 - 0.1), (x1 - 0.1, y0 + 0.1), (x1 - 0.1, y1 - 0.1)):
        C.cyl("metal", (px, py, 0), (px, py, zt), 0.05, segs=6, kind="detail")
        C.col(px - 0.05, px + 0.05, py - 0.05, py + 0.05, 0, zt)
    C.box("navy_l", x0 - 0.15, x1 + 0.05, y0 - 0.1, y1 + 0.1, zt, zt + 0.12)
    C.box("teal", x0 - 0.17, x0 - 0.13, y0 - 0.1, y1 + 0.1, zt + 0.02, zt + 0.1, kind="detail")
    C.box("glass_d", x1 - 0.08, x1, y0 + 0.15, y1 - 0.15, 0.25, zt - 0.1, kind="detail")
    C.col(x1 - 0.1, x1 + 0.02, y0, y1, 0, zt)
    # 남쪽 광고 조명판
    C.box("metal", x0 + 0.05, x1, y0, y0 + 0.18, 0.0, zt, kind="detail")
    C.rect("win_lit", ((x0 + x1) / 2 + 0.03, y0 - 0.002, 1.25), (0, -1, 0), x1 - x0 - 0.3, 1.6, lift=0.01)
    C.text("dark", "모나티엄 갓 탤런트", 0.16, ((x0 + x1) / 2 + 0.03, y0 - 0.02, 1.55), (0, -1, 0))
    C.text("violet", "S7 · 오늘 밤 8시", 0.12, ((x0 + x1) / 2 + 0.03, y0 - 0.02, 1.25), (0, -1, 0))
    C.col(x0 + 0.05, x1, y0, y0 + 0.18, 0, zt)
    mk.bench(C, (x0 + x1) / 2 + 0.25, (y0 + y1) / 2, yaw=90, length=2.0)
    # 노선 표지 기둥
    sx, sy = x0 - 0.35, y1 - 0.2
    C.cyl("metal", (sx, sy, 0), (sx, sy, 2.6), 0.045, segs=6, kind="detail")
    C.col(sx - 0.05, sx + 0.05, sy - 0.05, sy + 0.05, 0, 2.0)
    C.plate("navy", hw.rrect(0.62, 0.5, 0.1, 2), (sx, sy, 2.35), (-1, 0, 0), 0.04, kind="detail")
    C.text("white", "남서교차로", 0.1, (sx - 0.045, sy, 2.36), (-1, 0, 0), lift=0.006)


def riot_barricade(x, y, yaw=0.0, *, z=None, label=False, w=1.6, h=0.95):
    """진압반 바리케이드 (키트 barricade와 같은 모양·크기). 글자는 분대 쪽(뒷면) 한 면에만, 짧게."""
    z = gz(x, y) if z is None else z
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    M3 = Mx.to_3x3()
    N = (M3 @ Vector((0, -1, 0))).normalized()
    R = (M3 @ Vector((1, 0, 0))).normalized()
    c = Mx @ Vector((0, 0, h * 0.55))
    up = Vector((0, 0, 1))
    C.plate("violet", hw.rrect(w, h * 0.62, 0.12, 2), tuple(c), tuple(N), 0.06, back=0.03)
    for sgn in (1, -1):
        C.strip("teal", c - R * (w / 2 - 0.08) + N * (0.031 * sgn) - up * 0.12,
                c + R * (w / 2 - 0.08) + N * (0.031 * sgn) - up * 0.12, 0.1, N * sgn, lift=0.004)
    if label:
        C.text("white", "진압반", 0.12, c - N * 0.031 + up * 0.07, -N, lift=0.004)
    for s_ in (-1, 1):
        foot = Mx @ Vector((s_ * (w / 2 - 0.15), 0, 0))
        C.beam("steel", foot + up * 0.02, foot + up * (h * 0.8), 0.06, 0.06, kind="detail")
        C.beam("steel", foot - N * 0.3, foot + N * 0.3, 0.07, 0.05, kind="detail")
        C.beam("steel", foot - N * 0.28 + up * 0.03, foot + up * (h * 0.45), 0.04, 0.04, kind="detail")
        C.beam("steel", foot + N * 0.28 + up * 0.03, foot + up * (h * 0.45), 0.04, 0.04, kind="detail")
    mk.barricade_col(C, x, y, z, yaw, w, h)


def sign_post(x, y, ko, en=None, *, yaw=0.0, w=1.5, h=2.6):
    """도로명 표지 (헌글). 글자는 정면(-Y를 yaw로 돌린 쪽) 한 면에만."""
    C.cyl("metal", (x, y, 0), (x, y, h), 0.05, segs=6, kind="detail")
    C.col(x - 0.05, x + 0.05, y - 0.05, y + 0.05, 0, 2.0)
    a = math.radians(yaw)
    N = Vector((math.sin(a), -math.cos(a), 0))
    c = Vector((x, y, h - 0.3))
    C.plate("navy", hw.rrect(w, 0.48, 0.12, 2), tuple(c - N * 0.04), tuple(N), 0.08, kind="detail")
    C.text("white", ko, 0.2, tuple(c + N * 0.04 + Vector((0, 0, 0.07 if en else 0.0))), tuple(N), lift=0.006)
    if en:
        C.text("glow", en, 0.09, tuple(c + N * 0.04 - Vector((0, 0, 0.14))), tuple(N), lift=0.006)


def cheap_barricade(x, y, yaw):
    """글자 없는 진압반 바리케이드 (같은 크기, 삼각형 아낌)."""
    C.rbox("violet", (x, y, 0.56 + gz(x, y)), (1.6, 0.1, 0.58), (0, 0, yaw))
    C.rbox("teal", (x, y, 0.42 + gz(x, y)), (1.48, 0.12, 0.1), (0, 0, yaw), kind="detail")
    a = math.radians(yaw)
    for s in (-0.65, 0.65):
        px, py = x + math.cos(a) * s, y + math.sin(a) * s
        C.rbox("steel", (px, py, 0.14 + gz(x, y)), (0.07, 0.6, 0.06), (0, 0, yaw), kind="detail")
        C.rbox("steel", (px, py, 0.4 + gz(x, y)), (0.06, 0.06, 0.7), (0, 0, yaw), kind="detail")
    mk.barricade_col(C, x, y, gz(x, y), yaw, 1.6, 0.95)


def sandbags(x, y, yaw=0.0, n=4):
    z = gz(x, y)
    mk.sandbag_wall(C, x, y, yaw=yaw, z=z, n=n)    # COL은 키트가 단다 (돌린 상자)


def riot_crate(x, y, z=0.0, *, w=0.9, d=1.0, h=0.75, label=None, key="violet"):
    """진압반 보급 상자 (남보라 + 청록 띠 + 흰 표기)."""
    C.box(key, x - w / 2, x + w / 2, y - d / 2, y + d / 2, z, z + h, kind="detail")
    C.box("teal", x - w / 2 - 0.01, x + w / 2 + 0.01, y - 0.08, y + 0.08, z, z + h + 0.01, kind="detail")
    C.box("dark", x - w / 2 - 0.02, x + w / 2 + 0.02, y - d / 2 - 0.02, y + d / 2 + 0.02, z, z + 0.06,
          kind="detail")
    if label:
        C.text("white", label, 0.1, (x, y - d / 2, z + h * 0.6), (0, -1, 0), lift=0.012)


def ammo_crate(x, y, z=0.0, *, yaw=0.0):
    """고무탄 탄약 상자. 위 면 = z + 0.42."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    mk._bm_box(C.bm("navy_l", "detail"), -0.35, 0.35, -0.22, 0.22, 0, 0.42, matrix=Mx)
    mk._bm_box(C.bm("hazard", "detail"), -0.36, 0.36, -0.23, 0.23, 0.3, 0.36, matrix=Mx)
    N = Mx.to_3x3() @ Vector((0, -1, 0))
    C.text("white", "고무탄", 0.08, tuple(Mx @ Vector((0, -0.22, 0.17))), tuple(N), lift=0.01)
    col_rot(x, y, 0.35, 0.22, yaw, z, z + 0.42, shrink=0.0)
    return z + 0.42


def overturned_truck(xa, xb, y0):
    """넘어진 배송 화물차 (옆으로 누움). 바닥(바퀴)이 남쪽(적), 지붕이 북쪽(분대). 높이 2.0 = 차폭."""
    # 차대 (남쪽 면): 세로 보 2줄 + 굴대 + 바퀴 + 연료통. 짐칸 바닥판이 보이게 듬성듬성
    for (za, zb_) in ((0.42, 0.62), (1.38, 1.58)):
        C.box("dark", xa + 0.15, xb - 0.35, y0 + 0.3, y0 + 0.62, za, zb_, kind="detail")
    for wx in (xa + 1.0, xa + 2.2, xb - 1.1):
        C.cyl("dark", (wx, y0 + 0.3, 0.2), (wx, y0 + 0.3, 1.8), 0.08, segs=6, kind="detail")
        for (za, zb_) in ((0.0, 0.32), (1.68, 2.0)):
            C.cyl("rubber", (wx, y0 + 0.3, za), (wx, y0 + 0.3, zb_), 0.36, segs=10, kind="detail")
            C.cyl("steel", (wx, y0 + 0.3, za - 0.01), (wx, y0 + 0.3, zb_ + 0.01), 0.16, segs=8, kind="detail")
    C.cyl("steel", (xa + 2.7, y0 + 0.4, 1.0), (xa + 3.6, y0 + 0.4, 1.0), 0.22, segs=8, kind="detail")  # 연료통
    # 짐칸 (흰 상자). 옆면이 위를 본다: 민트 띠와 글자
    xc = xb - 1.6
    C.box("white", xa, xc, y0 + 0.62, y0 + 2.62, 0.0, 2.0)
    C.rect("mint", ((xa + xc) / 2, y0 + 2.25, 2.0), (0, 0, 1), xc - xa, 0.32, up=(0, 1, 0), lift=0.01)
    C.text("navy", "MONATIUM 25 · 신선 배송", 0.26, ((xa + xc) / 2, (y0 + 1.5), 2.0), (0, 0, 1), up=(0, -1, 0))
    for k in range(1, 4):                                                                    # 지붕 골 (북쪽 면)
        rx = xa + (xc - xa) * k / 4
        C.box("steel", rx - 0.05, rx + 0.05, y0 + 2.62, y0 + 2.67, 0.08, 1.92, kind="detail")
    C.box("steel", xa - 0.05, xa + 0.02, y0 + 0.66, y0 + 2.58, 0.04, 1.96, kind="detail")   # 뒷문
    C.rect("dark", (xa - 0.051, y0 + 1.62, 1.0), (-1, 0, 0), 0.05, 1.9, lift=0.004)
    # 운전실
    C.box("white", xc + 0.05, xb, y0 + 0.62, y0 + 2.22, 0.1, 1.9)
    C.rect("glass_d", (xb, y0 + 1.75, 1.0), (1, 0, 0), 0.8, 1.5, up=(0, 1, 0), lift=0.012)
    C.box("dark", xb, xb + 0.12, y0 + 0.62, y0 + 1.0, 0.1, 1.9, kind="detail")                # 범퍼
    C.col(xa, xb + 0.1, y0, y0 + 2.62, 0.0, 2.0)


def kiosk(x, y):
    C.box("navy", x - 0.8, x + 0.8, y - 0.7, y + 0.7, 0.0, 1.9)
    C.box("teal", x - 0.9, x + 0.9, y - 0.8, y + 0.8, 1.9, 2.05)
    C.rect("win_lit", (x, y - 0.7, 1.25), (0, -1, 0), 1.2, 0.7, lift=0.01)
    C.text("white", "신문 · 간식", 0.14, (x, y - 0.7, 1.75), (0, -1, 0))
    C.col(x - 0.8, x + 0.8, y - 0.7, y + 0.7, 0.0, 2.05)


def alert_pole(lid, x, y, h=3.0, blink=0.7):
    C.cyl("metal", (x, y, 0), (x, y, h), 0.06, segs=6, kind="detail")
    C.col(x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0, 2.0)
    mk.alert_beacon(C, lid, (x, y, h), blink=blink)
    C.fx(lid.replace("alert", "siren"), (x, y, h - 0.1), sound="siren", group="alert")


def bld(x0, x1, y0, y1, floors, style, front, sides, shop=None, sign=None, far=False, seed=0, **kw):
    sh = None
    if shop:
        nm, sub, awn = SHOPS[shop]
        sh = {"name": nm, "sub": sub, "awning": awn}
    return mk.building(C, x0, x1, y0, y1, floors=floors, style=style, front=front, sides=sides, shop=sh,
                       sign=sign, far=far, seed=seed, **kw)


SHOPS = {
    # 부제는 글자 삼각형이 비싸 짧은 것 두 개만 남긴다
    "m25": ("모나티엄 25", "남서점", "mint"),
    "cutlet": ("커틀릿 하우스", "공기커틀릿 아님", "coral"),
    "bakery": ("엘프 베이커리", "", "coral"),
    "pharm": ("정령 약국", "", "teal"),
    "cafe": ("카페 이슬", "", "mint"),
    "books": ("헌글 서점", "", "teal"),
    "flower": ("광장 꽃집", "", "coral"),
    "optic": ("에르피엔 안경", "", "mint"),
    "phone": ("모나폰", "", "teal"),
    "noodle": ("고기나무 국수", "", "coral"),
}

# ================================================================== 바닥: 도로·교차로·광장
C.group("ground")
# 남서대로 (R41 접근로, 4차로)
road("y", 0.0, -156.0, -6.0, lanes=4, walk=3.2, crossings=(-7.6,))
# 동서 옆길 (2차로, 측면 우회로)
road("x", 0.0, -58.4, -8.8, lanes=2, lane_w=3.0, walk=3.0, crossings=(-10.4,))
road("x", 0.0, 8.8, 58.4, lanes=2, lane_w=3.0, walk=3.0, crossings=(10.4,))
# 교차로 J0 (남쪽 팔 4차로, 북쪽 상가 거리 2차로)
asphalt(-5.6, 5.6, -6.0, 6.0)
asphalt(-8.8, -5.6, -3.0, 3.0)
asphalt(5.6, 8.8, -3.0, 3.0)
for (x0, x1, y0, y1) in ((-8.8, -5.6, -6.0, -3.0), (-8.8, -5.6, 3.0, 6.0), (5.6, 8.8, -6.0, -3.0), (5.6, 8.8, 3.0, 6.0)):
    walkway(x0, x1, y0, y1)
# 상가 거리 (북쪽, 2차로 + 넓은 보도 5.8 m)
road("y", 0.0, 6.0, 40.0, lanes=2, lane_w=3.0, walk=5.8, crossings=(7.6, 38.4))
road("y", 0.0, 52.0, 108.0, lanes=2, lane_w=3.0, walk=5.8, crossings=(53.6, 106.4))
# 광장로 교차 J1 (y=46)
road("x", 46.0, -30.4, -8.8, lanes=2, lane_w=3.0, walk=3.0, crossings=(-10.4,))
road("x", 46.0, 8.8, 30.4, lanes=2, lane_w=3.0, walk=3.0, crossings=(10.4,))
asphalt(-3.0, 3.0, 40.0, 52.0)
asphalt(-8.8, -3.0, 43.0, 49.0)
asphalt(3.0, 8.8, 43.0, 49.0)
for (x0, x1, y0, y1) in ((-8.8, -3.0, 40.0, 43.0), (-8.8, -3.0, 49.0, 52.0), (3.0, 8.8, 40.0, 43.0), (3.0, 8.8, 49.0, 52.0)):
    walkway(x0, x1, y0, y1)
# 광장 옆길 (y=124)
road("x", 124.0, -48.2, -26.0, lanes=2, lane_w=3.0, walk=3.0)
road("x", 124.0, 26.0, 48.2, lanes=2, lane_w=3.0, walk=3.0)

# 남서광장: 역 계단 구멍(x ±1.5, y 134..140)을 비운 판석
ST_Y0 = 134.0                 # 계단 입구(맨 윗단 앞 끝)
ST_HW = 1.5                   # 계단 반폭 (유효 폭 3.0 m)
# 구멍 양옆은 6 mm 넓게: 판석 구멍 옆면이 계단 옆벽 안쪽 면(x ±1.5)과 같은 평면이면 깜빡인다
for (x0, x1, y0, y1) in ((-26.0, 26.0, 108.0, ST_Y0), (-26.0, 26.0, ST_Y0 + 6.0, 160.0),
                         (-26.0, -ST_HW - 0.006, ST_Y0, ST_Y0 + 6.0), (ST_HW + 0.006, 26.0, ST_Y0, ST_Y0 + 6.0)):
    mk.paving(C, x0, x1, y0, y1, tile=1.6)
# 판석(x ±26)과 광장 동·서 건물(x ±26.2) 사이 0.2 m 바닥 틈 (캡슐 중심이 틈 위에 걸리면 걷지 못했다, 이동 충돌 감사)
for sx in (-1, 1):
    C.col(min(sx * 26.0, sx * 26.4), max(sx * 26.0, sx * 26.4), 128.0, 160.0, -0.3, 0.0)
for (a0, a1, b0, b1) in ((-26.0, 26.0, 108.0, 108.5), (-26.0, 26.0, 159.5, 160.0)):
    C.decal("pave_r", [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], (0, 0, 0), (0, 0, 1), up=(0, 1, 0), lift=0.014)
# 서남 모서리 소공원 (낮게 비워 차원문 시선을 연다)
mk.paving(C, -30.0, -8.8, -28.2, -6.0, tile=1.6)
mk.grass(C, -27.5, -19.0, -25.5, -17.0)
mk.grass(C, -27.5, -19.0, -14.5, -8.5)
# 바닥판 (건물 사이 틈으로 보이는 땅). 역 계단 구멍은 비운다
for (x0, x1, y0, y1) in ((-320, 320, -320, ST_Y0 - 0.3), (-320, 320, ST_Y0 + 6.4, 320),
                         (-320, -ST_HW - 0.3, ST_Y0 - 0.3, ST_Y0 + 6.4), (ST_HW + 0.3, 320, ST_Y0 - 0.3, ST_Y0 + 6.4)):
    C.box("pave_d", x0, x1, y0, y1, -0.62, -0.34, kind="fine")

# ================================================================== 건물
# (x0, x1, y0, y1, 층, 양식, 정면, 창 면, 상가, 간판, 원경)
C.group("south")
SOUTH = [
    # 서쪽 (소공원 남쪽 낮은 편의점 → 3~4층 → 원경)
    (-30.0, -9.0, -40.0, -28.2, 1, "brick", "+x", "+x+y", "m25", None, False),
    (-23.0, -9.0, -56.0, -40.4, 3, "office", "+x", "+x", None, None, False),
    (-23.0, -9.0, -72.0, -56.4, 3, "brick", "+x", "+x", "noodle", None, False),
    (-23.0, -9.0, -90.0, -72.4, 4, "office", "+x", "+x", None, None, False),
    # 적 쪽 먼 블록: 걸어 들어올 수 있으니 원경 LOD 대신 옥상을 뺀 보통 건물 (FLAT)
    (-23.0, -9.0, -110.0, -90.4, 3, "office", "+x", "+x", None, None, "flat"),
    (-23.0, -9.0, -130.0, -110.4, 4, "brick", "+x", "+x", None, None, "flat"),
    (-23.0, -9.0, -156.0, -130.4, 3, "glass", "+x", "+x", None, None, "flat"),
    # 동쪽 (4~6층)
    (9.0, 26.0, -24.0, -6.2, 5, "office", "-x", "-x+y", "cafe", None, False),
    (9.0, 24.0, -40.0, -24.2, 6, "glass", "-x", "-x", None, "MELU CORP.", False),
    (9.0, 24.0, -58.0, -40.4, 4, "office", "-x", "-x", "pharm", None, False),
    (9.0, 24.0, -76.0, -58.4, 6, "glass", "-x", "-x", None, None, False),
    (9.0, 24.0, -96.0, -76.4, 5, "office", "-x", "-x", None, None, "flat"),
    (9.0, 24.0, -116.0, -96.4, 4, "brick", "-x", "-x", None, None, "flat"),
    (9.0, 24.0, -136.0, -116.4, 6, "glass", "-x", "-x", None, None, "flat"),
    (9.0, 24.0, -156.0, -136.4, 4, "office", "-x", "-x", None, None, "flat"),
]
WESTEAST = [
    # 서남 블록 (소공원 뒤), 서쪽 옆길 남쪽
    (-44.0, -30.2, -28.0, -6.2, 4, "office", "+y", "+y+x", None, None, False),
    (-58.0, -44.2, -22.0, -6.2, 4, "brick", "+y", "+y", "books", None, False),
    # 서북 블록
    (-24.0, -9.0, 6.2, 22.0, 4, "brick", "+x", "+x-y", "bakery", None, False),
    (-30.2, -9.0, 22.2, 39.8, 4, "office", "+x", "+x+y", "phone", None, False),
    (-40.0, -24.2, 6.2, 20.0, 5, "apartment", "-y", "-y", None, None, False),
    (-58.0, -40.2, 6.2, 20.0, 4, "office", "-y", "-y", None, None, False),
    # 동남 블록 (동쪽 옆길 남쪽)
    (26.2, 42.0, -20.0, -6.2, 4, "brick", "+y", "+y", None, None, False),
    (42.2, 58.0, -20.0, -6.2, 4, "office", "+y", "+y", None, None, False),
    # 동북 블록
    (9.0, 24.0, 6.2, 22.0, 4, "office", "-x", "-x-y", "flower", None, False),
    (9.0, 30.2, 22.2, 39.8, 5, "brick", "-x", "-x+y", "optic", None, False),
    (24.2, 40.0, 6.2, 20.0, 4, "brick", "-y", "-y", None, None, False),
    (40.2, 58.0, 6.2, 20.0, 6, "glass", "-y", "-y", None, None, False),
    # 옆길 끝을 막는 건물 (T자 끝)
    (-74.0, -58.4, -22.0, 20.0, 5, "office", "+x", "+x", None, None, False),
    (58.4, 74.0, -22.0, 20.0, 5, "apartment", "-x", "-x", None, None, False),
    (-46.0, -30.4, 22.2, 66.0, 4, "office", "+x", "+x", None, None, False),
    (30.4, 46.0, 22.2, 66.0, 4, "brick", "-x", "-x", None, None, False),
]
SHOPS_ROW = [
    (-30.2, -9.0, 52.2, 66.0, 4, "brick", "+x", "+x-y", "cutlet", None, False),
    (-24.0, -9.0, 66.2, 80.0, 3, "apartment", "+x", "+x", "cafe", None, False),
    (-24.0, -9.0, 80.2, 94.0, 4, "office", "+x", "+x", "m25", None, False),
    (-26.0, -9.0, 94.2, 107.8, 5, "brick", "+x", "+x+y", "flower", None, False),
    (9.0, 30.2, 52.2, 66.0, 4, "office", "-x", "-x-y", "pharm", None, False),
    (9.0, 24.0, 66.2, 80.0, 4, "brick", "-x", "-x", "noodle", None, False),
    (9.0, 24.0, 80.2, 94.0, 3, "apartment", "-x", "-x", "books", None, False),
    (9.0, 26.0, 94.2, 107.8, 5, "glass", "-x", "-x+y", "phone", None, False),
]
PLAZA_B = [
    (-48.0, -26.2, 96.0, 117.8, 5, "office", "+x", "+x+y", "cafe", None, False),
    (-48.0, -26.2, 130.2, 160.0, 5, "apartment", "+x", "+x-y", None, None, False),
    (26.2, 48.0, 96.0, 117.8, 5, "office", "-x", "-x+y", "m25", None, False),
    (26.2, 48.0, 130.2, 160.0, 6, "glass", "-x", "-x-y", None, None, False),
    (-48.0, -16.0, 160.2, 176.0, 5, "office", "-y", "-y", None, None, False),
    (-15.8, 16.0, 160.2, 176.0, 7, "glass", "-y", "-y", None, "남서광장 타워", False),
    (16.2, 48.0, 160.2, 176.0, 5, "brick", "-y", "-y", None, None, False),
    (-62.0, -48.2, 110.0, 140.0, 4, "office", "+x", "+x", None, None, False),
    (48.2, 62.0, 110.0, 140.0, 4, "brick", "-x", "-x", None, None, False),
]


def build_rows(rows, seed0):
    for i, (x0, x1, y0, y1, fl, st, fr, sd, shop, sign, far) in enumerate(rows):
        flat = far == "flat"
        bld(x0, x1, y0, y1, fl, st, fr, sd, shop=shop, sign=sign, far=(far is True), seed=seed0 + i * 7,
            cctv=(i % 3 == 0) and not flat, roof=not flat, h0=3.0 if far else None)


build_rows(SOUTH, 100)
C.group("junction")
build_rows(WESTEAST, 300)
C.group("north")
build_rows(SHOPS_ROW, 500)
C.group("plaza")
build_rows(PLAZA_B, 700)


def corner_pinch(ax, ay, bx, by, out, r=1.0, z0=-0.3, z1=4.0):
    """대각선으로 맞닿은 두 건물의 둥근 모서리(반지름 r, 모서리 점 a·b) 사이 틈을 막는다. 두 모서리 호가 가장 가까운 두 점을
    잇는 선(틈의 가장 좁은 곳)에서 바깥(out 방향, 맵 밖) 쪽으로 0.6 m 두께, 양 끝은 건물 껍질 속 0.15 m.
    둥근 모서리 사이로 1.1 m 틈이 열려 건물 뒤 바닥판(충돌체 없는 원경 판)으로 걸어 나가 떨어졌다 (2026-11-04 groundcheck)"""
    ca = Vector((ax + math.copysign(r, ax - bx), ay + math.copysign(r, ay - by)))     # a 모서리 호 중심 (건물 안쪽)
    cb_ = Vector((bx + math.copysign(r, bx - ax), by + math.copysign(r, by - ay)))
    u = (cb_ - ca).normalized()
    pa, pb = ca + u * (r - 0.15), cb_ - u * (r - 0.15)
    o = Vector(out).normalized() * 0.6
    quad = [pa, pb, pb + o, pa + o]
    C.ccol([(p.x, p.y, z) for p in quad for z in (z0, z1)])


# 서남 모서리 소공원 남서 끝: 편의점(남쪽) 북서 모서리와 사무동(서쪽) 남동 모서리 사이 (맵 밖은 남서쪽)
corner_pinch(-30.0, -28.2, -30.2, -28.0, (-1.0, -1.0))

# ================================================================== 원경 (지붕 너머 고층, 차원문 쪽 아래는 낮게)
C.group("far")
FAR = [
    (-85, -40, 24, 18, 12), (-100, 30, 20, 22, 14), (-90, 95, 22, 18, 11), (-70, 205, 26, 20, 16),
    (0, 215, 30, 22, 18), (75, 200, 24, 20, 13), (95, 100, 20, 24, 15), (100, 25, 22, 18, 12),
    (90, -50, 24, 20, 14), (70, -175, 22, 22, 11), (-35, -205, 20, 16, 7), (25, -235, 26, 18, 9),
    (-120, -150, 24, 20, 8), (130, -120, 20, 26, 16), (-150, 70, 26, 22, 18), (150, 160, 30, 24, 20),
]
for k, (fx, fy, w, d, fl) in enumerate(FAR):
    mk.building(C, fx - w / 2, fx + w / 2, fy - d / 2, fy + d / 2, floors=fl, style=("glass", "office")[k % 2],
                far=True, seed=900 + k, h0=3.0, fh=3.0, r=3.0, col=False, sides="-y+y-x+x")


def smoke_plume(x, y, *, h=45.0, r=4.0, drift=(0.32, 0.14), seed=0):
    """거리에서 올려다보는 연기 기둥: 겹쳐 쌓은 덩어리 (키트 smoke_column은 위성 시점용이라 듬성듬성하다).
    아래는 검은 연기, 위로 갈수록 넓고 공기 원근의 회청색. 바람은 동북동."""
    rr_ = random.Random(seed)
    C.blob("fire", (x, y, r * 0.3), r * 0.55, (1, 1, 0.5), segs=6, rings=3)
    zz = r * 0.5
    while zz < h:
        t = zz / h
        rad = r * (0.55 + 1.35 * t) * rr_.uniform(0.9, 1.1)
        cx = x + drift[0] * zz + rr_.uniform(-0.25, 0.25) * rad
        cy = y + drift[1] * zz + rr_.uniform(-0.25, 0.25) * rad
        C.blob("smoke_d" if t < 0.7 else "far_d", (cx, cy, zz), rad, (1.0, 1.0, 0.8), segs=8, rings=5,
               rot_z=rr_.uniform(0, 3))
        zz += rad * 0.62


# 차원문 시선(남남서)은 비운다
for k, (sx, sy, h, r) in enumerate(((40, -205, 52, 4.5), (-140, -95, 60, 5.0), (85, -110, 44, 4.0), (55, 50, 34, 3.2))):
    smoke_plume(sx, sy, h=h, r=r, seed=k + 3)

# ================================================================== 차원문 A (남남서 하늘, 앞면이 교차로)
C.group("far")
GATE_C = (-70.0, -240.0, 88.0)
GATE_R = 50.0
GATE_YAW = math.degrees(math.atan2(-(0.0 - GATE_C[0]), (0.0 - GATE_C[1])))
mk.gate_r41(C, "a", GATE_C, radius=GATE_R, tilt=68.0, yaw=GATE_YAW)

# ================================================================== 남서대로 (R41 접근로): 버려진 차, 잔해, 가로 시설
C.group("south")
for y in range(-24, -150, -26):
    mk.lamp(C, -6.1, y)
    mk.lamp(C, 6.1, y - 13)
for y in (-30, -66, -102):
    mk.tree(C, 7.6, y, h=4.8, seed=y, lod=1)
    mk.tree(C, -7.6, y - 12, h=4.6, seed=-y, lod=1)
car(-4.4, -20.0, 12, "navy_l")
car(-4.6, -46.0, -6, "glass")
car(7.2, -60.0, 180, "white")
car(-4.4, -78.0, 168, "coral")
car(-3.9, -104.0, 30, wreck=True)
car(6.8, -120.0, -20, wreck=True)
C.fx("smoke_01", (-3.9, -104.0, 1.0), strength=0.6)
C.fx("smoke_02", (6.8, -120.0, 1.0), strength=0.6)
for (x, y, r_) in ((2.0, -44.0, 1.6), (-1.2, -92.0, 2.0), (4.2, -128.0, 1.8), (-6.8, -36.0, 1.2)):
    mk.scorch(C, x, y, r_, z=gz(x, y), seed=int(abs(y)))
mk.cctv_pole(C, 8.3, -26.0, yaw=150)
sign_post(-8.3, -12.0, "남서대로", "SW AVE", yaw=180)
mk.trash_bin(C, 8.2, -14.0)
mk.bollard(C, -6.0, -6.6)
mk.bollard(C, 6.0, -6.6)
# 남쪽 끝 차단선: 불타는 버스 + 차 잔해 (+ 넘어갈 수 없는 COL 벽)
bus_wreck(-2.0, -151.5, 84)
car(5.8, -150.2, -35, wreck=True)
cheap_barricade(-7.4, -149.0, 10)
C.col(-9.0, 9.0, -153.6, -151.6, -0.2, 4.0)
C.fx("smoke_03", (-2.0, -151.5, 2.4), strength=1.0)
C.fx("smoke_04", (5.8, -150.2, 1.0), strength=0.8)

# ================================================================== 서남 소공원 (낮은 화단·벤치, 나무는 서쪽 가장자리)
C.group("south")
mk.tree(C, -26.0, -11.5, h=5.2, seed=3)
mk.tree(C, -25.0, -22.5, h=4.8, seed=7)
mk.planter(C, -17.5, -12.5, -21.0, -20.0, h=0.5)
mk.planter(C, -15.0, -12.0, -12.0, -11.0, h=0.5)
mk.bench(C, -20.5, -15.6, yaw=180)
mk.bench(C, -11.0, -26.6, yaw=0)
sign_post(-9.6, -27.2, "남서 소공원", yaw=-90, w=1.3)
mk.trash_bin(C, -10.0, -16.0)
mk.vending(C, -29.4, -14.0, yaw=90, key="red")
C.col(-29.84, -28.96, -14.42, -13.58, 0, 1.6)

# ================================================================== 1선 「교차로」
C.group("junction")
L1Y = -9.6
for x in (-4.4, -2.6, 2.6, 4.4):
    riot_barricade(x, L1Y, 0, label=True)
sandbags(0.0, L1Y + 0.2, 0, n=3)
sandbags(-7.2, L1Y + 0.4, 0, n=4)
sandbags(7.2, L1Y + 0.4, 0, n=4)
# 버려진 시민 차량 (교차로 안 = 분대 엄폐, 옆길 = 측면 엄폐)
car(-3.6, -3.0, 70, "white")
car(6.6, -3.6, -15, "red")
car(-16.0, -1.6, 92, "hazard", taxi=True)
car(17.0, -1.8, -88, "mint")
# 버스 정류장 (상가 거리 동쪽 보도, 남쪽 끝 광고판이 높은 엄폐)
bus_stop(6.6, 8.4, 10.4, 14.5)
# 경보등 (미션이 켬)
for i, (x, y) in enumerate(((-8.2, -5.4), (8.2, -5.4), (-8.2, 5.4), (8.2, 5.4), (-8.3, -22.0), (8.3, -40.6))):
    alert_pole(f"alert_{i + 1:02d}", x, y, blink=0.6 + 0.07 * i)
for (x, y) in ((-8.0, 4.0), (8.0, 9.0)):
    mk.lamp(C, x, y, lit=True)
mk.cctv_pole(C, -8.4, -4.0, yaw=200)
sign_post(-8.4, 7.4, "남서교차로", "SW JCT", yaw=0)
# 모나티엄 표지는 미국 단위계 (docs/i18n/glossary.md 「도량형」). 판이 동쪽 건물 벽(x≈9.2)에 묻히지 않게 기둥을 길 쪽으로
sign_post(8.0, 17.0, "남서광장역 130 yd", "SW SQUARE STN", yaw=0, w=2.0)
# 동서 옆길: 가로등, 끝의 잔해
for x in (16.0, 34.0, 50.0):
    mk.lamp(C, x, 3.4)
    mk.lamp(C, -x, -3.4)
car(-52.0, 1.2, 120, wreck=True)
car(52.5, -1.0, -60, wreck=True)
cheap_barricade(-55.0, -2.6, 90)
cheap_barricade(55.0, 2.6, -90)
C.fx("smoke_05", (-52.0, 1.2, 1.0), strength=0.7)
C.fx("smoke_06", (52.5, -1.0, 1.0), strength=0.7)

# ================================================================== 상가 거리 (교차로 → 2선 → 광장)
C.group("north")
for y in (18.0, 34.0, 58.0, 72.0, 88.0, 102.0):
    mk.lamp(C, -3.6, y, lit=True)
    mk.lamp(C, 3.6, min(y + 6.0, 98.0), lit=True)
for (x, y, lod) in ((-6.6, 16.0, 1), (-6.6, 28.0, 1), (-6.6, 76.0, 1), (-6.6, 90.0, 1), (-6.6, 101.0, 1),
                    (6.6, 22.0, 1), (6.6, 32.0, 1), (6.6, 78.0, 1), (6.6, 90.0, 1), (6.6, 102.0, 1)):
    mk.planter(C, x - 0.8, x + 0.8, y - 0.8, y + 0.8, h=0.4, hedge=False)
    mk.tree(C, x, y, h=4.6, seed=int(y * 3 + x), z=0.4, lod=lod)
car(4.3, 27.0, 180, "red")
car(-4.3, 33.0, 0, "mint")
car(-4.3, 84.0, 4, "white")
car(4.4, 96.0, 176, "navy_l")
car(-20.0, 47.6, -90, "coral")
car(20.0, 44.2, 90, "white")
mk.vending(C, -8.4, 30.5, yaw=90)
C.col(-8.72, -8.0, 30.0, 31.0, 0, 1.6)
mk.bench(C, 8.2, 36.0, yaw=-90)
mk.trash_bin(C, -8.2, 86.5)
sign_post(-8.4, 41.0, "광장로", yaw=0)
mk.holo_ad(C, (-16.0, 87.0, 16.0), (1, 0, 0), 7.0, 3.0, "모나티엄 갓 탤런트")
# 광장로 끝 (습격차 진입로 양 끝)
cheap_barricade(-28.6, 41.8, 90)
cheap_barricade(28.6, 50.2, -90)

# ================================================================== 2선 「상가」 (y=60): 넘어진 화물차 + 보급 상자
C.group("north")
L2Y = 59.5
overturned_truck(-8.6, -2.5, L2Y)            # x -8.6..-2.4, y 59.5..62.1 (높이 2.0)
# 가운데 x -2.4..3.0 = 차량 통로 (VEH_apc2)
riot_crate(3.85, 60.4, 0.0, label="진압반 보급")
riot_crate(4.85, 60.4, 0.0)
riot_crate(4.35, 60.4, 0.75, w=0.85, d=0.95, h=0.7, label="SUPPRESSION UNIT SUPPLY")
C.col(3.4, 5.3, 59.9, 60.9, 0.0, 1.45)
sandbags(7.0, 60.4, 0, n=4)
# 발사기 상자 (긴 화기 상자, 위에 PICKUP_launcher)
riot_crate(4.4, 62.6, 0.0, w=1.4, d=0.55, h=0.5, key="violet_d")
C.text("white", "발사기 · LAUNCHER", 0.07, (4.4, 62.6 - 0.276, 0.3), (0, -1, 0), lift=0.012)
C.col(3.7, 5.1, 62.32, 62.88, 0.0, 0.5)
L2_AMMO_TOP = ammo_crate(-5.6, 63.5, yaw=10)
kiosk(-6.4, 71.0)
mk.planter(C, 5.4, 7.8, 71.5, 72.4, h=0.55)
alert_pole("alert_07", -8.3, 57.0, blink=0.66)
alert_pole("alert_08", 8.3, 57.0, blink=0.74)

# ================================================================== 남서광장 (역 앞 마지막 방어선)
C.group("plaza")
L3Y = 114.6
for x in (-7.8, -2.4, 2.4, 7.8):
    riot_barricade(x, L3Y, 0, label=(abs(x) < 3))
sandbags(-5.1, L3Y + 0.2, 0, n=4)
sandbags(5.1, L3Y + 0.2, 0, n=4)
for (sx, yaw) in ((-1, -90), (1, 90)):
    for y in (120.4, 122.2):
        riot_barricade(sx * 23.0, y, yaw)
    sandbags(sx * 23.2, 125.8, yaw, n=4)
for (x, y) in ((-20.0, 112.6), (20.0, 112.6), (-20.0, 155.0), (20.0, 155.0)):
    mk.planter(C, x - 1.4, x + 1.4, y - 1.4, y + 1.4, h=0.5, hedge=False)
    mk.tree(C, x, y, h=5.2, seed=int(x + y), z=0.5, lod=1)
mk.planter(C, -17.0, -12.5, 140.0, 141.0, h=0.5)
mk.planter(C, 12.5, 17.0, 140.0, 141.0, h=0.5)
mk.bench(C, -16.0, 150.0, yaw=180)
mk.bench(C, 16.0, 150.0, yaw=180)
mk.bench(C, -24.6, 145.0, yaw=-90)
mk.vending(C, -25.3, 136.5, yaw=90, key="teal")
C.col(-25.72, -25.0, 136.0, 137.0, 0, 1.6)
for (x, y) in ((-10.0, 110.6), (10.0, 110.6), (-10.0, 146.0), (10.0, 146.0), (-24.0, 152.0), (24.0, 152.0)):
    mk.lamp(C, x, y, lit=True)
mk.cctv_pole(C, -24.8, 110.8, yaw=-140)
sign_post(-9.6, 108.6, "남서광장", "SW SQUARE", yaw=0)
alert_pole("alert_09", -6.0, 128.0, blink=0.62)
alert_pole("alert_10", 6.0, 128.0, blink=0.7)
ST_AMMO_TOP = ammo_crate(-4.6, 125.5, yaw=-8)
ammo_crate(-4.0, 126.1, yaw=4)
riot_crate(-5.6, 126.3, 0.0, label="진압반 보급")
C.col(-6.06, -5.14, 125.79, 126.81, 0, 0.76)

# ================================================================== 남서광장역 출입구 + 계단 + 대합실 + 셔터
C.group("station")
Y0 = ST_Y0
HW = ST_HW
WT = 0.25                      # 벽 두께
ZB = -4.5                      # 대합실 바닥
NSTEP = 29                     # 0.15 m × 29단 + 계단참 = 4.5 m
TREAD = 0.30
Y1 = Y0 + NSTEP * TREAD        # 계단 아래 끝 (계단참 시작)
YS = Y0 + 10.0                 # 셔터 면
YC = YS + 4.6                  # 대합실 뒷벽
CW = 3.0                       # 대합실 반폭
YCUT = Y0 + 6.0                # 지하 천장 시작 (그 앞은 지붕 덮개 아래 트인 계단)
Z_CEIL_ST = -0.9               # 계단 통로 천장
Z_CEIL_CC = -1.6               # 대합실 천장
TILE = "mullion"               # 지하 벽 타일 (차가운 회청색: 지상의 따뜻한 석재와 갈린다)
CEIL = "concrete"

# 계단 (보이는 단: COL 없음, 아래 매끈한 경사 COL이 받는다)
for i in range(NSTEP):
    zt = -(i + 1) * 0.15
    ya = Y0 + i * TREAD
    C.box("stone_d", -HW, HW, ya, ya + TREAD + 0.01, -4.8, zt)
    C.strip("hazard", (-HW + 0.08, ya + 0.04, zt), (HW - 0.08, ya + 0.04, zt), 0.05, lift=0.006)
C.box("pave", -HW, HW, Y1, YS, -4.8, ZB)                        # 계단참
C.col(-HW, HW, Y0 + 8.85, YS + 0.2, -4.8, ZB)


def col_prism_yz(name, x0, x1, prof):
    """YZ 단면 다각형을 x0..x1로 세운 COL 메시 (경사로)."""
    b = bmesh.new()
    lo = [b.verts.new((x0, y, z)) for (y, z) in prof]
    hi = [b.verts.new((x1, y, z)) for (y, z) in prof]
    n = len(prof)
    b.faces.new(list(reversed(lo)))
    b.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces[:])
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    C.add_node(o)
    return o


# 경사 COL: 단 앞 끝과 뒤 끝 사이(7.5 cm 아래)를 지나는 26.6° 경사. 캡슐이 단에 걸리지 않는다
RAMP_END = Y0 + 8.85
col_prism_yz("COL_station_stairs", -HW, HW,
             [(Y0 - 0.02, -0.075), (RAMP_END, ZB), (RAMP_END, -4.8), (Y0 - 0.02, -4.8)])

# 계단 옆벽: 지상 부분(낮은 남색 벽, 유리 난간) + 지하 부분(흰 타일 벽, 청록 띠, 손잡이)
for s in (-1, 1):
    xa, xb = sorted((s * HW, s * (HW + WT)))
    # 타일 벽 윗면은 광장 판석 윗면(0)보다 6 mm 아래, 남색 낮은 벽은 그 높이부터 (같은 평면 겹침 방지)
    C.box(TILE, xa, xb, Y0 - 0.25, YS - 0.15, -4.8, -0.006)
    C.box("navy", xa, xb, Y0 - 0.25, YCUT + 0.3, -0.006, 1.05)
    C.box("steel", xa - 0.03, xb + 0.03, Y0 - 0.28, YCUT + 0.33, 1.05, 1.12, kind="detail")
    C.col(xa, xb, Y0 - 0.25, YCUT + 0.3, -4.8, 1.12)
    C.col(xa, xb, YCUT + 0.3, YS, -4.8, -0.3)
    xi = s * HW
    n_in = (-s, 0, 0)
    C.strip("teal", (xi, Y0 - 0.2, 0.55), (xi, Y1, ZB + 0.55), 0.14, n_in, lift=0.01)
    C.strip("navy", (xi, Y0 - 0.2, -0.05), (xi, Y1, ZB - 0.05), 0.2, n_in, lift=0.01)
    C.strip("teal", (xi, Y1, ZB + 0.55), (xi, YS - 0.2, ZB + 0.55), 0.14, n_in, lift=0.01)
    C.beam("steel", (xi - s * 0.07, Y0 - 0.2, 0.78), (xi - s * 0.07, Y1 + 0.3, ZB + 0.78), 0.05, 0.05, kind="detail")
    for k in range(4):
        t = (k + 0.5) / 4
        yy = Y0 - 0.2 + (Y1 + 0.3 - Y0 + 0.2) * t
        zz = 0.78 + (ZB + 0.78 - 0.78) * t
        C.beam("steel", (xi, yy, zz), (xi - s * 0.07, yy, zz), 0.03, 0.03, kind="detail")
    # 지상 유리 난간 (양면)
    xo = s * (HW + WT / 2)
    for nn in ((1, 0, 0), (-1, 0, 0)):
        C.rect("glass_a", (xo, (Y0 + YCUT) / 2, 1.75), nn, YCUT - Y0 + 0.4, 1.3, lift=WT / 2 + 0.01)
# 뒤쪽 막음 (지상 뒷벽 + 유리, 지하 천장 시작 테)
C.box("navy", -HW - WT, HW + WT, YCUT, YCUT + 0.3, 0.0, 1.05)
C.box("steel", -HW - WT - 0.03, HW + WT + 0.03, YCUT - 0.03, YCUT + 0.33, 1.05, 1.12, kind="detail")
for nn in ((0, 1, 0), (0, -1, 0)):
    C.rect("glass_a", (0, YCUT + 0.15, 1.8), nn, 2 * (HW + WT), 1.4, lift=0.16)
C.col(-HW - WT, HW + WT, YCUT, YCUT + 0.3, 0.0, 2.6)
C.box(CEIL, -HW, HW, YCUT, YS - 0.15, Z_CEIL_ST, -0.3)            # 계단 통로 천장
C.rect("lamp", (0, (YCUT + YS) / 2, Z_CEIL_ST), (0, 0, -1), 0.5, YS - YCUT - 0.8, up=(0, 1, 0), lift=0.012)
# 지붕 덮개: 기둥 4개 + 유리 지붕 + 정면 간판띠
for (px, py) in ((-HW - WT / 2, Y0 - 0.45), (HW + WT / 2, Y0 - 0.45), (-HW - WT / 2, YCUT + 0.15),
                 (HW + WT / 2, YCUT + 0.15)):
    C.cyl("metal", (px, py, 0.0), (px, py, 2.6), 0.07, segs=8, kind="detail")
C.box("glass_d", -HW - 0.45, HW + 0.45, Y0 - 0.6, YCUT + 0.4, 2.56, 2.66)
C.box("teal", -HW - 0.5, HW + 0.5, YCUT + 0.25, YCUT + 0.45, 2.5, 2.72, kind="detail")
C.box("navy", -HW - 0.5, HW + 0.5, Y0 - 0.8, Y0 - 0.55, 2.12, 2.82)
C.box("teal", -HW - 0.52, HW + 0.52, Y0 - 0.82, Y0 - 0.53, 2.06, 2.14, kind="detail")
FS = (0, -1, 0)
C.text("white", "남서광장역", 0.34, (0.25, Y0 - 0.8, 2.56), FS)
C.text("cyan_hot", "SOUTHWEST SQUARE · 서부선 WEST LINE", 0.105, (0.0, Y0 - 0.8, 2.26), FS)
C.decal("teal", hw.circle(0.25, 16), (-1.62, Y0 - 0.8, 2.48), FS)
C.text("white", "서", 0.26, (-1.62, Y0 - 0.8, 2.48), FS, lift=0.02)
# 역 표지 기둥 (청록 원판 + 이름판)
PX, PY = -3.4, Y0 - 0.6
C.box("navy", PX - 0.2, PX + 0.2, PY - 0.2, PY + 0.2, 0.0, 2.9, kind="detail")
C.col(PX - 0.2, PX + 0.2, PY - 0.2, PY + 0.2, 0.0, 2.9)
C.cyl("teal", (PX, PY - 0.06, 3.35), (PX, PY + 0.06, 3.35), 0.42, segs=20, kind="detail")
C.box("navy", PX - 0.6, PX + 0.6, PY - 0.21, PY + 0.21, 2.15, 2.7, kind="detail")
for sgn in (-1, 1):
    C.text("white", "서", 0.42, (PX, PY + sgn * 0.065, 3.35), (0, sgn, 0), lift=0.01)
C.text("white", "남서광장역", 0.17, (PX, PY - 0.21, 2.43), FS, lift=0.01)

# 셔터 벽 (계단참 ↔ 대합실). 가운데 x ±1.5, 높이 2.0 m가 셔터 자리 (COL 없음: 셔터가 직접 막는다)
SH_TOP = ZB + 2.0
C.box(TILE, -CW - WT, -HW, YS - 0.15, YS + 0.15, -4.8, -0.3)
C.box(TILE, HW, CW + WT, YS - 0.15, YS + 0.15, -4.8, -0.3)
C.box(TILE, -HW, HW, YS - 0.15, YS + 0.15, SH_TOP, -0.3)
C.col(-CW - WT, -HW, YS - 0.15, YS + 0.15, -4.8, -0.3)
C.col(HW, CW + WT, YS - 0.15, YS + 0.15, -4.8, -0.3)
C.col(-HW, HW, YS - 0.15, YS + 0.15, SH_TOP, -0.3)
C.box("metal", -HW - 0.05, HW + 0.05, YS - 0.42, YS - 0.15, SH_TOP, SH_TOP + 0.5, kind="detail")   # 셔터 통
for s in (-1, 1):
    C.box("metal", s * HW - 0.06 if s > 0 else -HW, s * HW if s > 0 else -HW + 0.06, YS - 0.2, YS - 0.08, ZB,
          SH_TOP, kind="detail")
C.rect("hazard", (0, YS - 0.15, SH_TOP + 0.12), FS, 2 * HW - 0.2, 0.14, lift=0.012)
C.text("white", "셔터 · 비상시 폐쇄", 0.1, (0, YS - 0.42, SH_TOP + 0.26), FS, lift=0.012)


def build_shutter(b):
    """롤 셔터 (닫힌 모습: 바닥까지 내려옴). 골판 = 번갈아 앞뒤로 어긋난 살."""
    n = 12
    hh = (SH_TOP - ZB) / n
    for k in range(n):
        za = ZB + k * hh
        off = 0.012 if k % 2 else -0.012
        mk._bm_box(b, -HW + 0.02, HW - 0.02, YS - 0.03 + off, YS + 0.03 + off, za, za + hh + 0.004)
    mk._bm_box(b, -HW + 0.02, HW - 0.02, YS - 0.05, YS + 0.05, ZB, ZB + 0.09)
    mk._bm_box(b, -0.25, 0.25, YS - 0.08, YS - 0.05, ZB + 0.12, ZB + 0.16)


C.special("DOOR_shutter", build_shutter, "concrete_d", props={"move": "0,2.4,0", "door": "shutter",
                                                          "label": "남서광장역 셔터"})

# 대합실 (계단참 너머 6 × 4.6 m): 바닥 타일, 벽, 천장 조명, 개찰구, 표지
mk.paving(C, -CW, CW, YS - 0.15, YC, z=ZB, key="pave", grout="pave_d", tile=0.6, t=0.3)
for (x0, x1, y0, y1) in ((-CW - WT, -CW, YS, YC + WT), (CW, CW + WT, YS, YC + WT), (-CW - WT, CW + WT, YC, YC + WT)):
    C.box(TILE, x0, x1, y0, y1, -4.8, -0.3)
    C.col(x0, x1, y0, y1, -4.8, -0.3)
C.box(CEIL, -CW, CW, YS + 0.15, YC, Z_CEIL_CC, -0.3)
for xx in (-1.6, 1.6):
    C.rect("lamp", (xx, (YS + YC) / 2, Z_CEIL_CC), (0, 0, -1), 0.4, YC - YS - 0.9, up=(0, 1, 0), lift=0.012)
for (cx_, nn, L) in ((-CW, (1, 0, 0), YC - YS), (CW, (-1, 0, 0), YC - YS)):
    C.rect("teal", (cx_, (YS + YC) / 2, ZB + 1.25), nn, L, 0.14, lift=0.01)
    C.rect("navy", (cx_, (YS + YC) / 2, ZB + 0.1), nn, L, 0.2, lift=0.01)
C.rect("teal", (0, YC, ZB + 1.25), (0, -1, 0), 2 * CW, 0.14, lift=0.01)
C.rect("navy", (0, YC, ZB + 0.1), (0, -1, 0), 2 * CW, 0.2, lift=0.01)
# 뒷벽: 승강장 내려가는 어두운 입구 + 표지
C.decal("steel", hw.rrect(2.3, 2.05, 0.2, 2), (0, YC, ZB + 1.02), (0, -1, 0), lift=0.01)
C.decal("dark", hw.rrect(2.0, 1.9, 0.16, 2), (0, YC, ZB + 0.95), (0, -1, 0), lift=0.014)
C.plate("navy", hw.rrect(3.6, 0.62, 0.12, 2), (0, YC, ZB + 2.55), (0, -1, 0), 0.05, kind="detail")
C.text("white", "서부선 승강장", 0.2, (-0.25, YC - 0.05, ZB + 2.64), (0, -1, 0), lift=0.012)
C.text("glow", "WEST LINE · PLATFORMS", 0.09, (-0.25, YC - 0.05, ZB + 2.42), (0, -1, 0), lift=0.012)
C.decal("teal", [(-0.12, 0.12), (0.12, 0.12), (0.12, -0.02), (0.22, -0.02), (0.0, -0.22), (-0.22, -0.02),
                 (-0.12, -0.02)], (1.45, YC - 0.05, ZB + 2.55), (0, -1, 0), lift=0.014)
# 서쪽 벽: 역 이름판, 동쪽 벽: 노선도
C.plate("navy", hw.rrect(2.4, 0.56, 0.1, 2), (-CW, YS + 1.4, ZB + 2.1), (1, 0, 0), 0.04, kind="detail")
C.text("white", "남서광장", 0.24, (-CW + 0.05, YS + 1.4, ZB + 2.1), (1, 0, 0), lift=0.012)
C.plate("white", hw.rrect(2.2, 1.1, 0.06, 2), (CW, YS + 1.5, ZB + 1.7), (-1, 0, 0), 0.03, kind="detail")
C.strip("teal", (CW - 0.04, YS + 0.55, ZB + 1.7), (CW - 0.04, YS + 2.45, ZB + 1.7), 0.06, (-1, 0, 0), lift=0.01)
C.strip("violet", (CW - 0.04, YS + 1.9, ZB + 1.35), (CW - 0.04, YS + 1.9, ZB + 2.1), 0.06, (-1, 0, 0), lift=0.012)
for k in range(6):
    C.rect("navy", (CW - 0.04, YS + 0.6 + k * 0.36, ZB + 1.7), (-1, 0, 0), 0.08, 0.08, lift=0.016)
# 개찰구 (y = YS+3.0): 남색 함 5개 + 시안 윗면 + 닫힌 날개. 지나갈 수 없다 (레벨 끝)
YG = YS + 3.0
for gx in (-2.88, -1.44, 0.0, 1.44, 2.88):
    C.box("navy", gx - 0.12, gx + 0.12, YG - 0.55, YG + 0.55, ZB, ZB + 0.95)
    C.box("steel", gx - 0.13, gx + 0.13, YG - 0.56, YG + 0.56, ZB + 0.95, ZB + 1.0, kind="detail")
    C.rect("glow", (gx, YG - 0.3, ZB + 1.0), (0, 0, 1), 0.16, 0.22, up=(0, 1, 0), lift=0.004)
for gx in (-2.16, -0.72, 0.72, 2.16):
    for s in (-1, 1):
        C.box("glass_a", gx + s * 0.6 - (0.42 if s > 0 else 0.0), gx + s * 0.6 + (0.0 if s > 0 else 0.42),
              YG - 0.02, YG + 0.02, ZB + 0.45, ZB + 0.85)
C.col(-CW, CW, YG - 0.12, YG + 0.12, ZB, ZB + 1.3)
for gx in (-2.88, -1.44, 0.0, 1.44, 2.88):
    C.col(gx - 0.12, gx + 0.12, YG - 0.55, YG + 0.55, ZB, ZB + 1.0)
# 셔터가 열렸을 때 셔터 위 끝(z -0.1)은 광장 판석(-0.3..0) 안에 숨는다

# ================================================================== 마커: 플레이어·구역·분대
C.group("markers")


def M_(name, x, y, z=None, *, face=None, look=None, yaw=None, **props):
    C.marker(name, (x, y, gz(x, y) if z is None else z), face=face, look=look, yaw=yaw, props=props or None)


# 스폰
M_("SPAWN_player", 1.0, -4.6, face=face_s(1.0, -4.6))
M_("SPAWN_line2", 0.6, 66.0, face=face_s(0.6, 66.0))
M_("SPAWN_station", 0.0, 119.5, face=face_s(0.0, 119.5))
# 목표
M_("MARK_line1", 0.0, L1Y, face=face_s(0.0, L1Y))
M_("MARK_line2", 0.3, 61.0, face=face_s(0.3, 61.0))
M_("MARK_station", 0.0, Y0 - 0.4, 0.0, face=face_n(0.0, Y0))
M_("MARK_station_in", 0.0, YS - 0.7, ZB, face=face_n(0.0, YS))
M_("MARK_gate_a", GATE_C[0], GATE_C[1], GATE_C[2], gate="GATE_a", radius=GATE_R)
# 분대 자리
HOLD = {
    "line1": ((0.0, -7.6), {"sabre": (-4.4, -8.6), "rona": (2.6, -8.6), "jesty": (7.2, -8.2), "karen": (-7.2, -8.2)}),
    "line2": ((0.3, 63.6), {"sabre": (-5.4, 63.0), "rona": (-3.2, 62.8), "jesty": (4.6, 61.6), "karen": (7.0, 61.3)}),
    "station": ((0.0, 117.0), {"sabre": (-5.1, 115.8), "rona": (5.1, 115.8), "jesty": (-12.0, 117.0),
                               "karen": (12.0, 117.0)}),
}
for sec, ((hx, hy), who) in HOLD.items():
    M_(f"MARK_hold_{sec}", hx, hy, face=face_s(hx, hy))
    for w, (x, y) in who.items():
        M_(f"MARK_hold_{sec}_{w}", x, y, face=face_s(x, y))
for w, (x, y) in {"sabre": (-4.4, -6.6), "rona": (2.6, -6.6), "jesty": (6.8, -6.4), "karen": (-6.8, -6.4)}.items():
    M_(f"ALLY_{w}", x, y, face=face_s(x, y), who=w, behavior="hold", weapon="monatium_riot_carbine")
# 광장의 칸나와 진압반
M_("ALLY_kanna", 9.0, 121.5, face=face_s(9.0, 121.5), who="kanna", behavior="hold")
for i, (x, y, fx, fy) in enumerate(((-7.8, 115.6, -7.8, 100.0), (7.8, 115.6, 7.8, 100.0),
                                    (-21.8, 121.3, -40.0, 121.3), (21.8, 121.3, 40.0, 121.3))):
    M_(f"ALLY_riot_{i + 1:02d}", x, y, face=(fx, fy), who="riot", behavior="hold", weapon="monatium_riot_carbine")
M_("VEH_kanna_apc", 13.5, 124.5, face=(13.5, 100.0), vehicle="monatium_riot_apc", faction="ally", state="ready")
# 집기
M_("PICKUP_launcher", 4.4, 62.6, 0.54, yaw=90, weapon="monatium_riot_launcher", lay="side")
M_("PICKUP_ammo_l2", -5.6, 63.5, L2_AMMO_TOP + 0.04, yaw=100, weapon="ammo", lay="side")
M_("PICKUP_ammo_st", -4.6, 125.5, ST_AMMO_TOP + 0.04, yaw=82, weapon="ammo", lay="side")
# 엄폐 지점 (-Y = 적 쪽)
COVERS = {
    "l1": [(-4.4, -8.7, "low"), (-2.6, -8.7, "low"), (0.0, -8.5, "low"), (2.6, -8.7, "low"), (4.4, -8.7, "low"),
           (-7.2, -8.3, "low"), (7.2, -8.3, "low"), (-3.4, -0.5, "high")],
    "l2": [(-7.6, 62.9, "high"), (-5.4, 62.9, "high"), (-3.2, 62.7, "high"), (3.9, 61.4, "high"), (6.3, 61.2, "low"),
           (7.8, 61.2, "low"), (-6.4, 72.3, "high"), (6.6, 73.0, "low")],
    "st": [(-2.4, 115.5, "low"), (2.4, 115.5, "low"), (-5.1, 115.4, "low"), (5.1, 115.4, "low"), (-7.8, 115.5, "low"),
           (7.8, 115.5, "low"), (-22.3, 121.3, "low"), (22.3, 121.3, "low")],
}
for sec, pts in COVERS.items():
    for i, (x, y, h) in enumerate(pts):
        f = face_s(x, y)
        if sec == "st" and abs(x) > 20:
            f = (x * 3, y)
        M_(f"COVER_{sec}_{i + 1:02d}", x, y, face=f, height=h)
# 트리거
trig("line2", -8.8, 8.8, 56.0, 66.5, -0.6, 3.0)
trig("station", -9.0, 9.0, 124.0, 140.5, -1.0, 3.5)
trig("station_in", -CW, CW, YS + 0.3, YG - 0.35, ZB - 0.5, ZB + 3.0)

# ================================================================== 적 (전부 spawn=manual)
C.group("enemies")
RIFLE = {"rifleman_a": "r41_carbine", "rifleman_b": "r41_carbine", "rifleman_c": "r41_dmr", "assault": "r41_suppressor",
         "riot": "r41_sidearm", "officer": "r41_sidearm"}


def enemy(group, i, kind, x, y, behavior, *, z=None, face=None, path=None):
    p = {"kind": kind, "group": group, "behavior": behavior, "spawn": "manual"}
    if kind in RIFLE:
        p["weapon"] = RIFLE[kind]
    if path:
        p["path"] = path
    M_(f"ENEMY_{group}_{i:02d}", x, y, z, face=face or face_n(x, y), **p)


W1 = [("rifleman_a", -6.8, -56.0), ("rifleman_b", -3.0, -60.0), ("rifleman_c", 6.6, -54.0), ("rifleman_a", -6.4, -70.0),
      ("rifleman_b", 7.4, -66.0), ("rifleman_c", -7.0, -84.0), ("rifleman_a", 1.0, -88.0), ("rifleman_b", 6.2, -95.0),
      ("assault", -1.6, -63.0), ("assault", 2.0, -77.0)]
for i, (k, x, y) in enumerate(W1, 1):
    enemy("w1", i, k, x, y, "rush" if k == "assault" else "advance")
for i, (x, y) in enumerate(((38.0, -1.8), (42.0, 1.6), (46.0, -2.2)), 1):
    enemy("w1_flank", i, ("rifleman_a", "rifleman_b", "rifleman_c")[i - 1], x, y, "flank", face=(0.0, y))
for i, (x, y, z) in enumerate(((-2.5, -58.0, 10.0), (3.5, -72.0, 11.0)), 1):
    enemy("w1_drone", i, "drone", x, y, "advance", z=z)
W2 = [("rifleman_a", -6.4, 2.0), ("rifleman_b", 5.0, -0.6), ("rifleman_c", -14.0, 4.4), ("rifleman_a", 15.0, -4.0),
      ("rifleman_b", -6.6, 16.0), ("rifleman_c", 6.0, 20.0), ("rifleman_a", -5.0, 28.0), ("rifleman_b", 5.6, 31.0),
      ("riot", -1.6, 12.0), ("riot", 1.8, 14.0), ("riot", 0.0, 22.0), ("officer", 0.4, 5.0)]
for i, (k, x, y) in enumerate(W2, 1):
    enemy("w2", i, k, x, y, "advance")
for i, (x, y, z) in enumerate(((-2.0, 44.0, 9.0), (2.5, 50.0, 10.0), (0.0, 56.0, 11.5)), 1):
    enemy("w2_drone", i, "drone", x, y, "advance", z=z)
W3 = [("rifleman_a", -6.4, 84.0), ("rifleman_b", 6.4, 88.0), ("assault", -1.6, 92.0), ("riot", 1.6, 96.0),
      ("rifleman_c", -5.8, 100.0), ("rifleman_a", -40.0, 121.5), ("assault", -36.0, 126.5), ("riot", -44.0, 124.0),
      ("rifleman_b", 40.0, 126.5), ("rifleman_c", 36.0, 121.5)]
for i, (k, x, y) in enumerate(W3, 1):
    f = (0.0, y) if abs(x) > 20 else None
    enemy("w3", i, k, x, y, "rush" if k == "assault" else ("flank" if abs(x) > 20 else "advance"), face=f)
for i, (x, y, z) in enumerate(((-6.0, 100.0, 12.0), (5.0, 104.0, 13.0), (0.0, 96.0, 14.0)), 1):
    enemy("w3_drone", i, "drone", x, y, "advance", z=z)

# 차량 + 경로 (WP_ 높이 = 차도 면)
PATHS = {
    "apc1": [(3.0, -140.0), (3.0, -112.0), (3.0, -80.0), (3.0, -52.0), (2.8, -34.0)],
    "apc2": [(52.0, 1.4), (20.0, 1.4), (8.0, 2.0), (2.4, 7.0), (0.4, 16.0), (0.4, 44.0), (0.4, 61.0), (0.4, 80.0),
             (0.4, 93.0)],
    "raider1": [(27.0, 47.6), (10.0, 47.6), (3.2, 50.5), (1.4, 54.5)],
    "raider2": [(-27.0, 44.4), (-10.0, 44.4), (-3.0, 48.0), (-1.4, 54.0)],
}
for pid, pts in PATHS.items():
    for i, (x, y) in enumerate(pts, 1):
        M_(f"WP_{pid}_{i:02d}", x, y, ZR)
VEHS = [("apc1", "r41_apc", "w1_apc"), ("raider1", "r41_raider", "w2_raider"), ("raider2", "r41_raider", "w2_raider"),
        ("apc2", "r41_apc", "w3_apc")]
for vid, veh, grp in VEHS:
    (x, y), (nx, ny) = PATHS[vid][0], PATHS[vid][1]
    M_(f"VEH_{vid}", x, y, ZR, face=(nx, ny), vehicle=veh, faction="enemy", state="ready", driver="ai", path=vid,
       group=grp, spawn="manual")

# ================================================================== 내보내기
ROOT = {
    "sky": "#bcd2e6",            # 차가운 새벽 하늘
    "fog": "80,760",
    "sun": "0.86,0.34,-0.38",    # 동북동의 낮은 해 (긴 그림자가 서쪽으로)
    "ambient": 1.25,
    "near": 0.1,
    "far": 1100,
    "music": "m1_combat",
    "sunIntensity": 2.3,
    "sunColor": "#ffcf9e",
    "hemiSky": "#cfe0f2",
    "hemiGround": "#9a8c7c",
    "timeOfDay": "dawn_0600",
}

# 검사: 사람이 서는 마커가 COL 박스 안에 있으면 경고
STAND = ("ENEMY_", "ALLY_", "COVER_", "SPAWN_", "MARK_hold", "WP_", "VEH_")
for (nm, loc, rot, props, g, sc) in C.markers:
    if not nm.startswith(STAND) or props.get("kind") == "drone":
        continue
    x, y, z = loc
    for (cn, x0, x1, y0, y1, z0, z1) in C.cols:
        if x0 < x < x1 and y0 < y < y1 and z0 < z + 0.4 < z1:
            print(f"[m1] 경고: {nm} ({x:.1f},{y:.1f},{z:.2f}) 가 {cn} 안")
            break

C.finish("levels/m1_streets.glb", root_props=ROOT, outline=0.025)

# 계약 노드 좌표표 (Blender 좌표, m)
print("[m1] ---- 계약 노드 (Blender x, y, z / -Y 정면 yaw°) ----")
counts = {}
for (nm, loc, rot, props, g, sc) in C.markers:
    pre = nm.split("_")[0]
    if pre == "ENEMY":
        grp = props.get("group")
        counts.setdefault(grp, {}).setdefault(props.get("kind"), 0)
        counts[grp][props.get("kind")] += 1
    if pre in ("SPAWN", "MARK", "ALLY", "VEH", "PICKUP", "COVER", "WP", "ENEMY"):
        yawd = math.degrees(rot[2]) if rot is not None else 0.0
        extra = ",".join(f"{k}={v}" for k, v in props.items() if k in ("kind", "behavior", "vehicle", "path", "weapon",
                                                                       "height", "who", "group"))
        print(f"[m1] {nm:28s} ({loc[0]:7.1f},{loc[1]:7.1f},{loc[2]:6.2f}) yaw {yawd:6.1f}  {extra}")
for nm, bx in TRIGS:
    print(f"[m1] {nm:28s} x {bx[0]:.1f}..{bx[1]:.1f}  y {bx[2]:.1f}..{bx[3]:.1f}  z {bx[4]:.1f}..{bx[5]:.1f}")
print(f"[m1] DOOR_shutter                 x {-HW + 0.02:.2f}..{HW - 0.02:.2f}  y {YS:.2f}  z {ZB:.1f}..{SH_TOP:.1f}  "
      f"move 0,2.4,0 (three.js)")
print(f"[m1] GATE_a center {GATE_C} radius {GATE_R} tilt 68 yaw {GATE_YAW:.1f}")
for grp, ks in counts.items():
    print(f"[m1] ENEMY group {grp}: " + ", ".join(f"{k}×{n}" for k, n in ks.items()) + f" = {sum(ks.values())}")
