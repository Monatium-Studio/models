"""노획 미군 화기 세트 공용 헬퍼 (weapons_us).

cb 위에 얹는 무기 전용 도구:
  - PAL / M(): 미군 화기 팔레트 (블랙, 파커라이징 강철, 밝은 강철, 코요테, OD, 태그 종이, 모나티엄 페인트, 언릿)
  - ycyl/xcyl/zcyl/ytube: 축 방향 원기둥·관
  - side()/section(): 옆모습(YZ) 또는 단면(XZ) 외곽선 돌출
  - rail(): 피카티니 레일 (슬롯 포함, 평면 셰이딩)
  - sweep(): 단면을 경로를 따라 쓸어 만든 메시 (휜 탄창, 끈, 탄띠)
  - torus(), strip(), rrect(), text()
  - Build: 정지/세부/움직이는 파츠/앵커를 모아 join → 부모 지정 → 내보내기

좌표: 무기 원점 = 오른손 파지점, 총구 +Y, 위 +Z, 사수 오른쪽 +X (docs/art/ART_GUIDE.md 7장).
"""
from __future__ import annotations

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb

# ------------------------------------------------------------------ palette

PAL = {
    "black": "#36393f",    # 양극산화 알루미늄, 폴리머 (리시버, 레일, 조준경)
    "steel": "#5b6068",    # 파커라이징 강철 (총열, 소염기, 버퍼튜브)
    "bright": "#a9aeb5",   # 맨 강철 (핀, 나사, 노리쇠, 가늠쇠 끝)
    "coyote": "#a88b62",   # 코요테 탄 (개머리판, 탄창, 레일 커버)
    "pvd": "#8c7656",      # 코요테 PVD 코팅 강철 (M17 슬라이드) - 프레임보다 한 단 어둡게
    "od": "#5c6646",       # OD 그린 (테이프, 슬링, 탄통)
    "paper": "#e9e0c8",    # 모나티엄 창고 태그, 스티커, 흰 각인
    "paint": "#3fa79c",    # 모나티엄 창고 관리 페인트 (청록) - 진영 색 확정 시 여기만 바꾼다
    "brass": "#c9a14a",    # 탄피, 놋쇠
    "red": "#a8382e",      # 산탄 탄피, 경고 표식
    "yellow": "#d9b43c",   # 고폭 표식 띠
}
_LINES = {
    "paper": "#6b5a3e",
    "paint": "#1d4f4a",
    "brass": "#5e4519",
}


def M(key: str):
    """팔레트 머티리얼. 'reticle'은 언릿 빨강."""
    if key == "reticle":
        return cb.mat("reticle", "#ff3b2b", emission="#ff3b2b", unlit=True)
    if key == "glow":
        return cb.mat("glow", "#ffe7a0", emission="#ffe7a0", unlit=True)
    return cb.mat(key, PAL[key], line=_LINES.get(key))


# ------------------------------------------------------------------ primitives

def ycyl(name, r, y0, y1, x=0.0, z=0.0, *, verts=24, r2=None, bevel=0.0, seg=2, mat=None, cap=True):
    """Y축 원기둥. y0 쪽 반지름 r, y1 쪽 반지름 r2."""
    if y1 < y0:
        y0, y1 = y1, y0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=y1 - y0, loc=(x, (y0 + y1) / 2, z), rot=(-90, 0, 0),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=mat and M(mat), cap=cap)


def xcyl(name, r, x0, x1, y=0.0, z=0.0, *, verts=16, r2=None, bevel=0.0, seg=2, mat=None):
    if x1 < x0:
        x0, x1 = x1, x0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=x1 - x0, loc=((x0 + x1) / 2, y, z), rot=(0, 90, 0),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=mat and M(mat))


def zcyl(name, r, z0, z1, x=0.0, y=0.0, *, verts=16, r2=None, bevel=0.0, seg=2, mat=None):
    if z1 < z0:
        z0, z1 = z1, z0
        if r2 is not None:
            r, r2 = r2, r
    return cb.cylinder(name, radius=r, radius2=r2, depth=z1 - z0, loc=(x, y, (z0 + z1) / 2),
                       verts=verts, bevel=bevel, bevel_segments=seg, material=mat and M(mat))


def ytube(name, r_out, r_in, y0, y1, x=0.0, z=0.0, *, verts=24, mat=None, r_out2=None):
    """Y축 관 (안쪽 구멍 포함). 소염기, 총구, 발사관."""
    bm = bmesh.new()
    ro2 = r_out if r_out2 is None else r_out2
    rings = []
    for (r, y) in ((r_out, y0), (ro2, y1), (r_in, y1), (r_in, y0)):
        rings.append([bm.verts.new((x + r * math.cos(2 * math.pi * i / verts), y,
                                    z + r * math.sin(2 * math.pi * i / verts))) for i in range(verts)])
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((rings[a][i], rings[a][j], rings[b][j], rings[b][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    cb.smooth(obj, angle=40)
    if mat:
        cb.assign(obj, M(mat))
    return obj


def box(name, size, loc, *, rot=(0, 0, 0), bevel=0.0, seg=1, mat=None):
    return cb.box(name, size=size, loc=loc, rot=rot, bevel=bevel, bevel_segments=seg, material=mat and M(mat))


def boxr(name, x0, x1, y0, y1, z0, z1, *, bevel=0.0, seg=1, mat=None):
    """범위로 지정하는 박스."""
    return box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               bevel=bevel, seg=seg, mat=mat)


def side(name, pts, width, x=0.0, *, bevel=0.0, seg=2, mat=None):
    """옆모습 (y, z) 외곽선을 X 방향 두께 width로 돌출."""
    return cb.profile_extrude(name, pts, width, axis="X", loc=(x, 0, 0), bevel=bevel, bevel_segments=seg,
                              material=mat and M(mat))


def section(name, pts, y0, y1, *, bevel=0.0, seg=2, mat=None):
    """단면 (x, z) 외곽선을 y0..y1로 돌출."""
    return cb.profile_extrude(name, pts, y1 - y0, axis="Y", loc=(0, (y0 + y1) / 2, 0), bevel=bevel,
                              bevel_segments=seg, material=mat and M(mat))


def rrect(w, h, r, n=3, cx=0.0, cy=0.0):
    """둥근 사각형 외곽선 (반시계). r=모서리 반지름, n=모서리당 분할."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
               (w / 2 - r, -h / 2 + r, 270))
    for (ox, oy, a0) in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def strip(path, thickness, closed=False):
    """2D 폴리라인을 두께가 있는 닫힌 외곽선으로 (방아쇠울, 손잡이 고리)."""
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
    a = off(path, thickness / 2)
    b = off(path, -thickness / 2)
    return a + list(reversed(b))


def torus(name, R, r, loc=(0, 0, 0), rot=(0, 0, 0), *, seg=20, rseg=8, arc=360.0, mat=None):
    """Z축 고리. arc<360이면 열린 고리(끝 막음 없음)."""
    bm = bmesh.new()
    full = arc >= 359.9
    n = seg if full else seg + 1
    rings = []
    for i in range(n):
        a = math.radians(arc) * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
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
    obj = cb._new_mesh_obj(name, bm)
    cb._place(obj, loc, rot, (1, 1, 1))
    cb.smooth(obj, angle=180)
    if mat:
        cb.assign(obj, M(mat))
    return obj


def sweep(name, path, section_pts, *, side_vec=(1, 0, 0), cap=True, mat=None, smooth=180.0, scales=None):
    """section_pts (u, v): u = side_vec 방향, v = side_vec x 접선 방향. path: 3D 점 리스트.
    scales: 점마다 (su, sv) 배율 (선택)."""
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
        rings.append([bm.verts.new(p + s * (u * su) + N * (v * sv)) for (u, v) in section_pts])
    k = len(section_pts)
    for i in range(len(rings) - 1):
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    cb.smooth(obj, angle=smooth)
    if mat:
        cb.assign(obj, M(mat))
    return obj


def circle_pts(r, n=8, rx=None):
    rx = r if rx is None else rx
    return [(rx * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _prism(bm, sec, y0, y1, bottom=True):
    a = [bm.verts.new((x, y0, z)) for (x, z) in sec]
    b = [bm.verts.new((x, y1, z)) for (x, z) in sec]
    n = len(sec)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        if not bottom and i == 0:
            continue  # 첫 변(바닥)은 붙어 있으니 생략
        bm.faces.new((a[i], a[j], b[j], b[i]))


_UP_ROT = {"+z": 0, "+x": 90, "-z": 180, "-x": -90}


def rail(name, y0, y1, *, origin=(0.0, 0.0), up="+z", pitch=0.01, slot=0.0052, mat="black", margin=0.003,
         height=0.0095, width=0.0212):
    """피카티니 레일. origin=(x, z): 장착면 중심선, up: 레일이 솟는 방향.
    바닥 띠 + 슬롯 사이 랜드(도브테일 단면). 평면 셰이딩."""
    bm = bmesh.new()
    hw = width / 2
    base_h = height * 0.42
    base = [(-hw * 0.74, 0.0), (hw * 0.74, 0.0), (hw * 0.74, base_h), (-hw * 0.74, base_h)]
    _prism(bm, base, y0, y1)
    land = [(-hw, base_h - 0.0004), (hw, base_h - 0.0004), (hw * 0.78, height), (-hw * 0.78, height)]
    L = y1 - y0 - 2 * margin
    n = max(1, int((L + slot) // pitch))
    span = n * pitch - slot
    start = y0 + (y1 - y0 - span) / 2
    for i in range(n):
        a = start + i * pitch
        _prism(bm, land, a, a + pitch - slot, bottom=False)
    obj = cb._new_mesh_obj(name, bm)
    obj.rotation_euler = (0, math.radians(_UP_ROT[up]), 0)
    cb.apply_transform(obj)
    obj.location = (origin[0], 0, origin[1])
    if mat:
        cb.assign(obj, M(mat))
    return obj


# ------------------------------------------------------------------ text

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


def text(name, s, size, center, *, right=(1, 0, 0), up=(0, 0, 1), mat="paper", font="din", lift=0.0002,
         align="CENTER", spacing=1.0):
    """평평한 글자 메시. right/up: 글자 진행 방향과 위쪽 (월드). 법선 = right x up 쪽으로 lift만큼 띄움.
    noOutline 세부 오브젝트(Build.f)에 넣어 쓴다."""
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
    obj = bpy.data.objects.new(name, me)
    cb.link(obj)
    R = Vector(right).normalized()
    U = Vector(up).normalized()
    N = R.cross(U).normalized()
    m = Matrix((R, U, N)).transposed().to_4x4()
    m.translation = Vector(center) + N * lift
    obj.matrix_world = m
    if mat:
        cb.assign(obj, M(mat))
    return obj


# ------------------------------------------------------------------ ops

def cut(obj, cutter, op="DIFFERENCE"):
    """불리언. cutter는 Build.finish에서 지워진다."""
    m = obj.modifiers.new("Bool", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    m.use_self = True          # 겹치는 커터를 한 메시로 합쳐도 안전하게
    m.use_hole_tolerant = True
    _cutters.append(cutter)
    # 불리언 다음에 베벨이 오도록 순서 조정
    names = [mod.name for mod in obj.modifiers if mod.type == "BEVEL"]
    for nm in names:
        i = obj.modifiers.find(nm)
        obj.modifiers.move(i, len(obj.modifiers) - 1)
    cutter.display_type = "WIRE"
    return obj


_cutters: list = []


def xform(obj, *, loc=None, rot=None, pivot=(0, 0, 0)):
    """오브젝트를 pivot 기준으로 회전(deg, XYZ) 후 이동해 메시에 굽는다."""
    cb.apply_modifiers(obj)
    M4 = Matrix.Identity(4)
    if rot:
        P = Vector(pivot)
        Rm = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
              @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        M4 = Matrix.Translation(P) @ Rm @ Matrix.Translation(-P)
    if loc:
        M4 = Matrix.Translation(Vector(loc)) @ M4
    obj.matrix_world = M4 @ obj.matrix_world
    return obj


def mirror_copy(obj, name=None):
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


def set_origin(obj, world_pt):
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    local = mw.inverted() @ Vector(world_pt)
    obj.data.transform(Matrix.Translation(-local))
    obj.matrix_world = mw @ Matrix.Translation(local)


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.matrix_world = mw


def _join(objs, name):
    objs = [o for o in objs if o is not None]
    if not objs:
        return None
    if len(objs) == 1:
        o = objs[0]
        cb.apply_modifiers(o)
        o.name = name
        o.data.name = name
        return o
    return cb.join(objs, name)


def _tris(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


class Build:
    """무기 한 자루 조립기.

    s(obj)            정지 파츠 (아웃라인 O) → body
    f(obj)            정지 세부 (아웃라인 X: 각인, 핀, 스티커) → body_fine
    p(part, obj)      움직이는 파츠 → <part>
    pf(part, obj)     움직이는 파츠의 세부 (아웃라인 X) → <part>_fine (part의 자식)
    pivot(part, pt, **props)  파츠 원점(회전축/기준점)과 커스텀 속성
    anchor(name, pt)  앵커 empty
    sub(part, parent) 파츠 부모 지정 (기본: 루트)
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
        _cutters.clear()

    def s(self, *objs):
        self.static.extend(objs)
        return objs[0]

    def f(self, *objs):
        self.fine.extend(objs)
        return objs[0]

    def p(self, part, *objs):
        self.parts.setdefault(part, []).extend(objs)
        return objs[0]

    def pf(self, part, *objs):
        self.pfine.setdefault(part, []).extend(objs)
        return objs[0]

    def pivot(self, part, pt, rest_rot=None, **props):
        """rest_rot: (x, y, z)도. 메시에 굽지 않고 오브젝트 회전으로 남긴다 → 엔진에서 회전을 0으로 두면 기본(닫힘) 상태."""
        self.pivots[part] = tuple(pt)
        self.pprops.setdefault(part, {}).update(props)
        if rest_rot:
            self.rest_rots[part] = rest_rot

    def sub(self, part, parent):
        self.parents[part] = parent

    def anchor(self, name, pt, parent=None):
        """parent: 움직이는 파츠 이름이면 그 파츠를 따라 움직인다 (예: 펌프 위 grip_support)."""
        self.anchors.append((name, tuple(pt), parent))

    def finish(self, rel_path, *, outline, fp, extra=None):
        if os.environ.get("US_DEBUG"):
            dg = bpy.context.evaluated_depsgraph_get()
            rows = []
            for o in bpy.context.scene.objects:
                if o.type != "MESH" or o in _cutters:
                    continue
                me = o.evaluated_get(dg).to_mesh()
                me.calc_loop_triangles()
                rows.append((len(me.loop_triangles), o.name))
                o.evaluated_get(dg).to_mesh_clear()
            rows.sort(reverse=True)
            print("[us] heavy:", ", ".join(f"{n}={t}" for t, n in rows[:30]))
        root = cb.empty(self.name, size=0.1)
        report = {}
        body = _join(self.static, "body")
        parent_keep(body, root)
        report["body"] = _tris(body)
        fine = _join(self.fine, "body_fine")
        if fine:
            fine["noOutline"] = 1
            parent_keep(fine, root)
            report["body_fine"] = _tris(fine)
        made = {}
        for part, objs in self.parts.items():
            o = _join(objs, part)
            set_origin(o, self.pivots.get(part, (0, 0, 0)))
            for k, v in self.pprops.get(part, {}).items():
                o[k] = v
            if part in self.rest_rots:
                o.rotation_euler = [math.radians(a) for a in self.rest_rots[part]]
            made[part] = o
            report[part] = _tris(o)
        for part, o in made.items():
            parent_keep(o, made[self.parents[part]] if part in self.parents else root)
        for part, objs in self.pfine.items():
            o = _join(objs, part + "_fine")
            o["noOutline"] = 1
            parent_keep(o, made[part])
            report[part + "_fine"] = _tris(o)
        for name, pt, par in self.anchors:
            e = cb.empty(name, loc=pt, size=0.02)
            parent_keep(e, made[par] if par else root)
        for c in _cutters:
            if c.name in bpy.data.objects:
                bpy.data.objects.remove(c, do_unlink=True)
        _cutters.clear()
        props = {"outline": outline, "fpOffset": fp}
        if extra:
            props.update(extra)
        print("[us] part tris:", ", ".join(f"{k}={v}" for k, v in report.items()))
        print("[us] materials:", sorted(m.name for m in bpy.data.materials if m.users))
        return cb.export(rel_path, props=props, root=root)
