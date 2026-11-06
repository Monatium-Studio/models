"""알프토반 관측 지점 키트 (overlook_kit): 3막 M8 「관측수」의 고가 고속도로, 관측탑, 원경.

모나티엄-에르피엔 고속도로(알프토반)의 고가 상판과 그 위에 버려진 차들, 무너진 경간, 고속도로 관제·정비탑(관측 지점),
삼각대 관측 장비(레이저 거리측정·지시기), 바람자루, 그리고 수 km 원경(밭이 있는 평야, 에르피엔 실루엣, 세계수,
정령산과 감시 초소, R41 진지·발사장, 연기, 구름, 새벽 하늘 돔)을 만든다.

- 조립기·팔레트·프리미티브는 monatium_city_kit(mk)를 그대로 쓴다 (mk.City, mk.M, mk.PAL). mk 파일은 고치지 않고,
  이 키트가 쓰는 색은 import 때 mk.PAL에 더한다(런타임만).
- 노드 규칙: docs/LEVELS.md, 전투 마커: docs/COMBAT.md 2장. 도시 키트 규약: docs/art/monatium-city.md.
- 좌표: Blender Z-up, 1 BU = 1 m, +X 동, +Y 북. 빈 오브젝트의 -Y가 정면.

체격: 엘프 기준(키 1.2 m, 점프 0.6 m, 자동 오르기 0.28 m). 방호벽 0.8 m(넘을 수 없음), 계단 단 높이 0.175~0.18 m,
난간 1.0 m, 통로 폭 1.4 m 이상.

먼 거리 깊이 정밀도: 레벨 near 0.05 / far 7000이라 수백 m 밖에서 같은 높이에 겹친 면은 깜빡인다.
원경 바닥은 겹치지 않는 한 장의 높이장(칸마다 머티리얼)이고, 길·생울타리는 0.6 m 이상 띄운 입체로 만든다.

사용:
    import monatium_city_kit as mk, overlook_kit as ok
    C = mk.City("m8_overlook")
    ok.deck(C, 0, 260, 0.0)
    ok.sign_gantry(C, 70, 0.0, ok.DECK_Z, [("에르피엔 12 mi", "ERPIEN")])
    col = ok.ColAcc()
    ...
    col.flush(C, "stairs")
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import erpien_flag as ef
import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== palette (mk.PAL에 런타임으로 더한다)
PAL = {
    # 고가 도로
    "barrier": "#dcd7cf",      # 콘크리트 방호벽 (뉴저지형)
    "deck_c": "#cfc9c2",       # 상판 콘크리트
    "girder": "#b3ada8",       # 상자형 거더·교각 (그늘진 콘크리트)
    "grate": "#77707b",        # 강재 격자 바닥 (관측탑 통로)
    "rail": "#c9c3bb",         # 아연도금 난간
    "rebar": "#8c5a44",        # 녹슨 철근
    "rubble": "#b9b2a8",       # 콘크리트 잔해
    "lamp_dead": "#8f8b86",    # 꺼진 가로등 갓 (새벽: 대부분 꺼짐)
    "soot": "#2f2b2e",         # 그을음, 불탄 차
    "gravel": "#b4ada3",       # 정비 마당 자갈
    "tyre": "#2c2830",
    "car_glass": "#33465c",
    # 버려진 민간 차량 (모나티엄 차: 둥근 차체, 밝은 단색)
    "car_white": "#efece6",
    "car_red": "#c95b4d",
    "car_blue": "#5a84b6",
    "car_teal": "#5ea89e",
    "car_yellow": "#e3c058",
    "car_gray": "#9a97a0",
    "car_cream": "#e6d8bd",
    # 평야
    "field_wheat": "#c4b47c",
    "field_green": "#8fae78",
    "field_lush": "#6d9a63",
    "field_soil": "#97826d",
    "field_fallow": "#b0a688",
    "field_flower": "#a197b2",  # 꽃밭 (엘리아스의 밝은 들판)
    "meadow": "#7ea56c",
    "forest_far": "#4b6c60",
    "mount_rock": "#8890a4",
    "mount_snow": "#cdd6e8",
    "road_far": "#76727c",
    # 에르피엔 (요정 왕국: 크림 석재 + 초록 지붕 + 금 장식, docs/art/fairy-faction.md의 초록·금·흰)
    "fairy_stone": "#cfc6bc",
    "fairy_stone_d": "#a99f98",
    "fairy_roof": "#3f7c64",
    "fairy_roof_l": "#5f9a7c",
    "fairy_roof_b": "#4d71a6",
    "fairy_roof_r": "#a86656",
    "fairy_gold": "#d9b45a",
    # 정비탑
    "tower_c": "#d5d0ca",
    "tower_band": "#706478",   # 진압반 남보라 띠 (모나티엄 시설 표식)
    # 바람자루
    "sock_o": "#ef7d3c",
    # 새벽 구름 (아래에서 동녘 빛을 받는 옅은 보라)
    "cloud_k": "#d6cbdc",
    "cloud_w": "#e9dccf",
}
GLOW = {
    "dawn_lamp": "#ffd9a0",    # 아직 켜진 가로등
    "beacon_r": "#ff5a4a",     # 항공 장애등
}
mk.PAL.update(PAL)
mk.GLOW.update(GLOW)
mk._DARK.update({"tyre", "car_glass", "soot", "grate"})

DECK_Z = 9.0          # 고가 상판 윗면
HALF = 6.6            # 상판 반폭 (방호벽 바깥면까지)
BAR_W = 0.56          # 방호벽 밑동 폭
BAR_H = 0.8           # 방호벽 높이 (엘프 점프 0.6 m로 넘지 못함)
WALL_UP = 0.0         # 방호벽 위 투명 벽 (기본 없음): 0.8 m 벽은 점프 0.6 m(공중 자동 오르기 꺼짐)로 넘지 못하고,
                      # 투명 벽은 관측탑에서 상판을 내려 쏘는 사선을 막는다(총탄 레이캐스트가 COL에 맞는다)
# 뉴저지형 방호벽 단면 (d = 바깥 모서리에서 안쪽 거리, h = 노면 기준 높이).
# 밑면은 콘크리트 판 윗면(노면 -5 cm)에 얹는다: 판 속으로 묻으면 바깥면·끝면이 판 옆면과 한 평면에 겹쳐 깜빡인다
JERSEY = [(0.0, -0.05), (BAR_W, -0.05), (BAR_W, 0.075), (0.36, 0.33), (0.24, BAR_H), (0.0, BAR_H)]


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ================================================================== 충돌 · 트리거 · 노드

class ColAcc:
    """기울어진 경사로·회전 상자 같은 축 정렬이 아닌 충돌을 한 메시(COL_<name>)로 모은다. 엔진은 COL_ 메시를
    트라이메시 충돌체로 읽는다(LevelLoader). 축 정렬 상자는 C.col()을 그대로 쓴다."""

    def __init__(self):
        self.bm = bmesh.new()

    def obox(self, p0, p1, w, z0, z1):
        """수평 선분 p0→p1(xy)을 따라 폭 w, 높이 z0..z1인 회전 상자 (대각 방호벽)."""
        a, b = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
        d = (b - a)
        if d.length < 1e-6:
            return
        d.normalize()
        n = Vector((-d.y, d.x, 0)) * (w / 2)
        q = [a - n, b - n, b + n, a + n]
        self.prism([(p.x, p.y) for p in q], z0, z1)

    def prism(self, pts, z0, z1):
        _prism_closed(self.bm, pts, z0, z1)

    def slab(self, quad_top, t=0.3):
        """윗면 네 점(3D, 반시계)으로 정한 경사 판 (두께 t). 경사로·계단 충돌."""
        top = [Vector(p) for p in quad_top]
        bot = [p - Vector((0, 0, t)) for p in top]
        vt = [self.bm.verts.new(p) for p in top]
        vb = [self.bm.verts.new(p) for p in bot]
        fs = [self.bm.faces.new(vt), self.bm.faces.new(list(reversed(vb)))]
        for i in range(4):
            j = (i + 1) % 4
            fs.append(self.bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
        bmesh.ops.recalc_face_normals(self.bm, faces=fs)

    def wall(self, p0, p1, z0, z1, t=0.08):
        """p0→p1(3D, 경사 가능) 선을 따라 세운 얇은 벽: 각 점의 높이 + z0 ~ + z1, 두께 t (선 가운데)."""
        P0, P1 = Vector(p0), Vector(p1)
        d = Vector((P1.x - P0.x, P1.y - P0.y, 0))
        if d.length < 1e-6:
            return
        d.normalize()
        n = Vector((-d.y, d.x, 0)) * (t / 2)
        q = [(P0, -1), (P1, -1), (P1, 1), (P0, 1)]
        vb = [self.bm.verts.new(P + n * s + Vector((0, 0, z0))) for (P, s) in q]
        vt = [self.bm.verts.new(P + n * s + Vector((0, 0, z1))) for (P, s) in q]
        fs = [self.bm.faces.new(vt), self.bm.faces.new(list(reversed(vb)))]
        for i in range(4):
            j = (i + 1) % 4
            fs.append(self.bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
        bmesh.ops.recalc_face_normals(self.bm, faces=fs)

    def flush(self, C, name):
        if not self.bm.faces:
            self.bm.free()
            return None
        me = bpy.data.meshes.new(f"COL_{name}")
        self.bm.to_mesh(me)
        self.bm.free()
        o = bpy.data.objects.new(f"COL_{name}", me)
        cb.link(o)
        C.add_node(o)
        self.bm = bmesh.new()
        return o


def _prism_closed(bm, pts, z0, z1):
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]
    hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    fs = [bm.faces.new(list(reversed(lo))), bm.faces.new(hi)]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)


def trig(C, tid, x0, x1, y0, y1, z0, z1, **props):
    """TRIG_<tid>: 축 정렬 상자 메시 (원점 = 중심). 렌더하지 않는다."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    o = mk._box_obj(f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    return o


def mesh_node(name, parts, *, loc=(0, 0, 0), yaw=0.0, props=None, outline=None):
    """로컬 좌표 부품(머티리얼 키 → bmesh 채우기 함수)으로 이름 있는 빈 오브젝트 + 자식 메시 트리를 만든다.
    미션이 통째로 숨기거나 돌릴 노드(GEAR_tripod)용. 자식 메시는 collider=0."""
    root = cb.empty(name, loc=loc, size=0.3)
    root.rotation_euler = (0, 0, math.radians(yaw))
    for k, v in (props or {}).items():
        root[k] = v
    for key, build in parts.items():
        b = bmesh.new()
        build(b)
        if not b.faces:
            b.free()
            continue
        me = bpy.data.meshes.new(f"{name}_{key}")
        b.to_mesh(me)
        b.free()
        o = bpy.data.objects.new(f"{name}_{key}", me)
        cb.link(o)
        cb.assign(o, mk.M(key))
        o.parent = root
        o["collider"] = 0
        if mk.is_glow(key):
            o["noOutline"] = 1
        elif outline is not None:
            o["outline"] = outline
    return root


# ================================================================== 고가 상판

def sweep(C, key, pts, inward, prof=JERSEY, *, kind="main", caps=True):
    """단면 prof(d, h)를 경로 pts(바깥 모서리, 노면 높이 3D 점)를 따라 돌출한다. inward: 안쪽 수평 방향(2D)."""
    b = C.bm(key, kind)
    I = Vector((inward[0], inward[1], 0)).normalized()
    rings = []
    for p in pts:
        P = Vector(p)
        rings.append([b.verts.new(P + I * d + Vector((0, 0, h))) for d, h in prof])
    fs = []
    n = len(prof)
    for a, c in zip(rings, rings[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            fs.append(b.faces.new((a[k], a[k2], c[k2], c[k])))
    if caps:
        fs.append(b.faces.new(list(reversed(rings[0]))))
        fs.append(b.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(b, faces=fs)


def barrier_col(C, p0, p1, inward, *, bottom=-0.25):
    """방호벽 COL_: 밑동 폭(BAR_W) 그대로 수직으로 높이 BAR_H까지, p0→p1(바깥 모서리, 노면 높이 3D 점)의 경사를
    따라 기운 상자 (볼록). 안쪽 면은 수직이어야 한다: 단면 그대로의 경사면은 점프한 캡슐이 타고 넘었다.
    예전 경사로 상자는 구간의 높은 끝 높이로 잘라 낮은 끝에서 보이는 벽보다 최대 0.4 m 솟았다."""
    I = Vector((inward[0], inward[1], 0)).normalized()
    pts = []
    for p in (p0, p1):
        P = Vector(p)
        for d in (0.0, BAR_W):
            for h in (bottom, BAR_H):
                pts.append(tuple(P + I * d + Vector((0, 0, h))))
    C.ccol(pts)


def _ranges(a0, a1, gaps):
    """a0..a1에서 gaps[(g0, g1)]를 뺀 구간들."""
    out = [(a0, a1)]
    for g0, g1 in gaps:
        nxt = []
        for s0, s1 in out:
            if g1 <= s0 or g0 >= s1:
                nxt.append((s0, s1))
                continue
            if g0 > s0:
                nxt.append((s0, g0))
            if g1 < s1:
                nxt.append((g1, s1))
        out = nxt
    return [(s0, s1) for s0, s1 in out if s1 - s0 > 0.05]


def barrier_x(C, x0, x1, y_edge, inward, z, *, col=True, wall=False, gaps=(), kind="main", end_marks=True):
    """x 방향 방호벽 (바깥 모서리 y_edge, 안쪽 부호 inward = ±1). 충돌: 벽 상자 + 그 위 투명 벽(WALL_UP)."""
    for s0, s1 in _ranges(x0, x1, gaps):
        sweep(C, "barrier", [(s0, y_edge, z), (s1, y_edge, z)], (0, inward), kind=kind)
        # 반사띠 (노란 점선 대신 얇은 띠): 위쪽 경사면
        C.strip("hazard", (s0, y_edge + inward * 0.30, z + 0.56), (s1, y_edge + inward * 0.30, z + 0.56), 0.05,
                (0, inward * 0.97, 0.24), lift=0.012)
        if end_marks:
            for xe, sg in ((s0, -1), (s1, 1)):
                if abs(xe - x0) < 0.01 or abs(xe - x1) < 0.01:
                    continue
                C.rect("hazard", (xe + sg * 0.002, y_edge + inward * 0.2, z + 0.4), (sg, 0, 0), 0.32, 0.6,
                       lift=0.01, kind="fine")
        if col:
            ya, yb = sorted((y_edge, y_edge + inward * BAR_W))
            C.col(s0, s1, ya, yb, z - 0.25, z + BAR_H)
            if wall and WALL_UP > 0:
                yc0, yc1 = sorted((y_edge, y_edge + inward * 0.12))
                C.col(s0, s1, yc0, yc1, z + BAR_H, z + BAR_H + WALL_UP)


def lane_lines(C, x0, x1, y_inner_s, y_inner_n, z, *, side="south", dash=3.0, gap=9.0, phase=0.0):
    """동행(east) 3차로: 남쪽 갓길 2.0 m + 차로 3.0×3 + 북쪽 갓길. side='north'면 서행(갓길이 북쪽)."""
    w = y_inner_n - y_inner_s
    if side == "south":
        edge_r = y_inner_s + 2.0              # 오른쪽 가장자리 흰 실선
        lanes = [edge_r + 3.0, edge_r + 6.0]  # 차로 점선
        edge_l = edge_r + 9.0                 # 왼쪽 가장자리 노란 실선
    else:
        edge_r = y_inner_n - 2.0
        lanes = [edge_r - 3.0, edge_r - 6.0]
        edge_l = edge_r - 9.0
    if not (y_inner_s < edge_l < y_inner_n):
        edge_l = None
    C.strip("line", (x0, edge_r, z), (x1, edge_r, z), 0.15, lift=0.02)
    if edge_l is not None:
        C.strip("line_y", (x0, edge_l, z), (x1, edge_l, z), 0.15, lift=0.02)
    for yl in lanes:
        x = x0 + phase
        while x < x1:
            xe = min(x + dash, x1)
            if xe - x > 0.3:
                C.strip("line", (x, yl, z), (xe, yl, z), 0.13, lift=0.02)
            x += dash + gap
    del w


def deck(C, x0, x1, yc, *, z=DECK_Z, half=HALF, south=True, north=True, gaps_s=(), gaps_n=(), lines="south",
         col=True, girder=True, kind="main", phase=0.0, wall=False, asphalt=True):
    """곧은 고가 상판 한 구간: 아스팔트 + 콘크리트 판 + 상자형 거더 + 양쪽 방호벽 + 차선. 충돌 포함.
    아스팔트는 윗면 한 장(옆면 없음): 닫힌 상자끼리 맞대면 툰 아웃라인 헐이 이음매에 검은 줄을 긋는다.
    콘크리트 판 윗면은 5 cm 아래라 먼 거리에서도 깜빡이지 않는다. asphalt=False면 윗면은 호출한 쪽이 깐다."""
    y0, y1 = yc - half, yc + half
    if asphalt:
        ya, yb = y0 + (0.3 if south else 0.0), y1 - (0.3 if north else 0.0)
        C.poly("asphalt", [(x0, ya, z), (x1, ya, z), (x1, yb, z), (x0, yb, z)], normal=(0, 0, 1), kind="fine")
    C.box("deck_c", x0, x1, y0, y1, z - 0.9, z - 0.05, kind=kind)
    if girder:
        C.box("girder", x0, x1, y0 + 2.4, y1 - 2.4, z - 2.4, z - 0.9, kind=kind)
        # 상판 처마 아래 물끊기 띠 (밖에서 보면 상판 두께가 읽힌다)
        for yy, s in ((y0, -1), (y1, 1)):
            C.strip("girder", (x0, yy, z - 0.62), (x1, yy, z - 0.62), 0.18, (0, s, 0), lift=0.01)
    if south:
        barrier_x(C, x0, x1, y0, +1, z, col=col, gaps=gaps_s, kind=kind, wall=wall)
    if north:
        barrier_x(C, x0, x1, y1, -1, z, col=col, gaps=gaps_n, kind=kind, wall=wall)
    if lines:
        lane_lines(C, x0, x1, y0 + BAR_W, y1 - BAR_W, z, side=lines, phase=phase)
    if col:
        C.col(x0, x1, y0, y1, z - 0.9, z)


def deck_far(C, x0, x1, yc, *, z=DECK_Z, half=HALF, pier_pitch=30.0, pier0=None, ground=None, kind="far",
             lamps=0.0):
    """원경 상판 (LOD): 판·거더·방호벽 윗면 상자 + 교각. ground(x, y) → 지면 높이."""
    y0, y1 = yc - half, yc + half
    mk.lod_box(C, "asphalt", x0, x1, y0, y1, z - 0.9, z, kind=kind)
    mk.lod_box(C, "girder", x0, x1, y0 + 2.4, y1 - 2.4, z - 2.4, z - 0.9, kind=kind)
    for yy in (y0, y1 - 0.45):
        mk.lod_box(C, "barrier", x0, x1, yy, yy + 0.45, z, z + 0.8, kind=kind)
    k = pier0 if pier0 is not None else x0 + pier_pitch / 2
    while k < x1:
        g = ground(k, yc) if ground else 0.0
        C.cyl("girder", (k, yc, g - 1.0), (k, yc, z - 3.2), 1.2, segs=8, kind=kind, cap=False)
        mk.lod_box(C, "girder", k - 0.9, k + 0.9, y0 + 1.2, y1 - 1.2, z - 3.3, z - 2.4, kind=kind)
        k += pier_pitch
    if lamps:
        k = x0 + lamps / 2
        while k < x1:
            yy = y1 - 0.25
            mk.lod_box(C, "dark", k - 0.1, k + 0.1, yy - 0.1, yy + 0.1, z + 0.8, z + 7.6, kind=kind)
            mk.lod_box(C, "dark", k - 0.15, k + 0.15, yy - 2.4, yy + 0.1, z + 7.4, z + 7.65, kind=kind)
            k += lamps


def pier(C, x, yc, *, z=DECK_Z, half=HALF, ground=0.0, kind="main"):
    """망치머리 교각: 둥근 기둥 + 사다리꼴 머리 (상자형 거더 아래)."""
    zc = z - 2.4
    C.cyl("girder", (x, yc, ground - 0.5), (x, yc, zc - 1.0), 1.25, segs=10, kind=kind, cap=False)
    # 기둥 밑동 기초 (지면 위로 조금)
    C.cyl("girder", (x, yc, ground - 0.3), (x, yc, ground + 0.35), 1.7, segs=10, kind="detail", cap=False)
    w0, w1 = half - 1.0, 2.2
    pts = [(x - 1.1, yc - w0), (x + 1.1, yc - w0), (x + 1.1, yc + w0), (x - 1.1, yc + w0)]
    C.prism("girder", pts, zc - 0.45, zc, kind=kind, top=True, bottom=True)
    lo = [(x - 1.1, yc - w1), (x + 1.1, yc - w1), (x + 1.1, yc + w1), (x - 1.1, yc + w1)]
    b = C.bm("girder", kind)
    va = [b.verts.new((px, py, zc - 0.45)) for px, py in pts]
    vb = [b.verts.new((px, py, zc - 1.3)) for px, py in lo]
    fs = [b.faces.new(list(reversed(vb)))]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(b.faces.new((vb[i], vb[j], va[j], va[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)
    # 받침 (베어링 패드)
    for s in (-1, 1):
        C.box("dark", x - 0.5, x + 0.5, yc + s * 1.8 - 0.4, yc + s * 1.8 + 0.4, zc, zc + 0.12, kind="detail")


def light_pole(C, x, y, z, *, arms=(1, -1), h=7.6, reach=2.3, lit=False, kind="detail"):
    """고속도로 가로등: 방호벽 위 기둥 + 팔(arms: +y/-y 쪽) + 갓. lit=False면 꺼진 갓(새벽의 정전 구간)."""
    C.cyl("dark", (x, y, z), (x, y, z + 0.5), 0.2, r2=0.14, segs=8, kind=kind)
    C.cyl("dark", (x, y, z + 0.5), (x, y, z + h), 0.1, r2=0.07, segs=6, kind=kind, cap=False)
    C.cyl("gold", (x, y, z + 0.5), (x, y, z + 0.62), 0.13, segs=8, kind=kind, cap=False)
    for s in arms:
        tip = (x, y + s * reach, z + h + 0.25)
        C.beam("dark", (x, y, z + h - 0.15), tip, 0.08, 0.08, kind=kind)
        C.box("dark", x - 0.22, x + 0.22, tip[1] - 0.45, tip[1] + 0.45, tip[2] - 0.05, tip[2] + 0.12, kind=kind)
        C.box("dawn_lamp" if lit else "lamp_dead", x - 0.18, x + 0.18, tip[1] - 0.38, tip[1] + 0.38, tip[2] - 0.1,
              tip[2] - 0.05, kind="fine" if lit else kind)


def sign_gantry(C, x, yc, z, panels, *, half=HALF, damaged=None, kind="main", facing=-1, col=True):
    """도로 위 표지 문형 (남색 판 + 흰 한글 + 시안 로마자, 미국 단위계 mi). 판은 서쪽(-X, 다가오는 동행 차)을 본다.
    damaged = 떨어져 매달린 판 번호(기울어 걸림)."""
    top = z + 6.2
    for s in (-1, 1):
        yy = yc + s * (half - 0.28)
        C.box("girder", x - 0.5, x + 0.5, yy - 0.3, yy + 0.3, z + BAR_H - 0.05, z + BAR_H + 0.35, kind=kind)
        if col:
            C.col(x - 0.5, x + 0.5, yy - 0.3, yy + 0.3, z + BAR_H - 0.05, z + BAR_H + 0.35)   # 방호벽 위 받침 (안쪽으로 나옴)
        for dx in (-0.22, 0.22):
            C.box("metal", x + dx - 0.07, x + dx + 0.07, yy - 0.07, yy + 0.07, z + BAR_H + 0.35, top + 0.4,
                  kind="detail")
        for k in range(5):
            za = z + BAR_H + 0.6 + k * 1.05
            C.beam("metal", (x - 0.22, yy, za), (x + 0.22, yy, za + 0.9), 0.05, 0.05, kind="detail")
    # 상자 트러스 (위·아래 현재 + 사재)
    y0, y1 = yc - half + 0.28, yc + half - 0.28
    for zz in (top - 0.9, top + 0.3):
        for dx in (-0.22, 0.22):
            C.box("metal", x + dx - 0.06, x + dx + 0.06, y0, y1, zz - 0.06, zz + 0.06, kind="detail")
    n = 12
    for k in range(n):
        ya = y0 + (y1 - y0) * k / n
        yb = y0 + (y1 - y0) * (k + 1) / n
        C.beam("metal", (x - facing * 0.22, ya, top - 0.9), (x - facing * 0.22, yb, top + 0.3), 0.04, 0.04,
               kind="detail")
    # 판
    m = len(panels)
    pw = (y1 - y0 - 0.6) / m
    for i, (ko, en) in enumerate(panels):
        ypc = y0 + 0.3 + pw * (i + 0.5)
        c = Vector((x + facing * 0.4, ypc, top - 1.15))
        N, up = Vector((facing, 0, 0)), Vector((0, 0, 1))
        if damaged == i:
            # 한쪽 볼트가 빠져 기울어 매달린 판
            c = Vector((x + facing * 0.45, ypc + 0.2, top - 1.6))
            up = Vector((0, math.sin(math.radians(24)), math.cos(math.radians(24))))
        C.plate("navy", hw.rrect(pw - 0.4, 2.1, 0.22, 2), tuple(c), tuple(N), 0.1, up=tuple(up), kind="detail")
        C.text("white", ko, 0.56, tuple(c + up * 0.28 - N * 0.11), tuple(N), up=tuple(up))
        C.text("glow", en, 0.3, tuple(c - up * 0.5 - N * 0.11), tuple(N), up=tuple(up))
        C.ring("white", hw.rrect(pw - 0.6, 1.9, 0.16, 2), hw.rrect(pw - 0.72, 1.78, 0.12, 2), tuple(c - N * 0.1),
               tuple(N), up=tuple(up), lift=0.012)
        # 판 뒤 걸이
        for s in (-1, 1):
            xh = x + facing * 0.29
            C.box("metal", xh - 0.04, xh + 0.04, ypc + s * (pw / 2 - 0.6) - 0.04, ypc + s * (pw / 2 - 0.6) + 0.04,
                  top - 1.9 if damaged != i else top - 1.2, top - 0.85, kind="detail")


# ================================================================== 차량 (버려진 민간 차, 툰 껍데기)

_CAR = {
    # 옆모습(u: 앞 +, v: 높이), 폭, 바퀴 위치, 바퀴 반지름
    "sedan": ([(-1.9, 0.28), (1.9, 0.28), (1.95, 0.72), (1.55, 0.86), (0.55, 0.92), (0.1, 1.32), (-1.05, 1.34),
               (-1.7, 0.96), (-1.95, 0.84)], 1.7, (1.25, -1.25), 0.3),
    "hatch": ([(-1.6, 0.28), (1.65, 0.28), (1.7, 0.74), (1.3, 0.88), (0.45, 0.95), (0.0, 1.4), (-1.45, 1.42),
               (-1.62, 0.95)], 1.66, (1.05, -1.05), 0.3),
    "van": ([(-2.2, 0.32), (2.2, 0.32), (2.25, 0.85), (1.95, 1.05), (1.35, 1.85), (-2.15, 1.9), (-2.22, 1.0)],
            1.8, (1.45, -1.45), 0.33),
    "pickup": ([(-2.3, 0.35), (2.2, 0.35), (2.25, 0.9), (1.7, 1.02), (0.85, 1.05), (0.5, 1.6), (-0.6, 1.62),
                (-0.75, 1.08), (-2.3, 1.08)], 1.8, (1.5, -1.5), 0.36),
}


def car(C, x, y, z, yaw, *, kind="sedan", key="car_white", burnt=False, col=True, tilt=0.0, ckind="main",
        roof_rack=False):
    """버려진 차 껍데기 (약 120~200 삼각형). yaw = 차 앞(+u)이 향하는 방위(도, 0 = +X 동쪽)."""
    prof, w, wheels, wr = _CAR[kind]
    a = math.radians(yaw)
    D = Vector((math.cos(a), math.sin(a), 0))
    S = Vector((-D.y, D.x, 0))
    Z = Vector((0, 0, 1))
    if tilt:
        # 한쪽 바퀴가 빠져 옆으로 기울어짐 (S 축 둘레 아님: D 축 둘레)
        rot = Matrix.Rotation(math.radians(tilt), 3, D)
        S, Z = rot @ S, rot @ Z
    O = Vector((x, y, z))

    def P(u, s, v):
        return O + D * u + S * s + Z * v
    body = "soot" if burnt else key
    b = C.bm(body, ckind)
    f0 = [b.verts.new(P(u, -w / 2, v)) for u, v in prof]
    f1 = [b.verts.new(P(u, w / 2, v)) for u, v in prof]
    n = len(prof)
    fs = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
    for i in range(n):
        j = (i + 1) % n
        fs.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)
    # 창 (옆 두 장, 앞·뒤 유리) — 불탄 차는 검은 구멍
    gk = "dark" if burnt else "car_glass"
    roof = [p for p in prof if p[1] > 1.2]
    if roof:
        u0 = min(p[0] for p in roof)
        u1 = max(p[0] for p in roof)
        vtop = max(p[1] for p in roof) - 0.08
        # 창 띠 아래 높이 = 어깨선 (두 번째로 높은 꺾임)
        vbelt = sorted({p[1] for p in prof if p[1] < 1.2})[-1] + 0.04
        for s in (-1, 1):
            pts = [(u0 - 0.35, vbelt), (u1 + 0.25, vbelt), (u1 + 0.0, vtop), (u0 - 0.05, vtop)]
            if kind == "van":
                pts = [(u0 + 0.1, vbelt), (u1 - 0.05, vbelt), (u1 - 0.3, vtop), (u0 + 0.1, vtop)]
            q = [P(u, s * (w / 2 + 0.012), v) for u, v in pts]
            C.poly(gk, [tuple(p) for p in q], normal=tuple(S * s), kind="fine")
        # 앞 유리: 앞쪽 경사면
        fr = [p for p in prof if p[0] > u1 - 0.01 and p[1] > vbelt - 0.1]
        if len(fr) >= 1:
            ua = u1 + 0.02
            q = [P(ua + 0.42, -w / 2 + 0.15, vbelt + 0.02), P(ua + 0.42, w / 2 - 0.15, vbelt + 0.02),
                 P(ua - 0.02, w / 2 - 0.2, vtop - 0.02), P(ua - 0.02, -w / 2 + 0.2, vtop - 0.02)]
            C.poly(gk, [tuple(p + D * 0.03 + Z * 0.02) for p in q], kind="fine")
    # 전조등·후미등
    if not burnt:
        for s in (-1, 1):
            C.poly("lamp_dead", [tuple(P(prof[2][0] + 0.012, s * (w / 2 - 0.5) + dd, vv)) for dd, vv in
                                ((-0.18, 0.6), (0.18, 0.6), (0.18, 0.72), (-0.18, 0.72))], normal=tuple(D),
                   kind="fine")
            ub = min(p[0] for p in prof) - 0.012
            C.poly("red", [tuple(P(ub, s * (w / 2 - 0.35) + dd, vv)) for dd, vv in
                           ((-0.15, 0.62), (0.15, 0.62), (0.15, 0.76), (-0.15, 0.76))], normal=tuple(-D),
                   kind="fine")
    # 바퀴
    for u in wheels:
        for s in (-1, 1):
            c = P(u, s * (w / 2 - 0.13), wr)
            C.cyl("tyre", tuple(c - S * 0.12), tuple(c + S * 0.12), wr, segs=6, kind="detail", smooth=False)
    if roof_rack:
        C.beam("metal", tuple(P(-0.9, -0.5, 1.4)), tuple(P(-0.9, 0.5, 1.4)), 0.05, 0.05, kind="detail")
        C.beam("metal", tuple(P(0.0, -0.5, 1.4)), tuple(P(0.0, 0.5, 1.4)), 0.05, 0.05, kind="detail")
    if col:
        # 옆모습 다각형을 세운 볼록 껍질 (밑은 바퀴까지 바닥): 상자는 본닛·트렁크 위에 0.4 m 넘게 남았다
        side = prof + [(prof[0][0], 0.0), (prof[1][0], 0.0)]
        C.ccol([tuple(P(u, s * w / 2, v)) for (u, v) in side for s in (-1, 1)])


def truck(C, x, y, z, yaw, *, key="car_white", box_key="white", col=True, jack=0.0, ckind="main", text=None):
    """상자 화물차 (운전칸 + 화물 상자). jack: 화물칸이 꺾인 각도(도, 잭나이프)."""
    a = math.radians(yaw)
    D = Vector((math.cos(a), math.sin(a), 0))
    S = Vector((-D.y, D.x, 0))
    O = Vector((x, y, z))
    # 운전칸 (앞 2.2 m)
    cab = [(-1.1, 0.45), (1.1, 0.45), (1.15, 1.1), (0.9, 1.25), (0.55, 2.25), (-1.1, 2.3)]
    b = C.bm(key, ckind)
    w = 2.1
    f0 = [b.verts.new(O + D * (u + 2.9) + S * (-w / 2) + Vector((0, 0, v))) for u, v in cab]
    f1 = [b.verts.new(O + D * (u + 2.9) + S * (w / 2) + Vector((0, 0, v))) for u, v in cab]
    fs = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
    for i in range(len(cab)):
        j = (i + 1) % len(cab)
        fs.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)
    for s in (-1, 1):
        q = [O + D * (2.1 + du) + S * (s * (w / 2 + 0.012)) + Vector((0, 0, v)) for du, v in
             ((0.0, 1.35), (0.85, 1.35), (0.5, 2.1), (0.0, 2.1))]
        C.poly("car_glass", [tuple(p) for p in q], normal=tuple(S * s), kind="fine")
    C.poly("car_glass", [tuple(O + D * 4.06 + S * (-0.85) + Vector((0, 0, 1.35))),
                         tuple(O + D * 4.06 + S * 0.85 + Vector((0, 0, 1.35))),
                         tuple(O + D * 3.62 + S * 0.8 + Vector((0, 0, 2.15))),
                         tuple(O + D * 3.62 + S * (-0.8) + Vector((0, 0, 2.15)))], kind="fine")
    # 화물 상자 (뒤 5.2 m), 꺾임
    ja = a + math.radians(jack)
    D2 = Vector((math.cos(ja), math.sin(ja), 0))
    S2 = Vector((-D2.y, D2.x, 0))
    hinge = O + D * 1.6
    cb_ = hinge - D2 * 2.75
    Mx = Matrix((S2, D2, Vector((0, 0, 1)))).transposed().to_4x4()
    Mx.translation = cb_
    mk._bm_box(C.bm(box_key, ckind), -1.12, 1.12, -2.7, 2.7, z + 0.55 - z, z + 3.0 - z, matrix=Mx)
    if text:
        for s in (-1, 1):
            C.text("teal", text, 0.42, tuple(cb_ + S2 * (s * 1.13) + Vector((0, 0, 1.9))), tuple(S2 * s))
    for u in (3.2, 1.1):
        for s in (-1, 1):
            c = O + D * u + S * (s * (w / 2 - 0.15)) + Vector((0, 0, 0.42))
            C.cyl("tyre", tuple(c - S * 0.14), tuple(c + S * 0.14), 0.42, segs=6, kind="detail", smooth=False)
    for u in (-1.9, -0.9):
        for s in (-1, 1):
            c = cb_ + D2 * u + S2 * (s * 0.95) + Vector((0, 0, 0.42))
            C.cyl("tyre", tuple(c - S2 * 0.14), tuple(c + S2 * 0.14), 0.42, segs=6, kind="detail", smooth=False)
    if col:
        # 운전칸 옆모습 껍질 + 뒷바퀴 축 + 화물 상자 (상자 밑 0.55 m는 상자 안쪽 바퀴뿐: 0.5 m 위부터)
        C.ccol([tuple(O + D * (u + 2.9) + S * (s * w / 2) + Vector((0, 0, v)))
                for (u, v) in cab + [(-1.1, 0.0), (1.1, 0.0)] for s in (-1, 1)])
        _col_oriented_box(C, O + D * 1.1, D, 0.84, w, z, z + 0.84)
        _col_oriented_box(C, cb_, D2, 5.4, 2.24, z + 0.5, z + 3.0)


def bus(C, x, y, z, yaw, *, key="white", stripe="teal", col=True, ckind="main", name="순환 12"):
    """모나티엄 시내버스 (흰 몸체 + 청록 띠 + 남색 창 띠). 길이 9.6 m, 큰 엄폐물."""
    a = math.radians(yaw)
    D = Vector((math.cos(a), math.sin(a), 0))
    S = Vector((-D.y, D.x, 0))
    O = Vector((x, y, z))
    L, w, H = 9.6, 2.35, 2.75
    Mx = Matrix((S, D, Vector((0, 0, 1)))).transposed().to_4x4()
    Mx.translation = O
    prof = hw.stadium(L, H - 0.35, 3, 0, (H - 0.35) / 2 + 0.35)   # 둥근 앞뒤
    b = C.bm(key, ckind)
    f0 = [b.verts.new(Mx @ Vector((-w / 2, u, v))) for u, v in prof]
    f1 = [b.verts.new(Mx @ Vector((w / 2, u, v))) for u, v in prof]
    fs = [b.faces.new(list(reversed(f1))), b.faces.new(f0)]
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        fs.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)
    for s in (-1, 1):
        N = S * s
        c = O + N * (w / 2) + Vector((0, 0, 1.85))
        C.decal("navy", hw.stadium(L - 1.6, 0.9, 3), tuple(c), tuple(N), up=(0, 0, 1), lift=0.015)
        C.strip(stripe, tuple(O + N * (w / 2) + Vector((0, 0, 0.95)) - D * (L / 2 - 0.5)),
                tuple(O + N * (w / 2) + Vector((0, 0, 0.95)) + D * (L / 2 - 0.5)), 0.28, tuple(N), lift=0.015)
        C.text("white", name, 0.22, tuple(O + N * (w / 2) + Vector((0, 0, 1.25)) + D * 1.5), tuple(N), up=(0, 0, 1),
               lift=0.02)
    C.decal("navy", hw.rrect(2.0, 1.2, 0.3, 2), tuple(O + D * (L / 2 + 0.01) + Vector((0, 0, 1.75))), tuple(D),
            lift=0.015)
    for u in (L / 2 - 1.8, -L / 2 + 2.0):
        for s in (-1, 1):
            c = O + D * u + S * (s * (w / 2 - 0.2)) + Vector((0, 0, 0.45))
            C.cyl("tyre", tuple(c - S * 0.16), tuple(c + S * 0.16), 0.45, segs=6, kind="detail", smooth=False)
    if col:
        r_end = (H - 0.35) / 2
        side = list(prof) + [(-L / 2 + r_end, 0.0), (L / 2 - r_end, 0.0)]  # 둥근 앞뒤 + 바퀴 밑
        C.ccol([tuple(Mx @ Vector((s * w / 2, u, v))) for (u, v) in side for s in (-1, 1)])


_OBB = ColAcc()


def _col_oriented_box(C, center, D, L, w, z0, z1):
    """차처럼 비스듬한 상자의 충돌: 축 정렬이면 C.col, 아니면 공용 COL 메시(flush_vehicle_cols로 내보냄)에."""
    D = Vector((D.x, D.y, 0)).normalized()
    if abs(D.x) > 0.999 or abs(D.y) > 0.999:
        hx = L / 2 if abs(D.x) > 0.5 else w / 2
        hy = w / 2 if abs(D.x) > 0.5 else L / 2
        C.col(center.x - hx, center.x + hx, center.y - hy, center.y + hy, z0, z1)
        return
    p0 = center - D * (L / 2)
    p1 = center + D * (L / 2)
    _OBB.obox((p0.x, p0.y), (p1.x, p1.y), w, z0, z1)


def flush_vehicle_cols(C, name="vehicles"):
    """car/truck/bus가 모은 비스듬한 충돌 상자를 COL_<name> 메시 하나로 내보낸다."""
    return _OBB.flush(C, name)


# ================================================================== 무너진 경간

def broken_end(C, x, yc, z, *, half=HALF, direction=1, seed=0, rebar=16, kind="main", depth=3.5, col=False):
    """상판 끝의 들쭉날쭉한 파단면 + 삐져나온 철근. direction=+1이면 동쪽 끝(파단면이 +X를 봄).
    x = 파단면 평균 위치. 상판은 x - direction*depth까지 deck()으로 이미 깔려 있어야 한다."""
    rng = random.Random(seed)
    y0, y1 = yc - half, yc + half
    n = 9
    edge = []
    for i in range(n + 1):
        yy = y0 + (y1 - y0) * i / n
        edge.append((x + direction * rng.uniform(-1.3, 1.1), yy))
    xb = x - direction * depth
    # 판 (윗면은 아스팔트, 옆은 콘크리트) — 바닥면 다각형을 위아래로 세운다
    poly = [(xb, y0)] + edge + [(xb, y1)]
    if direction < 0:
        poly = list(reversed(poly))
    # 볼록하지 않으니 띠 사각형으로 나눠 세운다
    for i in range(n):
        (ea, ya), (eb, yb_) = edge[i], edge[i + 1]
        quad = [(xb, ya), (ea, ya), (eb, yb_), (xb, yb_)]
        if direction < 0:
            quad = [(ea, ya), (xb, ya), (xb, yb_), (eb, yb_)]
        _prism_closed(C.bm("deck_c", kind), quad, z - 0.9, z - 0.05)
        if col:
            C.ccol([(px, py, zz) for px, py in quad for zz in (z - 0.9, z)])        # 바닥 (파단면까지)
        inset = 0.3 if i == 0 else 0.0
        inset2 = 0.3 if i == n - 1 else 0.0
        q2 = [(p[0], p[1] + (inset if abs(p[1] - y0) < 1e-6 else (-inset2 if abs(p[1] - y1) < 1e-6 else 0)))
              for p in quad]
        q3 = [(p[0] - direction * 0.12 if p[0] != xb else p[0], p[1]) for p in q2]
        C.poly("asphalt", [(px, py, z) for px, py in q3], normal=(0, 0, 1), kind="fine")
    # 거더는 더 일찍 끊김
    gx = x - direction * (1.5 + rng.uniform(0, 0.8))
    xa_, xb_ = sorted((xb, gx))
    C.box("girder", xa_, xb_, y0 + 2.4, y1 - 2.4, z - 2.4, z - 0.9, kind=kind)
    # 방호벽 토막
    for (yy, inward) in ((y0, 1), (y1, -1)):
        xe = x - direction * rng.uniform(0.2, 1.4)
        xa2, xb2 = sorted((xb, xe))
        sweep(C, "barrier", [(xa2, yy, z), (xb2, yy, z)], (0, inward), kind=kind)
        if col:
            ya2, yb2 = sorted((yy, yy + inward * BAR_W))
            C.col(xa2, xb2, ya2, yb2, z - 0.25, z + BAR_H)
    if col:
        # 추락 막이: 들쭉날쭉한 파단면을 따라 얇은 벽 (면에서 3~15 cm 안쪽, 끝까지 걸어가 내려다볼 수 있다)
        for (ea, ya), (eb, yb_) in zip(edge, edge[1:]):
            C.ccol([(ex - direction * dd, yy_, zz) for ex, yy_ in ((ea, ya), (eb, yb_)) for dd in (0.03, 0.15)
                    for zz in (z - 0.9, z + 4.0)])
    # 철근
    for k in range(rebar):
        yy = y0 + 0.4 + (y1 - y0 - 0.8) * (k + rng.uniform(0.2, 0.8)) / rebar
        # 파단면 위치 (보간)
        t = (yy - y0) / (y1 - y0) * n
        i = min(n - 1, int(t))
        f = t - i
        ex = edge[i][0] * (1 - f) + edge[i + 1][0] * f
        zz = z - rng.uniform(0.35, 0.8)
        L1 = rng.uniform(0.6, 1.6)
        p0 = Vector((ex - direction * 0.2, yy, zz))
        p1 = p0 + Vector((direction * L1, rng.uniform(-0.15, 0.15), -rng.uniform(0.0, 0.5)))
        p2 = p1 + Vector((direction * rng.uniform(0.2, 0.9), rng.uniform(-0.3, 0.3), -rng.uniform(0.4, 1.6)))
        C.cyl("rebar", tuple(p0), tuple(p1), 0.035, segs=4, kind="fine", smooth=False)
        if rng.random() < 0.7:
            C.cyl("rebar", tuple(p1), tuple(p2), 0.035, segs=4, kind="fine", smooth=False)
    return edge


def fallen_slab(C, top, bottom, yc, *, half=HALF, seed=0, kind="main", barriers=True, roll=0.0):
    """떨어진 경간 조각: top(x, z) 끝이 위에 걸리고 bottom(x, z) 끝이 땅에 박힌 기운 판."""
    rng = random.Random(seed)
    (xa, za), (xb, zb) = top, bottom
    L = math.hypot(xb - xa, zb - za)
    pitch = math.atan2(zb - za, xb - xa)
    c = Vector(((xa + xb) / 2, yc, (za + zb) / 2))
    Mx = (Matrix.Translation(c) @ Matrix.Rotation(-pitch, 4, "Y") @ Matrix.Rotation(math.radians(roll), 4, "X"))
    w = half
    mk._bm_box(C.bm("deck_c", kind), -L / 2, L / 2, -w, w, -0.9, -0.25, matrix=Mx)
    mk._bm_box(C.bm("asphalt", kind), -L / 2 + 0.2, L / 2 - 0.2, -w + 0.3, w - 0.3, -0.25, 0.0, matrix=Mx)
    mk._bm_box(C.bm("girder", kind), -L / 2 + 1.0, L / 2 - 1.5, -w + 2.4, w - 2.4, -2.4, -0.9, matrix=Mx)
    if barriers:
        for s in (-1, 1):
            mk._bm_box(C.bm("barrier", kind), -L / 2 + rng.uniform(0, 2), L / 2 - rng.uniform(0, 3),
                       s * w - (0.45 if s > 0 else 0), s * w + (0.45 if s < 0 else 0), 0.0, 0.8, matrix=Mx)
    # 차선 한 줄
    C.beam("line_y", tuple(Mx @ Vector((-L / 2 + 1, -0.4, 0.015))), tuple(Mx @ Vector((L / 2 - 1, -0.4, 0.015))),
           0.15, 0.01, kind="fine")
    # 철근 (양 끝)
    for end in (-1, 1):
        for k in range(10):
            yy = -w + 0.5 + (2 * w - 1.0) * (k + rng.uniform(0.2, 0.8)) / 10
            p0 = Mx @ Vector((end * L / 2, yy, -rng.uniform(0.3, 0.8)))
            p1 = Mx @ Vector((end * (L / 2 + rng.uniform(0.5, 1.4)), yy + rng.uniform(-0.2, 0.2),
                               -rng.uniform(0.2, 1.2)))
            C.cyl("rebar", tuple(p0), tuple(p1), 0.035, segs=4, kind="fine", smooth=False)
    return Mx


def rubble(C, cx, cy, z, r, n, *, seed=0, kind="main", key="rubble"):
    """콘크리트 잔해 더미: 납작한 덩어리 + 각진 조각."""
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = r * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        s = rng.uniform(0.4, 1.4) * (1.2 - d / r * 0.6)
        if rng.random() < 0.55:
            C.blob(key, (x, y, z + s * 0.25), s, (1.0, rng.uniform(0.6, 1.0), rng.uniform(0.35, 0.6)), segs=6, rings=4,
                   rot_z=rng.uniform(0, 3), kind=kind)
        else:
            C.rbox(key, (x, y, z + s * 0.2), (s * 1.6, s * 1.1, s * 0.5),
                   (rng.uniform(-25, 25), rng.uniform(-25, 25), rng.uniform(0, 180)), kind=kind)


# ================================================================== 강재 계단·난간 (관측탑)

def rail_run(C, p0, p1, *, h=0.85, posts=2.0, key="rail", toe=True, kind="detail", col=None, low_wall=False):
    """강재 난간 (엘프 높이 0.85 m: 눈높이 0.9 m 아래라 서서 너머로 보고 쏠 수 있다): 기둥 + 손잡이 + 중간대 + 발끝막이.
    p0, p1 = 바닥 높이 3D 점(경사 가능). col: ColAcc면 손잡이·중간대 높이에 얇은 충돌 막대를 더한다."""
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = Vector((d.x, d.y, 0)).length
    n = max(1, int(math.ceil(L / posts)))
    for k in range(n + 1):
        p = P0.lerp(P1, k / n)
        mk._bm_prism(C.bm(key, kind), [(p.x - 0.035, p.y - 0.035), (p.x + 0.035, p.y - 0.035),
                                         (p.x + 0.035, p.y + 0.035), (p.x - 0.035, p.y + 0.035)], p.z, p.z + h,
                     top=True, bottom=False)
    C.beam(key, tuple(P0 + Vector((0, 0, h))), tuple(P1 + Vector((0, 0, h))), 0.06, 0.06, kind=kind)
    C.beam(key, tuple(P0 + Vector((0, 0, h * 0.5))), tuple(P1 + Vector((0, 0, h * 0.5))), 0.035, 0.035, kind=kind)
    if toe:
        C.beam("hazard", tuple(P0 + Vector((0, 0, 0.06))), tuple(P1 + Vector((0, 0, 0.06))), 0.02, 0.12, kind=kind)
    if col is not None:
        # 충돌은 손잡이(0.94~1.0)와 중간대(0.42~0.5) 높이의 얇은 막대 두 개: 걷거나 웅크려(0.82 m) 빠져나갈 틈이 없고,
        # 막대 사이로는 총을 쏠 수 있다 (투명 벽은 관측탑에서 아래로 쏘는 사선을 막는다)
        dd = Vector((d.x, d.y, 0)).normalized()
        nrm = Vector((-dd.y, dd.x, 0)) * 0.05
        for (za, zb) in ((h * 0.42, h * 0.5), (h * 0.94, h + 0.04)):
            q = [P0 - nrm, P1 - nrm, P1 + nrm, P0 + nrm]
            b = col.bm
            vt = [b.verts.new(p + Vector((0, 0, zb))) for p in q]
            vb = [b.verts.new(p + Vector((0, 0, za))) for p in q]
            fs = [b.faces.new(vt), b.faces.new(list(reversed(vb)))]
            for i in range(4):
                j = (i + 1) % 4
                fs.append(b.faces.new((vb[i], vb[j], vt[j], vt[i])))
            bmesh.ops.recalc_face_normals(b, faces=fs)
        if low_wall:
            # 발끝막이 높이 낮은 벽 (중간대 아래 틈 0.42 m도 웅크림 0.82 m보다 낮지만, 굴러 떨어지는 NPC를 막는다)
            q = [P0 - nrm, P1 - nrm, P1 + nrm, P0 + nrm]
            b = col.bm
            vt = [b.verts.new(p + Vector((0, 0, 0.15))) for p in q]
            vb = [b.verts.new(p + Vector((0, 0, -0.05))) for p in q]
            fs = [b.faces.new(vt), b.faces.new(list(reversed(vb)))]
            for i in range(4):
                j = (i + 1) % 4
                fs.append(b.faces.new((vb[i], vb[j], vt[j], vt[i])))
            bmesh.ops.recalc_face_normals(b, faces=fs)


# 안전 철망 (M8 관측탑·계단·기단 층): 난간(0.85 m)·흉벽 위로 기둥을 올려 윗대와 반투명 철망을 단다. 레일 슈터처럼 정해진 길을
# 벗어나지 않게: 계단을 달려 내려가며 비스듬히 뛰어도 발이 계단 선 위 1.83 m까지밖에 못 오르고(점프 4.0 m/s, 중력 13.5,
# 질주 5.4 m/s, 30° 계단), 상자 더미(0.96 m) 위에서 뛰어도 1.55 m라 2.0 m 철망을 넘지 못한다. 넘기·오르기 상한(1.5 m)도 넘는다.
# 충돌은 철망과 같은 면의 얇은 벽(바닥 ~ 철망 윗대): 보이는 철망 그대로. 탄·시야는 반투명 철망을 지나간다(탄 형상 규칙)
GUARD_H = 2.0


def guard_run(C, col, p0, p1, *, h=GUARD_H, base=0.85, col_from=0.0, mesh_from=None, posts=2.0, key="rail",
              mesh="fence_a", kind="detail"):
    """p0→p1(바닥 높이 3D 점, 경사 가능)을 따라 선 안전 철망: 기둥(base ~ h, 난간 기둥과 같은 자리), 윗대(h),
    반투명 철망(mesh_from(기본: 난간이면 발끝막이 위 0.12) ~ h, 난간 선 위). col: ColAcc면 col_from ~ h 얇은 벽."""
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = Vector((d.x, d.y, 0)).length
    if L < 1e-3:
        return
    n = max(1, int(math.ceil(L / posts)))
    for k in range(n + 1):
        p = P0.lerp(P1, k / n)
        mk._bm_prism(C.bm(key, kind), [(p.x - 0.03, p.y - 0.03), (p.x + 0.03, p.y - 0.03), (p.x + 0.03, p.y + 0.03),
                                         (p.x - 0.03, p.y + 0.03)], p.z + base, p.z + h, top=True, bottom=False)
    C.beam(key, tuple(P0 + Vector((0, 0, h))), tuple(P1 + Vector((0, 0, h))), 0.05, 0.05, kind=kind)
    dd = Vector((d.x, d.y, 0)).normalized()
    nrm = Vector((-dd.y, dd.x, 0))
    lo = min(base, 0.12) if mesh_from is None else mesh_from
    C.poly(mesh, [tuple(P0 + Vector((0, 0, lo))), tuple(P1 + Vector((0, 0, lo))), tuple(P1 + Vector((0, 0, h - 0.02))),
                  tuple(P0 + Vector((0, 0, h - 0.02)))], normal=tuple(nrm), kind="fine")
    if col is not None:
        col.wall(P0, P1, col_from, h, t=0.08)


def stair_flight(C, col, x0, x1, ya, yb, za, zb, *, steps=None, key="grate", stringer="tower_band", rails=(True, True),
                 kind="detail", rail_col=True):
    """y 방향 강재 계단 (ya에서 za, yb에서 zb). 디딤판 상자 + 옆판 + 난간. 충돌은 매끈한 경사판(col)."""
    rise = zb - za
    if steps is None:
        steps = max(1, int(round(abs(rise) / 0.175)))
    sgn = 1 if yb > ya else -1
    run = abs(yb - ya)
    dz = rise / steps
    dy = run / steps
    for i in range(steps):
        y_a = ya + sgn * dy * i
        y_b = ya + sgn * dy * (i + 1)
        zt = za + dz * (i + 1)
        y_lo, y_hi = sorted((y_a, y_b))
        C.box(key, x0 + 0.025, x1 - 0.025, y_lo, y_hi, zt - 0.05, zt, kind=kind)
        yn = y_hi - 0.04 if sgn > 0 else y_lo + 0.04
        C.strip("hazard", (x0 + 0.08, yn, zt), (x1 - 0.08, yn, zt), 0.06, lift=0.006)
    # 옆판 (경사 보, 폭 4.5 cm): 바깥 면은 계단 가장자리 -2 cm, 안쪽 면은 +2.5 cm(디딤판이 맞닿음).
    # 층참 옆면(0)·가장자리 난간의 발끝막이(±1 cm)·기둥(±3.5 cm)·안쪽 난간(+1.5, +4 cm) 면과 모두 1 cm 넘게 어긋난다
    # (모두 같은 detail 등급이라 표준 깊이 버퍼에서 몇 mm 차는 먼 거리에서 깜빡인다)
    for xs in (x0 + 0.0025, x1 - 0.0025):
        C.beam(stringer, (xs, ya, za - 0.12), (xs, yb, zb - 0.12), 0.045, 0.3, kind=kind)
    # 난간
    for xs, on in ((x0, rails[0]), (x1, rails[1])):
        if on:
            rail_run(C, (xs, ya, za), (xs, yb, zb), h=0.85, posts=2.0, toe=False, kind=kind,
                     col=col if rail_col else None)
    # 충돌: 디딤판 앞 모서리(코)를 잇는 경사판 (자동 오르기·AI 이동이 매끄럽다). 첫 코에서 한 단 앞 바닥까지 늘이고,
    # 마지막 디딤판 위는 평판. 예전 판은 단의 안쪽 모서리를 이어 발이 디딤판 코보다 최대 한 단(0.18 m) 아래에 묻혔다.
    # 두께 0.15: 계단 밑에서 뛰면 디딤판보다 0.2 m 넘게 낮은 곳에 머리가 걸렸다
    y_f, y_t = ya - sgn * dy, yb - sgn * dy
    for (p, q, zp, zq) in ((y_f, y_t, za, zb), (y_t, yb, zb, zb)):
        col.slab([(x0, p, zp), (x0, q, zq), (x1, q, zq), (x1, p, zp)] if sgn > 0 else
                 [(x0, q, zq), (x0, p, zp), (x1, p, zp), (x1, q, zq)], t=0.15)
    # 옆판 (경사판보다 0.3 m 아래까지 내려온다): 계단 밑 마당에서 머리가 옆판을 지나가지 않게. 양 끝 0.5 m는 빼서
    # 바닥·층참에 낮은 턱을 만들지 않는다
    hv = 0.15 / math.cos(math.atan2(abs(rise), run))
    for xs in (x0 + 0.0025, x1 - 0.0025):
        ys = [ya + sgn * 0.5, yb - sgn * 0.5]
        zs = [za + rise * 0.5 / run - 0.12 + hv, zb - rise * 0.5 / run - 0.12 + hv]
        if sgn < 0:
            ys, zs = ys[::-1], zs[::-1]
        col.slab([(xs - 0.0225, ys[0], zs[0]), (xs - 0.0225, ys[1], zs[1]), (xs + 0.0225, ys[1], zs[1]),
                  (xs + 0.0225, ys[0], zs[0])], t=2 * hv)


def landing(C, x0, x1, y0, y1, z, *, key="grate", posts_to=None, kind="detail", col=True):
    """강재 층참: 격자판 + 테두리 보. posts_to = 기둥을 내릴 바닥 높이."""
    C.box(key, x0, x1, y0, y1, z - 0.08, z, kind=kind)
    C.box("tower_band", x0, x1, y0, y1, z - 0.3, z - 0.08, kind=kind)
    if posts_to is not None:
        # 기둥은 모서리에서 12 cm 안: 가장자리 난간(가장자리 + 5 cm 줄)의 가로대·발끝막이 면과 1 cm 넘게 어긋나게
        for x in (x0 + 0.12, x1 - 0.12):
            for y in (y0 + 0.12, y1 - 0.12):
                C.box("metal", x - 0.07, x + 0.07, y - 0.07, y + 0.07, posts_to, z - 0.3, kind=kind)
                if col:
                    C.col(x - 0.07, x + 0.07, y - 0.07, y + 0.07, posts_to, z - 0.3)
    if col:
        C.col(x0, x1, y0, y1, z - 0.3, z)


# ================================================================== 관측 장비 (삼각대 레이저 거리측정·지시기)

def tripod_gear(C, name, loc, yaw):
    """삼각대 위 레이저 거리측정·표적지시기(오리지널, 진압반 특수작전부 장비). 노드 트리:
        <name> (빈, 위치 = 삼각대 발 중심, -Y = 지시기 정면, hidden=1)
          <name>_*            삼각대 다리·배터리 상자·케이블 (메시)
          <name>_head (빈)    패닝 헤드 회전축 (미션이 표적 쪽으로 돌릴 수 있다. -Y = 대물렌즈 방향)
            <name>_head_*     지시기 몸체·대물렌즈·접안부·표시창
    엘프 눈높이 0.9 m에 접안부가 오게 헤드 높이 0.84 m."""
    HZ = 0.84

    def legs(b):
        for k in range(3):
            a = math.radians(90 + k * 120)
            foot = Vector((math.cos(a) * 0.46, math.sin(a) * 0.46, 0.0))
            top = Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, HZ - 0.1))
            mk._bm_cyl(b, foot + Vector((0, 0, 0.02)), top, 0.016, segs=5, smooth=False)
            mid = foot.lerp(top, 0.42)
            mk._bm_cyl(b, mid, Vector((0, 0, HZ * 0.42)), 0.008, segs=4, smooth=False)
        mk._bm_cyl(b, Vector((0, 0, HZ - 0.14)), Vector((0, 0, HZ - 0.02)), 0.045, segs=8)

    def feet(b):
        for k in range(3):
            a = math.radians(90 + k * 120)
            mk._bm_blob(b, (math.cos(a) * 0.46, math.sin(a) * 0.46, 0.015), 0.025, (1, 1, 0.6), segs=6, rings=3)
        mk._bm_cyl(b, Vector((0, 0, HZ * 0.42 - 0.02)), Vector((0, 0, HZ * 0.42 + 0.02)), 0.03, segs=6)

    def case(b):
        # 바닥의 배터리·무선 상자 (남보라 + 청록 띠)
        mk._bm_box(b, 0.35, 0.68, 0.18, 0.42, 0.0, 0.2)

    def case_band(b):
        mk._bm_box(b, 0.345, 0.685, 0.175, 0.425, 0.13, 0.16)      # 상자 면보다 5 mm 밖

    def cable(b):
        pts = [Vector((0.36, 0.3, 0.12)), Vector((0.22, 0.22, 0.02)), Vector((0.1, 0.08, 0.02)),
               Vector((0.03, 0.02, 0.35)), Vector((0.03, 0.03, HZ - 0.1))]
        for p, q in zip(pts, pts[1:]):
            mk._bm_cyl(b, p, q, 0.007, segs=4, smooth=False)

    root = mesh_node(name, {"metal": legs, "dark": feet, "violet": case, "teal": case_band, "rubber": cable},
                     loc=loc, yaw=yaw, props={"hidden": 1, "gear": "laser_designator"})

    def body(b):
        mk._bm_box(b, -0.075, 0.075, -0.2, 0.18, HZ + 0.0, HZ + 0.13)
        mk._bm_box(b, -0.03, 0.03, -0.06, 0.06, HZ - 0.02, HZ + 0.01)     # 퀵릴리즈 판
        mk._bm_box(b, -0.02, 0.02, -0.12, 0.08, HZ + 0.13, HZ + 0.19)     # 손잡이 기둥
        mk._bm_box(b, -0.022, 0.022, -0.14, 0.1, HZ + 0.17, HZ + 0.2)

    def optics(b):
        mk._bm_cyl(b, Vector((-0.032, -0.2, HZ + 0.07)), Vector((-0.032, -0.27, HZ + 0.07)), 0.052, segs=12)
        mk._bm_cyl(b, Vector((0.045, -0.2, HZ + 0.09)), Vector((0.045, -0.25, HZ + 0.09)), 0.024, segs=10)
        mk._bm_cyl(b, Vector((0.0, 0.18, HZ + 0.075)), Vector((0.0, 0.26, HZ + 0.075)), 0.032, r2=0.04, segs=10)

    def lens(b):
        mk._bm_cyl(b, Vector((-0.032, -0.27, HZ + 0.07)), Vector((-0.032, -0.276, HZ + 0.07)), 0.044, segs=12)
        mk._bm_cyl(b, Vector((0.045, -0.25, HZ + 0.09)), Vector((0.045, -0.256, HZ + 0.09)), 0.017, segs=10)

    def accent(b):
        # 금색 고리 대신 띠 (교주 차원 문법): 몸체·대물경 면보다 5~6 mm 밖
        mk._bm_box(b, -0.08, 0.08, -0.205, -0.185, HZ - 0.005, HZ + 0.135)
        mk._bm_cyl(b, Vector((-0.032, -0.255, HZ + 0.07)), Vector((-0.032, -0.262, HZ + 0.07)), 0.058, segs=12)

    def screen(b):
        mk._bm_box(b, 0.076, 0.085, -0.05, 0.08, HZ + 0.04, HZ + 0.1)     # 몸체 옆면보다 1 cm 밖

    head = mesh_node(f"{name}_head", {"navy": body, "dark": optics, "glass_d": lens, "gold": accent, "glow": screen},
                     loc=(0, 0, 0), yaw=0.0, props={"pivot": "pan"})
    head.parent = root
    C.add_node(root)
    return root


# ================================================================== 바람자루 (교량 강풍 표지)

def windsock(C, x, y, z, *, h=4.5, toward=(1.0, 0.4), kind="detail", sign=True):
    """다리 위 강풍 바람자루: 기둥 + 고리 + 주황·흰 띠 원뿔(바람 부는 쪽으로 늘어짐). 반환: 자루 가운데 점."""
    C.cyl("metal", (x, y, z), (x, y, z + h), 0.07, segs=6, kind=kind)
    top = Vector((x, y, z + h - 0.1))
    d = Vector((toward[0], toward[1], 0)).normalized()
    d = (d + Vector((0, 0, -0.35))).normalized()       # 약한 바람: 조금 처짐
    C.cyl("metal", tuple(top - Vector((0, 0, 0.05))), tuple(top + d * 0.45), 0.03, segs=4, kind=kind)
    L = 2.4
    seg = 5
    r0, r1 = 0.36, 0.15
    base = top + d * 0.45
    for i in range(seg):
        a = base + d * (L * i / seg)
        b_ = base + d * (L * (i + 1) / seg)
        ra = r0 + (r1 - r0) * i / seg
        rb = r0 + (r1 - r0) * (i + 1) / seg
        C.cyl("sock_o" if i % 2 == 0 else "white", tuple(a), tuple(b_), ra, r2=rb, segs=10, kind=kind, cap=False)
    C.cyl("dark", tuple(base - d * 0.02), tuple(base + d * 0.04), r0 + 0.03, segs=10, kind=kind, cap=False)
    C.blob("beacon_r", (x, y, z + h + 0.08), 0.09, segs=6, rings=4, kind="fine")
    if sign:
        c = Vector((x - 0.12, y, z + 1.9))
        C.plate("hazard", hw.rrect(1.3, 0.9, 0.12, 2), tuple(c), (-1, 0, 0), 0.04, kind="detail")
        C.text("dark", "강풍 주의", 0.22, tuple(c + Vector((-0.05, 0, 0.13))), (-1, 0, 0))
        C.text("dark", "HIGH WIND", 0.15, tuple(c + Vector((-0.05, 0, -0.17))), (-1, 0, 0))
    return base + d * (L * 0.5)


# ================================================================== 원경: 높이장 바닥

def grid_lines(a0, a1, c, step0=40.0, k=0.07, step_max=400.0):
    """c에서 멀어질수록 넓어지는 격자선 (a0..a1)."""
    out = [c]
    x = c
    while x < a1:
        x += min(step_max, step0 + k * abs(x - c))
        out.append(min(x, a1))
    x = c
    while x > a0:
        x -= min(step_max, step0 + k * abs(x - c))
        out.insert(0, max(x, a0))
    return out


def heightfield(C, xs, ys, h, mat_fn, *, strips=None, kind="far", smooth_above=40.0):
    """칸마다 머티리얼이 다른 높이장. 칸은 서로 겹치지 않는다(먼 거리 깊이 깜빡임 없음).
    같은 머티리얼 칸끼리는 정점을 나눠 smooth_above보다 높은 산 칸은 부드럽게 음영된다(툰 띠가 둥근 산처럼 갈린다).
    mat_fn(cx, cy, hc, slope) → 머티리얼 키. strips(cx, cy) → None 또는 (axis, [키...]): 칸을 띠 밭으로 나눈다."""
    H = [[h(x, y) for x in xs] for y in ys]
    shared = {}

    def V(key, i, j):
        k = (key, i, j)
        v = shared.get(k)
        if v is None:
            v = shared[k] = C.bm(key, kind).verts.new((xs[i], ys[j], H[j][i]))
        return v
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            z00, z10, z01, z11 = H[j][i], H[j][i + 1], H[j + 1][i], H[j + 1][i + 1]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            hc = (z00 + z10 + z01 + z11) / 4
            slope = max(abs(z10 - z00), abs(z11 - z01)) / (x1 - x0) + max(abs(z01 - z00), abs(z11 - z10)) / (y1 - y0)

            def bil(u, v):
                return (z00 * (1 - u) * (1 - v) + z10 * u * (1 - v) + z01 * (1 - u) * v + z11 * u * v)
            st = strips(cx, cy) if strips else None
            if st:
                axis, keys = st
                m = len(keys)
                for k, key in enumerate(keys):
                    t0, t1 = k / m, (k + 1) / m
                    if axis == "x":
                        uv = [(t0, 0), (t1, 0), (t1, 1), (t0, 1)]
                    else:
                        uv = [(0, t0), (1, t0), (1, t1), (0, t1)]
                    pts = [(x0 + (x1 - x0) * u, y0 + (y1 - y0) * v, bil(u, v)) for u, v in uv]
                    b = C.bm(key, kind)
                    b.faces.new([b.verts.new(p) for p in pts])
                continue
            key = mat_fn(cx, cy, hc, slope)
            b = C.bm(key, kind)
            f = b.faces.new((V(key, i, j), V(key, i + 1, j), V(key, i + 1, j + 1), V(key, i, j + 1)))
            f.smooth = hc > smooth_above
    return H


def raised_path(C, pts, w, h, *, key="road_far", lift=0.6, kind="far", step=60.0):
    """지면 위로 lift만큼 띄운 길 띠 (윗면 + 양옆). pts = [(x, y)], h(x, y) = 지면 높이."""
    P = []
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(math.ceil(L / step)))
        for k in range(n):
            t = k / n
            P.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    P.append(pts[-1])
    bm_ = C.bm(key, kind)
    prev = None
    for k, (x, y) in enumerate(P):
        a = P[min(k + 1, len(P) - 1)]
        c = P[max(k - 1, 0)]
        d = Vector((a[0] - c[0], a[1] - c[1], 0)).normalized()
        n_ = Vector((-d.y, d.x, 0)) * (w / 2)
        z = h(x, y)
        row = [bm_.verts.new((x - n_.x, y - n_.y, z + lift)), bm_.verts.new((x + n_.x, y + n_.y, z + lift)),
               bm_.verts.new((x + n_.x * 1.6, y + n_.y * 1.6, z - 0.5)),
               bm_.verts.new((x - n_.x * 1.6, y - n_.y * 1.6, z - 0.5))]
        if prev:
            for (u, v) in ((0, 1), (1, 2), (3, 0)):
                f = bm_.faces.new((prev[u], prev[v], row[v], row[u]))
                f.normal_update()
                if f.normal.z < 0:
                    f.normal_flip()
        prev = row


def hedge(C, p0, p1, h, *, height=1.8, width=1.4, key="hedge", kind="far", lift=-0.3):
    """생울타리 (지면 위 입체 띠, 바닥면 없음)."""
    a, b = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = (b - a)
    L = d.length
    if L < 1:
        return
    d.normalize()
    nrm = Vector((-d.y, d.x, 0)) * (width / 2)
    n = max(1, int(L / 80))
    bm_ = C.bm(key, kind)
    for k in range(n):
        pa = a.lerp(b, k / n)
        pb = a.lerp(b, (k + 1) / n)
        za, zb = h(pa.x, pa.y) + lift, h(pb.x, pb.y) + lift
        q = [pa - nrm, pb - nrm, pb + nrm, pa + nrm]
        zs = [za, zb, zb, za]
        lo = [bm_.verts.new((p.x, p.y, z)) for p, z in zip(q, zs)]
        hi = [bm_.verts.new((p.x, p.y, z + height)) for p, z in zip(q, zs)]
        bm_.faces.new(hi)
        for i in range(4):
            j = (i + 1) % 4
            bm_.faces.new((lo[i], lo[j], hi[j], hi[i]))


def farmstead(C, x, y, z, *, yaw_axis="x", seed=0, kind="far"):
    """원경 농가: 박공집 + 헛간 + 나무 둘."""
    rng = random.Random(seed)
    roofs = ["fairy_roof_r", "roof", "fairy_roof", "brick"]
    w, d = rng.uniform(7, 10), rng.uniform(5, 7)
    mk.lod_gable(C, "warm", rng.choice(roofs), x - w / 2, x + w / 2, y - d / 2, y + d / 2, z - 0.5, z + 3.2, z + 5.6,
                 axis=yaw_axis, kind=kind)
    bx, by = x + rng.choice((-1, 1)) * (w / 2 + 6), y + rng.uniform(-3, 3)
    mk.lod_gable(C, "wood_d", "roof", bx - 5, bx + 5, by - 3.5, by + 3.5, z - 0.5, z + 3.6, z + 6.4,
                 axis="y" if yaw_axis == "x" else "x", kind=kind)
    for k in range(2):
        mk.lod_tree(C, x + rng.uniform(-14, 14), y + rng.uniform(6, 14) * rng.choice((-1, 1)), h=rng.uniform(8, 12),
                    r=rng.uniform(3, 4.5), z=z - 0.5, key=rng.choice(("leaf", "leaf_d")), kind=kind)


# ================================================================== 원경: 에르피엔 (요정 왕국)

def fairy_tower(C, x, y, z, *, r=6.0, h=22.0, roof="fairy_roof", roof_h=None, kind="far", lit=None, segs=8):
    """둥근 석탑 + 원뿔 지붕 + 금 첨탑 (요정 성 문법: 크림 석재, 초록 지붕, 금 장식)."""
    rh = roof_h if roof_h is not None else r * 1.9
    C.cyl("fairy_stone", (x, y, z - 2), (x, y, z + h), r, segs=segs, kind=kind, cap=False)
    C.cyl("fairy_stone_d", (x, y, z + h), (x, y, z + h + r * 0.25), r * 1.12, segs=segs, kind=kind)
    C.cyl(roof, (x, y, z + h + r * 0.25), (x, y, z + h + r * 0.25 + rh), r * 1.2, r2=0.0, segs=segs, kind=kind)
    tip = z + h + r * 0.25 + rh
    C.cyl("fairy_gold", (x, y, tip - r * 0.2), (x, y, tip + r * 0.8), r * 0.09, r2=0.0, segs=4, kind=kind,
          smooth=False)
    if lit:
        C.rect("win_lit", (x - r * 1.0, y, z + h * 0.62), (-1, 0, 0), lit * 2, lit * 2.4, lift=0.3)
        C.rect("win_lit", (x, y - r * 1.0, z + h * 0.5), (0, -1, 0), lit * 1.6, lit * 2.0, lift=0.3)
    return tip + r * 0.8


def erpien(C, cx, cy, h, *, r_wall=480.0, seed=11, kind="far"):
    """에르피엔 원경 실루엣 (오리지널 디자인: 원작 도시 배치는 알려지지 않았다).
    언덕 위 성곽 도시: 바깥 성벽(20각) + 둥근 탑, 박공집 마을, 안쪽 성벽, 중앙 왕궁(큰 원탑 + 원뿔 첨탑 + 금 고리).
    반환: dict(center, palace_top, gate_west)."""
    rng = random.Random(seed)
    zc = h(cx, cy)
    # 바깥 성벽
    n = 20
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + 0.08
        rr = r_wall * (1 + 0.06 * math.sin(i * 1.7))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
        za, zb = h(xa, ya), h(xb, yb)
        d = Vector((xb - xa, yb - ya, 0))
        nrm = Vector((-d.y, d.x, 0)).normalized() * 2.5
        q = [(xa - nrm.x, ya - nrm.y), (xb - nrm.x, yb - nrm.y), (xb + nrm.x, yb + nrm.y), (xa + nrm.x, ya + nrm.y)]
        b = C.bm("fairy_stone", kind)
        lo = [b.verts.new((p[0], p[1], z - 3)) for p, z in zip(q, (za, zb, zb, za))]
        hi = [b.verts.new((p[0], p[1], z + 13)) for p, z in zip(q, (za, zb, zb, za))]
        b.faces.new(hi)
        for k in range(4):
            k2 = (k + 1) % 4
            b.faces.new((lo[k], lo[k2], hi[k2], hi[k]))
        # 성가퀴 띠 (윗면 바로 아래 짙은 띠: 위에서 보면 두께가 읽힘)
        b2 = C.bm("fairy_stone_d", kind)
        outer = [Vector((xa, ya, 0)) - nrm * 1.05, Vector((xb, yb, 0)) - nrm * 1.05]
        v = [b2.verts.new((outer[0].x, outer[0].y, za + 10.5)), b2.verts.new((outer[1].x, outer[1].y, zb + 10.5)),
             b2.verts.new((outer[1].x, outer[1].y, zb + 13.6)), b2.verts.new((outer[0].x, outer[0].y, za + 13.6))]
        b2.faces.new(v)
    for i, (x, y) in enumerate(pts):
        fairy_tower(C, x, y, h(x, y), r=7.5, h=24 + (6 if i % 5 == 0 else 0),
                    roof="fairy_roof" if i % 3 else "fairy_roof_b", kind=kind, segs=8,
                    lit=1.6 if i % 4 == 1 else None)
    # 서문 (고속도로가 닿는 곳): 쌍탑 문루
    ga = math.pi + 0.08
    gx, gy = cx + math.cos(ga) * r_wall, cy + math.sin(ga) * r_wall
    for s in (-1, 1):
        fairy_tower(C, gx, gy + s * 18, h(gx, gy), r=9, h=34, roof="fairy_roof", kind=kind, lit=2.0)
    mk.lod_box(C, "fairy_stone", gx - 6, gx + 6, gy - 12, gy + 12, h(gx, gy) - 2, h(gx, gy) + 22, kind=kind)
    C.box("fairy_gold", gx - 6.3, gx - 6.0, gy - 7, gy + 7, h(gx, gy) + 15, h(gx, gy) + 18, kind=kind)
    # 마을 (박공집, 알록달록한 지붕)
    roofs = ["fairy_roof_r", "fairy_roof", "fairy_roof_b", "fairy_roof_l", "fairy_roof_r", "roof"]
    walls = ["fairy_stone", "warm", "fairy_stone", "white"]
    placed = 0
    tries = 0
    while placed < 150 and tries < 2000:
        tries += 1
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(190, r_wall - 30)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        if abs(y - gy) < 22 and x < cx - r_wall + 120:
            continue
        w_, d_ = rng.uniform(9, 18), rng.uniform(7, 11)
        z = h(x, y)
        hh = rng.uniform(5, 11)
        ax = "x" if abs(math.cos(a)) < 0.7 else "y"
        mk.lod_gable(C, rng.choice(walls), rng.choice(roofs), x - w_ / 2, x + w_ / 2, y - d_ / 2, y + d_ / 2,
                     z - 1.5, z + hh, z + hh + rng.uniform(4, 7), axis=ax, kind=kind)
        if rng.random() < 0.3:
            C.rect("win_lit", (x - w_ / 2, y, z + hh * 0.5), (-1, 0, 0), 2.6, 2.6, lift=0.2)
        placed += 1
    for k in range(60):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(150, r_wall - 25)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        mk.lod_tree(C, x, y, h=rng.uniform(12, 18), r=rng.uniform(5, 8), z=h(x, y) - 1,
                    key=rng.choice(("leaf", "leaf_d", "canopy")), kind=kind)
    # 안쪽 성벽 + 탑
    ri = 160.0
    m = 12
    ipts = [(cx + math.cos(2 * math.pi * i / m) * ri, cy + math.sin(2 * math.pi * i / m) * ri) for i in range(m)]
    for i in range(m):
        (xa, ya), (xb, yb) = ipts[i], ipts[(i + 1) % m]
        d = Vector((xb - xa, yb - ya, 0))
        nrm = Vector((-d.y, d.x, 0)).normalized() * 3
        q = [(xa - nrm.x, ya - nrm.y), (xb - nrm.x, yb - nrm.y), (xb + nrm.x, yb + nrm.y), (xa + nrm.x, ya + nrm.y)]
        z0 = min(h(xa, ya), h(xb, yb)) - 3
        mk.lod_poly_prism(C, "fairy_stone", q, z0, z0 + 22, kind=kind)
    for i, (x, y) in enumerate(ipts):
        fairy_tower(C, x, y, h(x, y), r=9, h=34, roof="fairy_roof_l" if i % 2 else "fairy_roof", kind=kind,
                    lit=2.2 if i % 3 == 0 else None)
    # 왕궁: 단 2층 + 날개 + 큰 원탑 + 네 모서리 탑 + 금 고리
    mk.lod_box(C, "fairy_stone_d", cx - 95, cx + 95, cy - 70, cy + 70, zc - 2, zc + 14, kind=kind)
    mk.lod_box(C, "fairy_stone", cx - 70, cx + 70, cy - 50, cy + 50, zc + 14, zc + 34, kind=kind)
    mk.lod_gable(C, "fairy_stone", "fairy_roof", cx - 66, cx + 66, cy - 22, cy + 22, zc + 34, zc + 52, zc + 72,
                 axis="y", kind=kind)
    for sx in (-1, 1):
        for sy in (-1, 1):
            fairy_tower(C, cx + sx * 62, cy + sy * 44, zc + 14, r=12, h=72, roof="fairy_roof_b", roof_h=46,
                        kind=kind, segs=10, lit=2.6)
    keep_top = zc + 135
    R_keep = 30.0
    C.cyl("fairy_stone", (cx, cy, zc + 30), (cx, cy, keep_top), R_keep, segs=14, kind=kind, cap=False)
    C.cyl("fairy_stone_d", (cx, cy, keep_top), (cx, cy, keep_top + 7), R_keep + 3.5, segs=14, kind=kind)
    C.cyl("fairy_roof", (cx, cy, keep_top + 7), (cx, cy, keep_top + 107), R_keep + 6, r2=0.0, segs=14, kind=kind)
    spire = keep_top + 107
    C.cyl("fairy_gold", (cx, cy, spire - 12), (cx, cy, spire + 40), 3.0, r2=0.0, segs=6, kind=kind, smooth=False)
    b = C.bm("fairy_gold", kind)
    mk._bm_torus(b, (cx, cy, spire - 4), 13.0, 1.8, seg=20, rseg=4)
    mk._bm_torus(b, (cx, cy, keep_top + 3.5), R_keep + 4.5, 2.0, seg=28, rseg=4)
    for k in range(12):
        a = 2 * math.pi * k / 12
        for zz in (zc + 70, zc + 100):
            C.rect("win_lit", (cx + math.cos(a) * R_keep, cy + math.sin(a) * R_keep, zz), (math.cos(a), math.sin(a), 0),
                   4.0, 7.0, lift=0.6)
    for sx in (-1, 1):
        for k in range(6):
            C.rect("win_lit", (cx - 70, cy + sx * (8 + k * 7), zc + 24), (-1, 0, 0), 3.0, 5.0, lift=0.3)
    # 첨탑 신전들
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.4
        d = rng.uniform(240, 380)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        fairy_tower(C, x, y, h(x, y), r=6, h=rng.uniform(34, 52), roof=rng.choice(("fairy_roof_b", "fairy_roof")),
                    roof_h=rng.uniform(24, 34), kind=kind)
    return {"center": Vector((cx, cy, zc)), "palace_top": Vector((cx, cy, spire + 40)),
            "gate_west": Vector((gx, gy, h(gx, gy)))}


def fairy_watchtower(C, x, y, h, *, kind="far"):
    """에르피엔 바깥 망루 (언덕 위 외딴 석탑, 레이저 기준점). 반환: 지붕 꼭대기(금 첨탑 끝) 점."""
    z = h(x, y)
    # 작은 성벽 고리
    m = 10
    for i in range(m):
        a0 = 2 * math.pi * i / m
        a1 = 2 * math.pi * (i + 1) / m
        q = [(x + math.cos(a0) * 16, y + math.sin(a0) * 16), (x + math.cos(a1) * 16, y + math.sin(a1) * 16),
             (x + math.cos(a1) * 17.5, y + math.sin(a1) * 17.5), (x + math.cos(a0) * 17.5, y + math.sin(a0) * 17.5)]
        mk.lod_poly_prism(C, "fairy_stone", q, z - 2, z + 4.5, kind=kind)
    mk.lod_gable(C, "fairy_stone", "fairy_roof_r", x + 4, x + 12, y - 4, y + 4, z - 1, z + 4, z + 6.5, axis="x",
                 kind=kind)
    C.cyl("fairy_stone", (x, y, z - 2), (x, y, z + 26), 4.6, r2=4.0, segs=10, kind=kind, cap=False)
    C.cyl("fairy_stone_d", (x, y, z + 26), (x, y, z + 28.2), 5.3, segs=10, kind=kind)
    C.cyl("fairy_roof", (x, y, z + 28.2), (x, y, z + 38), 5.5, r2=0.0, segs=10, kind=kind)
    C.cyl("fairy_gold", (x, y, z + 37), (x, y, z + 41.5), 0.35, r2=0.0, segs=4, kind=kind, smooth=False)
    C.rect("win_lit", (x - 4.2, y, z + 22), (-1, 0, 0), 1.4, 2.2, lift=0.25)
    # 깃발: 에르피엔 군기 (lib/erpien_flag.far_flag, 초록 바탕 + 노란 나비). 깃대 7 m, 천은 +Y로
    ef.far_flag(ef.city(C), Matrix.Translation((x + 2.5, y, z + 33)) @ Matrix.Rotation(math.pi / 2, 4, "Z"), W=3.6,
                pole=6.8, r=0.12, layers={"pole": kind, "cloth": kind})
    return Vector((x, y, z + 41.5)), Vector((x, y, z + 28.2))


# ================================================================== 원경: 정령산 감시 초소, R41

def watch_post(C, x, y, z, *, kind="far"):
    """정령산 능선의 감시 초소 실루엣: 돌 기단 + 나무 망루(4기둥) + 지붕 + 깃대. 반환: 망루 바닥 점."""
    C.box("rock", x - 4, x + 4, y - 3.5, y + 3.5, z - 3, z + 2.5, kind=kind)
    mk.lod_gable(C, "wood_d", "roof", x + 4.5, x + 11, y - 3, y + 3, z - 2, z + 2.8, z + 4.6, axis="y", kind=kind)
    fz = z + 10.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.cyl("wood_d", (x + sx * 2.6, y + sy * 2.6, z + 2.5), (x + sx * 1.9, y + sy * 1.9, fz), 0.3, segs=4,
                  kind=kind, smooth=False)
    C.box("wood", x - 2.6, x + 2.6, y - 2.6, y + 2.6, fz - 0.5, fz, kind=kind)
    C.box("wood_d", x - 2.6, x + 2.6, y - 2.6, y + 2.6, fz, fz + 1.2, kind=kind)
    mk.lod_gable(C, "wood", "roof", x - 2.9, x + 2.9, y - 2.9, y + 2.9, fz + 2.6, fz + 2.8, fz + 4.4, axis="x",
                 kind=kind)
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.box("wood_d", x + sx * 2.5 - 0.15, x + sx * 2.5 + 0.15, y + sy * 2.5 - 0.15, y + sy * 2.5 + 0.15,
                  fz, fz + 2.7, kind=kind)
    C.cyl("metal", (x - 6, y, z), (x - 6, y, z + 15), 0.15, segs=4, kind=kind)
    C.poly("gold", [(x - 6, y, z + 14.8), (x - 6, y + 3.4, z + 14.4), (x - 6, y + 3.2, z + 12.6), (x - 6, y, z + 12.9)],
           kind="fine")
    return Vector((x, y, fz))


def r41_camp(C, x, y, h, *, seed=0, n=6, kind="far", beacon=True, yaw_deg=0.0):
    """R41 전방 진지 (원경): 어두운 차량 상자·막사·방벽 + 마젠타 표시등."""
    rng = random.Random(seed)
    a = math.radians(yaw_deg)
    D = Vector((math.cos(a), math.sin(a), 0))
    S = Vector((-D.y, D.x, 0))
    for k in range(n):
        p = Vector((x, y, 0)) + D * rng.uniform(-30, 30) + S * rng.uniform(-22, 22)
        z = h(p.x, p.y)
        if rng.random() < 0.6:
            C.rbox("r41_shell", (p.x, p.y, z + 1.4), (7.0, 3.2, 2.8), (0, 0, yaw_deg + rng.uniform(-20, 20)),
                   kind=kind)
            C.rbox("r41_metal", (p.x, p.y, z + 3.0), (2.6, 2.0, 0.8), (0, 0, yaw_deg + rng.uniform(-30, 30)),
                   kind=kind)
        else:
            mk.lod_gable(C, "r41_metal", "r41_shell", p.x - 4, p.x + 4, p.y - 3, p.y + 3, z - 0.5, z + 2.2, z + 3.6,
                         axis="x", kind=kind)
    # 방벽 (육각 벌집 문법: 비스듬한 판)
    for k in range(5):
        p = Vector((x, y, 0)) + D * (-38) + S * (-20 + k * 10)
        C.rbox("r41_light", (p.x, p.y, h(p.x, p.y) + 1.0), (1.2, 8.5, 2.2), (0, 0, yaw_deg), kind=kind)
    if beacon:
        z = h(x, y)
        C.cyl("r41_metal", (x, y, z), (x, y, z + 14), 0.3, segs=4, kind=kind)
        C.blob("magenta", (x, y, z + 14.6), 0.9, segs=6, rings=4, kind="fine")


def launch_site(C, x, y, h, *, kind="far"):
    """R41 반물질 중성자탄 발사장 (원경, 오리지널): 발사대 판 + 비스듬한 발사 레일 탑 + 벙커 + 마젠타 슬릿등.
    반환: 발사 레일 끝(탄이 떠나는 점)."""
    z = h(x, y)
    C.box("r41_metal", x - 40, x + 40, y - 40, y + 40, z - 2, z + 1.5, kind=kind)
    # 육각 발사구 고리
    hexo = [(x + math.cos(math.radians(30 + 60 * k)) * 16, y + math.sin(math.radians(30 + 60 * k)) * 16)
            for k in range(6)]
    hexi = [(x + math.cos(math.radians(30 + 60 * k)) * 11, y + math.sin(math.radians(30 + 60 * k)) * 11)
            for k in range(6)]
    C.ring_prism("r41_shell", hexo, hexi, z + 1.5, z + 6, kind=kind)
    # 발사 레일 탑 (남서쪽, 즉 모나티엄·에르피엔 쪽으로 기운 트러스)
    base = Vector((x + 4, y + 4, z + 6))
    tip = Vector((x - 16, y - 20, z + 78))
    up = Vector((0, 0, 1))
    d = (tip - base).normalized()
    side = d.cross(up).normalized()
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            off = side * (s1 * 2.4) + d.cross(side).normalized() * (s2 * 2.4)
            C.cyl("r41_shell", tuple(base + off), tuple(tip + off), 0.6, segs=4, kind=kind, smooth=False)
    for k in range(9):
        p = base.lerp(tip, (k + 0.5) / 9)
        C.rbox("r41_metal", tuple(p), (5.6, 5.6, 0.8), (0, -math.degrees(math.acos(d.z)), math.degrees(
            math.atan2(d.y, d.x))), kind=kind)
    # 받침 다리
    C.cyl("r41_shell", (x - 4, y - 6, z + 6), tuple(base.lerp(tip, 0.55)), 1.2, segs=4, kind=kind, smooth=False)
    # 벙커 (45° 모따기 상자) + 마젠타 슬릿
    # (둘째 벙커는 발사대 서쪽 끝에서 50 cm 안쪽: 끝이 맞으면 벙커 옆면이 발사대 옆면과 한 평면이 된다)
    for (bx, by, w, dd, hh) in ((x + 30, y + 20, 22, 14, 9), (x - 31.5, y + 24, 16, 12, 7), (x + 26, y - 30, 18, 10, 8)):
        zb = h(bx, by)
        pts = [(bx - w / 2 + 3, by - dd / 2), (bx + w / 2 - 3, by - dd / 2), (bx + w / 2, by - dd / 2 + 3),
               (bx + w / 2, by + dd / 2 - 3), (bx + w / 2 - 3, by + dd / 2), (bx - w / 2 + 3, by + dd / 2),
               (bx - w / 2, by + dd / 2 - 3), (bx - w / 2, by - dd / 2 + 3)]
        C.prism("r41_shell", pts, zb - 1, zb + hh, kind=kind, top=True)
        C.box("magenta", bx - w / 2 + 3, bx + w / 2 - 3, by - dd / 2 - 0.1, by - dd / 2, zb + hh * 0.6,
              zb + hh * 0.6 + 0.7, kind="fine")
        C.box("magenta", bx - w / 2 - 0.1, bx - w / 2, by - 2, by + 2, zb + hh * 0.6, zb + hh * 0.6 + 0.7,
              kind="fine")
    # 안테나 + 표시등
    for (ax, ay, ah) in ((x + 34, y + 22, 34), (x - 30, y + 30, 26)):
        C.cyl("r41_metal", (ax, ay, h(ax, ay)), (ax, ay, h(ax, ay) + ah), 0.5, segs=4, kind=kind)
        C.blob("magenta", (ax, ay, h(ax, ay) + ah + 1), 1.4, segs=6, rings=4, kind="fine")
    C.blob("magenta", tuple(tip + d * 2), 1.8, segs=6, rings=4, kind="fine")
    return tip + d * 3


def smoke(C, x, y, z, *, h=90.0, r=10.0, drift=(0.35, 0.1), seed=0, dark=0.45, fire=True, kind="far", segs=6,
          rings=4):
    """연기 기둥 (mk.smoke_column과 같은 생김새, kind·분할을 고를 수 있다). 덩어리가 서로 겹치게 쌓아 구슬 꿰미처럼
    보이지 않게 한다. 바닥 불씨는 UNLIT 주황."""
    rng = random.Random(seed)
    if fire:
        C.blob("fire", (x, y, z + r * 0.2), r * 0.5, (1, 1, 0.45), segs=6, rings=3, kind="fine")
        C.blob("fire_c", (x, y, z + r * 0.15), r * 0.25, (1, 1, 0.5), segs=6, rings=3, kind="fine")
    zz = z + r * 0.45
    segs, rings = max(segs, 7), max(rings, 5) if kind != "main" else rings
    while zz < z + h:
        t = (zz - z) / h
        rr = r * (0.5 + 1.3 * t) * rng.uniform(0.9, 1.1)
        cx = x + drift[0] * (zz - z) + rng.uniform(-0.12, 0.12) * rr
        cy = y + drift[1] * (zz - z) + rng.uniform(-0.12, 0.12) * rr
        C.blob("smoke_d" if t < dark else "smoke_l", (cx, cy, zz), rr, (1.0, 1.0, 0.75), segs=segs, rings=rings,
               rot_z=rng.uniform(0, 3), kind=kind)
        zz += rr * 1.05


def cloud(C, x, y, z, *, size=140.0, seed=0, key="cloud_k", kind="far", n=5):
    """납작한 원경 구름 (아래가 평평한 덩어리, 낮은 분할)."""
    rng = random.Random(seed)
    for i in range(n):
        u = (i - (n - 1) / 2) / ((n - 1) / 2)
        r = size * (0.42 - 0.18 * abs(u)) * rng.uniform(0.85, 1.15)
        C.blob(key, (x + u * size * 0.9, y + rng.uniform(-0.3, 0.3) * size * 0.3, z + r * 0.3), r, (1.2, 1.0, 0.55),
               segs=7, rings=4, kind=kind)


# ================================================================== 새벽 하늘 돔 (skyNode)

def _vc_unlit_material(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    node = nt.nodes.new("ShaderNodeVertexColor")
    node.layer_name = "Col"
    nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    m.use_backface_culling = True   # 안쪽만 보인다 (뷰어의 바깥 시점에서는 사라짐)
    return m


def sky_dome(C, name, loc, color_fn, *, radius=6600.0, segs=32, elevs=(-10, -1, 0.6, 2, 4, 7, 11, 17, 26, 40, 58,
                                                                           90), extras=None):
    """카메라를 따라다니는 하늘 돔 (루트 속성 skyNode=<name>). 정점색 UNLIT (안쪽 면), 원점 = 카메라.
    color_fn(azimuth_deg(0=동, 반시계), elevation_deg) → '#rrggbb'. extras(b_by_key) → 달·별 같은 UNLIT 장식(로컬 좌표).
    엔진: 노드 처음 자리를 기준점으로 카메라가 움직인 만큼 노드를 옮긴다(GameLevel). 그래서 돔 중심 = 카메라."""
    root = cb.empty(name, loc=loc, size=1.0)
    root["noOutline"] = 1
    b = bmesh.new()
    rows = []
    for e in elevs:
        er = math.radians(e)
        if e >= 90:
            rows.append([(Vector((0, 0, radius)), 0.0, 90.0)])
            continue
        row = []
        for i in range(segs):
            az = 360.0 * i / segs
            a = math.radians(az)
            row.append((Vector((math.cos(a) * math.cos(er) * radius, math.sin(a) * math.cos(er) * radius,
                                math.sin(er) * radius)), az, e))
        rows.append(row)
    vrows = [[(b.verts.new(p), az, e) for (p, az, e) in row] for row in rows]
    lay = None
    faces = []
    for k in range(len(vrows) - 1):
        lo, hi = vrows[k], vrows[k + 1]
        for i in range(segs):
            i2 = (i + 1) % segs
            if len(hi) == 1:
                f = b.faces.new((lo[i][0], lo[i2][0], hi[0][0]))
            else:
                f = b.faces.new((lo[i][0], lo[i2][0], hi[i2][0], hi[i][0]))
            faces.append(f)
    # 안쪽을 보게 (법선이 중심을 향함)
    for f in faces:
        f.normal_update()
        c = f.calc_center_median()
        if f.normal.dot(c) > 0:
            f.normal_flip()
    me = bpy.data.meshes.new(f"{name}_sky")
    b.to_mesh(me)
    b.free()
    ca = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="CORNER")
    # 정점 → 방위·고도 (위치로 다시 계산)
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            r = v.length
            el = math.degrees(math.asin(max(-1.0, min(1.0, v.z / r))))
            az = math.degrees(math.atan2(v.y, v.x)) % 360.0
            col = cb.hex_lin(color_fn(az, el))
            ca.data[li].color = (*col, 1.0)
    me.color_attributes.active_color = ca
    o = bpy.data.objects.new(f"{name}_sky", me)
    cb.link(o)
    o.data.materials.append(_vc_unlit_material("UNLIT_ov_sky_vc"))
    o.parent = root
    o["collider"] = 0
    o["noOutline"] = 1
    if extras:
        bys = {}
        extras(bys)
        for key, bb in bys.items():
            me2 = bpy.data.meshes.new(f"{name}_{key}")
            bb.to_mesh(me2)
            bb.free()
            o2 = bpy.data.objects.new(f"{name}_{key}", me2)
            cb.link(o2)
            cb.assign(o2, mk.M(key))
            o2.parent = root
            o2["collider"] = 0
            o2["noOutline"] = 1
    C.add_node(root)
    return root
