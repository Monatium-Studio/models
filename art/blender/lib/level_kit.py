"""엘피니아 함선 내부 모듈 키트 (level_kit).

레벨 규약: docs/LEVELS.md. 프롤로그 함내 레벨 설명: docs/art/level-prologue.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, level_kit as lk
    cb.reset()
    L = lk.Level("prologue_ship")
    L.zone("troop")
    L.floor(-7, 7, -2, 10, 0)
    L.wall("x", -2.2, -7, 7, +1, 0, 2.9, openings=[(0.8, 2.4, 0, 2.0)])
    L.portal("x", -2.4, 1.6, 1.6, 2.0, 0, 0.4)
    L.spawn("player", (-2, 15.7, 0), face=(-2, 30))
    L.finish("levels/prologue_ship.glb", root_props={...})

설계
  - 지오메트리는 (구역, 층, 머티리얼, 종류)별 bmesh에 바로 쌓고 finish에서 한 번에 메시로 만든다.
    → 구역마다 머티리얼별 메시 하나. 모든 보이는 메시에 collider=0 (충돌은 COL_ 박스가 맡는다).
  - 종류(kind): main(아웃라인, 레벨 기본 두께) / detail(얇은 아웃라인) / fine(아웃라인 없음: 데칼, 글자, 발광)
  - 층(layer): base / ceil. ceil은 천장과 매달린 것. 미리보기(PREVIEW=1)에서 빠진다.
  - 그룹(group): 이름 있는 노드로 묶을 지오메트리 (HOLO_<g>, LIGHT_main_<n>, BRIDGE_intact ...).
    mode='node'면 빈 오브젝트 아래 머티리얼별 메시, mode='mesh'면 메시 하나에 그 이름을 붙인다.
  - COL_, TRIG_는 축 정렬 박스 하나씩. 메시 중심 = 오브젝트 원점, 회전·스케일 없음.
    엔진이 월드 AABB로 읽든 트라이메시로 읽든 같은 결과가 나온다.

좌표: Blender Z-up, 1 BU = 1 m. 빈 오브젝트의 -Y가 정면(SPAWN, NPC, CAM, PROP, TARGET).
"""
from __future__ import annotations

import math
import os
import random
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw

# ------------------------------------------------------------------ palette
# 엘피니아 정규군: 회녹·남색 벽, 금색 포인트, 시안 발광 (docs/art/weapons-home.md 2·3장과 같은 계열)
PAL = {
    "hull": "#a3ada1",      # 회녹 밝은 벽판 (전투복 상의 #a3ada1)
    "hull_d": "#7f8a80",    # 회녹 짙은 벽판·징두리 (여밈 #7f8a80)
    "olive": "#8d988c",     # 회녹 폴리머 (제식 화기와 같음)
    "navy": "#3c4558",      # 남색: 걸레받이, 난간 받침, 천장 리브, 코니스
    "navy_d": "#272d3b",    # 짙은 남색: 홀로 방 바닥·벽, 패널선
    "navy_l": "#566079",    # 밝은 남색: 문짝, 화면 테
    "floor": "#646069",     # 자줏빛 회색 바닥판
    "floor_d": "#4f4b55",   # 바닥 패널선·통로 띠
    "metal": "#5d555d",     # 자줏빛 건메탈: 기둥, 구조재
    "steel": "#cfcac4",     # 은색 금속: 난간, 볼트
    "gold": "#d6b25e",      # 금색 포인트: 문틀 테, 엘프 로고, 기둥 고리
    "hazard": "#e8c34a",    # 경고 노랑: 계단 코, 낙하 가장자리
    "paper": "#e9e0c8",     # 흰 스텐실 글자·선
    "red_d": "#7a3a3a",     # 꺼진 경고등 렌즈
    "pad": "#465a78",       # 훈련 블록 쿠션 (남청)
    "seat": "#4a5468",      # 좌석 천
    "lamp_off": "#7d8798",  # 꺼진 조명판 (LIGHT_main 아래에 깔림)
    "mattress": "#d3d8cc",  # 매트리스 시트
    "blanket": "#8d988c",   # 모포 (회녹)
    "pillow": "#ece6da",
    "red": "#c0453c",       # 소화기
    "rubber": "#2a252b",
    "helmet": "#6a636b",    # 헬멧 (전투복 헬멧과 같은 자줏빛 회색)
    "scorch": "#2a2326",    # 그을림
}
# UNLIT (조명 없는 단색, 발광)
GLOW = {
    "glow": "#7ff0ea",      # 시안 발광 (엘피니아 장비)
    "lamp": "#e9fbf8",      # 천장 조명판 (거의 흰 시안)
    "glow_d": "#2c8f8d",    # 어두운 시안 (꺼진 패널 바탕, 홀로 격자 약한 선)
    "screen": "#14283c",    # 화면 바탕 (짙은 남청)
    "star": "#ffffff",
    "star_c": "#bfefff",
    "star_y": "#ffe9b8",
    "space": "#0d1428",     # 우주 (sky와 같은 색)
    "alert": "#ff4a3a",     # 경고등 켜짐
    "ocean": "#2f6fb0",     # 망원 영상: 바다
    "land": "#6aa860",      # 망원 영상: 육지
    "cloud": "#e8f2f6",
    "amber": "#ffc45a",     # 데이터 강조 (화면 안)
    "engine": "#8ff7ff",    # 함대 엔진 불빛
}
# 반투명 (UNLIT + alpha): 홀로그램, 유리, 빛기둥
ALPHA = {
    "holo": ("#5fe6e0", 0.30),
    "holo_l": ("#9ff4ef", 0.16),
    "glass": ("#a9dce6", 0.10),
    "beam": ("#7ff0ea", 0.12),
    "holo_gold": ("#ffd36a", 0.5),   # 골든 레코드 홀로그램
    "holo_red": ("#ff5a4a", 0.55),   # 홀로그램 표적 표시
}
# 먹선: 원작처럼 붉은 갈색. 아주 어두운 재질은 더 짙게
LINE = "#4a2229"
LINE_DARK = "#24100f"
_DARK = {"navy", "navy_d", "metal", "floor_d", "seat", "pad", "rubber", "scorch"}

_mats: dict[str, bpy.types.Material] = {}


def M(key: str) -> bpy.types.Material:
    """키트 팔레트 머티리얼 (이름 lk_<key>, 발광은 UNLIT_lk_<key>)."""
    m = _mats.get(key)
    if m is not None:
        try:
            if m.name in bpy.data.materials:
                return m
        except ReferenceError:
            pass
    if key in GLOW:
        m = cb.mat(f"lk_{key}", GLOW[key], emission=GLOW[key], unlit=True)
    elif key in ALPHA:
        c, a = ALPHA[key]
        m = cb.mat(f"lk_{key}", c, emission=c, unlit=True, alpha=a)
    else:
        m = cb.mat(f"lk_{key}", PAL[key], line=LINE_DARK if key in _DARK else LINE, roughness=0.7)
    _mats[key] = m
    return m


def is_glow(key):
    return key in GLOW or key in ALPHA


def _srgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def vc_material(dark=False):
    """정점색 머티리얼 (불투명 팔레트를 한 머티리얼로). dark면 짙은 먹선."""
    name = "lk_vc_dark" if dark else "lk_vc"
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
    bsdf.inputs["Roughness"].default_value = 0.7
    m["lineColor"] = LINE_DARK if dark else LINE
    return m


# ------------------------------------------------------------------ small math

def yaw_to(src, dst) -> float:
    """src에서 dst를 바라보게 하는 Z 회전(라디안). 로컬 -Y가 그 방향을 향한다."""
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.atan2(dx, -dy)


def frame(normal, up=(0, 0, 1)):
    """면 위 2D 좌표계 (right, up). normal = right x up."""
    N = Vector(normal).normalized()
    U = Vector(up).normalized()
    R = U.cross(N).normalized()
    U = N.cross(R).normalized()
    return tuple(R), tuple(U)


def octagon(r, cx=0.0, cy=0.0):
    return hw.circle(r, 8, cx, cy)


def round_top(w, h, r, n=4, cx=0.0, z0=0.0):
    """아래가 평평하고 위 두 모서리가 둥근 사각형 외곽선 (반시계). 문 개구부 모양."""
    r = min(r, w / 2 - 1e-4, h - 1e-4)
    pts = [(cx + w / 2, z0)]
    pts += hw.arc_pts(cx + w / 2 - r, z0 + h - r, r, 0, 90, n)
    pts += hw.arc_pts(cx - w / 2 + r, z0 + h - r, r, 90, 180, n)
    pts.append((cx - w / 2, z0))
    return pts


def _sub_intervals(a0, a1, cuts):
    """[a0,a1]에서 cuts 구간들을 뺀 나머지 구간 목록."""
    out = [(a0, a1)]
    for c0, c1 in cuts:
        nxt = []
        for s0, s1 in out:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 > s0:
                nxt.append((s0, c0))
            if c1 < s1:
                nxt.append((c1, s1))
        out = nxt
    return [(s0, s1) for s0, s1 in out if s1 - s0 > 1e-4]


# ------------------------------------------------------------------ bmesh writers

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
    # 인덱스: z(0/1)*4 + y(0/1)*2 + x(0/1)
    F = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    for f in F:
        bm.faces.new([v[i] for i in f])


def _bm_poly(bm, pts3d, normal=None):
    vs = [bm.verts.new(Vector(p)) for p in pts3d]
    f = bm.faces.new(vs)
    if normal is not None:
        f.normal_update()
        if f.normal.dot(Vector(normal)) < 0:
            f.normal_flip()
    return f


# ------------------------------------------------------------------ Level

class Level:
    """레벨 조립기. zone()으로 구역을 바꿔 가며 지오메트리와 마커를 쌓고 finish()로 내보낸다."""

    def __init__(self, name, *, preview=None, decal_lift=0.006, vcol=True):
        self.name = name
        self.vcol = vcol
        self.zname = "misc"
        self.layer = "base"
        self.grp = None
        self.groups: dict[str, dict] = {}
        self.acc: dict[tuple, bmesh.types.BMesh] = {}
        self.objs: list[tuple] = []        # (zone, layer, key, kind, obj) finish에서 합침
        self.cols: list[tuple] = []        # (name, zone, x0, x1, y0, y1, z0, z1)
        self.ocols: list[tuple] = []       # (name, x, y, z0, sx, sy, sz, yaw) 돌린 상자 (바닥 중심)
        self.ccols: list[tuple] = []       # (name, verts) 볼록 다면체
        self.trigs: list[tuple] = []       # (id, x0, x1, y0, y1, z0, z1, props)
        self.markers: list[tuple] = []     # (name, loc, rot_matrix3 or yaw, props)
        self.specials: list[tuple] = []    # (zone, obj) 이름 있는 메시 (DOOR_, LIGHT_)
        self.preview = preview if preview is not None else os.environ.get("PREVIEW", "")
        self.lift = decal_lift
        self._ncol = 0

    # ---------------------------------------------------------- state
    def zone(self, name):
        self.zname = name
        self.layer = "base"
        self.grp = None
        return self

    def group(self, name, *, mode="node", parent=None, pivot=None, **props):
        """이후 지오메트리를 이름 있는 노드로 묶는다. group(None)으로 끝낸다.
        parent: 이 그룹 노드를 넣을 다른 그룹, pivot: 노드 원점(회전 중심, spin 속성용)."""
        if name is None:
            self.grp = None
            return self
        g = self.groups.setdefault(name, {"mode": mode, "props": {}, "zone": self.zname, "parent": parent,
                                          "pivot": pivot})
        if parent:
            g["parent"] = parent
        if pivot:
            g["pivot"] = pivot
        g["props"].update(props)
        self.grp = name
        return self

    @contextmanager
    def in_group(self, name, **kw):
        """with L.in_group("HOLO_course"): ... (끝나면 이전 그룹으로)."""
        prev = self.grp
        self.group(name, **kw)
        try:
            yield self
        finally:
            self.grp = prev

    def ceil_layer(self, on=True):
        self.layer = "ceil" if on else "base"
        return self

    def bm(self, key, kind="main", layer=None, group=None):
        k = (self.zname, layer or self.layer, group if group is not None else self.grp, key, kind)
        b = self.acc.get(k)
        if b is None:
            b = self.acc[k] = bmesh.new()
        return b

    def kind_for(self, key, kind):
        return "fine" if is_glow(key) else kind

    # ---------------------------------------------------------- primitives
    def box(self, key, x0, x1, y0, y1, z0, z1, *, kind="main", col=False, layer=None):
        _bm_box(self.bm(key, self.kind_for(key, kind), layer), x0, x1, y0, y1, z0, z1)
        if col:
            self.col(x0, x1, y0, y1, z0, z1)

    def rbox(self, key, center, size, rot=(0, 0, 0), *, kind="main", layer=None):
        """회전한 박스 (보이는 것만, 충돌 없음). rot = XYZ 도."""
        Mx = (Matrix.Translation(Vector(center)) @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
              @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        sx, sy, sz = (s / 2 for s in size)
        _bm_box(self.bm(key, self.kind_for(key, kind), layer), -sx, sx, -sy, sy, -sz, sz, matrix=Mx)

    def poly(self, key, pts3d, *, normal=None, kind="fine", layer=None):
        return _bm_poly(self.bm(key, self.kind_for(key, kind), layer), pts3d, normal)

    def decal(self, key, pts2d, center, normal, *, up=(0, 0, 1), lift=None, kind="fine", layer=None):
        """면에 붙는 2D 다각형 (center = 면 위 점, normal = 바깥 방향)."""
        R, U = frame(normal, up)
        R, U, N = Vector(R), Vector(U), Vector(normal).normalized()
        c = Vector(center) + N * (self.lift if lift is None else lift)
        return self.poly(key, [c + R * u + U * v for u, v in pts2d], normal=N, kind=kind, layer=layer)

    def ring(self, key, outer, inner, center, normal, *, up=(0, 0, 1), lift=None, kind="fine", layer=None):
        """같은 점 개수의 바깥·안 외곽선 사이를 채우는 고리 데칼 (패널 테두리, 원판 테)."""
        R, U = frame(normal, up)
        R, U, N = Vector(R), Vector(U), Vector(normal).normalized()
        c = Vector(center) + N * (self.lift if lift is None else lift)
        b = self.bm(key, self.kind_for(key, kind), layer)
        vo = [b.verts.new(c + R * u + U * v) for u, v in outer]
        vi = [b.verts.new(c + R * u + U * v) for u, v in inner]
        n = len(vo)
        for i in range(n):
            j = (i + 1) % n
            f = b.faces.new((vo[i], vo[j], vi[j], vi[i]))
            f.normal_update()
            if f.normal.dot(N) < 0:
                f.normal_flip()

    def strip(self, key, p0, p1, width, normal, *, lift=None, kind="fine", layer=None):
        """두 점 사이 띠 (바닥 선, 벽 줄). normal 쪽으로 lift만큼 띄운다."""
        P0, P1, N = Vector(p0), Vector(p1), Vector(normal).normalized()
        d = (P1 - P0).normalized()
        s = N.cross(d).normalized() * (width / 2)
        o = N * (self.lift if lift is None else lift)
        return self.poly(key, [P0 - s + o, P1 - s + o, P1 + s + o, P0 + s + o], normal=N, kind=kind, layer=layer)

    def extrude(self, key, pts2d, center, normal, depth, *, up=(0, 0, 1), kind="main", layer=None, back=0.0):
        """2D 외곽선을 normal 방향으로 depth만큼 돌출 (center 면에서 -back .. depth-back)."""
        R, U = frame(normal, up)
        R, U, N = Vector(R), Vector(U), Vector(normal).normalized()
        c = Vector(center)
        b = self.bm(key, self.kind_for(key, kind), layer)
        f0 = [b.verts.new(c + R * u + U * v - N * back) for u, v in pts2d]
        f1 = [b.verts.new(c + R * u + U * v + N * (depth - back)) for u, v in pts2d]
        n = len(pts2d)
        faces = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
        for i in range(n):
            j = (i + 1) % n
            faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
        bmesh.ops.recalc_face_normals(b, faces=faces)

    def ring_extrude(self, key, outer, inner, center, normal, depth, *, up=(0, 0, 1), kind="main", layer=None,
                     back=0.0):
        """구멍 있는 판 (창틀, 둥근 창 고리). outer/inner는 같은 점 개수."""
        R, U = frame(normal, up)
        R, U, N = Vector(R), Vector(U), Vector(normal).normalized()
        c = Vector(center)
        b = self.bm(key, self.kind_for(key, kind), layer)

        def ring_at(pts, off):
            return [b.verts.new(c + R * u + U * v + N * off) for u, v in pts]

        o0, o1 = ring_at(outer, -back), ring_at(outer, depth - back)
        i0, i1 = ring_at(inner, -back), ring_at(inner, depth - back)
        n = len(outer)
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces += [b.faces.new((o1[i], o1[j], i1[j], i1[i])),     # 앞면
                      b.faces.new((o0[j], o0[i], i0[i], i0[j])),     # 뒷면
                      b.faces.new((o0[i], o0[j], o1[j], o1[i])),     # 바깥 둘레
                      b.faces.new((i1[i], i1[j], i0[j], i0[i]))]     # 안 둘레
        bmesh.ops.recalc_face_normals(b, faces=faces)

    def obj(self, key, o, *, kind="main", layer=None):
        """cb/hw로 만든 오브젝트를 등록 (finish에서 구역·머티리얼 메시에 합쳐진다)."""
        if o is None:
            return None
        self.objs.append((self.zname, layer or self.layer, self.grp, key, self.kind_for(key, kind), o))
        return o

    def bev(self, key, size, loc, *, rot=(0, 0, 0), bevel=0.01, seg=1, kind="main", layer=None):
        """둥글린 박스 (베벨 모디파이어, 소품용). size = 전체 크기, rot = XYZ 도."""
        return self.obj(key, hw.box("bev", size, loc, rot=rot, bevel=bevel, seg=seg), kind=kind, layer=layer)

    def dome(self, key, center, r, *, scale=(1, 1, 1), segs=14, rings=5, kind="main", layer=None):
        """반구 (바닥이 열린 돔: 헬멧, 경고등 렌즈). center = 바닥 원 중심."""
        b = self.bm(key, self.kind_for(key, kind), layer)
        c = Vector(center)
        sx, sy, sz = scale
        top = b.verts.new(c + Vector((0, 0, r * sz)))
        ringv = []
        for j in range(rings):
            a = math.pi / 2 * j / rings
            ringv.append([b.verts.new(c + Vector((math.cos(2 * math.pi * i / segs) * math.cos(a) * r * sx,
                                                   math.sin(2 * math.pi * i / segs) * math.cos(a) * r * sy,
                                                   math.sin(a) * r * sz))) for i in range(segs)])
        faces = []
        for j in range(rings - 1):
            for i in range(segs):
                i2 = (i + 1) % segs
                faces.append(b.faces.new((ringv[j][i], ringv[j][i2], ringv[j + 1][i2], ringv[j + 1][i])))
        for i in range(segs):
            faces.append(b.faces.new((ringv[-1][i], ringv[-1][(i + 1) % segs], top)))
        for f in faces:
            f.smooth = True
        bmesh.ops.recalc_face_normals(b, faces=faces)

    def cyl(self, key, p0, p1, r, *, verts=12, kind="main", layer=None, cap=True, r2=None):
        """p0→p1 원기둥 (임의 방향)."""
        P0, P1 = Vector(p0), Vector(p1)
        d = P1 - P0
        o = cb.cylinder("cyl", radius=r, radius2=r2, depth=d.length, verts=verts, cap=cap)
        q = d.normalized().to_track_quat("Z", "Y")
        o.matrix_world = Matrix.Translation((P0 + P1) / 2) @ q.to_matrix().to_4x4()
        return self.obj(key, o, kind=kind, layer=layer)

    def text(self, key, s, size, center, normal, *, up=(0, 0, 1), lift=None, kind="fine", layer=None, font=None,
             align="CENTER", spacing=1.0):
        R, U = frame(normal, up)
        N = Vector(normal).normalized()
        c = Vector(center) + N * (self.lift if lift is None else lift)
        o = hw.text("txt", s, size, tuple(c), right=R, up=U, mat=None, font=font, lift=0.0, align=align,
                    spacing=spacing)
        return self.obj(key, o, kind=kind, layer=layer)

    def logo(self, center, size, normal, *, up=(0, 0, 1), key="gold", disc="navy", disc_scale=0.66, ring=None,
             lift=None, kind="fine", layer=None):
        """원작 엘프 로고 (높이 size). disc: 바탕 원판 머티리얼, ring: 원판 테 머티리얼."""
        lf = self.lift if lift is None else lift
        R, U = frame(normal, up)
        if disc:
            self.decal(disc, hw.circle(size * disc_scale, 32), center, normal, up=up, lift=lf, kind=kind, layer=layer)
        if ring:
            r0 = size * disc_scale
            self.ring(ring, hw.circle(r0 + size * 0.06, 32), hw.circle(r0, 32), center, normal, up=up,
                      lift=lf, kind=kind, layer=layer)
        N = Vector(normal).normalized()
        c = Vector(center) + N * (lf + 0.003)
        o = hw.elf_logo("logo", tuple(c), size, right=R, up=U, mat=None, lift=0.0)
        if o is None:
            self.marker(f"EMBLEM_slot_{len(self.markers)}", tuple(center), props={"emblemSize": size})
            return None
        return self.obj(key, o, kind=kind, layer=layer)

    # ---------------------------------------------------------- collision / triggers
    def col(self, x0, x1, y0, y1, z0, z1, name=None):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        self._ncol += 1
        self.cols.append((name or f"COL_{self.zname}_{self._ncol:03d}", self.zname, x0, x1, y0, y1, z0, z1))

    def ocol(self, base, size, yaw=0.0, name=None):
        """돌린 COL_ 상자: base = 바닥 중심 (x, y, z0), size = (로컬 X, 로컬 Y, 높이), yaw = Z축 도.
        LevelLoader가 회전 상자 충돌체로 만든다."""
        x, y, z0 = base
        sx, sy, sz = size
        if min(sx, sy, sz) < 1e-4:
            return
        self._ncol += 1
        self.ocols.append((name or f"COL_{self.zname}_{self._ncol:03d}", x, y, z0, sx, sy, sz, yaw))

    def ccol(self, verts, name=None):
        """볼록 COL_ (꼭짓점들의 볼록 껍질, 월드 좌표). 둥근 탁자·기둥처럼 상자로는 모서리가 남는 모양."""
        self._ncol += 1
        self.ccols.append((name or f"COL_{self.zname}_{self._ncol:03d}", [tuple(v) for v in verts]))

    def ccyl(self, cx, cy, r, z0, z1, n=16, name=None):
        """세운 원기둥 COL (n각 기둥, 변까지 거리 = r)."""
        rr = r / math.cos(math.pi / n)
        self.ccol([(cx + math.cos(2 * math.pi * k / n) * rr, cy + math.sin(2 * math.pi * k / n) * rr, z)
                   for k in range(n) for z in (z0, z1)], name=name)

    def attach(self, group, marker):
        """그룹 노드(또는 mode=mesh 메시)를 마커 빈 오브젝트의 자식으로 (미션이 '마커 아래 메시'를 찾을 때)."""
        self.attachments = getattr(self, "attachments", [])
        self.attachments.append((group, marker))

    def trig(self, tid, x0, x1, y0, y1, z0, z1, **props):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        self.trigs.append((tid, x0, x1, y0, y1, z0, z1, props))

    # ---------------------------------------------------------- markers
    def marker(self, name, loc, *, yaw=None, face=None, look=None, props=None):
        """빈 오브젝트 마커. yaw(도) 또는 face=(x,y) 또는 look=(x,y,z)(3D 시선)."""
        rot = None
        if look is not None:
            d = Vector(look) - Vector(loc)
            rot = d.normalized().to_track_quat("-Y", "Z").to_euler()
        elif face is not None:
            rot = (0, 0, yaw_to(loc, face))
        elif yaw is not None:
            rot = (0, 0, math.radians(yaw))
        self.markers.append((name, tuple(loc), rot, dict(props or {})))

    def spawn(self, sid, loc, **kw):
        self.marker(f"SPAWN_{sid}", loc, **kw)

    def npc(self, nid, loc, model, *, props=None, **kw):
        p = {"model": model}
        p.update(props or {})
        self.marker(f"NPC_{nid}", loc, props=p, **kw)

    def target(self, tid, loc, group, *, kind="popup", props=None, **kw):
        p = {"kind": kind, "group": group}
        p.update(props or {})
        self.marker(f"TARGET_{tid}", loc, props=p, **kw)

    def prop(self, pid, loc, model, **kw):
        self.marker(f"PROP_{pid}", loc, props={"model": model}, **kw)

    def mark(self, mid, loc, **kw):
        self.marker(f"MARK_{mid}", loc, **kw)

    def wp(self, wid, loc, **kw):
        self.marker(f"WP_{wid}", loc, **kw)

    def cam_rail(self, shot, points):
        """points: [(t, cam_xyz, look_xyz, fov or None), ...] → CAM_<shot>_<nn>, LOOK_<shot>_<nn>."""
        for i, (t, cam, look, fov) in enumerate(points, start=1):
            p = {"t": float(t)}
            if fov:
                p["fov"] = float(fov)
            self.marker(f"CAM_{shot}_{i:02d}", cam, look=look, props=p)
            self.marker(f"LOOK_{shot}_{i:02d}", look)

    # ---------------------------------------------------------- named meshes (DOOR_, LIGHT_)
    def special(self, name, build, key, props, *, kind="main"):
        """build(bm)로 지오메트리를 채운 이름 있는 메시 하나. 원점 = 바운딩 박스 중심."""
        b = bmesh.new()
        build(b)
        me = bpy.data.meshes.new(name)
        b.to_mesh(me)
        b.free()
        o = bpy.data.objects.new(name, me)
        cb.link(o)
        cb.assign(o, M(key))
        # 원점을 바운딩 박스 중심으로
        lo = Vector((min(v.co.x for v in me.vertices), min(v.co.y for v in me.vertices), min(v.co.z for v in me.vertices)))
        hi = Vector((max(v.co.x for v in me.vertices), max(v.co.y for v in me.vertices), max(v.co.z for v in me.vertices)))
        c = (lo + hi) / 2
        me.transform(Matrix.Translation(-c))
        o.location = c
        for k, v in props.items():
            o[k] = v
        if kind == "fine" or is_glow(key):
            o["noOutline"] = 1
        self.specials.append((self.zname, o))
        return o

    def special_obj(self, name, o, key, props, *, kind="main"):
        """cb/hw로 만든 오브젝트 하나를 이름 있는 메시로 (원점 = 바운딩 박스 중심)."""
        dg = bpy.context.evaluated_depsgraph_get()
        eo = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(eo)
        me.transform(o.matrix_world)
        old = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(old, bpy.types.Mesh) and old.users == 0:
            bpy.data.meshes.remove(old)
        b = bmesh.new()
        b.from_mesh(me)
        bpy.data.meshes.remove(me)
        return self.special(name, lambda bm_: _copy_bm(b, bm_), key, props, kind=kind)

    # ================================================================ modules
    # 벽: axis 'x' = X를 따라 뻗은 벽(면 y=c), 'y' = Y를 따라 뻗은 벽(면 x=c).
    # side = 방 안쪽 방향(+1/-1). 표면은 c, 벽체는 c - side*t 까지.
    def _wpt(self, axis, c, side, a, d, z):
        return (a, c + side * d, z) if axis == "x" else (c + side * d, a, z)

    def _wbox(self, key, axis, c, side, a0, a1, d0, d1, z0, z1, *, kind="main", col=False, layer=None):
        p0 = self._wpt(axis, c, side, a0, d0, z0)
        p1 = self._wpt(axis, c, side, a1, d1, z1)
        self.box(key, p0[0], p1[0], p0[1], p1[1], p0[2], p1[2], kind=kind, col=col, layer=layer)

    def _wnormal(self, axis, side):
        return (0, side, 0) if axis == "x" else (side, 0, 0)

    def _banded(self, key, axis, c, side, a0, a1, d0, d1, z0, z1, openings, *, kind="main", col=False,
                col_only=False, layer=None):
        """개구부를 피해 띠 단위로 박스를 채운다."""
        zs = {z0, z1}
        for (_, _, ozb, ozt) in openings:
            for z in (ozb, ozt):
                if z0 < z < z1:
                    zs.add(z)
        zs = sorted(zs)
        for zb, zt in zip(zs, zs[1:]):
            cuts = [(oa0, oa1) for (oa0, oa1, ozb, ozt) in openings if ozb <= zb + 1e-6 and ozt >= zt - 1e-6]
            for s0, s1 in _sub_intervals(a0, a1, cuts):
                if col_only:
                    p0 = self._wpt(axis, c, side, s0, d0, zb)
                    p1 = self._wpt(axis, c, side, s1, d1, zt)
                    self.col(p0[0], p1[0], p0[1], p1[1], p0[2], p1[2])
                else:
                    self._wbox(key, axis, c, side, s0, s1, d0, d1, zb, zt, kind=kind, col=col, layer=layer)

    def wall(self, axis, c, a0, a1, side, z0, z1, *, openings=(), t=0.2, pitch=2.4, strip=True, pillars=True,
             insets=True, cornice=True, col=True, style="std", band=None, pipes=False, bolts=True, inset_group=None):
        """표준 벽. 아래부터 걸레받이(남) · 징두리(짙은 회녹) · 손잡이 턱(남) + 시안 줄 · 위 벽판(밝은 회녹),
        일정 간격 기둥(건메탈, 금색 고리, 볼트), 위 벽판의 둥근 사각 패널선, 천장 코니스.
        openings: [(a0, a1, z_bottom, z_top)] (월드 z). style='holo'면 홀로 방(남색 바탕 + 시안 격자)."""
        if a1 < a0:
            a0, a1 = a1, a0
        H = z1 - z0
        ops = [(oa0, oa1, ozb, ozt) for (oa0, oa1, ozb, ozt) in openings]
        N = self._wnormal(axis, side)
        upper = "navy_d" if style == "holo" else "hull"
        # 벽체
        self._banded(upper, axis, c, side, a0, a1, -t, 0.0, z0, z1, ops)
        if col:
            self._banded(None, axis, c, side, a0, a1, -t, 0.06, z0, z1, ops, col_only=True)
        # 걸레받이, 징두리, 턱
        self._banded("navy", axis, c, side, a0, a1, 0.0, 0.06, z0, z0 + 0.16, ops)
        self._banded("hull_d", axis, c, side, a0, a1, 0.0, 0.03, z0 + 0.16, z0 + 0.95, ops)
        self._banded("navy", axis, c, side, a0, a1, 0.0, 0.07, z0 + 0.95, z0 + 1.02, ops)
        if strip:
            for (zb, zt) in [(z0 + 0.968, z0 + 1.002)]:
                cuts = [(oa0 - 0.02, oa1 + 0.02) for (oa0, oa1, ozb, ozt) in ops if ozb < zt and ozt > zb]
                for s0, s1 in _sub_intervals(a0 + 0.05, a1 - 0.05, cuts):
                    p0 = self._wpt(axis, c, side, s0, 0.073, zb)   # 턱(0.07) 앞면보다 3 mm 앞
                    p1 = self._wpt(axis, c, side, s1, 0.073, zt)
                    if axis == "x":
                        pts = [(p0[0], p0[1], zb), (p1[0], p0[1], zb), (p1[0], p0[1], zt), (p0[0], p0[1], zt)]
                    else:
                        pts = [(p0[0], p0[1], zb), (p0[0], p1[1], zb), (p0[0], p1[1], zt), (p0[0], p0[1], zt)]
                    self.poly("glow", pts, normal=N)
        if band:  # 높은 벽의 중간 띠 (갑판선)
            for zb in band:
                self._banded("navy", axis, c, side, a0, a1, 0.0, 0.08, zb, zb + 0.14, ops)
        if cornice:
            self._banded("navy", axis, c, side, a0, a1, 0.0, 0.10, z1 - 0.20, z1, ops)
        # 기둥과 패널선
        L_ = a1 - a0
        n = max(1, round(L_ / pitch))
        P = L_ / n
        marks = [a0 + i * P for i in range(n + 1)]

        def blocked(a, half):
            return any(oa0 - half - 0.12 < a < oa1 + half + 0.12 for (oa0, oa1, ozb, ozt) in ops)

        if pillars:
            for i, a in enumerate(marks):
                if i in (0, n):
                    continue
                if blocked(a, 0.11):
                    continue
                self._wbox("metal", axis, c, side, a - 0.11, a + 0.11, 0.0, 0.09, z0, z1 - (0.2 if cornice else 0))
                self._wbox("gold", axis, c, side, a - 0.12, a + 0.12, 0.0, 0.10, z0 + 1.02, z0 + 1.08, kind="detail")
                if bolts:
                    for zb in (z0 + 0.42, z1 - 0.55):
                        for da in (-0.055, 0.055):
                            ctr = self._wpt(axis, c, side, a + da, 0.09, zb)
                            self.decal("steel", octagon(0.018), ctr, N, lift=0.003)
        if insets:
            ztop = z1 - (0.35 if cornice else 0.15)
            zbot = z0 + 1.25
            if band:
                ztop = min(ztop, min(band) - 0.15)
            if ztop - zbot > 0.5:
                for i in range(n):
                    s0, s1 = marks[i] + 0.22, marks[i + 1] - 0.22
                    if s1 - s0 < 0.5:
                        continue
                    if any(oa0 - 0.1 < s1 and oa1 + 0.1 > s0 and ozb < ztop and ozt > zbot
                           for (oa0, oa1, ozb, ozt) in ops):
                        continue
                    w, h = s1 - s0, ztop - zbot
                    ctr = self._wpt(axis, c, side, (s0 + s1) / 2, 0.0, (zbot + ztop) / 2)
                    lk = "glow_d" if style == "holo" else "hull_d"
                    prev_g = self.grp
                    if style == "holo" and inset_group:
                        self.grp = inset_group
                    self.ring(lk, hw.rrect(w, h, 0.12, n=2), hw.rrect(w - 0.05, h - 0.05, 0.10, n=2), ctr, N)
                    if style == "holo":
                        # 홀로 격자: 가로 줄 두 개
                        for k in (1, 2):
                            zz = zbot + h * k / 3
                            q0 = self._wpt(axis, c, side, s0 + 0.12, 0.0, zz)
                            q1 = self._wpt(axis, c, side, s1 - 0.12, 0.0, zz)
                            self.strip("glow_d", q0, q1, 0.02, N)
                    self.grp = prev_g
        if pipes:
            zp = z1 - (0.42 if cornice else 0.3)
            p0 = self._wpt(axis, c, side, a0, 0.16, zp)
            p1 = self._wpt(axis, c, side, a1, 0.16, zp)
            self.cyl("metal", p0, p1, 0.055, verts=10, kind="detail")
            p0 = self._wpt(axis, c, side, a0, 0.13, zp - 0.15)
            p1 = self._wpt(axis, c, side, a1, 0.13, zp - 0.15)
            self.cyl("gold", p0, p1, 0.028, verts=8, kind="detail")
            for a in marks[1:-1]:
                if blocked(a, 0.2):
                    continue
                self._wbox("navy", axis, c, side, a - 0.05, a + 0.05, 0.0, 0.23, zp - 0.24, zp + 0.08, kind="detail")

    def floor(self, x0, x1, y0, y1, z, *, key="floor", line="floor_d", grid=1.2, col=True, t=0.12, lines=True,
              col_depth=0.4, line_group=None, _lines_only=False):
        if not _lines_only:
            self.box(key, x0, x1, y0, y1, z - t, z)
        if col:
            self.col(x0, x1, y0, y1, z - col_depth, z)
        if line_group and lines and grid:
            with self.in_group(line_group):
                self.floor(x0, x1, y0, y1, z, key=key, line=line, grid=grid, col=False, t=t, lines=True,
                           _lines_only=True)
            return
        if lines and grid:
            nx = max(1, round((x1 - x0) / grid))
            ny = max(1, round((y1 - y0) / grid))
            for i in range(1, nx):
                x = x0 + (x1 - x0) * i / nx
                self.strip(line, (x, y0 + 0.02, z), (x, y1 - 0.02, z), 0.025, (0, 0, 1))
            for j in range(1, ny):
                y = y0 + (y1 - y0) * j / ny
                self.strip(line, (x0 + 0.02, y, z), (x1 - 0.02, y, z), 0.025, (0, 0, 1))

    def ceiling(self, x0, x1, y0, y1, z, *, key="navy", rib_axis="x", pitch=2.4, lamps=True, lamp_w=0.5,
                lamp_len=1.2, col=True, rib_key="metal", lamp_rows=None, lamp_group=None):
        """천장 판 + 리브 + 조명판(UNLIT). 층 ceil. lamp_group을 주면 발광판만 그 그룹(LIGHT_main_n)으로."""
        prev = self.layer
        self.layer = "ceil"
        self._lamp_group = lamp_group
        self.box(key, x0, x1, y0, y1, z, z + 0.15)
        if col:
            self.col(x0, x1, y0, y1, z, z + 0.4)
        if rib_axis == "x":  # 리브가 X 방향으로 뻗음, Y를 따라 반복
            n = max(1, round((y1 - y0) / pitch))
            for i in range(1, n):
                y = y0 + (y1 - y0) * i / n
                self.box(rib_key, x0, x1, y - 0.09, y + 0.09, z - 0.14, z)
            if lamps:
                rows = lamp_rows or [(x0 + x1) / 2]
                for i in range(n):
                    yc = y0 + (y1 - y0) * (i + 0.5) / n
                    for xc in rows:
                        self._lamp(xc, yc, z, lamp_len, lamp_w)
        else:
            n = max(1, round((x1 - x0) / pitch))
            for i in range(1, n):
                x = x0 + (x1 - x0) * i / n
                self.box(rib_key, x - 0.09, x + 0.09, y0, y1, z - 0.14, z)
            if lamps:
                rows = lamp_rows or [(y0 + y1) / 2]
                for i in range(n):
                    xc = x0 + (x1 - x0) * (i + 0.5) / n
                    for yc in rows:
                        self._lamp(xc, yc, z, lamp_w, lamp_len)
        self.layer = prev
        self._lamp_group = None

    _lamp_group = None

    def _lamp(self, xc, yc, z, lx, ly, group=None):
        """천장 조명판: 남색 테 + 꺼진 렌즈 + 발광판(LIGHT_main 그룹이면 따로 켜고 끈다)."""
        self.box("navy", xc - lx / 2 - 0.06, xc + lx / 2 + 0.06, yc - ly / 2 - 0.06, yc + ly / 2 + 0.06, z - 0.05, z,
                 kind="detail")
        self.decal("lamp_off", hw.rrect(lx, ly, 0.08, n=2), (xc, yc, z - 0.05), (0, 0, -1), up=(0, 1, 0), lift=0.002)
        g = group or self._lamp_group
        R, U = frame((0, 0, -1), (0, 1, 0))
        c = Vector((xc, yc, z - 0.05 - 0.005))
        pts = [c + Vector(R) * u + Vector(U) * v for u, v in hw.rrect(lx, ly, 0.08, n=2)]
        _bm_poly(self.bm("lamp", "fine", group=g), pts, (0, 0, -1))

    def stairs(self, axis, w0, w1, s_low, dir_up, z_low, z_high, n, tread=0.3, *, key="metal", top_key="floor",
               col=True, stringer=True, nosing=True, solid_to=None):
        """직선 계단. axis 'y'면 Y를 따라 오른다(폭 = X w0..w1). s_low = 아래 끝(첫 단 시작), dir_up = ±1.
        단 높이 = (z_high-z_low)/n. 디딤판 n-1개, 마지막 단 다음부터 z_high 바닥(따로 만든다).
        반환: 위층 바닥이 시작하는 s 값."""
        r = (z_high - z_low) / n
        base = z_low if solid_to is None else solid_to
        if col:
            # 충돌은 단마다 상자가 아니라 단 코를 잇는 경사판 하나 (볼록): 캡슐 아래 반구가 단 모서리에 얹혀 멈추지 않는다
            # (0.22 m 단은 단 상자로는 오르지 못했다, 이동 충돌 감사). 디딤판 위로 최대 반 단쯤 뜨거나 묻힌다
            # 경사면 = 단 코와 디딤판 사이 가운데 선 (반 단 앞에서 바닥, 마지막 단 반 디딤 뒤에서 위층 바닥)
            s_a = s_low - dir_up * tread / 2
            s_b = s_low + dir_up * (n - 0.5) * tread
            prof = [(s_a, min(base, z_low - 0.01)), (s_a, z_low), (s_b, z_high), (s_b, min(base, z_low - 0.01))]
            if axis == "y":
                self.ccol([(w, s, z) for w in (w0, w1) for s, z in prof])
            else:
                self.ccol([(s, w, z) for w in (w0, w1) for s, z in prof])
        for k in range(1, n):
            sa = s_low + dir_up * (k - 1) * tread
            sb = s_low + dir_up * k * tread
            zt = z_low + k * r
            if axis == "y":
                self.box(key, w0, w1, sa, sb, base, zt - 0.05, col=False)
                self.box(top_key, w0, w1, sa, sb, zt - 0.05, zt, kind="detail")
                if nosing:
                    edge = sa
                    self.strip("hazard", (w0 + 0.05, edge + dir_up * 0.05, zt), (w1 - 0.05, edge + dir_up * 0.05, zt),
                               0.06, (0, 0, 1), lift=0.004)
            else:
                self.box(key, sa, sb, w0, w1, base, zt - 0.05, col=False)
                self.box(top_key, sa, sb, w0, w1, zt - 0.05, zt, kind="detail")
                if nosing:
                    edge = sa
                    self.strip("hazard", (edge + dir_up * 0.05, w0 + 0.05, zt), (edge + dir_up * 0.05, w1 - 0.05, zt),
                               0.06, (0, 0, 1), lift=0.004)
        s_top = s_low + dir_up * (n - 1) * tread
        if stringer:
            # 옆판: 경사를 따라가는 평행사변형 판 (양쪽)
            for wx, sgn in ((w0, -1), (w1, 1)):
                sa, sb = s_low - dir_up * 0.15, s_top
                pts_s = [(sa, z_low - 0.0), (sb, z_high - r - 0.0), (sb, z_high + 0.12), (sa, z_low + r + 0.12)]
                # 옆판 안쪽 면을 디딤판 끝보다 10 mm 안으로: 계단이 벽에 붙어도 벽 면·벽 데칼(0.006)과
                # 같은 평면에 놓이지 않는다
                if axis == "y":
                    p3 = [(wx - sgn * 0.01, s, z) for s, z in pts_s]
                    self._side_plate("navy", p3, (sgn, 0, 0), 0.05)
                else:
                    p3 = [(s, wx - sgn * 0.01, z) for s, z in pts_s]
                    self._side_plate("navy", p3, (0, sgn, 0), 0.05)
        return s_top

    def _side_plate(self, key, pts3d, normal, thick, kind="main"):
        b = self.bm(key, kind)
        N = Vector(normal) * thick
        f0 = [b.verts.new(Vector(p)) for p in pts3d]
        f1 = [b.verts.new(Vector(p) + N) for p in pts3d]
        n = len(pts3d)
        faces = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
        for i in range(n):
            j = (i + 1) % n
            faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
        bmesh.ops.recalc_face_normals(b, faces=faces)

    def railing(self, pts, z, *, h=0.78, post=1.1, col=True, col_h=1.15, key="steel", gate=None):
        """축 정렬 꺾은선 난간: 기둥(건메탈 + 금색 머리), 위 손잡이(은색), 중간 봉. 충돌은 얇은 박스."""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L_ = math.hypot(x1 - x0, y1 - y0)
            n = max(1, math.ceil(L_ / post))
            for i in range(n + 1):
                t = i / n
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                self.cyl("metal", (x, y, z), (x, y, z + h - 0.03), 0.022, verts=8, kind="detail")
                self.cyl("gold", (x, y, z + h - 0.05), (x, y, z + h + 0.025), 0.032, verts=8, kind="detail")
            self.cyl(key, (x0, y0, z + h), (x1, y1, z + h), 0.026, verts=8, kind="detail")
            self.cyl("metal", (x0, y0, z + h * 0.5), (x1, y1, z + h * 0.5), 0.014, verts=6, kind="detail")
            self.cyl("navy", (x0, y0, z + 0.06), (x1, y1, z + 0.06), 0.03, verts=6, kind="detail")
            if col:
                if abs(x1 - x0) > abs(y1 - y0):
                    self.col(min(x0, x1), max(x0, x1), y0 - 0.06, y0 + 0.06, z, z + col_h)
                else:
                    self.col(x0 - 0.06, x0 + 0.06, min(y0, y1), max(y0, y1), z, z + col_h)

    def portal(self, axis, c_mid, a_center, w, h, z0, depth, *, rad=0.3, border=0.15, window=False, logo=True,
               light=True, faces=(1, -1), key="metal", lip="gold", logo_size=0.26):
        """둥근 문틀/창틀. c_mid = 벽 두께 중심, depth = 벽 전체 두께(양쪽 0.06씩 더 나옴).
        문: 아래가 열린 U자 (위 모서리 둥금). 창: 닫힌 고리 (네 모서리 둥금)."""
        N = (0, 1, 0) if axis == "x" else (1, 0, 0)
        ctr = (a_center, c_mid, z0) if axis == "x" else (c_mid, a_center, z0)
        # frame(): normal=N, up=Z → right = Z x N. axis x: N=+Y → right = -X. 2D u가 -X 방향이므로 a를 뒤집는다
        # (좌우 대칭이라 상관없지만 로고·글자 방향을 위해 기록)
        # 깊이 다툼 방지: 틀 안쪽 면은 벽 개구부(w×h)보다 _PORTAL_INSET만큼 안으로 나와 벽 측면·상인방 밑면과
        # 같은 평면에 놓이지 않는다. 틀 앞면은 벽에서 _PORTAL_PROUD(걸레받이 0.06·턱 0.07·띠 0.08·기둥 0.09와
        # 다른 깊이), 금테는 그보다 1 cm 더 나온다.
        e = _PORTAL_INSET
        D = depth + 2 * _PORTAL_PROUD
        if window:
            inner = hw.rrect(w - 2 * e, h - 2 * e, rad, n=4, cy=h / 2)
            outer = hw.rrect(w + 2 * border, h + 2 * border, rad + border, n=4, cy=h / 2)
            self.ring_extrude(key, outer, inner, ctr, N, D, back=D / 2)
            li = hw.rrect(w - 2 * e + 0.01, h - 2 * e + 0.01, rad, n=4, cy=h / 2)
            lo = hw.rrect(w - 2 * e + 0.07, h - 2 * e + 0.07, rad + 0.03, n=4, cy=h / 2)
            self.ring_extrude(lip, lo, li, ctr, N, D + 0.02, back=(D + 0.02) / 2, kind="detail")
        else:
            # 다리는 바닥 속으로 (틀 1 cm, 금테 5 mm): 밑면이 벽·문짝 밑면(z0)과 같은 평면에 놓이지 않게
            c_f = Vector(ctr) - Vector((0, 0, 0.01))
            c_l = Vector(ctr) - Vector((0, 0, 0.005))
            self.extrude(key, _u_shape(w - 2 * e, h - e + 0.01, rad, border + e), tuple(c_f), N, D, back=D / 2)
            self.extrude(lip, _u_shape(w - 2 * e + 0.01, h - e + 0.01, rad, 0.035), tuple(c_l), N, D + 0.02,
                         back=(D + 0.02) / 2, kind="detail")
        top = z0 + h + (border if window else border)
        for sgn in faces:
            n_ = (0, sgn, 0) if axis == "x" else (sgn, 0, 0)
            face_c = Vector(ctr) + Vector(n_) * (D / 2)
            if light and not window:
                self.decal("glow", hw.stadium(0.34, 0.06), tuple(face_c + Vector((0, 0, h + border * 0.5))), n_,
                           lift=0.004)
            if logo and not window:
                wall_face = Vector(ctr) + Vector(n_) * (depth / 2)
                self.logo_plate(tuple(wall_face + Vector((0, 0, h + border + logo_size * 0.8))), logo_size, n_)

    def logo_plate(self, wall_pt, size, normal, *, thick=0.05, up=(0, 0, 1), disc="navy", layer=None):
        """벽에 붙은 둥근 로고 판 (남색 원판 + 금테 + 금색 엘프 로고). wall_pt = 벽 표면 위 중심."""
        r = size * 0.66
        self.extrude(disc, hw.circle(r, 24), wall_pt, normal, thick, up=up, kind="detail", layer=layer)
        fc = tuple(Vector(wall_pt) + Vector(normal).normalized() * thick)
        self.ring("gold", hw.circle(r - 0.004, 24), hw.circle(r - 0.03, 24), fc, normal, up=up, lift=0.003,
                  layer=layer)
        self.logo(fc, size * 0.82, normal, up=up, disc=None, lift=0.004, layer=layer)

    def porthole(self, axis, c_mid, a, z, r, depth, *, side=1, glass_group=None, **glass_props):
        """둥근 창 (선체 바깥 벽). 금테, 볼트 8개, 유리."""
        N = (0, 1, 0) if axis == "x" else (1, 0, 0)
        ctr = (a, c_mid, z) if axis == "x" else (c_mid, a, z)
        D = depth + 0.1
        self.ring_extrude("metal", hw.circle(r + 0.12, 20), hw.circle(r, 20), ctr, N, D, back=D / 2)
        # 금테 안쪽 면은 쇠 고리 안쪽 면보다 6 mm 안으로 (같은 원통면에 겹치지 않게)
        self.ring_extrude("gold", hw.circle(r + 0.03, 20), hw.circle(r - 0.006, 20), ctr, N, D + 0.03,
                          back=(D + 0.03) / 2, kind="detail")
        n_ = (0, side, 0) if axis == "x" else (side, 0, 0)
        fc = Vector(ctr) + Vector(n_) * (D / 2)
        for i in range(8):
            ang = 2 * math.pi * (i + 0.5) / 8
            R, U = frame(n_)
            p = fc + Vector(R) * (math.cos(ang) * (r + 0.075)) + Vector(U) * (math.sin(ang) * (r + 0.075))
            self.decal("steel", octagon(0.016), tuple(p), n_, lift=0.003)
        gc = Vector(ctr)
        if glass_group:
            with self.in_group(glass_group, mode="mesh", **glass_props):
                self.decal("glass", hw.circle(r, 20), tuple(gc), n_, lift=0.0)
        else:
            self.decal("glass", hw.circle(r, 20), tuple(gc), n_, lift=0.0)

    def sign(self, center, normal, w, h, text=None, *, size=None, key="navy", border="gold", text_key="glow",
             logo=False, up=(0, 0, 1), layer=None, sub=None, sub_key="paper", depth=0.04):
        """표지판: 남색 판(얇은 상자) + 금테 + 글자(시안 발광)."""
        R, U = frame(normal, up)
        N = Vector(normal).normalized()
        self.extrude(key, hw.rrect(w, h, min(0.06, h / 4), n=2), center, normal, depth, up=up, kind="detail",
                     layer=layer)
        fc = tuple(Vector(center) + N * depth)
        self.ring(border, hw.rrect(w - 0.02, h - 0.02, min(0.05, h / 4), n=2),
                  hw.rrect(w - 0.06, h - 0.06, min(0.04, h / 5), n=2), fc, normal, up=up, lift=0.003, layer=layer)
        if logo:
            lc = Vector(fc) - Vector(R) * (w / 2 - h / 2)
            self.logo(tuple(lc), h * 0.62, normal, up=up, disc=None, lift=0.004, layer=layer)
        if text:
            off = Vector(R) * (h * 0.3 if logo else 0.0)
            tc = Vector(fc) + off + (Vector(U) * (h * 0.13) if sub else Vector((0, 0, 0)))
            self.text(text_key, text, size or h * 0.5, tuple(tc), normal, up=up, lift=0.004, layer=layer)
            if sub:
                sc = Vector(fc) + off - Vector(U) * (h * 0.27)
                self.text(sub_key, sub, (size or h * 0.5) * 0.42, tuple(sc), normal, up=up, lift=0.004, layer=layer)

    def stars(self, center, normal, w, h, count, *, seed=1, up=(0, 0, 1), size=(0.06, 0.22)):
        """별 배경 판: 작은 마름모(UNLIT). 배경색은 레벨 sky가 맡는다."""
        rnd = random.Random(seed)
        R, U = frame(normal, up)
        R, U = Vector(R), Vector(U)
        c = Vector(center)
        for i in range(count):
            u = rnd.uniform(-w / 2, w / 2)
            v = rnd.uniform(-h / 2, h / 2)
            s = rnd.uniform(*size) * (2.2 if rnd.random() < 0.05 else 1.0)
            key = rnd.choices(["star", "star_c", "star_y"], [6, 2, 1])[0]
            # 색마다 다른 깊이 (겹친 별끼리 같은 평면에서 깜빡이지 않게)
            p = c + R * u + U * v + Vector(normal).normalized() * (0.02 * ("star", "star_c", "star_y").index(key))
            if s > 0.3:  # 큰 별은 네 갈래
                pts = []
                for k in range(8):
                    a = math.pi / 4 * k
                    rr = s if k % 2 == 0 else s * 0.22
                    pts.append(p + R * (math.cos(a) * rr) + U * (math.sin(a) * rr))
                self.poly(key, pts, normal=normal)
            else:
                self.poly(key, [p + R * s, p + U * s, p - R * s, p - U * s], normal=normal)

    def _gnode(self, name, gnodes, zone_parent):
        """그룹 빈 오브젝트 (필요하면 부모 그룹부터 만든다). pivot이 있으면 그 자리에 둔다."""
        if name in gnodes:
            return gnodes[name]
        info = self.groups.get(name, {"mode": "node", "props": {}})
        par = zone_parent
        if info.get("parent"):
            par = self._gnode(info["parent"], gnodes, zone_parent)
        e = cb.empty(name, size=0.5)
        e.parent = par
        bpy.context.view_layer.update()
        if par is not None:
            e.matrix_parent_inverse = par.matrix_world.inverted()
        if info.get("pivot"):
            e.location = info["pivot"]
            e["_pivoted"] = 1
        elif par is not None and par.get("_pivoted"):
            e["_pivoted"] = 1
        bpy.context.view_layer.update()
        for k2, v2 in info.get("props", {}).items():
            e[k2] = v2
        gnodes[name] = e
        return e

    # ================================================================ finish
    def finish(self, rel_path, *, root_props=None, outline=0.009, detail_outline=0.004, prop=False,
               extra_preview=None, preview_skip=()):
        """메시 생성 → (미리보기 처리) → glb 내보내기. 반환: 통계 dict."""
        dg = bpy.context.evaluated_depsgraph_get()
        bpy.context.view_layer.update()
        # 등록된 오브젝트를 누적 bmesh에 합친다
        dbg = []
        for (zn, layer, grp, key, kind, o) in self.objs:
            k = (zn, layer, grp, key, kind)
            b = self.acc.get(k)
            if b is None:
                b = self.acc[k] = bmesh.new()
            eo = o.evaluated_get(dg)
            me = eo.to_mesh()
            me.transform(o.matrix_world)
            if os.environ.get("LK_DEBUG"):
                me.calc_loop_triangles()
                dbg.append((len(me.loop_triangles), o.name, key))
            b.from_mesh(me)
            eo.to_mesh_clear()
        if dbg:
            agg = {}
            for n, nm, key in dbg:
                kk = nm.split(".")[0] + ":" + key
                agg[kk] = agg.get(kk, 0) + n
            print("[lk] heavy objs:", ", ".join(f"{k}={v}" for k, v in sorted(agg.items(), key=lambda kv: -kv[1])[:14]))
            print("[lk] direct bmesh:", ", ".join(f"{k[3]}/{k[4]}={len(b.faces)}f" for k, b in
                                              sorted(self.acc.items(), key=lambda kv: -len(kv[1].faces))[:10]))
        for (_, _, _, _, _, o) in self.objs:
            data = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)
        self.objs.clear()

        root = cb.empty(self.name, size=1.0)
        zroots = {}
        stats = {"tris": 0, "meshes": 0, "by_zone": {}, "by_mat": {}}
        prev = self.preview
        # 불투명 팔레트 색을 정점색(Col)으로 합친다: 구역·층·그룹·종류마다 vc(밝은 먹선)/vcd(짙은 먹선) 메시 하나
        pal_of = {}
        if self.vcol:
            merged = {}
            for (zn, layer, grp, key, kind), b in list(self.acc.items()):
                if is_glow(key) or not b.faces:
                    continue
                if grp and self.groups.get(grp, {}).get("mode") == "mesh":
                    continue
                cls = "vcd" if key in _DARK else "vc"
                T = (zn, layer, grp, cls, kind)
                big = merged.get(T)
                if big is None:
                    big = merged[T] = bmesh.new()
                    pal_of[T] = []
                tmp = bpy.data.meshes.new("tmp_vc")
                b.to_mesh(tmp)
                b.free()
                n0 = len(big.faces)
                big.from_mesh(tmp)
                bpy.data.meshes.remove(tmp)
                pal_of[T].extend([key] * (len(big.faces) - n0))
                del self.acc[(zn, layer, grp, key, kind)]
            self.acc.update(merged)
        gnodes = {}
        gcount = {}
        for (zn, layer, grp, key, kind) in self.acc:
            if grp:
                gcount[grp] = gcount.get(grp, 0) + 1
        for (zn, layer, grp, key, kind), b in sorted(self.acc.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
            if prev and (layer == "ceil" or zn in preview_skip):
                b.free()
                continue
            if not b.faces:
                b.free()
                continue
            nm = f"{zn}_{'ceil_' if layer == 'ceil' else ''}{key}{'' if kind == 'main' else '_' + kind}"
            if grp:  # 그룹 자식은 소문자 (접두사 규칙은 그룹 노드에만 걸리게)
                nm = f"{grp.lower()}__{'ceil_' if layer == 'ceil' else ''}{key}{'' if kind == 'main' else '_' + kind}"
            if prop:
                nm = f"{self.name}_{key}{'' if kind == 'main' else '_' + kind}"
            gmode = self.groups.get(grp, {}).get("mode") if grp else None
            if grp and gmode == "mesh":
                if gcount[grp] != 1:
                    raise RuntimeError(f"[lk] 그룹 {grp}(mode=mesh)에 머티리얼이 여럿: mode='node'로 바꿀 것")
                nm = grp
            me = bpy.data.meshes.new(nm)
            b.to_mesh(me)
            b.free()
            o = bpy.data.objects.new(nm, me)
            cb.link(o)
            if key in ("vc", "vcd"):
                cb.assign(o, vc_material(key == "vcd"))
                keys = pal_of[(zn, layer, grp, key, kind)]
                ca = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
                cols = {k2: (*_srgb(PAL[k2]), 1.0) for k2 in set(keys)}
                for poly in me.polygons:
                    c = cols[keys[poly.index]]
                    for li in poly.loop_indices:
                        ca.data[li].color_srgb = c
            else:
                cb.assign(o, M(key))
            o["collider"] = 0
            if kind == "fine":
                o["noOutline"] = 1
            elif kind == "detail":
                o["outline"] = detail_outline
            parent = root
            if not prop:
                if zn not in zroots:
                    zroots[zn] = cb.empty(f"zone_{zn}", parent=root, size=0.5)
                parent = zroots[zn]
            if grp:
                ginfo = self.groups.get(grp, {"mode": "node", "props": {}})
                if ginfo["mode"] == "mesh":
                    for k2, v2 in ginfo["props"].items():
                        o[k2] = v2
                    if ginfo.get("pivot"):
                        P = Vector(ginfo["pivot"])
                        me.transform(Matrix.Translation(-P))
                        o.location = P
                    if ginfo.get("parent"):
                        parent = self._gnode(ginfo["parent"], gnodes, parent)
                else:
                    parent = self._gnode(grp, gnodes, parent)
            o.parent = parent
            if parent is not None and parent.get("_pivoted"):
                o.matrix_parent_inverse = parent.matrix_world.inverted()
            me.calc_loop_triangles()
            nt = len(me.loop_triangles)
            stats["tris"] += nt
            stats["meshes"] += 1
            stats["by_zone"][zn] = stats["by_zone"].get(zn, 0) + nt
            stats["by_mat"][key] = stats["by_mat"].get(key, 0) + nt
        self.acc.clear()
        for zn, o in self.specials:
            if not prop:
                if zn not in zroots:
                    zroots[zn] = cb.empty(f"zone_{zn}", parent=root, size=0.5)
                o.parent = zroots[zn]
            else:
                o.parent = root
            o.data.calc_loop_triangles()
            stats["tris"] += len(o.data.loop_triangles)
            stats["meshes"] += 1

        # 충돌 박스
        show_col = prev == "col"
        if (self.cols or self.ocols or self.ccols) and (not prev or show_col):
            croot = cb.empty("colliders", parent=root, size=0.5)
            colm = cb.mat("COL_debug", "#ff3050", unlit=True, emission="#ff3050", alpha=0.35) if show_col else None
            made = []
            for (nm, zn, x0, x1, y0, y1, z0, z1) in self.cols:
                made.append(_box_obj(nm if not show_col else "dbg_" + nm, x0, x1, y0, y1, z0, z1))
            for (nm, x, y, z0, sx, sy, sz, yaw) in self.ocols:
                o = _box_obj(nm if not show_col else "dbg_" + nm, -sx / 2, sx / 2, -sy / 2, sy / 2, -sz / 2, sz / 2)
                o.location = (x, y, z0 + sz / 2)
                o.rotation_euler = (0.0, 0.0, math.radians(yaw))
                made.append(o)
            for (nm, verts) in self.ccols:
                b = bmesh.new()
                for v in verts:
                    b.verts.new(v)
                bmesh.ops.convex_hull(b, input=list(b.verts))
                me = bpy.data.meshes.new(nm)
                b.to_mesh(me)
                b.free()
                o = bpy.data.objects.new(nm if not show_col else "dbg_" + nm, me)
                cb.link(o)
                made.append(o)
            for o in made:
                o.parent = croot
                if colm:
                    cb.assign(o, colm)
                    o["noOutline"] = 1
        stats["cols"] = len(self.cols) + len(self.ocols) + len(self.ccols)
        # 트리거
        if self.trigs:
            troot = cb.empty("triggers", parent=root, size=0.5)
            trm = cb.mat("TRIG_debug", "#40ff90", unlit=True, emission="#40ff90", alpha=0.25) if prev else None
            for (tid, x0, x1, y0, y1, z0, z1, props) in self.trigs:
                o = _box_obj(("dbg_" if prev else "") + f"TRIG_{tid}", x0, x1, y0, y1, z0, z1)
                o.parent = troot
                for k, v in props.items():
                    o[k] = v
                if trm:
                    cb.assign(o, trm)
                    o["noOutline"] = 1
        # 마커
        if self.markers:
            mroot = cb.empty("markers", parent=root, size=0.5)
            for (nm, loc, rot, props) in self.markers:
                e = cb.empty(nm, loc=loc, parent=mroot, size=0.25)
                if rot is not None:
                    e.rotation_euler = rot
                for k, v in props.items():
                    e[k] = v
                if prev:
                    _gizmo(nm, loc, rot, props, mroot)
        stats["markers"] = len(self.markers)
        bpy.context.view_layer.update()
        for group, marker in getattr(self, "attachments", []):
            g = bpy.data.objects.get(group)
            mk = bpy.data.objects.get(marker)
            if g is None or mk is None:
                continue
            mw = g.matrix_world.copy()
            g.parent = mk
            g.matrix_parent_inverse = mk.matrix_world.inverted()
            g.matrix_world = mw
        if extra_preview and prev:
            extra_preview(root)
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        for o in bpy.context.scene.objects:
            if "_pivoted" in o.keys():
                del o["_pivoted"]
        props = {"outline": outline}
        props.update(root_props or {})
        mats = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                       for s in o.material_slots if s.material})
        stats["materials"] = len(mats)
        print(f"[lk] {self.name}: tris {stats['tris']} meshes {stats['meshes']} materials {len(mats)} "
              f"cols {stats['cols']} trigs {len(self.trigs)} markers {stats['markers']}")
        print("[lk] tris by zone:", ", ".join(f"{k}={v}" for k, v in sorted(stats["by_zone"].items())))
        top = sorted(stats["by_mat"].items(), key=lambda kv: -kv[1])[:12]
        print("[lk] tris by material:", ", ".join(f"{k}={v}" for k, v in top))
        path = cb.export(rel_path, props=props, root=root)
        stats["bytes"] = os.path.getsize(path)
        print(f"[lk] glb {stats['bytes'] / 1024:.0f} KB → {path}")
        return stats


def _copy_bm(src, dst):
    me = bpy.data.meshes.new("tmp_copy")
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)


def bm_ring(bm, outer, inner, center, normal, up=(0, 0, 1)):
    """bmesh에 평평한 고리 (special 빌드용)."""
    R, U = frame(normal, up)
    R, U, N = Vector(R), Vector(U), Vector(normal).normalized()
    c = Vector(center)
    vo = [bm.verts.new(c + R * u + U * v) for u, v in outer]
    vi = [bm.verts.new(c + R * u + U * v) for u, v in inner]
    n = len(vo)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((vo[i], vo[j], vi[j], vi[i]))
        f.normal_update()
        if f.normal.dot(N) < 0:
            f.normal_flip()


def bm_cone(bm, base, axis, r1, r2, h, segs=12):
    """bmesh에 원뿔대 (base = 아래 중심, axis = 방향)."""
    A = Vector(axis).normalized()
    q = A.to_track_quat("Z", "Y").to_matrix().to_4x4()
    Mx = Matrix.Translation(Vector(base) + A * (h / 2)) @ q
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=h,
                          matrix=Mx)


_PORTAL_INSET = 0.008   # 문틀·창틀 안쪽 면이 벽 개구부 가장자리보다 안으로 나온 거리
_PORTAL_PROUD = 0.085   # 문틀·창틀 앞면이 벽 표면보다 나온 거리 (금테는 +0.01)


def _u_shape(w, h, rad, border, n=4):
    """문틀 U자 외곽선 (아래 열림). 안쪽 폭 w·높이 h, 위 모서리 반지름 rad, 테 두께 border."""
    inner = round_top(w, h, rad, n=n)            # (w/2,0) → 위 → (-w/2,0)
    outer = round_top(w + 2 * border, h + border, rad + border, n=n)
    # 다각형: 바깥(오른쪽 아래 → 위 → 왼쪽 아래) 다음 안쪽을 거꾸로(왼쪽 아래 → 위 → 오른쪽 아래)
    return outer + list(reversed(inner))


def _box_obj(name, x0, x1, y0, y1, z0, z1):
    """축 정렬 박스 메시 오브젝트 (원점 = 중심, 정점 8개, 매끈 셰이딩으로 정점 공유)."""
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    b = bmesh.new()
    _bm_box(b, x0 - cx, x1 - cx, y0 - cy, y1 - cy, z0 - cz, z1 - cz)
    for f in b.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    o.location = (cx, cy, cz)
    cb.link(o)
    return o


# ------------------------------------------------------------------ preview gizmos (PREVIEW=1)

_GZ = {"SPAWN": "#30e070", "NPC": "#4a8cff", "TARGET": "#ff8a2a", "MARK": "#ff40d0", "CAM": "#ffe040",
       "LOOK": "#ffe040", "WP": "#ffffff", "PROP": "#c0c0c0", "SPEAKER": "#40e0ff", "EMBLEM": "#ff0000"}


def _gizmo(nm, loc, rot, props, parent):
    kind = nm.split("_")[0]
    col = _GZ.get(kind)
    if not col or kind in ("PROP", "LOOK"):
        return
    m = cb.mat(f"UNLIT_gz_{kind}", col, emission=col, unlit=True)
    R = Matrix.Identity(4)
    if rot is not None:
        R = (rot.to_matrix().to_4x4() if hasattr(rot, "to_matrix")
             else Matrix.Rotation(rot[2], 4, "Z"))
    Mw = Matrix.Translation(Vector(loc)) @ R
    b = bmesh.new()
    if kind in ("NPC", "SPAWN"):
        _bm_box(b, -0.18, 0.18, -0.12, 0.12, 0.0, 1.15 if kind == "NPC" else 0.08, matrix=Mw)
        _bm_box(b, -0.05, 0.05, -0.55, -0.12, 0.85 if kind == "NPC" else 0.0, 0.95 if kind == "NPC" else 0.08,
                matrix=Mw)  # 정면(-Y) 막대
    elif kind == "TARGET":
        _bm_box(b, -0.25, 0.25, -0.03, 0.03, 0.6, 1.3, matrix=Mw)
    elif kind == "CAM":
        _bm_box(b, -0.08, 0.08, -0.08, 0.08, -0.06, 0.06, matrix=Mw)
        _bm_box(b, -0.02, 0.02, -0.5, 0.0, -0.02, 0.02, matrix=Mw)
    else:
        _bm_box(b, -0.12, 0.12, -0.12, 0.12, 0.0, 0.24, matrix=Mw)
    me = bpy.data.meshes.new("gz_" + nm)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new("gz_" + nm, me)
    cb.link(o)
    cb.assign(o, m)
    o["noOutline"] = 1
    o.parent = parent


def import_props(root, markers_parent_name="markers"):
    """미리보기용: PROP_ 마커 자리에 소품 glb를 불러와 붙인다."""
    mroot = bpy.data.objects.get(markers_parent_name)
    if not mroot:
        return
    for e in list(mroot.children):
        model = e.get("model")
        if not e.name.startswith("PROP_") or not model:
            continue
        path = os.path.join(cb.MODELS_DIR, model)
        if not os.path.exists(path):
            continue
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=path)
        new = [o for o in bpy.data.objects if o not in before]
        tops = [o for o in new if o.parent is None or o.parent not in new]
        bpy.context.view_layer.update()
        for o in tops:
            o.parent = None
            o.matrix_world = e.matrix_world @ o.matrix_world
            o.parent = root
            o.matrix_parent_inverse = root.matrix_world.inverted()
