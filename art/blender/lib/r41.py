"""R41 모나티엄 제국군 공용 헬퍼 (r41).

시각 언어 문서: docs/art/r41-style.md
무기·드론 목록: docs/art/weapons-r41.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, r41
    cb.reset()
    M = r41.mats()                      # R41 팔레트 머티리얼
    body = r41.faceted("body", side_pts, front_pts, ...)
    ...
    r41.finish("r41_carbine", "weapons/r41/r41_carbine.glb",
               moving={"mag": [mag, mag_glow]}, anchors={"muzzle": (0, 0.33, 0.07)},
               props={"outline": 0.002, "fpOffset": "0.1,-0.12,-0.3"})

규칙 (cb와 동일)
  - 무기: 원점 = 오른손 파지점, 총구 +Y, 사수 오른쪽 = +X, 위 = +Z
  - 드론: 정면 -Y (캐릭터와 같음), 가장 낮은 점 z=0
  - 이름에 점(.) 금지. 데칼 오브젝트는 이름을 'decal_'로 시작 → 합쳐서 noOutline=1
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb

# ------------------------------------------------------------------ palette
# 값은 docs/art/r41-style.md 의 표와 같다. 바꾸면 문서도 같이 바꾼다.
PAL = {
    # 장비 · 병기
    "shell": "#2a2733",      # 제국 흑 (광택 셸): 차가운 보라빛 검정
    "metal": "#4d4959",      # 건메탈 바이올렛: 총열, 레일, 기계부
    "light": "#cbc8d1",      # R41 라이트 그레이: 총기 몸통·핸드가드, 헬멧 (PV 3:00~3:03 소총)
    "ceramic": "#ddd9e6",    # 본 화이트: 세라믹 장갑판, 데칼, 지휘관 코트
    "polymer": "#67617a",    # 슬레이트 라벤더: 손잡이, 하부 프레임, 군복 기본
    "steel": "#aab0bd",      # 냉간 강철: 전극, 노출 금속, 스프링
    "amber": "#f09a3e",      # R41 앰버: 총기 줄무늬·띠, 어깨 휘장, 위험 표시 (PV 3:01~3:03)
    "rubber": "#1c1a22",     # 고무 · 패드
    # 발광 (UNLIT)
    "glow": "#ff4fd8",       # 시그널 마젠타: 에너지 · 상태등 (R41의 서명색)
    "glow_dim": "#a070ff",   # 딥 바이올렛: 렌즈, 대기 상태, 2차 발광
    "glow_amber": "#ffb259", # 경고 발광 (과충전, 장전 표시)
    # 군복 (병사 모델용 참고값, PV 3:01~3:03 / 4:59~5:07)
    "uniform": "#9e9aa1",        # 회갈색이 섞인 밝은 회색 전투복
    "uniform_light": "#c6c2c8",  # 셔츠, 밝은 면
    "uniform_dark": "#3b3940",   # 조끼 끈, 장갑, 헤드셋, 부츠
    "helmet": "#b9b6bf",         # 밝은 회색 헬멧 (위에 짙은 띠)
    "visor": "#4f4c58",          # 연기색 감싸는 고글 렌즈
    "beret": "#7b7596",          # 진압반 근무모 (타이다 R41)
}

# 아웃라인: R41 물체는 붉은 갈색 대신 차가운 보라 먹선을 쓴다 (교주 차원과의 대비)
LINE = {
    "shell": "#110c18",
    "metal": "#191422",
    "light": "#47425a",
    "ceramic": "#4a3f63",
    "polymer": "#211b2d",
    "steel": "#2c2a3a",
    "amber": "#5a2a12",
    "rubber": "#0b090f",
}


def mats() -> dict[str, bpy.types.Material]:
    """R41 표준 머티리얼 세트. 쓰지 않은 머티리얼은 내보내기 전에 지워진다 (finish)."""
    M = {}
    for k in ("shell", "metal", "light", "ceramic", "polymer", "steel", "amber", "rubber"):
        M[k] = cb.mat(f"r41_{k}", PAL[k], line=LINE.get(k), roughness=0.5)
    M["glow"] = cb.mat("r41_glow", PAL["glow"], emission=PAL["glow"], unlit=True)
    M["glow_dim"] = cb.mat("r41_glow_dim", PAL["glow_dim"], emission=PAL["glow_dim"], unlit=True)
    M["glow_amber"] = cb.mat("r41_glow_amber", PAL["glow_amber"], emission=PAL["glow_amber"], unlit=True)
    return M


# ------------------------------------------------------------------ primitives

def chbox(name, size, loc=(0, 0, 0), rot=(0, 0, 0), ch=0.002, mat=None, seg=1):
    """모따기 상자. R41 형태 언어의 기본 단위 (평평한 45° 모따기)."""
    return cb.box(name, size=size, loc=loc, rot=rot, bevel=ch, bevel_segments=seg, material=mat)


def prof(name, pts, depth, loc=(0, 0, 0), ch=0.0, mat=None, seg=1, axis="X"):
    """옆모습 외곽선(u=Y, v=Z)을 X로 돌출. loc는 X 중심."""
    return cb.profile_extrude(name, pts, depth, axis=axis, loc=loc, bevel=ch, bevel_segments=seg, material=mat)


def faceted(name, side_pts, front_pts, *, x_center=0.0, ch=0.0, seg=1, mat=None):
    """옆모습(u=Y, v=Z) ∩ 단면(u=X, v=Z) 불리언 교집합.

    R41 셸 특유의 '모서리를 깎은 캡슐' 형태를 만든다. 단면은 X=0 기준, x_center로 이동.
    """
    ys = [p[0] for p in side_pts]
    y0, y1 = min(ys) - 0.01, max(ys) + 0.01
    xs = [p[0] for p in front_pts]
    a = cb.profile_extrude(name, side_pts, (max(xs) - min(xs)) + 0.02, axis="X", loc=(x_center, 0, 0))
    b = cb.profile_extrude(name + "_cut", front_pts, y1 - y0, axis="Y", loc=(x_center, (y0 + y1) / 2, 0))
    m = a.modifiers.new("Isect", "BOOLEAN")
    m.operation = "INTERSECT"
    m.object = b
    m.solver = "EXACT"
    cb.apply_modifiers(a)
    bpy.data.objects.remove(b, do_unlink=True)
    _cleanup(a)
    if ch > 0:
        cb.add_bevel(a, ch, seg, angle=30)
    else:
        cb.smooth(a, angle=30)
    if mat:
        cb.assign(a, mat)
    return a


def _cleanup(obj, dist=1e-5):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def cut(obj, cutter, op="DIFFERENCE"):
    """불리언으로 obj에서 cutter를 빼거나(DIFFERENCE) 합친다(UNION). cutter는 지워진다.

    obj에 이미 베벨 모디파이어가 있으면 불리언이 그 앞에 오도록 순서를 바꾼다.
    """
    m = obj.modifiers.new("Cut", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    idx = obj.modifiers.find(m.name)
    if idx > 0:
        try:
            obj.modifiers.move(idx, 0)
        except AttributeError:
            with bpy.context.temp_override(object=obj, active_object=obj):
                bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)
    cutter.hide_set(True)
    cutter.hide_render = True
    return m


def apply_cuts(obj):
    """cut()으로 걸어 둔 불리언을 적용하고 커터를 지운다."""
    cutters = [m.object for m in obj.modifiers if m.type == "BOOLEAN" and m.object]
    for c in cutters:
        c.hide_set(False)
    cb.apply_modifiers(obj)
    for c in cutters:
        if c.name in bpy.data.objects:
            bpy.data.objects.remove(c, do_unlink=True)
    return obj


def cyl_y(name, r, length, center, *, r_front=None, verts=20, mat=None, ch=0.0, seg=1, cap=True):
    """Y축 원기둥. r = 뒤(-Y) 반지름, r_front = 앞(+Y) 반지름."""
    o = cb.cylinder(name, radius=r, radius2=r_front, depth=length, loc=center, rot=(-90, 0, 0),
                    verts=verts, bevel=ch, bevel_segments=seg, material=mat, cap=cap)
    return o


def cyl_x(name, r, length, center, *, verts=16, mat=None, ch=0.0, seg=1):
    """X축 원기둥 (핀, 축, 나사 머리 등)."""
    return cb.cylinder(name, radius=r, depth=length, loc=center, rot=(0, 90, 0), verts=verts,
                       bevel=ch, bevel_segments=seg, material=mat)


def cyl_z(name, r, length, center, *, r_top=None, verts=16, mat=None, ch=0.0, seg=1):
    return cb.cylinder(name, radius=r, radius2=r_top, depth=length, loc=center, verts=verts,
                       bevel=ch, bevel_segments=seg, material=mat)


def tube(name, r_out, r_in, length, center, *, axis="Y", verts=24, mat=None, ch=0.0):
    """속이 빈 원통 (링, 코일, 덕트). axis: 'X' | 'Y' | 'Z'."""
    bm = bmesh.new()
    h = length / 2
    rings = []
    for r, z in ((r_out, -h), (r_out, h), (r_in, h), (r_in, -h)):
        ring = []
        for i in range(verts):
            a = 2 * math.pi * i / verts
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for k in range(4):
        A, B = rings[k], rings[(k + 1) % 4]
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((A[i], A[j], B[j], B[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rot = {"Y": (-90, 0, 0), "X": (0, 90, 0), "Z": (0, 0, 0)}[axis]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    o.location = center
    o.rotation_euler = [math.radians(a) for a in rot]
    if ch > 0:
        cb.add_bevel(o, ch, 1, angle=50)
    else:
        cb.smooth(o, angle=50)
    if mat:
        cb.assign(o, mat)
    return o


def ngon_prism(name, n, r, length, center, *, axis="Y", rot_deg=0.0, mat=None, ch=0.0, seg=1, r2=None):
    """정n각 기둥 (육각 약실, 오각 프레임). r = 외접원 반지름.

    rot_deg = 꼭짓점 하나가 놓이는 로컬 각도 (로컬 +X에서 반시계).
      axis='Z': 로컬 = 월드 XY. 육각 rot_deg=30 → 평면이 ±X를 봄
      axis='Y': 로컬 (cosθ, sinθ) → 월드 (cosθ, 0, -sinθ). 오각 rot_deg=90 → 꼭짓점이 아래(-Z)
                육각 rot_deg=0 → 꼭짓점이 ±X, 평면이 위아래
    (bmesh create_cone은 첫 꼭짓점을 +90°에 두므로 먼저 0°로 돌려 맞춘다)
    """
    o = cb.cylinder(name, radius=r, radius2=r2, depth=length, loc=center,
                    rot={"Y": (-90, 0, 0), "X": (0, 90, 0), "Z": (0, 0, 0)}[axis], verts=n,
                    bevel=ch, bevel_segments=seg, material=mat)
    o.data.transform(Matrix.Rotation(math.radians(rot_deg - 90.0), 4, "Z"))
    cb.smooth(o, angle=30)
    return o


def screw(name, loc, axis="X", r=0.0024, h=0.0016, mat=None, verts=6):
    """육각 볼트 머리 (3차 디테일). axis 방향으로 표면에서 튀어나온다."""
    rot = {"X": (0, 90, 0), "Y": (-90, 0, 0), "Z": (0, 0, 0)}[axis]
    o = cb.cylinder(name, radius=r, depth=h, loc=loc, rot=rot, verts=verts, material=mat)
    cb.smooth(o, angle=30)
    return o


def slits(prefix, start, step, count, size, mat, rot=(0, 0, 0)):
    """발광 슬릿 열. R41 상태등은 항상 2~4개의 짧은 막대가 줄지어 있다."""
    out = []
    for i in range(count):
        p = (start[0] + step[0] * i, start[1] + step[1] * i, start[2] + step[2] * i)
        out.append(cb.box(f"{prefix}{i}", size=size, loc=p, rot=rot, material=mat))
    return out


def ring_eye(prefix, center, r, *, axis="X", sign=1, mat_ring=None, mat_dot=None, depth=0.0012, verts=20):
    """'고리-점' 표시등: 바깥 고리 + 가운데 점. R41 기계의 눈이자 상태 표시.

    axis/sign: 표면이 바라보는 방향 (예: 'X', +1 → 오른쪽 면).
    """
    rot = {"X": (0, 90, 0), "Y": (-90, 0, 0), "Z": (0, 0, 0)}[axis]
    off = Vector({"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}[axis]) * sign * depth / 2
    c = Vector(center) + off
    ring = tube(prefix + "ring", r, r * 0.68, depth, tuple(c), axis=axis, verts=verts, mat=mat_ring)
    dot = cb.cylinder(prefix + "dot", radius=r * 0.34, depth=depth, loc=tuple(c), rot=rot, verts=12, material=mat_dot or mat_ring)
    return [ring, dot]


# ------------------------------------------------------------------ 엘프 로고 (원작 엘프 종족 로고)
# ART_GUIDE 1장 '엘프 로고 예외'. 원본: public/ui/elf_logo_mono.svg (단색 path 하나)
ELF_LOGO_SVG = "public/ui/elf_logo_mono.svg"
_logo_cache: dict = {}


def _svg_path_points(d: str, samples: int = 8) -> list[list[tuple[float, float]]]:
    """SVG path d → 닫힌 외곽선 목록 (M/L/H/V/C/S/Z, 대소문자). 베지어는 samples개로 나눈다."""
    import re
    toks = re.findall(r"[MmLlHhVvCcSsZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    i, cmd = 0, None
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    last_c2 = None
    loops, pts = [], []

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        if re.fullmatch(r"[A-Za-z]", toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                if pts:
                    loops.append(pts)
                pts, cur = [], start
                continue
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if c == "M":
            cur = start = (ox + num(), oy + num())
            if pts:
                loops.append(pts)
            pts = [cur]
            cmd = "l" if rel else "L"
        elif c == "L":
            cur = (ox + num(), oy + num())
            pts.append(cur)
        elif c == "H":
            cur = ((cur[0] if rel else 0.0) + num(), cur[1])
            pts.append(cur)
        elif c == "V":
            cur = (cur[0], (cur[1] if rel else 0.0) + num())
            pts.append(cur)
        elif c in "CS":
            if c == "C":
                c1 = (ox + num(), oy + num())
            else:
                c1 = (2 * cur[0] - last_c2[0], 2 * cur[1] - last_c2[1]) if last_c2 else cur
            c2 = (ox + num(), oy + num())
            p3 = (ox + num(), oy + num())
            p0 = cur
            for k in range(1, samples + 1):
                t = k / samples
                mt = 1 - t
                pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                            mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
            cur, last_c2 = p3, c2
            continue
        last_c2 = None
    if pts:
        loops.append(pts)
    return loops


def _rdp(pts, eps):
    """Douglas-Peucker 단순화 (닫힌 외곽선은 호출 전에 끝점을 정리)."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0.0, 0
    for k in range(1, len(pts) - 1):
        px, py = pts[k]
        dd = abs(dy * px - dx * py + x1 * y0 - y1 * x0) / L
        if dd > dmax:
            dmax, idx = dd, k
    if dmax > eps:
        return _rdp(pts[: idx + 1], eps)[:-1] + _rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def elf_logo_outline(tolerance: float = 0.0035) -> list[tuple[float, float]]:
    """엘프 로고 외곽선을 높이 1, 가운데 원점, 위 = +v 로 정규화한 점 목록 (반시계)."""
    key = round(tolerance, 6)
    if key in _logo_cache:
        return _logo_cache[key]
    import os
    import re
    path = os.path.join(cb.ROOT, ELF_LOGO_SVG)
    if not os.path.exists(path):
        raise FileNotFoundError(f"엘프 로고 SVG가 없음: {path}")
    svg = open(path, encoding="utf-8").read()
    d = re.search(r'\sd="([^"]+)"', svg).group(1)
    loops = _svg_path_points(d)
    outer = max(loops, key=len)              # 로고는 구멍 없는 외곽선 하나
    xs = [p[0] for p in outer]
    ys = [p[1] for p in outer]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    h = max(ys) - min(ys)
    norm = [((x - cx) / h, -(y - cy) / h) for x, y in outer]   # SVG y는 아래 → 뒤집음
    if math.dist(norm[0], norm[-1]) < 1e-6:
        norm = norm[:-1]
    # 시작점에서 반으로 나눠 단순화 (닫힌 곡선용)
    half = len(norm) // 2
    simp = _rdp(norm[: half + 1], tolerance)[:-1] + _rdp(norm[half:] + [norm[0]], tolerance)[:-1]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(simp, simp[1:] + simp[:1]))
    if area < 0:
        simp.reverse()
    _logo_cache[key] = simp
    return simp


def elf_logo(prefix, center, size, *, axis="X", sign=1, mat=None, depth=0.0008, tolerance=0.0035):
    """원작 엘프 로고 데칼 (톱니바퀴 + 렌치 홈). size = 전체 높이(m).

    axis/sign = 붙는 면의 바깥 방향. 한 면짜리 n각형 데칼이고 이름이 decal_ 로 시작한다 (noOutline).
    """
    pts = [(u * size, v * size) for u, v in elf_logo_outline(tolerance)]
    return [_flat_poly(f"decal_{prefix}elf_logo", pts, center, axis, sign, depth, mat)]


def emblem(prefix, center, size, *, axis="X", sign=1, mat=None, depth=0.0008):
    """R41 엠블럼 = 원작 엘프 로고 (2026-11-01 사용자 결정). 예전 '분열 오각'은 split_pentagon()."""
    return elf_logo(prefix, center, size, axis=axis, sign=sign, mat=mat, depth=depth)


def split_pentagon(prefix, center, size, *, axis="X", sign=1, mat=None, depth=0.0008):
    """(보관용) 예전 오리지널 엠블럼 '분열 오각'. 엠블럼 자리에는 쓰지 않는다 (emblem() = 엘프 로고).

    부대 마크나 계급장 같은 보조 도형이 필요할 때만 쓴다.
    """
    s = size
    gap = s * 0.09
    # 오각 방패 (위가 넓고 아래가 뾰족) 반쪽 외곽선, 로컬 (u=가로, v=세로), 중심 원점
    w = s * 0.42
    top = s * 0.18
    mid = -s * 0.12
    bot = -s * 0.5
    right = [(gap / 2, top), (w, top), (w, mid), (gap / 2 + 0.0, bot + s * 0.06)]
    left = [(-x, y) for x, y in reversed(right)]
    out = []
    for nm, pts in (("R", right), ("L", left)):
        out.append(_flat_poly(f"decal_{prefix}emb_{nm}", pts, center, axis, sign, depth, mat))
    # 위 고리
    ring_c = (0.0, s * 0.36)
    out.append(_flat_ring(f"decal_{prefix}emb_ring", ring_c, s * 0.14, s * 0.075, center, axis, sign, depth, mat))
    return out


def _local_to_world(u, v, center, axis, sign, d):
    cx, cy, cz = center
    if axis == "X":   # 면이 ±X를 봄: u=+Y(앞쪽, sign<0이면 반전), v=Z
        return (cx + sign * d, cy + u * sign, cz + v)
    if axis == "Y":   # 면이 ±Y를 봄: u=X, v=Z
        return (cx - u * sign, cy + sign * d, cz + v)
    return (cx + u, cy + v * sign, cz + sign * d)  # Z: u=X, v=Y


def _outward(axis, sign):
    return Vector({"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}[axis]) * sign


def _flat_poly(name, pts, center, axis, sign, depth, mat):
    """데칼용 한 면짜리 다각형 (표면에서 depth만큼 띄움, 바깥을 향함)."""
    verts = [_local_to_world(u, v, center, axis, sign, depth) for u, v in pts]
    o = cb.from_pydata(name, verts, [list(range(len(pts)))], material=mat)
    _face_out(o, _outward(axis, sign))
    return o


def _flat_ring(name, c2, r_out, r_in, center, axis, sign, depth, mat, seg=16):
    """데칼용 한 면짜리 고리."""
    verts = []
    for r in (r_out, r_in):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append(_local_to_world(c2[0] + r * math.cos(a), c2[1] + r * math.sin(a), center, axis, sign, depth))
    faces = [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)]
    o = cb.from_pydata(name, verts, faces, material=mat)
    _face_out(o, _outward(axis, sign))
    return o


def _face_out(o, out):
    """모든 면의 노멀이 out 쪽을 보도록 뒤집는다 (한 면짜리 데칼)."""
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


def _fix_normals(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False


def stencil_bars(prefix, center, *, axis="X", sign=1, h=0.006, mat=None, pattern=(1, 0, 1, 1, 0, 1), unit=0.0024):
    """부대 식별용 막대 부호 (바코드처럼 읽히는 짧은 세로 막대). 데칼."""
    out = []
    x = -len(pattern) * unit / 2
    for i, b in enumerate(pattern):
        if b:
            pts = [(x, -h / 2), (x + unit * 0.62, -h / 2), (x + unit * 0.62, h / 2), (x, h / 2)]
            out.append(_flat_poly(f"decal_{prefix}bar{i}", pts, center, axis, sign, 0.0006, mat))
        x += unit
    return out


def capture_tag(prefix, anchor, *, mat_tag=None, mat_cord=None, size=(0.02, 0.0012, 0.028), drop=0.026, swing=10):
    """노획 병기 관리 태그 (모나티엄 창고 태그) + 끈. anchor = 끈을 묶은 점. 끈은 뒤(-Y)로 swing도 기운다."""
    t = math.radians(swing)
    d = Vector((0, -math.sin(t), -math.cos(t)))
    a = Vector(anchor)
    c = a + d * (drop / 2)
    cord = cb.cylinder(prefix + "tag_cord", radius=0.0008, depth=drop, loc=tuple(c), rot=(-swing, 0, 0), verts=6, material=mat_cord)
    end = a + d * drop
    tc = end + d * (size[2] / 2 - 0.002)
    tag = cb.box(prefix + "tag", size=size, loc=tuple(tc), rot=(-swing, 0, 6), bevel=0.0012, bevel_segments=1, material=mat_tag)
    return [cord, tag]


# ------------------------------------------------------------------ loft (드론 동체)

OCT_UNIT = [(-0.6, -1.0), (0.6, -1.0), (1.0, -0.55), (1.0, 0.45), (0.55, 1.0), (-0.55, 1.0), (-1.0, 0.45), (-1.0, -0.55)]
"""R41 기본 단면: 위 모서리를 크게 깎은 팔각 (x, z 모두 -1..1)."""


def clip_unit(pts, z_min):
    """단위 단면에서 z >= z_min 부분만 남긴다 (등판 장갑처럼 위쪽만 덮는 판)."""
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ina, inb = a[1] >= z_min, b[1] >= z_min
        if ina:
            out.append(a)
        if ina != inb:
            t = (z_min - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, z_min))
    return out


def section_at(sections, y):
    """sections [(y, 반폭, 반높이, 중심z)] 를 y에서 선형 보간."""
    for (y0, *a), (y1, *b) in zip(sections, sections[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0) if y1 != y0 else 0
            return tuple(p + (q - p) * t for p, q in zip(a, b))
    raise ValueError(f"y={y} 가 단면 범위 밖")


def loft(name, sections, *, base=None, inflate=0.0, mat=None, smooth_angle=32):
    """단면(base, 단위 다각형)을 Y를 따라 이어 붙인 몸통. sections = [(y, 반폭, 반높이, 중심z)].

    inflate: 반폭·반높이에 더하는 값 (위에 덮는 띠·장갑판용).
    """
    base = base or OCT_UNIT
    bm = bmesh.new()
    rings = []
    for y, hw, hh, zc in sections:
        hw += inflate
        hh += inflate
        rings.append([bm.verts.new((x * hw, y, zc + z * hh)) for x, z in base])
    n = len(base)
    for A, B in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((A[i], A[j], B[j], B[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    cb.smooth(o, angle=smooth_angle)
    if mat:
        cb.assign(o, mat)
    return o


def band(name, sections, y0, y1, *, base=None, inflate=0.005, steps=2, mat=None):
    """몸통을 감싸는 띠 (y0..y1 구간을 sections에서 샘플링해 부풀림)."""
    ys = [y0 + (y1 - y0) * i / steps for i in range(steps + 1)]
    secs = [(y, *section_at(sections, y)) for y in ys]
    return loft(name, secs, base=base, inflate=inflate, mat=mat)


def pivot_rotate(objs, pivot, axis, deg):
    """objs를 pivot 둘레로 회전 (월드 기준)."""
    bpy.context.view_layer.update()
    T = Matrix.Translation(Vector(pivot))
    R = Matrix.Rotation(math.radians(deg), 4, axis)
    for o in objs:
        o.matrix_world = T @ R @ T.inverted() @ o.matrix_world


def parent_keep(child, parent):
    """child를 parent 아래로 (둘 다 회전 없는 원점 기준일 때) 월드 위치 유지."""
    bpy.context.view_layer.update()
    w = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.matrix_world = w
    return child


# ------------------------------------------------------------------ assembly

def set_origin(obj, point):
    """메시를 옮겨서 오브젝트 원점을 point(월드)에 둔다. 회전·스케일은 먼저 굽는다."""
    cb.apply_transform(obj, location=True, rotation=True, scale=True)
    p = Vector(point)
    obj.data.transform(Matrix.Translation(-p))
    obj.location = p
    obj.data.update()
    return obj


def merge(objs, name, origin=(0, 0, 0)):
    """여러 파츠를 한 오브젝트로 (머티리얼이 섞여도 됨). 원점 지정."""
    objs = [o for o in objs if o is not None]
    for o in objs:
        cb.apply_modifiers(o)
    out = cb.join(objs, name) if len(objs) > 1 else objs[0]
    out.name = name
    out.data.name = name
    set_origin(out, origin)
    return out


def finish(root_name, rel_path, *, moving=None, anchors=None, props=None, keep=None, static_name=None,
           node_props=None, ground=False):
    """정지 파츠를 머티리얼별로 합치고, 움직이는 파츠/앵커를 루트 아래에 두고 내보낸다.

    moving: {이름: ([오브젝트...], 원점(x,y,z))}  — 하나로 합쳐서 그 이름으로 남김
    anchors: {이름: (x,y,z)}                      — 빈 오브젝트
    keep: 그대로 둘 오브젝트 (이미 합쳐진 회전부 등). 부모 관계는 유지된다.
    node_props: {노드 이름: {속성: 값}} — 특정 노드에만 커스텀 속성 (예: 로터만 얇은 outline)
    ground: True면 가장 낮은 점이 z=0이 되도록 전체(앵커 포함)를 내린다 (드론, 소품)
    """
    moving = moving or {}
    anchors = anchors or {}
    keep = list(keep or [])
    static_name = static_name or root_name
    used = set()
    moved_objs = []
    for name, (objs, origin) in moving.items():
        o = merge(objs, name, origin)
        moved_objs.append(o)
        used.update(id(x) for x in objs)
    keep_ids = {id(o) for o in keep} | {id(o) for o in moved_objs}

    statics = [o for o in bpy.context.scene.objects
               if o.type == "MESH" and id(o) not in keep_ids and o.parent is None]
    groups: dict[str, list] = {}
    decals = []
    for o in statics:
        if o.name.startswith("decal_"):
            decals.append(o)
            continue
        key = o.data.materials[0].name if o.data.materials else "none"
        groups.setdefault(key, []).append(o)
    finals = []
    for key, objs in groups.items():
        short = key.replace("UNLIT_", "").replace("r41_", "")
        finals.append(merge(objs, f"{static_name}_{short}"))
    if decals:
        d = merge(decals, f"{static_name}_decals")
        d["noOutline"] = 1
        finals.append(d)

    dz = 0.0
    if ground:
        lo, _ = cb.bounds()
        dz = -lo.z
        for o in finals + moved_objs + [k for k in keep if k.parent is None]:
            o.location.z += dz
        anchors = {k: (v[0], v[1], v[2] + dz) for k, v in anchors.items()}
        print(f"[r41] ground: shifted by {dz:+.4f} m")

    root = bpy.data.objects.new(root_name, None)
    cb.link(root)
    for o in finals + moved_objs + [k for k in keep if k.parent is None]:
        o.parent = root
    for name, loc in anchors.items():
        cb.empty(name, loc=loc, parent=root, size=0.02)

    for name, kv in (node_props or {}).items():
        o = bpy.data.objects[name]
        for k, v in kv.items():
            o[k] = v

    # 안 쓴 머티리얼 정리 (머티리얼 수 집계를 정확하게)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    cb.export(rel_path, props=props, root=root)
    mats_used = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH" for s in o.material_slots if s.material})
    print(f"[r41] materials ({len(mats_used)}): {', '.join(mats_used)}")
    print(f"[r41] nodes: {', '.join(o.name for o in bpy.context.scene.objects)}")
    deps = bpy.context.evaluated_depsgraph_get()
    per = []
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            me = o.evaluated_get(deps).to_mesh()
            me.calc_loop_triangles()
            per.append((len(me.loop_triangles), o.name))
            o.evaluated_get(deps).to_mesh_clear()
    print("[r41] tris per node: " + ", ".join(f"{n}={t}" for t, n in sorted(per, reverse=True)))
    return root
