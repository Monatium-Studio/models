"""모나티엄 도시 키트 (monatium_city_kit).

교주 차원 모나티엄(엘리아스 동부의 엘프 도시)을 모듈 단위로 조립한다. 인터루드 4~7 디오라마와 1막 레벨(시가전 등)이
같은 모듈을 쓴다. 근거와 규약: docs/art/monatium-city.md, 레벨 노드 규칙: docs/LEVELS.md.

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, monatium_city_kit as mk
    cb.reset()
    C = mk.City("m2_streets")
    mk.paving(C, -20, 20, -10, 10)
    mk.building(C, -30, -18, -30, -20, floors=4, style="office", front="+y")
    mk.lamp(C, 0, -11)
    C.npc("rita", (0, 0, 0), "characters/rita.glb", pose="idle", face=(0, -5))
    C.finish("levels/m2_streets.glb", root_props={"sky": "#9fd3f2"})

설계 (prologue의 level_kit과 같은 원리, 의존성은 cb·home_weapons만):
  - 지오메트리는 (그룹, 머티리얼, 종류)별 bmesh에 바로 쌓고 finish에서 그룹마다 머티리얼별 메시 하나로 만든다.
  - 종류(kind): main(아웃라인, 레벨 기본) / detail(얇은 아웃라인) / far(원경, 굵은 아웃라인) / fine(아웃라인 없음: 데칼·글자·발광)
  - 보이는 메시는 전부 collider=0. 충돌은 단순한 COL_ 박스가 맡는다(축 정렬 col(), 돌린 상자 ocol()/lcol(),
    볼록 다면체 ccol(). LevelLoader가 상자는 회전 상자, 볼록은 볼록 껍질 충돌체로 만든다).
    거리 소품(가로등, 벤치, 가로수, 난간, 자판기, 볼라드, 표지 기둥, 쓰레기통, 상자, 모래주머니, 천막, 바위)도 자기 COL을 단다.
  - 그룹: C.group("STAGE_0")처럼 대문자 접두사 이름이면 그 이름의 노드가 생기고(몽타주가 켜고 끈다),
    그 그룹에서 만든 마커(PROP_, FX_, LIGHT_ …)도 그 노드 아래에 들어간다. 소문자 이름은 zone_<이름> 노드.
  - 좌표: Blender Z-up, 1 BU = 1 m. 빈 오브젝트의 -Y가 정면(NPC, PROP, CAM).

체격: 엘프 기준(키 1.2 m). 문 1.8 m, 층고 2.7 m(1층 상가 3.2 m), 보도 3 m, 차로 2.8 m.
"""
from __future__ import annotations

import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw

# ================================================================== palette
# 원작 모나티엄 배경(유리 고층, 고가 모노레일, 밝은 석재 보도, 검은 가로등, 나무 난간, 자판기)을 따르고
# 교주 차원 형태 언어(둥근 판, 스타디움 창, 금색 고리, 시안 발광, 엘프 로고 원판)로 묶는다.
PAL = {
    # 바닥
    "pave": "#e7e1d2",       # 광장·보도 석재 (원작 배경의 밝은 크림 판석)
    "pave_d": "#cbc3b0",     # 판석 줄눈, 연석 윗면
    "pave_r": "#d9b9a4",     # 보도 띠 (붉은 벽돌 톤)
    "asphalt": "#5e5a66",    # 차도 (자줏빛 회색)
    "curb": "#b8b2ad",       # 연석
    "line": "#f1ece0",       # 차선·횡단보도
    "line_y": "#e8c34a",     # 중앙선 (경고 노랑과 같은 값)
    "grass": "#93c477",
    "grass_d": "#73aa5f",
    "soil": "#a88a6c",
    # 건물
    "stone": "#efe8dc",      # 시청 석재 (흰 크림)
    "stone_d": "#cfc6b8",    # 석재 그림자 띠, 계단
    "concrete": "#dcd8d4",   # 사무 건물
    "concrete_d": "#a9a3a8", # 띠, 기단
    "warm": "#e9d8c3",       # 주거 건물
    "warm_d": "#c7ad94",
    "brick": "#c98d78",      # 상가 벽돌
    "glass": "#7fb3dc",      # 유리 (원작 고층의 청색)
    "glass_d": "#4c7fae",    # 유리 아래쪽·짙은 창
    "glass_t": "#5c97c9",    # 유리탑 몸체
    "mullion": "#d3dde8",    # 유리탑 멀리언
    "roof": "#8d8893",
    "metal": "#5d555d",      # 자줏빛 건메탈 (가로등, 기계)
    "dark": "#3a333b",
    "steel": "#cfcac4",
    "gold": "#d6b25e",       # 지휘색 포인트 (고리, 로고)
    "navy": "#2f3644",       # 엘피니아 남색 (표지판 바탕, 문틀)
    "navy_l": "#4a5468",
    "violet": "#706478",     # 진압반 남보라
    "violet_d": "#56445b",
    "teal": "#3f9a94",       # 비살상 청록 (진압반 표식)
    "hazard": "#e8c34a",
    "white": "#f6f3ee",
    "red": "#cf5546",        # 자판기, 소화전
    "coral": "#e58a6c",      # 차양
    "coral_hair": "#d58f88", # 엘레나 머리색 (초상)
    "mint": "#8fd0bf",       # 차양
    "wood": "#c9a26c",       # 난간, 벤치 (원작 배경의 나무 난간)
    "wood_d": "#9a7650",
    "trunk": "#7a5644",
    "leaf": "#5fae6a",
    "leaf_l": "#86c77a",
    "leaf_d": "#468f57",
    "hedge": "#5a9f5e",
    "rubber": "#4a4450",     # 훈련장 바닥
    "sand": "#c8b48c",       # 모래주머니
    "canvas": "#d8cba6",     # 천막
    "tarp": "#4f7fc0",       # 지구제 방수포 (파랑)
    "olive": "#8d988c",      # 엘피니아 회녹
    "rock": "#9d97a0",
    "far": "#a9bfd3",        # 원경 고층 (공기 원근)
    "far_d": "#8ea6be",
    # 엘리아스 자연
    "bark": "#8a6a55",
    "canopy": "#78b986",     # 세계수 잎
    "canopy_l": "#9ccf95",
    "mount": "#a7b8c9",
    "mount_l": "#dfe8ef",
    "meat": "#b8654f",       # 나무에 열린 고기 (원작: 엘리아스는 고기가 나무에서 열린다)
    "bone": "#f3ead8",
    "flower_p": "#f2a7c3",
    "flower_y": "#f6dc6e",
    # R41 (차원문·틈) r41-style.md 팔레트
    "r41_shell": "#2a2733",
    "r41_metal": "#4d4959",
    "r41_light": "#cbc8d1",
    "amber": "#f09a3e",
}
GLOW = {
    "glow": "#7ff0ea",       # 모나티엄 네트워크 시안 (HUD·코어 AI와 같은 색)
    "glow_off": "#2c5f63",   # 꺼진 시안 (기동 전 코어)
    "lamp": "#fff1c9",       # 가로등 켜짐
    "lamp_off": "#e8e4da",   # 낮의 가로등 갓
    "win_lit": "#ffe7b0",    # 불 켜진 창
    "screen": "#14283c",     # 꺼진 화면 (몽타주가 텍스처를 씌움)
    "alert": "#ff4a3a",      # 경보 켜짐
    "alert_d": "#7a2a2a",    # 경보 렌즈 (꺼짐, UNLIT 아님 → PAL로)
    "magenta": "#ff4fd8",    # R41 기계 발광
    "violet_glow": "#a070ff",
    "fire": "#ffb35a",
    "fire_c": "#fff0b0",
    "sky_a": "#ffffff",      # 하늘 장식 (달)
    "moon": "#f4efe6",
    "moon_d": "#d9d2e6",
    "cyan_hot": "#e9fffd",
}
ALPHA = {
    "holo": ("#5fe6e0", 0.32),
    "holo_l": ("#a8f6f1", 0.18),
    "glass_a": ("#a9dce6", 0.22),
    "haze": ("#f3f6f8", 0.30),     # 엘리아스 경계의 안개
    "vortex": ("#ff4fd8", 0.55),
    "vortex_l": ("#ffc4f1", 0.75),
    "vortex_v": ("#7a3cff", 0.35),
    "rift": ("#ff6fe0", 0.65),
    "portal": ("#7ff0ea", 0.55),
    "portal_l": ("#e9fffd", 0.8),
    "beam": ("#7ff0ea", 0.16),
    "smoke": ("#eceae6", 0.85),
}
# 경보 렌즈 꺼짐색은 보통 머티리얼
PAL["alert_d"] = "#7a3a3a"
del GLOW["alert_d"]

LINE = "#4a2229"
LINE_DARK = "#24100f"
LINE_R41 = "#191422"
_DARK = {"asphalt", "metal", "dark", "navy", "navy_l", "violet_d", "rubber", "r41_metal", "trunk", "glass_d"}
_R41 = {"r41_shell", "r41_metal", "r41_light", "amber"}

_mats: dict[str, bpy.types.Material] = {}


def M(key: str) -> bpy.types.Material:
    """키트 팔레트 머티리얼 (이름 mc_<key>, 발광은 UNLIT_mc_<key>)."""
    m = _mats.get(key)
    if m is not None:
        try:
            if m.name in bpy.data.materials:
                return m
        except ReferenceError:
            pass
    if key in GLOW:
        m = cb.mat(f"mc_{key}", GLOW[key], emission=GLOW[key], unlit=True)
    elif key in ALPHA:
        c, a = ALPHA[key]
        m = cb.mat(f"mc_{key}", c, emission=c, unlit=True, alpha=a)
    else:
        line = LINE_R41 if key in _R41 else (LINE_DARK if key in _DARK else LINE)
        m = cb.mat(f"mc_{key}", PAL[key], line=line, roughness=0.7)
    _mats[key] = m
    return m


def is_glow(key):
    return key in GLOW or key in ALPHA


def _kind(key, kind):
    """메시 종류: main(아웃라인) / detail(얇은 아웃라인) / fine(아웃라인 없음, 강한 깊이 편향) /
    under(아웃라인 없음, 약한 깊이 편향: 메시 이름 *_under_detail). under는 겹쳐 쌓는 데칼의 맨 아래 판(창유리, 로고
    원판)에 쓴다. 그 위의 fine 데칼이 런타임 편향(src/art/toon.ts depthBiasFor)으로 거리와 상관없이 이긴다.
    표준 깊이 버퍼(근평면 3 cm)는 같은 등급 두 면을 50 m에서 5 mm까지만 가르므로 fine 위 fine은 1 cm 넘게 띄운다."""
    if kind == "under":
        return "under"
    return "fine" if is_glow(key) else kind


# ================================================================== small math

def yaw_to(src, dst) -> float:
    """src에서 dst를 바라보는 Z 회전(라디안). 로컬 -Y가 그 방향을 향한다."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def frame(normal, up=(0, 0, 1)):
    """면 위 2D 좌표계 (right, up). normal = right x up."""
    N = Vector(normal).normalized()
    U = Vector(up).normalized()
    if abs(N.dot(U)) > 0.999:
        U = Vector((0, 1, 0)) if abs(N.z) > 0.5 else Vector((0, 0, 1))
    R = U.cross(N).normalized()
    U = N.cross(R).normalized()
    return R, U, N


FRONT = {"-y": Vector((0, -1, 0)), "+y": Vector((0, 1, 0)), "-x": Vector((-1, 0, 0)), "+x": Vector((1, 0, 0))}


def noise2(x, y, seed=0):
    """부드러운 값 잡음 (사인 합). 지형 높이용."""
    s = seed * 1.7
    return (math.sin(x * 0.051 + s) * math.cos(y * 0.043 - s * 0.7) * 0.6
            + math.sin(x * 0.11 + y * 0.07 + s * 2.1) * 0.3
            + math.cos(x * 0.023 - y * 0.031 + s) * 0.8)


# ================================================================== bmesh writers

def _bm_box(bm, x0, x1, y0, y1, z0, z1, matrix=None):
    xs, ys, zs = (min(x0, x1), max(x0, x1)), (min(y0, y1), max(y0, y1)), (min(z0, z1), max(z0, z1))
    v = []
    for z in zs:
        for y in ys:
            for x in xs:
                p = Vector((x, y, z))
                if matrix is not None:
                    p = matrix @ p
                v.append(bm.verts.new(p))
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        bm.faces.new([v[i] for i in f])


def _bm_prism(bm, pts, z0, z1, matrix=None, top=True, bottom=True, smooth=False):
    """xy 다각형(반시계)을 z0..z1로 세운 기둥."""
    def P(x, y, z):
        p = Vector((x, y, z))
        return bm.verts.new(matrix @ p if matrix is not None else p)
    lo = [P(x, y, z0) for x, y in pts]
    hi = [P(x, y, z1) for x, y in pts]
    n = len(pts)
    faces = []
    if bottom:
        faces.append(bm.faces.new(list(reversed(lo))))
    if top:
        faces.append(bm.faces.new(hi))
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        f.smooth = smooth
        faces.append(f)
    return faces


def _bm_ring_prism(bm, outer, inner, z0, z1, matrix=None):
    """같은 점 개수의 바깥·안 외곽선 사이를 세운 고리 (난간벽, 파라펫)."""
    def ring(pts, z):
        return [bm.verts.new((matrix @ Vector((x, y, z))) if matrix is not None else Vector((x, y, z)))
                for x, y in pts]
    o0, o1, i0, i1 = ring(outer, z0), ring(outer, z1), ring(inner, z0), ring(inner, z1)
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((o0[i], o0[j], o1[j], o1[i]))
        bm.faces.new((i1[i], i1[j], i0[j], i0[i]))
        bm.faces.new((o1[i], o1[j], i1[j], i1[i]))
        bm.faces.new((i0[i], i0[j], o0[j], o0[i]))


def _bm_poly(bm, pts3d, normal=None):
    vs = [bm.verts.new(Vector(p)) for p in pts3d]
    f = bm.faces.new(vs)
    if normal is not None:
        f.normal_update()
        if f.normal.dot(Vector(normal)) < 0:
            f.normal_flip()
    return f


def _bm_cyl(bm, p0, p1, r, segs=12, r2=None, cap=True, smooth=True):
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    if d.length < 1e-6:
        return
    q = d.normalized().to_track_quat("Z", "Y")
    Mx = Matrix.Translation((P0 + P1) / 2) @ q.to_matrix().to_4x4()
    res = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs, radius1=r,
                                radius2=r if r2 is None else r2, depth=d.length, matrix=Mx)
    if smooth:
        vs = set(res["verts"])
        for f in {f for v in vs for f in v.link_faces}:
            if len(f.verts) == 4:
                f.smooth = True


def _bm_blob(bm, center, radius, scale=(1, 1, 1), segs=10, rings=6, smooth=True, rot_z=0.0):
    Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z, 4, "Z")
          @ Matrix.Diagonal((*scale, 1.0)))
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius, matrix=Mx)
    if smooth:
        vs = set(res["verts"])
        for f in {f for v in vs for f in v.link_faces}:
            f.smooth = True


def _bm_quad_uv(bm, pts3d, uvs):
    lay = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(Vector(p)) for p in pts3d]
    f = bm.faces.new(vs)
    for loop, uv in zip(f.loops, uvs):
        loop[lay].uv = uv
    return f


def _box_obj(name, x0, x1, y0, y1, z0, z1):
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    b = bmesh.new()
    _bm_box(b, x0 - cx, x1 - cx, y0 - cy, y1 - cy, z0 - cz, z1 - cz)
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    o.location = (cx, cy, cz)
    cb.link(o)
    return o


def _copy_into(dst, src_bm):
    me = bpy.data.meshes.new("tmp_copy")
    src_bm.to_mesh(me)
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)


def _text(name, s, size, c, R, U, N, *, font=None, align="CENTER", spacing=1.0, res=3):
    """평평한 글자 메시. home_weapons.text와 같지만 곡선 분할(res)을 올려 O·0이 마름모가 되지 않게 한다."""
    if font is None:
        font = "kr" if any(ord(ch) > 0x2000 for ch in s) else "din"
    cu = bpy.data.curves.new(name + "_crv", "FONT")
    cu.body = s
    f = hw._font(font)
    if f:
        cu.font = f
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.resolution_u = res
    cu.space_character = spacing
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    cb.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.name = name
    o = bpy.data.objects.new("decal_" + name, me)
    cb.link(o)
    m4 = Matrix((R, U, N)).transposed().to_4x4()
    m4.translation = Vector(c)
    o.matrix_world = m4
    return o


# ================================================================== City

class City:
    """레벨·디오라마 조립기. group()으로 그룹을 바꿔 가며 쌓고 finish()로 내보낸다."""

    def __init__(self, name, *, prop=False, lift=0.015):
        self.name = name
        self.prop_mode = prop
        self.grp = "city"
        self.acc: dict[tuple, bmesh.types.BMesh] = {}
        self.objs: list[tuple] = []
        self.cols: list[tuple] = []
        self.col_props: dict[str, dict] = {}  # COL 이름 → 노드 커스텀 속성 (예: climb=0)
        self.ocols: list[tuple] = []          # (name, x, y, z0, sx, sy, sz, yaw) 돌린 상자 (바닥 중심)
        self.ccols: list[tuple] = []          # (name, verts) 볼록 다면체
        self.markers: list[tuple] = []        # (name, loc, rot, props, grp, scale)
        self.specials: list[tuple] = []       # (grp, obj)
        self.nodes: list[tuple] = []          # (grp, obj) 직접 만든 노드 트리 (GATE_, RIFT_)
        self.group_props: dict[str, dict] = {}
        self.lift = lift
        self._n = 0

    # ---------------------------------------------------------- state
    def group(self, name, **props):
        self.grp = name
        if props:
            self.group_props.setdefault(name, {}).update(props)
        return self

    def bm(self, key, kind="main"):
        k = (self.grp, key, _kind(key, kind))
        b = self.acc.get(k)
        if b is None:
            b = self.acc[k] = bmesh.new()
        return b

    def uid(self, prefix="n"):
        self._n += 1
        return f"{prefix}{self._n:04d}"

    # ---------------------------------------------------------- primitives
    def box(self, key, x0, x1, y0, y1, z0, z1, *, kind="main", col=False):
        _bm_box(self.bm(key, kind), x0, x1, y0, y1, z0, z1)
        if col:
            self.col(x0, x1, y0, y1, z0, z1)

    def rbox(self, key, center, size, rot=(0, 0, 0), *, kind="main"):
        """회전한 박스. rot = XYZ 도."""
        Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
              @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        sx, sy, sz = (s / 2 for s in size)
        _bm_box(self.bm(key, kind), -sx, sx, -sy, sy, -sz, sz, matrix=Mx)

    def beam(self, key, p0, p1, w, h, *, kind="main", up=(0, 0, 1)):
        """p0→p1 사각 보 (폭 w, 높이 h)."""
        P0, P1 = Vector(p0), Vector(p1)
        d = P1 - P0
        L = d.length
        if L < 1e-6:
            return
        Y = d.normalized()
        U = Vector(up)
        if abs(Y.dot(U)) > 0.99:
            U = Vector((1, 0, 0))
        X = Y.cross(U).normalized()
        Z = X.cross(Y).normalized()
        Mx = Matrix((X, Y, Z)).transposed().to_4x4()
        Mx.translation = (P0 + P1) / 2
        _bm_box(self.bm(key, kind), -w / 2, w / 2, -L / 2, L / 2, -h / 2, h / 2, matrix=Mx)

    def prism(self, key, pts, z0, z1, *, kind="main", matrix=None, top=True, bottom=False, smooth=False):
        return _bm_prism(self.bm(key, kind), pts, z0, z1, matrix=matrix, top=top, bottom=bottom, smooth=smooth)

    def ring_prism(self, key, outer, inner, z0, z1, *, kind="main", matrix=None):
        _bm_ring_prism(self.bm(key, kind), outer, inner, z0, z1, matrix=matrix)

    def cyl(self, key, p0, p1, r, *, segs=12, r2=None, kind="main", cap=True, smooth=True):
        _bm_cyl(self.bm(key, kind), p0, p1, r, segs=segs, r2=r2, cap=cap, smooth=smooth)

    def blob(self, key, center, radius, scale=(1, 1, 1), *, segs=10, rings=6, kind="main", rot_z=0.0):
        _bm_blob(self.bm(key, kind), center, radius, scale, segs=segs, rings=rings, rot_z=rot_z)

    def poly(self, key, pts3d, *, normal=None, kind="fine"):
        return _bm_poly(self.bm(key, kind), pts3d, normal)

    def decal(self, key, pts2d, center, normal, *, up=(0, 0, 1), lift=None, kind="fine"):
        """면에 붙는 2D 다각형 (center = 면 위 점, normal = 바깥)."""
        R, U, N = frame(normal, up)
        c = Vector(center) + N * (self.lift if lift is None else lift)
        return self.poly(key, [c + R * u + U * v for u, v in pts2d], normal=N, kind=kind)

    def rect(self, key, center, normal, w, h, *, up=(0, 0, 1), lift=None, kind="fine"):
        return self.decal(key, [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], center, normal,
                          up=up, lift=lift, kind=kind)

    def ring(self, key, outer, inner, center, normal, *, up=(0, 0, 1), lift=None, kind="fine"):
        R, U, N = frame(normal, up)
        c = Vector(center) + N * (self.lift if lift is None else lift)
        b = self.bm(key, kind)
        vo = [b.verts.new(c + R * u + U * v) for u, v in outer]
        vi = [b.verts.new(c + R * u + U * v) for u, v in inner]
        n = len(vo)
        for i in range(n):
            j = (i + 1) % n
            f = b.faces.new((vo[i], vo[j], vi[j], vi[i]))
            f.normal_update()
            if f.normal.dot(N) < 0:
                f.normal_flip()

    def strip(self, key, p0, p1, width, normal=(0, 0, 1), *, lift=None, kind="fine"):
        P0, P1, N = Vector(p0), Vector(p1), Vector(normal).normalized()
        d = (P1 - P0).normalized()
        s = N.cross(d).normalized() * (width / 2)
        o = N * (self.lift if lift is None else lift)
        return self.poly(key, [P0 - s + o, P1 - s + o, P1 + s + o, P0 + s + o], normal=N, kind=kind)

    def plate(self, key, pts2d, center, normal, depth, *, up=(0, 0, 1), kind="main", back=0.0):
        """2D 외곽선을 normal 방향으로 depth만큼 돌출한 판 (간판, 액자, 문짝)."""
        R, U, N = frame(normal, up)
        c = Vector(center)
        b = self.bm(key, kind)
        f0 = [b.verts.new(c + R * u + U * v - N * back) for u, v in pts2d]
        f1 = [b.verts.new(c + R * u + U * v + N * (depth - back)) for u, v in pts2d]
        n = len(pts2d)
        faces = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
        for i in range(n):
            j = (i + 1) % n
            faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
        bmesh.ops.recalc_face_normals(b, faces=faces)

    def obj(self, key, o, *, kind="main"):
        if o is None:
            return None
        self.objs.append((self.grp, key, _kind(key, kind), o))
        return o

    def text(self, key, s, size, center, normal, *, up=(0, 0, 1), lift=None, font=None, align="CENTER",
             spacing=1.0, kind="fine"):
        R, U, N = frame(normal, up)
        c = Vector(center) + N * (self.lift * 1.5 if lift is None else lift)
        o = _text(self.uid("txt"), s, size, c, R, U, N, font=font, align=align, spacing=spacing,
                  res=3 if size >= 0.3 else 2)
        return self.obj(key, o, kind=kind)

    def logo(self, center, size, normal, *, up=(0, 0, 1), key="gold", disc=None, ring=None, disc_scale=0.68,
             lift=None, kind="fine"):
        """원작 엘프 로고 (높이 size). disc: 바탕 원판, ring: 원판 테.
        층: 바탕 면 → (lift) 원판·테 → (lift + 층 간격) 로고. 층 간격은 lift의 0.6배, 크기의 0.3%, 3 mm 중 큰 값이라
        lift=0으로 원판을 바탕에 바로 붙여도 로고가 원판과 같은 평면에 오지 않는다(겹친 면 깜빡임, docs/art/zfight-audit.md)."""
        lf = self.lift if lift is None else lift
        R, U, N = frame(normal, up)
        base_kind = "under" if kind == "fine" else kind   # 원판·테는 약한 편향 층: 그 위 로고(fine)가 늘 이긴다
        if disc:
            self.decal(disc, hw.circle(size * disc_scale, 32), center, normal, up=up, lift=lf, kind=base_kind)
        if ring:
            r0 = size * disc_scale
            self.ring(ring, hw.circle(r0 + size * 0.07, 32), hw.circle(r0, 32), center, normal, up=up, lift=lf,
                      kind=base_kind)
        c = Vector(center) + N * (lf + max(0.003, lf * 0.6, size * 0.003))
        o = hw.elf_logo(self.uid("logo"), tuple(c), size, right=tuple(R), up=tuple(U), mat=None, lift=0.0)
        if o is None:
            self.marker(f"EMBLEM_slot_{self.uid()}", tuple(center), props={"emblemSize": size})
            return None
        return self.obj(key, o, kind=kind)

    # ---------------------------------------------------------- collision
    def col(self, x0, x1, y0, y1, z0, z1, name=None, props=None):
        """축 정렬 COL_ 상자. props = 노드 커스텀 속성 (예: {"climb": 0}, docs/LEVELS.md '엔진 쪽 확장 속성')."""
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        if x1 - x0 < 1e-3 or y1 - y0 < 1e-3 or z1 - z0 < 1e-3:
            return
        nm = name or f"COL_{self.grp}_{len(self.cols) + 1:03d}"
        self.cols.append((nm, x0, x1, y0, y1, z0, z1))
        if props:
            self.col_props[nm] = dict(props)

    def ocol(self, base, size, yaw=0.0, name=None):
        """돌린 COL_ 상자. base = 바닥 중심 (x, y, z0), size = (로컬 X 폭, 로컬 Y 깊이, 높이), yaw = Z축 도.
        90°의 배수면 축 정렬 col()로 넣는다 (replace_col·drop_cols_in이 찾을 수 있게)."""
        x, y, z0 = base
        sx, sy, sz = size
        if sx < 1e-3 or sy < 1e-3 or sz < 1e-3:
            return
        q = round(yaw / 90.0)
        if abs(yaw - q * 90.0) < 0.5:
            if q % 2:
                sx, sy = sy, sx
            self.col(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z0, z0 + sz, name=name)
            return
        self.ocols.append((name or f"COL_{self.grp}_o{len(self.ocols) + 1:03d}", x, y, z0, sx, sy, sz, yaw))

    def lcol(self, x, y, z, yaw, x0, x1, y0, y1, z0, z1, name=None):
        """소품 로컬 상자(정면 -Y 기준 x0..x1, y0..y1, z0..z1)를 (x, y, z)에 yaw만큼 돌려 COL_로."""
        a = math.radians(yaw)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.ocol((x + cx * math.cos(a) - cy * math.sin(a), y + cx * math.sin(a) + cy * math.cos(a), z + z0),
                  (x1 - x0, y1 - y0, z1 - z0), yaw, name=name)

    def ccyl(self, cx, cy, r, z0, z1, n=16, name=None):
        """세운 원기둥 COL (n각 기둥, 변까지 거리 = r)."""
        rr = r / math.cos(math.pi / n)
        self.ccol([(cx + math.cos(2 * math.pi * k / n) * rr, cy + math.sin(2 * math.pi * k / n) * rr, z)
                   for k in range(n) for z in (z0, z1)], name=name)

    def rrcol(self, x0, x1, y0, y1, z0, z1, r, seg=4, name=None):
        """모서리가 둥근 직사각형 기둥 COL (반지름 r, 모서리당 seg 조각). 둥근 모서리 건물의 상자 COL은 모서리에 투명 벽이 남았다."""
        if r <= 0.01:
            self.col(x0, x1, y0, y1, z0, z1, name=name)
            return
        pts = []
        for (cx, cy, a0) in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
            for k in range(seg + 1):
                a = math.radians(a0 + 90 * k / seg)
                rr = r / math.cos(math.radians(45 / seg))
                pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        self.ccol([(px, py, z) for px, py in pts for z in (z0, z1)], name=name)

    def ccol(self, verts, name=None):
        """볼록 COL_ (꼭짓점 목록의 볼록 껍질, 월드 좌표). 천막처럼 상자로는 크게 남는 모양."""
        self.ccols.append((name or f"COL_{self.grp}_c{len(self.ccols) + 1:03d}", [tuple(v) for v in verts]))

    # ---------------------------------------------------------- markers
    def marker(self, name, loc, *, yaw=None, face=None, look=None, props=None, scale=None):
        """빈 오브젝트. yaw(도) / face=(x,y) / look=(x,y,z) 중 하나로 -Y 정면을 정한다."""
        rot = None
        if look is not None:
            d = Vector(look) - Vector(loc)
            rot = d.normalized().to_track_quat("-Y", "Z").to_euler()
        elif face is not None:
            rot = (0, 0, yaw_to(loc, face))
        elif yaw is not None:
            rot = (0, 0, math.radians(yaw))
        self.markers.append((name, tuple(loc), rot, dict(props or {}), self.grp, scale))

    def npc(self, nid, loc, model, *, pose="idle", name=None, look=None, fallback=None, props=None, **kw):
        """NPC_<nid>. pose 이름 목록: docs/art/interlude-elias.md. look: 'player' | NPC id | 'none'."""
        p = {"model": model, "pose": pose}
        if name:
            p["name"] = name
        if look:
            p["look"] = look
        if fallback:
            p["fallback"] = fallback
        if self.grp.isupper() or self.grp[:1].isupper():
            p.setdefault("stage", self.grp)
        p.update(props or {})
        self.marker(f"NPC_{nid}", loc, props=p, **kw)

    def prop(self, pid, loc, model, *, scale=None, props=None, **kw):
        p = {"model": model}
        p.update(props or {})
        self.marker(f"PROP_{pid}", loc, props=p, scale=scale, **kw)

    def fx(self, fid, loc, **props):
        self.marker(f"FX_{fid}", loc, props=props)

    def cam(self, shot, points):
        """points: [(t, cam_xyz, look_xyz, fov), ...] → CAM_<shot>_<nn> + LOOK_<shot>_<nn>."""
        for i, (t, cpos, lpos, fov) in enumerate(points, start=1):
            p = {"t": float(t)}
            if fov:
                p["fov"] = float(fov)
            self.marker(f"CAM_{shot}_{i:02d}", cpos, look=lpos, props=p)
            self.marker(f"LOOK_{shot}_{i:02d}", lpos)

    # ---------------------------------------------------------- named meshes
    def special(self, name, build, key, props=None, *, kind="main"):
        """build(bm)로 채운 이름 있는 메시 하나 (원점 = 바운딩 박스 중심)."""
        b = bmesh.new()
        build(b)
        me = bpy.data.meshes.new(name)
        b.to_mesh(me)
        b.free()
        o = bpy.data.objects.new(name, me)
        cb.link(o)
        cb.assign(o, M(key))
        if len(me.vertices):
            xs = [v.co for v in me.vertices]
            lo = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
            hi = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
            c = (lo + hi) / 2
            me.transform(Matrix.Translation(-c))
            o.location = c
        for k, v in (props or {}).items():
            o[k] = v
        o["collider"] = 0
        if kind == "fine" or is_glow(key):
            o["noOutline"] = 1
        self.specials.append((self.grp, o))
        return o

    def screen(self, sid, center, normal, w, h, *, up=(0, 0, 1), frame_key="navy", bezel=0.25, depth=0.3,
               props=None):
        """SCREEN_<sid>: 몽타주가 텍스처·오버레이를 씌우는 화면 (UV 0..1, 정면에서 볼 때 왼쪽 아래가 (0,0)).
        center = 붙일 벽면 위의 점. 테두리 판이 벽에서 depth만큼 나오고 화면은 그 앞에 붙는다."""
        R, U, N = frame(normal, up)
        c = Vector(center)
        self.plate(frame_key, hw.rrect(w + bezel * 2, h + bezel * 2, min(0.4, bezel * 1.5), 2), center, normal,
                   depth, up=up, back=0.0, kind="detail")
        fc = c + N * (depth + 0.02)

        def build(b):
            pts = [fc + R * (-w / 2) + U * (-h / 2), fc + R * (w / 2) + U * (-h / 2),
                   fc + R * (w / 2) + U * (h / 2), fc + R * (-w / 2) + U * (h / 2)]
            _bm_quad_uv(b, pts, [(0, 0), (1, 0), (1, 1), (0, 1)])
        p = {"screen": 1, "aspect": round(w / h, 4), "w": round(w, 3), "h": round(h, 3)}
        p.update(props or {})
        return self.special(f"SCREEN_{sid}", build, "screen", p, kind="fine")

    def add_node(self, o):
        """직접 만든 오브젝트 트리(GATE_, RIFT_)를 현재 그룹 아래에 붙인다."""
        self.nodes.append((self.grp, o))
        return o

    # ================================================================ finish
    def finish(self, rel_path, *, root_props=None, outline=0.025, detail_outline=0.01, far_outline=0.07,
               col_debug=False, root_offset=None):
        """root_offset = (x, y, z): 루트를 옮겨 내보낸다 (이웃 레벨과 한 월드 좌표에 놓을 때, 예: m2_subway)."""
        dg = bpy.context.evaluated_depsgraph_get()
        bpy.context.view_layer.update()
        for (g, key, kind, o) in self.objs:
            k = (g, key, kind)
            b = self.acc.get(k)
            if b is None:
                b = self.acc[k] = bmesh.new()
            eo = o.evaluated_get(dg)
            me = eo.to_mesh()
            me.transform(o.matrix_world)
            b.from_mesh(me)
            eo.to_mesh_clear()
        for (_, _, _, o) in self.objs:
            data = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)
        self.objs.clear()

        root = cb.empty(self.name, size=1.0)
        gnodes: dict[str, bpy.types.Object] = {}

        def gnode(g):
            if self.prop_mode:
                return root
            if g not in gnodes:
                nm = g if g[:1].isupper() else f"zone_{g}"
                gnodes[g] = cb.empty(nm, parent=root, size=0.5)
                for k, v in self.group_props.get(g, {}).items():
                    gnodes[g][k] = v
            return gnodes[g]

        stats = {"tris": 0, "by_group": {}, "by_mat": {}}
        for (g, key, kind), b in sorted(self.acc.items()):
            if not b.faces:
                b.free()
                continue
            suffix = "" if kind == "main" else ("_under_detail" if kind == "under" else "_" + kind)
            nm = f"{self.name}_{key}{suffix}" if self.prop_mode else f"{g}_{key}{suffix}"
            me = bpy.data.meshes.new(nm)
            b.to_mesh(me)
            b.free()
            o = bpy.data.objects.new(nm, me)
            cb.link(o)
            cb.assign(o, M(key))
            o["collider"] = 0
            if kind in ("fine", "under"):
                o["noOutline"] = 1
            elif kind == "detail":
                o["outline"] = detail_outline
            elif kind == "far":
                o["outline"] = far_outline
            o.parent = gnode(g)
            me.calc_loop_triangles()
            nt = len(me.loop_triangles)
            stats["tris"] += nt
            stats["by_group"][g] = stats["by_group"].get(g, 0) + nt
            stats["by_mat"][key] = stats["by_mat"].get(key, 0) + nt
        self.acc.clear()
        for g, o in self.specials + self.nodes:
            o.parent = gnode(g)
            for x in [o] + list(o.children_recursive):
                if x.type == "MESH":
                    x.data.calc_loop_triangles()
                    nt = len(x.data.loop_triangles)
                    stats["tris"] += nt
                    stats["by_group"][g] = stats["by_group"].get(g, 0) + nt

        if self.cols or self.ocols or self.ccols:
            croot = cb.empty("colliders", parent=root, size=0.5)
            colm = cb.mat("COL_debug", "#ff3050", unlit=True, emission="#ff3050", alpha=0.35) if col_debug else None
            made = []
            for (nm, x0, x1, y0, y1, z0, z1) in self.cols:
                o = _box_obj(("dbg_" if col_debug else "") + nm, x0, x1, y0, y1, z0, z1)
                for k, v in self.col_props.get(nm, {}).items():
                    o[k] = v
                made.append(o)
            for (nm, x, y, z0, sx, sy, sz, yaw) in self.ocols:
                o = _box_obj(("dbg_" if col_debug else "") + nm, -sx / 2, sx / 2, -sy / 2, sy / 2, -sz / 2, sz / 2)
                o.location = (x, y, z0 + sz / 2)
                o.rotation_euler = (0.0, 0.0, math.radians(yaw))
                for k, v in self.col_props.get(nm, {}).items():     # 돌린 상자·볼록 COL도 이름으로 속성 (climb=0 등)
                    o[k] = v
                made.append(o)
            for (nm, verts) in self.ccols:
                b = bmesh.new()
                for v in verts:
                    b.verts.new(v)
                bmesh.ops.convex_hull(b, input=list(b.verts))
                me = bpy.data.meshes.new(nm)
                b.to_mesh(me)
                b.free()
                o = bpy.data.objects.new(("dbg_" if col_debug else "") + nm, me)
                cb.link(o)
                for k, v in self.col_props.get(nm, {}).items():
                    o[k] = v
                made.append(o)
            for o in made:
                o.parent = croot
                if colm:
                    cb.assign(o, colm)
                    o["noOutline"] = 1
        if self.markers:
            mroot = cb.empty("markers", parent=root, size=0.5)
            for (nm, loc, rot, props, g, scale) in self.markers:
                parent = gnode(g) if (g[:1].isupper() and not self.prop_mode) else mroot
                e = cb.empty(nm, loc=loc, parent=parent, size=0.25)
                if rot is not None:
                    e.rotation_euler = rot
                if scale is not None:
                    e.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
                for k, v in props.items():
                    e[k] = v
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        props = {"outline": outline}
        props.update(root_props or {})
        mats = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                       for s in o.material_slots if s.material})
        print(f"[mk] {self.name}: tris {stats['tris']} materials {len(mats)} cols {len(self.cols)} "
              f"markers {len(self.markers)}")
        print("[mk] tris by group:", ", ".join(f"{k}={v}" for k, v in sorted(stats["by_group"].items())))
        top = sorted(stats["by_mat"].items(), key=lambda kv: -kv[1])[:14]
        print("[mk] tris by material:", ", ".join(f"{k}={v}" for k, v in top))
        if root_offset:
            root.location = root_offset
        path = cb.export(rel_path, props=props, root=root)
        print(f"[mk] glb {os.path.getsize(path) / 1024:.0f} KB → {path}")
        stats["materials"] = len(mats)
        return stats


# ================================================================== ground · roads

def paving(C, x0, x1, y0, y1, *, z=0.0, key="pave", grout="pave_d", tile=1.6, t=0.3, col=True, border=None,
           kind="main"):
    """판석 바닥 (광장, 보도). 줄눈은 tile 간격 띠. border: 가장자리 띠 머티리얼."""
    C.box(key, x0, x1, y0, y1, z - t, z, kind=kind)
    if col:
        C.col(x0, x1, y0, y1, z - t, z)
    if grout:
        w = 0.06
        x = x0 + tile
        while x < x1 - 0.1:
            C.strip(grout, (x, y0, z), (x, y1, z), w, lift=0.01)
            x += tile
        y = y0 + tile
        while y < y1 - 0.1:
            C.strip(grout, (x0, y, z), (x1, y, z), w, lift=0.01)
            y += tile
    if border:
        bw = 0.5
        for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + bw), (x0, x1, y1 - bw, y1), (x0, x0 + bw, y0, y1),
                                 (x1 - bw, x1, y0, y1)):
            C.decal(border, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], (0, 0, z), (0, 0, 1), up=(0, 1, 0), lift=0.014)


def grass(C, x0, x1, y0, y1, *, z=0.0, t=0.3, col=True, edge=True):
    C.box("grass", x0, x1, y0, y1, z - t, z - 0.02)
    if col:
        C.col(x0, x1, y0, y1, z - t, z - 0.02)
    if edge:
        e = 0.18
        for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + e), (x0, x1, y1 - e, y1), (x0, x0 + e, y0, y1), (x1 - e, x1, y0, y1)):
            C.box("curb", a0, a1, b0, b1, z - 0.05, z + 0.06, kind="detail")


def road(C, axis, c, a0, a1, *, lanes=4, lane_w=2.8, walk=3.2, z=0.0, median=0.0, walk_key="pave",
         line_dash=3.0, col=True, crossings=()):
    """도로 (차로 + 양쪽 보도 + 연석). axis 'x' = X를 따라 뻗음(중심선 y=c), 'y' = Y를 따라 뻗음(x=c).
    차도면 z-0.15, 보도면 z. median > 0이면 가운데에 화단 섬. crossings: 횡단보도 위치(a) 목록.
    반환: dict(road_lo, road_hi, walk_lo, walk_hi, median_lo, median_hi)."""
    half = lanes * lane_w / 2 + median / 2
    zr = z - 0.15

    def B(key, s0, s1, za, zb, kind="main"):
        if axis == "x":
            C.box(key, a0, a1, c + s0, c + s1, za, zb, kind=kind)
        else:
            C.box(key, c + s0, c + s1, a0, a1, za, zb, kind=kind)

    def S(key, s, w, zz, a_from=a0, a_to=a1, lift=0.012):
        if axis == "x":
            C.strip(key, (a_from, c + s, zz), (a_to, c + s, zz), w, lift=lift)
        else:
            C.strip(key, (c + s, a_from, zz), (c + s, a_to, zz), w, lift=lift)

    def COL(s0, s1, za, zb):
        if not col:
            return
        if axis == "x":
            C.col(a0, a1, c + s0, c + s1, za, zb)
        else:
            C.col(c + s0, c + s1, a0, a1, za, zb)

    B("asphalt", -half, half, zr - 0.4, zr)
    COL(-half, half, zr - 0.4, zr)
    for sgn in (-1, 1):
        s_in = sgn * half
        s_out = sgn * (half + walk)
        lo, hi = sorted((s_in, s_out))
        B(walk_key, lo, hi, z - 0.4, z)
        COL(lo, hi, z - 0.4, z)
        cs = sorted((s_in, s_in + sgn * 0.3))
        B("curb", cs[0], cs[1], z - 0.4, z + 0.005, kind="detail")
        # 보도 줄눈 (가로 방향만)
        k = a0 + 1.6
        while k < a1:
            if axis == "x":
                C.strip("pave_d", (k, c + lo, z), (k, c + hi, z), 0.05, lift=0.01)
            else:
                C.strip("pave_d", (c + lo, k, z), (c + hi, k, z), 0.05, lift=0.01)
            k += 1.6
        S("pave_r", sgn * (half + walk * 0.62), walk * 0.3, z)
        # 가장자리선
        S("line", sgn * (half - (median / 2 if False else 0) - 0.25), 0.12, zr)
    # 차선
    lanes_side = lanes // 2
    for sgn in (-1, 1):
        for i in range(1, lanes_side):
            s = sgn * (median / 2 + i * lane_w)
            a = a0
            while a < a1:
                S("line", s, 0.12, zr, a, min(a + line_dash, a1))
                a += line_dash * 2.2
    if median > 0:
        B("curb", -median / 2, median / 2, zr, z + 0.05, kind="detail")
        B("grass", -median / 2 + 0.15, median / 2 - 0.15, zr, z + 0.08)
    else:
        S("line_y", -0.12, 0.1, zr)
        S("line_y", 0.12, 0.1, zr)
    for a in crossings:
        crosswalk(C, axis, c, a, half, zr)
    return {"road_lo": c - half, "road_hi": c + half, "walk_lo": c - half - walk, "walk_hi": c + half + walk,
            "z_road": zr}


def crosswalk(C, axis, c, a, half, zr, *, depth=3.0, bar=0.5):
    s = -half + 0.4
    while s < half - 0.4:
        if axis == "x":
            C.decal("line", [(a - depth / 2, c + s), (a + depth / 2, c + s), (a + depth / 2, c + s + bar),
                             (a - depth / 2, c + s + bar)], (0, 0, zr), (0, 0, 1), up=(0, 1, 0), lift=0.016)
        else:
            C.decal("line", [(c + s, a - depth / 2), (c + s + bar, a - depth / 2), (c + s + bar, a + depth / 2),
                             (c + s, a + depth / 2)], (0, 0, zr), (0, 0, 1), up=(0, 1, 0), lift=0.016)
        s += bar * 2


# ================================================================== buildings

STYLES = {
    #        몸체        띠            창           창 아래     1층
    "office": ("concrete", "concrete_d", "glass", "glass_d", "concrete_d"),
    "apartment": ("warm", "warm_d", "glass", "glass_d", "warm_d"),
    "brick": ("brick", "warm", "glass", "glass_d", "warm_d"),
    "glass": ("glass_t", "mullion", "glass", "glass_d", "concrete"),
}


def _side_frames(x0, x1, y0, y1, r):
    """건물 네 옆면: (이름, 바깥 법선, 면 중심 xy, 가로 방향, 평평한 길이)."""
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [
        ("-y", Vector((0, -1, 0)), Vector((cx, y0, 0)), Vector((1, 0, 0)), w - 2 * r),
        ("+y", Vector((0, 1, 0)), Vector((cx, y1, 0)), Vector((-1, 0, 0)), w - 2 * r),
        ("-x", Vector((-1, 0, 0)), Vector((x0, cy, 0)), Vector((0, -1, 0)), d - 2 * r),
        ("+x", Vector((1, 0, 0)), Vector((x1, cy, 0)), Vector((0, 1, 0)), d - 2 * r),
    ]


def building(C, x0, x1, y0, y1, *, floors=4, style="office", front="-y", sides="-y+y-x+x", seed=0, shop=None,
             sign=None, door=True, roof=True, h0=None, fh=2.7, r=1.0, kind="main", z=0.0, win="band", col=True,
             far=False, cctv=True):
    """도시 블록 건물 하나.
    style: office(흰 콘크리트 + 띠창), apartment(따뜻한 석재 + 낱창), brick(벽돌 상가), glass(청색 유리 고층)
    front: 정면 방향('-y','+y','-x','+x'). sides: 창을 그릴 면 (뒤에 붙은 면은 빼서 삼각형을 아낀다)
    shop: 1층 상가 dict(awning='coral'|'mint'|'teal', name='모나티엄 25', sub='MONATIUM 25')
    sign: 옥상·벽 간판 문자열. far=True면 원경용 단순 블록(창 띠만).
    반환: dict(top=z_top, front_center, front_normal)."""
    rng = random.Random(seed)
    body, band, gl, gl_d, base = STYLES[style]
    if far:
        body = "far"
    h0 = h0 if h0 is not None else (3.2 if shop else 3.0)
    H = z + h0 + floors * fh
    r = min(r, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    fp = hw.rrect(x1 - x0, y1 - y0, r, 3, cx, cy)
    k_main = "far" if far else kind
    C.prism(body, fp, z + (h0 if not far else 0), H, kind=k_main)
    if not far:
        C.prism(base, fp, z, z + h0, kind=k_main)
    if col:
        C.rrcol(x0, x1, y0, y1, z, H, r)        # 둥근 모서리 그대로 (예전 상자는 모서리마다 0.4 m 투명 벽)
        # 발자국 밑 바닥판: 둥근 모서리와 건물 사이 틈(0.4 m 골목, 보도와 0.2 m 띠)이 땅 구멍이 되지 않게
        C.col(x0, x1, y0, y1, z - 0.3, z)
    # 층 띠 (슬래브 끝)
    if not far:
        fp_out = hw.rrect(x1 - x0 + 0.16, y1 - y0 + 0.16, r + 0.08, 3, cx, cy)
        for i in range(floors + 1):
            zb = z + h0 + i * fh
            if i == floors:
                continue
            C.prism(band, fp_out, zb - 0.12, zb + 0.06, kind="detail")
    # 파라펫 + 옥상
    if roof and not far:
        po = hw.rrect(x1 - x0 + 0.2, y1 - y0 + 0.2, r + 0.1, 3, cx, cy)
        pi = hw.rrect(x1 - x0 - 0.4, y1 - y0 - 0.4, max(r - 0.2, 0.05), 3, cx, cy)
        C.ring_prism(band, po, pi, H, H + 0.7, kind="detail")
        C.prism("roof", pi, H, H + 0.05, kind="detail")
        n_units = rng.randint(1, 3)
        for i in range(n_units):
            ux = rng.uniform(x0 + 1.5, x1 - 2.5)
            uy = rng.uniform(y0 + 1.5, y1 - 2.5)
            # 실외기는 옥상 판(H+0.05) 위에 두고 하나마다 4 cm씩 높이를 달리한다: 밑면이 파라펫 밑면(H)과, 겹쳐 놓인
            # 실외기끼리 윗면이 같은 평면이 되지 않게 (난수는 그대로)
            hu = 0.9 + 0.04 * i
            C.box("steel", ux, ux + 1.4, uy, uy + 1.0, H + 0.05, H + 0.05 + hu, kind="detail")
            C.cyl("metal", (ux + 0.7, uy + 0.5, H + 0.05 + hu), (ux + 0.7, uy + 0.5, H + 0.1 + hu), 0.38, segs=10,
                  kind="detail")
        if rng.random() < 0.5:
            tx, ty = rng.uniform(x0 + 2, x1 - 2), rng.uniform(y0 + 2, y1 - 2)
            C.cyl("concrete_d", (tx, ty, H), (tx, ty, H + 2.2), 0.9, segs=12, kind="detail")
            C.cyl("roof", (tx, ty, H + 2.2), (tx, ty, H + 2.5), 0.95, r2=0.3, segs=12, kind="detail")
        else:
            ax, ay = rng.uniform(x0 + 1.5, x1 - 1.5), rng.uniform(y0 + 1.5, y1 - 1.5)
            C.cyl("metal", (ax, ay, H), (ax, ay, H + 3.5), 0.05, segs=6, kind="detail")
            C.cyl("gold", (ax, ay, H + 3.2), (ax, ay, H + 3.3), 0.12, segs=8, kind="detail")
    elif far:
        C.prism("far_d", hw.rrect(x1 - x0 - 1, y1 - y0 - 1, max(r - 0.5, 0.05), 2, cx, cy), H, H + 1.2, kind="far")

    # 옆면 창
    for (nm, N, c0, R, L) in _side_frames(x0, x1, y0, y1, r):
        if nm not in sides or L < 1.5:
            continue
        lift = 0.06 if far else 0.02
        if far:
            for i in range(floors):
                zc = z + h0 + i * fh + fh * 0.5
                C.rect("glass_d" if i % 2 else "far_d", c0 + Vector((0, 0, zc)), N, L * 0.92, fh * 0.42, lift=lift)
            continue
        is_front = (nm == front)
        for i in range(floors):
            zf = z + h0 + i * fh
            if style == "glass":
                continue
            if win == "band" or style == "office":
                wc = c0 + Vector((0, 0, zf + 0.75 + 0.62))
                # 창 층: 유리(under, 약한 편향) → 아래 짙은 유리(fine, +4 mm) → 창살(fine, 짙은 유리보다 1.6 cm 위).
                # 같은 fine끼리는 표준 깊이 버퍼에서 1.6 cm면 약 90 m까지 갈린다
                C.rect(gl, wc, N, L - 0.6, 1.24, lift=lift, kind="under")
                C.rect(gl_d, wc - Vector((0, 0, 0.36)), N, L - 0.6, 0.52, lift=lift + 0.004)
                n_m = max(1, int((L - 0.6) / 1.4))
                for k in range(1, n_m):
                    u = -(L - 0.6) / 2 + k * (L - 0.6) / n_m
                    C.rect("mullion" if style != "brick" else band, wc + R * u, N, 0.1, 1.24, lift=lift + 0.02)
            else:
                bay = 2.2
                n = max(1, int(L / bay))
                for k in range(n):
                    u = -L / 2 + (k + 0.5) * L / n
                    wc = c0 + R * u + Vector((0, 0, zf + 0.7 + 0.65))
                    C.decal(gl, hw.rrect(1.15, 1.3, 0.22, 2), wc, N, lift=lift, kind="under")
                    C.rect(gl_d, wc - Vector((0, 0, 0.36)), N, 1.05, 0.5, lift=lift + 0.004)
                    C.rect(band, wc - Vector((0, 0, 0.75)), N, 1.4, 0.12, lift=lift + 0.003)
                    if style == "apartment" and (k + i) % 3 == 0:
                        # 작은 발코니 난간
                        p = wc - Vector((0, 0, 0.75)) + N * 0.35
                        C.beam("steel", p - R * 0.75, p + R * 0.75, 0.05, 0.05, kind="detail")
                        C.beam("steel", p - R * 0.75 + Vector((0, 0, 0.5)), p + R * 0.75 + Vector((0, 0, 0.5)), 0.05,
                               0.05, kind="detail")
                        for s in (-0.75, 0, 0.75):
                            C.beam("steel", p + R * s, p + R * s + Vector((0, 0, 0.5)), 0.04, 0.04, kind="detail")
                        C.beam(band, p - N * 0.18 - R * 0.8, p - N * 0.18 + R * 0.8, 0.08, 0.4 + 0.0, kind="detail")
        if style == "glass":
            # 유리탑: 멀리언 격자
            zt = H
            n_v = max(2, int(L / 1.5))
            for k in range(n_v + 1):
                u = -L / 2 + k * L / n_v
                p0 = c0 + R * u + Vector((0, 0, z + h0))
                C.strip("mullion", p0, p0 + Vector((0, 0, zt - z - h0)), 0.1, N, lift=lift)
            for i in range(floors + 1):
                zz = z + h0 + i * fh
                # 가로 창살은 세로 창살과 엇갈리는 곳에서 1.5 cm 위 (같은 fine)
                C.strip("mullion", c0 - R * (L / 2) + Vector((0, 0, zz)), c0 + R * (L / 2) + Vector((0, 0, zz)), 0.14,
                        N, lift=lift + 0.015)
        # 1층
        if is_front and shop:
            storefront(C, c0, N, R, L, z, h0, shop, seed=seed)
        elif is_front and door:
            entrance(C, c0 + Vector((0, 0, z)), N, R)
        elif style != "glass":
            # 1층 낱창
            n = max(1, int(L / 3.0))
            for k in range(n):
                u = -L / 2 + (k + 0.5) * L / n
                if is_front and abs(u) < 1.5:
                    continue
                C.decal(gl_d, hw.rrect(1.3, 1.4, 0.25, 2), c0 + R * u + Vector((0, 0, z + 1.6)), N, lift=lift)
        if cctv and is_front and rng.random() < 0.7:
            cctv_cam(C, c0 + R * (L / 2 - 0.3) + Vector((0, 0, z + h0 - 0.2)) + N * 0.02, N, R)
    if sign:
        nm, N, c0, R, L = [f for f in _side_frames(x0, x1, y0, y1, r) if f[0] == front][0]
        sc = c0 + Vector((0, 0, H - 0.9))
        sw = min(L * 0.8, 0.9 * len(sign) + 1.0)
        C.plate("navy", hw.rrect(sw, 1.1, 0.4, 2), sc, N, 0.15, kind="detail")
        C.text("white", sign, 0.7, sc + N * 0.15, N)
    front_frame = [f for f in _side_frames(x0, x1, y0, y1, r) if f[0] == front][0]
    return {"top": H, "front_center": front_frame[2] + Vector((0, 0, z)), "front_normal": front_frame[1],
            "front_right": front_frame[3], "front_len": front_frame[4]}


def entrance(C, base, N, R, *, w=1.0, h=1.8, key="navy", canopy=True):
    """문 (엘프 체격 1.8 m). base = 문 아래 가운데 (벽면 위)."""
    base = Vector(base)
    C.plate(key, hw.rrect(w + 0.36, h + 0.2, 0.18, 2), base + Vector((0, 0, (h + 0.2) / 2)), N, 0.1, kind="detail")
    hw_ = (w + 0.36) / 2
    C.ccol([base + R * (sx * hw_) + N * d + Vector((0, 0, zz)) for sx in (-1, 1) for d in (-0.02, 0.1) for zz in (0, h + 0.2)])   # 문틀 판 (벽에서 0.1 m 나온다)
    C.decal("glass_d", hw.rrect(w, h, 0.12, 2), base + Vector((0, 0, h / 2)) + N * 0.1, N, lift=0.012)
    C.rect("steel", base + Vector((0, 0, h * 0.5)) + N * 0.1 + R * (w * 0.32), N, 0.05, 0.3, lift=0.02)
    if canopy:
        cc = base + Vector((0, 0, h + 0.45)) + N * 0.55
        C.rbox("navy_l", tuple(cc), (abs(R.x) * (w + 1.2) + abs(N.x) * 1.1 + 0.001,
                                    abs(R.y) * (w + 1.2) + abs(N.y) * 1.1 + 0.001, 0.12), kind="detail")


def storefront(C, c0, N, R, L, z, h0, shop, *, seed=0):
    """1층 상가: 유리 진열창, 문, 차양, 간판."""
    name = shop.get("name", "")
    sub = shop.get("sub", "")
    awn = shop.get("awning", "coral")
    W = L - 0.4
    base = Vector(c0) + Vector((0, 0, z))
    C.rect("glass", base + Vector((0, 0, 1.25)), N, W, 1.9, lift=0.02, kind="under")   # 진열창 바탕 (약한 편향)
    C.rect("glass_d", base + Vector((0, 0, 0.75)), N, W, 0.9, lift=0.024)
    n = max(2, int(W / 1.8))
    for k in range(n + 1):
        u = -W / 2 + k * W / n
        C.rect("dark", base + R * u + Vector((0, 0, 1.25)), N, 0.09, 1.9, lift=0.04)   # 창살: 짙은 유리보다 1.6 cm 위
    entrance(C, base, N, R, w=1.0, canopy=False)
    # 차양 (기울어진 판 + 줄무늬)
    depth = 1.1
    ac = base + Vector((0, 0, 2.55)) + N * (depth / 2)
    ang = math.degrees(math.atan2(N.y, N.x))
    # 상자 좌표계: X = R, Y = N
    Mx = Matrix((R, N, Vector((0, 0, 1)))).transposed().to_4x4()
    Mx.translation = ac
    tilt = Matrix.Rotation(math.radians(-18), 4, "X")
    b = C.bm(awn, "detail")
    _bm_box(b, -W / 2, W / 2, -depth / 2, depth / 2, -0.04, 0.04, matrix=Mx @ tilt)
    k = -W / 2
    stripe = 0.5
    i = 0
    while k < W / 2 - 0.01:
        if i % 2 == 0:
            p0 = Mx @ tilt @ Vector((k, -depth / 2, 0.045))
            p1 = Mx @ tilt @ Vector((min(k + stripe, W / 2), -depth / 2, 0.045))
            p2 = Mx @ tilt @ Vector((min(k + stripe, W / 2), depth / 2, 0.045))
            p3 = Mx @ tilt @ Vector((k, depth / 2, 0.045))
            C.poly("white", [p0, p1, p2, p3])
        k += stripe
        i += 1
    # 간판
    sc = base + Vector((0, 0, h0 - 0.35))
    C.plate("navy", hw.rrect(min(W, 1.0 + 0.62 * max(len(name), 3)), 0.62, 0.22, 2), sc, N, 0.12, kind="detail")
    if name:
        C.text("white" if awn != "mint" else "glow", name, 0.38, sc + N * 0.12 + Vector((0, 0, 0.04)), N)
    if sub:
        C.text("gold", sub, 0.14, sc + N * 0.12 - Vector((0, 0, 0.21)), N)


def cctv_cam(C, p, N, R, *, key="white"):
    """감시 카메라 (원작: 모나티엄에 21만 대). 벽 받침 + 몸통 + 렌즈."""
    p = Vector(p)
    C.beam("metal", p, p + N * 0.35, 0.06, 0.06, kind="detail")
    body = p + N * 0.42 - Vector((0, 0, 0.08))
    C.beam(key, body - N * 0.15, body + N * 0.2, 0.16, 0.14, kind="detail")
    C.rect("dark", body + N * 0.205, N, 0.1, 0.09, lift=0.0)
    C.rect("glow", body + N * 0.215 + R * 0.06 + Vector((0, 0, 0.05)), N, 0.025, 0.025, lift=0.0)


# ================================================================== landmarks

def city_hall(C, cx, cy, *, front="-y", portrait=True, screen=True, flags=True, scale=1.0, name_text=True,
              col=True):
    """모나티엄 시청 (원작: 시장 엘레나의 전신 초상이 걸린 시청, 지하 23층, 시청 앞 광장).
    정면 -Y 기준으로 만들고 front가 다르면 지원하지 않는다(배치 쪽에서 맞춘다).
    반환: dict(portico_front_y, tower_top, podium_z, screen_center, portrait_center)."""
    s = scale
    WW, WD, WH = 34 * s, 14 * s, 11.4 * s       # 날개
    TW, TD, TH = 11 * s, 11 * s, 27 * s          # 가운데 탑
    y_front = cy - WD / 2
    PZ = 0.9 * s                                  # 기단 높이
    # 기단
    C.prism("stone_d", hw.rrect(WW + 2, WD + 2, 4.2 * s, 4, cx, cy), 0, PZ, kind="main")
    if col:
        C.col(cx - WW / 2 - 1, cx + WW / 2 + 1, cy - WD / 2 - 1, cy + WD / 2 + 1, 0, PZ)
    # 날개: 양 끝이 둥근 판 (교주 차원 형태 언어)
    wing = hw.rrect(WW, WD, 3.8 * s, 5, cx, cy)
    C.prism("stone", wing, PZ, WH, kind="main")
    if col:
        C.col(cx - WW / 2, cx + WW / 2, cy - WD / 2, cy + WD / 2, PZ, WH)
    # 처마 띠·지붕 난간
    C.prism("navy", hw.rrect(WW + 0.5, WD + 0.5, 4.05 * s, 5, cx, cy), WH - 0.25, WH + 0.25, kind="detail")
    C.ring_prism("stone_d", hw.rrect(WW + 0.3, WD + 0.3, 3.95 * s, 5, cx, cy),
                 hw.rrect(WW - 0.5, WD - 0.5, 3.55 * s, 5, cx, cy), WH + 0.25, WH + 1.0, kind="detail")
    for zb in (PZ + 3.4 * s, PZ + 6.8 * s):
        C.prism("stone_d", hw.rrect(WW + 0.18, WD + 0.18, 3.89 * s, 5, cx, cy), zb - 0.1, zb + 0.08, kind="detail")
    # 날개 앞면 스타디움 창 (3층)
    N = Vector((0, -1, 0))
    R = Vector((1, 0, 0))
    flat = WW - 2 * 3.8 * s
    for row in range(3):
        zc = PZ + 1.75 * s + row * 3.4 * s
        for side in (-1, 1):
            x_from = cx + side * (TW / 2 + 1.2)
            x_to = cx + side * (flat / 2 - 0.6)
            n = int(abs(x_to - x_from) / 2.4)
            for k in range(n):
                x = x_from + side * (k + 0.5) * abs(x_to - x_from) / n
                if screen and side > 0 and row >= 1:
                    continue          # 오른쪽 날개 2~3층은 화면 자리
                c = Vector((x, y_front, zc))
                C.decal("glass", hw.stadium(2.0 * s, 1.0 * s, 4, angle=90), c, N, lift=0.02, kind="under")
                C.decal("glass_d", hw.stadium(0.95 * s, 0.9 * s, 3, cy=-0.45 * s, angle=90), c, N, lift=0.024)
                C.rect("stone_d", c - Vector((0, 0, 1.15 * s)), N, 1.3 * s, 0.14, lift=0.018)
    # 뒷면·옆 둥근 끝의 창 (단순)
    for row in range(3):
        zc = PZ + 1.75 * s + row * 3.4 * s
        for k in range(8):
            x = cx - flat / 2 + (k + 0.5) * flat / 8
            C.decal("glass_d", hw.stadium(1.8 * s, 0.9 * s, 3, angle=90), (x, cy + WD / 2, zc), (0, 1, 0), lift=0.02)
    # 가운데 탑
    tower = hw.rrect(TW, TD, 2.4 * s, 4, cx, cy - 1.0)
    C.prism("stone", tower, WH, TH, kind="main")
    if col:
        C.col(cx - TW / 2, cx + TW / 2, cy - 1 - TD / 2, cy - 1 + TD / 2, WH, TH)
    C.prism("navy", hw.rrect(TW + 0.5, TD + 0.5, 2.65 * s, 4, cx, cy - 1.0), TH - 0.3, TH + 0.3, kind="detail")
    # 탑 머리: 둥근 관 + 금색 고리 + 로고 원판
    C.cyl("stone", (cx, cy - 1, TH + 0.3), (cx, cy - 1, TH + 2.6 * s), 4.2 * s, r2=3.6 * s, segs=24, kind="main")
    C.cyl("gold", (cx, cy - 1, TH + 2.6 * s), (cx, cy - 1, TH + 3.0 * s), 3.7 * s, segs=24, kind="detail")
    C.blob("violet", (cx, cy - 1, TH + 3.0 * s), 3.3 * s, (1, 1, 0.55), segs=20, rings=8)
    C.cyl("gold", (cx, cy - 1, TH + 4.6 * s), (cx, cy - 1, TH + 7.5 * s), 0.12, segs=8, kind="detail")
    C.blob("gold", (cx, cy - 1, TH + 7.6 * s), 0.35, segs=10, rings=6)
    # 로고 원판 (탑 정면 꼭대기)
    lc = Vector((cx, cy - 1 - TD / 2, TH - 2.6 * s))
    C.logo(tuple(lc), 3.2 * s, (0, -1, 0), key="gold", disc="navy", ring="gold", lift=0.03)
    # 탑 옆면 세로 창
    for side in (-1, 1):
        for k in range(3):
            y = cy - 1 - TD / 2 + 2.6 + k * 2.9
            C.decal("glass_d", hw.stadium(5.5 * s, 0.9 * s, 3, angle=90), (cx + side * TW / 2, y, WH + 6.5 * s),
                    (side, 0, 0), lift=0.02)
    # 포르티코 (둥근 기둥 6개 + 지붕 판)
    PY0 = y_front - 5.0 * s
    PH = 8.2 * s
    C.prism("stone", hw.rrect(TW + 6, 5.6 * s, 1.6 * s, 3, cx, PY0 + 2.6 * s), PH, PH + 0.9 * s, kind="main")
    C.prism("navy", hw.rrect(TW + 6.3, 5.9 * s, 1.75 * s, 3, cx, PY0 + 2.6 * s), PH + 0.9 * s, PH + 1.15 * s,
            kind="detail")
    for k in range(6):
        x = cx - (TW + 4) / 2 + k * (TW + 4) / 5
        C.cyl("stone", (x, PY0 + 0.9, PZ), (x, PY0 + 0.9, PH), 0.48 * s, segs=16)
        C.cyl("stone_d", (x, PY0 + 0.9, PZ), (x, PY0 + 0.9, PZ + 0.5), 0.62 * s, segs=16, kind="detail")
        C.cyl("gold", (x, PY0 + 0.9, PH - 0.5), (x, PY0 + 0.9, PH - 0.3), 0.56 * s, segs=16, kind="detail")
        if col:
            C.col(x - 0.48, x + 0.48, PY0 + 0.42, PY0 + 1.38, PZ, PH)
    # 이름 띠
    if name_text:
        nc = Vector((cx, PY0 + 2.6 * s - 2.8 * s - 0.01, PH + 0.45 * s))
        C.text("gold", "모나티엄 시청", 0.62 * s, nc + Vector((0, 0, 0.05)), (0, -1, 0), lift=0.03)
        C.text("navy", "MONATIUM CITY HALL", 0.22 * s, nc - Vector((0, 0, 0.3)), (0, -1, 0), lift=0.03)
    # 계단 (단 높이 0.15, 엘프 자동 오르기 0.28 안)
    # 단마다 자기 디딤 칸만 채운다(맨 윗단만 기단 안쪽 PY0+4까지). 모든 단을 PY0+4까지 겹쳐 쌓으면 양 옆면이 같은 평면에서
    # stone/stone_d로 번갈아 겹쳐 깜빡인다.
    steps = int(PZ / 0.15)
    for i in range(steps):
        z1 = (i + 1) * PZ / steps
        y0 = PY0 + 0.0 - (steps - i) * 0.45
        y1 = y0 + 0.45 if i < steps - 1 else PY0 + 4
        C.box("stone_d" if i % 2 else "stone", cx - TW / 2 - 2.5, cx + TW / 2 + 2.5, y0, y1, 0, z1,
              kind="detail")
    if col:
        for i in range(steps):
            z1 = (i + 1) * PZ / steps
            y0 = PY0 - (steps - i) * 0.45
            C.col(cx - TW / 2 - 2.5, cx + TW / 2 + 2.5, y0, y0 + 0.45, 0, z1)
        C.col(cx - TW / 2 - 2.5, cx + TW / 2 + 2.5, PY0, y_front, 0, PZ)
    # 정문 (큰 둥근 문 + 금테)
    dc = Vector((cx, y_front, PZ))
    C.plate("navy", hw.rrect(4.0 * s, 4.4 * s, 1.2 * s, 4), dc + Vector((0, 0, 2.2 * s)), N, 0.25, kind="detail")
    C.ring("gold", hw.rrect(4.2 * s, 4.6 * s, 1.3 * s, 4), hw.rrect(4.0 * s, 4.4 * s, 1.2 * s, 4),
           dc + Vector((0, 0, 2.2 * s)) + N * 0.25, N, lift=0.01)
    C.decal("glass_d", hw.rrect(1.6 * s, 3.0 * s, 0.6 * s, 3), dc + Vector((-0.9 * s, 0, 1.5 * s)) + N * 0.25, N,
            lift=0.015)
    C.decal("glass_d", hw.rrect(1.6 * s, 3.0 * s, 0.6 * s, 3), dc + Vector((0.9 * s, 0, 1.5 * s)) + N * 0.25, N,
            lift=0.015)
    out = {"portico_front_y": PY0 - steps * 0.45, "tower_top": TH, "podium_z": PZ, "y_front": y_front}
    # 전신 초상 (탑 정면, 포르티코 위)
    if portrait:
        pc = Vector((cx, cy - 1 - TD / 2, WH + 6.8 * s))
        elena_portrait(C, pc, (0, -1, 0), 6.0 * s, 9.6 * s)
        out["portrait_center"] = tuple(pc)
    # 화면 (오른쪽 날개)
    if screen:
        sc = Vector((cx + TW / 2 + 1.2 + (flat / 2 - TW / 2 - 1.8) / 2, y_front, PZ + 6.4 * s))
        sw = min(flat / 2 - TW / 2 - 2.6, 9.0 * s)
        C.screen("cityhall", tuple(sc), (0, -1, 0), sw, sw * 9 / 16, bezel=0.3)
        out["screen_center"] = tuple(sc)
    # 깃발 (남보라 + 금색 로고)
    if flags:
        for side in (-1, 1):
            for k in range(2):
                fx = cx + side * (TW / 2 + 3.2 + k * 4.2)
                banner(C, (fx, y_front, WH - 0.6), N, 1.4 * s, 4.6 * s)
    # 감시 카메라
    for side in (-1, 1):
        cctv_cam(C, (cx + side * (WW / 2 - 4.0), y_front - 0.02, WH - 1.0), N, Vector((side, 0, 0)))
    return out


def banner(C, top_center, normal, w, h, *, key="violet", trim="gold", logo=True):
    """세로 현수막: 봉 + 남보라 천 + 금색 테 + 엘프 로고."""
    N = Vector(normal).normalized()
    R, U, _ = frame(N)
    t = Vector(top_center) + N * 0.12
    C.cyl("gold", t - R * (w / 2 + 0.15), t + R * (w / 2 + 0.15), 0.05, segs=8, kind="detail")
    pts = [(-w / 2, 0), (w / 2, 0), (w / 2, -h), (0, -h - w * 0.3), (-w / 2, -h)]
    C.plate(key, pts, t, N, 0.04, kind="detail")
    C.ring(trim, [(x * 1.0, y) for x, y in pts], [(x * 0.86, (y + 0.12) * 0.97 - 0.06) for x, y in pts], t + N * 0.04,
           N, lift=0.005)
    if logo:
        C.logo(tuple(t + N * 0.04 - U * (h * 0.4)), w * 0.55, N, key="gold", lift=0.008)


def elena_portrait(C, center, normal, w, h, *, frame_key="gold"):
    """시청에 걸린 엘레나 시장의 전신 초상 (원작 서술). 식별 요소만: 연어색 긴 생머리, 흰 가운, 하늘색 원피스,
    짙은 갈색 신. 납작한 색면으로 새로 그렸다. 원작 일러스트를 옮기지 않는다.
    PORTRAIT_elena 노드(UV 0..1)도 함께 둬서 나중에 그림 텍스처로 바꿀 수 있다."""
    c = Vector(center)
    N = Vector(normal).normalized()
    R, U, _ = frame(N)
    # 액자
    C.plate(frame_key, hw.rrect(w + 0.6, h + 0.6, 0.5, 3), c, N, 0.22, kind="detail")
    C.plate("violet_d", hw.rrect(w, h, 0.3, 3), c + N * 0.22, N, 0.02, kind="detail")
    s = h / 9.6
    L0 = 0.26   # 액자 앞면에서 띄우는 거리
    # 층 dz(0~0.02)를 차례(0, 1, 2 …)로 바꿔 한 층에 1 cm씩 띄운다. 예전 1~4 mm 간격은 표준 깊이 버퍼에서 20~45 m부터
    # 깜빡였다(광장에서 탑을 보는 거리). 1 cm면 약 70 m까지 갈린다. 맨 위 층이 판에서 12 cm
    ranks = {v: i for i, v in enumerate(sorted({0.0, 0.002, 0.003, 0.006, 0.010, 0.011, 0.012, 0.013, 0.014, 0.015,
                                                 0.016, 0.018, 0.02}))}

    def D(key, pts, dz=0.0):
        C.decal(key, [(u * s, v * s) for u, v in pts], c + N * L0, N, lift=0.004 + 0.01 * ranks[dz])
    # 바탕: 아래쪽 밝은 띠 (무대 조명)
    D("violet", [(-2.9, -4.7), (2.9, -4.7), (2.9, 1.0), (-2.9, 1.0)])
    D("gold", hw.circle(2.6, 24, 0, 1.6), 0.002)
    D("violet_d", hw.circle(2.35, 24, 0, 1.6), 0.003)
    # 머리 뒤 커튼 (허리 아래까지)
    D("coral_hair", [(-1.75, 2.9), (1.75, 2.9), (1.95, -1.4), (1.2, -1.9), (0.0, -1.5), (-1.2, -1.9), (-1.95, -1.4)], 0.006)
    # 가운 (흰색, 헐렁한 소매)
    D("white", [(-1.5, 0.1), (1.5, 0.1), (2.1, -1.0), (1.8, -3.9), (-1.8, -3.9), (-2.1, -1.0)], 0.010)
    D("mint", [(-0.7, 0.05), (0.7, 0.05), (0.85, -3.4), (-0.85, -3.4)], 0.012)  # 하늘색 원피스
    D("white", [(-2.1, -1.0), (-1.45, -0.3), (-1.2, -2.3), (-1.8, -2.5)], 0.014)  # 소매
    D("white", [(2.1, -1.0), (1.45, -0.3), (1.2, -2.3), (1.8, -2.5)], 0.014)
    # 다리·신
    D("warm", [(-0.6, -3.4), (-0.15, -3.4), (-0.2, -4.35), (-0.55, -4.35)], 0.011)
    D("warm", [(0.15, -3.4), (0.6, -3.4), (0.55, -4.35), (0.2, -4.35)], 0.011)
    D("trunk", [(-0.75, -4.3), (-0.1, -4.3), (-0.1, -4.6), (-0.8, -4.6)], 0.013)
    D("trunk", [(0.1, -4.3), (0.75, -4.3), (0.8, -4.6), (0.1, -4.6)], 0.013)
    # 얼굴·귀
    D("white", hw.circle(1.2, 24, 0, 1.55, rx=1.25), 0.016)
    D("warm", [(-1.2, 1.55), (-2.0, 1.95), (-1.15, 1.85)], 0.015)
    D("warm", [(1.2, 1.55), (2.0, 1.95), (1.15, 1.85)], 0.015)
    # 앞머리 (일자) + 정수리
    D("coral_hair", [(-1.35, 1.95), (-1.25, 2.6), (-0.6, 2.95), (0.6, 2.95), (1.25, 2.6), (1.35, 1.95), (1.0, 1.75),
                (0.5, 1.9), (0.0, 1.75), (-0.5, 1.9), (-1.0, 1.75)], 0.018)
    # 눈 (하늘색) + 볼터치
    D("glass", hw.circle(0.2, 12, -0.45, 1.45, rx=0.16), 0.02)
    D("glass", hw.circle(0.2, 12, 0.45, 1.45, rx=0.16), 0.02)
    D("flower_p", hw.circle(0.16, 12, -0.78, 1.12, rx=0.24), 0.02)
    D("flower_p", hw.circle(0.16, 12, 0.78, 1.12, rx=0.24), 0.02)
    # 시장 신분증·명판
    D("navy", [(-1.6, -4.35), (1.6, -4.35), (1.6, -4.7), (-1.6, -4.7)], 0.02)
    C.text("gold", "ELENA · 시장", 0.22 * s, c + N * (L0 + 0.004 + 0.01 * ranks[0.02] + 0.01) + U * (-4.52 * s), N,
           lift=0.0)   # 명판(맨 위 층)보다 1 cm 위

    def build(b):
        fc = c + N * (L0 - 0.002)
        pts = [fc - R * (w / 2) - U * (h / 2), fc + R * (w / 2) - U * (h / 2), fc + R * (w / 2) + U * (h / 2),
               fc - R * (w / 2) + U * (h / 2)]
        _bm_quad_uv(b, pts, [(0, 0), (1, 0), (1, 1), (0, 1)])
    C.special("PORTRAIT_elena", build, "violet_d", {"portrait": "elena", "aspect": round(w / h, 4)}, kind="fine")




def core_ai(C, cx, cy, *, lit=True, h=34.0, col=True, glow_overlay=False):
    """모나티엄 코어 AI 시설 (원작: 도시를 운영하는 모나티엄 AI, 시청의 코어 AI 룸).
    지하 코어와 이어진 냉각·통신 탑. lit=False면 띠가 꺼진 시안(기동 전).
    glow_overlay=True면 기동 연출 겹침(빛 띠·빛기둥·후광)만 만든다(STAGE_3용)."""
    R0 = 7.0
    if not glow_overlay:
        # 둥근 기단 건물
        C.cyl("stone", (cx, cy, 0), (cx, cy, 5.2), R0, segs=32, smooth=True)
        C.cyl("navy", (cx, cy, 5.2), (cx, cy, 5.6), R0 + 0.3, segs=32, kind="detail")
        C.cyl("stone_d", (cx, cy, 5.6), (cx, cy, 6.2), R0 - 0.6, r2=R0 - 1.4, segs=32, kind="detail")
        if col:
            C.col(cx - R0 * 0.85, cx + R0 * 0.85, cy - R0 * 0.85, cy + R0 * 0.85, 0, 6.2)
        # 탑
        C.cyl("concrete", (cx, cy, 6.2), (cx, cy, h), 3.4, r2=2.6, segs=24)
        if col:
            C.col(cx - 3, cx + 3, cy - 3, cy + 3, 6.2, h)
        for i in range(6):
            z = 9 + i * (h - 12) / 6
            r = 3.4 - (3.4 - 2.6) * (z - 6.2) / (h - 6.2) + 0.25
            C.cyl("navy", (cx, cy, z - 0.35), (cx, cy, z + 0.35), r, segs=24, kind="detail")
            C.cyl("glow" if lit else "glow_off", (cx, cy, z - 0.12), (cx, cy, z + 0.12), r + 0.04, segs=24,
                  kind="fine", cap=False)
        # 꼭대기: 안테나 관 + 후광 고리
        C.cyl("navy", (cx, cy, h), (cx, cy, h + 1.2), 2.9, r2=1.4, segs=24, kind="detail")
        C.cyl("gold", (cx, cy, h + 1.2), (cx, cy, h + 7), 0.18, segs=8, kind="detail")
        C.blob("glow" if lit else "glow_off", (cx, cy, h + 7.3), 0.55, segs=12, rings=8)
        _bm_torus(C.bm("gold", "detail"), (cx, cy, h + 3.2), 3.6, 0.16, seg=32, rseg=6)
        # 문 + 표지
        N = Vector((0, -1, 0))
        dp = Vector((cx, cy - R0, 0))
        entrance(C, dp, N, Vector((1, 0, 0)), w=1.6, h=2.2)
        C.text("navy", "CORE · 코어 AI", 0.5, dp + Vector((0, -0.05, 3.6)), N, lift=0.06)
        C.logo((cx, cy - R0 - 0.02, 4.4), 0.9, (0, -1, 0), key="gold", disc="navy", lift=0.05)
        # 바닥 네트워크 선 (시안, 광장으로 뻗음)
        for a in (200, 250, 290, 340):
            ang = math.radians(a)
            p0 = Vector((cx + math.cos(ang) * R0, cy + math.sin(ang) * R0, 0.0))
            p1 = Vector((cx + math.cos(ang) * (R0 + 14), cy + math.sin(ang) * (R0 + 14), 0.0))
            C.strip("glow" if lit else "glow_off", p0, p1, 0.16, lift=0.02)
    else:
        for i in range(6):
            z = 9 + i * (h - 12) / 6
            r = 3.4 - (3.4 - 2.6) * (z - 6.2) / (h - 6.2) + 0.25
            C.cyl("glow", (cx, cy, z - 0.14), (cx, cy, z + 0.14), r + 0.06, segs=24, kind="fine", cap=False)
            C.cyl("beam", (cx, cy, z - 0.6), (cx, cy, z + 0.6), r + 0.9, segs=24, kind="fine", cap=False)
        C.cyl("beam", (cx, cy, h + 7), (cx, cy, h + 90), 1.2, r2=2.4, segs=16, kind="fine", cap=False)
        C.blob("cyan_hot", (cx, cy, h + 7.3), 0.7, segs=12, rings=8, kind="fine")
        _bm_torus(C.bm("glow", "fine"), (cx, cy, h + 3.2), 3.6, 0.22, seg=32, rseg=6)
        C.cyl("holo_l", (cx, cy, 0.05), (cx, cy, 0.06), R0 + 9, segs=40, kind="fine")
        for a in (200, 250, 290, 340):
            ang = math.radians(a)
            p0 = Vector((cx + math.cos(ang) * R0, cy + math.sin(ang) * R0, 0.0))
            p1 = Vector((cx + math.cos(ang) * (R0 + 14), cy + math.sin(ang) * (R0 + 14), 0.0))
            C.strip("glow", p0, p1, 0.2, lift=0.03)


def _bm_torus(bm, center, R, r, seg=24, rseg=6, axis=(0, 0, 1)):
    c = Vector(center)
    A = Vector(axis).normalized()
    q = A.to_track_quat("Z", "Y").to_matrix()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            p = Vector(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
            ring.append(bm.verts.new(c + q @ p))
        rings.append(ring)
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(rseg):
            j2 = (j + 1) % rseg
            f = bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))
            f.smooth = True


# ================================================================== monorail · highway

def monorail(C, pts, *, z=7.5, pitch=16.0, beam_w=1.0, beam_h=1.3, col=False):
    """도심 순환 모노레일 (원작: 도시 중앙부를 순환하는 모노레일). pts = [(x,y), ...] 직선 구간들.
    궤도 보 + T자 기둥. 기둥 밑동은 지면 z=0(차도면은 -0.15)."""
    for i in range(len(pts) - 1):
        p0 = Vector((*pts[i], z))
        p1 = Vector((*pts[i + 1], z))
        C.beam("concrete", p0, p1, beam_w, beam_h)
        C.beam("concrete_d", p0 - Vector((0, 0, beam_h / 2 + 0.08)), p1 - Vector((0, 0, beam_h / 2 + 0.08)),
               beam_w + 0.2, 0.16, kind="detail")
        d = (p1 - p0)
        L = d.length
        n = max(1, int(L / pitch))
        side = Vector((-d.y, d.x, 0)).normalized()
        for k in range(n + 1):
            p = p0 + d * (k / n)
            C.cyl("concrete", (p.x, p.y, -0.15), (p.x, p.y, z - beam_h / 2 - 1.0), 0.55, segs=14)
            C.beam("concrete", p - Vector((0, 0, beam_h / 2 + 0.6)) - side * 1.3,
                   p - Vector((0, 0, beam_h / 2 + 0.6)) + side * 1.3, 1.1, 0.9)
            if col:
                C.col(p.x - 0.55, p.x + 0.55, p.y - 0.55, p.y + 0.55, -0.15, z - beam_h / 2 - 1.0)
        # 궤도 위 시안 전력선
        C.strip("glow", p0 + Vector((0, 0, beam_h / 2)), p1 + Vector((0, 0, beam_h / 2)), 0.08, lift=0.01)


def monorail_car(C, center, direction, *, n=2, length=8.0, w=2.3, h=2.5, z_beam_top=None, drift=None, sid=None):
    """모노레일 차량 (흰 몸체 + 남색 창 띠 + 시안 띠 + 금색 로고). center = 첫 차량 중심(바닥 높이 z)."""
    D = Vector(direction).normalized()
    S = Vector((-D.y, D.x, 0))
    c0 = Vector(center)
    for i in range(n):
        c = c0 - D * (i * (length + 0.6))
        Mx = Matrix((S, D, Vector((0, 0, 1)))).transposed().to_4x4()
        Mx.translation = c
        # 옆모습: 앞뒤가 둥근 캡슐 (스타디움 단면을 폭 방향으로 돌출)
        prof = hw.stadium(length, h, 6, 0, h / 2)
        b = C.bm("white", "main")
        f0 = [b.verts.new(Mx @ Vector((-w / 2, u, v))) for u, v in prof]
        f1 = [b.verts.new(Mx @ Vector((w / 2, u, v))) for u, v in prof]
        m = len(prof)
        faces = [b.faces.new(list(reversed(f1))), b.faces.new(f0)]
        for k in range(m):
            k2 = (k + 1) % m
            faces.append(b.faces.new((f0[k], f0[k2], f1[k2], f1[k])))
        bmesh.ops.recalc_face_normals(b, faces=faces)
        for sx in (-1, 1):
            N = S * sx
            ctr = c + N * (w / 2) + Vector((0, 0, h * 0.62))
            C.decal("navy", hw.stadium(length - 1.4, 0.9, 4), ctr, N, up=(0, 0, 1), lift=0.02, kind="under")
            for k in range(5):
                u = -length / 2 + 1.4 + k * (length - 2.8) / 4
                C.rect("glass", ctr + D * u * (1 if sx > 0 else 1), N, 0.9, 0.6, lift=0.026)
            C.strip("glow", c + N * (w / 2) + Vector((0, 0, h * 0.3)) - D * (length / 2 - 0.6),
                    c + N * (w / 2) + Vector((0, 0, h * 0.3)) + D * (length / 2 - 0.6), 0.16, N, lift=0.02)
            C.logo(tuple(c + N * (w / 2) + Vector((0, 0, h * 0.62)) + D * (length / 2 - 0.9)), 0.42, tuple(N),
                   key="gold", lift=0.03)
        # 앞창
        if i == 0:
            C.decal("glass_d", hw.rrect(1.6, 0.8, 0.3, 2), c + D * (length / 2 + 0.05) + Vector((0, 0, h * 0.62)), D,
                    lift=0.02)
        C.beam("dark", c - D * (length / 2 - 1.2) - Vector((0, 0, 0.3)), c + D * (length / 2 - 1.2) - Vector((0, 0, 0.3)),
               1.0, 0.6, kind="detail")


def highway(C, *, x_ramp0, x_ramp1, y_c, z_deck=9.0, x_end=None, width=11.0, lanes=3, pillar_pitch=18.0,
            sign=True, col=False):
    """모나티엄-에르피엔 고속도로(알프토반) 진입부. 원작: 1막에서 엘레나가 흑뉴아를 이 고속도로로 끌어들인다.
    x_ramp0(지면, 도로 z=-0.15)에서 x_ramp1(z_deck)까지 오르막, 그 뒤 x_end까지 고가 상판."""
    x_end = x_end if x_end is not None else x_ramp1 + 80
    hw_ = width / 2
    zr = -0.15
    n = 12
    for i in range(n):
        xa = x_ramp0 + (x_ramp1 - x_ramp0) * i / n
        xb = x_ramp0 + (x_ramp1 - x_ramp0) * (i + 1) / n
        ta, tb = i / n, (i + 1) / n
        sa = ta * ta * (3 - 2 * ta)
        sb = tb * tb * (3 - 2 * tb)
        za, zb = zr + (z_deck - zr) * sa, zr + (z_deck - zr) * sb
        _deck_seg(C, xa, xb, y_c, hw_, za, zb, rail=True)
        if col:
            C.col(xa, xb, y_c - hw_, y_c + hw_, min(za, zb) - 0.5, max(za, zb))
        if i % 3 == 2 and zb > 2:
            for s in (-1, 1):
                C.cyl("concrete", (xb, y_c + s * (hw_ - 1.5), zr), (xb, y_c + s * (hw_ - 1.5), zb - 1.0), 0.6, segs=12)
    _deck_seg(C, x_ramp1, x_end, y_c, hw_, z_deck, z_deck, rail=True)
    k = x_ramp1 + pillar_pitch / 2
    while k < x_end:
        C.cyl("concrete", (k, y_c, zr), (k, y_c, z_deck - 1.6), 1.1, segs=16)
        C.beam("concrete", (k, y_c - hw_ + 0.5, z_deck - 1.25), (k, y_c + hw_ - 0.5, z_deck - 1.25), 1.6, 0.7)
        k += pillar_pitch
    # 차선
    for i in range(1, lanes * 2):
        s = -hw_ + 0.6 + i * (width - 1.2) / (lanes * 2)
        if i == lanes:
            continue
        C.strip("line", (x_ramp1, y_c + s, z_deck), (x_end, y_c + s, z_deck), 0.12, lift=0.02)
    C.strip("line_y", (x_ramp1, y_c, z_deck), (x_end, y_c, z_deck), 0.14, lift=0.02)
    if sign:
        gantry(C, x_ramp0 - 4, y_c, hw_ + 1.5, [("알프토반 1", "ALFTOBAHN 1"), ("에르피엔 26 mi →", "ERPIEN")])


def _deck_seg(C, xa, xb, y_c, hw_, za, zb, *, rail=True):
    b = C.bm("asphalt", "main")
    pts = [(xa, y_c - hw_, za), (xb, y_c - hw_, zb), (xb, y_c + hw_, zb), (xa, y_c + hw_, za)]
    lo = [Vector((p[0], p[1], p[2] - 0.9)) for p in pts]
    hi = [Vector(p) for p in pts]
    vh = [b.verts.new(p) for p in hi]
    vl = [b.verts.new(p) for p in lo]
    b.faces.new(vh)
    b.faces.new(list(reversed(vl)))
    for i in range(4):
        j = (i + 1) % 4
        b.faces.new((vl[i], vl[j], vh[j], vh[i]))
    if rail:
        for s in (-1, 1):
            y0 = y_c + s * hw_
            y1 = y0 - s * 0.45
            yy = sorted((y0, y1))
            bb = C.bm("concrete", "detail")
            q = [(xa, yy[0], za), (xb, yy[0], zb), (xb, yy[1], zb), (xa, yy[1], za)]
            v0 = [bb.verts.new(Vector(p)) for p in q]
            v1 = [bb.verts.new(Vector((p[0], p[1], p[2] + 0.9))) for p in q]
            bb.faces.new(v1)
            for i in range(4):
                j = (i + 1) % 4
                bb.faces.new((v0[i], v0[j], v1[j], v1[i]))
            C.strip("violet", Vector((xa, y0 - s * 0.0, za + 0.65)), Vector((xb, y0, zb + 0.65)), 0.14,
                    (0, s, 0), lift=0.02)


def gantry(C, x, y_c, half, panels):
    """도로 위 표지 문형 (남색 판 + 흰 글자, 미국 단위계 mi: 원작 모나티엄은 미국 단위계를 쓴다)."""
    for s in (-1, 1):
        C.cyl("metal", (x, y_c + s * half, -0.15), (x, y_c + s * half, 6.4), 0.18, segs=10)
    C.beam("metal", (x, y_c - half, 6.2), (x, y_c + half, 6.2), 0.2, 0.25)
    C.beam("metal", (x, y_c - half, 5.4), (x, y_c + half, 5.4), 0.15, 0.15)
    n = len(panels)
    pw = (2 * half - 1.0) / n
    for i, (ko, en) in enumerate(panels):
        yc = y_c - half + 0.5 + pw * (i + 0.5)
        c = Vector((x - 0.12, yc, 5.85))
        C.plate("navy", hw.rrect(pw - 0.4, 1.6, 0.25, 2), c, (-1, 0, 0), 0.1, up=(0, 0, 1), kind="detail")
        C.text("white", ko, 0.46, c + Vector((-0.11, 0, 0.22)), (-1, 0, 0))
        C.text("glow", en, 0.24, c + Vector((-0.11, 0, -0.38)), (-1, 0, 0))


# ================================================================== street furniture

def lamp(C, x, y, *, h=3.6, yaw=0.0, lit=False, z=0.0, arm=True):
    """가로등: 검은 기둥 + 금색 고리 + 둥근 등갓 (원작 배경의 검은 가로등을 교주 차원 문법으로). 약 150 삼각형."""
    C.cyl("dark", (x, y, z), (x, y, z + 0.35), 0.16, r2=0.12, segs=8, kind="detail")
    C.cyl("dark", (x, y, z + 0.35), (x, y, z + h), 0.065, r2=0.05, segs=6, kind="detail", cap=False)
    C.cyl("gold", (x, y, z + 0.35), (x, y, z + 0.45), 0.1, segs=8, kind="detail", cap=False)
    C.cyl("dark", (x, y, z + h), (x, y, z + h + 0.12), 0.2, r2=0.24, segs=8, kind="detail")
    C.cyl("lamp" if lit else "lamp_off", (x, y, z + h + 0.12), (x, y, z + h + 0.5), 0.2, r2=0.17, segs=8,
          kind="detail", cap=False)
    C.cyl("dark", (x, y, z + h + 0.5), (x, y, z + h + 0.68), 0.24, r2=0.04, segs=8, kind="detail")
    C.col(x - 0.12, x + 0.12, y - 0.12, y + 0.12, z, z + 2.2)    # 받침(반지름 0.16)과 기둥(0.065) 사이


def bench(C, x, y, *, yaw=0.0, z=0.0, length=1.5):
    """벤치 (엘프 좌판 높이 0.32 m). 정면 -Y(앉은 사람이 보는 방향)를 yaw로 돌린다."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    b = C.bm("wood", "detail")
    for k in range(3):
        y0 = -0.2 + k * 0.14
        _bm_box(b, -length / 2, length / 2, y0, y0 + 0.11, 0.28, 0.33, matrix=Mx)
    for k in range(2):
        z0 = 0.45 + k * 0.15
        _bm_box(b, -length / 2, length / 2, 0.2, 0.25, z0, z0 + 0.1, matrix=Mx)
    bd = C.bm("dark", "detail")
    for s in (-1, 1):
        xx = s * (length / 2 - 0.15)
        _bm_box(bd, xx - 0.04, xx + 0.04, -0.18, 0.18, 0, 0.28, matrix=Mx)
        _bm_box(bd, xx - 0.04, xx + 0.04, 0.21, 0.27, 0.28, 0.65, matrix=Mx)   # 등판 살 앞면(0.2)보다 1 cm 뒤
    C.lcol(x, y, z, yaw, -length / 2, length / 2, -0.2, 0.22, 0, 0.33)        # 좌판 (밟고 올라설 수 있다)
    C.lcol(x, y, z, yaw, -length / 2, length / 2, 0.2, 0.27, 0, 0.65)         # 등판


def tree(C, x, y, *, h=4.6, seed=0, z=0.0, scale=1.0, kind="main", leaf=None, lod=0):
    """가로수: 줄기 + 둥근 잎 덩어리 3개 (원작 배경의 둥근 활엽수). lod=1이면 원경용(덩어리 2개, 낮은 분할)."""
    rng = random.Random(seed)
    s = scale
    C.cyl("trunk", (x, y, z), (x, y, z + h * 0.55 * s), 0.17 * s, r2=0.12 * s, segs=8 if lod == 0 else 5,
          kind=kind, cap=lod == 0)
    if kind != "far":
        C.col(x - 0.14 * s, x + 0.14 * s, y - 0.14 * s, y + 0.14 * s, z, z + min(h * 0.55 * s, 2.4))   # 줄기
    keys = leaf or ("leaf", "leaf_l", "leaf_d")
    for i in range(3 if lod == 0 else 2):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.3, 0.7) * s
        cz = z + h * s * rng.uniform(0.62, 0.8)
        # 덩어리마다 다른 방향으로 돌린다: 같은 분할의 구가 겹치면 나란한 면이 몇 mm 사이로 맞붙어 깜빡인다 (난수는 그대로)
        C.blob(keys[i % len(keys)], (x + math.cos(a) * rr, y + math.sin(a) * rr, cz),
               h * s * rng.uniform(0.22, 0.28) * (1.0 if lod == 0 else 1.15), (1, 1, 0.85),
               segs=10 if lod == 0 else 7, rings=6 if lod == 0 else 4, kind=kind, rot_z=0.29 * (i + 1) + 0.13 * (seed % 5))


def planter(C, x0, x1, y0, y1, *, z=0.0, hedge=True, h=0.55, col=True):
    """흰 화단 상자 + 다듬은 생울타리 (원작 배경)."""
    C.box("white", x0, x1, y0, y1, z, z + h, kind="detail")
    C.box("soil", x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, z + h, z + h + 0.02, kind="detail")
    if col:
        C.col(x0, x1, y0, y1, z, z + h)
    if hedge:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lx, ly = (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1
        C.blob("hedge", (cx, cy, z + h + 0.1), 1.0, (lx, ly, 0.45), segs=12, rings=6)
        if col:
            # 생울타리 덩어리(타원체) 윗부분의 볼록 껍질: 화단에 뛰어올라 울타리 속에 서지 않게
            pts = []
            for la in (0, 15, 35, 60, 90):
                for k in range(12):
                    a = 2 * math.pi * k / 12
                    pts.append((cx + lx * math.cos(math.radians(la)) * math.cos(a), cy + ly * math.cos(math.radians(la)) * math.sin(a),
                                z + h + 0.1 + 0.45 * math.sin(math.radians(la))))
            pts += [(cx + lx * math.cos(2 * math.pi * k / 12), cy + ly * math.sin(2 * math.pi * k / 12), z + h) for k in range(12)]
            C.ccol(pts)


def fence(C, p0, p1, *, h=0.85, pitch=1.6, key="wood", z=0.0):
    """나무 난간 (원작 배경의 낮은 난간). 기둥 + 가로대 2줄 + 세로살."""
    P0, P1 = Vector((*p0[:2], z)), Vector((*p1[:2], z))
    d = P1 - P0
    L = d.length
    n = max(1, int(L / pitch))
    for k in range(n + 1):
        p = P0 + d * (k / n)
        C.beam(key, p, p + Vector((0, 0, h)), 0.1, 0.1, kind="detail")
    for zz in (h * 0.45, h - 0.05):
        C.beam(key, P0 + Vector((0, 0, zz)), P1 + Vector((0, 0, zz)), 0.07, 0.09, kind="detail")
    m = int(L / 0.3)
    for k in range(1, m):
        p = P0 + d * (k / m)
        C.beam("wood_d", p + Vector((0, 0, 0.12)), p + Vector((0, 0, h - 0.08)), 0.035, 0.035, kind="detail")
    if L > 1e-3:
        mid = (P0 + P1) / 2
        C.ocol((mid.x, mid.y, z), (L + 0.1, 0.12, h), math.degrees(math.atan2(d.y, d.x)))


def vending(C, x, y, *, yaw=0.0, z=0.0, key="red", simple=False):
    """자판기 (원작: 모나티엄 자판기에는 500원을 넣는다). 정면 -Y를 yaw로 돌림.
    simple=True면 머티리얼 4개(몸체, 짙은 판, 유리, 발광)로 줄인 소품판."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    _bm_box(C.bm(key, "detail"), -0.42, 0.42, -0.3, 0.3, 0, 1.55, matrix=Mx)
    _bm_box(C.bm("dark", "detail"), -0.44, 0.44, -0.32, 0.32, 1.55, 1.62, matrix=Mx)
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    c = Mx @ Vector((0, -0.3, 0))
    C.rect("glass_a", c + Vector((0, 0, 1.0)), N, 0.62, 0.62, lift=0.022)   # 반투명 진열창: 상품(0.012)보다 1 cm 앞
    R = (Mx.to_3x3() @ Vector((1, 0, 0))).normalized()
    for row in range(3):
        for k in range(4):
            col = ("glow" if (row + k) % 2 else "dark") if simple else ("hazard", "mint", "coral", "glass")[(row + k) % 4]
            C.rect(col, c + Vector((0, 0, 0.82 + row * 0.18)) + R * (-0.22 + k * 0.147), N, 0.08, 0.12, lift=0.012)
    C.rect("dark", c + Vector((0, 0, 0.28)), N, 0.6, 0.18, lift=0.01)
    C.rect("glow", c + Vector((0, 0, 0.55)) + R * 0.22, N, 0.12, 0.06, lift=0.012)
    C.text("glow" if simple else "white", "500원", 0.07, c + Vector((0, 0, 0.55)) - R * 0.12, N, lift=0.012)
    C.text("glow" if simple else "white", "MONATIUM 25", 0.08, c + Vector((0, 0, 1.43)), N, lift=0.012)
    C.lcol(x, y, z, yaw, -0.44, 0.44, -0.32, 0.32, 0, 1.62)


def bollard(C, x, y, *, z=0.0):
    C.cyl("dark", (x, y, z), (x, y, z + 0.6), 0.1, segs=8, kind="detail")
    C.cyl("gold", (x, y, z + 0.5), (x, y, z + 0.55), 0.105, segs=8, kind="detail")
    C.col(x - 0.1, x + 0.1, y - 0.1, y + 0.1, z, z + 0.6)


def cctv_pole(C, x, y, *, yaw=0.0, h=4.2, z=0.0):
    """감시 카메라 기둥 (원작: 시청 앞 광장 등 모나티엄 곳곳에 21만 대)."""
    C.cyl("metal", (x, y, z), (x, y, z + h), 0.06, segs=8, kind="detail")
    N = Vector((math.sin(math.radians(yaw)) * -1, -math.cos(math.radians(yaw)), 0))
    R = Vector((-N.y, N.x, 0))
    cctv_cam(C, (x, y, z + h - 0.15), N, R)
    C.blob("white", (x, y, z + h + 0.05), 0.13, (1, 1, 0.7), segs=8, rings=4)
    C.col(x - 0.07, x + 0.07, y - 0.07, y + 0.07, z, z + 2.2)


def street_sign(C, x, y, text_ko, text_en, *, yaw=0.0, z=0.0, h=2.6, w=1.5):
    """도로명 표지 (헌글: 한글 + 로마자 혼용)."""
    C.cyl("metal", (x, y, z), (x, y, z + h), 0.05, segs=8, kind="detail")
    C.col(x - 0.06, x + 0.06, y - 0.06, y + 0.06, z, z + 2.0)
    N = Vector((-math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)), 0))
    c = Vector((x, y, z + h - 0.3)) + N * 0.06
    C.plate("navy", hw.rrect(w, 0.48, 0.12, 2), c, N, 0.04, kind="detail")
    C.plate("navy", hw.rrect(w, 0.48, 0.12, 2), c, -N, 0.04, kind="detail")
    for sgn in (1, -1):
        C.text("white", text_ko, 0.2, c + N * 0.04 * sgn + Vector((0, 0, 0.07)), N * sgn, lift=0.006)
        C.text("glow", text_en, 0.1, c + N * 0.04 * sgn - Vector((0, 0, 0.14)), N * sgn, lift=0.006)


def holo_ad(C, center, normal, w, h, text_ko, text_en=None, *, frame_key="metal"):
    """홀로 광고판 (사이버펑크 클리셰가 섞인 모나티엄). 금속 틀 + 반투명 시안 판 + 발광 글자."""
    c = Vector(center)
    N = Vector(normal).normalized()
    R, U, _ = frame(N)
    for s in (-1, 1):
        C.beam(frame_key, c + R * (s * w / 2) - U * (h / 2 + 0.6), c + R * (s * w / 2) + U * (h / 2 + 0.2), 0.12, 0.12,
               kind="detail")
    C.beam(frame_key, c - R * (w / 2) - U * (h / 2 + 0.1), c + R * (w / 2) - U * (h / 2 + 0.1), 0.1, 0.1, kind="detail")
    C.rect("holo", c, N, w, h, lift=0.003)      # 앞뒤 두 장을 6 mm 띄운다(같은 평면이면 반투명이 겹쳐 깜빡임)
    C.rect("holo", c, -N, w, h, lift=0.003)
    C.text("glow", text_ko, h * 0.32, c + U * (h * 0.12), N, lift=0.02)
    C.text("glow", text_ko, h * 0.32, c + U * (h * 0.12), -N, lift=0.02)
    if text_en:
        C.text("cyan_hot", text_en, h * 0.13, c - U * (h * 0.25), N, lift=0.02)
        C.text("cyan_hot", text_en, h * 0.13, c - U * (h * 0.25), -N, lift=0.02)


def trash_bin(C, x, y, *, z=0.0):
    C.cyl("navy_l", (x, y, z), (x, y, z + 0.7), 0.24, segs=10, kind="detail")
    C.cyl("dark", (x, y, z + 0.7), (x, y, z + 0.78), 0.26, r2=0.2, segs=10, kind="detail")
    C.cyl("teal", (x, y, z + 0.5), (x, y, z + 0.56), 0.245, segs=10, kind="detail")
    C.col(x - 0.25, x + 0.25, y - 0.25, y + 0.25, z, z + 0.78)


def alert_beacon(C, lid, base, *, color="#ff4a3a", blink=0.8, group="alert", siren=True):
    """경보등 (LIGHT_<lid>): 받침 + 꺼진 렌즈(항상 보임) + 발광 렌즈(미션이 켜고 끔).
    속성은 prologue 레벨의 경고등과 같다: emissiveToggle, group, on, blink, color."""
    b = Vector(base)
    C.cyl("metal", tuple(b), tuple(b + Vector((0, 0, 0.12))), 0.2, segs=12, kind="detail")
    C.cyl("alert_d", tuple(b + Vector((0, 0, 0.12))), tuple(b + Vector((0, 0, 0.42))), 0.16, r2=0.11, segs=12,
          kind="detail")
    C.cyl("gold", tuple(b + Vector((0, 0, 0.42))), tuple(b + Vector((0, 0, 0.47))), 0.07, segs=8, kind="detail")

    def build(bm):
        _bm_cyl(bm, b + Vector((0, 0, 0.13)), b + Vector((0, 0, 0.43)), 0.168, segs=12, r2=0.118)
    C.special(f"LIGHT_{lid}", build, "alert", {"emissiveToggle": 1, "group": group, "on": 0, "blink": blink,
                                               "color": color, "range": 18.0}, kind="fine")
    if siren:
        # 나팔 스피커 (경보음 FX 지점)
        C.cyl("white", tuple(b + Vector((0.0, 0, -0.35))), tuple(b + Vector((0.0, -0.45, -0.25))), 0.05, r2=0.18,
              segs=10, kind="detail")


# ================================================================== R41: 차원문 · 차원 틈

def _node_obj(name, bm, key, parent=None, props=None, matrix=None, no_outline=False, outline=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    cb.assign(o, M(key))
    if parent is not None:
        o.parent = parent
    if matrix is not None:
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = matrix
    o["collider"] = 0
    if no_outline or is_glow(key):
        o["noOutline"] = 1
    if outline is not None:
        o["outline"] = outline
    for k, v in (props or {}).items():
        o[k] = v
    return o


def _spiral(bm, r0, r1, turns, arms, width, z, seg=40):
    for a in range(arms):
        off = 2 * math.pi * a / arms
        prev = None
        for i in range(seg + 1):
            t = i / seg
            ang = off + t * turns * 2 * math.pi
            r = r0 + (r1 - r0) * t
            wv = width * (0.3 + 0.7 * math.sin(math.pi * t))
            c = Vector((math.cos(ang) * r, math.sin(ang) * r, z))
            n = Vector((math.cos(ang), math.sin(ang), 0))
            pa = bm.verts.new(c - n * wv / 2)
            pb = bm.verts.new(c + n * wv / 2)
            if prev:
                bm.faces.new((prev[0], prev[1], pb, pa))
            prev = (pa, pb)


def gate_r41(C, gid, center, *, radius=18.0, tilt=60.0, yaw=0.0, segments=14, spin=24.0, scale_open=1.0):
    """R41 대규모 침공 차원문 GATE_<gid> (1막 개전용, r41-style.md: 고리 마디의 마젠타 슬릿등, 마젠타 소용돌이).
    노드: GATE_<gid> (위치·기울기, 스케일 0→1로 '열림' 연출)
          ├ GATE_<gid>_frame   제국 흑 마디 고리 (45° 모따기 덩어리)
          ├ GATE_<gid>_slits   마젠타 슬릿등 (UNLIT)
          ├ GATE_<gid>_vortex  마젠타 소용돌이 (UNLIT 반투명, spin)
          └ GATE_<gid>_swirl   밝은 나선 (UNLIT, 반대 spin)
    고리면은 로컬 XY, 로컬 -Z가 '앞'(차원문에서 나오는 쪽). tilt: X축 기울기(도), yaw: Z 회전(도)."""
    Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
          @ Matrix.Rotation(math.radians(tilt), 4, "X"))
    root = cb.empty(f"GATE_{gid}", size=1.0)
    root.matrix_world = Mx
    root["gate"] = "r41"
    root["radius"] = radius
    root["open"] = scale_open
    rr = radius
    # 마디 고리
    bf = bmesh.new()
    bs = bmesh.new()
    gap = 0.06
    th = rr * 0.16
    dep = rr * 0.12
    for i in range(segments):
        a0 = 2 * math.pi * (i + gap) / segments
        a1 = 2 * math.pi * (i + 1 - gap) / segments
        steps = 3
        pts_o, pts_i = [], []
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            pts_o.append((math.cos(a), math.sin(a)))
        # 모따기 단면: 안·바깥 반지름, 앞뒤 깊이
        sec = [(rr - th / 2, -dep / 2 + dep * 0.25), (rr - th / 2 + th * 0.25, -dep / 2), (rr + th / 2 - th * 0.25, -dep / 2),
               (rr + th / 2, -dep / 2 + dep * 0.25), (rr + th / 2, dep / 2 - dep * 0.25), (rr + th / 2 - th * 0.25, dep / 2),
               (rr - th / 2 + th * 0.25, dep / 2), (rr - th / 2, dep / 2 - dep * 0.25)]
        rings = []
        for (cx_, cy_) in pts_o:
            rings.append([bf.verts.new(Vector((cx_ * r_, cy_ * r_, z_))) for (r_, z_) in sec])
        m = len(sec)
        for k in range(steps):
            for j in range(m):
                j2 = (j + 1) % m
                bf.faces.new((rings[k][j], rings[k + 1][j], rings[k + 1][j2], rings[k][j2]))
        bf.faces.new(list(reversed(rings[0])))
        bf.faces.new(rings[-1])
        # 슬릿등: 앞면(-Z)에 가는 마젠타 띠 + 바깥 테 쪽 짧은 막대
        am = (a0 + a1) / 2
        for da in (-0.25, 0.25):
            a = am + da * (a1 - a0) / 2
            r_in, r_out = rr - th * 0.28, rr + th * 0.28
            w = 0.035 * rr
            c, s_ = math.cos(a), math.sin(a)
            t = Vector((-s_, c, 0))
            p0 = Vector((c * r_in, s_ * r_in, -dep / 2 - 0.05))
            p1 = Vector((c * r_out, s_ * r_out, -dep / 2 - 0.05))
            q = [p0 - t * w, p1 - t * w, p1 + t * w, p0 + t * w]
            vs = [bs.verts.new(p) for p in q]
            f = bs.faces.new(vs)
            f.normal_update()
            if f.normal.z > 0:
                f.normal_flip()
    # 안쪽 테 (건메탈)
    bm_in = bmesh.new()
    _bm_torus(bm_in, (0, 0, 0), rr - th / 2 - rr * 0.02, rr * 0.03, seg=48, rseg=6)
    fr = _node_obj(f"GATE_{gid}_frame", bf, "r41_shell", parent=root, outline=0.12)
    _node_obj(f"GATE_{gid}_rim", bm_in, "r41_metal", parent=root, outline=0.06)
    _node_obj(f"GATE_{gid}_slits", bs, "magenta", parent=root)
    # 소용돌이: 바깥 보라 → 마젠타 → 밝은 중심
    bv = bmesh.new()
    for (r_, z_, key) in ((rr * 0.97, 0.0, None),):
        pass
    disc = [Vector((math.cos(2 * math.pi * i / 48) * rr * 0.9, math.sin(2 * math.pi * i / 48) * rr * 0.9, 0.0))
            for i in range(48)]
    bv.faces.new([bv.verts.new(p) for p in disc])
    _node_obj(f"GATE_{gid}_vortex", bv, "vortex", parent=root, props={"spin": f"0,{spin},0"})
    bv2 = bmesh.new()
    disc2 = [Vector((math.cos(2 * math.pi * i / 32) * rr * 0.35, math.sin(2 * math.pi * i / 32) * rr * 0.35, -0.3))
             for i in range(32)]
    bv2.faces.new([bv2.verts.new(p) for p in disc2])
    _node_obj(f"GATE_{gid}_core", bv2, "vortex_l", parent=root)
    bsw = bmesh.new()
    _spiral(bsw, rr * 0.12, rr * 0.88, 0.9, 5, rr * 0.07, -0.15)
    _node_obj(f"GATE_{gid}_swirl", bsw, "vortex_v", parent=root, props={"spin": f"0,{-spin * 1.6:g},0"})
    bsw2 = bmesh.new()
    _spiral(bsw2, rr * 0.08, rr * 0.7, 0.7, 3, rr * 0.035, -0.22)
    _node_obj(f"GATE_{gid}_streaks", bsw2, "vortex_l", parent=root, props={"spin": f"0,{spin * 2.2:g},0"})
    C.add_node(root)
    C.marker(f"LIGHT_gate_{gid}", tuple(Vector(center)), props={"color": GLOW["magenta"], "intensity": 6.0,
                                                               "range": radius * 6, "pointLight": 1})
    return root


def rift(C, rid, center, *, size=2.2, yaw=0.0, tilt=0.0, seed=0, open_state=True, flicker=0.35):
    """R41 수색용 작은 차원 틈 RIFT_<rid> (D-7: 선언 방송 시점, 수색 진압반이 차원을 뒤짐).
    찢긴 마젠타 틈 + 둘레의 깨진 조각 + 빛 번짐. 노드 구성:
      RIFT_<rid>            위치·방향 (속성 rift=1, flicker=초 간격 제안, size)
      ├ RIFT_<rid>_open     열린 상태: 찢긴 틈(밝은 마젠타 중심 + 보라 테) — 몽타주가 깜빡임
      ├ RIFT_<rid>_glow     빛 번짐 (UNLIT 반투명)
      └ RIFT_<rid>_closed   닫힌 상태: 가는 실금 한 줄 (기본 숨김 hidden=1)
    틈 면은 로컬 XZ(정면 -Y). 하늘 틈은 tilt로 아래를 향하게 기울인다."""
    rng = random.Random(seed)
    Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
          @ Matrix.Rotation(math.radians(tilt), 4, "X"))
    root = cb.empty(f"RIFT_{rid}", size=0.5)
    root.matrix_world = Mx
    root["rift"] = 1
    root["flicker"] = flicker
    root["size"] = size
    root["state"] = "open" if open_state else "closed"

    def jag(n, half_len, half_w, jitter):
        """세로로 길쭉한 찢김 외곽선 (u=가로, v=세로)."""
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            v = -half_len + 2 * half_len * t
            w = half_w * math.sin(math.pi * t) ** 0.8
            left.append((-w * (1 + rng.uniform(-jitter, jitter)) + rng.uniform(-0.04, 0.04) * size, v))
            right.append((w * (1 + rng.uniform(-jitter, jitter)) + rng.uniform(-0.04, 0.04) * size, v))
        return right + list(reversed(left[1:-1]))

    def face_bm(pts, y):
        b = bmesh.new()
        vs = [b.verts.new(Vector((u, y, v))) for u, v in pts]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
        bmesh.ops.triangulate(b, faces=[f])
        return b
    L = size
    outer = jag(12, L / 2, L * 0.3, 0.35)
    inner = [(u * 0.62, v * 0.9) for u, v in outer]
    core = [(u * 0.24, v * 0.75) for u, v in outer]
    o_open = cb.empty(f"RIFT_{rid}_open", size=0.3)
    o_open.parent = root
    _node_obj(f"RIFT_{rid}_edge", face_bm(outer, 0.0), "violet_glow", parent=o_open)
    _node_obj(f"RIFT_{rid}_tear", face_bm(inner, -0.02), "magenta", parent=o_open)
    _node_obj(f"RIFT_{rid}_core", face_bm(core, -0.04), "cyan_hot", parent=o_open)
    # 깨진 조각 (작은 삼각 파편이 틈 둘레에 떠 있음)
    bsh = bmesh.new()
    for i in range(9):
        a = rng.uniform(0, 2 * math.pi)
        rr_ = rng.uniform(0.35, 0.7) * L
        c = Vector((math.cos(a) * rr_ * 0.6, rng.uniform(-0.1, 0.1), math.sin(a) * rr_))
        s_ = rng.uniform(0.05, 0.12) * L
        tri = [c + Vector((0, 0, s_)), c + Vector((s_ * 0.8, 0, -s_ * 0.6)), c + Vector((-s_ * 0.7, 0, -s_ * 0.5))]
        vs = [bsh.verts.new(p) for p in tri]
        bsh.faces.new(vs)
    _node_obj(f"RIFT_{rid}_shards", bsh, "violet_glow", parent=o_open)
    bg = bmesh.new()
    ring_pts = [Vector((math.cos(2 * math.pi * i / 24) * L * 0.42, 0.04, math.sin(2 * math.pi * i / 24) * L * 0.62))
                for i in range(24)]
    bg.faces.new([bg.verts.new(p) for p in ring_pts])
    _node_obj(f"RIFT_{rid}_glow", bg, "rift", parent=o_open)
    bh = bmesh.new()
    halo = [Vector((math.cos(2 * math.pi * i / 24) * L * 0.75, 0.08, math.sin(2 * math.pi * i / 24) * L * 0.95))
            for i in range(24)]
    bh.faces.new([bh.verts.new(p) for p in halo])
    _node_obj(f"RIFT_{rid}_halo", bh, "vortex_v", parent=o_open)
    # 닫힌 상태: 실금
    o_closed = cb.empty(f"RIFT_{rid}_closed", size=0.3)
    o_closed.parent = root
    o_closed["hidden"] = 1
    crack = [(u * 0.06, v * 0.8) for u, v in outer]
    _node_obj(f"RIFT_{rid}_crack", face_bm(crack, -0.01), "magenta", parent=o_closed)
    C.add_node(root)
    return root


# ================================================================== Elias nature (불시착·건설)

def terrain(C, *, radius=320.0, rings=22, segs=48, seed=3, amp=6.0, flat_r=45.0, key="grass", z=0.0,
            pad=None, col=True):
    """엘리아스 초원 (원작: 원래부터 식생이 나쁘지 않은 땅). 가운데 flat_r 안은 평평, 밖으로 갈수록 언덕.
    방사형 격자. 반환: 높이 함수 h(x, y)."""
    def h(x, y):
        r = math.hypot(x, y)
        t = max(0.0, min(1.0, (r - flat_r) / (radius * 0.5)))
        t = t * t * (3 - 2 * t)
        return z + amp * t * (noise2(x, y, seed) + 1.2)
    b = C.bm(key, "main")
    radii = [0.0] + [flat_r * 0.4 * (i + 1) / 3 for i in range(3)]
    rr = flat_r
    while rr < radius:
        radii.append(rr)
        rr *= 1.22 if rr > flat_r * 1.5 else 1.12
    radii.append(radius)
    rows = []
    for ri, r in enumerate(radii):
        if r == 0:
            rows.append([b.verts.new(Vector((0, 0, h(0, 0))))])
            continue
        row = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            x, y = math.cos(a) * r, math.sin(a) * r
            row.append(b.verts.new(Vector((x, y, h(x, y)))))
        rows.append(row)
    for i in range(segs):
        b.faces.new((rows[0][0], rows[1][i], rows[1][(i + 1) % segs]))
    for k in range(1, len(rows) - 1):
        for i in range(segs):
            i2 = (i + 1) % segs
            f = b.faces.new((rows[k][i], rows[k + 1][i], rows[k + 1][i2], rows[k][i2]))
            f.smooth = True
    if col:
        C.col(-flat_r, flat_r, -flat_r, flat_r, z - 1.0, z)
    return h


def world_tree(C, x, y, *, h=320.0, z=0.0, kind="far"):
    """세계수 엘드르 (원작: 에르피엔 한가운데의 거대한 신목). 모든 장면이 같은 디자인을 쓰도록 erpien_kit의 원경 실루엣으로
    넘긴다. 둘레의 왕국까지 세우려면 erpien_kit.erpien을 쓴다 (docs/art/erpien.md)."""
    import erpien_kit  # 늦게 가져온다 (erpien_kit가 이 모듈을 가져온다)
    return erpien_kit.world_tree(C, x, y, z, h, detail=0, kind=kind)


def mountains(C, cx, cy, *, count=6, dist=420.0, spread=60.0, h=(60, 130), seed=5, key="mount", snow=True,
              arc=(0.0, 360.0)):
    """원경 산 (정령산 방향). 둥근 봉우리 2~3개가 겹친 덩어리 + 눈 모자."""
    rng = random.Random(seed)
    for i in range(count):
        a = math.radians(arc[0] + (arc[1] - arc[0]) * (i + rng.uniform(0.2, 0.8)) / count)
        d = dist + rng.uniform(-spread, spread)
        px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
        hh = rng.uniform(*h)
        t = Vector((-math.sin(a), math.cos(a), 0))
        for k in range(rng.randint(2, 3)):
            off = t * rng.uniform(-0.8, 0.8) * hh
            hk = hh * (1.0 if k == 0 else rng.uniform(0.55, 0.8))
            rb = hk * rng.uniform(1.1, 1.5)
            q = Vector((px, py, 0)) + off
            C.cyl(key, (q.x, q.y, -6), (q.x, q.y, hk * 0.82), rb, r2=hk * 0.32, segs=14, kind="far")
            C.blob(key, (q.x, q.y, hk * 0.8), hk * 0.34, (1, 1, 0.62), segs=14, rings=6, kind="far")
            if snow and k == 0:
                C.blob("mount_l", (q.x, q.y, hk * 0.86), hk * 0.3, (1, 1, 0.5), segs=14, rings=6, kind="far")


def haze_wall(C, *, radius=560.0, h=90.0, segs=40):
    """엘리아스를 둘러싼 안개 경계 (원작: 숲 너머 안개로 둘러싸인 바깥쪽)."""
    b = C.bm("haze", "fine")
    lo, hi = [], []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        lo.append(b.verts.new(Vector((math.cos(a) * radius, math.sin(a) * radius, -5))))
        hi.append(b.verts.new(Vector((math.cos(a) * radius, math.sin(a) * radius, h))))
    for i in range(segs):
        j = (i + 1) % segs
        b.faces.new((lo[i], lo[j], hi[j], hi[i]))


def sky_moons(C, center, normal, *, r=38.0, second=(0.55, 22.0, 70.0)):
    """낯선 하늘의 두 달 (낮달). UNLIT 원판 + 옅은 무늬."""
    c = Vector(center)
    N = Vector(normal).normalized()
    R, U, _ = frame(N)
    C.decal("moon", hw.circle(r, 40), c, N, lift=0.0)
    for (du, dv, rr) in ((-0.3, 0.2, 0.18), (0.25, -0.15, 0.12), (0.1, 0.35, 0.08), (-0.1, -0.35, 0.1)):
        C.decal("moon_d", hw.circle(r * rr, 16, du * r, dv * r), c, N, lift=0.5)
    k, du, dv = second
    c2 = c + R * du + U * dv
    C.decal("moon", hw.circle(r * k, 32), c2, N, lift=0.0)
    C.decal("moon_d", hw.circle(r * k * 0.82, 32, r * k * 0.2, 0), c2, N, lift=0.4)


def cloud(C, x, y, z, *, size=14.0, seed=0, key="white"):
    """뭉게구름: 아래가 평평한 덩어리 7개."""
    rng = random.Random(seed)
    for i in range(7):
        u = (i - 3) / 3.0
        r = size * (0.42 - 0.18 * abs(u)) * rng.uniform(0.85, 1.15)
        C.blob(key, (x + u * size * 0.9, y + rng.uniform(-0.3, 0.3) * size * 0.3, z + r * 0.35), r, (1.15, 1.0, 0.8),
               segs=12, rings=7, kind="far")


def forest(C, cx, cy, *, r=18.0, n=12, seed=0, hfun=None, hmin=5.0, hmax=8.0):
    """숲 덩어리 (원경 나무 무리)."""
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = r * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        z = hfun(x, y) - 0.1 if hfun else 0.0
        tree(C, x, y, h=rng.uniform(hmin, hmax), seed=seed * 31 + i, z=z, kind="far", lod=1)


def meat_tree(C, x, y, *, h=4.2, seed=0, z=0.0):
    """고기가 열리는 나무 (원작: 엘리아스에서는 고기가 나무에서 열린다). 뼈 붙은 고기 열매."""
    rng = random.Random(seed)
    tree(C, x, y, h=h, seed=seed, z=z, leaf=("leaf_d", "leaf", "leaf"))
    for i in range(5):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.6, 1.0) * h * 0.22
        cz = z + h * rng.uniform(0.48, 0.58)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        C.cyl("trunk", (px, py, cz + 0.35), (px, py, cz + 0.12), 0.02, segs=5, kind="detail")
        C.cyl("bone", (px, py, cz + 0.12), (px, py, cz - 0.05), 0.035, segs=6, kind="detail")
        C.blob("bone", (px, py, cz + 0.13), 0.05, segs=6, rings=4, kind="detail")
        C.blob("meat", (px, py, cz - 0.17), 0.16, (1, 1, 1.25), segs=8, rings=6, kind="detail")


def rock(C, x, y, *, s=1.0, z=0.0, seed=0, key="rock"):
    rng = random.Random(seed)
    sy, sz = rng.uniform(0.7, 1.0), rng.uniform(0.45, 0.7)
    rz = rng.uniform(0, 3)
    C.blob(key, (x, y, z + 0.2 * s), 0.6 * s, (1.0, sy, sz), segs=7, rings=4, rot_z=rz, kind="detail")
    # 돌린 타원 덩어리 그대로의 볼록 껍질 (돌린 상자는 비탈진 바위에 수직 턱을 만들었다)
    R0 = 0.6 * s
    cz0 = z + 0.2 * s
    pts = []
    for la in (-90, -45, 0, 30, 60, 90):
        for k in range(8):
            a = 2 * math.pi * k / 8
            lx, ly, lz = R0 * math.cos(math.radians(la)) * math.cos(a), R0 * sy * math.cos(math.radians(la)) * math.sin(a), R0 * sz * math.sin(math.radians(la))
            pts.append((x + lx * math.cos(rz) - ly * math.sin(rz), y + lx * math.sin(rz) + ly * math.cos(rz), cz0 + lz))
    C.ccol(pts)


def flowers(C, cx, cy, *, r=3.0, n=14, seed=0, z=0.0):
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, r)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        C.cyl("leaf_d", (x, y, z), (x, y, z + 0.18), 0.012, segs=4, kind="fine", smooth=False)
        C.blob("flower_p" if i % 2 else "flower_y", (x, y, z + 0.2), 0.05, segs=6, rings=3, kind="fine")


# ================================================================== construction era

def tent(C, x, y, *, yaw=0.0, w=2.6, d=3.2, h=1.9, key="canvas", z=0.0, door=True):
    """A자 천막 (엘프 체격). 정면 -Y(입구)를 yaw로 돌림."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    b = C.bm(key, "main")
    tri = [(-w / 2, 0.0), (w / 2, 0.0), (0.0, h)]
    f0 = [b.verts.new(Mx @ Vector((u, -d / 2, v))) for u, v in tri]
    f1 = [b.verts.new(Mx @ Vector((u, d / 2, v))) for u, v in tri]
    faces = [b.faces.new(f0), b.faces.new(list(reversed(f1)))]
    for i in range(3):
        j = (i + 1) % 3
        if i == 0:
            continue
        faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=faces)
    C.ccol([Mx @ Vector((u, t * d / 2, v)) for t in (-1, 1) for u, v in tri])
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    if door:
        C.decal("dark", [(-0.45, 0), (0.45, 0), (0, h * 0.75)], Mx @ Vector((0, -d / 2, 0)), N, lift=0.02)
    for s in (-1, 1):
        p = Mx @ Vector((0, s * (d / 2 + 0.05), 0))
        C.cyl("wood_d", tuple(p), tuple(p + Vector((0, 0, h + 0.25))), 0.04, segs=6, kind="detail")
    # 줄 + 말뚝
    for s in (-1, 1):
        for t in (-1, 1):
            a = Mx @ Vector((s * w * 0.5, t * d * 0.5, 0.05))
            g = Mx @ Vector((s * (w * 0.5 + 0.7), t * (d * 0.5 + 0.4), 0.0))
            C.beam("wood_d", a, g, 0.02, 0.02, kind="fine")


def campfire(C, x, y, *, z=0.0, lit=True):
    C.col(x - 0.6, x + 0.6, y - 0.6, y + 0.6, z, z + 0.3)    # 돌 테 (불 속으로 걸어 들어가지 않게)
    for i in range(8):
        a = 2 * math.pi * i / 8
        C.blob("rock", (x + math.cos(a) * 0.5, y + math.sin(a) * 0.5, z + 0.06), 0.13, (1, 1, 0.6), segs=6, rings=4,
               kind="detail")
    for i in range(3):
        a = 2 * math.pi * i / 3
        C.cyl("trunk", (x + math.cos(a) * 0.35, y + math.sin(a) * 0.35, z + 0.05), (x, y, z + 0.35), 0.05, segs=6,
              kind="detail")
    if lit:
        C.cyl("fire", (x, y, z + 0.05), (x, y, z + 0.75), 0.26, r2=0.0, segs=8, kind="fine")
        C.cyl("fire_c", (x, y, z + 0.05), (x, y, z + 0.45), 0.13, r2=0.0, segs=8, kind="fine")


def crate(C, x, y, *, s=0.6, yaw=0.0, z=0.0, key="olive", stencil=True):
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    _bm_box(C.bm(key, "detail"), -s / 2, s / 2, -s / 2, s / 2, 0, s * 0.8, matrix=Mx)
    for k in (-1, 1):
        _bm_box(C.bm("wood_d", "detail"), -s / 2 - 0.01, s / 2 + 0.01, k * s * 0.35 - 0.03, k * s * 0.35 + 0.03, -0.01,
                s * 0.8 + 0.01, matrix=Mx)
    C.lcol(x, y, z, yaw, -s / 2, s / 2, -s / 2, s / 2, 0, s * 0.8)


def terraformer(C, x, y, *, z=0.0, lit=True, rings=3):
    """테라포밍 장치 (원작: 엘프는 테라포밍 장치로 모나티엄을 세웠다). 세 다리 + 둥근 몸체 + 시안 코어 +
    주변으로 퍼지는 푸른 풀 고리."""
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        C.cyl("metal", (x + math.cos(a) * 1.6, y + math.sin(a) * 1.6, z), (x, y, z + 2.2), 0.12, segs=8)
        C.cyl("dark", (x + math.cos(a) * 1.6, y + math.sin(a) * 1.6, z), (x + math.cos(a) * 1.6, y + math.sin(a) * 1.6,
                                                                           z + 0.12), 0.3, segs=10, kind="detail")
    C.cyl("olive", (x, y, z + 1.6), (x, y, z + 3.0), 1.1, r2=0.9, segs=16)
    C.cyl("navy", (x, y, z + 3.0), (x, y, z + 3.3), 1.0, segs=16, kind="detail")
    C.blob("glow" if lit else "glow_off", (x, y, z + 3.6), 0.55, segs=12, rings=8)
    _bm_torus(C.bm("gold", "detail"), (x, y, z + 3.45), 0.8, 0.07, seg=20, rseg=5)
    C.cyl("glow" if lit else "glow_off", (x, y, z + 2.2), (x, y, z + 2.35), 1.05, segs=16, kind="fine", cap=False)
    C.text("white", "TERRAFORM-7", 0.18, (x, y - 1.0 - 0.01, z + 2.6), (0, -1, 0), lift=0.0)
    if lit:
        for i in range(rings):
            r0 = 3.5 + i * 3.2
            C.ring("grass_d" if i % 2 else "leaf_l", hw.circle(r0 + 0.6, 40), hw.circle(r0, 40), (x, y, z), (0, 0, 1),
                   up=(0, 1, 0), lift=0.03 + i * 0.002)
        C.cyl("beam", (x, y, z + 3.6), (x, y, z + 40), 0.4, r2=1.2, segs=12, kind="fine", cap=False)


def factory_shed(C, x0, x1, y0, y1, *, h=4.2, teeth=4, key="concrete", roof="roof", chimney=True, seed=0):
    """톱니 지붕 공장 (건설 2단계). X 방향 톱니."""
    C.box(key, x0, x1, y0, y1, 0, h)
    C.col(x0, x1, y0, y1, 0, h)
    w = (x1 - x0) / teeth
    for i in range(teeth):
        xa = x0 + i * w
        b = C.bm(roof, "detail")
        tri = [(xa, h), (xa + w, h), (xa + w, h + 1.6)]
        f0 = [b.verts.new(Vector((u, y0, v))) for u, v in tri]
        f1 = [b.verts.new(Vector((u, y1, v))) for u, v in tri]
        faces = [b.faces.new(f0), b.faces.new(list(reversed(f1)))]
        for k in range(3):
            j = (k + 1) % 3
            faces.append(b.faces.new((f0[k], f0[j], f1[j], f1[k])))
        bmesh.ops.recalc_face_normals(b, faces=faces)
        C.decal("glass", [(-0.5, 0.05), (0.5, 0.05), (0.5, 1.35), (-0.5, 1.35)], (xa + w - 0.0, (y0 + y1) / 2, h),
                (1, 0, 0), up=(0, 0, 1), lift=0.02)
    for k in range(int((x1 - x0) / 3)):
        xx = x0 + 1.5 + k * 3
        C.rect("glass_d", (xx, y0, h * 0.6), (0, -1, 0), 1.6, 1.0, lift=0.02)
    entrance(C, Vector(((x0 + x1) / 2, y0, 0)), Vector((0, -1, 0)), Vector((1, 0, 0)), w=2.6, h=2.4, key="hazard",
             canopy=False)
    if chimney:
        rng = random.Random(seed)
        cx_ = x1 - 1.5
        cy_ = (y0 + y1) / 2 + rng.uniform(-1, 1)
        C.cyl("brick", (cx_, cy_, h), (cx_, cy_, h + 9), 0.8, r2=0.6, segs=12)
        C.cyl("dark", (cx_, cy_, h + 8.4), (cx_, cy_, h + 9.05), 0.65, segs=12, kind="detail")
        for i in range(4):
            C.blob("smoke", (cx_ + i * 1.3, cy_ + i * 0.3, h + 10 + i * 1.6), 0.9 + i * 0.45, segs=8, rings=5,
                   kind="fine")


def crane(C, x, y, *, h=24.0, jib=18.0, yaw=0.0, key="hazard"):
    """타워 크레인 (노란 격자 기둥 + 지브 + 평형추)."""
    m = 0.9
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.beam(key, (x + sx * m / 2, y + sy * m / 2, 0), (x + sx * m / 2, y + sy * m / 2, h), 0.12, 0.12)
    C.col(x - m / 2 - 0.06, x + m / 2 + 0.06, y - m / 2 - 0.06, y + m / 2 + 0.06, 0, h)
    k = 0.0
    while k < h - 1:
        for (a, b_) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            C.beam(key, (x + a[0] * m / 2, y + a[1] * m / 2, k), (x + b_[0] * m / 2, y + b_[1] * m / 2, k + 1.8), 0.06,
                   0.06, kind="detail")
        k += 1.8
    D = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
    top = Vector((x, y, h))
    C.beam(key, top - D * jib * 0.3, top + D * jib, 0.7, 0.7)
    C.box("concrete_d", x - 0.8, x + 0.8, y - 0.8, y + 0.8, h - 0.2, h + 1.6, kind="detail")
    cw = top - D * jib * 0.27 - Vector((0, 0, 0.9))
    C.box("concrete_d", cw.x - 0.8, cw.x + 0.8, cw.y - 0.8, cw.y + 0.8, cw.z - 0.6, cw.z + 0.6, kind="detail")
    C.beam("metal", top + Vector((0, 0, 0.3)), top + Vector((0, 0, 4)), 0.2, 0.2, kind="detail")
    C.beam("metal", top + Vector((0, 0, 4)), top + D * jib * 0.8, 0.05, 0.05, kind="detail")
    hook = top + D * jib * 0.7
    C.beam("dark", hook, hook - Vector((0, 0, 8)), 0.03, 0.03, kind="fine")
    C.box("hazard", hook.x - 0.3, hook.x + 0.3, hook.y - 0.3, hook.y + 0.3, hook.z - 8.6, hook.z - 8.0, kind="detail")


def scaffold(C, x0, x1, y0, y1, h, *, key="steel", pitch=2.4, lift=2.7):
    """비계 (공사 중 건물 둘레). 기둥 + 층 발판."""
    for (a0, a1, b0, b1) in ((x0, x1, y0, y0), (x0, x1, y1, y1), (x0, x0, y0, y1), (x1, x1, y0, y1)):
        L = math.hypot(a1 - a0, b1 - b0)
        n = max(1, int(L / pitch))
        for k in range(n + 1):
            px = a0 + (a1 - a0) * k / n
            py = b0 + (b1 - b0) * k / n
            C.beam(key, (px, py, 0), (px, py, h), 0.07, 0.07, kind="detail")
            C.col(px - 0.04, px + 0.04, py - 0.04, py + 0.04, 0, 2.0)
        zz = lift
        while zz <= h:
            C.beam("wood", (a0, b0, zz), (a1, b1, zz), 0.45, 0.06, kind="detail")
            C.beam(key, (a0, b0, zz + 0.9), (a1, b1, zz + 0.9), 0.05, 0.05, kind="detail")
            zz += lift


def spirit_plant(C, x, y, *, lit=True):
    """정령 발전소 (원작: 화석 연료가 부족한 엘리아스에서 모나티엄은 정령을 에너지원으로 우대한다).
    유리 돔 안의 빛나는 구체."""
    C.cyl("concrete", (x, y, 0), (x, y, 2.4), 6.0, segs=28)
    C.col(x - 5, x + 5, y - 5, y + 5, 0, 2.4)
    C.cyl("navy", (x, y, 2.4), (x, y, 2.7), 6.2, segs=28, kind="detail")
    C.blob("glass_a", (x, y, 2.7), 5.4, (1, 1, 0.75), segs=20, rings=8, kind="fine")
    C.blob("fire" if lit else "glow_off", (x, y, 4.6), 1.6, segs=12, rings=8)
    C.blob("fire_c" if lit else "glow_off", (x, y, 4.6), 0.9, segs=10, rings=6, kind="fine")
    C.text("navy", "정령 발전소 SPIRIT POWER", 0.6, (x, y - 6.02, 1.5), (0, -1, 0), lift=0.02)


def podium(C, x, y, *, yaw=0.0, z=0.0):
    """취임식 연단: 단상 + 연설대 + 마이크 + 엘프 로고 (엘레나 시장 취임 장면)."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    b = C.bm("navy", "main")
    _bm_box(b, -3.5, 3.5, -2.0, 2.0, 0, 0.6, matrix=Mx)
    bs = C.bm("stone_d", "detail")
    for i in range(3):
        _bm_box(bs, -1.2, 1.2, -2.0 - (i + 1) * 0.35, -2.0 - i * 0.35, 0, 0.6 * (3 - i) / 4 + 0.0, matrix=Mx)
    # 연설대: 엘프 가슴 높이 (단 위 0.72 m)
    C.rbox("violet", tuple(Mx @ Vector((0, -0.75, 0.6 + 0.32))), (0.9, 0.5, 0.64), (0, 0, yaw))
    C.rbox("navy", tuple(Mx @ Vector((0, -0.7, 0.6 + 0.66))), (1.0, 0.62, 0.05), (-8, 0, yaw), kind="detail")
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    C.logo(tuple(Mx @ Vector((0, -1.01, 0.94))), 0.36, tuple(N), key="gold", disc="navy", lift=0.01)
    mic0 = Mx @ Vector((0, -0.85, 1.28))
    C.cyl("dark", tuple(mic0), tuple(Mx @ Vector((0, -0.62, 1.55))), 0.012, segs=5, kind="detail")
    C.blob("dark", tuple(Mx @ Vector((0, -0.6, 1.57))), 0.035, segs=6, rings=4, kind="detail")
    for s in (-1, 1):
        p = Mx @ Vector((s * 3.2, 1.6, 0.6))
        C.cyl("gold", tuple(p), tuple(p + Vector((0, 0, 4.5))), 0.05, segs=8, kind="detail")
        banner(C, tuple(p + Vector((0, 0, 4.3)) - N * 0.1), tuple(N), 1.2, 3.2)
    lo, hi = Mx @ Vector((-3.5, -2.0, 0)), Mx @ Vector((3.5, 2.0, 0))
    C.col(lo.x, hi.x, lo.y, hi.y, z, z + 0.6)
    return Mx @ Vector((0, -0.05, 0.6))


# ================================================================== suppression unit training yard

def training_yard(C, x0, x1, y0, y1, *, z=0.0, sign=True):
    """모나티엄 진압반 훈련장 한쪽 (원작: 진압반은 고무탄·전기충격기, 칸나 휘하. 표식은 남보라·청록 비살상).
    고무 바닥 + 트랙 선 + 모래주머니 벽 + 표적대 + 방패 거치대 + 장애물 봉 + 훈련용 허수아비.
    반환: 주요 지점 dict."""
    C.box("rubber", x0, x1, y0, y1, z - 0.3, z + 0.02)
    C.col(x0, x1, y0, y1, z - 0.3, z + 0.02)
    C.strip("teal", (x0 + 1, y0 + 1.0, z + 0.02), (x1 - 1, y0 + 1.0, z + 0.02), 0.3, lift=0.012)
    # 울타리
    for (a, b_) in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1))):
        fence(C, a, b_, h=1.0, key="metal", pitch=2.0, z=z)
    # 사로: 사수 선 y0+4, 표적 y1-2. 서쪽 장애물·방패, 동쪽 엄폐 연습(모래주머니)·허수아비
    cx = (x0 + x1) / 2
    fire_y = y0 + 4.0
    C.strip("teal", (x0 + 5, fire_y - 0.6, z + 0.02), (x1 - 6, fire_y - 0.6, z + 0.02), 0.22, lift=0.014)
    for k in range(6):
        lx = x0 + 5.5 + k * (x1 - x0 - 12) / 5
        C.strip("line", (lx, fire_y - 0.2, z + 0.02), (lx, y1 - 3.0, z + 0.02), 0.06, lift=0.013)
    def sandbags(sx, sy, n=4, rows=3, axis="x"):
        for row in range(rows):
            for k in range(n - row % 2):
                off = -0.31 * (n - 1) + k * 0.62 + (0.31 if row % 2 else 0)
                p = (sx + off, sy) if axis == "x" else (sx, sy + off)
                C.blob("sand", (p[0], p[1], z + 0.14 + row * 0.24), 0.34,
                       (1, 0.6, 0.42) if axis == "x" else (0.6, 1, 0.42), segs=8, rings=4, kind="detail")
        hw_ = 0.31 * n + 0.1
        if axis == "x":
            C.col(sx - hw_, sx + hw_, sy - 0.3, sy + 0.3, z, z + 0.24 * rows + 0.1)
        else:
            C.col(sx - 0.3, sx + 0.3, sy - hw_, sy + hw_, z, z + 0.24 * rows + 0.1)
    sandbags(x1 - 3.2, fire_y + 3.0)
    sandbags(x1 - 3.2, fire_y + 7.5, n=3)
    sandbags(x0 + 3.2, fire_y + 9.0, n=3)
    # 표적대 (고무탄 표적: 청록 고리)
    for k in range(5):
        tx = x0 + 6.5 + k * (x1 - x0 - 14) / 4
        ty = y1 - 2.0
        C.beam("wood_d", (tx - 0.4, ty, z), (tx - 0.4, ty, z + 1.3), 0.06, 0.06, kind="detail")
        C.beam("wood_d", (tx + 0.4, ty, z), (tx + 0.4, ty, z + 1.3), 0.06, 0.06, kind="detail")
        c = Vector((tx, ty - 0.04, z + 1.2))
        C.plate("white", hw.circle(0.42, 20), c, (0, -1, 0), 0.04, kind="detail")
        C.ring("teal", hw.circle(0.34, 20), hw.circle(0.26, 20), c + Vector((0, -0.04, 0)), (0, -1, 0), lift=0.01)
        C.decal("violet", hw.circle(0.11, 14), c + Vector((0, -0.04, 0)), (0, -1, 0), lift=0.012)
    C.box("concrete_d", x0 + 4, x1 - 5, y1 - 1.2, y1 - 0.4, z, z + 2.2, kind="detail")   # 탄 받이 벽
    C.col(x0 + 4, x1 - 5, y1 - 1.2, y1 - 0.4, z, z + 2.2)
    # 훈련용 허수아비 (둥근 덩어리)
    for k, (dx, dy) in enumerate(((x1 - 2.4, y1 - 4.0), (x1 - 2.4, y1 - 6.0))):
        C.cyl("dark", (dx, dy, z), (dx, dy, z + 0.4), 0.2, segs=8, kind="detail")
        C.blob("sand", (dx, dy, z + 0.75), 0.32, (1, 1, 1.15), segs=10, rings=6)
        C.blob("sand", (dx, dy, z + 1.25), 0.24, segs=10, rings=6)
        C.decal("teal", hw.circle(0.09, 12), (dx - 0.32, dy, z + 0.8), (-1, 0, 0), lift=0.01)
    # 방패 거치대 (진압 방패: 남보라 테 + 투명 창)
    rx = x0 + 1.2
    for k in range(4):
        ry = y0 + 1.6 + k * 0.8
        C.plate("violet", hw.rrect(0.5, 0.95, 0.12, 2), (rx, ry, z + 0.6), (1, 0, 0), 0.05, kind="detail")
        C.decal("glass_a", hw.rrect(0.32, 0.3, 0.08, 2), (rx + 0.05, ry, z + 0.85), (1, 0, 0), lift=0.01)
        C.decal("teal", [(-0.22, -0.02), (0.22, -0.02), (0.22, 0.04), (-0.22, 0.04)], (rx + 0.05, ry, z + 0.45),
                (1, 0, 0), lift=0.012)
    C.beam("metal", (rx - 0.2, y0 + 1.1, z + 0.3), (rx - 0.2, y0 + 4.6, z + 0.3), 0.06, 0.06, kind="detail")
    # 장애물 봉 (뛰어넘기·기어가기) — 서쪽 줄
    ox, oy = x0 + 3.0, fire_y + 1.5
    for k in range(3):
        yy = oy + k * 2.0
        hh = (0.5, 0.82, 0.5)[k]
        for s_ in (-1, 1):
            C.beam("metal", (ox + s_ * 1.0, yy, z), (ox + s_ * 1.0, yy, z + hh + 0.1), 0.08, 0.08, kind="detail")
        C.beam("hazard", (ox - 1.0, yy, z + hh), (ox + 1.0, yy, z + hh), 0.07, 0.07, kind="detail")
    # 훈련장 표지
    if sign:
        sc = Vector((x0 + 6, y0 - 0.05, z + 1.9))
        C.cyl("metal", (sc.x - 1.4, y0, z), (sc.x - 1.4, y0, z + 2.4), 0.06, segs=8, kind="detail")
        C.cyl("metal", (sc.x + 1.4, y0, z), (sc.x + 1.4, y0, z + 2.4), 0.06, segs=8, kind="detail")
        C.plate("violet", hw.rrect(3.2, 0.9, 0.25, 2), sc, (0, -1, 0), 0.08, kind="detail")
        C.text("white", "EBI 진압반 훈련장", 0.3, sc + Vector((0, -0.08, 0.12)), (0, -1, 0))
        C.text("gold", "MONATIUM SUPPRESSION UNIT · TRAINING", 0.13, sc + Vector((0, -0.08, -0.22)), (0, -1, 0))
    return {"drill": Vector((cx, fire_y, z)), "targets_y": y1 - 2.0, "obstacles": Vector((ox, oy, z)),
            "shields": Vector((rx, y0 + 2.8, z))}


# ================================================================== layouts (여러 세트·레벨이 같이 쓰는 배치)

AVENUE_Y = -20.8          # 중앙로(시청 앞 큰길) 중심선
PLAZA = (-24.0, 24.0, -11.0, 18.0)


def fountain(C, x, y, *, r=4.0, z=0.0):
    """광장 분수: 석재 둥근 수반 + 물 + 가운데 금색 고리 조형물(엘프 로고)."""
    C.cyl("stone_d", (x, y, z), (x, y, z + 0.5), r, segs=32)
    C.cyl("glass", (x, y, z + 0.506), (x, y, z + 0.52), r - 0.35, segs=32, kind="fine")   # 물: 수반 윗면에서 6 mm 띄움
    C.cyl("stone", (x, y, z + 0.5), (x, y, z + 0.62), r, segs=32, kind="detail", cap=False)
    _bm_torus(C.bm("stone", "detail"), (x, y, z + 0.56), r - 0.17, 0.2, seg=32, rseg=6)
    C.ccyl(x, y, r, z, z + 0.62, n=32)     # 둥근 수반 (예전 0.8r 정사각형: 테두리로 걸어 들어가고 모서리는 튀어나왔다)
    C.ccyl(x, y, 0.72, z + 0.62, z + 1.75, n=16)    # 가운데 조형물 기둥
    C.cyl("stone", (x, y, z + 0.5), (x, y, z + 1.6), 0.7, r2=0.5, segs=16)
    _bm_torus(C.bm("gold", "main"), (x, y, z + 3.0), 1.3, 0.14, seg=32, rseg=8, axis=(0, 1, 0))
    C.cyl("gold", (x, y, z + 1.6), (x, y, z + 1.75), 0.55, segs=16, kind="detail")
    # 조형물 판: 등을 맞댄 남색 원판 두 장(4 cm 사이) 위에 금색 로고. logo()가 로고를 원판보다 4.5 mm 앞에 띄운다
    C.logo((x, y - 0.02, z + 3.0), 1.5, (0, -1, 0), key="gold", disc="navy", lift=0.0)
    C.logo((x, y + 0.02, z + 3.0), 1.5, (0, 1, 0), key="gold", disc="navy", lift=0.0)
    for i in range(6):
        a = 2 * math.pi * i / 6
        p = Vector((x + math.cos(a) * 0.8, y + math.sin(a) * 0.8, z + 1.5))
        C.cyl("holo_l", tuple(p), tuple(p + Vector((math.cos(a) * 1.6, math.sin(a) * 1.6, 0.9))), 0.06, r2=0.12,
              segs=6, kind="fine", cap=False)


SOUTH_ROW = [
    # (폭, 층, 스타일, 상가(이름, 부제, 차양) 또는 None, 옥상 간판)
    (14, 4, "brick", ("모나티엄 25", "MONATIUM 25 · 24H", "mint"), None),
    (11, 5, "apartment", ("커틀릿 하우스", "진짜 돼지고기 · 공기커틀릿 아님", "coral"), None),
    (13, 6, "office", ("엘프 은행", "ELF BANK · 프리미엄 시민 창구", "teal"), None),
    (16, 9, "glass", None, "MELU CORP. 모나티엄 지사"),
    (12, 5, "apartment", ("꽃집 루루", "FLOWERS", "mint"), None),
    (10, 4, "brick", ("모나티엄 서점", "BOOKS · 엘레나 자서전 입고", "coral"), None),
    (14, 7, "office", ("모나티엄 우체국", "POST · 인트라넷 우편", "teal"), None),
    (12, 5, "apartment", ("카페 귀쟁이", "CAFE", "coral"), None),
    (14, 4, "brick", ("모나티엄 25", "MONATIUM 25", "mint"), None),
    (13, 6, "office", None, None),
]


def downtown(C, *, variant="day", training=True, train=True, highway_on=True, skyline=True, x_span=(-96, 96),
             screens=True, seed=11, train_x=-56.0):
    """시청 앞 광장 일대 (인터루드 6·7, 1막 M1·M2 공용 배치).
    북쪽 시청(정면 -Y) · 가운데 광장과 분수 · 남쪽 중앙로(4차로 + 모노레일) · 큰길 건너 상가 줄 ·
    서쪽 진압반 훈련장과 EBI 본부 · 동쪽 대형 화면 건물 · 동쪽 끝 알프토반 진입로 · 북동 코어 AI 탑 · 원경 고층.
    variant: 'day' | 'dusk' (가로등 켜짐). 반환: 배치 기준점 dict."""
    lit = variant != "day"
    A = {}
    C.group("plaza")
    px0, px1, py0, py1 = PLAZA
    paving(C, px0, px1, py0, py1, tile=1.6, border="pave_r")
    fountain(C, 0, 2.0)
    A["fountain"] = Vector((0, 2.0, 0))
    # 광장 둘레 화단·나무·벤치
    for sx in (-1, 1):
        for k in range(3):
            y = -6 + k * 7.5
            x = sx * 17.5
            planter(C, x - 1.4, x + 1.4, y - 1.4, y + 1.4, h=0.5, hedge=False)
            tree(C, x, y, h=5.2, seed=seed + k * 3 + (sx + 1), z=0.5)
            bench(C, x - sx * 2.6, y, yaw=-90 * sx)
        for k in range(2):
            y = -2.2 + k * 7.5
            planter(C, sx * 9.5 - 1.6, sx * 9.5 + 1.6, y - 0.5, y + 0.5, h=0.45)
    for sx in (-1, 1):
        lamp(C, sx * 6.5, -9.5, lit=lit)
        lamp(C, sx * 6.5, 13.0, lit=lit)
        lamp(C, sx * 22.5, 14.5, lit=lit)
        cctv_pole(C, sx * 22.8, -10.2, yaw=sx * -30)
        trash_bin(C, sx * 8.0, -10.0)
    vending(C, 21.5, 9.2, yaw=-90)
    vending(C, 21.5, 10.2, yaw=-90, key="teal")
    A["vending"] = Vector((20.3, 9.7, 0))
    street_sign(C, -22.5, -10.6, "시청 앞 광장", "CITY HALL PLAZA", yaw=0)
    street_sign(C, 22.5, -10.6, "엘레나대로", "ELENA AVE", yaw=0)
    # 시청 (광장 북쪽)
    C.group("cityhall")
    ch = city_hall(C, 0, 26.0, screen=screens)
    A.update({f"cityhall_{k}": v for k, v in ch.items()})
    paving(C, -24, 24, 18, 36, tile=2.0, grout=None, col=True)
    # 코어 AI 탑 (북동)
    C.group("core")
    core_ai(C, 32, 36, lit=True)
    paving(C, 24, 42, 22, 48, tile=2.0, grout=None)
    A["core"] = Vector((32, 36, 0))
    # 중앙로 + 모노레일
    C.group("avenue")
    rd = road(C, "x", AVENUE_Y, x_span[0], x_span[1] - 30 if highway_on else x_span[1], lanes=4, median=2.0,
              crossings=(-12.0, 12.0))
    A["road"] = rd
    monorail(C, [(-120.0, AVENUE_Y), (136.0, AVENUE_Y)], z=7.5)   # 기둥 x = -8+16k (시청 축 x=0은 비움)
    for x in range(int(x_span[0]) + 6, int(x_span[1]) - 30, 12):
        if -24 < x < 24 and x % 24 == 6:
            pass
        lamp(C, x, rd["walk_hi"] - 0.6, lit=lit)
        lamp(C, x + 6, rd["walk_lo"] + 0.6, lit=lit)
        if x % 24 == 6:
            tree(C, x + 6, rd["walk_lo"] + 1.4, h=4.8, seed=x)
    for x in (-60, -36, 36):
        cctv_pole(C, x + 3, rd["walk_hi"] - 0.5, yaw=180)
    street_sign(C, -12, rd["walk_lo"] + 0.5, "엘레나디지털단지역 →", "MONORAIL · 중앙역", yaw=180, w=2.2)
    if highway_on:
        highway(C, x_ramp0=x_span[1] - 30, x_ramp1=x_span[1] + 40, y_c=AVENUE_Y, x_end=x_span[1] + 170)
        A["highway_gantry"] = Vector((x_span[1] - 34, AVENUE_Y, 5.8))
    if train:
        # 열차 노드: drift(three.js m/s)로 +X 방향 주행. 몽타주는 컷 시작에 위치를 되돌린다(trainStart).
        C.group("MONORAIL_train", drift="8,0,0", train=1, trainStart=f"{train_x:g}")
        monorail_car(C, (train_x, AVENUE_Y, 7.5 + 0.15), (1, 0, 0), n=2)
        A["train"] = Vector((train_x, AVENUE_Y, 7.65))
    # 큰길 건너 상가 줄 (정면 +Y)
    C.group("south")
    x = -80.0
    yb1 = rd["walk_lo"] - 0.4
    yb0 = yb1 - 13
    i = 0
    A["shops"] = []
    while x < x_span[1] - 34:
        w, fl, st, shop, sg = SOUTH_ROW[i % len(SOUTH_ROW)]
        sh = dict(zip(("name", "sub", "awning"), shop)) if shop else None
        b = building(C, x, x + w, yb0, yb1, floors=fl, style=st, front="+y", sides="+y-x+x", seed=seed + i * 7,
                     shop=sh, sign=sg)
        A["shops"].append((sh["name"] if sh else sg, b))
        x += w + (2.0 if i % 3 == 2 else 0.4)
        i += 1
    # 상가 옥상 홀로 광고
    # 아래 틀 보 윗면이 옥상 바닥(19.45)과 같은 높이가 되지 않게 6 cm 올린다
    holo_ad(C, (-46, yb0 + 6, 21.56), (0, 1, 0), 9.0, 4.0, "모나티엄 갓 탤런트", "MONATIUM'S GOT TALENT · S7")
    holo_ad(C, (22, yb0 + 6, 27.5), (0, 1, 0), 8.0, 3.6, "엘레나디지털단지", "ELENA DIGITAL COMPLEX · 분양 중")
    if screens:
        C.screen("street", (8.0, yb1 + 0.02, 12.0), (0, 1, 0), 7.2, 4.05)
        A["screen_street"] = Vector((8.0, yb1 + 0.34, 12.0))
    # 광장 동쪽: 대형 화면 건물 + 주거
    C.group("east")
    building(C, 26, 42, -9, 9, floors=6, style="office", front="-x", sides="-x-y+y", seed=seed + 101,
             shop={"name": "MONATIUM 25", "sub": "광장점", "awning": "mint"})
    if screens:
        C.screen("plaza", (26.0, 0.0, 12.6), (-1, 0, 0), 12.0, 6.75)
        A["screen_plaza"] = Vector((25.68, 0.0, 12.6))
    building(C, 26, 40, 11, 22, floors=5, style="apartment", front="-x", sides="-x-y", seed=seed + 102)
    # 광장 서쪽: 진압반 훈련장 + EBI 본부
    C.group("west")
    if training:
        A["yard"] = training_yard(C, -48, -26, -9, 12)
    else:
        paving(C, -48, -26, -9, 12)
    ebi = building(C, -48, -28, 14, 30, floors=5, style="office", front="+x", sides="+x-y", seed=seed + 103,
                   sign="EBI 진압반 본부")
    banner(C, (-27.9, 18.5, 14.0), (1, 0, 0), 1.6, 5.0)
    banner(C, (-27.9, 25.5, 14.0), (1, 0, 0), 1.6, 5.0)
    paving(C, -28, -24, 12, 36, grout=None)
    A["ebi"] = ebi
    # 북쪽·서쪽 뒤 건물 (시청 뒤 배경)
    C.group("north")
    for k, (x0, w, fl, st) in enumerate(((-60, 12, 6, "office"), (-46, 14, 7, "glass"), (-30, 12, 5, "apartment"),
                                         (44, 14, 8, "glass"), (60, 12, 6, "office"))):
        building(C, x0, x0 + w, 40, 52, floors=fl, style=st, front="-y", sides="-y", seed=seed + 200 + k,
                 door=False, cctv=False)
    for k, (x0, y0) in enumerate(((-64, -8), (-64, 10), (48, -8), (48, 8))):
        building(C, x0, x0 + 13, y0, y0 + 14, floors=5 + k % 3, style=("apartment", "office")[k % 2],
                 front="-y", sides="-y+x" if x0 < 0 else "-y-x", seed=seed + 300 + k, door=False, cctv=False)
    paving(C, -96, -48, -11, 60, grout=None, col=False, t=0.25)
    paving(C, 42, 96, -11, 60, grout=None, col=False, t=0.25)
    paving(C, -48, 42, 36, 60, grout=None, col=False, t=0.25)
    paving(C, -96, 96, -60, yb0, grout=None, col=False, t=0.25)
    # 원경 고층 (공기 원근, 단순 블록)
    if skyline:
        C.group("skyline")
        rng = random.Random(seed + 900)
        k = 0
        for ring_r, n, fl_rng in ((95.0, 18, (8, 14)), (135.0, 22, (12, 22))):
            for i in range(n):
                a = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / n
                sx, sy = math.cos(a) * ring_r * 1.25, math.sin(a) * ring_r
                if sy < -40 and abs(sx) < 60 and ring_r < 100:
                    sy -= 10
                if abs(sy - AVENUE_Y) < 14 and sx > 0:      # 고속도로 축은 비운다
                    continue
                w = rng.uniform(14, 24)
                d = rng.uniform(12, 20)
                fl = rng.randint(*fl_rng)
                building(C, sx - w / 2, sx + w / 2, sy - d / 2, sy + d / 2, floors=fl,
                         style=("glass", "office")[k % 2], far=True, seed=seed + k, h0=3.0, fh=3.0, r=3.0,
                         col=False, sides="-y+y-x+x")
                k += 1
        C.box("pave_d", -260, 260, -220, 220, -0.6, -0.32, kind="fine")
    C.group("city")
    return A


def portal_escape(C, gid, center, *, radius=3.6, tilt=-70.0, yaw=0.0, seed=4, spin=40.0):
    """탈출 게이트의 출구 GATE_<gid> (인터루드 4: 엘레나가 지구에서 조립한 차원 게이트가 엘리아스 하늘에 연 구멍).
    교주 차원 쪽 시안(엘피니아·모나티엄 발광색). R41 차원문(gate_r41)과 달리 기계 고리가 없다
    (기계는 지구 쪽에 남았다). 불안정한 빛 고리 + 반투명 원판 + 나선 + 튀는 전광.
    노드: GATE_<gid> > _ring(UNLIT 고리), _disc(spin), _swirl(반대 spin), _arcs(전광). 로컬 XY가 고리면, 로컬 -Z가 출구 쪽."""
    rng = random.Random(seed)
    Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
          @ Matrix.Rotation(math.radians(tilt), 4, "X"))
    root = cb.empty(f"GATE_{gid}", size=1.0)
    root.matrix_world = Mx
    root["gate"] = "escape"
    root["radius"] = radius
    rr = radius
    # 들쭉날쭉한 빛 고리
    br = bmesh.new()
    n = 48
    jit = [1 + rng.uniform(-0.07, 0.07) for _ in range(n)]
    outer = [Vector((math.cos(2 * math.pi * i / n) * rr * jit[i] * 1.08, math.sin(2 * math.pi * i / n) * rr * jit[i] * 1.08, 0))
             for i in range(n)]
    inner = [Vector((math.cos(2 * math.pi * i / n) * rr * jit[i] * 0.94, math.sin(2 * math.pi * i / n) * rr * jit[i] * 0.94, 0))
             for i in range(n)]
    vo = [br.verts.new(p) for p in outer]
    vi = [br.verts.new(p) for p in inner]
    for i in range(n):
        j = (i + 1) % n
        br.faces.new((vo[i], vo[j], vi[j], vi[i]))
    _node_obj(f"GATE_{gid}_ring", br, "cyan_hot", parent=root)
    bh = bmesh.new()
    halo_o = [p * 1.35 for p in outer]
    ho = [bh.verts.new(p + Vector((0, 0, 0.02))) for p in halo_o]
    hi = [bh.verts.new(p + Vector((0, 0, 0.02))) for p in outer]
    for i in range(n):
        j = (i + 1) % n
        bh.faces.new((ho[i], ho[j], hi[j], hi[i]))
    _node_obj(f"GATE_{gid}_halo", bh, "portal", parent=root)
    bd = bmesh.new()
    bd.faces.new([bd.verts.new(p * 0.97 + Vector((0, 0, 0.05))) for p in inner])
    _node_obj(f"GATE_{gid}_disc", bd, "portal", parent=root, props={"spin": f"0,{spin:g},0"})
    bs = bmesh.new()
    _spiral(bs, rr * 0.1, rr * 0.9, 1.1, 4, rr * 0.08, -0.08)
    _node_obj(f"GATE_{gid}_swirl", bs, "portal_l", parent=root, props={"spin": f"0,{-spin * 1.5:g},0"})
    # 전광 (꺾인 선)
    ba = bmesh.new()
    for k in range(7):
        a = rng.uniform(0, 2 * math.pi)
        p = Vector((math.cos(a) * rr, math.sin(a) * rr, 0))
        d = Vector((math.cos(a), math.sin(a), 0))
        t = Vector((-d.y, d.x, 0))
        pts = [p]
        for s in range(4):
            p = p + d * rng.uniform(0.3, 0.7) + t * rng.uniform(-0.4, 0.4) + Vector((0, 0, rng.uniform(-0.3, 0.3)))
            pts.append(p)
        for a_, b_ in zip(pts, pts[1:]):
            w = (b_ - a_).normalized().cross(Vector((0, 0, 1))).normalized() * 0.05
            vs = [ba.verts.new(a_ - w), ba.verts.new(b_ - w), ba.verts.new(b_ + w), ba.verts.new(a_ + w)]
            ba.faces.new(vs)
    _node_obj(f"GATE_{gid}_arcs", ba, "glow", parent=root, props={"flicker": 0.12})
    C.add_node(root)
    C.marker(f"LIGHT_gate_{gid}", tuple(Vector(center)), props={"color": GLOW["glow"], "intensity": 4.0,
                                                               "range": radius * 8, "pointLight": 1})
    return root


def scorch(C, x, y, r, *, z=0.0, seed=0):
    """불시착 자국: 그을린 흙 + 패인 줄."""
    rng = random.Random(seed)
    pts = [(math.cos(2 * math.pi * i / 20) * r * rng.uniform(0.8, 1.15), math.sin(2 * math.pi * i / 20) * r * rng.uniform(0.8, 1.15))
           for i in range(20)]
    C.decal("soil", pts, (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.03)
    C.decal("trunk", [(u * 0.55, v * 0.55) for u, v in pts], (x, y, z), (0, 0, 1), up=(0, 1, 0), lift=0.035)


def barricade(C, x, y, *, yaw=0.0, z=0.0, w=1.6, h=0.95):
    """진압반 바리케이드 (모나티엄 진압반: 남보라 지휘색 + 청록 비살상 띠). 1막 시가전 엄폐물.
    두 다리 받침 + 둥근 모서리 판 + 청록 띠 + 흰 글자. 정면 -Y."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    N = (Mx.to_3x3() @ Vector((0, -1, 0))).normalized()
    R = (Mx.to_3x3() @ Vector((1, 0, 0))).normalized()
    c = Mx @ Vector((0, 0, h * 0.55))
    C.plate("violet", hw.rrect(w, h * 0.62, 0.12, 3), tuple(c), tuple(N), 0.06, kind="main", back=0.03)
    for sgn in (1, -1):
        C.strip("teal", c - R * (w / 2 - 0.08) + N * (0.031 * sgn) - Vector((0, 0, 0.12)),
                c + R * (w / 2 - 0.08) + N * (0.031 * sgn) - Vector((0, 0, 0.12)), 0.1, N * sgn, lift=0.004)
        C.text("white", "진압반 · MONATIUM SUPPRESSION UNIT", 0.075, c + N * (0.031 * sgn) + Vector((0, 0, 0.08)), N * sgn,
               lift=0.004)
    for s_ in (-1, 1):
        foot = Mx @ Vector((s_ * (w / 2 - 0.15), 0, 0))
        # 다리 기둥은 판(두께 6 cm)보다 굵게 7 cm: 같으면 기둥 옆면이 판 앞뒤 면과 같은 평면
        C.beam("steel", foot + Vector((0, 0, 0.02)), foot + Vector((0, 0, h * 0.8)), 0.07, 0.07, kind="detail")
        C.beam("steel", foot - N * 0.3, foot + N * 0.3, 0.07, 0.05, kind="detail")
        C.beam("steel", foot - N * 0.28 + Vector((0, 0, 0.03)), foot + Vector((0, 0, h * 0.45)), 0.04, 0.04,
               kind="detail")
        C.beam("steel", foot + N * 0.28 + Vector((0, 0, 0.03)), foot + Vector((0, 0, h * 0.45)), 0.04, 0.04,
               kind="detail")
    barricade_col(C, x, y, z, yaw, w, h)


def barricade_col(C, x, y, z, yaw, w, h):
    """바리케이드 COL: 받침 다리 판(앞뒤 0.3 m, 높이 0.08: 밟고 설 수 있다) + 곧게 선 판(두께 0.14 m).
    예전 상자(앞뒤 0.6 m 통째)는 가슴 높이에서 판 앞뒤로 0.27 m씩 보이지 않는 벽이 남았고, 사다리꼴 비탈은 점프한
    캡슐이 비탈에 얹혔다."""
    C.lcol(x, y, z, yaw, -w / 2, w / 2, -0.3, 0.3, 0, 0.08)
    C.lcol(x, y, z, yaw, -w / 2, w / 2, -0.07, 0.07, 0, h)


def sandbag_wall(C, x, y, *, yaw=0.0, z=0.0, n=4, rows=3):
    """모래주머니 벽 (훈련장·1막 엄폐). 정면 -Y."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    for row in range(rows):
        for k in range(n - row % 2):
            off = -0.31 * (n - 1) + k * 0.62 + (0.31 if row % 2 else 0)
            p = Mx @ Vector((off, 0, 0.14 + row * 0.24))
            C.blob("sand", tuple(p), 0.34, (1, 0.6, 0.42), segs=8, rings=4, kind="main", rot_z=math.radians(yaw))
        for k in range(n - row % 2):
            off = -0.31 * (n - 1) + k * 0.62 + (0.31 if row % 2 else 0)
            p = Mx @ Vector((off, -0.2, 0.16 + row * 0.24))
            C.strip("sand_d", p - (Mx.to_3x3() @ Vector((0.18, 0, 0))), p + (Mx.to_3x3() @ Vector((0.18, 0, 0))),
                    0.03, (Mx.to_3x3() @ Vector((0, -1, 0))), lift=0.0)
    half = 0.31 * (n - 1) + 0.32
    C.lcol(x, y, z, yaw, -half, half, -0.2, 0.2, 0, 0.14 + (rows - 1) * 0.24 + 0.14)


PAL["sand_d"] = "#a8946c"


# ================================================================== 원경·위성 시점 (1막 위성 브리핑 act1_overview)
# 수백 m~수 km 위에서 내려다보는 도시용 값싼 모듈. 기존 함수의 동작은 바꾸지 않는다.
# 바닥면 없는 상자(삼각형 10개), 박공집, 육각 쌍뿔 나무(12개), 높이가 바뀌는 고가 궤도, 고가역, 지하철 출입구, 연기 기둥.

PAL.update({
    "smoke_l": "#d9d6d0",    # 흰 연기 (불투명, 그림자를 드리운다)
    "smoke_d": "#6e6a72",    # 검은 연기 (기름·차량 화재)
    "soot": "#2f2b2e",       # 그을음 (폐허 변형 계획의 soot과 같은 값)
})


def _bm_box_open(bm, x0, x1, y0, y1, z0, z1):
    """바닥면 없는 상자 (위에서만 보는 건물·지붕용, 삼각형 10개)."""
    xs, ys = (min(x0, x1), max(x0, x1)), (min(y0, y1), max(y0, y1))
    v = [bm.verts.new((x, y, z)) for z in (z0, z1) for y in ys for x in xs]
    for f in ((4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        bm.faces.new([v[i] for i in f])


def lod_box(C, key, x0, x1, y0, y1, z0, z1, *, kind="main"):
    """원경 건물·지붕·차량 상자 (바닥면 없음)."""
    _bm_box_open(C.bm(key, kind), x0, x1, y0, y1, z0, z1)


def lod_poly_prism(C, key, pts, z0, z1, *, kind="main"):
    """xy 볼록 다각형(반시계)을 z0..z1로 세운 판 (바닥면 없음). 잘린 블록 바닥판용."""
    _bm_prism(C.bm(key, kind), pts, z0, z1, top=True, bottom=False)


def lod_gable(C, key_wall, key_roof, x0, x1, y0, y1, z0, z_eave, z_ridge, *, axis="x", kind="main"):
    """박공지붕 집: 벽 상자 + 맞배지붕(용마루가 axis 방향). 위에서 보면 두 지붕면이 해 쪽·그늘 쪽으로 갈린다."""
    _bm_box_open(C.bm(key_wall, kind), x0, x1, y0, y1, z0, z_eave)
    b = C.bm(key_roof, kind)
    o = 0.4                                  # 처마
    if axis == "x":
        ym = (y0 + y1) / 2
        P = [(x0 - o, y0 - o, z_eave - 0.2), (x1 + o, y0 - o, z_eave - 0.2), (x1 + o, ym, z_ridge),
             (x0 - o, ym, z_ridge), (x0 - o, y1 + o, z_eave - 0.2), (x1 + o, y1 + o, z_eave - 0.2)]
        q = [b.verts.new(p) for p in P]
        b.faces.new((q[0], q[1], q[2], q[3]))
        b.faces.new((q[3], q[2], q[5], q[4]))
        b.faces.new((q[0], q[3], q[4]))
        b.faces.new((q[1], q[5], q[2]))
    else:
        xm = (x0 + x1) / 2
        P = [(x0 - o, y0 - o, z_eave - 0.2), (x0 - o, y1 + o, z_eave - 0.2), (xm, y1 + o, z_ridge),
             (xm, y0 - o, z_ridge), (x1 + o, y0 - o, z_eave - 0.2), (x1 + o, y1 + o, z_eave - 0.2)]
        q = [b.verts.new(p) for p in P]
        b.faces.new((q[0], q[3], q[2], q[1]))
        b.faces.new((q[3], q[4], q[5], q[2]))
        b.faces.new((q[0], q[4], q[3]))
        b.faces.new((q[1], q[2], q[5]))


def lod_tree(C, x, y, *, h=8.0, r=3.0, z=0.0, key="leaf", rot=0.0, kind="main", sides=6, smooth=True):
    """다각 쌍뿔 수관 (삼각형 2×sides개, 줄기 없음). 위에서 보는 가로수·공원·숲 가장자리용.
    smooth면 정점을 공유하는 부드러운 면(툰 명암이 둥근 덩어리처럼 갈리고 glb 정점이 1/4로 준다)."""
    b = C.bm(key, kind)
    zc = z + h * 0.55
    top = b.verts.new((x, y, z + h))
    bot = b.verts.new((x, y, z + h * 0.18))
    ring = [b.verts.new((x + math.cos(rot + k * 2 * math.pi / sides) * r,
                         y + math.sin(rot + k * 2 * math.pi / sides) * r, zc)) for k in range(sides)]
    for k in range(sides):
        k2 = (k + 1) % sides
        b.faces.new((ring[k], ring[k2], top)).smooth = smooth
        b.faces.new((ring[k2], ring[k], bot)).smooth = smooth


def fillet_path(pts, r, seg=6):
    """꺾은선의 안쪽 꼭짓점을 반지름 r 원호로 둥글린다. pts = [(x, y[, z]), ...] (z는 꼭짓점 값을 그대로 씀).
    r은 수 하나 또는 안쪽 꼭짓점마다의 목록."""
    P = [Vector((p[0], p[1], p[2] if len(p) > 2 else 0.0)) for p in pts]
    rs = list(r) if isinstance(r, (list, tuple)) else [r] * max(0, len(P) - 2)
    out = [P[0]]
    for i in range(1, len(P) - 1):
        r = rs[i - 1]
        a, b, c = P[i - 1], P[i], P[i + 1]
        d0 = Vector((b.x - a.x, b.y - a.y, 0))
        d1 = Vector((c.x - b.x, c.y - b.y, 0))
        if d0.length < 1e-6 or d1.length < 1e-6:
            out.append(b)
            continue
        d0.normalize()
        d1.normalize()
        turn = math.acos(max(-1.0, min(1.0, d0.dot(d1))))
        if turn < 1e-3:
            out.append(b)
            continue
        t = min(r * math.tan(turn / 2), (b - a).length * 0.49, (c - b).length * 0.49)
        rr = t / math.tan(turn / 2)
        p0 = b - d0 * t
        n0 = Vector((-d0.y, d0.x, 0)) * (1 if d0.cross(d1).z > 0 else -1)
        ctr = p0 + n0 * rr
        a0 = math.atan2(p0.y - ctr.y, p0.x - ctr.x)
        sgn = 1 if d0.cross(d1).z > 0 else -1
        for k in range(seg + 1):
            ang = a0 + sgn * turn * k / seg
            out.append(Vector((ctr.x + math.cos(ang) * rr, ctr.y + math.sin(ang) * rr, b.z)))
    out.append(P[-1])
    return [(p.x, p.y, p.z) for p in out]


def path_points(pts, step):
    """꺾은선을 step 간격으로 다시 뽑는다 (끝점 포함). 반환: [(x, y, z, 누적 길이)]."""
    P = [Vector(p) for p in pts]
    out = [(P[0].x, P[0].y, P[0].z, 0.0)]
    s = 0.0
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        L = (b - a).length
        n = max(1, int(math.ceil(L / step)))
        for k in range(1, n + 1):
            q = a.lerp(b, k / n)
            out.append((q.x, q.y, q.z, s + L * k / n))
        s += L
    return out


def monorail_path(C, pts, *, zf=None, pitch=24.0, beam_w=1.0, beam_h=1.3, ground=0.0, segs=8, step=12.0,
                  avoid=None, pillar_from=0.0, pillar_to=None, glow=True):
    """높이가 바뀌는 모노레일 고가 궤도 (monorail의 원경판). pts = [(x, y), ...] 또는 [(x, y, z)] 꺾은선(fillet_path로
    둥글린 것). zf(x, y) → 보 중심 높이(없으면 점의 z, 그것도 0이면 7.5). 기둥은 길이 pitch마다 T자 받침,
    avoid(x, y)가 참이면 그 기둥은 건너뛴다. 반환: 다시 뽑은 점 [(x, y, z_center, s)]."""
    P = [(p[0], p[1], (p[2] if len(p) > 2 and p[2] else 7.5)) for p in pts]
    R = path_points(P, step)
    if zf is not None:
        R = [(x, y, zf(x, y), s) for (x, y, z, s) in R]
    for i in range(len(R) - 1):
        a, b = Vector(R[i][:3]), Vector(R[i + 1][:3])
        C.beam("concrete", a, b, beam_w, beam_h)
        if glow:
            C.strip("glow", a + Vector((0, 0, beam_h / 2)), b + Vector((0, 0, beam_h / 2)), 0.08, lift=0.01)
    total = R[-1][3]
    s = pillar_from
    end = total if pillar_to is None else pillar_to
    j = 0
    while s <= end + 1e-6:
        while j < len(R) - 2 and R[j + 1][3] < s:
            j += 1
        a, b = R[j], R[j + 1]
        t = 0.0 if b[3] == a[3] else (s - a[3]) / (b[3] - a[3])
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        z = a[2] + (b[2] - a[2]) * t
        if not (avoid and avoid(x, y)):
            d = Vector((b[0] - a[0], b[1] - a[1], 0))
            side = Vector((-d.y, d.x, 0)).normalized() if d.length > 1e-6 else Vector((0, 1, 0))
            top = z - beam_h / 2 - 1.0
            C.cyl("concrete", (x, y, ground), (x, y, top), 0.55, segs=segs, cap=False)
            p = Vector((x, y, z - beam_h / 2 - 0.6))
            C.beam("concrete", p - side * 1.3, p + side * 1.3, 1.1, 0.9)
        s += pitch
    return R


def station_platform(C, a0, a1, c, *, axis="x", z=7.5, beam_h=1.3, width=3.4, gap=1.45, roof=True, roof_key="white",
                     floor_key="concrete_d", posts=None, stairs=(), ground=0.0, name=None, en=None):
    """고가 모노레일 역: 궤도 양쪽 승강장(윗면 = 궤도 윗면 + 0.05) + 받침 보 + 지붕 + 계단탑.
    a0..a1 = 궤도 방향 범위, c = 궤도 중심선(axis='x'면 y, 'y'면 x). posts = 받침 보 위치(궤도 방향 좌표, 기존 궤도
    기둥 자리에 맞춘다. 없으면 8 m마다 + 가운데 기둥). stairs = [(위치, 쪽 ±1, 바깥 거리 d0, d1)]: 승강장 바깥에서
    d0..d1(궤도 중심에서 잰 거리) 사이에 계단탑을 세우고 다리로 잇는다. 반환: dict(top=승강장 윗면 z, roof=지붕 z)."""
    def R(u0, u1, v0, v1):
        """(궤도 방향 u, 옆 방향 v) 범위 → (x0, x1, y0, y1)."""
        if axis == "x":
            return u0, u1, c + v0, c + v1
        return c + v0, c + v1, u0, u1
    top = z + beam_h / 2 + 0.05
    edge = gap + width
    for s in (-1, 1):
        v0, v1 = sorted((s * gap, s * edge))
        C.box(floor_key, *R(a0, a1, v0, v1), top - 0.45, top)
        vv = sorted((s * (edge - 0.15), s * edge))
        C.box("steel", *R(a0, a1, vv[0], vv[1]), top, top + 1.0, kind="detail")
        C.strip("hazard", Vector((*_uv(axis, a0, s * (gap + 0.25), c), top)),
                Vector((*_uv(axis, a1, s * (gap + 0.25), c), top)), 0.25, lift=0.012)
    us = posts if posts is not None else [a0 + 2 + k * 8.0 for k in range(int((a1 - a0 - 4) / 8.0) + 1)]
    for u in us:
        C.box("concrete", *R(u - 0.6, u + 0.6, -edge, edge), top - 1.25, top - 0.45)
        if posts is None:
            px, py = _uv(axis, u, 0.0, c)
            C.cyl("concrete", (px, py, ground), (px, py, top - 1.25), 0.6, segs=10, cap=False)
    zr = top + 3.2
    if roof:
        for u in us:
            for s in (-1, 1):
                v = s * (edge - 0.3)
                C.box("metal", *R(u - 0.15, u + 0.15, v - 0.15, v + 0.15), top, zr, kind="detail")
        C.box(roof_key, *R(a0 - 1.0, a1 + 1.0, -edge - 0.6, edge + 0.6), zr, zr + 0.35)
        C.box("glass_d", *R(a0 + 2.0, a1 - 2.0, -0.9, 0.9), zr + 0.35, zr + 0.6)
    for (u, s, d0, d1) in stairs:
        lo, hi = sorted((s * d0, s * d1))
        C.box("navy_l", *R(u - 3.0, u + 3.0, lo, hi), ground, top + 3.0)
        C.box("glass", *R(u - 2.6, u + 2.6, lo + 0.2, hi - 0.2), top + 3.0, top + 3.15, kind="detail")
        blo, bhi = sorted((s * edge, s * d0))
        if bhi - blo > 0.05:
            C.box(floor_key, *R(u - 1.6, u + 1.6, blo, bhi), top - 0.45, top)
            C.box("glass_d", *R(u - 1.6, u + 1.6, blo, bhi), top + 2.6, top + 2.8, kind="detail")
    if name:
        for s in (-1, 1):
            px, py = _uv(axis, (a0 + a1) / 2, s * (edge + 0.62), c)
            N = (0, s, 0) if axis == "x" else (s, 0, 0)
            C.text("white", name, 0.9, (px, py, zr - 0.3), N)
            if en:
                C.text("glow", en, 0.45, (px, py, zr - 1.2), N)
    return {"top": top, "roof": zr}


def _uv(axis, u, v, c):
    return (u, c + v) if axis == "x" else (c + v, u)


def subway_entrance(C, x, y, *, yaw=0.0, z=0.0, name=None, en=None, w=2.8, length=6.0, key="navy", roof="teal"):
    """지하철 출입구 (계단 덮개 + 기둥 표지). 정면(-Y, yaw로 돌림)이 계단 입구이고 계단은 +Y 쪽으로 내려간다.
    위에서 보면 청록 지붕 판 + 시안 표지등 점. 반환: 입구 바닥 중심과 계단 아래 끝(-4.5 m) 위치."""
    Mx = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")

    def bx(k, x0, x1, y0, y1, z0, z1, kind="main"):
        _bm_box(C.bm(k, kind), x0, x1, y0, y1, z0, z1, matrix=Mx)
    hw_ = w / 2
    # 계단 구멍(어두운 바닥) + 낮은 옆벽 + 뒷벽
    bx("dark", -hw_ + 0.2, hw_ - 0.2, -length / 2 + 0.3, length / 2 - 0.2, -0.6, 0.02)
    for s in (-1, 1):
        bx(key, s * hw_ - 0.18, s * hw_ + 0.18, -length / 2, length / 2, 0.0, 1.05)
    bx(key, -hw_, hw_, length / 2 - 0.3, length / 2, 0.0, 2.55)
    # 유리 덮개 (뒤쪽 2/3) + 청록 지붕 띠
    for s in (-1, 1):
        bx("metal", s * (hw_ - 0.1) - 0.07, s * (hw_ - 0.1) + 0.07, -length / 6 - 0.07, -length / 6 + 0.07, 1.05, 2.45,
           "detail")
    bx("glass_d", -hw_ - 0.1, hw_ + 0.1, -length / 6, length / 2, 2.45, 2.6)
    bx(roof, -hw_ - 0.15, hw_ + 0.15, -length / 6 - 0.3, -length / 6 + 0.25, 2.3, 2.75)
    # 기둥 표지: 남색 기둥 + 시안 등 상자 (위에서 보이는 점)
    px = hw_ + 0.7
    bx(key, px - 0.18, px + 0.18, -length / 2 - 0.18, -length / 2 + 0.18, 0.0, 2.9)
    bx("glow", px - 0.32, px + 0.32, -length / 2 - 0.32, -length / 2 + 0.32, 2.9, 3.45)
    if name:
        N = Mx.to_3x3() @ Vector((0, -1, 0))
        c = Mx @ Vector((0, -length / 6 - 0.31, 2.53))
        C.text("white", name, 0.26, tuple(c), tuple(N), lift=0.01)
        if en:
            C.text("white", en, 0.12, tuple(c - Vector((0, 0, 0.15))), tuple(N), lift=0.01)
    return {"entrance": Mx @ Vector((0, -length / 2, 0)), "bottom": Mx @ Vector((0, length / 2 - 0.5, -4.5))}


def smoke_column(C, x, y, *, z=0.0, h=60.0, r=6.0, drift=(0.35, 0.1), seed=0, key="smoke_l", key_d="smoke_d",
                 segs=7, rings=4, dark=0.4, fire=True):
    """전쟁 피해 연기 기둥: 바닥의 불씨(UNLIT) + 위로 갈수록 커지고 바람 쪽(drift, 높이 1 m당 수평 m)으로 기우는
    불투명 덩어리 더미. 아래쪽 dark 비율은 검은 연기. 위성 시점에서 그림자를 드리운다."""
    rng = random.Random(seed)
    n = max(3, int(h / 11))
    if fire:
        C.blob("fire", (x, y, z + r * 0.25), r * 0.45, (1, 1, 0.5), segs=6, rings=3)
    for k in range(n):
        t = k / max(1, n - 1)
        zz = z + r * 0.5 + t * h
        rr = r * (0.55 + 1.25 * t) * rng.uniform(0.85, 1.15)
        cx = x + drift[0] * (zz - z) + rng.uniform(-0.15, 0.15) * rr
        cy = y + drift[1] * (zz - z) + rng.uniform(-0.15, 0.15) * rr
        C.blob(key_d if t < dark else key, (cx, cy, zz), rr, (1.0, 1.0, 0.8), segs=segs, rings=rings,
               rot_z=rng.uniform(0, 3))
