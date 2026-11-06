"""인터루드 「기록」 지구 장면 디오라마 키트 (interlude_kit).

투항(interlude_surrender), 포로 생활(interlude_camp), 대탈주(interlude_escape) 세 세트가 같이 쓴다.
규약: docs/LEVELS.md(노드 이름), 설명: docs/art/interlude-earth.md, 대본: docs/script/interlude.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, interlude_kit as ik
    L = ik.begin("interlude_camp", mode="day")      # cb.reset + 팔레트 등록 + level_kit.Level
    F = ik.Frame((4, 2, 0), yaw=90)                  # 지역 좌표계 (원점, Z 회전 도)
    ik.workbench(L, F, 6.0)
    ik.finish(L, "levels/interlude_camp.glb", root_props={...})

설계
  - 지오메트리 누적·마커·카메라 레일·LIGHT_ 노드는 level_kit.Level을 그대로 쓴다(구역 × 머티리얼별 메시 하나).
    이 키트는 지구 쪽 팔레트(들판, 수용소, 작업장)와 모듈 함수만 더한다.
  - 디오라마라 충돌체를 만들지 않는다. 모든 메시 collider=0. 엔진에서는 physics:false로 읽는다.
  - 이름 있는 노드 묶음(group): GATE_off/on, CAL_page_nn, LIGHT_search_nn처럼 미션이 켜고 끄거나 돌리는 것.
    빈 오브젝트(피벗) 아래 머티리얼별 자식 메시. 피벗 = 돌리는 축(달력 장은 윗변, 서치라이트는 받침).
  - mode="night"이면 불투명 팔레트 전체를 밤빛(남청)으로 눌러 등록한다. 엔진 주광 세기가 고정(2.4)이라
    밤을 조명만으로 만들 수 없어서 색 자체를 밤색으로 칠한다. 발광(UNLIT)은 그대로 밝다.

좌표: Blender Z-up, 1 BU = 1 m, 빈 오브젝트의 -Y가 정면(NPC, CAM, PROP). Frame(yaw=0)의 지역 -Y도 정면이다.
"""
from __future__ import annotations

import math
import os
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import cb
import home_weapons as hw
import level_kit as lk

# ------------------------------------------------------------------ palette (불투명, 툰)
EPAL = {
    # 땅·자연
    "grass": "#93ab6c", "grass_d": "#74905a", "wheat": "#d8b874", "wheat_d": "#bf9a5a",
    "dirt": "#8b6a52", "dirt_d": "#6a4f40", "dirt_l": "#ab8d70", "gravel": "#aaa49b", "gravel_d": "#8c867f",
    "bark": "#6d5446", "leaf": "#6f9658", "leaf_d": "#577c48", "leaf_l": "#8fb46c",
    "hill": "#98ab8e", "hill_d": "#82967f", "rock": "#9b958f",
    # 인간 시설 (수용소)
    "concrete": "#bcb6ac", "concrete_d": "#9b958c", "corr": "#a8adb1", "corr_d": "#878d92", "rust": "#a0644a",
    "wood": "#b08a62", "wood_d": "#86674a", "plank": "#c6a679", "od": "#6f7a5c", "od_d": "#59634a",
    "pipe": "#7e8389", "barn": "#a65a4b", "roof": "#6a666c", "silo": "#cbc5bb", "barbed": "#5a5c62",
    "mattress": "#cdc6b2", "blanket": "#6e7a8d", "blanket_d": "#5a6577", "pillow": "#e6e0d0",
    "bench": "#9c7c5c", "bench_d": "#6f5843", "belt": "#3f3d43", "roller": "#b8bbc0",
    "box": "#c49a64", "box_d": "#a47e50", "tape": "#d9c39a",
    "toy_red": "#c9473f", "toy_green": "#3f7a4f", "toy_white": "#f1ede4", "toy_skin": "#f2d4c0",
    "toy_gold": "#e1b54d", "ribbon": "#e7c04c",
    "pcb": "#3f8a5a", "chip": "#2c2b31", "copper": "#c98a4a", "solder": "#c9cbd0",
    "bean": "#2b211e", "tray": "#b7bcc1", "can_y": "#f0c43c", "can_k": "#2e2b31",
    "cal": "#f4eee0", "ink": "#3a3439", "ink_r": "#c4463e", "chalk": "#3f4b45", "chalk_w": "#eae6da",
    "lampshade": "#59615a", "battery": "#3a3f48", "cable": "#2f2d34", "cable_r": "#a8463c", "cable_y": "#d6b34a",
    "scorch": "#3c3537", "cloth_w": "#f0ede5", "cloud_w": "#f6f2ec", "cloud_s": "#d9d3d6",
    "smoke": "#7c797c", "smoke_l": "#a9a6a7", "smoke_d": "#59565b",
    "screen_off": "#26303a", "plastic_g": "#8f9692", "tarp": "#7c8466",
}
# UNLIT 발광 (조명 없는 단색)
EGLOW = {
    "sunwin": "#fff5d6",      # 한여름 창빛
    "lamp_on": "#fff0c2",     # 백열등
    "moonwin": "#9fb6e6",     # 밤 창빛 (달빛)
    "search": "#fffbea",      # 서치라이트 렌즈
    "ember": "#ff8a3d", "fire": "#ffc35a",
    "gate": "#7ff0ea", "gate_core": "#effffd", "gate_off": "#2c4c56",
    "bulb_r": "#ff6a5a", "bulb_g": "#7dffa0", "bulb_y": "#ffe17a", "bulb_off": "#4a4648",
    "led_g": "#7dff9a", "led_r": "#ff5a4a",
    "sun_disc": "#fff1c8",
    # 하늘 띠 (배경판)
    "sky_dawn_0": "#f6cfae", "sky_dawn_1": "#e8b9a8", "sky_dawn_2": "#c9b1bd", "sky_dawn_3": "#a8a9c6",
    "sky_dusk_0": "#ffbf7a", "sky_dusk_1": "#f39a78", "sky_dusk_2": "#c97f92", "sky_dusk_3": "#8a78a6",
    "sky_dusk_4": "#5b5e93",
    "star_w": "#ffffff",
    # 인간 실루엣 (가까움 → 멂). hum_n: 밤에 빛 앞을 지나는 역광 실루엣 (human_runner tone="n")
    "hum_0": "#2b2f36", "hum_1": "#3d434c", "hum_2": "#5d6570", "hum_n": "#121419",
}
# 반투명 UNLIT (색, 알파)
EALPHA = {
    "sunbeam": ("#fff2c8", 0.16), "searchbeam": ("#fff8dc", 0.11), "moonbeam": ("#a9c2ff", 0.11),
    "portal": ("#7ff0ea", 0.62), "portal_w": ("#e8fffc", 0.45), "spill": ("#7ff0ea", 0.20),
    "gate_beam": ("#9ff6f1", 0.06),
    "fence_net": ("#8e949a", 0.16), "window_g": ("#bcd8e0", 0.22), "haze": ("#f3dccb", 0.14),
    "alarm_beam": ("#ff4a3a", 0.12),
}
# 실루엣 번짐 껍질: 안쪽 면만 그리는(뒷면 컬링 + 뒤집힌 법선) 반투명 UNLIT
EHALO = {"halo_0": ("#2b2f36", 0.34), "halo_0b": ("#2b2f36", 0.14), "halo_1": ("#3d434c", 0.28),
         "halo_2": ("#5d6570", 0.22), "halo_n": ("#121419", 0.32)}
DARK_LINE = {"belt", "chip", "can_k", "bean", "cable", "battery", "scorch", "od_d", "screen_off", "barbed",
             "smoke_d", "dirt_d", "bark"}

NIGHT_TINT = "#1c2645"


def _mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cbb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cbb))


def _scale(h, k):
    h = h.lstrip("#")
    return "#" + "".join(f"{min(255, round(int(h[i:i + 2], 16) * k)):02x}" for i in (0, 2, 4))


def night(h, t=0.55, k=0.68):
    """밤색: 남청 쪽으로 섞고 어둡게."""
    return _scale(_mix(h, NIGHT_TINT, t), k)


MODE = "day"


def begin(name, *, mode="day"):
    """cb.reset → 팔레트 등록 → Level. mode: day / dawn / night."""
    global MODE
    MODE = mode
    cb.reset()
    lk._mats.clear()
    pal = dict(EPAL)
    base_lk = dict(_LK_PAL0)
    if mode == "night":
        pal = {k: night(v) for k, v in pal.items()}
        base_lk = {k: night(v) for k, v in base_lk.items()}
    lk.PAL.clear()
    lk.PAL.update(base_lk)
    lk.PAL.update(pal)
    lk.GLOW.update(EGLOW)
    lk.ALPHA.update(EALPHA)
    lk.ALPHA.update({k: v for k, v in EHALO.items()})
    lk._DARK.update(DARK_LINE)
    # 번짐 껍질: 뒷면 컬링 머티리얼을 캐시에 먼저 넣는다 (lk.M이 그대로 돌려준다)
    for k, (c, a) in EHALO.items():
        lk._mats[k] = cb.mat(f"lk_{k}", c, emission=c, unlit=True, alpha=a, double_sided=False)
    L = lk.Level(name)
    L.ik_groups = []
    L.ik_extra = []
    return L


_LK_PAL0 = dict(lk.PAL)   # level_kit 원래 팔레트 (밤 모드 재등록용)


def finish(L, rel_path, *, root_props=None, outline=0.012, detail_outline=0.005, prop=False):
    """Level.finish + 묶음 노드(group)와 불러온 오브젝트(ik_extra)를 루트 아래로 옮겨 내보낸다."""
    orig = cb.export

    def export(rel, *, props=None, root=None):
        bpy.context.view_layer.update()
        for o in L.ik_groups + L.ik_extra:
            if o.parent is None:
                mw = o.matrix_world.copy()
                o.parent = root
                o.matrix_parent_inverse = Matrix.Identity(4)
                o.matrix_world = mw
        for o in bpy.context.scene.objects:
            if o.type == "MESH":
                o["collider"] = 0
        return orig(rel, props=props, root=root)

    cb.export = export
    try:
        return L.finish(rel_path, root_props=root_props, outline=outline, detail_outline=detail_outline, prop=prop)
    finally:
        cb.export = orig


# ------------------------------------------------------------------ local frame

class Frame:
    """지역 좌표계: origin + Z 회전(도). p()는 월드 점, box/rbox/cyl은 L에 바로 쌓는다."""

    def __init__(self, origin=(0, 0, 0), yaw=0.0):
        self.o = Vector(origin)
        self.yaw = yaw
        self.R = Matrix.Rotation(math.radians(yaw), 4, "Z")
        self.M = Matrix.Translation(self.o) @ self.R

    def p(self, x, y=0.0, z=0.0):
        if isinstance(x, (tuple, list, Vector)):
            x, y, z = x
        return tuple(self.M @ Vector((x, y, z)))

    def d(self, x, y=0.0, z=0.0):
        if isinstance(x, (tuple, list, Vector)):
            x, y, z = x
        return tuple(self.R.to_3x3() @ Vector((x, y, z)))

    def sub(self, x, y, z=0.0, yaw=0.0):
        return Frame(self.p(x, y, z), self.yaw + yaw)

    def box(self, L, key, x0, x1, y0, y1, z0, z1, *, kind="main", rot=(0, 0, 0)):
        c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        L.rbox(key, self.p(c), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)),
               (rot[0], rot[1], rot[2] + self.yaw), kind=kind)

    def rbox(self, L, key, c, size, rot=(0, 0, 0), *, kind="main"):
        L.rbox(key, self.p(c), size, (rot[0], rot[1], rot[2] + self.yaw), kind=kind)

    def cyl(self, L, key, p0, p1, r, *, verts=12, kind="main", r2=None, cap=True):
        return L.cyl(key, self.p(p0), self.p(p1), r, verts=verts, kind=kind, r2=r2, cap=cap)

    def place(self, o):
        o.matrix_world = self.M @ o.matrix_basis
        return o

    def obj(self, L, key, o, *, kind="main"):
        return L.obj(key, self.place(o), kind=kind)

    def face(self, nx, ny, nz=0.0):
        """지역 법선 → 월드 법선."""
        return self.d(nx, ny, nz)


def sphere(key_unused, r, c, scale=(1, 1, 1), seg=10, rings=7, rot=(0, 0, 0)):
    """저분할 구 (L.obj로 넘겨 합친다)."""
    return cb.sphere("sph", radius=r, loc=c, scale=scale, segments=seg, rings=rings, rot=rot)


def obj_from_bm(build, name="tmp"):
    b = bmesh.new()
    build(b)
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    return o


# ------------------------------------------------------------------ named groups (GATE_, CAL_page_, LIGHT_ ...)

class Group:
    """이름 있는 노드 묶음. 피벗(빈 오브젝트) 아래 머티리얼별 자식 메시.

    g = ik.Group(L, "GATE_on", pivot=(0, 0, 1.2), props={"state": "on"})
    g.obj("gate", o)       # cb 오브젝트(월드 좌표) 추가
    g.bm("portal")         # 월드 좌표 bmesh에 직접 쓰기
    g.done()
    """

    def __init__(self, L, name, pivot=(0, 0, 0), *, props=None, rot=None):
        self.L = L
        self.name = name
        self.pivot = Vector(pivot)
        self.rot = rot
        self.props = dict(props or {})
        self.parts: dict[tuple, bmesh.types.BMesh] = {}

    def bm(self, key, kind="main"):
        kind = "fine" if lk.is_glow(key) else kind
        k = (key, kind)
        if k not in self.parts:
            self.parts[k] = bmesh.new()
        return self.parts[k]

    def obj(self, key, o, *, kind="main"):
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.transform(o.matrix_world)
        self.bm(key, kind).from_mesh(me)
        eo.to_mesh_clear()
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(data, bpy.types.Mesh) and data.users == 0:
            bpy.data.meshes.remove(data)

    def box(self, key, x0, x1, y0, y1, z0, z1, *, kind="main", matrix=None):
        lk._bm_box(self.bm(key, kind), x0, x1, y0, y1, z0, z1, matrix=matrix)

    def rbox(self, key, center, size, rot=(0, 0, 0), *, kind="main"):
        Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
              @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        sx, sy, sz = (s / 2 for s in size)
        lk._bm_box(self.bm(key, kind), -sx, sx, -sy, sy, -sz, sz, matrix=Mx)

    def cyl(self, key, p0, p1, r, *, verts=12, kind="main", r2=None, cap=True):
        P0, P1 = Vector(p0), Vector(p1)
        d = P1 - P0
        o = cb.cylinder("gcyl", radius=r, radius2=r2, depth=d.length, verts=verts, cap=cap)
        q = d.normalized().to_track_quat("Z", "Y")
        o.matrix_world = Matrix.Translation((P0 + P1) / 2) @ q.to_matrix().to_4x4()
        self.obj(key, o, kind=kind)

    def done(self):
        root = cb.empty(self.name, loc=tuple(self.pivot), size=0.3)
        if self.rot is not None:
            root.rotation_euler = self.rot
        for k, v in self.props.items():
            root[k] = v
        bpy.context.view_layer.update()
        inv = root.matrix_world.inverted()
        for (key, kind), b in sorted(self.parts.items()):
            if not b.faces:
                b.free()
                continue
            nm = f"{self.name}_{key}"
            me = bpy.data.meshes.new(nm)
            b.to_mesh(me)
            b.free()
            me.transform(inv)
            o = bpy.data.objects.new(nm, me)
            cb.link(o)
            cb.assign(o, lk.M(key))
            o.parent = root
            o["collider"] = 0
            if kind == "fine":
                o["noOutline"] = 1
            elif kind == "detail":
                o["outline"] = 0.004
            for p in me.polygons:
                p.use_smooth = kind != "flat"
        self.L.ik_groups.append(root)
        return root


# ------------------------------------------------------------------ noise / terrain

def vnoise(x, y, seed=0):
    """싼 값 잡음 (-1..1): 사인 합."""
    s = seed * 1.618
    return (math.sin(x * 0.071 + s) * math.cos(y * 0.053 - s * 0.7) * 0.55
            + math.sin(x * 0.163 - y * 0.121 + s * 2.1) * 0.3
            + math.sin(x * 0.37 + y * 0.29 + s * 3.3) * 0.15)


def grid_lines(lo, hi, near=(-20, 20), fine=2.0, grow=1.35, maxstep=40.0):
    """가까운 곳은 촘촘하고 멀수록 성긴 격자선."""
    xs = []
    a = near[0]
    while a <= near[1] + 1e-6:
        xs.append(a)
        a += fine
    step = fine
    a = near[1]
    while a < hi:
        step = min(maxstep, step * grow)
        a = min(hi, a + step)
        xs.append(a)
    step = fine
    a = near[0]
    while a > lo:
        step = min(maxstep, step * grow)
        a = max(lo, a - step)
        xs.insert(0, a)
    return xs


def terrain(L, xs, ys, height, keyf, *, kind="main"):
    """격자 지형. height(x,y) → z, keyf(cx,cy) → 머티리얼 키. 키마다 정점을 공유해 매끈하게."""
    verts: dict[tuple, dict] = {}
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            key = keyf(cx, cy)
            b = L.bm(key, kind)
            vd = verts.setdefault(key, {})

            def V(ii, jj):
                v = vd.get((ii, jj))
                if v is None:
                    x, y = xs[ii], ys[jj]
                    v = vd[(ii, jj)] = b.verts.new((x, y, height(x, y)))
                return v
            f = b.faces.new((V(i, j), V(i + 1, j), V(i + 1, j + 1), V(i, j + 1)))
            f.smooth = True


# ------------------------------------------------------------------ nature

def tree(L, pos, h=6.0, r=2.4, seed=0, *, keys=("bark", "leaf", "leaf_d", "leaf_l"), kind="main"):
    """툰 나무: 줄기 + 뭉게 잎 3~4덩이."""
    rnd = random.Random(seed)
    x, y, z = pos
    L.cyl(keys[0], (x, y, z - 0.3), (x, y, z + h * 0.55), r * 0.12, verts=7, r2=r * 0.08, kind=kind)
    L.cyl(keys[0], (x, y, z + h * 0.35), (x + r * 0.35, y + r * 0.1, z + h * 0.62), r * 0.05, verts=5, kind=kind)
    blobs = [(0, 0, h * 0.72, 1.0)]
    for i in range(3):
        a = rnd.uniform(0, 6.28)
        blobs.append((math.cos(a) * r * 0.45, math.sin(a) * r * 0.45, h * rnd.uniform(0.55, 0.68),
                      rnd.uniform(0.62, 0.8)))
    for bi, (bx, by, bz, s) in enumerate(blobs):
        key = keys[1] if bi == 0 else keys[2 if bi % 2 else 3]
        # 덩이마다 다른 방위(11°씩): 겹친 두 덩이의 면이 나란히 놓여 깊이 다툼하지 않게
        L.obj(key, cb.sphere("t", radius=r * 0.5 * s, loc=(x + bx, y + by, z + bz), rot=(0, 0, bi * 11),
                             scale=(1, 1, 0.82), segments=8, rings=5), kind=kind)


def tuft(L, pos, s=0.35, seed=0, key="grass_d"):
    """풀 덤불: 잎 모양 판 3장 (아웃라인 얇게)."""
    rnd = random.Random(seed)
    x, y, z = pos
    b = L.bm(key, "detail")
    for i in range(3):
        a = rnd.uniform(0, math.pi) + i * 1.05
        d = Vector((math.cos(a), math.sin(a), 0))
        lean = Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 1)).normalized()
        w = s * rnd.uniform(0.18, 0.28)
        hgt = s * rnd.uniform(0.8, 1.2)
        base = Vector((x, y, z - 0.02))
        p = [base - d * w, base + d * w, base + d * w * 0.3 + lean * hgt, base + lean * hgt * 1.08,
             base - d * w * 0.3 + lean * hgt]
        f = b.faces.new([b.verts.new(q) for q in (p[0], p[1], p[2], p[3], p[4])])
        f.smooth = True


def rock(L, pos, s=0.5, seed=0, key="rock"):
    rnd = random.Random(seed)
    o = cb.sphere("rock", radius=s, loc=pos, scale=(rnd.uniform(0.9, 1.3), rnd.uniform(0.8, 1.1), 0.55),
                  segments=7, rings=5, rot=(0, 0, rnd.uniform(0, 180)))
    L.obj(key, o)


def hills_ring(L, center, r0, r1, n, *, h=(8, 22), seed=3, keys=("hill", "hill_d"), arc=(0, 360)):
    """먼 언덕 줄 (안개에 반쯤 묻힘)."""
    rnd = random.Random(seed)
    cx, cy = center[0], center[1]
    for i in range(n):
        a = math.radians(arc[0] + (arc[1] - arc[0]) * (i + rnd.uniform(0.1, 0.9)) / n)
        r = rnd.uniform(r0, r1)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        w = rnd.uniform(30, 60)
        hh = rnd.uniform(*h)
        o = cb.sphere("hill", radius=1.0, loc=(x, y, -hh * 0.35), scale=(w, w * 0.6, hh),
                      segments=14, rings=7, rot=(0, 0, math.degrees(a) + 90))
        L.obj(keys[i % len(keys)], o)


def cloud(L, center, size=10.0, seed=0, *, keys=("cloud_w", "cloud_s"), kind="fine"):
    """납작한 바닥의 뭉게구름 (아웃라인 없음)."""
    rnd = random.Random(seed)
    x, y, z = center
    n = 5
    for i in range(n):
        t = (i - (n - 1) / 2) / n
        r = size * (0.42 - abs(t) * 0.35) * rnd.uniform(0.85, 1.15)
        L.obj(keys[0], cb.sphere("cl", radius=r, loc=(x + t * size * 1.4, y + rnd.uniform(-1, 1) * size * 0.15,
                                                     z + r * 0.35), scale=(1.2, 0.8, 0.75), segments=8, rings=5),
              kind=kind)
    L.obj(keys[1], cb.sphere("cl", radius=size * 0.55, loc=(x, y, z - size * 0.05),
                             scale=(1.5, 0.75, 0.22), segments=12, rings=5), kind=kind)


def sky_backdrop(L, center, radius, a0, a1, z0, bands, *, seg=24, key_prefix="sky_dusk_", lift_disc=None):
    """하늘 띠 배경판: 카메라 쪽을 향한 원통 조각 (UNLIT). bands = [(키, 높이), ...] 아래부터."""
    cx, cy = center[0], center[1]
    z = z0
    for key, hgt in bands:
        b = L.bm(key, "fine")
        top = z + hgt
        prev = None
        for i in range(seg + 1):
            a = math.radians(a0 + (a1 - a0) * i / seg)
            p0 = b.verts.new((cx + math.cos(a) * radius, cy + math.sin(a) * radius, z))
            p1 = b.verts.new((cx + math.cos(a) * radius, cy + math.sin(a) * radius, top))
            if prev:
                f = b.faces.new((prev[0], p0, p1, prev[1]))
                f.normal_update()
                cen = Vector((cx, cy, (z + top) / 2))
                if f.normal.dot(cen - f.calc_center_median()) < 0:
                    f.normal_flip()
            prev = (p0, p1)
        z = top


# ------------------------------------------------------------------ farmland props

def rail_fence(L, pts, height_fn, *, h=1.1, post=3.2, key="wood_d", rail="wood"):
    """나무 울타리 (기둥 + 가로대 2줄)."""
    for (a, b) in zip(pts, pts[1:]):
        A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        n = max(1, round((B - A).length / post))
        for i in range(n + 1):
            P = A.lerp(B, i / n)
            z = height_fn(P.x, P.y)
            L.box(key, P.x - 0.06, P.x + 0.06, P.y - 0.06, P.y + 0.06, z - 0.1, z + h)
        for i in range(n):
            P0, P1 = A.lerp(B, i / n), A.lerp(B, (i + 1) / n)
            for zz in (0.45, 0.85):
                z0 = height_fn(P0.x, P0.y) + zz * h
                z1 = height_fn(P1.x, P1.y) + zz * h
                L.cyl(rail, (P0.x, P0.y, z0), (P1.x, P1.y, z1), 0.045, verts=4, kind="detail", cap=False)


def power_line(L, pts, height_fn, *, h=8.0, key="wood_d", wire="cable"):
    """전봇대 줄 + 처진 전선 3가닥."""
    tops = []
    for (x, y) in pts:
        z = height_fn(x, y)
        L.cyl(key, (x, y, z - 0.5), (x, y, z + h), 0.13, verts=7, r2=0.1)
        tops.append((x, y, z + h))
    for i, (x, y, zt) in enumerate(tops):
        if i + 1 < len(tops):
            d = Vector((tops[i + 1][0] - x, tops[i + 1][1] - y, 0)).normalized()
        else:
            d = Vector((x - tops[i - 1][0], y - tops[i - 1][1], 0)).normalized()
        s = Vector((-d.y, d.x, 0))
        L.cyl(key, tuple(Vector((x, y, zt - 0.5)) - s * 1.0), tuple(Vector((x, y, zt - 0.5)) + s * 1.0), 0.07, verts=5)
    for i in range(len(tops) - 1):
        A, B = Vector(tops[i]), Vector(tops[i + 1])
        d = (B - A)
        d.z = 0
        d.normalize()
        s = Vector((-d.y, d.x, 0))
        for k in (-0.85, 0.0, 0.85):
            off = s * k + Vector((0, 0, -0.42 if k else -0.05))
            prev = A + off
            for t in range(1, 5):
                u = t / 4
                P = A.lerp(B, u) + off + Vector((0, 0, -1.1 * 4 * u * (1 - u)))
                L.cyl(wire, tuple(prev), tuple(P), 0.025, verts=4, kind="fine")
                prev = P


def barn(L, F, *, w=10.0, d=16.0, h=5.0, roof_h=4.0):
    """먼 농가 헛간(박공지붕 꺾임) + 사일로. 지역 원점 = 헛간 앞 가운데 바닥."""
    F.box(L, "barn", -w / 2, w / 2, 0, d, -0.5, h)
    prof = [(-w / 2 - 0.3, h), (-w / 2 + 1.2, h + roof_h * 0.62), (0, h + roof_h), (w / 2 - 1.2, h + roof_h * 0.62),
            (w / 2 + 0.3, h)]
    L.extrude("roof", prof, F.p(0, -0.3, 0), F.d(0, 1, 0), d + 0.6, up=(0, 0, 1))
    gable = [(-w / 2, h - 0.05), (-w / 2 + 1.15, h + roof_h * 0.6), (0, h + roof_h * 0.95),
             (w / 2 - 1.15, h + roof_h * 0.6), (w / 2, h - 0.05)]   # 밑면은 몸체 속 (지붕 밑면 h와 겹치지 않게)
    L.extrude("barn", gable, F.p(0, 0.02, 0), F.d(0, 1, 0), d - 0.04, up=(0, 0, 1))
    # 큰 문 (흰 X 테)
    N = F.d(0, -1, 0)
    c = F.p(0, -0.02, h * 0.42)
    L.decal("toy_white", hw.rrect(w * 0.42, h * 0.8, 0.02), c, N, lift=0.03)
    L.decal("barn", hw.rrect(w * 0.42 - 0.4, h * 0.8 - 0.4, 0.02), c, N, lift=0.05)
    L.strip("toy_white", F.p(-w * 0.19, -0.08, 0.2), F.p(w * 0.19, -0.08, h * 0.8 - 0.2), 0.25, N, lift=0.0)
    L.strip("toy_white", F.p(w * 0.19, -0.08, 0.2), F.p(-w * 0.19, -0.08, h * 0.8 - 0.2), 0.25, N, lift=0.0)
    # 사일로
    sx, sy = w / 2 + 3.2, d * 0.35
    F.cyl(L, "silo", (sx, sy, -0.5), (sx, sy, h + roof_h + 3.5), 2.4, verts=16)
    L.obj("roof", F.place(cb.sphere("dome", radius=2.45, loc=(sx, sy, h + roof_h + 3.5), scale=(1, 1, 0.55),
                                    segments=16, rings=6)))
    for zz in (2.0, 5.0, 8.0):
        F.cyl(L, "roof", (sx, sy, zz), (sx, sy, zz + 0.18), 2.46, verts=16, kind="detail")


# ------------------------------------------------------------------ smoke / fire / scorch

def smoke_column(L, name, base, *, height=40.0, r0=3.0, r1=9.0, lean=(0.35, 0.15), n=12, seed=0, props=None):
    """뭉게 연기 기둥 (정적 메시 묶음 SMOKE_<name>). FX 마커와 함께 둔다. 입자 연기로 바꾸면 숨긴다."""
    rnd = random.Random(seed)
    g = Group(L, f"SMOKE_{name}", pivot=base, props=dict({"fx": "smoke"}, **(props or {})))
    bx, by, bz = base
    for i in range(n):
        t = i / (n - 1)
        r = r0 + (r1 - r0) * t ** 0.8
        z = bz + height * t ** 1.1
        cx = bx + lean[0] * height * t ** 1.6 + rnd.uniform(-0.3, 0.3) * r
        cy = by + lean[1] * height * t ** 1.6 + rnd.uniform(-0.3, 0.3) * r
        key = "smoke_d" if t < 0.25 else ("smoke" if t < 0.65 else "smoke_l")
        for k in range(2 if t > 0.2 else 1):
            o = cb.sphere("puff", radius=r * rnd.uniform(0.7, 1.0),
                          loc=(cx + rnd.uniform(-0.5, 0.5) * r, cy + rnd.uniform(-0.5, 0.5) * r, z + k * r * 0.4),
                          scale=(1.0, 1.0, 0.82), segments=9, rings=6)
            g.obj(key, o)
    g.done()
    L.marker(f"FX_smoke_{name}", base, props=dict({"kind": "smoke", "height": height, "radius": r1,
                                                    "lean": f"{lean[0]:.2f},{lean[1]:.2f}"}, **(props or {})))
    return g


def scorch(L, pos, r=2.0, seed=0, normal=(0, 0, 1)):
    """그을음 자국 (지면 데칼)."""
    rnd = random.Random(seed)
    pts = []
    for i in range(14):
        a = i / 14 * 6.283
        rr = r * rnd.uniform(0.65, 1.05)
        pts.append((math.cos(a) * rr, math.sin(a) * rr * 0.8))
    L.decal("scorch", pts, pos, normal, lift=0.03)


def embers(L, pos, r=0.6, n=5, seed=0):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0, r)
        p = (pos[0] + math.cos(a) * rr, pos[1] + math.sin(a) * rr, pos[2] + 0.04)
        L.decal("ember", hw.circle(rnd.uniform(0.05, 0.14), 6), p, (0, 0, 1), lift=0.04)


# ------------------------------------------------------------------ human silhouettes (초점 나간 인간)

def _limb(parts, p0, p1, r0, r1=None, verts=8):
    parts.append(("cyl", p0, p1, r0, r1 if r1 is not None else r0, verts))
    parts.append(("sph", p0, r0))
    parts.append(("sph", p1, r1 if r1 is not None else r0))


def _chain(parts, pts, radii, verts=8):
    """관절 사슬 (어깨-팔꿈치-손): 마디마다 원뿔대, 관절마다 구 하나 (겹치는 관절 구를 두 번 만들지 않는다)."""
    for (p0, r0), (p1, r1) in zip(zip(pts, radii), zip(pts[1:], radii[1:])):
        parts.append(("cyl", p0, p1, r0, r1, verts))
    for p, r in zip(pts, radii):
        parts.append(("sph", p, r))


def _human_parts(pose, H):
    """인간 병사 실루엣 부품 (지역 좌표, -Y가 정면, 발 z=0). H = 키(m)."""
    if pose in RUN_POSES:
        return _human_run_parts(pose, H)
    k = H / 1.8
    P = []
    hip = Vector((0, 0, 0.98 * k))
    chest = Vector((0, 0.02 * k, 1.38 * k))
    lean = 0.0
    if pose == "aim":
        chest = Vector((0, -0.08 * k, 1.36 * k))
        lean = 1
    neck = chest + Vector((0, 0, 0.18 * k))
    head = neck + Vector((0, -0.02 * k, 0.15 * k))
    # 몸통 (조끼로 두툼)
    P.append(("ell", (hip + chest) / 2, (0.24 * k, 0.17 * k, 0.36 * k)))
    P.append(("ell", chest + Vector((0, -0.02 * k, -0.02 * k)), (0.27 * k, 0.2 * k, 0.2 * k)))
    # 머리 + 헬멧
    P.append(("sph", head, 0.12 * k))
    P.append(("ell", head + Vector((0, 0.01 * k, 0.05 * k)), (0.155 * k, 0.165 * k, 0.12 * k)))
    # 다리
    stance = 0.13 * k
    if pose == "walk":
        _limb(P, hip + Vector((stance, 0, -0.05 * k)), Vector((stance, -0.18 * k, 0.5 * k)), 0.1 * k, 0.085 * k)
        _limb(P, Vector((stance, -0.18 * k, 0.5 * k)), Vector((stance, -0.1 * k, 0.08 * k)), 0.085 * k, 0.07 * k)
        _limb(P, hip + Vector((-stance, 0, -0.05 * k)), Vector((-stance, 0.16 * k, 0.5 * k)), 0.1 * k, 0.085 * k)
        _limb(P, Vector((-stance, 0.16 * k, 0.5 * k)), Vector((-stance, 0.3 * k, 0.1 * k)), 0.085 * k, 0.07 * k)
    else:
        for sx in (1, -1):
            knee = Vector((sx * stance * 1.1, -0.02 * k, 0.5 * k))
            _limb(P, hip + Vector((sx * stance, 0, -0.05 * k)), knee, 0.105 * k, 0.085 * k)
            _limb(P, knee, Vector((sx * stance * 1.2, 0.0, 0.08 * k)), 0.085 * k, 0.07 * k)
    for sx in (1, -1):  # 군화
        fx = sx * stance * (1.2 if pose != "walk" else 1.0)
        fy = 0.0 if pose != "walk" else (-0.1 * k if sx > 0 else 0.3 * k)
        P.append(("ell", Vector((fx, fy - 0.05 * k, 0.05 * k)), (0.07 * k, 0.14 * k, 0.06 * k)))
    # 팔 + 소총
    shL, shR = chest + Vector((0.25 * k, 0, 0.1 * k)), chest + Vector((-0.25 * k, 0, 0.1 * k))
    if pose == "aim":
        stock = chest + Vector((-0.17 * k, -0.12 * k, 0.12 * k))
        muzzle = stock + Vector((0.06 * k, -0.95 * k, -0.08 * k))
        P.append(("cyl", stock, muzzle, 0.035 * k, 0.03 * k, 6))
        P.append(("ell", stock.lerp(muzzle, 0.25) + Vector((0, 0, -0.06 * k)), (0.03 * k, 0.1 * k, 0.08 * k)))
        hR = stock + Vector((0.0, -0.18 * k, -0.06 * k))
        hL = stock.lerp(muzzle, 0.55) + Vector((0, 0, -0.04 * k))
        _limb(P, shR, shR.lerp(hR, 0.5) + Vector((-0.12 * k, 0.05 * k, -0.12 * k)), 0.075 * k, 0.065 * k)
        _limb(P, shR.lerp(hR, 0.5) + Vector((-0.12 * k, 0.05 * k, -0.12 * k)), hR, 0.065 * k, 0.055 * k)
        _limb(P, shL, shL.lerp(hL, 0.5) + Vector((0.1 * k, 0.0, -0.18 * k)), 0.075 * k, 0.065 * k)
        _limb(P, shL.lerp(hL, 0.5) + Vector((0.1 * k, 0.0, -0.18 * k)), hL, 0.065 * k, 0.055 * k)
    elif pose in ("ready", "walk"):
        a = chest + Vector((-0.22 * k, -0.2 * k, -0.18 * k))
        b = chest + Vector((0.32 * k, -0.42 * k, -0.42 * k))
        P.append(("cyl", a + (a - b) * 0.25, b + (b - a) * 0.55, 0.035 * k, 0.03 * k, 6))
        hR, hL = a, a.lerp(b, 0.7)
        _limb(P, shR, Vector((-0.3 * k, -0.05 * k, 1.12 * k)), 0.075 * k, 0.065 * k)
        _limb(P, Vector((-0.3 * k, -0.05 * k, 1.12 * k)), hR, 0.065 * k, 0.055 * k)
        _limb(P, shL, Vector((0.3 * k, -0.1 * k, 1.12 * k)), 0.075 * k, 0.065 * k)
        _limb(P, Vector((0.3 * k, -0.1 * k, 1.12 * k)), hL, 0.065 * k, 0.055 * k)
    else:  # stand: 총은 어깨에 멘다
        for sx, sh in ((1, shL), (-1, shR)):
            el = Vector((sx * 0.31 * k, 0.02 * k, 1.12 * k))
            _limb(P, sh, el, 0.075 * k, 0.065 * k)
            _limb(P, el, Vector((sx * 0.31 * k, -0.04 * k, 0.86 * k)), 0.065 * k, 0.055 * k)
        P.append(("cyl", Vector((-0.2 * k, 0.16 * k, 0.6 * k)), Vector((0.1 * k, 0.17 * k, 1.62 * k)),
                  0.035 * k, 0.03 * k, 6))
    return P


RUN_POSES = ("run_a", "run_b")


def _run_rifle(pose, H):
    """달리기 자세의 총 (지역 좌표): 개머리판을 오른 어깨에 붙이고 총구를 앞 아래로 (낮은 겨눔). (개머리, 방향)."""
    k = H / 1.8
    s = 1 if pose == "run_a" else -1
    chest = Vector((0, -0.12 * k, 1.32 * k))
    bob = Vector((0.012 * k * s, 0, 0.02 * k * s))      # 걸음마다 총이 조금 흔들린다
    stock = chest + Vector((-0.16 * k, -0.12 * k, 0.06 * k)) + bob
    d = Vector((0.12, -0.88, -0.46 + 0.03 * s)).normalized()
    return stock, d


def _human_run_parts(pose, H):
    """뛰는 인간 병사 (run_a: 왼발이 앞, run_b: 오른발이 앞). 상체를 앞으로 숙이고 총은 낮은 겨눔. -Y가 정면."""
    k = H / 1.8
    s = 1 if pose == "run_a" else -1
    P = []
    lean = 17.5
    hip = Vector((0, 0, 0.94 * k))
    chest = Vector((0, -0.12 * k, 1.32 * k))
    neck = chest + Vector((0, -0.04 * k, 0.17 * k))
    head = neck + Vector((0, -0.05 * k, 0.14 * k))
    P.append(("ell", (hip + chest) / 2, (0.24 * k, 0.17 * k, 0.36 * k), (lean, 0, 0)))
    P.append(("ell", chest + Vector((0, -0.02 * k, -0.02 * k)), (0.27 * k, 0.2 * k, 0.2 * k), (lean, 0, 0)))
    P.append(("sph", head, 0.12 * k))
    P.append(("ell", head + Vector((0, 0.02 * k, 0.05 * k)), (0.155 * k, 0.165 * k, 0.12 * k), (8, 0, 0)))
    # 다리: 앞다리는 무릎을 들어 내딛고, 뒷다리는 뒤로 차 올린다
    st = 0.12 * k
    fx, bx = s * st, -s * st
    knee_f, foot_f = Vector((fx, -0.33 * k, 0.56 * k)), Vector((fx, -0.36 * k, 0.1 * k))
    knee_b, foot_b = Vector((bx, 0.16 * k, 0.5 * k)), Vector((bx, 0.5 * k, 0.3 * k))
    legr = (0.1 * k, 0.085 * k, 0.07 * k)
    _chain(P, (hip + Vector((fx, -0.02 * k, -0.05 * k)), knee_f, foot_f), legr)
    _chain(P, (hip + Vector((bx, 0.02 * k, -0.05 * k)), knee_b, foot_b), legr)
    P.append(("ell", Vector((fx, foot_f.y - 0.06 * k, 0.05 * k)), (0.07 * k, 0.14 * k, 0.06 * k)))
    P.append(("ell", Vector((bx, foot_b.y + 0.04 * k, foot_b.z - 0.03 * k)), (0.07 * k, 0.14 * k, 0.06 * k), (40, 0, 0)))
    # 총과 팔
    stock, d = _run_rifle(pose, H)
    muzzle = stock + d * 0.95 * k
    P.append(("cyl", stock, muzzle, 0.035 * k, 0.03 * k, 6))
    P.append(("ell", stock.lerp(muzzle, 0.3) + Vector((0, 0, -0.07 * k)), (0.03 * k, 0.08 * k, 0.08 * k)))
    bob = Vector((0.012 * k * s, 0, 0.02 * k * s))
    shR, shL = chest + Vector((-0.25 * k, 0, 0.1 * k)), chest + Vector((0.25 * k, 0, 0.1 * k))
    hR = stock + d * 0.24 * k + Vector((0, 0, -0.05 * k))
    hL = stock + d * 0.58 * k + Vector((0, 0, -0.04 * k))
    elR = shR.lerp(hR, 0.5) + Vector((-0.12 * k, 0.06 * k, -0.12 * k)) + bob
    elL = shL.lerp(hL, 0.5) + Vector((0.1 * k, 0.02 * k, -0.16 * k)) + bob
    armr = (0.075 * k, 0.065 * k, 0.055 * k)
    _chain(P, (shR, elR, hR), armr)
    _chain(P, (shL, elL, hL), armr)
    return P


def _rifle_light(pose, H):
    """총에 단 전등의 자리와 방향 (지역 좌표). 그 자세에 총구가 앞을 보지 않으면 None."""
    k = H / 1.8
    if pose in RUN_POSES:
        stock, d = _run_rifle(pose, H)
    elif pose == "aim":
        chest = Vector((0, -0.08 * k, 1.36 * k))
        stock = chest + Vector((-0.17 * k, -0.12 * k, 0.12 * k))
        d = Vector((0.06, -0.95, -0.08)).normalized()
    else:
        return None
    return stock + d * 0.9 * k + Vector((0, 0, -0.03 * k)), d


def human_runner(L, name, pos, yaw, *, frames=("run_a", "run_b", "ready"), H=1.82, tone=0, halo=True, torch=False,
                 beam=4.5, props=None):
    """뛰어드는 인간 병사 (플립북). 미션이 묶음을 옮기며 자세 자식을 번갈아 보인다. tone 0..2 또는 "n"(역광, 가장 어둡다).

    <name>        빈 오브젝트 (피벗 = 발밑, Z 회전 = yaw, hidden=1). kind=human_runner, frames="run_a,run_b,..."
    <name>_<자세>  자세마다 자식 묶음 (hum_<tone> + halo_<tone>, torch면 총 전등의 렌즈 search + 빛줄기 searchbeam).
                  첫 자세만 보이고 나머지는 hidden=1. 미션은 run_a/run_b를 걸음마다 바꾸고, 멈추면 마지막 자세를 보인다.
    얼굴·휘장 없는 단색 덩어리는 human()과 같다. 지오메트리는 지역 -Y가 정면이라 미션이 루트를 진행 방향으로 돌린다.
    """
    lo = tone == 2
    root = cb.empty(name, loc=tuple(pos), size=0.3)
    root.rotation_euler = (0, 0, math.radians(yaw))
    root["kind"] = "human_runner"
    root["frames"] = ",".join(frames)
    root["hidden"] = 1
    for k_, v in (props or {}).items():
        root[k_] = v
    bpy.context.view_layer.update()
    F = Frame(pos, 0)
    for i, pose in enumerate(frames):
        g = Group(L, f"{name}_{pose}", pivot=tuple(pos), props={"frame": pose, **({"hidden": 1} if i else {})})
        b = _human_bm(F, pose, H, lo)
        me = bpy.data.meshes.new("tmp_runner")
        b.to_mesh(me)
        g.bm(f"hum_{tone}").from_mesh(me)
        bpy.data.meshes.remove(me)
        if halo and not lo:
            hb = _halo_of(b, 0.045 if tone == 1 else 0.05)
            me = bpy.data.meshes.new("tmp_runner_halo")
            hb.to_mesh(me)
            g.bm(f"halo_{tone}").from_mesh(me)
            bpy.data.meshes.remove(me)
            hb.free()
        b.free()
        lt = _rifle_light(pose, H) if torch else None
        if lt:
            p, d = lt
            g.obj("search", cb.sphere("lens", radius=0.035, loc=F.p(p), segments=8, rings=5))
            g.cyl("searchbeam", F.p(p), F.p(p + d * beam), 0.035, r2=0.06 + beam * 0.055, verts=12, cap=False)
        sub = g.done()
        L.ik_groups.remove(sub)
        sub.parent = root
        sub.matrix_parent_inverse = Matrix.Identity(4)
        sub.location = (0, 0, 0)
        sub.rotation_euler = (0, 0, 0)
    L.ik_groups.append(root)
    return root


def _bm_of(objs):
    """cb 오브젝트들(월드 변환 포함)을 bmesh 하나로 모으고 오브젝트는 지운다."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    b = bmesh.new()
    for o in objs:
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.transform(o.matrix_world)
        b.from_mesh(me)
        eo.to_mesh_clear()
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(data, bpy.types.Mesh) and data.users == 0:
            bpy.data.meshes.remove(data)
    return b


def _push_bm(L, key, b, kind="fine"):
    me = bpy.data.meshes.new("tmp_push")
    b.to_mesh(me)
    L.bm(key, kind).from_mesh(me)
    bpy.data.meshes.remove(me)


def _halo_of(b, g):
    """번짐 껍질: 정점 법선 방향으로 g만큼 부풀리고 면을 뒤집는다 (안쪽 면만 보이게)."""
    h = b.copy()
    h.normal_update()
    for v in h.verts:
        v.co += v.normal * g
    bmesh.ops.reverse_faces(h, faces=h.faces)
    return h


def _human_bm(F, pose, H, lo):
    """인간 실루엣 한 자세를 bmesh로 (F의 월드 좌표). ell 부품의 넷째 값은 회전(도, 선택)."""
    objs = []
    for part in _human_parts(pose, H):
        if part[0] == "sph":
            if lo:
                continue
            o = cb.sphere("h", radius=part[2], loc=part[1], segments=6, rings=4)
        elif part[0] == "ell":
            o = cb.sphere("h", radius=1.0, loc=part[1], scale=tuple(part[2]), segments=8 if not lo else 6,
                          rings=5 if not lo else 4, rot=tuple(part[3]) if len(part) > 3 else (0, 0, 0))
        else:
            _, p0, p1, r0, r1, vv = part
            d = p1 - p0
            o = cb.cylinder("h", radius=r0, radius2=r1, depth=d.length, verts=6 if not lo else 5, cap=lo)
            q = d.normalized().to_track_quat("Z", "Y")
            o.matrix_world = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4()
        o.matrix_world = F.M @ o.matrix_basis
        objs.append(o)
    return _bm_of(objs)


def human(L, pos, yaw, *, pose="ready", H=1.82, tone=0, halo=True):
    """초점이 나간 인간 병사: 얼굴·휘장 없는 단색 UNLIT 덩어리 + 반투명 번짐 껍질 하나. tone 0(가까움)..2(멂)."""
    F = Frame(pos, yaw)
    b = _human_bm(F, pose, H, tone >= 2)
    _push_bm(L, f"hum_{tone}", b)
    if halo and tone < 2:
        hb = _halo_of(b, 0.05 if tone == 0 else 0.045)
        _push_bm(L, f"halo_{tone}", hb)
        hb.free()
    b.free()


def _flip(o):
    me = o.data
    b = bmesh.new()
    b.from_mesh(me)
    bmesh.ops.reverse_faces(b, faces=b.faces)
    b.to_mesh(me)
    b.free()


def vehicle_silhouette(L, pos, yaw, *, tone=1, kind="truck", halo=True):
    """인간 차량 실루엣 (표식 없음). kind: truck(군용 트럭) / apc(바퀴형 장갑차)."""
    F = Frame(pos, yaw)
    key, hk = f"hum_{tone}", f"halo_{tone}"
    parts = []
    if kind == "truck":
        parts += [("box", (0, -2.2, 1.35), (2.3, 1.9, 1.6)), ("box", (0, -3.35, 0.95), (2.2, 0.6, 0.8)),
                  ("box", (0, 1.1, 1.75), (2.4, 4.6, 0.25)), ("box", (0, 1.1, 2.2), (2.35, 4.4, 1.5)),
                  ("box", (0, 0.0, 0.85), (1.8, 7.0, 0.5))]
        wheels = [(-3.0,), (0.6,), (2.4,)]
    else:
        parts += [("box", (0, 0, 1.45), (2.7, 6.6, 1.5)), ("box", (0, -3.1, 1.05), (2.6, 1.0, 0.9)),
                  ("box", (0, 0.6, 2.45), (1.2, 1.4, 0.5)), ("cylx", (0, -0.9, 2.55), 0.08, 1.6)]
        wheels = [(-2.3,), (-0.8,), (0.8,), (2.3,)]
    for (wy,) in wheels:
        for sx in (1, -1):
            parts.append(("wheel", (sx * 1.15, wy, 0.55), 0.55))
    objs = []
    for p in parts:
        if p[0] == "box":
            o = cb.box("v", size=p[2], loc=p[1], bevel=0.12, bevel_segments=1)
        elif p[0] == "wheel":
            o = cb.cylinder("w", radius=p[2], depth=0.45, loc=p[1], rot=(0, 90, 0), verts=10)
        else:
            o = cb.cylinder("b", radius=p[2], depth=p[3], loc=(p[1][0], p[1][1] - p[3] / 2, p[1][2]),
                            rot=(90, 0, 0), verts=6)
        o.matrix_world = F.M @ o.matrix_basis
        objs.append(o)
    b = _bm_of(objs)
    _push_bm(L, key, b)
    if halo and tone < 2:
        hb = _halo_of(b, 0.07)
        _push_bm(L, hk, hb)
        hb.free()
    b.free()


def helicopter_silhouette(L, pos, yaw, *, tone=2, tilt=8.0):
    """하늘의 헬기 실루엣 (회전날개는 반투명 원판)."""
    F = Frame(pos, yaw)
    key = f"hum_{tone}"
    rot = (tilt, 0, 0)
    M = Matrix.Rotation(math.radians(tilt), 4, "X")

    def add(o):
        o.matrix_world = M @ o.matrix_basis
        F.obj(L, key, o, kind="fine")
    add(cb.sphere("hb", radius=1.0, loc=(0, 0, 0), scale=(1.2, 2.6, 1.15), segments=12, rings=8))
    add(cb.cylinder("tb", radius=0.32, radius2=0.18, depth=5.0, loc=(0, 4.2, 0.35), rot=(90, 0, 0), verts=8))
    add(cb.box("tf", size=(0.15, 0.9, 1.4), loc=(0, 6.6, 0.9)))
    add(cb.box("sk", size=(2.0, 3.4, 0.08), loc=(0, -0.2, -1.35)))
    add(cb.cylinder("mast", radius=0.12, depth=0.6, loc=(0, -0.2, 1.3), verts=6))
    o = cb.cylinder("rotor", radius=5.6, depth=0.04, loc=(0, -0.2, 1.6), verts=24)
    o.matrix_world = M @ o.matrix_basis
    F.obj(L, f"halo_{tone}", o, kind="fine")


# ------------------------------------------------------------------ camp structures

def corrugated_arc(L, F, length, R, *, t=0.06, seg=20, key="corr", rib="corr_d", ribs=1.4, x0=0.0, rib_seg=12):
    """퀀셋 막사 껍데기: 지역 X를 따라 뻗은 반원통 (바닥 z=0, 축 z=0). 골함석 줄은 원호 방향 띠."""
    outer = [(math.cos(math.pi * i / seg) * R, math.sin(math.pi * i / seg) * R) for i in range(seg + 1)]
    inner = [(math.cos(math.pi * i / seg) * (R - t), math.sin(math.pi * i / seg) * (R - t)) for i in range(seg + 1)]
    pts = outer + list(reversed(inner))
    # 지역 X 방향으로 돌출: 단면은 (Y,Z)
    L.extrude(key, [(-u, v) for (u, v) in pts], F.p(x0, 0, 0), F.d(1, 0, 0), length, up=F.d(0, 0, 1))
    n = int(length / ribs)
    for i in range(n + 1):
        x = x0 + 0.08 + (length - 0.16) * i / n
        outer2 = [(math.cos(math.pi * k / rib_seg) * (R + 0.035), math.sin(math.pi * k / rib_seg) * (R + 0.035))
                  for k in range(rib_seg + 1)]
        inner2 = [(math.cos(math.pi * k / rib_seg) * (R - 0.005), math.sin(math.pi * k / rib_seg) * (R - 0.005))
                  for k in reversed(range(rib_seg + 1))]
        L.extrude(rib, [(-u, v) for (u, v) in outer2 + inner2], F.p(x - 0.04, 0, 0), F.d(1, 0, 0), 0.08,
                  up=F.d(0, 0, 1), kind="detail")


def quonset(L, F, *, length=14.0, R=3.2, door_ends=(True, False), windows=3, interior=True, lit=False):
    """퀀셋(반원통) 막사. 지역 원점 = 앞(-X쪽) 끝벽 바닥 가운데, 길이 방향 +X."""
    corrugated_arc(L, F, length, R, x0=0.0)
    for end, x_end in ((0, 0.0), (1, length)):
        sgn = -1 if end == 0 else 1          # 바깥 방향 (지역 X)
        N = F.d(sgn, 0, 0)
        Ni = F.d(-sgn, 0, 0)
        # 끝벽은 껍데기 끝 고리 면보다 1 cm 안으로 (끝벽 반지름이 껍데기 안 반지름보다 커서 고리와 겹친다.
        # 같은 정점색 메시라 깊이 편향이 없으므로 표준 깊이 버퍼가 멀리서도 가르는 간격)
        x = x_end - sgn * 0.01               # 바깥 면
        xi = x - sgn * 0.08                  # 안쪽 면
        semi = [(math.cos(math.pi * i / 16) * (R - 0.04), math.sin(math.pi * i / 16) * (R - 0.04)) for i in range(17)]
        L.extrude("corr_d", semi, F.p(min(x, xi), 0, 0), F.d(1, 0, 0), 0.08, up=F.d(0, 0, 1))
        # 판자 이음 줄 (안·밖)
        for k in range(-3, 4):
            yy = k * 0.95
            top = math.sqrt(max(0.0, (R - 0.1) ** 2 - yy * yy))
            for (xx, nn) in ((x, N), (xi, Ni)):
                L.strip("od_d", F.p(xx, yy, 0.05), F.p(xx, yy, top), 0.03, nn, lift=0.004)
        # 데칼 층: 이음 줄 4 mm → 틀 12 mm → 문짝·유리 20 mm → 손잡이·창살 28 mm (층마다 8 mm)
        for (xx, nn, lift) in ((x, N, 0.012), (xi, Ni, 0.012)):
            if door_ends[end]:
                L.decal("wood_d", hw.rrect(1.06, 2.16, 0.02), F.p(xx, 0, 1.08), nn, lift=lift)
                L.decal("wood", hw.rrect(0.92, 2.04, 0.02), F.p(xx, 0, 1.08), nn, lift=lift + 0.008)
                L.decal("pipe", hw.circle(0.04, 8), F.p(xx, -0.36 * (1 if nn is N else -1), 1.05), nn,
                        lift=lift + 0.016)
            for wy in (-1.9, 1.9):
                L.decal("wood_d", hw.rrect(0.75, 0.7, 0.02), F.p(xx, wy, 1.6), nn, lift=lift)
                L.decal("lamp_on" if lit else "window_g", hw.rrect(0.62, 0.57, 0.02), F.p(xx, wy, 1.6), nn,
                        lift=lift + 0.008)
                L.strip("wood_d", F.p(xx, wy, 1.32), F.p(xx, wy, 1.88), 0.04, nn, lift=lift + 0.016)
        if door_ends[end]:
            F.box(L, "corr_d", x_end + sgn * 0.02, x_end + sgn * 0.5, -0.8, 0.8, 2.3, 2.36)
            F.box(L, "concrete", x, x_end + sgn * 0.7, -0.75, 0.75, -0.1, 0.16)
    # 옆 창: 지붕에서 튀어나온 작은 창 (dormer 대신 판)
    for i in range(windows):
        x = length * (i + 1) / (windows + 1)
        for sy in (1, -1):
            a = math.radians(68)
            P = F.p(x, sy * math.cos(a) * (R + 0.03), math.sin(a) * (R + 0.03))
            N = F.d(0, sy * math.cos(a), math.sin(a))
            L.decal("wood_d", hw.rrect(0.62, 0.9, 0.02), P, N, up=F.d(1, 0, 0), lift=0.02)
            L.decal("lamp_on" if lit else "window_g", hw.rrect(0.5, 0.78, 0.02), P, N, up=F.d(1, 0, 0), lift=0.035)
    # 바닥 기초
    F.box(L, "concrete_d", -0.15, length + 0.15, -R - 0.15, R + 0.15, -0.3, 0.06)
    if interior:
        F.box(L, "plank", 0.08, length - 0.08, -R + 0.1, R - 0.1, 0.06, 0.1)
        for i in range(int(length / 0.6)):
            x = 0.1 + i * 0.6
            L.strip("wood_d", F.p(x, -R + 0.15, 0.104), F.p(x, R - 0.15, 0.104), 0.025, (0, 0, 1), lift=0.002)


def chain_fence(L, F, length, *, h=2.6, post=3.0, dense=None, barbed=True, concertina=None, net=True, top=True,
                key_post="pipe", gate_gaps=(), sp=0.22, barbs=True):
    """철망 울타리: 지역 X를 따라 0..length, 철망 면은 y=0. 바깥(수용소 밖) = -Y.

    dense: (x0, x1) 구간은 촘촘한 마름모 (카메라 가까이). concertina: (x0, x1) 윤형 철조망 구간.
    """
    n = max(1, round(length / post))
    for i in range(n + 1):
        x = length * i / n
        if any(g0 < x < g1 for g0, g1 in gate_gaps):
            continue
        F.cyl(L, key_post, (x, 0, -0.3), (x, 0, h + 0.09), 0.045, verts=5, cap=False)
        if barbed:
            # 바깥쪽으로 45° 기운 팔
            F.cyl(L, key_post, (x, 0, h), (x, -0.42, h + 0.42), 0.025, verts=4, kind="detail", cap=False)
    if top:
        F.cyl(L, key_post, (0, 0, h - 0.04), (length, 0, h - 0.04), 0.03, verts=6, kind="detail")
        F.cyl(L, key_post, (0, 0, 0.08), (length, 0, 0.08), 0.02, verts=5, kind="detail")
    # 철망 면 (반투명) + 마름모 선
    segs = [(0.0, length)]
    for g0, g1 in gate_gaps:
        segs = [s for a, b in segs for s in ((a, g0), (g1, b)) if s[1] - s[0] > 0.05]
    N = F.d(0, -1, 0)
    for (s0, s1) in segs:
        if net:
            L.poly("fence_net", [F.p(s0, 0, 0.05), F.p(s1, 0, 0.05), F.p(s1, 0, h - 0.05), F.p(s0, 0, h - 0.05)],
                   normal=N)
        sp_all = sp
        ranges = [(s0, s1, sp_all)]
        if dense:
            d0, d1 = max(s0, dense[0]), min(s1, dense[1])
            if d1 > d0:
                ranges = [(s0, d0, sp_all), (d0, d1, 0.09), (d1, s1, sp_all)]
        for (a0, a1, sp) in ranges:
            if a1 - a0 < 0.05:
                continue
            _diamonds(L, F, a0, a1, 0.05, h - 0.05, sp, 0.012 if sp < 0.1 else 0.016)
    if barbed:
        for k in range(3):
            o = 0.14 * (k + 1)
            F.cyl(L, "barbed", (0, -o, h + o), (length, -o, h + o), 0.008, verts=3, kind="fine", cap=False)
            for i in range(int(length / 0.5) if barbs else 0):
                x = 0.2 + i * 0.5
                for sz in (1, -1):
                    L.strip("barbed", F.p(x - 0.035, -o, h + o - sz * 0.03), F.p(x + 0.035, -o, h + o + sz * 0.03),
                            0.01, F.d(0, -1, 0), lift=0.0)
    if concertina:
        c0, c1 = concertina
        _concertina(L, F, c0, c1, (0, -0.3, h + 0.55), 0.32)


def _diamonds(L, F, x0, x1, z0, z1, sp, w):
    """마름모 철망 선 (45° 두 방향 띠)."""
    N = F.d(0, -1, 0)
    H = z1 - z0
    for sgn in (1, -1):
        for k in range(math.floor((x0 - H) / sp), math.ceil((x1 + H) / sp) + 1):
            u0 = k * sp     # 선이 z0에서 지나는 x
            # 선: x = u0 + sgn*(z - z0)  (sgn=1: 오른쪽 위로)
            pts = []
            for (za, xa) in ((z0, u0), (z1, u0 + sgn * H)):
                pts.append((xa, za))
            # 구간 [x0, x1]로 자르기
            (xa, za), (xb, zb) = pts
            if xb == xa:
                continue
            ta = (x0 - xa) / (xb - xa)
            tb = (x1 - xa) / (xb - xa)
            t0, t1 = max(0.0, min(ta, tb)), min(1.0, max(ta, tb))
            if t1 <= t0:
                continue
            pa = (xa + (xb - xa) * t0, za + (zb - za) * t0)
            pb = (xa + (xb - xa) * t1, za + (zb - za) * t1)
            # 반투명 철망 판(y=0)보다 1.5 cm 앞: 같은 편향 등급이라 표준 깊이 버퍼로 80 m 넘게까지 갈리게
            L.strip("barbed", F.p(pa[0], -0.015, pa[1]), F.p(pb[0], -0.015, pb[1]), w, N, lift=0.0)


def _concertina(L, F, x0, x1, c, r, pitch=0.28, seg=8):
    """윤형 철조망: 지역 X를 따라 도는 나선 (가는 관)."""
    n = int((x1 - x0) / pitch * seg)
    prev = None
    for i in range(n + 1):
        t = i / seg
        a = t * 2 * math.pi
        x = x0 + t * pitch + math.sin(a) * 0.05
        p = F.p(x, c[1] + math.cos(a) * r, c[2] + math.sin(a) * r)
        if prev is not None:
            L.cyl("barbed", prev, p, 0.008, verts=3, kind="fine", cap=False)
        prev = p


def watchtower(L, F, *, h=6.5, top=2.6, light=None, light_on=False, aim=(0, -1, -0.35), sweep=(-40, 40)):
    """감시탑: 네 다리 + 가새 + 지붕 있는 망루 + 사다리 + 서치라이트. 지역 원점 = 바닥 가운데."""
    s0, s1 = 1.5, 1.05   # 다리 아래·위 반폭
    for sx in (1, -1):
        for sy in (1, -1):
            F.cyl(L, "wood_d", (sx * s0, sy * s0, -0.3), (sx * s1, sy * s1, h), 0.1, verts=6)
    for lv in (0.25, 0.5, 0.75):
        z = h * lv
        s = s0 + (s1 - s0) * lv
        for (ax, ay, bx, by) in ((1, 1, -1, 1), (-1, 1, -1, -1), (-1, -1, 1, -1), (1, -1, 1, 1)):
            F.cyl(L, "wood", (ax * s, ay * s, z), (bx * s, by * s, z), 0.05, verts=5, kind="detail")
    for (ax, ay, bx, by) in ((1, -1, -1, -1), (1, 1, -1, 1)):
        for lv0, lv1 in ((0.0, 0.5), (0.5, 1.0)):
            sa, sb = s0 + (s1 - s0) * lv0, s0 + (s1 - s0) * lv1
            F.cyl(L, "wood", (ax * sa, ay * sa, h * lv0 + 0.1), (bx * sb, by * sb, h * lv1 - 0.1), 0.04, verts=5,
                  kind="detail")
    # 사다리
    for sx in (0.25, -0.25):
        F.cyl(L, "wood", (sx, -s0 - 0.1, 0), (sx, -s1 - 0.05, h), 0.035, verts=5, kind="detail")
    for i in range(1, int(h / 0.32)):
        t = i * 0.32 / h
        y = -(s0 + 0.1) + (s0 - s1 + 0.05) * t
        F.cyl(L, "wood", (-0.25, y, i * 0.32), (0.25, y, i * 0.32), 0.022, verts=4, kind="detail")
    # 망루
    W = 1.4
    F.box(L, "plank", -W, W, -W, W, h, h + 0.15)
    for sx in (1, -1):
        F.box(L, "wood_d", -W, W, sx * W - 0.06, sx * W + 0.06, h + 0.15, h + 1.05)
        F.box(L, "wood_d", sx * W - 0.06, sx * W + 0.06, -W, W, h + 0.15, h + 1.05)
    for sx in (1, -1):
        for sy in (1, -1):
            F.cyl(L, "wood_d", (sx * (W - 0.08), sy * (W - 0.08), h + 1.0), (sx * (W - 0.08), sy * (W - 0.08),
                                                                           h + top), 0.06, verts=6)
    # 지붕 (낮은 피라미드)
    rz = h + top
    b = L.bm("roof")
    v = [b.verts.new(F.p(x, y, rz)) for x, y in ((-W - 0.35, -W - 0.35), (W + 0.35, -W - 0.35), (W + 0.35, W + 0.35),
                                                  (-W - 0.35, W + 0.35))]
    apex = b.verts.new(F.p(0, 0, rz + 0.8))
    for i in range(4):
        b.faces.new((v[i], v[(i + 1) % 4], apex))
    b.faces.new(list(reversed(v)))
    # 서치라이트
    if light:
        searchlight(L, light, F.p(0, -W + 0.15, h + 1.05), aim=F.d(*aim), on=light_on, sweep=sweep)


def searchlight(L, lid, base, *, aim=(0, -1, -0.3), on=False, sweep=(-40, 40), beam_len=26.0, beam_r=2.6,
                r=0.32, hz=0.11):
    """서치라이트: 받침(고정) + 머리 묶음 LIGHT_<lid>(피벗 = 받침 위 회전축, 지역 -Y = 비추는 방향).

    머리 안에 하우징·렌즈(UNLIT)·빛기둥(반투명, 자식 LIGHT_<lid>_beam 메시)이 있다. 미션은 묶음을 Z(three.js Y)로
    sweep 범위 안에서 흔든다. on=0이면 렌즈를 꺼진 색으로 바꾸고 빛기둥을 숨긴다.
    """
    B = Vector(base)
    L.cyl("pipe", tuple(B), tuple(B + Vector((0, 0, 0.3))), 0.07, verts=8, kind="detail")
    A = Vector(aim).normalized()
    yaw = math.atan2(A.x, -A.y)
    pitch = -math.asin(max(-1, min(1, A.z)))
    piv = B + Vector((0, 0, 0.42))
    g = Group(L, f"LIGHT_{lid}", pivot=tuple(piv), rot=(0, 0, yaw),
              props={"kind": "searchlight", "on": 1 if on else 0, "sweep": f"{sweep[0]},{sweep[1]}", "sweepHz": hz,
                     "color": EGLOW["search"], "group": "searchlight"})
    Mx = Matrix.Translation(piv) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "X")
    # 요크
    for sx in (1, -1):
        g.box("pipe", sx * (r + 0.02), sx * (r + 0.07), -0.05, 0.05, -0.12, 0.05, matrix=Mx)
    # 하우징 (지역 -Y가 앞)
    o = cb.cylinder("hs", radius=r * 0.85, radius2=r, depth=0.6, loc=(0, 0.05, 0), rot=(90, 0, 0), verts=16)
    o.matrix_world = Mx @ o.matrix_basis
    g.obj("od", o)
    o = cb.cylinder("rim", radius=r + 0.03, depth=0.07, loc=(0, -0.26, 0), rot=(90, 0, 0), verts=16)
    o.matrix_world = Mx @ o.matrix_basis
    g.obj("pipe", o, kind="detail")
    o = cb.cylinder("lens", radius=r - 0.03, depth=0.02, loc=(0, -0.3, 0), rot=(90, 0, 0), verts=16)
    o.matrix_world = Mx @ o.matrix_basis
    g.obj("search" if on else "screen_off", o)
    for i in range(3):
        o = cb.cylinder("fin", radius=r + 0.02, depth=0.025, loc=(0, 0.12 + i * 0.07, 0), rot=(90, 0, 0), verts=16)
        o.matrix_world = Mx @ o.matrix_basis
        g.obj("od_d", o, kind="detail")
    if on:
        o = cb.cylinder("beam", radius=r * 0.8, radius2=beam_r, depth=beam_len, loc=(0, -0.3 - beam_len / 2, 0),
                        rot=(90, 0, 0), verts=16, cap=False)
        o.matrix_world = Mx @ o.matrix_basis
        g.obj("searchbeam", o)
    root = g.done()
    return root


def alarm_light(L, lid, base, normal=(0, 0, 1), *, on=True, r=0.16, beams=True):
    """회전 경광등: 받침 + LIGHT_<lid> 묶음(빨간 렌즈 + 회전하는 빛살 2개). spin 속성으로 빛살이 돈다."""
    B = Vector(base)
    L.cyl("pipe", tuple(B), tuple(B + Vector((0, 0, 0.08))), r + 0.03, verts=10, kind="detail")
    g = Group(L, f"LIGHT_{lid}", pivot=tuple(B + Vector((0, 0, 0.08))),
              props={"kind": "alarm", "on": 1 if on else 0, "emissiveToggle": 1, "group": "alarm",
                     "blink": 0.8, "color": lk.GLOW["alert"], "spin": "0,240,0"})
    o = cb.cylinder("lens", radius=r, radius2=r * 0.75, depth=0.22, loc=tuple(B + Vector((0, 0, 0.19))), verts=12)
    g.obj("alert" if on else "red_d", o)
    o = cb.sphere("cap", radius=r * 0.75, loc=tuple(B + Vector((0, 0, 0.3))), scale=(1, 1, 0.6), segments=12, rings=5)
    g.obj("alert" if on else "red_d", o)
    if on and beams:
        for sgn in (1, -1):
            o = cb.cylinder("ab", radius=0.06, radius2=1.1, depth=5.0, loc=(0, sgn * 2.6, 0), rot=(-90 * sgn, 0, 0), verts=10,
                            cap=False)
            o.matrix_world = Matrix.Translation(B + Vector((0, 0, 0.19))) @ o.matrix_basis
            g.obj("alarm_beam", o)
    return g.done()


# ------------------------------------------------------------------ workshop / barracks furniture

def workbench(L, F, length, *, depth=0.85, h=0.86, shelf=True, back=True, key="bench", leg="pipe"):
    """긴 작업대 (인간 높이 0.86 m). 지역 원점 = 앞 가장자리 가운데 바닥, 길이 방향 X, 작업자는 -Y쪽."""
    hl = length / 2
    F.box(L, key, -hl, hl, 0, depth, h - 0.06, h)
    F.box(L, "bench_d", -hl, hl, -0.01, 0.03, h - 0.09, h - 0.06, kind="detail")
    n = max(2, round(length / 1.6) + 1)
    for i in range(n):
        x = -hl + 0.08 + (length - 0.16) * i / (n - 1)
        for y in (0.08, depth - 0.08):
            F.box(L, leg, x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0, h - 0.06)
    if shelf:
        F.box(L, "bench_d", -hl + 0.055, hl - 0.055, 0.055, depth - 0.055, 0.18, 0.22)   # 다리 바깥 면보다 5 mm 안
    if back:
        # 뒤판 + 공구걸이
        F.box(L, "bench_d", -hl, hl, depth - 0.04, depth, h, h + 0.55)
        for i in range(int(length / 0.35)):
            x = -hl + 0.2 + i * 0.35
            F.cyl(L, "pipe", (x, depth - 0.04, h + 0.42), (x, depth - 0.12, h + 0.44), 0.008, verts=4, kind="fine")


def step_crate(L, F, x, y, *, h=0.28, w=0.5):
    """엘프가 인간 작업대에 닿으려고 올라서는 나무 상자 (윗면 z = h)."""
    F.box(L, "wood", x - w / 2, x + w / 2, y - w * 0.4, y + w * 0.4, 0, h)
    for zz in (h * 0.33, h * 0.66):
        F.box(L, "wood_d", x - w / 2 - 0.005, x + w / 2 + 0.005, y - w * 0.4 - 0.005, y + w * 0.4 + 0.005, zz - 0.012,
              zz + 0.012, kind="detail")


def parts_bin(L, F, x, y, z, *, w=0.28, d=0.4, h=0.14, key="od", fill="pcb"):
    F.box(L, key, x - w / 2, x + w / 2, y - d / 2, y + d / 2, z, z + h)
    F.box(L, fill, x - w / 2 + 0.02, x + w / 2 - 0.02, y - d / 2 + 0.02, y + d / 2 - 0.02, z + h - 0.03, z + h - 0.01,
          kind="detail")


def pcb(L, F, x, y, z, *, w=0.16, d=0.1, rot=0.0, chips=3, seed=0):
    """칩이 박힌 초록 기판 (작업대 위). 금색 핀 줄과 검은 칩."""
    rnd = random.Random(seed)
    S = F.sub(x, y, z, rot)
    S.box(L, "pcb", -w / 2, w / 2, -d / 2, d / 2, 0, 0.008, kind="detail")
    for i in range(chips):
        cx = -w / 2 + w * (i + 0.5) / chips + rnd.uniform(-0.01, 0.01)
        cw = rnd.uniform(0.025, 0.04)
        S.box(L, "chip", cx - cw / 2, cx + cw / 2, -0.02, 0.02, 0.008, 0.016, kind="fine")
        for sy in (-1, 1):
            L.strip("copper", S.p(cx - cw / 2, sy * 0.023, 0.0085), S.p(cx + cw / 2, sy * 0.023, 0.0085), 0.006,
                    (0, 0, 1), lift=0.0005)


def santa_doll(L, F, x, y, z, *, s=1.0, rot=0.0, stage="done", lie=False, V=7, kind="detail"):
    """산타 인형 (원작: 크리스마스 장난감 연중 생산). stage: body(몸통만) / head(머리만) / done.

    높이 약 0.22 m × s. 지역 원점 = 인형 바닥 가운데.
    """
    S = F.sub(x, y, z, rot)
    if lie:
        S = Frame(S.o, S.yaw)
    k = s
    pieces = []
    if stage in ("done", "body"):
        pieces += [("toy_red", cb.cylinder("b", radius=0.06 * k, radius2=0.045 * k, depth=0.12 * k,
                                            loc=(0, 0, 0.06 * k), verts=V)),
                   ("toy_white", cb.cylinder("hem", radius=0.063 * k, depth=0.018 * k, loc=(0, 0, 0.01 * k), verts=V)),
                   ("can_k", cb.cylinder("belt", radius=0.054 * k, depth=0.014 * k, loc=(0, 0, 0.075 * k), verts=V)),
                   ("toy_gold", cb.box("buckle", size=(0.022 * k, 0.01 * k, 0.016 * k),
                                        loc=(0, -0.053 * k, 0.075 * k)))]
        for sx in (1, -1):
            pieces.append(("toy_red", cb.sphere("arm", radius=0.022 * k, loc=(sx * 0.055 * k, -0.01 * k, 0.085 * k),
                                                scale=(1, 1, 1.5), segments=max(5, V - 4), rings=max(3, V // 4 + 1))))
    if stage in ("done", "head"):
        hz = 0.155 * k if stage == "done" else 0.04 * k
        pieces += [("toy_skin", cb.sphere("h", radius=0.042 * k, loc=(0, 0, hz), segments=V, rings=max(4, V // 2))),
                   ("toy_white", cb.sphere("beard", radius=0.04 * k, loc=(0, -0.018 * k, hz - 0.022 * k),
                                           scale=(1.05, 0.8, 1.0), segments=max(5, V - 2), rings=4)),
                   ("toy_red", cb.cylinder("hat", radius=0.044 * k, radius2=0.004 * k, depth=0.07 * k,
                                           loc=(0, 0.008 * k, hz + 0.05 * k), rot=(12, 0, 0), verts=V)),
                   ("toy_white", cb.cylinder("brim", radius=0.046 * k, depth=0.014 * k, loc=(0, 0, hz + 0.022 * k),
                                             verts=V)),
                   ("toy_white", cb.sphere("pom", radius=0.013 * k, loc=(0, 0.02 * k, hz + 0.088 * k), segments=5,
                                           rings=3))]
    for key, o in pieces:
        if lie:
            o.matrix_world = Matrix.Rotation(math.radians(90), 4, "X") @ o.matrix_basis
        S.obj(L, key, o, kind=kind)


def gift(L, F, x, y, z, *, w=0.3, d=0.3, h=0.22, rot=0.0, wrap="toy_red", ribbon="ribbon", bow=True):
    """포장된 선물 상자 (리본 십자 + 나비매듭)."""
    S = F.sub(x, y, z, rot)
    S.box(L, wrap, -w / 2, w / 2, -d / 2, d / 2, 0, h)
    t = min(w, d) * 0.12
    S.box(L, ribbon, -t / 2, t / 2, -d / 2 - 0.004, d / 2 + 0.004, -0.002, h + 0.004, kind="detail")
    S.box(L, ribbon, -w / 2 - 0.004, w / 2 + 0.004, -t / 2, t / 2, -0.002, h + 0.004, kind="detail")
    if bow:
        for sx in (1, -1):
            o = cb.sphere("bow", radius=t * 1.2, loc=(sx * t * 1.1, 0, h + t * 0.6), scale=(1.3, 0.6, 0.7),
                          segments=5, rings=3, rot=(0, sx * 25, 0))
            S.obj(L, ribbon, o, kind="detail")


def cardboard(L, F, x, y, z, *, w=0.5, d=0.4, h=0.35, rot=0.0, open_=False, label=None):
    S = F.sub(x, y, z, rot)
    S.box(L, "box", -w / 2, w / 2, -d / 2, d / 2, 0, h)
    S.box(L, "tape", -0.04, 0.04, -d / 2 - 0.003, d / 2 + 0.003, h - 0.002, h + 0.003, kind="fine")
    S.box(L, "tape", -0.04, 0.04, -d / 2 - 0.003, -d / 2 + 0.002, h - 0.12, h, kind="fine")
    if open_:
        for sy in (1, -1):
            S.rbox(L, "box_d", (0, sy * (d / 2 + 0.09), h + 0.06), (w - 0.02, 0.18, 0.01), (sy * 60, 0, 0))
    if label:
        L.text("ink", label, min(w, h) * 0.18, S.p(0, -d / 2, h * 0.5), S.d(0, -1, 0), lift=0.004)


def drink_can(L, F, x, y, z, *, rot=0.0, lie=False):
    """'붕붕드링크' 캔 (원작: 포로 시절 강제로 마신 카페인 음료). 디자인은 새로 만든 노랑·검정 캔."""
    S = F.sub(x, y, z, rot)
    M = Matrix.Rotation(math.radians(90), 4, "X") if lie else Matrix.Identity(4)
    zc = 0.033 if lie else 0.06
    for key, o in (("can_y", cb.cylinder("c", radius=0.033, depth=0.115, loc=(0, 0, 0), verts=12)),
                   ("can_k", cb.cylinder("band", radius=0.035, depth=0.03, loc=(0, 0, 0.01), verts=12)),   # 몸통보다 2 mm
                   ("solder", cb.cylinder("lid", radius=0.03, depth=0.008, loc=(0, 0, 0.06), verts=12))):
        o.matrix_world = Matrix.Translation((0, 0, zc)) @ M @ o.matrix_basis
        S.obj(L, key, o, kind="detail")


def bunk_bed(L, F, *, w=0.95, length=2.0, h1=0.42, h2=1.5, sleeper=(False, False), messy=0, seed=0):
    """이층 침대 (인간 규격 철제). 지역 원점 = 침대 한가운데 바닥, 길이 방향 X, 통로는 -Y쪽."""
    rnd = random.Random(seed)
    hl, hw_ = length / 2, w / 2
    for sx in (1, -1):
        for sy in (1, -1):
            F.cyl(L, "pipe", (sx * hl, sy * hw_, 0), (sx * hl, sy * hw_, h2 + 0.55), 0.028, verts=5)
    for z in (h1, h2):
        for sy in (1, -1):
            F.cyl(L, "pipe", (-hl, sy * hw_, z), (hl, sy * hw_, z), 0.022, verts=4, kind="detail", cap=False)
        for sx in (1, -1):
            F.cyl(L, "pipe", (sx * hl, -hw_, z), (sx * hl, hw_, z), 0.022, verts=4, kind="detail", cap=False)
            F.cyl(L, "pipe", (sx * hl, -hw_, z + 0.35), (sx * hl, hw_, z + 0.35), 0.02, verts=4, kind="detail",
                  cap=False)
        F.box(L, "mattress", -hl + 0.04, hl - 0.04, -hw_ + 0.04, hw_ - 0.04, z + 0.01, z + 0.12)
        F.rbox(L, "pillow", (hl - 0.28, 0, z + 0.16), (0.34, w * 0.6, 0.1), (0, 0, rnd.uniform(-6, 6)))
        # 담요 (반쯤 접힘)
        bx0 = -hl + 0.05
        bx1 = hl - 0.55 - rnd.uniform(0, 0.3) * messy
        F.box(L, "blanket", bx0, bx1, -hw_ + 0.02, hw_ - 0.02, z + 0.12, z + 0.16)
        F.box(L, "blanket_d", bx1 - 0.18, bx1, -hw_ + 0.01, hw_ - 0.01, z + 0.16, z + 0.22, kind="detail")
    # 사다리
    for i in range(4):
        z = h1 + 0.27 * (i + 1) - 0.1
        F.cyl(L, "pipe", (-hl + 0.12, -hw_, z), (-hl + 0.42, -hw_, z), 0.015, verts=4, kind="detail", cap=False)
    F.cyl(L, "pipe", (-hl + 0.42, -hw_, h1), (-hl + 0.42, -hw_, h2 + 0.35), 0.02, verts=5, kind="detail")


def hanging_lamp(L, pos, *, drop=0.9, on=True, r=0.2):
    x, y, z = pos
    L.cyl("cable", (x, y, z), (x, y, z - drop), 0.008, verts=4, kind="fine")
    L.cyl("lampshade", (x, y, z - drop), (x, y, z - drop - 0.14), 0.04, verts=10, r2=r)
    L.obj("lamp_on" if on else "lamp_off", cb.sphere("bulb", radius=0.06, loc=(x, y, z - drop - 0.15),
                                                     segments=8, rings=5))


def shelf_unit(L, F, *, w=1.6, d=0.45, h=2.0, levels=4, seed=0, fill=("box", "od", "toy_red", "toy_green")):
    rnd = random.Random(seed)
    for sx in (-w / 2, w / 2):
        for sy in (0.02, d - 0.02):
            F.box(L, "pipe", sx - 0.025, sx + 0.025, sy - 0.02, sy + 0.02, 0, h)
    for i in range(levels):
        z = 0.12 + (h - 0.2) * i / (levels - 1)
        F.box(L, "plank", -w / 2, w / 2, 0.005, d - 0.005, z, z + 0.03)   # 기둥 바깥 면보다 5 mm 안
        if i < levels - 1:
            x = -w / 2 + 0.05
            while x < w / 2 - 0.25:
                bw = rnd.uniform(0.22, 0.42)
                bh = rnd.uniform(0.15, 0.3)
                key = rnd.choice(fill)
                F.box(L, key, x, x + bw * 0.92, 0.05, d - 0.05, z + 0.03, z + 0.03 + bh)
                if key in ("toy_red", "toy_green"):
                    F.box(L, "ribbon", x + bw * 0.4, x + bw * 0.52, 0.04, d - 0.04, z + 0.029, z + 0.035 + bh,
                          kind="detail")
                x += bw


def board(L, F, x, z, w, h, lines, *, key="chalk", frame="wood_d", text_key="chalk_w", size=0.09, y=0.0):
    """벽 칠판·게시판 (지역 y=0 벽면, -Y가 앞). lines = [(문자열, 상대 높이, 크기 배율, 키), ...]."""
    F.box(L, frame, x - w / 2 - 0.04, x + w / 2 + 0.04, y - 0.05, y, z - h / 2 - 0.04, z + h / 2 + 0.04)
    F.box(L, key, x - w / 2, x + w / 2, y - 0.06, y - 0.05, z - h / 2, z + h / 2)
    for s, rz, sc, tk in lines:
        L.text(tk or text_key, s, size * sc, F.p(x, y - 0.06, z + rz * h / 2), F.d(0, -1, 0), up=F.d(0, 0, 1),
               lift=0.004)


def wall_x(L, F, y, x0, x1, h, *, t=0.12, openings=(), key="corr", inner=+1, girts=(1.25, 2.65), girt_key="wood_d",
           col_pitch=3.0, col_key="wood_d"):
    """지역 X를 따라 뻗은 벽(면 y, 두께 t는 바깥쪽). openings = [(xa, xb, za, zb), ...]. inner = 방 안쪽 방향(+1/-1)."""
    yo = y - inner * t
    ys = sorted((y, yo))
    cuts = sorted(openings)
    xs = [x0]
    for (xa, xb, za, zb) in cuts:
        xs += [xa, xb]
    xs.append(x1)
    for i in range(0, len(xs), 2):
        a, b = xs[i], xs[i + 1]
        if b - a > 1e-3:
            F.box(L, key, a, b, ys[0], ys[1], 0, h)
    for (xa, xb, za, zb) in cuts:
        if za > 0.01:
            F.box(L, key, xa, xb, ys[0], ys[1], 0, za)
        if zb < h - 0.01:
            F.box(L, key, xa, xb, ys[0], ys[1], zb, h)
    # 안쪽 골함석 줄 (세로 띠) + 띠장 + 기둥
    N = F.d(0, inner, 0)
    k = x0 + 0.3
    while k < x1 - 0.1:
        if not any(xa - 0.05 < k < xb + 0.05 and True for (xa, xb, za, zb) in cuts):
            L.strip("corr_d", F.p(k, y + inner * 0.002, 0.05), F.p(k, y + inner * 0.002, h - 0.05), 0.05, N, lift=0.0)
        k += 0.45
    for gz in girts:
        segs = [(x0, x1)]
        for (xa, xb, za, zb) in cuts:
            if za < gz + 0.08 and zb > gz:
                segs = [s2 for (p, q) in segs for s2 in ((p, xa), (xb, q)) if s2[1] - s2[0] > 0.05]
        for (p, q) in segs:
            F.box(L, girt_key, p, q, y + inner * 0.0, y + inner * 0.08, gz, gz + 0.14, kind="detail")
    n = max(1, round((x1 - x0) / col_pitch))
    for i in range(n + 1):
        xc = x0 + (x1 - x0) * i / n
        if any(xa - 0.15 < xc < xb + 0.15 for (xa, xb, za, zb) in cuts):
            continue
        # 양 끝 기둥은 벽 끝 안쪽으로: 모서리에서 옆 벽 끝면과 같은 평면에 놓이지 않게
        xc = min(max(xc, x0 + 0.09), x1 - 0.09)
        F.box(L, col_key, xc - 0.09, xc + 0.09, y + inner * 0.0, y + inner * 0.16, 0, h)


def window(L, F, x, y, z0, z1, w, *, inner=+1, pane="sunwin", t=0.14, mull=2, sill=True, beam=None, beam_dir=None,
           beam_world=None):
    """창: 틀 + 창살 + 발광 유리(UNLIT). beam: 빛살 반투명 키(바닥까지 비스듬히)."""
    N = F.d(0, inner, 0)
    yi = y + inner * 0.01
    yo = y - inner * t
    ys = sorted((yi, yo))
    F.box(L, "wood_d", x - w / 2 - 0.06, x + w / 2 + 0.06, ys[0], ys[1], z0 - 0.06, z0)
    F.box(L, "wood_d", x - w / 2 - 0.06, x + w / 2 + 0.06, ys[0], ys[1], z1, z1 + 0.06)
    for sx in (-1, 1):
        F.box(L, "wood_d", x + sx * w / 2 - (0.06 if sx < 0 else 0), x + sx * w / 2 + (0.06 if sx > 0 else 0),
              ys[0], ys[1], z0, z1)
    # 유리 (바깥 쪽 깊숙이)
    yp = y - inner * t * 0.6
    L.poly(pane, [F.p(x - w / 2, yp, z0), F.p(x + w / 2, yp, z0), F.p(x + w / 2, yp, z1), F.p(x - w / 2, yp, z1)],
           normal=N)
    for i in range(1, mull + 1):
        xm = x - w / 2 + w * i / (mull + 1)
        F.box(L, "wood_d", xm - 0.02, xm + 0.02, yp - 0.02, yp + 0.02, z0, z1, kind="detail")
    F.box(L, "wood_d", x - w / 2, x + w / 2, yp - 0.02, yp + 0.02, (z0 + z1) / 2 - 0.02, (z0 + z1) / 2 + 0.02,
          kind="detail")
    if sill:
        # 창턱 윗면은 아래 틀 윗면(z0)보다 4 mm 위
        F.box(L, "wood", x - w / 2 - 0.1, x + w / 2 + 0.1, y, y + inner * 0.16, z0 - 0.05, z0 + 0.004, kind="detail")
    if beam:
        d = Vector(beam_dir or (0.25, inner * 1.0, -0.8)).normalized()
        quad = [Vector(F.p(x - w / 2, yp, z0)), Vector(F.p(x + w / 2, yp, z0)), Vector(F.p(x + w / 2, yp, z1)),
                Vector(F.p(x - w / 2, yp, z1))]
        Dw = Vector(beam_world).normalized() if beam_world is not None else Vector(F.d(*d))
        far = []
        for q in quad:
            tt = (q.z - 0.02) / max(0.05, -Dw.z)
            far.append(q + Dw * tt)
        b = L.bm(beam, "fine")
        vn = [b.verts.new(q) for q in quad]
        vf = [b.verts.new(q) for q in far]
        for i in range(4):
            j = (i + 1) % 4
            b.faces.new((vn[i], vn[j], vf[j], vf[i]))
        b.faces.new(vf)


def shed(L, F, w, d, h, *, ridge=1.6, wins=(), doors=(), pane="sunwin", beam=None, beam_dir=None, lamps=(),
         lamp_on=True, floor_key="concrete", truss_pitch=3.0, beam_sides="nsew"):
    """작업장 창고 (안에서 찍는 방). 지역 원점 = 바닥 가운데. 방은 x ±w/2, y ±d/2, 벽 높이 h, 박공지붕.

    wins: [(벽 'n'/'s'/'e'/'w', 중심, z0, z1, 폭), ...], doors: [(벽, 중심, 폭, 높이), ...]
    lamps: [(x, y), ...] 트러스에 매단 전등.
    """
    hw_, hd = w / 2, d / 2
    F.box(L, floor_key, -hw_ - 0.2, hw_ + 0.2, -hd - 0.2, hd + 0.2, -0.25, 0.0)
    # 바닥 이음 줄
    for i in range(1, int(w / 3)):
        xx = -hw_ + i * 3.0
        L.strip("concrete_d", F.p(xx, -hd, 0.0), F.p(xx, hd, 0.0), 0.03, (0, 0, 1), lift=0.004)
    for i in range(1, int(d / 3) + 1):
        yy = -hd + i * 3.0
        if yy < hd:
            L.strip("concrete_d", F.p(-hw_, yy, 0.0), F.p(hw_, yy, 0.0), 0.03, (0, 0, 1), lift=0.004)
    ops = {"n": [], "s": [], "e": [], "w": []}
    for (side, c, z0, z1, ww) in wins:
        ops[side].append((c - ww / 2 - 0.06, c + ww / 2 + 0.06, z0 - 0.06, z1 + 0.06))
    for (side, c, ww, hh) in doors:
        ops[side].append((c - ww / 2, c + ww / 2, 0.0, hh))
    wall_x(L, F, hd, -hw_, hw_, h, openings=ops["n"], inner=-1)
    wall_x(L, F, -hd, -hw_, hw_, h, openings=ops["s"], inner=+1)
    Fe = F.sub(hw_, 0, 0, 90)      # 동쪽 벽: 지역 X가 월드 +Y
    Fw = F.sub(-hw_, 0, 0, -90)
    wall_x(L, Fe, 0.0, -hd, hd, h, openings=[(a, b, c, d2) for (a, b, c, d2) in ops["e"]], inner=+1)
    wall_x(L, Fw, 0.0, -hd, hd, h, openings=[(-b, -a, c, d2) for (a, b, c, d2) in ops["w"]], inner=+1)
    # 빛살 방향(beam_dir, 창고 지역 좌표)을 월드로. 벽마다 방 안쪽으로 들어오게 법선 성분을 뒤집는다
    bd = Vector(F.d(*(beam_dir or (0.3, -1.0, -0.8)))).normalized()
    inward = {"n": Vector(F.d(0, -1, 0)), "s": Vector(F.d(0, 1, 0)), "e": Vector(F.d(-1, 0, 0)),
              "w": Vector(F.d(1, 0, 0))}

    def bw(side):
        n = inward[side]
        k = bd.dot(n)
        return bd if k > 0.15 else bd - n * (2 * k) if k < -0.15 else bd + n * 0.8
    for (side, c, z0, z1, ww) in wins:
        bm_ = beam if side in beam_sides else None
        if side == "n":
            window(L, F, c, hd, z0, z1, ww, inner=-1, pane=pane, beam=bm_, beam_world=bw(side))
        elif side == "s":
            window(L, F, c, -hd, z0, z1, ww, inner=+1, pane=pane, beam=bm_, beam_world=bw(side))
        elif side == "e":
            window(L, Fe, c, 0.0, z0, z1, ww, inner=+1, pane=pane, beam=bm_, beam_world=bw(side))
        else:
            window(L, Fw, -c, 0.0, z0, z1, ww, inner=+1, pane=pane, beam=bm_, beam_world=bw(side))
    # 박공 벽 위 삼각형 (동·서)
    for sx in (1, -1):
        tri = [(-hd - 0.12, h), (hd + 0.12, h), (0, h + ridge)]
        L.extrude("corr", tri, F.p(sx * hw_, 0, 0), F.d(sx, 0, 0), 0.12, up=(0, 0, 1), back=0.0)
    # 지붕 판 + 트러스
    import math as _m
    run = hd + 0.35
    ang = _m.degrees(_m.atan2(ridge, hd))
    slope_len = _m.hypot(run, ridge * run / hd)
    for sy in (1, -1):
        cy = sy * run / 2
        cz = h + ridge - ridge * (run / 2) / hd + 0.08
        F.rbox(L, "roof", (0, cy, cz), (w + 0.6, slope_len, 0.1), (-sy * ang, 0, 0))
    n = max(1, round(w / truss_pitch))
    for i in range(n + 1):
        xx = -hw_ + 0.15 + (w - 0.3) * i / n
        F.box(L, "wood_d", xx - 0.06, xx + 0.06, -hd, hd, h - 0.12, h, kind="detail")
        for sy in (1, -1):
            F.cyl(L, "wood_d", (xx, sy * hd, h), (xx, 0, h + ridge - 0.05), 0.06, verts=4, kind="detail")
            F.cyl(L, "wood_d", (xx, sy * hd * 0.5, h), (xx, sy * hd * 0.5, h + ridge * 0.5 - 0.05), 0.045, verts=4,
                  kind="detail")
            F.cyl(L, "wood_d", (xx, sy * hd * 0.5, h), (xx, 0, h + ridge - 0.1), 0.04, verts=4, kind="detail")
        F.cyl(L, "wood_d", (xx, 0, h), (xx, 0, h + ridge), 0.05, verts=4, kind="detail")
    F.box(L, "wood_d", -hw_, hw_, -0.06, 0.06, h + ridge - 0.14, h + ridge - 0.02, kind="detail")
    for (lx, ly) in lamps:
        hanging_lamp(L, F.p(lx, ly, h), drop=1.1, on=lamp_on)


# ------------------------------------------------------------------ calendar (CAL_page_nn)

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
PIC = [("toy_green", "toy_white"), ("sky_dusk_3", "toy_white"), ("leaf_l", "grass_d"), ("leaf", "toy_red"),
       ("can_y", "leaf"), ("sky_dawn_0", "toy_red"), ("sunwin", "leaf_d"), ("can_y", "wheat_d"),
       ("wheat", "dirt"), ("toy_red", "dirt_d"), ("sky_dusk_4", "box_d"), ("toy_red", "toy_white")]


def calendar(L, F, x, z, pages, *, w=0.42, h=0.6, first=6, crossed=None, y=0.0):
    """벽걸이 달력: CAL_page_01..N 묶음 노드 (01이 맨 앞). 피벗 = 윗변 가운데(넘길 때 지역 X축으로 돈다).

    pages: 장 수, first: 첫 장의 달(0=1월). crossed: 장마다 X 친 날 수 (기본: 앞 장은 다 침).
    """
    N = F.d(0, -1, 0)
    # 걸이 못 + 받침 판
    F.box(L, "box_d", x - w / 2 - 0.01, x + w / 2 + 0.01, y - 0.012, y, z - h - 0.01, z + 0.01)
    L.obj("pipe", F.place(cb.cylinder("nail", radius=0.008, depth=0.05, loc=(x, y - 0.03, z + 0.04),
                                      rot=(90, 0, 0), verts=6)), kind="detail")
    F.cyl(L, "pipe", (x - 0.06, y - 0.02, z + 0.005), (x, y - 0.03, z + 0.04), 0.004, verts=4, kind="fine")
    F.cyl(L, "pipe", (x + 0.06, y - 0.02, z + 0.005), (x, y - 0.03, z + 0.04), 0.004, verts=4, kind="fine")
    for i in range(pages):
        mon = (first + i) % 12
        # 01이 가장 앞(벽에서 멀다). 장 사이 4 mm, 한 장 안의 층(종이 0 → 격자·그림 1 mm → 언덕·글자·X 2 mm)은
        # 뒷장의 가장 앞 층이 앞장 종이보다 2 mm 뒤에 있게 한다
        off = 0.014 + (pages - 1 - i) * 0.004
        piv = F.p(x, y - off, z)
        g = Group(L, f"CAL_page_{i + 1:02d}", pivot=piv, rot=(0, 0, math.radians(F.yaw)),
                  props={"page": i + 1, "month": mon + 1, "hinge": "x", "flipDeg": -170})
        S = Frame(piv, F.yaw)

        def P(u, v, d=0.0):
            return S.p(u, -d, v)
        # 종이
        b = g.bm("cal", "detail")
        vs = [b.verts.new(P(u, v)) for u, v in ((-w / 2, -h), (w / 2, -h), (w / 2, 0), (-w / 2, 0))]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.dot(Vector(N)) < 0:
            f.normal_flip()
        # 그림 칸 (위 40%)
        ph = h * 0.42
        c1, c2 = PIC[mon]
        b = g.bm(c1, "fine")
        _quad(b, P(-w / 2 + 0.02, -0.035, 0.001), P(w / 2 - 0.02, -0.035, 0.001), P(w / 2 - 0.02, -0.035 - ph, 0.001),
              P(-w / 2 + 0.02, -0.035 - ph, 0.001), N)
        # 그림: 언덕(아래)과 해 or 별 (단순 도형)
        b = g.bm(c2, "fine")
        hill = [(-w / 2 + 0.02, -0.035 - ph)]
        for k in range(9):
            u = -w / 2 + 0.02 + (w - 0.04) * k / 8
            hill.append((u, -0.035 - ph + ph * (0.28 + 0.12 * math.sin(k * 0.9 + mon))))
        hill.append((w / 2 - 0.02, -0.035 - ph))
        vs = [b.verts.new(P(u, v, 0.002)) for u, v in hill]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.dot(Vector(N)) < 0:
            f.normal_flip()
        # 달 이름·숫자
        gy = -0.035 - ph - 0.01
        o = hw.text("m", f"{mon + 1}", 0.065, P(-w / 2 + 0.07, gy - 0.04, 0.002), right=S.d(1, 0, 0), up=(0, 0, 1),
                    mat=None, font="din", lift=0.0)
        g.obj("ink_r" if mon == 11 else "ink", o, kind="fine")
        o = hw.text("mn", MONTHS[mon], 0.035, P(w / 2 - 0.09, gy - 0.04, 0.002), right=S.d(1, 0, 0), up=(0, 0, 1),
                    mat=None, font="din", lift=0.0)
        g.obj("ink", o, kind="fine")
        # 날짜 칸 7 × 5 + X 표시
        gx0, gx1 = -w / 2 + 0.02, w / 2 - 0.02
        gz0, gz1 = -h + 0.02, gy - 0.085
        b = g.bm("ink", "fine")
        for k in range(8):
            u = gx0 + (gx1 - gx0) * k / 7
            _strip(b, P(u, gz0, 0.001), P(u, gz1, 0.001), 0.0018, N, S.d(1, 0, 0))
        for k in range(6):
            v = gz0 + (gz1 - gz0) * k / 5
            _strip(b, P(gx0, v, 0.001), P(gx1, v, 0.001), 0.0018, N, (0, 0, 1))
        nx = 35 if crossed is None else crossed[i]
        b = g.bm("ink_r", "fine")
        cw, ch = (gx1 - gx0) / 7, (gz1 - gz0) / 5
        for dd in range(min(nx, 31)):
            r_, c_ = divmod(dd + (mon * 3) % 7, 7)
            if r_ > 4:
                break
            cx = gx0 + cw * (c_ + 0.5)
            cz = gz1 - ch * (r_ + 0.5)
            a, bb = cw * 0.32, ch * 0.32
            _strip(b, P(cx - a, cz - bb, 0.002), P(cx + a, cz + bb, 0.002), 0.004, N, None)
            _strip(b, P(cx - a, cz + bb, 0.002), P(cx + a, cz - bb, 0.002), 0.004, N, None)
        g.done()


def _quad(b, a, bb, c, d, N):
    f = b.faces.new([b.verts.new(p) for p in (a, bb, c, d)])
    f.normal_update()
    if f.normal.dot(Vector(N)) < 0:
        f.normal_flip()


def _strip(b, p0, p1, wdt, N, _side):
    P0, P1, Nn = Vector(p0), Vector(p1), Vector(N).normalized()
    d = (P1 - P0).normalized()
    s = Nn.cross(d).normalized() * (wdt / 2)
    _quad(b, P0 - s, P1 - s, P1 + s, P0 + s, Nn)


# ------------------------------------------------------------------ glb import (잔해 등)

def import_glb(L, rel, *, name=None, matrix=None, keep=None, drop=(), props=None):
    """public/models/<rel>을 불러와 루트 아래에 둔다(L.ik_extra). keep/drop: 노드 이름 걸러내기."""
    path = os.path.join(cb.MODELS_DIR, rel)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    tops = [o for o in new if o.parent is None]
    kill = set()
    for o in new:
        if any(o.name == d or o.name.startswith(d + ".") for d in drop):
            kill.add(o.name)
            kill.update(c.name for c in o.children_recursive)
    keep_names = [o.name for o in new if o.name not in kill]
    tops_names = [o.name for o in tops if o.name not in kill]
    for nm in kill:
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
    new = [bpy.data.objects[n] for n in keep_names]
    tops = [bpy.data.objects[n] for n in tops_names]
    holder = cb.empty(name or os.path.splitext(os.path.basename(rel))[0] + "_set", size=1.0)
    for t in tops:
        t.parent = holder
    if matrix is not None:
        holder.matrix_world = matrix
    for k, v in (props or {}).items():
        holder[k] = v
    for o in new:
        o.name = o.name.replace(".", "_")
        if o.type == "MESH":
            o["collider"] = 0
    L.ik_extra.append(holder)
    return holder, new
