"""모나티엄 지하 키트 (monatium_subway_kit).

[오리지널] 모나티엄 지하철 서부선(섬식 승강장 역, 복선 터널, 멈춘 전동차)과 진압반 지하 시설(연락 통로, 병기창고,
차량 경사로, 정비 계단)을 모듈로 조립한다. 원작에는 지하철과 병기창고가 나오지 않는다. 형태는 도시 키트의 문법
(크림 타일, 남색 표지 + 금색 엘프 로고 원판, 시안 네트워크 발광, 헌글 표지, 진압반 남보라 + 청록)을 그대로 따른다.
1막 M2 「방어선」 지하 구간(levels/m2_subway.py)이 처음 쓴다. 근거와 규약: docs/art/monatium-city.md, docs/LEVELS.md.

사용:
    import monatium_city_kit as mk
    import monatium_subway_kit as sk
    C = mk.City("m2_subway")
    sk.station_hall(C, -30, 24, 9.4, z_bed=-1.0, z_plat=0.0, z_ceil=4.2)
    sk.island_platform(C, -26, 18, -3.8, 3.8, z_top=0.0, z_bed=-1.0)
    sk.subway_car(C, 40, 52, -2.9, 0.0, -1.0, walk=True, cab=(True, False))
    lamps = sk.LampSet("emerg_01", "r")
    sk.emerg_lamp(C, lamps, (0, 9.4, 3.2), (0, -1, 0))
    lamps.emit(C)
    sk.trig(C, "tunnel", 24, 28, -5.8, 5.8, -1.5, 2.0)

설계 (도시 키트 City 위에 얹는다):
  - 보이는 메시는 도시 키트처럼 (그룹, 머티리얼, 종류)별로 합친다(collider=0). 충돌은 축 정렬 COL_ 박스,
    계단·경사로는 꽉 찬 COL_ 쐐기(col_wedge, trimesh)가 맡는다. 쐐기는 디딤판 앞 모서리를 잇는 경사라 발이 걸리지 않는다.
  - 정전 조명: 비상등은 구역·색마다 LIGHT_ 노드 하나(LampSet)에 렌즈를 모으고, 벽의 붉은 번짐 원판은 그 자식 메시로 둔다
    (노드가 꺼지면 함께 숨는다). 꺼진 렌즈(emerg_off)는 그 아래에 늘 보인다.
  - 문(DOOR_<id>)은 닫힌 자리에 모델링하고 move(three.js 기준)만큼 열린다. 장식은 문 메시의 자식이라 함께 움직인다.
    문 자리에는 COL_를 두지 않는다(엔진이 문 메시로 충돌체를 만든다).
  - 팔레트는 mk.PAL / mk.GLOW / mk.ALPHA에 런타임으로 더한다(도시 키트 파일은 고치지 않는다).

체격: 엘프 기준(키 1.2 m, 자동 오르기 0.28 m). 승강장은 궤도 바닥보다 1.0 m 높고 열차 바닥 = 승강장 높이,
열차 문 1.9 m, 연락 통로 폭 2.4 m, 계단 단 높이 0.15 m.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw
import monatium_city_kit as mk

# ================================================================== palette (런타임 추가)
mk.PAL.update({
    "tile": "#ede5d4",       # 역 벽 타일 (크림)
    "tile_d": "#cbbda4",     # 타일 줄눈
    "tunnel": "#b7b0a8",     # 터널 콘크리트 (밝게: 정전 속에서도 형태가 읽히게)
    "tunnel_d": "#938c86",   # 터널 아래 띠, 천장
    "bed": "#6f6873",        # 궤도 바닥 (자줏빛 콘크리트)
    "rail": "#aaa6b0",       # 레일
    "sleeper": "#aca69e",    # 콘크리트 침목
    "car": "#f2efe8",        # 전동차 몸체
    "car_in": "#e2dccf",     # 전동차 실내 벽
    "car_floor": "#8f8a98",  # 전동차 바닥
    "seat": "#4f86a8",       # 좌석 (모나티엄 청색)
    "line_w": "#e8873a",     # 서부선 노선색 (주황) [오리지널]
    "od": "#646d48",         # 미군 올리브 드랩 (노획품 상자)
    "od_d": "#4b5236",
    "stencil": "#efe7cf",    # 상자 스텐실
    "gun": "#2d2b30",        # 거치대의 총 실루엣
    "gun_t": "#a8916a",      # 탄색 부품
    "steel_d": "#77727c",    # 거치대·선반
    "floor_ar": "#aca8a4",   # 병기창고 바닥 도장
    "floor_ar_d": "#8f8b88",
    "emerg_off": "#5e2a2a",  # 꺼진 비상등 렌즈
    "amber_off": "#6e5126",
    "rubble": "#8f8883",     # 무너진 콘크리트
    "soil_d": "#6a5a4c",
    "cardboard": "#c9a878",
    "lamp_dead": "#7b7787",  # 정전으로 꺼진 조명판 (UNLIT lamp_off는 켜진 듯 밝아서 쓰지 않는다)
})
mk.GLOW.update({
    "emerg_r": "#ff3b30",    # 적색 비상등
    "emerg_a": "#ffb03a",    # 호박색 비상등
    "sig_r": "#ff2a22",      # 신호등 정지
    "day": "#fff3d8",        # 지상 햇빛 (무너진 천장, 경사로 출구)
})
mk.ALPHA.update({
    "halo_r": ("#ff4a38", 0.2),
    "halo_a": ("#ffb446", 0.18),
    "daybeam": ("#fff1d0", 0.16),
    "mesh_a": ("#4a4552", 0.5),   # 탄약 철망
})
mk._DARK.update({"bed", "od_d", "gun", "steel_d", "emerg_off", "amber_off", "car_floor", "soil_d"})

EMERG = {
    # 색: (발광 키, 켜졌을 때 hex, 번짐 키, 꺼진 렌즈 키)
    "r": ("emerg_r", "#ff3b30", "halo_r", "emerg_off"),
    "a": ("emerg_a", "#ffb03a", "halo_a", "amber_off"),
}

CAR_W = 2.5          # 전동차 폭 (엘프 체격)
CAR_H = 2.6          # 바닥에서 지붕 꼭대기
CAR_WALL = 2.2       # 바닥에서 옆벽 위 끝 (지붕 곡면 시작)
DOOR_W, DOOR_H = 1.1, 1.9

_count = {"ramp": 0}
# 천장을 그릴지 (False면 COL만: 위에서 내려다보는 미리보기용 PREVIEW=cut)
CEIL = {"on": True}


def ceil_box(C, key, x0, x1, y0, y1, z0, z1, *, col=True, kind="main"):
    """천장 판. CEIL['on']이 False면 충돌만 남긴다."""
    if CEIL["on"]:
        C.box(key, x0, x1, y0, y1, z0, z1, col=col, kind=kind)
    elif col:
        C.col(x0, x1, y0, y1, z0, z1)


# ================================================================== nodes · collision

def _mesh_obj(name, verts, faces):
    vs = [Vector(v) for v in verts]
    c = sum(vs, Vector()) / len(vs)
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v - c) for v in vs], [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = c
    cb.link(o)
    return o


def _slope_fn(x0, x1, y0, y1, z_lo, z_hi, rise):
    def h(x, y):
        if rise == "+x":
            t = (x - x0) / (x1 - x0)
        elif rise == "-x":
            t = (x1 - x) / (x1 - x0)
        elif rise == "+y":
            t = (y - y0) / (y1 - y0)
        else:
            t = (y1 - y) / (y1 - y0)
        return z_lo + (z_hi - z_lo) * t
    return h


def col_wedge(C, x0, x1, y0, y1, z_lo, z_hi, rise, *, z_floor=None):
    """경사 COL_ (계단·경사로). rise = 높아지는 쪽 '+x' '-x' '+y' '-y'. z_floor부터 경사면까지 꽉 찬 쐐기(trimesh)."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    zf = (min(z_lo, z_hi) - 0.3) if z_floor is None else z_floor
    h = _slope_fn(x0, x1, y0, y1, z_lo, z_hi, rise)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    verts = [(x, y, zf) for x, y in corners] + [(x, y, h(x, y)) for x, y in corners]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    _count["ramp"] += 1
    o = _mesh_obj(f"COL_{C.grp}_ramp_{_count['ramp']:02d}", verts, faces)
    return C.add_node(o)


def wedge(C, key, x0, x1, y0, y1, z_lo, z_hi, rise, *, z_floor, kind="main"):
    """보이는 쐐기 (경사로 바닥)."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    h = _slope_fn(x0, x1, y0, y1, z_lo, z_hi, rise)
    b = C.bm(key, kind)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    lo = [b.verts.new((x, y, z_floor)) for x, y in corners]
    hi = [b.verts.new((x, y, h(x, y))) for x, y in corners]
    faces = [b.faces.new(list(reversed(lo))), b.faces.new(hi)]
    for i in range(4):
        j = (i + 1) % 4
        faces.append(b.faces.new((lo[i], lo[j], hi[j], hi[i])))
    bmesh.ops.recalc_face_normals(b, faces=faces)
    return h


TRIGS: dict[str, tuple] = {}


def trig(C, tid, x0, x1, y0, y1, z0, z1, **props):
    """TRIG_<tid>: 렌더하지 않는 축 정렬 상자 (발이 확실히 들어가게 바닥-0.5 ~ 바닥+3으로 높게)."""
    o = mk._box_obj(f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
    for k, v in props.items():
        o[k] = v
    C.add_node(o)
    TRIGS[tid] = (x0, x1, y0, y1, z0, z1)
    return o


def _child(parent, name, key, build, *, no_outline=True):
    """parent(C.special 결과) 아래 붙는 다른 머티리얼의 메시. build(bm)는 월드 좌표로 그린다."""
    b = bmesh.new()
    build(b)
    if not b.faces:
        b.free()
        return None
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    me.transform(Matrix.Translation(-Vector(parent.location)))
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    cb.assign(o, mk.M(key))
    o.parent = parent
    o["collider"] = 0
    if no_outline:
        o["noOutline"] = 1
    return o


def door(C, did, box, move, *, key="steel", parts=None, props=None):
    """DOOR_<did>: 닫힌 자리의 문짝 상자 box=(x0,x1,y0,y1,z0,z1). move = three.js 열림 이동 "x,y,z".
    parts = [(머티리얼 키, build(bm)), ...] 장식(월드 좌표). 문과 함께 움직인다."""
    x0, x1, y0, y1, z0, z1 = box
    p = {"move": move}
    p.update(props or {})
    o = C.special(f"DOOR_{did}", lambda b: mk._bm_box(b, x0, x1, y0, y1, z0, z1), key, p)
    for i, (k, fn) in enumerate(parts or ()):
        _child(o, f"door_{did}_{k}_{i}", k, fn, no_outline=mk.is_glow(k) or k in ("hazard", "stencil", "dark"))
    return o


def door_text(o, s, size, center, normal, *, key="stencil", up=(0, 0, 1)):
    """문(DOOR_) 위 글자: 문 메시의 자식이라 함께 움직인다."""
    R, U, N = mk.frame(normal, up)
    c = Vector(center) + N * 0.006
    t = mk._text(f"{o.name}_txt{len(o.children)}", s, size, c, R, U, N)
    t.parent = o
    t.matrix_parent_inverse = Matrix.Translation(-Vector(o.location))
    cb.assign(t, mk.M(key))
    t["collider"] = 0
    t["noOutline"] = 1
    return t


# ================================================================== emergency lights

def _bm_disc(b, center, normal, r, n=16, up=(0, 0, 1)):
    R, U, N = mk.frame(normal, up)
    c = Vector(center)
    vs = [b.verts.new(c + R * (r * math.cos(2 * math.pi * i / n)) + U * (r * math.sin(2 * math.pi * i / n)))
          for i in range(n)]
    f = b.faces.new(vs)
    f.normal_update()
    if f.normal.dot(N) < 0:
        f.normal_flip()


class LampSet:
    """LIGHT_<name>: 같은 구역·색의 비상등 렌즈를 메시 하나로 모은다. 번짐 원판은 자식 메시(같이 켜고 꺼짐).
    group: emergency(적색·호박색 비상등) / main(병기창고 평상 조명). on: 처음 상태. blink: 깜빡임 주기(초)."""

    def __init__(self, name, color="r", *, group="emergency", on=1, blink=0.0, key=None, hexcol=None, halo=True):
        self.name = name
        self.color = color
        e = EMERG.get(color)
        self.key = key or (e[0] if e else "lamp")
        self.hex = hexcol or (e[1] if e else mk.GLOW.get(self.key, "#fff1c9"))
        self.halo_key = (e[2] if e else None) if halo else None
        self.off_key = e[3] if e else "lamp_off"
        self.group = group
        self.on = on
        self.blink = blink
        self.lens: list = []
        self.halos: list = []

    def add(self, fn):
        self.lens.append(fn)

    def add_halo(self, center, normal, r, up=(0, 0, 1)):
        if self.halo_key:
            self.halos.append((tuple(center), tuple(normal), r, tuple(up)))

    def emit(self, C):
        if not self.lens:
            return None
        props = {"emissiveToggle": 1, "group": self.group, "on": int(self.on), "color": self.hex, "range": 9.0}
        if self.blink:
            props["blink"] = float(self.blink)
        fns = list(self.lens)
        o = C.special(f"LIGHT_{self.name}", lambda b: [f(b) for f in fns], self.key, props, kind="fine")
        if self.halos:
            hs = list(self.halos)

            def build(b):
                for (c, n, r, up) in hs:
                    _bm_disc(b, c, n, r, n=18, up=up)
            _child(o, f"halo_{self.name}", self.halo_key, build)
        return o


def emerg_lamp(C, ls, pos, normal, *, w=0.34, h=0.14, halo=0.9, up=(0, 0, 1), halo_lift=0.02):
    """벽 비상등: 남색 받침 + 꺼진 렌즈(늘 보임) + 발광 렌즈(ls에 모음) + 벽 번짐 원판.
    halo_lift: 번짐 원판이 벽에서 뜬 거리. 벽에 2 cm 띠(room의 band)나 hazard_frame이 있으면 그 면과 겹치지 않게 키운다."""
    P, N = Vector(pos), Vector(normal).normalized()
    R, U, _ = mk.frame(N, up)
    C.plate("navy", hw.rrect(w + 0.12, h + 0.12, 0.05, 2), tuple(P), tuple(N), 0.05, up=up, kind="detail")
    lc = P + N * 0.05
    C.plate(ls.off_key, hw.stadium(w, h, 4), tuple(lc), tuple(N), 0.06, up=up, kind="detail")
    pts = hw.stadium(w + 0.01, h + 0.01, 4)

    def fn(b, lc=lc + N * 0.065, R=R, U=U, N=N):
        vs = [b.verts.new(lc + R * u + U * v) for u, v in pts]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.dot(N) < 0:
            f.normal_flip()
    ls.add(fn)
    if halo:
        ls.add_halo(P + N * halo_lift, N, halo, up=up)


def ceiling_lamp(C, ls, pos, *, r=0.16, halo=0.0):
    """천장 비상등 (아래를 보는 둥근 렌즈)."""
    P = Vector(pos)
    C.cyl("navy", tuple(P), tuple(P - Vector((0, 0, 0.06))), r + 0.05, segs=10, kind="detail")
    C.cyl(ls.off_key, tuple(P - Vector((0, 0, 0.06))), tuple(P - Vector((0, 0, 0.13))), r, r2=r * 0.8, segs=10,
          kind="detail")

    def fn(b, P=P):
        mk._bm_cyl(b, P - Vector((0, 0, 0.055)), P - Vector((0, 0, 0.14)), r + 0.01, segs=10, r2=r * 0.8 + 0.01)
    ls.add(fn)
    if halo:
        ls.add_halo(P - Vector((0, 0, 0.005)), (0, 0, -1), halo, up=(0, 1, 0))


def beacon(C, ls, base, *, r=0.16, h=0.3, halo=1.1, wall_normal=None):
    """회전 경광등 (받침 + 꺼진 렌즈 + 발광 렌즈). wall_normal이 있으면 벽 받침대와 번짐을 단다."""
    b = Vector(base)
    if wall_normal is not None:
        N = Vector(wall_normal).normalized()
        C.beam("metal", tuple(b - N * 0.3 - Vector((0, 0, 0.05))), tuple(b - Vector((0, 0, 0.05))), 0.08, 0.08,
               kind="detail")
        ls.add_halo(b - N * 0.29 + Vector((0, 0, 0.15)), N, halo)
    C.cyl("metal", tuple(b - Vector((0, 0, 0.08))), tuple(b), r + 0.04, segs=10, kind="detail")
    C.cyl(ls.off_key, tuple(b), tuple(b + Vector((0, 0, h))), r, r2=r * 0.75, segs=10, kind="detail")
    C.cyl("gold", tuple(b + Vector((0, 0, h))), tuple(b + Vector((0, 0, h + 0.04))), r * 0.45, segs=8, kind="detail")

    def fn(bm, b=b):
        mk._bm_cyl(bm, b + Vector((0, 0, 0.01)), b + Vector((0, 0, h + 0.01)), r + 0.012, segs=10, r2=r * 0.75 + 0.012)
    ls.add(fn)


def main_panel(C, ls, xc, yc, z, lx, ly):
    """천장 평상 조명판 (LIGHT_main): 남색 테 + 꺼진 판(lamp_dead, 늘 보임) + 발광판(ls)."""
    C.box("navy", xc - lx / 2 - 0.07, xc + lx / 2 + 0.07, yc - ly / 2 - 0.07, yc + ly / 2 + 0.07, z - 0.06, z,
          kind="detail")
    C.decal("lamp_dead", hw.rrect(lx, ly, 0.08, 2), (xc, yc, z - 0.06), (0, 0, -1), up=(0, 1, 0), lift=0.004)
    pts = hw.rrect(lx, ly, 0.08, 2)

    def fn(b):
        c = Vector((xc, yc, z - 0.06 - 0.009))
        R, U, N = mk.frame((0, 0, -1), (0, 1, 0))
        vs = [b.verts.new(c + R * u + U * v) for u, v in pts]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.z > 0:
            f.normal_flip()
    ls.add(fn)


# ================================================================== walls · rooms

def wall_x(C, key, x0, x1, y0, y1, z0, z1, openings=(), *, col=True, kind="main"):
    """X 방향으로 뻗은 벽(두께 = y0..y1). openings = [(x_a, x_b, z_아래, z_위)]: 그 구간을 비운다."""
    x = x0
    for (a, b, zb, zt) in sorted(openings):
        a, b = max(a, x0), min(b, x1)
        if b <= a:
            continue
        if a > x:
            C.box(key, x, a, y0, y1, z0, z1, kind=kind, col=col)
        if zb > z0:
            C.box(key, a, b, y0, y1, z0, min(zb, z1), kind=kind, col=col)
        if zt < z1:
            C.box(key, a, b, y0, y1, max(zt, z0), z1, kind=kind, col=col)
        x = max(x, b)
    if x < x1:
        C.box(key, x, x1, y0, y1, z0, z1, kind=kind, col=col)


def wall_y(C, key, x0, x1, y0, y1, z0, z1, openings=(), *, col=True, kind="main"):
    """Y 방향으로 뻗은 벽(두께 = x0..x1). openings = [(y_a, y_b, z_아래, z_위)]."""
    y = y0
    for (a, b, zb, zt) in sorted(openings):
        a, b = max(a, y0), min(b, y1)
        if b <= a:
            continue
        if a > y:
            C.box(key, x0, x1, y, a, z0, z1, kind=kind, col=col)
        if zb > z0:
            C.box(key, x0, x1, a, b, z0, min(zb, z1), kind=kind, col=col)
        if zt < z1:
            C.box(key, x0, x1, a, b, max(zt, z0), z1, kind=kind, col=col)
        y = max(y, b)
    if y < y1:
        C.box(key, x0, x1, y, y1, z0, z1, kind=kind, col=col)


def grid_face(C, key, axis, c, a0, a1, z0, z1, side, *, du=0.6, dv=0.6, w=0.03, lift=0.008, skip=()):
    """벽면 줄눈. axis='x'면 면이 y=c에 있고(x a0..a1), 'y'면 x=c(y a0..a1). side = 면이 바라보는 쪽(±1).
    skip = [(a_a, a_b, z_아래, z_위)]: 그 구간(문 구멍)에는 세로 줄눈을 긋지 않는다."""
    N = (0, side, 0) if axis == "x" else (side, 0, 0)

    def P(a, z):
        return (a, c, z) if axis == "x" else (c, a, z)
    a = a0 + du
    while a < a1 - 0.05:
        if not any(s0 - 0.02 <= a <= s1 + 0.02 for (s0, s1, _, _) in skip):
            C.strip(key, P(a, z0), P(a, z1), w, N, lift=lift)
        a += du
    z = z0 + dv
    while z < z1 - 0.05:
        segs = [(a0, a1)]
        for (s0, s1, zb, zt) in skip:
            if zb <= z <= zt:
                nxt = []
                for (p, q) in segs:
                    if s1 <= p or s0 >= q:
                        nxt.append((p, q))
                    else:
                        if s0 > p:
                            nxt.append((p, s0))
                        if s1 < q:
                            nxt.append((s1, q))
                segs = nxt
        for (p, q) in segs:
            if q - p > 0.05:
                C.strip(key, P(p, z), P(q, z), w, N, lift=lift)
        z += dv


def room(C, x0, x1, y0, y1, z0, h, *, t=0.3, openings=None, walls="nsew", wall_key="concrete", floor_key="floor_ar",
         ceil_key="navy_l", band="violet", band_z=0.9, ceil=True, grout="floor_ar_d", tile=1.2, kick="navy"):
    """사각 실내(통로·전실): 바닥(+COL), 천장(+COL), 네 벽(구멍 openings={'n'|'s'|'e'|'w': [(a, b, z_아래, z_위)]}),
    진압반 남보라 띠(벽 안쪽 면, 높이 band_z), 걸레받이. a, b는 벽 방향 절대 좌표(n/s는 x, e/w는 y), z도 절대."""
    op = openings or {}
    zt = z0 + h
    mk.paving(C, x0, x1, y0, y1, z=z0, key=floor_key, grout=grout, tile=tile, t=0.3)
    if ceil:
        ceil_box(C, ceil_key, x0 - t, x1 + t, y0 - t, y1 + t, zt, zt + 0.3)
    if "n" in walls:
        wall_x(C, wall_key, x0 - t, x1 + t, y1, y1 + t, z0 - 0.3, zt, op.get("n", ()))
        if band:
            wall_x(C, band, x0, x1, y1 - 0.02, y1, z0 + band_z, z0 + band_z + 0.14, op.get("n", ()), col=False,
                   kind="detail")
        wall_x(C, kick, x0, x1, y1 - 0.03, y1, z0, z0 + 0.12, op.get("n", ()), col=False, kind="detail")
    if "s" in walls:
        wall_x(C, wall_key, x0 - t, x1 + t, y0 - t, y0, z0 - 0.3, zt, op.get("s", ()))
        if band:
            wall_x(C, band, x0, x1, y0, y0 + 0.02, z0 + band_z, z0 + band_z + 0.14, op.get("s", ()), col=False,
                   kind="detail")
        wall_x(C, kick, x0, x1, y0, y0 + 0.03, z0, z0 + 0.12, op.get("s", ()), col=False, kind="detail")
    if "e" in walls:
        wall_y(C, wall_key, x1, x1 + t, y0, y1, z0 - 0.3, zt, op.get("e", ()))
        if band:
            wall_y(C, band, x1 - 0.02, x1, y0, y1, z0 + band_z, z0 + band_z + 0.14, op.get("e", ()), col=False,
                   kind="detail")
        wall_y(C, kick, x1 - 0.03, x1, y0, y1, z0, z0 + 0.12, op.get("e", ()), col=False, kind="detail")
    if "w" in walls:
        wall_y(C, wall_key, x0 - t, x0, y0, y1, z0 - 0.3, zt, op.get("w", ()))
        if band:
            wall_y(C, band, x0, x0 + 0.02, y0, y1, z0 + band_z, z0 + band_z + 0.14, op.get("w", ()), col=False,
                   kind="detail")
        wall_y(C, kick, x0, x0 + 0.03, y0, y1, z0, z0 + 0.12, op.get("w", ()), col=False, kind="detail")


def pipes(C, p0, p1, *, n=2, r=0.07, step=(0, 0.22, 0), keys=("steel", "teal"), brackets=3.0):
    """천장 배관 다발 (p0→p1, 옆으로 step씩 벌림) + 걸쇠."""
    P0, P1, S = Vector(p0), Vector(p1), Vector(step)
    for i in range(n):
        C.cyl(keys[i % len(keys)], tuple(P0 + S * i), tuple(P1 + S * i), r * (1.0 - 0.2 * (i % 2)), segs=8,
              kind="detail", cap=False)
    L = (P1 - P0).length
    m = max(1, int(L / brackets))
    for k in range(m + 1):
        p = P0 + (P1 - P0) * (k / m)
        C.beam("metal", tuple(p - S * 0.5 + Vector((0, 0, r + 0.02))), tuple(p + S * (n - 0.5) + Vector((0, 0, r + 0.02))),
               0.05, 0.04, kind="detail")


def sign(C, center, normal, w, h, lines, *, key="navy", rim="gold", logo=False, depth=0.05, up=(0, 0, 1)):
    """남색 표지판 + 금테. lines = [(글자, 크기, 머티리얼, 세로 위치 v, 가로 위치 u)].
    금테 판은 뒷면을 판 뒷면보다 4 mm 뒤에 둔다(앞면은 그대로): 같은 평면이면 벽에서 뜬 표지(철망 우리, 벽 끝을 넘는
    표지)의 뒷면이 남색·금색으로 번갈아 깜빡인다."""
    c, N = Vector(center), Vector(normal).normalized()
    R, U, _ = mk.frame(N, up)
    if rim:
        C.plate(rim, hw.rrect(w + 0.08, h + 0.08, min(0.16, h * 0.3), 2), tuple(c), tuple(N), depth * 0.6 + 0.004,
                up=up, kind="detail", back=0.004)
    C.plate(key, hw.rrect(w, h, min(0.14, h * 0.28), 2), tuple(c), tuple(N), depth, up=up, kind="detail")
    f = c + N * depth
    for (s, size, k, v, u) in lines:
        C.text(k, s, size, tuple(f + U * v + R * u), tuple(N), up=up, lift=0.01)
    if logo:
        C.logo(tuple(f + R * (w / 2 - h * 0.5)), h * 0.62, tuple(N), up=up, key="gold", disc="navy_l", lift=0.01)


def hazard_frame(C, center, normal, w, h, *, band=0.16, up=(0, 0, 1), lift=0.012, block=0.3):
    """문 구멍 둘레 노랑·검정 띠 (위와 양옆). center = 구멍 가운데, w·h = 구멍 크기.
    노랑과 검정 칸을 번갈아 나란히 놓는다(한 평면, 겹침 없음). 노랑 띠 위에 검정 칸을 몇 mm 띄워 얹으면 같은 편향 등급이라
    수십 m 밖에서 깜빡인다(기본 깊이 버퍼, docs/art/zfight-audit.md)."""
    c, N = Vector(center), Vector(normal).normalized()
    for (u0, u1, v0, v1) in ((-w / 2 - band, w / 2 + band, h / 2, h / 2 + band),
                             (-w / 2 - band, -w / 2, -h / 2, h / 2),
                             (w / 2, w / 2 + band, -h / 2, h / 2)):
        horiz = (u1 - u0) > (v1 - v0)
        a, b_ = (u0, u1) if horiz else (v0, v1)
        edges = [a]
        while edges[-1] < b_ - 0.02:
            edges.append(min(edges[-1] + block, b_))
        if len(edges) == 1:
            edges.append(b_)
        edges[-1] = b_   # 2 cm 미만 자투리는 마지막 칸에 붙인다
        for i in range(len(edges) - 1):
            k, e = edges[i], edges[i + 1]
            q = [(k, v0), (e, v0), (e, v1), (k, v1)] if horiz else [(u0, k), (u1, k), (u1, e), (u0, e)]
            C.decal("dark" if i % 2 else "hazard", q, tuple(c), tuple(N), up=up, lift=lift)


# ================================================================== station

def station_hall(C, x0, x1, y_half, *, z_bed, z_plat, z_ceil, t=0.4, ends=None, rib_pitch=3.0,
                 lamp_rows=(-1.9, 1.9), glow_z=None, band=(1.0, 2.35)):
    """섬식 승강장 역 상자: 궤도 바닥(+COL), 옆벽(아래 콘크리트 띠, 크림 타일, 남색 표지 띠, 시안 네트워크 선),
    천장(남색 판, 리브, 꺼진 조명판). ends = {'w': [(y_a, y_b, z_아래, z_위)], 'e': [...]}: 끝벽 구멍(터널 입구)."""
    ends = ends or {}
    C.box("bed", x0, x1, -y_half, y_half, z_bed - 0.3, z_bed, col=True)
    for s in (-1, 1):
        y0, y1 = sorted((s * y_half, s * (y_half + t)))
        C.box("tile", x0 - t, x1 + t, y0, y1, z_bed - 0.3, z_ceil + 0.3, col=True)
        yf = s * y_half
        # 아래 콘크리트 띠 (궤도 높이에서 승강장 위 0.5 m까지)
        ya, yb = sorted((yf, yf - s * 0.03))
        C.box("tunnel_d", x0, x1, ya, yb, z_bed, z_plat + 0.5, kind="detail")
        # 남색 표지 띠 + 금색 선
        C.box("navy", x0, x1, ya, yb, z_plat + band[0], z_plat + band[1], kind="detail")
        C.strip("gold", (x0, yf - s * 0.03, z_plat + band[1] + 0.06), (x1, yf - s * 0.03, z_plat + band[1] + 0.06),
                0.05, (0, -s, 0), lift=0.004)
        grid_face(C, "tile_d", "x", yf, x0, x1, z_plat + 0.5, z_plat + band[0], -s, du=0.6, dv=0.25, lift=0.006)
        grid_face(C, "tile_d", "x", yf, x0, x1, z_plat + band[1] + 0.1, z_ceil, -s, du=0.6, dv=0.6, lift=0.006)
        gz = glow_z if glow_z is not None else z_ceil - 0.45
        C.strip("glow", (x0, yf - s * 0.031, gz), (x1, yf - s * 0.031, gz), 0.06, (0, -s, 0), lift=0.004)
    # 끝벽
    for side, xa, xb in (("w", x0 - t, x0), ("e", x1, x1 + t)):
        wall_y(C, "tile", xa, xb, -y_half, y_half, z_bed - 0.3, z_ceil + 0.3, ends.get(side, ()))
    # 천장
    ceil_box(C, "navy", x0, x1, -y_half, y_half, z_ceil, z_ceil + 0.3)
    if not CEIL["on"]:
        return
    n = max(1, round((x1 - x0) / rib_pitch))
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        C.box("metal", x - 0.1, x + 0.1, -y_half, y_half, z_ceil - 0.2, z_ceil, kind="detail")
    for i in range(n):
        xc = x0 + (x1 - x0) * (i + 0.5) / n
        for yc in lamp_rows:
            C.box("navy_l", xc - 0.75, xc + 0.75, yc - 0.3, yc + 0.3, z_ceil - 0.05, z_ceil, kind="detail")
            C.decal("lamp_dead", hw.rrect(1.3, 0.42, 0.08, 2), (xc, yc, z_ceil - 0.05), (0, 0, -1), up=(0, 1, 0),
                    lift=0.004)


def island_platform(C, x0, x1, y0, y1, *, z_top, z_bed, steps=("w", "e"), step_w=2.4, tile=0.8, rail_h=1.0):
    """섬식 승강장: 판석 윗면, 가장자리 흰 마감돌 + 노란 점자 띠, 가장자리 아래 대피 홈(어두운 띠),
    양 끝 궤도로 내려가는 정비 계단(쐐기 COL) + 끝 난간(COL)."""
    yc = (y0 + y1) / 2
    mk.paving(C, x0, x1, y0, y1, z=z_top, key="pave", grout="pave_d", tile=tile, t=0.2)
    C.box("tunnel_d", x0, x1, y0 + 0.3, y1 - 0.3, z_bed, z_top - 0.2, col=True)
    for s, ye in ((-1, y0), (1, y1)):
        C.strip("white", (x0, ye - s * 0.12, z_top), (x1, ye - s * 0.12, z_top), 0.24, lift=0.012)
        C.strip("hazard", (x0, ye - s * 0.52, z_top), (x1, ye - s * 0.52, z_top), 0.3, lift=0.012)
        # 마감돌 앞면 주황 띠 (서부선)
        C.strip("line_w", (x0, ye, z_top - 0.1), (x1, ye, z_top - 0.1), 0.08, (0, s, 0), lift=0.008)
    for side in steps:
        xe = x1 if side == "e" else x0
        d = 1 if side == "e" else -1
        n = 7
        tread = 0.3
        ya, yb = yc - step_w / 2, yc + step_w / 2
        s_bot = xe + d * (n - 1) * tread
        stair_flight(C, "x", ya, yb, s_bot, -d, z_bed, z_top, n, tread=tread, key="steel_d", top_key="steel",
                     z_floor=z_bed)
        # 끝 난간 (계단 자리 비움) + 계단 옆 난간
        for (p, q) in ((y0 + 0.05, ya), (yb, y1 - 0.05)):
            railing(C, (xe - d * 0.08, p, z_top), (xe - d * 0.08, q, z_top), h=rail_h)
        for yy in (ya - 0.06, yb + 0.06):
            x_far, z_far = xe + d * (n - 1) * tread, z_top - (n - 1) / n * (z_top - z_bed)
            railing(C, (xe, yy, z_top), (x_far, yy, z_far), h=rail_h, col=False)
            # 기운 난간을 따르는 COL (예전 상자는 낮은 쪽 끝에서 손잡이보다 0.86 m 높았다)
            C.ccol([(x, y, z) for (x, ztop) in ((xe, z_top + rail_h + 0.05), (x_far, z_far + rail_h + 0.05))
                    for y in (yy - 0.04, yy + 0.04) for z in (z_bed, ztop)])


def railing(C, p0, p1, *, h=1.0, post=1.2, key="steel", col=True, mid=True):
    """난간: 기둥 + 손잡이 + 중간 가로대. p0, p1 = 바닥 높이 점 (기울어도 된다)."""
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = d.length
    if L < 0.05:
        return
    n = max(1, int(L / post))
    for k in range(n + 1):
        p = P0 + d * (k / n)
        C.beam(key, tuple(p), tuple(p + Vector((0, 0, h))), 0.06, 0.06, kind="detail")
    C.cyl(key, tuple(P0 + Vector((0, 0, h))), tuple(P1 + Vector((0, 0, h))), 0.035, segs=6, kind="detail")
    if mid:
        C.beam(key, tuple(P0 + Vector((0, 0, h * 0.5))), tuple(P1 + Vector((0, 0, h * 0.5))), 0.03, 0.03, kind="detail")
    if col and abs(d.z) < 1e-3:
        C.col(min(P0.x, P1.x) - 0.04, max(P0.x, P1.x) + 0.04, min(P0.y, P1.y) - 0.04, max(P0.y, P1.y) + 0.04,
              P0.z, P0.z + h + 0.1)


def stair_flight(C, axis, w0, w1, s_low, dir_up, z_lo, z_hi, n, *, tread=0.3, key="concrete_d", top_key="concrete",
                 z_floor=None, nosing=True, col=True):
    """직선 계단 (꽉 찬 단). axis='x'면 x를 따라 오른다(폭 = y w0..w1), 'y'면 y를 따라(폭 = x w0..w1).
    s_low = 첫 단(아래) 앞 모서리, dir_up = ±1, n = 단 수(높이 (z_hi-z_lo)/n). 디딤판 n-1개 다음부터 z_hi 바닥이 이어진다.
    COL은 디딤판 앞 모서리를 잇는 쐐기 (첫 단 한 칸 앞 바닥에서 시작). 반환: 위 바닥이 시작하는 좌표."""
    r = (z_hi - z_lo) / n
    base = z_lo if z_floor is None else z_floor
    for k in range(1, n):
        sa = s_low + dir_up * (k - 1) * tread
        sb = s_low + dir_up * k * tread
        zt = z_lo + k * r
        lo, hi = sorted((sa, sb))
        if axis == "x":
            C.box(key, lo, hi, w0, w1, base, zt - 0.04)
            C.box(top_key, lo, hi, w0, w1, zt - 0.04, zt, kind="detail")
            if nosing:
                C.strip("hazard", (sa + dir_up * 0.05, w0 + 0.05, zt), (sa + dir_up * 0.05, w1 - 0.05, zt), 0.06,
                        lift=0.004)
        else:
            C.box(key, w0, w1, lo, hi, base, zt - 0.04)
            C.box(top_key, w0, w1, lo, hi, zt - 0.04, zt, kind="detail")
            if nosing:
                C.strip("hazard", (w0 + 0.05, sa + dir_up * 0.05, zt), (w1 - 0.05, sa + dir_up * 0.05, zt), 0.06,
                        lift=0.004)
    s_top = s_low + dir_up * (n - 1) * tread
    if col:
        s_start = s_low - dir_up * tread
        a, b = sorted((s_start, s_top))
        rise = ("+" if dir_up > 0 else "-") + axis
        if axis == "x":
            col_wedge(C, a, b, w0, w1, z_lo, z_hi, rise, z_floor=min(base, z_lo) - 0.2)
        else:
            col_wedge(C, w0, w1, a, b, z_lo, z_hi, rise, z_floor=min(base, z_lo) - 0.2)
    return s_top


def round_pillar(C, x, y, *, z0, z1, r=0.38, logo_n=None, ls=None):
    """승강장 둥근 기둥: 크림 타일 몸통 + 남색 걸레받이·표지 띠 + 금색 고리 + 시안 띠 + 나팔 기둥머리.
    ls(LampSet)가 있으면 ±Y 두 면에 비상등을 단다."""
    C.cyl("tile", (x, y, z0), (x, y, z1), r, segs=16, cap=False)
    C.cyl("navy", (x, y, z0), (x, y, z0 + 0.14), r + 0.03, segs=16)
    C.cyl("navy", (x, y, z0 + 1.15), (x, y, z0 + 1.7), r + 0.015, segs=16, cap=False)
    C.cyl("gold", (x, y, z0 + 1.7), (x, y, z0 + 1.76), r + 0.035, segs=16, cap=False)
    C.cyl("glow", (x, y, z1 - 0.62), (x, y, z1 - 0.56), r + 0.02, segs=16, cap=False)
    C.cyl("navy", (x, y, z1 - 0.32), (x, y, z1), r + 0.04, r2=r + 0.32, segs=16)
    C.col(x - r, x + r, y - r, y + r, z0, z1)
    for s in (-1, 1):
        N = (0, s, 0)
        p = (x, y + s * (r + 0.015), z0 + 1.43)
        if logo_n:
            C.text("white", logo_n, 0.16, p, N, lift=0.012)
        if ls is not None:
            emerg_lamp(C, ls, (x, y + s * (r + 0.02), z0 + 2.35), N, w=0.22, h=0.1, halo=0.0)


def name_board(C, center, normal, ko, en, *, w=3.4, h=1.0, line="W", left=None, right=None, logo=True):
    """역 이름판 (헌글: 한글 + 로마자). 노선 원판(서부선 주황 W) 왼쪽, 엘프 로고 원판 오른쪽, 아래 양옆 방면 글자."""
    c, N = Vector(center), Vector(normal).normalized()
    R, U, _ = mk.frame(N)
    C.plate("gold", hw.rrect(w + 0.1, h + 0.1, 0.22, 3), tuple(c), tuple(N), 0.039, kind="detail", back=0.004)
    C.plate("navy", hw.rrect(w, h, 0.18, 3), tuple(c), tuple(N), 0.06, kind="detail")
    f = c + N * 0.06
    C.text("white", ko, h * 0.34, tuple(f + U * (h * 0.12)), tuple(N), lift=0.01)
    C.text("glow", en, h * 0.11, tuple(f - U * (h * 0.2)), tuple(N), lift=0.01)
    lc = f - R * (w / 2 - 0.42)
    C.decal("line_w", hw.circle(0.27, 20), tuple(lc + U * 0.08), tuple(N), lift=0.012)
    C.text("white", line, 0.26, tuple(lc + U * 0.08), tuple(N), lift=0.02)
    if logo:
        C.logo(tuple(f + R * (w / 2 - 0.42) + U * 0.08), 0.42, tuple(N), key="gold", disc="navy_l", lift=0.012)
    if left:
        C.text("white", left, 0.1, tuple(f - U * (h * 0.38) - R * (w * 0.28)), tuple(N), lift=0.01)
    if right:
        C.text("white", right, 0.1, tuple(f - U * (h * 0.38) + R * (w * 0.28)), tuple(N), lift=0.01)


def line_map(C, center, normal, stations, here, *, w=5.2, h=0.62):
    """노선도 띠: 남색 판 + 주황 노선 + 역 점(현재 역은 금색 고리) + 역 이름."""
    c, N = Vector(center), Vector(normal).normalized()
    R, U, _ = mk.frame(N)
    C.plate("navy", hw.rrect(w, h, 0.12, 2), tuple(c), tuple(N), 0.04, kind="detail")
    f = c + N * 0.04
    m = len(stations)
    C.strip("line_w", tuple(f - R * (w / 2 - 0.4) + U * 0.1), tuple(f + R * (w / 2 - 0.4) + U * 0.1), 0.07, tuple(N),
            lift=0.008)
    for i, nm in enumerate(stations):
        u = -w / 2 + 0.4 + (w - 0.8) * i / max(1, m - 1)
        p = f + R * u + U * 0.1
        if nm == here:
            C.ring("gold", hw.circle(0.11, 14), hw.circle(0.07, 14), tuple(p), tuple(N), lift=0.015)   # 주황 선 + 7 mm
        C.decal("white", hw.circle(0.06, 12), tuple(p), tuple(N), lift=0.015)
        C.text("gold" if nm == here else "white", nm, 0.1, tuple(p - U * 0.2), tuple(N), lift=0.01)


def hanging_sign(C, center, w, h, front, back, *, axis="x", z_ceil, key="navy"):
    """천장에 매단 양면 표지. axis='x'면 판이 ±X를 본다. front/back = [(글자, 크기, 키, v)]."""
    c = Vector(center)
    N = Vector((1, 0, 0)) if axis == "x" else Vector((0, 1, 0))
    R, U, _ = mk.frame(N)
    C.plate(key, hw.rrect(w, h, 0.1, 2), tuple(c), tuple(N), 0.08, back=0.04, kind="detail")
    for s in (-1, 1):
        rod = c + R * (s * (w / 2 - 0.25)) + U * (h / 2)
        C.cyl("metal", tuple(rod), (rod.x, rod.y, z_ceil), 0.025, segs=6, kind="detail")
    for sgn, lines in ((1, front), (-1, back)):
        f = c + N * (0.04 * sgn)
        for (s, size, k, v) in lines:
            C.text(k, s, size, tuple(f + U * v), tuple(N * sgn), lift=0.008)


def floodgate(C, x, y0, y1, z0, z1, side):
    """터널 입구 방수문 (닫힘): 강철 판 + 리브 + 노랑 띠 + 글자. side = 문 앞면이 보는 쪽(+1이면 +X)."""
    N = Vector((side, 0, 0))
    xf = x + side * 0.02
    C.box("steel_d", min(x, xf), max(x, xf) + 0.0001, y0, y1, z0, z1, kind="detail")
    C.col(min(x, x + side * 0.13), max(x, x + side * 0.13), y0, y1, z0, z1)   # 문판 + 리브 (벽 COL 앞 0.13 m)
    yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
    for k in range(1, 4):
        z = z0 + (z1 - z0) * k / 4
        C.beam("metal", (xf + side * 0.04, y0 + 0.1, z), (xf + side * 0.04, y1 - 0.1, z), 0.08, 0.08, kind="detail")
    C.strip("hazard", (xf + side * 0.081, y0 + 0.1, z0 + 0.3), (xf + side * 0.081, y1 - 0.1, z0 + 0.3), 0.3,
            tuple(N), lift=0.004)
    C.text("white", "방수문 · FLOOD GATE", 0.16, (xf + side * 0.09, yc, zc + 0.15), tuple(N), lift=0.004)


# ================================================================== track · tunnel

def _offsets(P):
    """꺾은선 점마다 옆 방향(평균 법선)."""
    n = len(P)
    out = []
    for i in range(n):
        a = P[max(0, i - 1)]
        b = P[min(n - 1, i + 1)]
        d = (b - a)
        d.z = 0
        d.normalize()
        out.append(Vector((-d.y, d.x, 0)))
    return out


def track(C, pts, z_bed, *, gauge=1.2, pitch=1.0, third=0, sleepers=True):
    """궤도: 콘크리트 침목 + 레일 2줄 (+ third=±1이면 그쪽에 제3궤조와 노랑 덮개). pts = XY 중심선(촘촘히).
    충돌 없음 (높이 0.21 m: 궤도 바닥 COL 위를 걷는다)."""
    P = [Vector((x, y, 0.0)) for x, y in pts]
    S = _offsets(P)
    zr = z_bed + 0.155
    for i in range(len(P) - 1):
        for s in (-1, 1):
            a = P[i] + S[i] * (s * gauge / 2) + Vector((0, 0, zr))
            b = P[i + 1] + S[i + 1] * (s * gauge / 2) + Vector((0, 0, zr))
            C.beam("rail", tuple(a), tuple(b), 0.07, 0.11, kind="detail")
        if third:
            # 덮개 윗면 z_bed + 0.245: 대피 보도 윗면(궤도 + 0.25)보다 5 mm 낮아 굽은 구간이 보도 밑을 지나도 겹치지 않는다
            a = P[i] + S[i] * (third * (gauge / 2 + 0.55)) + Vector((0, 0, z_bed + 0.215))
            b = P[i + 1] + S[i + 1] * (third * (gauge / 2 + 0.55)) + Vector((0, 0, z_bed + 0.215))
            C.beam("hazard", tuple(a), tuple(b), 0.16, 0.06, kind="detail")
    if sleepers:
        # 길이를 따라 pitch마다 침목
        acc = 0.0
        for i in range(len(P) - 1):
            seg = (P[i + 1] - P[i]).length
            while acc <= seg:
                t = acc / seg if seg > 0 else 0
                c = P[i].lerp(P[i + 1], t) + Vector((0, 0, z_bed + 0.05))
                n = S[i].lerp(S[i + 1], t).normalized()
                C.beam("sleeper", tuple(c - n * (gauge / 2 + 0.38)), tuple(c + n * (gauge / 2 + 0.38)), 0.24, 0.1,
                       kind="detail")
                acc += pitch
            acc -= seg
    if third:
        # 절연 받침 (4 m마다)
        acc = 0.0
        for i in range(len(P) - 1):
            seg = (P[i + 1] - P[i]).length
            while acc <= seg:
                t = acc / seg if seg > 0 else 0
                c = P[i].lerp(P[i + 1], t) + S[i] * (third * (gauge / 2 + 0.55))
                C.box("white", c.x - 0.05, c.x + 0.05, c.y - 0.05, c.y + 0.05, z_bed, z_bed + 0.19, kind="detail")
                acc += 4.0
            acc -= seg


def s_curve(xa, xb, ya, yb, step=1.0):
    """xa→xb 동안 ya에서 yb로 부드럽게 옮겨 가는 중심선 점."""
    n = max(2, int(abs(xb - xa) / step))
    out = []
    for i in range(n + 1):
        t = i / n
        k = t * t * (3 - 2 * t)
        out.append((xa + (xb - xa) * t, ya + (yb - ya) * k))
    return out


def tunnel(C, x0, x1, y0, y1, *, z_bed, z_ceil, t=0.5, walkway=None, pillars=None, openings_n=(), openings_s=(),
           lamp_pitch=8.0, ceil_holes=(), trays=True, ls_red=None, red_pitch=12.0):
    """박스형 복선 터널(개착식): 바닥(+COL), 양 벽(구멍 openings_*), 천장(구멍 ceil_holes), 가운데 기둥 줄 + 천장 보,
    케이블 트레이, 꺼진 터널등, 적색 비상등(ls_red). walkway = (side ±1, 폭, 높이): 그 벽을 따라 올린 대피 보도(+COL).
    pillars = (y, x_from, x_to, pitch, size)."""
    C.box("bed", x0, x1, y0, y1, z_bed - 0.3, z_bed, col=True)
    for s, (ya, yb), ops in ((1, (y1, y1 + t), openings_n), (-1, (y0 - t, y0), openings_s)):
        wall_x(C, "tunnel", x0, x1, ya, yb, z_bed - 0.3, z_ceil + 0.4, ops)
        yf = y1 if s > 0 else y0
        y_in = (yf - 0.03, yf) if s > 0 else (yf, yf + 0.03)
        # 아래 띠: 대피 보도가 있는 구간은 보도 윗면부터 (보도 속으로 내려가면 끝면·문 문턱이 보도 면과 같은 평면에 겹친다)
        segs = [(x0, x1, z_bed)]
        if walkway and (walkway[0] > 0) == (s > 0):
            wa, wb = walkway[3] if len(walkway) > 3 else (x0, x1)
            segs = [(p, q, z) for (p, q, z) in ((x0, wa, z_bed), (wa, wb, z_bed + walkway[2]), (wb, x1, z_bed))
                    if q - p > 1e-6]
        for (p, q, z) in segs:
            wall_x(C, "tunnel_d", p, q, y_in[0], y_in[1], z, z_bed + 1.2, ops, col=False, kind="detail")
        if trays:
            for zz in (z_bed + 2.75, z_bed + 3.15):
                ys = (yf - 0.32, yf) if s > 0 else (yf, yf + 0.32)
                C.box("steel_d", x0, x1, ys[0], ys[1], zz, zz + 0.06, kind="detail")
                C.box("navy_l", x0, x1, ys[0] + 0.04, ys[1] - 0.04, zz + 0.06, zz + 0.14, kind="detail")
            k = x0 + 1.5
            while k < x1:
                ys = (yf - 0.34, yf) if s > 0 else (yf, yf + 0.34)
                C.box("metal", k - 0.03, k + 0.03, ys[0], ys[1], z_bed + 2.6, z_bed + 3.25, kind="detail")
                k += 3.0
        # 꺼진 터널등
        k = x0 + lamp_pitch / 2 + (0 if s > 0 else lamp_pitch / 2)
        while k < x1:
            if not any(a - 0.6 < k < b + 0.6 for (a, b, _, _) in ops):
                N = (0, -s, 0)
                C.plate("navy", hw.rrect(0.7, 0.2, 0.06, 2), (k, yf, z_bed + 3.55), N, 0.06, kind="detail")
                C.decal("lamp_dead", hw.rrect(0.6, 0.12, 0.05, 2), (k, yf - s * 0.06, z_bed + 3.55), N, lift=0.004)
            k += lamp_pitch
        if ls_red is not None:
            k = x0 + red_pitch / 2 + (red_pitch / 2 if s > 0 else 0)
            while k < x1 - 1:
                if not any(a - 0.8 < k < b + 0.8 for (a, b, _, _) in ops):
                    emerg_lamp(C, ls_red, (k, yf, z_bed + 2.35), (0, -s, 0))
                k += red_pitch
    # 천장 (구멍을 피해 조각)
    _ceiling_with_holes(C, "tunnel_d", x0, x1, y0, y1, z_ceil, z_ceil + 0.4, ceil_holes)
    if walkway:
        side, wdt, hh = walkway[:3]
        ya, yb = (y0, y0 + wdt) if side < 0 else (y1 - wdt, y1)
        xa, xb = walkway[3] if len(walkway) > 3 else (x0, x1)
        C.box("tunnel", xa, xb, ya, yb, z_bed, z_bed + hh, col=True)
        ye = yb if side < 0 else ya
        C.strip("hazard", (xa, ye + side * 0.12, z_bed + hh), (xb, ye + side * 0.12, z_bed + hh), 0.1, lift=0.006)
        # 대피 유도 시안 띠 (보도 가장자리 옆면)
        C.strip("glow", (xa, ye, z_bed + hh - 0.08), (xb, ye, z_bed + hh - 0.08), 0.04, (0, -side, 0), lift=0.006)
    if pillars:
        py, pa, pb, pitch, size = pillars
        ceil_box(C, "tunnel_d", x0, x1, py - 0.35, py + 0.35, z_ceil - 0.45, z_ceil, kind="detail", col=False)
        k = pa
        while k <= pb + 1e-6:
            h_ = size / 2
            C.box("tunnel", k - h_, k + h_, py - h_, py + h_, z_bed, z_ceil - 0.45, col=True)
            for s in (-1, 1):
                # 노랑 띠를 검정 줄 위·아래 두 조각으로 나눠 검정 줄과 한 평면에 나란히 (겹쳐 얹으면 멀리서 깜빡인다)
                for (zc, hh_) in ((z_bed + 0.395, 0.19), (z_bed + 0.705, 0.19)):
                    C.rect("hazard", (k, py + s * h_, zc), (0, s, 0), size, hh_, lift=0.006)
                C.rect("dark", (k, py + s * h_, z_bed + 0.55), (0, s, 0), size, 0.12, lift=0.006)
                C.rect("hazard", (k + s * h_, py, z_bed + 0.55), (s, 0, 0), size, 0.5, lift=0.006)
            C.text("white", f"{k:.0f}", 0.16, (k - h_, py, z_bed + 1.6), (-1, 0, 0), lift=0.01)
            k += pitch


def _ceiling_with_holes(C, key, x0, x1, y0, y1, z0, z1, holes):
    if not holes:
        ceil_box(C, key, x0, x1, y0, y1, z0, z1)
        return
    (ha, hb, hc, hd) = holes[0]
    ceil_box(C, key, x0, ha, y0, y1, z0, z1)
    ceil_box(C, key, hb, x1, y0, y1, z0, z1)
    ceil_box(C, key, ha, hb, y0, hc, z0, z1)
    ceil_box(C, key, ha, hb, hd, y1, z0, z1)


def signal_post(C, x, y, z, face, *, lit="r"):
    """궤도 신호기: 기둥 + 남색 머리 + 렌즈 3개(맨 위 적색만 비상 전원으로 켜짐). face = 신호가 보이는 쪽 (x,y) 방향."""
    F = Vector((face[0], face[1], 0)).normalized()
    C.cyl("dark", (x, y, z), (x, y, z + 2.0), 0.06, segs=8, kind="detail")
    hc = Vector((x, y, z + 2.25))
    C.beam("navy", tuple(hc - Vector((0, 0, 0.42))), tuple(hc + Vector((0, 0, 0.42))), 0.32, 0.22, kind="detail",
           up=tuple(F))
    for i, k in enumerate(("sig_r", "dark", "dark")):
        p = hc + F * 0.12 + Vector((0, 0, 0.24 - i * 0.24))
        C.decal(k if (i == 0 and lit == "r") else "dark", hw.circle(0.085, 12), tuple(p), tuple(F), lift=0.008)
        C.ring("navy_l", hw.circle(0.12, 12), hw.circle(0.09, 12), tuple(p), tuple(F), lift=0.006)
    C.col(x - 0.07, x + 0.07, y - 0.07, y + 0.07, z, z + 2.0)   # 기둥 (머리는 키보다 위)


def km_plate(C, pos, normal, text):
    """거리표 (흰 판 + 남색 글자)."""
    C.plate("white", hw.rrect(0.5, 0.22, 0.05, 2), pos, normal, 0.02, kind="detail")
    C.text("navy", text, 0.11, tuple(Vector(pos) + Vector(normal) * 0.02), normal, lift=0.006)


def cave_in(C, x0, x1, y0, y1, *, z_bed, z_ceil, hole, seed=3, shaft_h=6.0, tracks=(2.9, -2.9), ceil_t=0.4):
    """무너진 터널 끝 [오리지널: R41 포격]: 잔해 더미(잔해를 감싸는 볼록 COL, 뒤는 천장까지 막힘), 기운 슬래브, 휜 레일,
    늘어진 케이블, 천장 구멍 위 수직 갱도 + 지상 햇빛판 + 빛기둥. hole = (xa, xb, ya, yb) 천장 구멍.
    ceil_t = 터널 천장 판 두께(tunnel()과 같게): 갱도 벽은 그 위에서 시작한다(판 속으로 내려오면 구멍 옆면·밑면이 겹친다)."""
    rng = random.Random(seed)
    span = x1 - x0
    blobs, slabs = [], []          # COL을 잔해 모양에 맞추려고 기억해 둔다 (난수 순서는 그대로)
    for i in range(46):
        u = rng.random() ** 0.7
        x = x0 + u * span
        y = rng.uniform(y0 + 0.3, y1 - 0.3)
        top = z_bed + 0.3 + u * (z_ceil - z_bed) * 1.05
        r = rng.uniform(0.35, 0.9) * (0.7 + 0.6 * u)
        c = (x, y, min(top, z_ceil + 0.3) - r * 0.4)
        sc = (rng.uniform(0.9, 1.5), rng.uniform(0.8, 1.3), rng.uniform(0.5, 0.8))
        rz = rng.uniform(0, 6.28)
        if x < x0 + 2.0:
            # 더미 앞쪽(쐐기가 바닥에서 시작하는 x0 + 2 앞) 덩이는 바닥에 얹는다 (2026-11-03 floatcheck: 서로만 붙은 덩이
            # 넷이 궤도 바닥 위 0.17~0.42 m에 떠 있었다). 난수 순서는 그대로
            c = (c[0], c[1], min(c[2], z_bed - 0.03 + r * sc[2]))
        C.blob("rubble" if i % 3 else "tunnel_d", c, r, sc, segs=7, rings=4, rot_z=rz)
        blobs.append((c, r, sc, rz))
    for i in range(5):
        cx = x0 + rng.uniform(0.3, 0.8) * span
        cy = rng.uniform(y0 + 1, y1 - 1)
        c = (cx, cy, z_bed + 1.0 + rng.uniform(0, 1.5))
        size = (rng.uniform(1.6, 3.0), rng.uniform(1.0, 2.2), 0.3)
        rot = (rng.uniform(-35, 35), rng.uniform(15, 40), rng.uniform(-40, 40))
        C.rbox("tunnel_d", c, size, rot=rot)
        Mx = (Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
              @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        slabs.append([Mx @ Vector((sx * size[0] / 2, sy * size[1] / 2, sz * size[2] / 2))
                      for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    for ty in tracks:
        C.beam("rail", (x0 - 0.5, ty + 0.6, z_bed + 0.2), (x0 + 2.0, ty + 1.1, z_bed + 1.1), 0.07, 0.11,
               kind="detail")
    for i in range(6):
        cx = rng.uniform(hole[0], hole[1])
        cy = rng.uniform(hole[2], hole[3])
        C.cyl("dark", (cx, cy, z_ceil), (cx + rng.uniform(-0.6, 0.6), cy + rng.uniform(-0.5, 0.5),
                                        z_ceil - rng.uniform(0.8, 2.0)), 0.025, segs=5, kind="detail")
    # 수직 갱도 + 햇빛
    ha, hb, hc, hd = hole
    zt = z_ceil + shaft_h
    for (a, b, c, d) in ((ha - 0.5, ha, hc - 0.5, hd + 0.5), (hb, hb + 0.5, hc - 0.5, hd + 0.5),
                         (ha, hb, hc - 0.5, hc), (ha, hb, hd, hd + 0.5)):
        ceil_box(C, "soil_d", a, b, c, d, z_ceil + ceil_t, zt, col=False)
    ceil_box(C, "day", ha, hb, hc, hd, zt, zt + 0.1, col=False)
    # 빛기둥(반투명, 양면)은 햇빛판 1 cm 아래에서 멈춘다: 윗면이 햇빛판 밑면과 같은 평면이면 번갈아 비친다
    C.box("daybeam", ha + 0.3, hb - 0.3, hc + 0.3, hd - 0.3, z_bed + 0.6, zt - 0.01)
    # COL: 잔해 덩이·슬래브마다 그 꼭짓점의 볼록 껍질 하나 (보이는 모양 그대로) + 더미 속 가파른 쐐기(x0 + 2에서 바닥,
    # x0 + 4.5에서 천장)와 그 뒤 천장까지 막힌 상자. 뒤쪽 덩이는 공중에 얹혀 밑이 비어 쐐기 없이는 그 밑으로 기어들었다.
    # 천장 구멍(x0 + 1..5) 아래 덩이 윗면은 바닥 + 3.5 m 아래라 올라서서 뛰어도 구멍 위 갱도(충돌 없음)나
    # 터널 천장 윗면(바닥 + 4.8 m)에 닿지 않는다. 예전 낮은 단 COL(0.25 / 0.5 m)은 앞쪽 잔해 속을 걸어 지나가게 했다
    zb = z_bed - 0.05
    xw, xb = x0 + 2.0, x0 + 4.5
    for (c, r, sc, rz) in blobs:
        if c[0] - r * max(sc[0], sc[1]) >= xb:
            continue
        b = bmesh.new()
        mk._bm_blob(b, c, r, sc, segs=7, rings=4, rot_z=rz)
        C.ccol([(v.co.x, v.co.y, max(v.co.z, zb)) for v in b.verts])
        b.free()
    for corners in slabs:
        if min(v.x for v in corners) < xb:
            C.ccol([(v.x, v.y, max(v.z, zb)) for v in corners])
    C.ccol([(x, y, z) for y in (y0, y1) for (x, z) in ((xw, zb), (xb, zb), (xb, z_ceil + 0.4))])
    C.col(xb, x1, y0, y1, z_bed, z_ceil + 0.4)
    # 휜 레일: 발목(0.35 m)보다 높은 쪽만 레일 자체를 감싼다 (낮은 끝은 걸려 넘어지는 높이라 그냥 둔다)
    for ty in tracks:
        p0, p1 = Vector((x0 - 0.5, ty + 0.6, z_bed + 0.2)), Vector((x0 + 2.0, ty + 1.1, z_bed + 1.1))
        a = p0.lerp(p1, (0.35 - 0.2) / 0.9)
        n = Vector((-(p1 - p0).y, (p1 - p0).x, 0)).normalized() * 0.05
        C.ccol([(q.x, q.y, q.z + dz) for p in (a, p1) for q in (p - n, p + n) for dz in (-0.07, 0.07)])


# ================================================================== subway car

def _minus(a, b, gaps):
    """구간 [a, b]에서 gaps [(p, q)]를 뺀 조각들."""
    segs = [(a, b)]
    for (p, q) in gaps:
        nxt = []
        for (u, v) in segs:
            if q <= u or p >= v:
                nxt.append((u, v))
                continue
            if p > u:
                nxt.append((u, p))
            if q < v:
                nxt.append((q, v))
        segs = nxt
    return [(u, v) for (u, v) in segs if v - u > 0.05]


# 전동차 옆면 장식 층 (몸체 면에서 뜬 거리, m). 모두 같은 편향 등급(_fine)이라 겹치는 층 사이를 7 mm씩 띄운다:
# 기본 깊이 버퍼(24비트, 근평면 3 cm)에서 7 mm는 약 60 m까지 갈린다(승강장 끝에서 반대쪽 끝 칸까지 약 45 m).
CAR_LAYER = {"band": 0.010, "win": 0.017, "door": 0.024, "door_win": 0.031, "disc": 0.038, "logo": 0.045}


def _car_side_decals(C, xa, xb, yc, zf, s, doors, *, open_doors=(), num=None, logo=True):
    """옆면 장식: 창 띠, 창, 문, 서부선 주황 띠, 시안 띠, 차량 번호. s = 옆(±1), 면 y = yc + s*CAR_W/2.
    열린 문(open_doors) 자리는 띠를 끊는다. 층은 CAR_LAYER (띠·주황·시안 → 창·번호 → 문 → 문 창·가운데 틈 → 원판 → 로고)."""
    Ly = CAR_LAYER
    yf = yc + s * CAR_W / 2
    N = (0, s, 0)
    L = xb - xa
    xc = (xa + xb) / 2
    gaps = [(doors[j] - DOOR_W / 2 - 0.02, doors[j] + DOOR_W / 2 + 0.02) for j in open_doors]
    if not gaps:
        C.decal("navy", hw.stadium(L - 1.0, 0.95, 4), (xc, yf, zf + 1.48), N, lift=Ly["band"])
    else:
        for (u, v) in _minus(xa + 0.5, xb - 0.5, gaps):
            C.rect("navy", ((u + v) / 2, yf, zf + 1.48), N, v - u, 0.95, lift=Ly["band"])
    # 창 (문 사이)
    edges = [xa + 0.5] + sum(([d - DOOR_W / 2 - 0.25, d + DOOR_W / 2 + 0.25] for d in doors), []) + [xb - 0.5]
    for i in range(0, len(edges), 2):
        a, b = edges[i], edges[i + 1]
        if b - a < 0.8:
            continue
        nwin = max(1, int((b - a) / 1.6))
        ww = (b - a) / nwin
        for k in range(nwin):
            C.rect("glass_d", (a + ww * (k + 0.5), yf, zf + 1.5), N, ww - 0.22, 0.72, lift=Ly["win"])
    for j, d in enumerate(doors):
        if j in open_doors:
            continue
        C.rect("navy_l", (d, yf, zf + DOOR_H / 2), N, DOOR_W, DOOR_H, lift=Ly["door"])
        for k in (-1, 1):
            C.rect("glass_d", (d + k * DOOR_W / 4, yf, zf + 1.3), N, DOOR_W / 2 - 0.2, 0.62, lift=Ly["door_win"])
        C.rect("dark", (d, yf, zf + DOOR_H / 2), N, 0.03, DOOR_H, lift=Ly["door_win"])
    for (u, v) in _minus(xa + 0.3, xb - 0.3, gaps):
        C.strip("line_w", (u, yf, zf + 0.42), (v, yf, zf + 0.42), 0.17, N, lift=Ly["band"])
        C.strip("glow", (u, yf, zf + 0.24), (v, yf, zf + 0.24), 0.04, N, lift=Ly["band"])
    if num:
        C.text("navy", num, 0.13, (xa + 0.9 if s < 0 else xb - 0.9, yf, zf + 2.05), N, lift=Ly["win"])
    # 로고는 가운데 문 위(문판·가운데 틈 앞)에 쌓는다: 남색 원판 → 금색 로고. logo(lift=lf)는 로고를 lf·1.6에 둔다.
    # 가운데 문이 열려 있으면 그 자리에 벽이 없어 그리지 않는다
    mid = min(range(len(doors)), key=lambda j: abs(doors[j] - xc))
    if logo and mid not in open_doors:
        C.decal("navy", hw.circle(0.3 * 0.68, 32), (xc, yf, zf + 0.75), N, lift=Ly["disc"])
        C.logo((xc, yf, zf + 0.75), 0.3, N, key="gold", lift=Ly["logo"] / 1.6)


def _car_end_decals(C, x, yc, zf, d, cab, *, door_open=False):
    """끝면 장식. d = 끝면이 보는 쪽(±1 X). cab이면 앞창·전조등·행선 표시."""
    N = (d, 0, 0)
    if cab:
        if door_open:
            for s in (-1, 1):
                C.decal("glass_d", hw.rrect(0.6, 0.85, 0.2, 3), (x, yc + s * 0.84, zf + 1.5), N, lift=0.02)
                C.rect("line_w", (x, yc + s * 0.85, zf + 0.85), N, 0.62, 0.12, lift=0.02)
        else:
            C.decal("glass_d", hw.rrect(1.95, 0.85, 0.25, 3), (x, yc, zf + 1.6), N, lift=0.02)
            C.rect("line_w", (x, yc, zf + 0.85), N, 2.2, 0.12, lift=0.02)
        for s in (-1, 1):
            C.decal("lamp_dead", hw.circle(0.1, 12), (x, yc + s * 0.82, zf + 0.5), N, lift=0.024)
        C.rect("dark", (x, yc, zf + 2.27), N, 1.2, 0.22, lift=0.02)
        C.text("line_w", "서부선 · W", 0.12, (x, yc, zf + 2.27), N, lift=0.027)
    if not door_open:
        C.decal("navy_l", hw.rrect(0.9, 1.8, 0.1, 2), (x, yc, zf + 0.92), N, lift=0.027)   # 앞창·주황 띠(0.02)보다 7 mm 앞


def _bogies(C, xa, xb, yc, zf, z_bed):
    for xb_ in (xa + 2.0, xb - 2.0):
        C.box("dark", xb_ - 1.0, xb_ + 1.0, yc - 0.95, yc + 0.95, z_bed + 0.35, zf - 0.35, kind="detail")
        for dx in (-0.6, 0.6):
            for s in (-1, 1):
                p = (xb_ + dx, yc + s * 0.6, z_bed + 0.49)
                C.cyl("metal", (p[0], p[1] - 0.05, p[2]), (p[0], p[1] + 0.05, p[2]), 0.28, segs=10, kind="detail")
    if xb - xa > 6:
        C.box("dark", xa + 3.3, xb - 3.3, yc - 0.9, yc + 0.9, z_bed + 0.5, zf - 0.35, kind="detail")


def subway_car(C, xa, xb, yc, zf, z_bed, *, walk=False, cab=(False, False), open_side=0, open_doors=(),
               num="W-2041", lamps=None, seed=0, end_doors=(True, True), plain_side=0):
    """전동차 한 칸 (X 방향, 엘프 체격 폭 2.5 m, 바닥 zf = 승강장 높이). cab = (xa 쪽, xb 쪽) 운전실 끝.
    walk=False: 닫힌 껍데기(둥근 단면) + 통짜 COL. walk=True: 들어가 걸을 수 있는 실내(좌석, 손잡이, 꺼진 조명,
    비상등 lamps), 끝벽 비상문 구멍(end_doors), open_side(±1) 쪽 open_doors(문 번호 0..2) 열림. COL은 바닥 아래
    궤도까지 꽉 차서 차 밑으로 기어들 수 없다."""
    L = xb - xa
    hw_ = CAR_W / 2
    doors = [xa + L * f for f in (0.2, 0.5, 0.8)]
    _bogies(C, xa, xb, yc, zf, z_bed)
    if not walk:
        C.plate("car", hw.rrect(CAR_W, CAR_H + 0.35, 0.42, 3), (xa, yc, zf + (CAR_H - 0.35) / 2), (1, 0, 0), L)
        for s in (-1, 1):
            plain = s == plain_side
            _car_side_decals(C, xa, xb, yc, zf, s, doors, num=None if plain else num, logo=not plain)
        for x, d, cb_ in ((xa, -1, cab[0]), (xb, 1, cab[1])):
            _car_end_decals(C, x, yc, zf, d, cb_)
        C.box("steel", xa + 2.5, xa + 4.3, yc - 0.6, yc + 0.6, zf + CAR_H - 0.05, zf + CAR_H + 0.22, kind="detail")
        C.box("steel", xb - 4.3, xb - 2.5, yc - 0.6, yc + 0.6, zf + CAR_H - 0.05, zf + CAR_H + 0.22, kind="detail")
        C.col(xa, xb, yc - hw_, yc + hw_, z_bed, zf + CAR_H)
        return
    # ---- 걸어 들어가는 칸
    tw = 0.08
    # 바닥은 끝벽 안쪽부터 (끝벽 비상문 문턱 윗면·끝면과 같은 평면에 겹치지 않게)
    C.box("car_floor", xa + tw, xb - tw, yc - hw_ + tw, yc + hw_ - tw, zf - 0.1, zf)
    C.strip("line_w", (xa + 0.2, yc, zf), (xb - 0.2, yc, zf), 0.08, lift=0.006)
    C.col(xa, xb, yc - hw_, yc + hw_, z_bed, zf)
    for s in (-1, 1):
        ya, yb = sorted((yc + s * hw_, yc + s * (hw_ - tw)))
        ops = [(doors[j] - DOOR_W / 2, doors[j] + DOOR_W / 2, zf, zf + DOOR_H) for j in open_doors] if s == open_side else []
        wall_x(C, "car", xa, xb, ya, yb, zf - 0.35, zf + CAR_WALL, ops)
        _car_side_decals(C, xa, xb, yc, zf, s, doors, open_doors=open_doors if s == open_side else (), num=num)
        # 실내 면: 창, 문 안쪽
        yi = yc + s * (hw_ - tw)
        Ni = (0, -s, 0)
        wall_x(C, "car_in", xa + tw, xb - tw, min(yi, yi - s * 0.01), max(yi, yi - s * 0.01), zf, zf + CAR_WALL, ops,
               col=False, kind="detail")
        for j, d in enumerate(doors):
            if s == open_side and j in open_doors:
                C.rect("hazard", (d, yi - s * 0.012, zf + DOOR_H + 0.05), Ni, DOOR_W, 0.06, lift=0.004)
                continue
            C.rect("steel", (d, yi - s * 0.01, zf + DOOR_H / 2), Ni, DOOR_W, DOOR_H, lift=0.006)
            C.rect("glass_d", (d, yi - s * 0.01, zf + 1.3), Ni, DOOR_W - 0.3, 0.62, lift=0.013)   # 문판 + 7 mm
        edges = [xa + 0.5] + sum(([d - DOOR_W / 2 - 0.25, d + DOOR_W / 2 + 0.25] for d in doors), []) + [xb - 0.5]
        for i in range(0, len(edges), 2):
            a, b = edges[i], edges[i + 1]
            nwin = max(1, int((b - a) / 1.6))
            ww = (b - a) / nwin
            for k in range(nwin):
                C.rect("glass_d", (a + ww * (k + 0.5), yi - s * 0.01, zf + 1.5), Ni, ww - 0.22, 0.72, lift=0.008)
            # 좌석 (엘프 좌판 0.32 m) + 등받이 + COL
            sa, sb = a + 0.1, b - 0.1
            y_in = yi - s * 0.44
            y0_, y1_ = sorted((yi, y_in))
            C.box("steel_d", sa, sb, y0_, y1_, zf, zf + 0.2, kind="detail")
            C.box("seat", sa, sb, y0_, y1_, zf + 0.2, zf + 0.32, kind="detail")
            yb0, yb1 = sorted((yi, yi - s * 0.1))
            C.box("seat", sa, sb, yb0, yb1, zf + 0.32, zf + 0.82, kind="detail")
            C.col(sa, sb, y0_, y1_, zf, zf + 0.34)
            C.col(sa, sb, yb0, yb1, zf, zf + 0.82)    # 등받이 (좌판에 올라서면 몸이 등받이에 묻혔다)
            # 손잡이 가로봉 + 세로봉
            yr = yc + s * (hw_ - 0.62)
            C.cyl("steel", (sa, yr, zf + 1.72), (sb, yr, zf + 1.72), 0.02, segs=6, kind="detail")
            for xx in (sa, sb):
                C.cyl("steel", (xx, yi - s * 0.46, zf), (xx, yi - s * 0.46, zf + 2.2), 0.022, segs=6, kind="detail")
    # 지붕 곡면 (바깥 + 안 천장)
    n = 10
    outer = []
    for i in range(n + 1):
        u = -hw_ + CAR_W * i / n
        outer.append((u, zf + CAR_WALL + (CAR_H - CAR_WALL) * math.sqrt(max(0.0, 1 - (u / hw_) ** 2))))
    inner = [(u, z - 0.1) for (u, z) in reversed(outer)]
    band = outer + inner
    C.plate("car", [(u, z) for (u, z) in band], (xa, yc, 0.0), (1, 0, 0), L)
    # 지붕 COL: 둥근 안쪽 천장(옆벽 위 2.1 → 가운데 2.5)을 따라 가운데 띠를 꺼진 조명(2.32) 높이까지 올린다.
    # 통짜 판(2.2)은 좌판 위에서 보이지 않는 천장이 됐다
    C.col(xa, xb, yc - 1.0, yc + 1.0, zf + CAR_WALL + 0.12, zf + CAR_H)
    for s in (-1, 1):
        ya, yb = sorted((yc + s * 1.0, yc + s * hw_))
        C.col(xa, xb, ya, yb, zf + CAR_WALL, zf + CAR_H)
    # 실내 천장 조명(꺼짐) 두 줄 + 비상등
    for s in (-1, 1):
        C.box("lamp_dead", xa + 0.6, xb - 0.6, yc + s * 0.5 - 0.09, yc + s * 0.5 + 0.09, zf + CAR_WALL + 0.12,
              zf + CAR_WALL + 0.16, kind="detail")
    if lamps is not None:
        for f in (0.35, 0.65):
            ceiling_lamp(C, lamps, (xa + L * f, yc, zf + CAR_H - 0.1), r=0.1)
    # 끝벽 (비상문 구멍) + 지붕 아래 채움
    for (x0_, x1_, d, is_cab, open_) in ((xa, xa + tw, -1, cab[0], end_doors[0]), (xb - tw, xb, 1, cab[1], end_doors[1])):
        ops = [(yc - 0.5, yc + 0.5, zf, zf + DOOR_H)] if open_ else []
        wall_y(C, "car", x0_, x1_, yc - hw_, yc + hw_, zf - 0.35, zf + CAR_WALL, ops)
        C.plate("car", list(outer), (x0_, yc, 0.0), (1, 0, 0), tw)
        xf = x1_ if d > 0 else x0_
        _car_end_decals(C, xf, yc, zf, d, is_cab, door_open=open_)
        if open_:
            C.rect("hazard", (xf, yc, zf + DOOR_H + 0.05), (d, 0, 0), 1.0, 0.06, lift=0.02)
    # 바닥 소지품 (흘린 가방, 신문)
    rng = random.Random(seed)
    for i in range(2):
        px = rng.uniform(xa + 1.5, xb - 1.5)
        C.blob("violet_d" if i else "coral", (px, yc + rng.uniform(-0.4, 0.4), zf + 0.1), 0.16, (1.4, 0.9, 0.7),
               segs=8, rings=4, kind="detail")
    C.rect("white", (rng.uniform(xa + 2, xb - 2), yc + 0.2, zf), (0, 0, 1), 0.35, 0.5, up=(1, 0.4, 0), lift=0.008)


def gangway(C, xa, xb, yc, zf, z_bed):
    """두 칸 사이 통로: 발판 + 주름 덮개(옆·위) + COL. 덮개 바깥 틈도 막는다."""
    # 발판은 양쪽 칸 문턱에 5 cm 걸쳐 5 mm 높게 (윗면이 바닥과 같은 평면이면 깜빡인다). 폭은 비상문(±0.5)보다
    # 1 cm씩 넓혀 옆면을 문 옆 벽·주름 덮개 밑에 묻는다
    C.box("steel_d", xa - 0.05, xb + 0.05, yc - 0.51, yc + 0.51, zf - 0.06, zf + 0.005, kind="detail")
    C.col(xa, xb, yc - CAR_W / 2, yc + CAR_W / 2, z_bed, zf)
    for s in (-1, 1):
        ya, yb = sorted((yc + s * 0.5, yc + s * 0.62))
        C.box("dark", xa, xb, ya, yb, zf, zf + 1.95)
        k = xa + 0.08
        while k < xb:
            C.box("metal", k - 0.02, k + 0.02, ya - 0.01, yb + 0.01, zf - 0.005, zf + 1.95, kind="detail")
            k += 0.15
        # 주름 덮개(안쪽 면 ±0.49)부터 바깥까지: 덮개 옆판에 COL이 없어 통로를 지나는 몸이 덮개 속으로 묻혔다
        yo0, yo1 = sorted((yc + s * 0.49, yc + s * CAR_W / 2))
        C.col(xa, xb, yo0, yo1, z_bed, zf + CAR_H)
    C.box("dark", xa, xb, yc - 0.62, yc + 0.62, zf + 1.95, zf + 2.07)
    C.col(xa, xb, yc - 0.62, yc + 0.62, zf + 1.95, zf + CAR_H)


def detrain_steps(C, x_end, d, yc, zf, z_bed, *, w=1.0):
    """비상 하차 계단 (운전실 끝 비상문 → 궤도 바닥). d = 계단이 뻗는 쪽(±1 X)."""
    n = 6
    tread = 0.36
    s_bot = x_end + d * (n - 1) * tread
    stair_flight(C, "x", yc - w / 2, yc + w / 2, s_bot, -d, z_bed, zf, n, tread=tread, key="steel_d", top_key="steel",
                 z_floor=z_bed + 0.02, nosing=True)
    for s in (-1, 1):
        yy = yc + s * (w / 2 + 0.04)
        z_low = z_bed + (zf - z_bed) / n
        railing(C, (x_end, yy, zf), (s_bot, yy, z_low), h=0.85, key="hazard", col=False, mid=False)
        # 기운 난간 COL: 없으면 계단 옆으로 난간을 뚫고 오르내렸다 (AI 경로도 옆구리로 붙었다)
        C.ccol([(x, y_, z) for (x, ztop) in ((x_end, zf + 0.9), (s_bot, z_low + 0.9))
                for y_ in (yy - 0.04, yy + 0.04) for z in (z_bed, ztop)])


def train(C, x0, yc, zf, z_bed, n, *, length=12.0, gap=0.6, walk=False, open_side=0, open_map=None, nums=None,
          lamps=None, plain_side=0):
    """전동차 편성 (x0에서 +X로 n칸). 맨 앞·뒤는 운전실. 반환: (x 시작, x 끝)."""
    x = x0
    for i in range(n):
        xa, xb = x, x + length
        subway_car(C, xa, xb, yc, zf, z_bed, walk=walk, cab=(i == 0, i == n - 1), open_side=open_side,
                   open_doors=(open_map or {}).get(i, ()), num=(nums[i] if nums else f"W-20{41 + i}"), lamps=lamps,
                   seed=i, plain_side=plain_side)
        if i < n - 1:
            if walk:
                gangway(C, xb, xb + gap, yc, zf, z_bed)
            else:
                C.box("dark", xb, xb + gap, yc - 0.62, yc + 0.62, zf - 0.1, zf + 2.05, kind="detail")
                C.col(xb, xb + gap, yc - CAR_W / 2, yc + CAR_W / 2, z_bed, zf + CAR_H)
        x = xb + gap
    return x0, x - gap


# ================================================================== armory props

def rifle(C, p, d, up, kind="m4", key="gun"):
    """거치대용 총 실루엣 (실제 크기, 상자 5~7개). p = 총 가운데, d = 총구 방향, up = 위."""
    D = Vector(d).normalized()
    U = Vector(up).normalized()
    X = D.cross(U).normalized()
    U = X.cross(D).normalized()
    Mx = Matrix((X, D, U)).transposed().to_4x4()
    Mx.translation = Vector(p)
    b = C.bm(key, "detail")
    parts = {
        "m4": [(-0.022, 0.022, -0.42, -0.18, -0.06, 0.04), (-0.028, 0.028, -0.18, 0.1, -0.05, 0.05),
               (-0.033, 0.033, 0.1, 0.3, -0.04, 0.04), (-0.011, 0.011, 0.3, 0.44, -0.011, 0.011),
               (-0.02, 0.02, -0.06, 0.02, -0.19, -0.05), (-0.018, 0.018, -0.15, -0.1, -0.13, -0.05),
               (-0.016, 0.016, -0.1, 0.06, 0.05, 0.1)],
        "m249": [(-0.025, 0.025, -0.48, -0.2, -0.07, 0.04), (-0.04, 0.04, -0.2, 0.14, -0.06, 0.06),
                 (-0.03, 0.03, 0.14, 0.32, -0.04, 0.04), (-0.014, 0.014, 0.32, 0.55, -0.014, 0.014),
                 (-0.05, 0.05, -0.08, 0.06, -0.2, -0.06), (-0.018, 0.018, -0.17, -0.12, -0.14, -0.06)],
        "m870": [(-0.022, 0.022, -0.45, -0.15, -0.06, 0.035), (-0.026, 0.026, -0.15, 0.08, -0.045, 0.045),
                 (-0.03, 0.03, 0.08, 0.26, -0.06, -0.01), (-0.013, 0.013, 0.08, 0.5, 0.0, 0.026)],
        "m72": [(-0.034, 0.034, -0.4, 0.4, -0.034, 0.034), (-0.02, 0.02, -0.05, 0.05, -0.12, -0.03)],
    }[kind]
    for (a, b_, c, d_, e, f) in parts:
        mk._bm_box(b, a, b_, c, d_, e, f, matrix=Mx)
    if kind in ("m4", "m870"):
        mk._bm_box(C.bm("gun_t" if kind == "m870" else key, "detail"), -0.025, 0.025, -0.43, -0.3, -0.065, 0.045,
                   matrix=Mx)


def weapon_rack(C, x, y, *, yaw=0.0, z=0.0, n=6, kind="m4", double=False, length=2.0, label=None, col=True):
    """총 거치대: 받침 + 홈 판 + 등판 + 세워 둔 총 n정 (double이면 양면). 정면 -Y를 yaw로 돌린다."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    L = length
    dep = 0.55 if double else 0.42
    b = C.bm("steel_d", "detail")
    mk._bm_box(b, -L / 2, L / 2, -dep / 2, dep / 2, 0, 0.1, matrix=Mx)
    mk._bm_box(C.bm("steel", "detail"), -L / 2, L / 2, -0.03, 0.03, 0.1, 1.15, matrix=Mx)   # 밝은 등판: 총 실루엣이 보이게
    mk._bm_box(b, -L / 2 - 0.04, -L / 2 + 0.04, -dep / 2, dep / 2, 0, 1.2, matrix=Mx)
    mk._bm_box(b, L / 2 - 0.04, L / 2 + 0.04, -dep / 2, dep / 2, 0, 1.2, matrix=Mx)
    mk._bm_box(C.bm("violet", "detail"), -L / 2, L / 2, -dep / 2 - 0.005, dep / 2 + 0.005, 0.1, 0.16, matrix=Mx)
    R3 = Mx.to_3x3()
    sides = (-1, 1) if double else (-1,)
    for sgn in sides:
        # 총구 홈 막대 (위)
        mk._bm_box(b, -L / 2, L / 2, sgn * 0.03, sgn * 0.11, 0.98, 1.03, matrix=Mx)
        for i in range(n):
            u = -L / 2 + (i + 0.5) * L / n
            base = Mx @ Vector((u, sgn * 0.14, 0.56))
            dirv = R3 @ Vector((0, sgn * -0.08, 1))
            upv = R3 @ Vector((0, sgn, 0))
            rifle(C, tuple(base), tuple(dirv), tuple(upv), kind=kind)
    if label:
        N = R3 @ Vector((0, -1, 0))
        C.text("white", label, 0.08, tuple(Mx @ Vector((0, -dep / 2 - 0.006, 0.13))), tuple(N), lift=0.004)
    if col:
        lo = Mx @ Vector((-L / 2, -dep / 2, 0))
        hi = Mx @ Vector((L / 2, dep / 2, 0))
        C.col(min(lo.x, hi.x), max(lo.x, hi.x), min(lo.y, hi.y), max(lo.y, hi.y), z, z + 1.2)


def work_table(C, x0, x1, y0, y1, z, *, h=0.62, top="steel", mat_key="navy_l", col=True):
    """작업대 (엘프 높이 0.62 m): 상판 + 고무 매트 + 다리 + 아래 선반. 반환: 상판 윗면 z."""
    zt = z + h
    C.box(top, x0, x1, y0, y1, zt - 0.05, zt, kind="detail")
    C.box(mat_key, x0 + 0.08, x1 - 0.08, y0 + 0.08, y1 - 0.08, zt, zt + 0.012, kind="detail")
    for (xa, ya) in ((x0 + 0.06, y0 + 0.06), (x1 - 0.06, y0 + 0.06), (x0 + 0.06, y1 - 0.06), (x1 - 0.06, y1 - 0.06)):
        C.box("steel_d", xa - 0.035, xa + 0.035, ya - 0.035, ya + 0.035, z, zt - 0.05, kind="detail")
    C.box("steel_d", x0 + 0.06, x1 - 0.06, y0 + 0.06, y1 - 0.06, z + 0.16, z + 0.2, kind="detail")
    if col:
        C.col(x0, x1, y0, y1, z, zt)
    return zt + 0.012


US_STENCIL = ("U.S. ARMY", "노획품 · 지구 반입 · MNT-A")


def us_crate(C, x, y, z, *, l=1.0, w=0.6, h=0.5, rot=False, stencil=1, key="od", text_sides=(-1,), col=True):
    """노획 미군 상자 (올리브 드랩, 테두리 각재, 스텐실). rot=True면 긴 쪽이 Y. stencil 0: 없음, 1: U.S. ARMY,
    2: U.S. ARMY + '노획품 · 지구 반입 · MNT-A'. 반환: 윗면 z."""
    lx, ly = (w, l) if rot else (l, w)
    x0, x1, y0, y1 = x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2
    C.box(key, x0, x1, y0, y1, z, z + h, kind="detail")
    # 테 각재·모서리 기둥은 뚜껑(z + h)보다 4 mm 낮게 끝난다: 같은 높이면 각재 윗면이 뚜껑 전체를 덮어 od/od_d가 깜빡인다
    zl = z + h - 0.004
    for (a, b_) in ((z, z + 0.05), (z + h - 0.05, zl)):
        C.box("od_d", x0 - 0.012, x1 + 0.012, y0 - 0.012, y1 + 0.012, a, b_, kind="detail")
    for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        C.box("od_d", cx - 0.03, cx + 0.03, cy - 0.03, cy + 0.03, z, zl, kind="detail")
    if stencil:
        for s in text_sides:
            if rot:
                N = (s, 0, 0)
                fc = (x + s * lx / 2, y, z + h * 0.58)
            else:
                N = (0, s, 0)
                fc = (x, y + s * ly / 2, z + h * 0.58)
            size = min(0.11, (l - 0.2) / 7.0)
            C.text("stencil", US_STENCIL[0], size, fc, N, lift=0.01)
            if stencil >= 2:
                C.text("stencil", US_STENCIL[1], size * 0.62, (fc[0], fc[1], fc[2] - h * 0.3), N, lift=0.01)
    if col:
        C.col(x0, x1, y0, y1, z, z + h)
    return z + h


def ammo_cans(C, x, y, z, n=4, *, axis="x", key="od"):
    """탄약통 줄 (작은 올리브 상자 + 손잡이)."""
    for i in range(n):
        cx = x + (i * 0.3 if axis == "x" else 0)
        cy = y + (i * 0.3 if axis == "y" else 0)
        C.box(key, cx - 0.13, cx + 0.13, cy - 0.08, cy + 0.08, z, z + 0.19, kind="detail")
        C.box("od_d", cx - 0.06, cx + 0.06, cy - 0.015, cy + 0.015, z + 0.19, z + 0.22, kind="detail")


def ammo_cage(C, x0, x1, y0, y1, z, *, h=2.4, gate=("n", 0.0, 1.4), sign_text=("탄약 · AMMUNITION", "화기 엄금")):
    """탄약 철망 우리: 기둥 + 위 테 + 반투명 철망 + 가로대, 문 자리(gate=(쪽, 시작, 폭)) 열린 문짝. COL 벽(문 비움)."""
    side, g0, gw = gate
    posts = []
    for (xa, ya) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        posts.append((xa, ya))
    for (xa, ya) in posts:
        C.box("steel_d", xa - 0.05, xa + 0.05, ya - 0.05, ya + 0.05, z, z + h, kind="detail")
    C.box("steel_d", x0, x1, y0 - 0.03, y0 + 0.03, z + h - 0.06, z + h, kind="detail")
    C.box("steel_d", x0, x1, y1 - 0.03, y1 + 0.03, z + h - 0.06, z + h, kind="detail")
    C.box("steel_d", x0 - 0.03, x0 + 0.03, y0, y1, z + h - 0.06, z + h, kind="detail")
    C.box("steel_d", x1 - 0.03, x1 + 0.03, y0, y1, z + h - 0.06, z + h, kind="detail")
    sides = {"n": ("x", y1, x0, x1, 1), "s": ("x", y0, x0, x1, -1), "e": ("y", x1, y0, y1, 1), "w": ("y", x0, y0, y1, -1)}
    for nm, (ax, c, a0, a1, sg) in sides.items():
        segs = [(a0, a1)]
        if nm == side:
            ga, gb = a0 + g0, a0 + g0 + gw
            segs = [(a0, ga), (gb, a1)]
        for (a, b_) in segs:
            if b_ - a < 0.05:
                continue
            m = (a + b_) / 2
            N = (0, sg, 0) if ax == "x" else (sg, 0, 0)
            ctr = (m, c, z + h / 2) if ax == "x" else (c, m, z + h / 2)
            # 반투명 양면 철망 두 장: 같은 평면이면 겹쳐 깜빡이므로 3 mm씩 앞뒤로 (가로대·기둥 ±2 cm 안)
            C.rect("mesh_a", ctr, N, b_ - a, h - 0.1, lift=0.003)
            C.rect("mesh_a", ctr, tuple(-v for v in N), b_ - a, h - 0.1, lift=0.003)
            k = a + 0.5
            while k < b_ - 0.1:
                if ax == "x":
                    C.box("steel_d", k - 0.02, k + 0.02, c - 0.02, c + 0.02, z, z + h, kind="detail")
                else:
                    C.box("steel_d", c - 0.02, c + 0.02, k - 0.02, k + 0.02, z, z + h, kind="detail")
                k += 0.5
            for zz in (z + 0.1, z + h * 0.5):
                if ax == "x":
                    C.box("steel_d", a, b_, c - 0.02, c + 0.02, zz, zz + 0.04, kind="detail")
                    C.col(a, b_, c - 0.04, c + 0.04, z, z + h)
                else:
                    C.box("steel_d", c - 0.02, c + 0.02, a, b_, zz, zz + 0.04, kind="detail")
                    C.col(c - 0.04, c + 0.04, a, b_, z, z + h)
    # 열린 문짝 (밖으로 젖힘)
    ax, c, a0, a1, sg = sides[side]
    ga = a0 + g0
    if ax == "x":
        hinge = Vector((ga, c, z))
        C.rbox("mesh_a", (hinge.x - 0.0, hinge.y + sg * gw / 2, z + h / 2), (0.03, gw, h - 0.1), kind="fine")
        C.box("steel_d", ga - 0.02, ga + 0.02, min(c, c + sg * gw) - 0.005, max(c, c + sg * gw) + 0.005, z + h - 0.12,
              z + h - 0.08, kind="detail")   # 문짝 철망 끝면보다 5 mm 길게
        C.col(ga - 0.04, ga + 0.04, min(c, c + sg * gw), max(c, c + sg * gw), z, z + h)
        sc = (ga + gw / 2, c + sg * 0.05, z + h - 0.32)
        sn = (0, sg, 0)
    else:
        hinge = Vector((c, ga, z))
        C.rbox("mesh_a", (c + sg * gw / 2, ga, z + h / 2), (gw, 0.03, h - 0.1), kind="fine")
        C.col(min(c, c + sg * gw), max(c, c + sg * gw), ga - 0.04, ga + 0.04, z, z + h)
        sc = (c + sg * 0.05, ga + gw / 2, z + h - 0.32)
        sn = (sg, 0, 0)
    if sign_text:
        sign(C, sc, sn, 1.7, 0.42, [(sign_text[0], 0.12, "hazard", 0.06, 0.0), (sign_text[1], 0.09, "white", -0.11, 0.0)],
             key="dark", rim="hazard", depth=0.03)


def shelf_unit(C, x0, x1, y0, y1, z, *, h=2.0, levels=4, seed=0, col=True, fill=("od", "cardboard", "od_d")):
    """강철 선반 + 상자·탄약통. 긴 쪽 자동."""
    rng = random.Random(seed)
    # 기둥은 선반 판 끝면보다 5 mm 밖으로 (같은 평면이면 판 끝면과 기둥 면이 깜빡인다)
    for (xa, ya) in ((x0 + 0.03, y0 + 0.03), (x1 - 0.03, y0 + 0.03), (x0 + 0.03, y1 - 0.03), (x1 - 0.03, y1 - 0.03)):
        C.box("steel_d", xa - 0.035, xa + 0.035, ya - 0.035, ya + 0.035, z, z + h, kind="detail")
    along_x = (x1 - x0) >= (y1 - y0)
    for k in range(levels):
        zz = z + 0.12 + k * (h - 0.2) / max(1, levels - 1) if levels > 1 else z + 0.12
        C.box("steel", x0, x1, y0, y1, zz - 0.03, zz, kind="detail")
        if k == levels - 1:
            continue
        a, b_ = (x0, x1) if along_x else (y0, y1)
        p = a + 0.08
        while p < b_ - 0.3:
            wdt = rng.uniform(0.25, 0.55)
            hh = rng.uniform(0.18, min(0.42, (h - 0.2) / max(1, levels - 1) - 0.08))
            if rng.random() < 0.85:
                key = fill[rng.randrange(len(fill))]
                if along_x:
                    C.box(key, p, min(p + wdt, b_ - 0.05), y0 + 0.06, y1 - 0.06, zz, zz + hh, kind="detail")
                else:
                    C.box(key, x0 + 0.06, x1 - 0.06, p, min(p + wdt, b_ - 0.05), zz, zz + hh, kind="detail")
            p += wdt + 0.05
    if col:
        C.col(x0, x1, y0, y1, z, z + h)


def riot_rack(C, x0, x1, y, z, *, side=-1, n=5):
    """진압반 방패 거치대 [오리지널]: 남보라 틀 + 청록 띠 방패(둥근 판) + 전기충격봉. side = 정면(-1이면 -Y 쪽)."""
    C.box("violet_d", x0, x1, y - 0.25, y + 0.25, z, z + 0.12, kind="detail")
    C.box("violet_d", x0, x1, y - 0.04, y + 0.04, z + 0.12, z + 1.3, kind="detail")
    N = (0, side, 0)
    for i in range(n):
        u = x0 + (i + 0.5) * (x1 - x0) / n
        c = (u, y + side * 0.12, z + 0.7)
        C.plate("violet", hw.rrect(0.42, 0.9, 0.14, 3), c, N, 0.03, kind="detail")
        C.strip("teal", (u - 0.19, y + side * 0.151, z + 0.95), (u + 0.19, y + side * 0.151, z + 0.95), 0.07, N,
                lift=0.002)
        C.decal("glass_a", hw.rrect(0.26, 0.14, 0.04, 2), (u, y + side * 0.151, z + 0.78), N, lift=0.004)
    C.text("white", "진압반 · SUPPRESSION UNIT", 0.1, ((x0 + x1) / 2, y + side * 0.041, z + 1.2), N, lift=0.004)
    C.col(x0, x1, y - 0.25, y + 0.25, z, z + 1.3)


def column_sq(C, x, y, z0, z1, *, s=0.8, key="concrete"):
    """병기창고 사각 기둥 + 노랑·검정 띠 + COL."""
    h_ = s / 2
    C.box(key, x - h_, x + h_, y - h_, y + h_, z0, z1, col=True)
    for (N, c) in (((1, 0, 0), (x + h_, y)), ((-1, 0, 0), (x - h_, y)), ((0, 1, 0), (x, y + h_)), ((0, -1, 0), (x, y - h_))):
        # 노랑·검정 세로 줄을 한 평면에 나란히 (노랑 위에 검정을 얹으면 같은 편향 등급이라 멀리서 깜빡인다)
        T = (N[1], N[0])
        cuts = [-h_] + sum(([k * 0.25 - 0.045, k * 0.25 + 0.045] for k in (-1, 0, 1)), []) + [h_]
        for i in range(0, len(cuts), 2):
            u = (cuts[i] + cuts[i + 1]) / 2
            C.rect("hazard", (c[0] + T[0] * u, c[1] + T[1] * u, z0 + 0.5), N, cuts[i + 1] - cuts[i], 0.6, lift=0.006)
        for k in (-1, 0, 1):
            C.rect("dark", (c[0] + T[0] * k * 0.25, c[1] + T[1] * k * 0.25, z0 + 0.5), N, 0.09, 0.6, lift=0.006)


def tool_board(C, x0, x1, y, z, *, side=1):
    """작업대 위 공구판 (구멍판 + 공구 실루엣)."""
    N = (0, side, 0)
    C.rect("cardboard", ((x0 + x1) / 2, y, z + 0.55), N, x1 - x0, 1.0, lift=0.01)
    rng = random.Random(7)
    k = x0 + 0.2
    while k < x1 - 0.15:
        hh = rng.uniform(0.2, 0.45)
        C.rect("gun" if rng.random() < 0.5 else "red", (k, y, z + 0.55 + rng.uniform(-0.2, 0.2)), N, 0.05, hh, lift=0.016)
        k += rng.uniform(0.18, 0.32)


def vehicle_ramp(C, x0, x_flat, x_top, x1, y0, y1, *, z0, z_top, t=0.5, head=4.2, ls=None):
    """차량 경사로 터널: 앞마당(z0) → 경사(+COL 쐐기) → 윗마당(z_top) → 지상 출구(햇빛판 + 빛기둥, 뒤는 COL 벽).
    벽(+COL)과 기울어진 천장, 노랑 가장자리 띠, 미끄럼 방지 줄, 호박색 비상등(ls)."""
    C.box("concrete_d", x0, x_flat, y0, y1, z0 - 0.3, z0, col=True)
    h = wedge(C, "concrete_d", x_flat, x_top, y0, y1, z0, z_top, "+x", z_floor=z0 - 0.3)
    col_wedge(C, x_flat, x_top, y0, y1, z0, z_top, "+x", z_floor=z0 - 0.3)
    C.box("concrete_d", x_top, x1, y0, y1, z_top - 0.3, z_top, col=True)
    ang = math.atan2(z_top - z0, x_top - x_flat)
    # 가장자리 띠 + 미끄럼 방지 홈
    for yy in (y0 + 0.2, y1 - 0.2):
        C.strip("hazard", (x_flat, yy, z0), (x_top, yy, z_top), 0.16, (-math.sin(ang), 0, math.cos(ang)), lift=0.01)
    k = x_flat + 0.6
    while k < x_top - 0.3:
        zz = h(k, y0)
        C.strip("dark", (k, y0 + 0.5, zz), (k, y1 - 0.5, zz), 0.06, (-math.sin(ang), 0, math.cos(ang)), lift=0.008)
        k += 0.9
    # 벽
    zmax = z_top + head + 0.4
    for (ya, yb) in ((y0 - t, y0), (y1, y1 + t)):
        C.box("concrete", x0, x1 + t, ya, yb, z0 - 0.3, zmax, col=True)
    for (yf, s) in ((y0, 1), (y1, -1)):
        C.strip("violet", (x0, yf, z0 + 0.9), (x_flat, yf, z0 + 0.9), 0.14, (0, s, 0), lift=0.008)
        C.strip("violet", (x_flat, yf, z0 + 0.9), (x_top, yf, z_top + 0.9), 0.14, (0, s, 0), lift=0.008)
        C.strip("violet", (x_top, yf, z_top + 0.9), (x1, yf, z_top + 0.9), 0.14, (0, s, 0), lift=0.008)
    # 천장 (앞마당 평판, 경사 기울어진 판, 윗마당 평판): 두 벽 사이(y0..y1)만 채운다. 벽 두께까지 덮으면 판 옆면이
    # 벽 바깥면과 같은 평면에 겹친다(벽은 천장보다 높이 올라가 있어 틈이 없다)
    ceil_box(C, "tunnel_d", x0, x_flat, y0, y1, z0 + head, z0 + head + 0.3, col=False)
    L = math.hypot(x_top - x_flat, z_top - z0)
    if CEIL["on"]:
        C.rbox("tunnel_d", ((x_flat + x_top) / 2, (y0 + y1) / 2, (z0 + z_top) / 2 + head + 0.15),
               (L + 0.1, y1 - y0, 0.3), rot=(0, -math.degrees(ang), 0))
    ceil_box(C, "tunnel_d", x_top, x1 + t, y0, y1, z_top + head, z_top + head + 0.3, col=False)
    # 지상 출구: 햇빛판 + 빛기둥 + 막는 COL
    C.box("day", x1, x1 + 0.1, y0, y1, z_top, z_top + head)
    C.box("daybeam", x1 - 6.0, x1 - 0.01, y0 + 0.4, y1 - 0.4, z_top + 0.05, z_top + head - 0.2)   # 햇빛판과 1 cm
    C.col(x1, x1 + t, y0, y1, z_top - 0.3, z_top + head)
    if ls is not None:
        k = x0 + 2.0
        while k < x1 - 1.0:
            zz = h(k, y0) if x_flat <= k <= x_top else (z0 if k < x_flat else z_top)
            for (yf, s) in ((y0, 1), (y1, -1)):
                emerg_lamp(C, ls, (k, yf, zz + 2.4), (0, s, 0), halo=0.7)
            k += 7.0
    return h


def ladder(C, x, y, z0, z1, *, normal=(1, 0, 0), w=0.5):
    """벽 사다리 (가로대 0.3 m)."""
    N = Vector(normal).normalized()
    R = Vector((-N.y, N.x, 0))
    base = Vector((x, y, z0)) + N * 0.18
    for s in (-1, 1):
        p = base + R * (s * w / 2)
        C.beam("steel_d", tuple(p), tuple(p + Vector((0, 0, z1 - z0))), 0.05, 0.05, kind="detail")
    k = z0 + 0.3
    while k < z1:
        p = Vector((x, y, k)) + N * 0.18
        C.cyl("steel", tuple(p - R * (w / 2)), tuple(p + R * (w / 2)), 0.02, segs=6, kind="detail")
        k += 0.3
    a, b = Vector((x, y, 0)) - R * (w / 2 + 0.03), Vector((x, y, 0)) + R * (w / 2 + 0.03) + N * 0.21
    C.col(min(a.x, b.x), max(a.x, b.x), min(a.y, b.y), max(a.y, b.y), z0, z1)   # 벽에서 0.21 m (몸이 사다리에 묻혔다)


# ================================================================== report

def report(C):
    """규약 노드 목록 (보고용): 마커 위치·속성, TRIG 상자, DOOR move, LIGHT 묶음."""
    pref = ("SPAWN_", "MARK_", "ALLY_", "PICKUP_", "ENEMY_", "COVER_", "FX_", "NPC_")
    print("[sk] ---- contract nodes (Blender coords, z up) ----")
    groups: dict[str, int] = {}
    for (nm, loc, rot, props, g, _) in C.markers:
        if not nm.startswith(pref):
            continue
        yaw = math.degrees(rot[2]) if rot is not None else 0.0
        pp = " ".join(f"{k}={v}" for k, v in props.items())
        print(f"[sk] {nm:28s} ({loc[0]:7.2f}, {loc[1]:7.2f}, {loc[2]:6.2f}) yaw {yaw:6.1f}  {pp}")
        if nm.startswith("ENEMY_"):
            gg = props.get("group", "?")
            groups[gg] = groups.get(gg, 0) + 1
    for tid, (x0, x1, y0, y1, z0, z1) in TRIGS.items():
        print(f"[sk] TRIG_{tid:23s} x {x0:.2f}..{x1:.2f}  y {y0:.2f}..{y1:.2f}  z {z0:.2f}..{z1:.2f}")
    for g, o in C.specials:
        if o.name.startswith(("DOOR_", "LIGHT_")):
            me = o.data
            xs = [o.location + v.co for v in me.vertices]
            lo = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
            hi = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
            extra = (f"move={o['move']}" if o.name.startswith("DOOR_")
                     else f"group={o['group']} on={o['on']} color={o['color']}" + (f" blink={o['blink']}" if "blink" in o else ""))
            print(f"[sk] {o.name:28s} box ({lo.x:.2f},{lo.y:.2f},{lo.z:.2f})..({hi.x:.2f},{hi.y:.2f},{hi.z:.2f})  {extra}")
    print("[sk] enemy groups:", ", ".join(f"{k}={v}" for k, v in sorted(groups.items())))
