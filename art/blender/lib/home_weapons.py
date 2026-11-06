"""교주 차원 제식 병기 공용 헬퍼 (home_weapons).

엘피니아 군(지구 침공 당시 정규군)과 그 후신인 모나티엄 진압반의 제식 병기를 만든다.
무기 목록과 수치: docs/art/weapons-home.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, home_weapons as hw
    cb.reset()
    g = hw.Gun("elfinia_rifle")
    g.s(hw.side("shell", pts, 0.034, bevel=0.004, mat="olive"))       # 정지 파츠 (아웃라인 O)
    g.f(hw.text("mk", "7식", 0.008, (-0.018, 0, 0.05), **hw.LEFT, mat="gold"))  # 세부 (아웃라인 X)
    g.p("mag", obj); g.pivot("mag", (0, -0.07, 0.02), move=hw.mv(0, 0, -0.15))
    g.logo((-0.0175, 0.05, 0.06), 0.026, **hw.LEFT)                    # 원작 엘프 로고 (없으면 emblem_slot)
    g.anchor("muzzle", (0, 0.36, 0.072))
    g.finish("weapons/elfinia/elfinia_rifle.glb", outline=0.002, fp="0.15,-0.17,-0.36", fprot="0,6,0")

형태 문법 (원작 엘프 화기에서 가져온 것, 문서 2장)
  - 둥근 판: 옆모습 돌출 + 큰 베벨(3단). R41의 45° 모따기와 반대로 모서리를 둥글린다
  - 스타디움 창(긴 원형 구멍)과 둥근 구멍 줄
  - 총구의 금색 고리, 손 전체를 감싸는 D자 손잡이 고리
  - 짧은 개머리(엘프 팔 길이), 시안 표시창(엘피니아 발광)

좌표: 무기 원점 = 오른손 파지점, 총구 +Y, 위 +Z, 사수 오른쪽 +X (docs/art/ART_GUIDE.md 7장).
움직이는 파츠의 move/rotAxis/rotDeg는 three.js 부모 공간 기준이다 (mv()가 Blender 변위를 바꿔 준다).
"""
from __future__ import annotations

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb

# ------------------------------------------------------------------ palette
# 원작 진압반 시각 언어(docs/art/reference-notes.md 6장)와 리타 특수작전부 복장(monatium_sop.PAL)에서 가져온 값.
PAL = {
    # 공통 (교주 차원)
    "metal": "#5d555d",     # 자줏빛 건메탈: 리시버, 슬라이드, 하우징
    "gear": "#7b737a",      # 밝은 장비 회색: 덮개, 레일, 조준기 몸통
    "dark": "#3a333b",      # 어두운 폴리머: 탄창, 총열, 손잡이
    "rubber": "#2a252b",    # 고무: 손잡이 링, 개머리 패드
    "steel": "#cfcac4",     # 은색 금속: 핀, 노리쇠, 전극 (진압반 일반 금속)
    "gold": "#d6b25e",      # 금색 포인트: 총구 고리, 엘프 로고 (계급장 금색과 같음)
    # 엘피니아 정규군 (지구 침공 당시)
    "olive": "#8d988c",     # 회녹 폴리머 (엘피니아 전투복 #7f8a80~#a3ada1 사이)
    "olive_d": "#6f7a70",   # 회녹 그림자 (덮개, 손잡이 판)
    "navy": "#2f3644",      # 엘피니아 남색 (계급장 바탕): 로고 판
    # 모나티엄 진압반
    "violet": "#706478",    # 남보라 (진압반 지휘색): 외장
    "violet_d": "#56445b",  # 남보라 그림자: 손잡이, 펌프
    "teal": "#3f9a94",      # 비살상 표식: 고무탄 띠 (리타 스카프·창고 페인트와 같은 계열)
    "hazard": "#e8c34a",    # 경고 노랑: 전기·가스 경고 (교주 측 노랑, R41은 쓰지 않음)
    "paper": "#e9e0c8",     # 흰 스텐실 글자
    "lens": "#26303a",      # 꺼진 렌즈, 화면 바탕
    # 발광 (UNLIT)
    "glow": "#7ff0ea",      # 시안: 엘피니아·모나티엄 장비 발광 (R41 마젠타와 대비)
    "glow_warm": "#ffe7a6", # 손전등 렌즈
}
GLOW_KEYS = ("glow", "glow_warm")

# 먹선: 원작처럼 붉은 갈색 한 가지. 아주 어두운 재질만 더 짙은 갈색으로 (밝은 테처럼 보이지 않게)
LINE = "#4a2229"
LINE_DARK = "#24100f"
_DARK = {"dark", "rubber", "navy", "lens", "violet_d", "metal"}


def M(key: str):
    """팔레트 머티리얼 (이름 hw_<key>). 'glow*'는 UNLIT."""
    if key in GLOW_KEYS:
        return cb.mat(f"hw_{key}", PAL[key], emission=PAL[key], unlit=True)
    return cb.mat(f"hw_{key}", PAL[key], line=LINE_DARK if key in _DARK else LINE, roughness=0.55)


def _m(mat):
    if mat is None:
        return None
    return M(mat) if isinstance(mat, str) else mat


def mv(dx: float, dy: float, dz: float) -> str:
    """Blender 변위 → three.js 부모 공간 move 문자열 (x, z, -y)."""
    def f(v):
        v = round(v + 0.0, 4)
        return f"{v:g}"
    return f"{f(dx)},{f(dz)},{f(-dy)}"


# 데칼·글자 방향 프리셋 (right, up). 법선 = right x up
LEFT = dict(right=(0, -1, 0), up=(0, 0, 1))     # -X 면 (1인칭에서 보이는 면)
RIGHT = dict(right=(0, 1, 0), up=(0, 0, 1))     # +X 면
TOP = dict(right=(1, 0, 0), up=(0, 1, 0))       # +Z 면 (뒤에서 읽음)
BACK = dict(right=(1, 0, 0), up=(0, 0, 1))      # -Y 면 (사수 쪽)
FRONT = dict(right=(-1, 0, 0), up=(0, 0, 1))    # +Y 면


# ------------------------------------------------------------------ 2D outlines

def rrect(w, h, r, n=3, cx=0.0, cy=0.0):
    """둥근 사각형 외곽선 (반시계). r=모서리 반지름, n=모서리당 분할."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    for (ox, oy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                         (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def stadium(length, width, n=6, cx=0.0, cy=0.0, angle=0.0):
    """스타디움(긴 원형) 외곽선. length = 전체 길이(u), width = 폭(v), angle = 회전(도)."""
    r = width / 2
    a = max(length / 2 - r, 0.0)
    pts = []
    for i in range(n + 1):
        t = -math.pi / 2 + math.pi * i / n
        pts.append((a + r * math.cos(t), r * math.sin(t)))
    for i in range(n + 1):
        t = math.pi / 2 + math.pi * i / n
        pts.append((-a + r * math.cos(t), r * math.sin(t)))
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return [(cx + u * c - v * s, cy + u * s + v * c) for u, v in pts]


def circle(r, n=12, cx=0.0, cy=0.0, rx=None):
    rx = r if rx is None else rx
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def arc_pts(cx, cy, r, a0, a1, n):
    """원호 위의 점 (a0→a1 도, 끝점 포함)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def strip(path, thickness):
    """2D 폴리라인을 두께 있는 닫힌 외곽선으로 (방아쇠울, D자 고리)."""
    def off(pts, d):
        out = []
        n = len(pts)
        for i, p in enumerate(pts):
            a = Vector(pts[i - 1] if i > 0 else pts[0])
            b = Vector(pts[i + 1] if i < n - 1 else pts[-1])
            t = (b - a).normalized()
            nrm = Vector((-t.y, t.x))
            out.append((p[0] + nrm.x * d, p[1] + nrm.y * d))
        return out
    return off(path, thickness / 2) + list(reversed(off(path, -thickness / 2)))


# ------------------------------------------------------------------ primitives

def side(name, pts, width, x=0.0, *, bevel=0.0, seg=3, mat=None, angle=40.0):
    """옆모습 (y, z) 외곽선을 X 두께 width로 돌출. bevel은 둥근 모서리(seg 단)."""
    o = cb.profile_extrude(name, pts, width, axis="X", loc=(x, 0, 0), material=_m(mat))
    if bevel > 0:
        cb.add_bevel(o, bevel, seg, angle=angle)
    else:
        cb.smooth(o, angle=35)
    return o


def section(name, pts, y0, y1, *, bevel=0.0, seg=3, mat=None, angle=40.0):
    """단면 (x, z) 외곽선을 y0..y1로 돌출."""
    o = cb.profile_extrude(name, pts, y1 - y0, axis="Y", loc=(0, (y0 + y1) / 2, 0), material=_m(mat))
    if bevel > 0:
        cb.add_bevel(o, bevel, seg, angle=angle)
    else:
        cb.smooth(o, angle=35)
    return o


def sculpt(name, side_pts, sec_pts, *, x_center=0.0, bevel=0.0, seg=3, mat=None):
    """옆모습(y,z) ∩ 단면(x,z) 불리언 교집합. 둥근 단면(rrect)을 주면 둥근 몸통이 된다."""
    ys = [p[0] for p in side_pts]
    xs = [p[0] for p in sec_pts]
    y0, y1 = min(ys) - 0.01, max(ys) + 0.01
    a = cb.profile_extrude(name, side_pts, (max(xs) - min(xs)) + 0.02, axis="X", loc=(x_center, 0, 0))
    b = cb.profile_extrude(name + "_isect", sec_pts, y1 - y0, axis="Y", loc=(x_center, (y0 + y1) / 2, 0))
    m = a.modifiers.new("Isect", "BOOLEAN")
    m.operation = "INTERSECT"
    m.object = b
    m.solver = "EXACT"
    cb.apply_modifiers(a)
    bpy.data.objects.remove(b, do_unlink=True)
    _clean(a)
    if bevel > 0:
        cb.add_bevel(a, bevel, seg, angle=35)
    else:
        cb.smooth(a, angle=35)
    if mat:
        cb.assign(a, _m(mat))
    return a


def _clean(obj, dist=1e-5):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def box(name, size, loc, *, rot=(0, 0, 0), bevel=0.0, seg=2, mat=None):
    return cb.box(name, size=size, loc=loc, rot=rot, bevel=bevel, bevel_segments=seg, material=_m(mat))


def boxr(name, x0, x1, y0, y1, z0, z1, *, bevel=0.0, seg=2, mat=None):
    return box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               bevel=bevel, seg=seg, mat=mat)


def ycyl(name, r, y0, y1, x=0.0, z=0.0, *, verts=24, r2=None, bevel=0.0, seg=2, mat=None, cap=True):
    """Y축 원기둥. y0 쪽 반지름 r, y1 쪽 반지름 r2."""
    if y1 < y0:
        y0, y1 = y1, y0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=y1 - y0, loc=(x, (y0 + y1) / 2, z), rot=(-90, 0, 0),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=_m(mat), cap=cap)


def xcyl(name, r, x0, x1, y=0.0, z=0.0, *, verts=16, r2=None, bevel=0.0, seg=2, mat=None):
    if x1 < x0:
        x0, x1 = x1, x0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=x1 - x0, loc=((x0 + x1) / 2, y, z), rot=(0, 90, 0),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=_m(mat))


def zcyl(name, r, z0, z1, x=0.0, y=0.0, *, verts=16, r2=None, bevel=0.0, seg=2, mat=None):
    if z1 < z0:
        z0, z1 = z1, z0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=z1 - z0, loc=(x, y, (z0 + z1) / 2),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=_m(mat))


def tube(name, r_out, r_in, a0, a1, *, axis="Y", c=(0.0, 0.0), verts=24, r_out2=None, r_in2=None, mat=None,
         smooth=40.0):
    """속이 빈 관 (총구, 링, 조준경 몸통). axis 방향으로 a0..a1, c = 나머지 두 축의 중심.
    axis='Y': c=(x, z), 'X': c=(y, z), 'Z': c=(x, y)."""
    bm = bmesh.new()
    ro2 = r_out if r_out2 is None else r_out2
    ri2 = r_in if r_in2 is None else r_in2

    def P(r, t, a):
        u, v = r * math.cos(a), r * math.sin(a)
        if axis == "Y":
            return (c[0] + u, t, c[1] + v)
        if axis == "X":
            return (t, c[0] + u, c[1] + v)
        return (c[0] + u, c[1] + v, t)

    rings = []
    for (r, t) in ((r_out, a0), (ro2, a1), (ri2, a1), (r_in, a0)):
        rings.append([bm.verts.new(P(r, t, 2 * math.pi * i / verts)) for i in range(verts)])
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((rings[a][i], rings[a][j], rings[b][j], rings[b][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=smooth)
    if mat:
        cb.assign(o, _m(mat))
    return o


def torus(name, R, r, loc=(0, 0, 0), rot=(0, 0, 0), *, seg=20, rseg=8, arc=360.0, mat=None, ry=None):
    """Z축 고리. arc<360이면 열린 고리. ry를 주면 타원 고리(Y 반지름)."""
    bm = bmesh.new()
    full = arc >= 359.9
    n = seg if full else seg + 1
    ry = R if ry is None else ry
    rings = []
    for i in range(n):
        a = math.radians(arc) * i / seg
        ring = []
        ca, sa = math.cos(a), math.sin(a)
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            ring.append(bm.verts.new(((R + r * math.cos(b)) * ca, (ry + r * math.cos(b)) * sa, r * math.sin(b))))
        rings.append(ring)
    for i in range(seg):
        i2 = (i + 1) % n if full else i + 1
        for j in range(rseg):
            j2 = (j + 1) % rseg
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))
    if not full:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb._place(o, loc, rot, (1, 1, 1))
    cb.smooth(o, angle=180)
    if mat:
        cb.assign(o, _m(mat))
    return o


def sweep(name, path, sec, *, side_vec=(1, 0, 0), cap=True, mat=None, smooth=180.0, scales=None):
    """단면 sec (u, v)를 3D 경로를 따라 쓸기. u = side_vec 방향, v = side x 접선."""
    bm = bmesh.new()
    S = Vector(side_vec).normalized()
    P = [Vector(p) for p in path]
    rings = []
    for i, p in enumerate(P):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, len(P) - 1)]
        T = (b - a).normalized()
        s = (S - T * S.dot(T)).normalized()
        N = s.cross(T).normalized()
        su, sv = scales[i] if scales else (1.0, 1.0)
        rings.append([bm.verts.new(p + s * (u * su) + N * (v * sv)) for (u, v) in sec])
    k = len(sec)
    for i in range(len(rings) - 1):
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=smooth)
    if mat:
        cb.assign(o, _m(mat))
    return o


def xform(obj, *, loc=None, rot=None, pivot=(0, 0, 0)):
    """pivot 기준 회전(도, XYZ) 뒤 이동을 메시에 굽는다."""
    cb.apply_modifiers(obj)
    M4 = Matrix.Identity(4)
    if rot:
        P = Vector(pivot)
        R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
             @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        M4 = Matrix.Translation(P) @ R @ Matrix.Translation(-P)
    if loc:
        M4 = Matrix.Translation(Vector(loc)) @ M4
    obj.matrix_world = M4 @ obj.matrix_world
    return obj


def mirror_x(obj, name=None):
    """X 대칭 복사본 (모디파이어 적용 후)."""
    cb.apply_modifiers(obj)
    me = obj.data.copy()
    me.transform(obj.matrix_world)
    me.transform(Matrix.Scale(-1, 4, Vector((1, 0, 0))))
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o2 = bpy.data.objects.new(name or obj.name + "_m", me)
    cb.link(o2)
    return o2


# ------------------------------------------------------------------ boolean

_cutters: list = []


def cut(obj, cutter, op="DIFFERENCE"):
    """불리언 (커터는 Gun.finish에서 지워진다). 베벨은 불리언 뒤로 옮겨 잘린 모서리도 둥글게."""
    m = obj.modifiers.new("Bool", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    m.use_self = True
    m.use_hole_tolerant = True
    _cutters.append(cutter)
    for nm in [mod.name for mod in obj.modifiers if mod.type == "BEVEL"]:
        obj.modifiers.move(obj.modifiers.find(nm), len(obj.modifiers) - 1)
    cutter.display_type = "WIRE"
    cutter.hide_render = True
    return obj


def slot_cutter(name, pts_uv, center, *, axis="X", depth=0.03):
    """2D 외곽선(u, v)을 axis 방향으로 관통하는 커터. axis='X': u=Y, v=Z. 'Z': u=X, v=Y. 'Y': u=X, v=Z."""
    ax = {"X": "X", "Z": "Z", "Y": "Y"}[axis]
    o = cb.profile_extrude(name, pts_uv, depth, axis=ax, loc=center)
    return o


# ------------------------------------------------------------------ decals · text

def _frame(right, up):
    R = Vector(right).normalized()
    U = Vector(up).normalized()
    return R, U, R.cross(U).normalized()


def decal(name, pts, center, *, right, up, lift=0.0005, mat=None):
    """한 면짜리 다각형 데칼. pts (u, v) = right/up 방향 좌표. 이름은 decal_로 시작하게 만든다."""
    R, U, N = _frame(right, up)
    c = Vector(center) + N * lift
    verts = [c + R * u + U * v for u, v in pts]
    nm = name if name.startswith("decal_") else "decal_" + name
    o = cb.from_pydata(nm, verts, [list(range(len(pts)))], material=_m(mat))
    _face_out(o, N)
    return o


def ring_decal(name, center, r_out, r_in, *, right, up, lift=0.0005, mat=None, seg=20):
    R, U, N = _frame(right, up)
    c = Vector(center) + N * lift
    verts = []
    for r in (r_out, r_in):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append(c + R * (r * math.cos(a)) + U * (r * math.sin(a)))
    faces = [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)]
    o = cb.from_pydata("decal_" + name, verts, faces, material=_m(mat))
    _face_out(o, N)
    return o


def _face_out(o, out):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    flip = [f for f in bm.faces if f.normal.dot(out) < 0]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False


def holes(prefix, center, count, pitch, r, *, right, up, along=(1, 0), lift=0.0005, mat="dark", n=10):
    """둥근 구멍 줄 (어두운 원 데칼). along = (u, v) 방향 단위. 원작 엘프 화기의 '구멍 줄' 문법."""
    out = []
    du, dv = along
    for i in range(count):
        k = i - (count - 1) / 2
        out.append(decal(f"{prefix}{i}", circle(r, n, k * pitch * du, k * pitch * dv), center,
                         right=right, up=up, lift=lift, mat=mat))
    return out


_FONTS = {
    "din": "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
    "kr": "/System/Library/Fonts/AppleSDGothicNeo.ttc",
}
_font_cache: dict = {}


def _font(key):
    if key in _font_cache:
        return _font_cache[key]
    path = _FONTS.get(key)
    f = None
    if path and os.path.exists(path):
        try:
            f = bpy.data.fonts.load(path, check_existing=True)
        except Exception:
            f = None
    _font_cache[key] = f
    return f


def text(name, s, size, center, *, right, up, mat="paper", font=None, lift=0.0004, align="CENTER", spacing=1.0):
    """평평한 글자 메시 (세부 데칼). 한글이 있으면 기본 글꼴이 AppleSDGothicNeo."""
    if font is None:
        font = "kr" if any(ord(ch) > 0x2000 for ch in s) else "din"
    cu = bpy.data.curves.new(name + "_crv", "FONT")
    cu.body = s
    f = _font(font)
    if f:
        cu.font = f
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.resolution_u = 1
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
    R, U, N = _frame(right, up)
    m4 = Matrix((R, U, N)).transposed().to_4x4()
    m4.translation = Vector(center) + N * lift
    o.matrix_world = m4
    if mat:
        cb.assign(o, _m(mat))
    return o


# ------------------------------------------------------------------ 엘프 로고 (원작 엘프 종족 로고)
# ART_GUIDE 1장 '엘프 로고 예외'. 원본: public/ui/elf_logo_mono.svg. SVG 파싱은 r41.elf_logo_outline을 재사용한다.
ELF_LOGO_SVG = os.path.join(cb.ROOT, "public", "ui", "elf_logo_mono.svg")


def elf_logo_available() -> bool:
    return os.path.exists(ELF_LOGO_SVG)


def elf_logo(name, center, size, *, right, up, mat="gold", lift=0.0006, tolerance=0.0035):
    """원작 엘프 로고 데칼 (높이 size m). SVG가 없으면 None."""
    if not elf_logo_available():
        return None
    import r41  # 수정하지 않고 외곽선 파서만 빌려 쓴다
    pts = [(u * size, v * size) for u, v in r41.elf_logo_outline(tolerance)]
    return decal(name, pts, center, right=right, up=up, lift=lift, mat=mat)


# ------------------------------------------------------------------ family parts (엘프 화기 문법)

def muzzle_ring(name, y0, y1, r, *, x=0.0, z=0.0, mat="gold", verts=24, flare=0.0):
    """금색 총구 고리 (칸나 발사기의 금색 총구 테). flare>0이면 앞으로 벌어진다."""
    return ycyl(name, r, y0, y1, x=x, z=z, r2=r + flare, verts=verts, bevel=min(0.0012, (y1 - y0) * 0.3), seg=2,
                mat=mat)


def d_loop(name, y_back, y_front, z_top, z_bottom, *, thick=0.008, width=0.012, r=0.012, mat="olive", bevel=0.002):
    """손 전체를 감싸는 D자 손잡이 고리 (옆모습). 뒤 기둥은 없이 앞·아래만 둘러 손잡이에 붙는다.
    y_back: 손잡이 아래 끝(뒤쪽 붙는 점), y_front: 앞 기둥, z_top: 위(몸통에 붙는 높이), z_bottom: 아래 테."""
    path = [(y_back, z_bottom)]
    path += arc_pts(y_front - r, z_bottom + r, r, 270, 360, 4)
    path += [(y_front, z_top)]
    return side(name, strip(path, thick), width, bevel=bevel, seg=2, mat=mat)


# ------------------------------------------------------------------ assembly

def _join(objs, name):
    objs = [o for o in objs if o is not None]
    if not objs:
        return None
    for o in objs:
        cb.apply_modifiers(o)
    if len(objs) == 1:
        o = objs[0]
        o.name = name
        o.data.name = name
        return o
    return cb.join(objs, name)


def _set_origin(obj, world_pt):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    local = mw.inverted() @ Vector(world_pt)
    obj.data.transform(Matrix.Translation(-local))
    obj.matrix_world = mw @ Matrix.Translation(local)


def _parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.matrix_world = mw


def _tris(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


class Gun:
    """무기 한 자루 조립기.

    s(obj)            정지 파츠 (아웃라인 O) → body
    f(obj)            정지 세부 (아웃라인 X: 데칼, 글자, 핀) → body_fine
    p(part, obj)      움직이는 파츠 → <part>
    pf(part, obj)     움직이는 파츠의 세부 (아웃라인 X) → <part>_fine (part의 자식)
    pivot(part, pt, **props)  파츠 원점(회전축/기준점)과 커스텀 속성(move, rotAxis, rotDeg ...)
    sub(part, parent) 파츠 부모 지정 (기본: 루트)
    anchor(name, pt, parent=None)
    logo(center, size, right, up, mat, part=None)  원작 엘프 로고. SVG가 없으면 emblem_slot 빈 오브젝트
    """

    def __init__(self, name):
        self.name = name
        self.static, self.fine = [], []
        self.parts: dict[str, list] = {}
        self.pfine: dict[str, list] = {}
        self.pivots: dict[str, tuple] = {}
        self.pprops: dict[str, dict] = {}
        self.parents: dict[str, str] = {}
        self.anchors: list[tuple] = []
        self.rest_rots: dict[str, tuple] = {}
        self.slots: list[tuple] = []
        _cutters.clear()

    def s(self, *objs):
        self.static.extend(objs)
        return objs[0]

    def f(self, *objs):
        self.fine.extend(o for o in objs if o is not None)
        return objs[0]

    def p(self, part, *objs):
        self.parts.setdefault(part, []).extend(objs)
        return objs[0]

    def pf(self, part, *objs):
        self.pfine.setdefault(part, []).extend(o for o in objs if o is not None)
        return objs[0]

    def pivot(self, part, pt, rest_rot=None, **props):
        self.pivots[part] = tuple(pt)
        self.pprops.setdefault(part, {}).update(props)
        if rest_rot:
            self.rest_rots[part] = rest_rot

    def sub(self, part, parent):
        self.parents[part] = parent

    def anchor(self, name, pt, parent=None):
        self.anchors.append((name, tuple(pt), parent))

    def logo(self, center, size, *, right, up, mat="gold", part=None, name="elf_logo", lift=0.0011):
        """lift: 바탕 원판(0.0005) 위로 띄우는 높이. 원판과 겹치면 깜빡이므로 0.0005 이상 차이를 둔다."""
        o = elf_logo(name, center, size, right=right, up=up, mat=mat, lift=lift)
        if o is None:
            print(f"[hw] {ELF_LOGO_SVG} 없음 → emblem_slot 빈 오브젝트")
            self.slots.append((center, size, part))
            return None
        if part:
            self.pf(part, o)
        else:
            self.f(o)
        return o

    def finish(self, rel_path, *, outline, fp, fprot=None, extra=None, budget=12000, max_mats=8):
        root = cb.empty(self.name, size=0.1)
        report = {}
        body = _join(self.static, "body")
        _parent_keep(body, root)
        report["body"] = _tris(body)
        fine = _join(self.fine, "body_fine")
        if fine:
            fine["noOutline"] = 1
            _parent_keep(fine, root)
            report["body_fine"] = _tris(fine)
        made = {}
        for part, objs in self.parts.items():
            o = _join(objs, part)
            _set_origin(o, self.pivots.get(part, (0, 0, 0)))
            for k, v in self.pprops.get(part, {}).items():
                o[k] = v
            if part in self.rest_rots:
                o.rotation_euler = [math.radians(a) for a in self.rest_rots[part]]
            made[part] = o
            report[part] = _tris(o)
        for part, o in made.items():
            _parent_keep(o, made[self.parents[part]] if part in self.parents else root)
        for part, objs in self.pfine.items():
            o = _join(objs, part + "_fine")
            o["noOutline"] = 1
            _parent_keep(o, made[part])
            report[part + "_fine"] = _tris(o)
        for name, pt, par in self.anchors:
            e = cb.empty(name, loc=pt, size=0.02)
            _parent_keep(e, made[par] if par else root)
        for i, (c, size, par) in enumerate(self.slots):
            e = cb.empty("emblem_slot" if i == 0 else f"emblem_slot_{i}", loc=c, size=size / 2)
            e["emblemSize"] = size
            _parent_keep(e, made[par] if par else root)
        for c in _cutters:
            if c.name in bpy.data.objects:
                bpy.data.objects.remove(c, do_unlink=True)
        _cutters.clear()
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        props = {"outline": outline, "fpOffset": fp}
        if fprot:
            props["fpRot"] = fprot
        if extra:
            props.update(extra)
        total = sum(report.values())
        mats_used = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                            for s in o.material_slots if s.material})
        print("[hw] part tris:", ", ".join(f"{k}={v}" for k, v in report.items()))
        print(f"[hw] total tris {total} / {budget}, materials {len(mats_used)} / {max_mats}: {', '.join(mats_used)}")
        if total > budget or len(mats_used) > max_mats:
            raise RuntimeError(f"[hw] 예산 초과: tris {total}/{budget}, materials {len(mats_used)}/{max_mats}")
        return cb.export(rel_path, props=props, root=root)
