"""노획 미군 차량 세트 공용 헬퍼 (vehicles_us).

weapons_us 위에 얹는 차량 전용 도구 (docs/art/VEHICLES.md, docs/art/vehicles-us.md):
  - PAL 확장: 사막 탄(CARC 686A 계열) 차체색, 고무, 방탄유리, 엘프 방석, 램프(언릿), 충돌 전용(투명)
  - lathe(): 회전체 (타이어, 휠, 보기륜, 큐폴라)
  - loft(): 같은 점 수 단면을 Y를 따라 잇기 (차체, 포탑 쐐기)
  - wheel(): 군용 타이어 + 휠 + 허브 (외곽/얇은/세부 세 층)
  - track_loop(): 원 여러 개를 감싸는 궤도 경로 + 슈 배치
  - tag(): 모나티엄 창고 태그 (무기 세트와 같은 문법, 크기 배율)
  - pintle(): 거치 무기 피벗(클레비스 + 기둥). weapons/us/m2.glb 요람 아래 고각 핀에 맞는다
  - VBuild: body / body_thin / body_fine + 움직이는 파츠 + 빈 오브젝트 + COL_ 충돌체 조립기

좌표: 1 BU = 1 m, 차량 정면 -Y, 위 +Z, 차량 왼쪽 +X. 원점 = 차체 중심 아래 지면(z=0).
Blender (x, y, z) → three.js (x, z, -y). 회전: Blender X = three X, Blender Z θ = three Y θ, Blender Y θ = three Z -θ.
"""
from __future__ import annotations

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import weapons_us as us
from weapons_us import (box, boxr, circle_pts, mirror_copy, parent_keep, rrect, section, set_origin, side,  # noqa: F401
                        strip, sweep, text, torus, xcyl, xform, ycyl, ytube, zcyl)

# ------------------------------------------------------------------ palette

VPAL = {
    "tan": "#c4a87c",      # CARC 사막 탄 (686A 계열): 차체 주색
    "tan_dk": "#9b835e",   # 탄 그늘색: 하부, 실내, 프레임 안쪽, 휠
    "rubber": "#3c3e42",   # 타이어, 고무 패드, 궤도 슈 패드
    "glass": "#566e7b",    # 방탄유리 (청회색)
    "glass_hl": "#b9cdd6", # 유리 반사 줄 (세부 데칼)
    "cushion": "#ec9fb1",  # 엘프 방석 (분홍)
    "rope": "#d8c9a3",     # 밧줄, 끈
}
_VLINES = {
    "tan": "#4f3f28",
    "tan_dk": "#3e3221",
    "glass": "#25343c",
    "cushion": "#7a3a4a",
    "rope": "#5e5236",
}
us.PAL.update({k: v for k, v in VPAL.items() if k not in us.PAL})
us._LINES.update({k: v for k, v in _VLINES.items() if k not in us._LINES})


_US_M = us.M


def M(key: str):
    """차량 팔레트 머티리얼. lamp/tail/amber는 언릿, col은 투명(충돌 전용), glass는 반투명.
    weapons_us 헬퍼(boxr, ycyl ...)의 mat= 인자도 이 함수를 거친다(아래 us.M 교체)."""
    if key == "lamp":
        return cb.mat("lamp", "#fff4d2", emission="#fff4d2", unlit=True)
    if key == "tail":
        return cb.mat("tail", "#ff4b3a", emission="#ff4b3a", unlit=True)
    if key == "amber":
        return cb.mat("amber", "#ffb43a", emission="#ffb43a", unlit=True)
    if key == "col":
        return cb.mat("COL", "#ff00ff", alpha=0.0)
    if key == "glass":   # 반투명: 운전석 시점에서 밖이 보이고 밖에서 실내(방석)가 보인다
        return cb.mat("glass", VPAL["glass"], alpha=0.26, line=_VLINES["glass"])
    if key == "glint":   # 유리 반사 줄: 한 면만 (실내에서는 안 보임)
        return cb.mat("glint", VPAL["glass_hl"], double_sided=False)
    return _US_M(key)


us.M = M   # weapons_us 헬퍼가 특수 키(lamp, tail, amber, col, glass)도 알아보게 한다 (런타임 확장, 파일은 그대로)


def setmat(obj, key):
    cb.assign(obj, M(key))
    return obj


# ------------------------------------------------------------------ geometry helpers

def _axp(axis, a, u, v):
    if axis == "x":
        return (a, u, v)
    if axis == "y":
        return (u, a, v)
    return (u, v, a)


def lathe(name, prof, *, segs=32, axis="x", loc=(0, 0, 0), mat=None, smooth=40.0, closed=False, phase=0.0):
    """회전체. prof: [(a, r)] (a = 축 방향 위치, r = 반지름). r=0이면 극점(부채꼴로 닫힘).
    closed=True면 마지막 링을 첫 링에 잇는다 (타이어 단면처럼 닫힌 고리)."""
    bm = bmesh.new()
    rings = []
    for a, r in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(_axp(axis, a, 0.0, 0.0))])
        else:
            rings.append([bm.verts.new(_axp(axis, a, r * math.cos(phase + 2 * math.pi * i / segs),
                                            r * math.sin(phase + 2 * math.pi * i / segs))) for i in range(segs)])
    pairs = list(zip(rings[:-1], rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for A, B in pairs:
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            for j in range(segs):
                bm.faces.new((A[0], B[j], B[(j + 1) % segs]))
        elif len(B) == 1:
            for j in range(segs):
                bm.faces.new((A[(j + 1) % segs], A[j], B[0]))
        else:
            for j in range(segs):
                j2 = (j + 1) % segs
                bm.faces.new((A[j], A[j2], B[j2], B[j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    obj.location = loc
    cb.smooth(obj, angle=smooth)
    if mat:
        setmat(obj, mat)
    return obj


def loft(name, secs, *, mat=None, cap=True, smooth=30.0, axis="y", bevel=0.0, seg=1):
    """secs: [(t, [(u, v), ...]), ...]. axis='y'면 (u, v) = (x, z)이고 t = y.
    모든 단면은 점 수가 같고 같은 방향으로 돈다."""
    bm = bmesh.new()
    rings = []
    for t, pts in secs:
        ring = []
        for (u, v) in pts:
            if axis == "y":
                ring.append(bm.verts.new((u, t, v)))
            elif axis == "x":
                ring.append(bm.verts.new((t, u, v)))
            else:
                ring.append(bm.verts.new((u, v, t)))
        rings.append(ring)
    n = len(rings[0])
    for A, B in zip(rings[:-1], rings[1:]):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((A[j], A[j2], B[j2], B[j]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    if bevel > 0:
        cb.add_bevel(obj, bevel, seg)
    else:
        cb.smooth(obj, angle=smooth)
    if mat:
        setmat(obj, mat)
    return obj


def sym(pts_half):
    """오른쪽 절반 (x>=0, 아래→위) 외곽선을 X 대칭으로 닫는다 → 반시계 전체 외곽선."""
    right = list(pts_half)
    left = [(-x, z) for (x, z) in reversed(right)]
    return right + left


def mx(obj, name=None):
    """X 대칭 복사본까지 [원본, 복사본]으로 돌려준다."""
    return [obj, mirror_copy(obj, name or obj.name + "_mx")]


def plate(name, pts, thick, *, normal_axis="x", at=0.0, bevel=0.0, mat=None):
    """평판: pts는 법선 축에 수직인 평면의 2D 외곽선. normal_axis='x'면 (y,z), 'y'면 (x,z), 'z'면 (x,y)."""
    if normal_axis == "x":
        return cb.profile_extrude(name, pts, thick, axis="X", loc=(at, 0, 0), bevel=bevel, material=mat and M(mat))
    if normal_axis == "y":
        return cb.profile_extrude(name, pts, thick, axis="Y", loc=(0, at, 0), bevel=bevel, material=mat and M(mat))
    return cb.profile_extrude(name, pts, thick, axis="Z", loc=(0, 0, at), bevel=bevel, material=mat and M(mat))


def beam(name, p0, p1, w, h=None, *, up=(0, 0, 1), mat=None, bevel=0.0):
    """두 점 사이 각재 (폭 w, 높이 h). 롤케이지 대신 각진 부재, 받침대."""
    h = w if h is None else h
    P0, P1 = Vector(p0), Vector(p1)
    d = P1 - P0
    L = d.length
    o = cb.box(name, size=(w, L, h), loc=(0, 0, 0), bevel=bevel, material=mat and M(mat))
    T = d.normalized()
    U = Vector(up)
    if abs(T.dot(U)) > 0.98:
        U = Vector((1, 0, 0))
    S = T.cross(U).normalized()
    U = S.cross(T).normalized()
    m = Matrix((S, T, U)).transposed().to_4x4()
    m.translation = (P0 + P1) / 2
    o.matrix_world = m
    return o


def tube(name, pts, r, *, mat=None, verts=10, cap=True, smooth=60.0):
    """원형 단면 관을 경로를 따라 (롤케이지, 손잡이, 난간). 평행 이송 프레임이라 꼬이지 않는다."""
    P = [Vector(p) for p in pts]
    bm = bmesh.new()
    T0 = (P[1] - P[0]).normalized()
    ref = Vector((0, 0, 1)) if abs(T0.z) < 0.9 else Vector((1, 0, 0))
    N = (ref - T0 * ref.dot(T0)).normalized()
    rings = []
    prevT = T0
    for i, p in enumerate(P):
        if i == 0:
            T = T0
        elif i == len(P) - 1:
            T = (P[i] - P[i - 1]).normalized()
        else:
            T = ((P[i] - P[i - 1]).normalized() + (P[i + 1] - P[i]).normalized()).normalized()
        # 평행 이송
        ax = prevT.cross(T)
        if ax.length > 1e-6:
            ang = math.asin(max(-1.0, min(1.0, ax.length)))
            if prevT.dot(T) < 0:
                ang = math.pi - ang
            N = Matrix.Rotation(ang, 3, ax.normalized()) @ N
        prevT = T
        B = T.cross(N).normalized()
        # 꺾인 점에서 단면이 얇아지지 않게 보정
        k = 1.0
        if 0 < i < len(P) - 1:
            a = (P[i] - P[i - 1]).normalized()
            c = math.cos(0.5 * a.angle((P[i + 1] - P[i]).normalized(), 0.0))
            k = 1.0 / max(c, 0.5)
        ring = []
        for j in range(verts):
            t = 2 * math.pi * j / verts
            ring.append(bm.verts.new(p + N * (r * math.cos(t)) + B * (r * math.sin(t) * k)))
        rings.append(ring)
    for A, Bv in zip(rings[:-1], rings[1:]):
        for j in range(verts):
            j2 = (j + 1) % verts
            bm.faces.new((A[j], A[j2], Bv[j2], Bv[j]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    cb.smooth(obj, angle=smooth)
    if mat:
        setmat(obj, mat)
    return obj


def bend(p0, p1, p2, r, n=4):
    """p1 모서리를 반지름 r로 둥글린 점열 (p0→p1→p2), 끝점 p0, p2 포함 안 함."""
    P0, P1, P2 = Vector(p0), Vector(p1), Vector(p2)
    a = (P0 - P1).normalized()
    c = (P2 - P1).normalized()
    ang = a.angle(c, math.pi)
    if ang < 1e-3 or ang > math.pi - 1e-3:
        return [tuple(P1)]
    d = r / math.tan(ang / 2)
    d = min(d, (P0 - P1).length * 0.49, (P2 - P1).length * 0.49)
    s = P1 + a * d
    e = P1 + c * d
    out = []
    for i in range(n + 1):
        t = i / n
        q = (1 - t) ** 2 * s + 2 * (1 - t) * t * P1 + t ** 2 * e
        out.append(tuple(q))
    return out


def rounded_path(pts, r, n=4):
    """꺾은선의 안쪽 모서리를 반지름 r로 둥글린다."""
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        out += bend(pts[i - 1], pts[i], pts[i + 1], r, n)
    out.append(tuple(pts[-1]))
    return out


def glint(name, center, normal, w, h, *, angle=25.0):
    """유리 반사 줄: 법선 쪽에서만 보이는 기울어진 사각 면 (noOutline 세부층에 넣는다)."""
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
    r = up.cross(n).normalized()
    u = n.cross(r).normalized()
    a = math.radians(angle)
    r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
    c = Vector(center) + n * 0.002
    vs = [c - r * w / 2 - u * h / 2, c + r * w / 2 - u * h / 2, c + r * w / 2 + u * h / 2, c - r * w / 2 + u * h / 2]
    o = cb.from_pydata(name, [tuple(v) for v in vs], [(0, 1, 2, 3)])
    if (Vector(vs[1]) - Vector(vs[0])).cross(Vector(vs[2]) - Vector(vs[1])).dot(n) < 0:
        o.data.flip_normals()
    setmat(o, "glint")
    return o


def radial_disc(name, center, normal, r, thick=0.002, *, verts=8, mat=None):
    """표면 법선 방향 원판 (볼트 머리, 리벳, 구멍 표시)."""
    n = Vector(normal).normalized()
    o = cb.cylinder(name, radius=r, depth=thick, verts=verts, material=mat and M(mat))
    q = Vector((0, 0, 1)).rotation_difference(n)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = q
    o.location = Vector(center)
    return o


def bolts_ring(prefix, center, axis, R, n, r, *, thick=0.006, verts=6, mat="steel", phase=0.0):
    """축 axis('x'/'y'/'z') 둘레 반지름 R 원 위 볼트 n개 (세부층)."""
    C = Vector(center)
    out = []
    for i in range(n):
        t = phase + 2 * math.pi * i / n
        if axis == "x":
            p = C + Vector((0, R * math.cos(t), R * math.sin(t)))
            nrm = (1, 0, 0)
        elif axis == "y":
            p = C + Vector((R * math.cos(t), 0, R * math.sin(t)))
            nrm = (0, 1, 0)
        else:
            p = C + Vector((R * math.cos(t), R * math.sin(t), 0))
            nrm = (0, 0, 1)
        out.append(radial_disc(f"{prefix}{i}", p, nrm, r, thick, verts=verts, mat=mat))
    return out


# ------------------------------------------------------------------ wheels

def wheel(prefix, R, W, *, rim_r, outer=+1, lugs=30, lug_depth=0.02, rim_mat="tan", hub_mat="tan_dk",
          segs=40, nuts=8, beadlock=True, style="mt", rim_segs=20, bead_bolts=8, hub_bolts=0):
    """X축 군용 바퀴 (원점 = 바퀴 중심). outer=+1이면 바깥 면이 +X.
    반환: dict(main=[타이어, 휠], thin=[허브 돌기], fine=[너트, 밸브])."""
    h = W / 2
    side_h = R - rim_r
    o = outer
    # 타이어 단면 (닫힌 고리): 바깥 비드 → 숄더 → 트레드 → 안쪽 숄더 → 안쪽 비드
    prof = [
        (o * h * 0.80, rim_r + 0.004),
        (o * h * 0.97, rim_r + side_h * 0.30),
        (o * h * 1.00, rim_r + side_h * 0.62),
        (o * h * 0.95, R - 0.030),
        (o * h * 0.80, R - 0.006),
        (o * h * 0.55, R),
        (-o * h * 0.55, R),
        (-o * h * 0.80, R - 0.006),
        (-o * h * 0.95, R - 0.030),
        (-o * h * 1.00, rim_r + side_h * 0.62),
        (-o * h * 0.97, rim_r + side_h * 0.30),
        (-o * h * 0.80, rim_r + 0.004),
    ]
    tire = lathe(prefix + "_tire", prof, segs=segs, axis="x", closed=True, smooth=50, mat="rubber")
    parts = [tire]
    # 트레드 블록 (두 줄 엇갈림, 숄더까지 감싸는 MT 패턴). lugs=0이면 민무늬
    for i in range(lugs):
        for row in (0, 1):
            t = 360.0 * (i + 0.5 * row) / lugs
            sx = 1 if row == 0 else -1
            if style == "mt":
                x0, x1 = sx * h * 0.06, sx * h * 1.02
            else:
                x0, x1 = sx * h * 0.10, sx * h * 0.78
            xa, xb = min(x0, x1), max(x0, x1)
            arc = 2 * math.pi * R / lugs * 0.46
            rr = R + lug_depth / 2 - 0.004
            lug = cb.box(f"{prefix}_lug{i}_{row}", size=(xb - xa, arc, lug_depth),
                         loc=((xa + xb) / 2, -rr * math.sin(math.radians(t)), rr * math.cos(math.radians(t))),
                         rot=(t, 0, 0), material=M("rubber"))
            parts.append(lug)
    tire_all = cb.join(parts, prefix + "_tire") if len(parts) > 1 else tire
    # 휠 (회전체 솔리드): 바깥 캡 → 허브 → 디스크 → 림 립 → 안쪽
    a_out = o * h * 0.72
    hub_r = rim_r * 0.42
    rp = [
        (a_out + o * 0.030, 0.0),
        (a_out + o * 0.030, hub_r * 0.62),
        (a_out + o * 0.012, hub_r),
        (a_out - o * 0.020, hub_r * 1.05),
        (a_out - o * 0.034, rim_r * 0.80),
        (a_out - o * 0.022, rim_r * 0.92),
        (a_out - o * 0.002, rim_r - 0.004),
        (a_out + o * 0.010, rim_r + 0.012),
        (a_out - o * 0.008, rim_r + 0.016),
        (-a_out, rim_r + 0.006),
        (-a_out, 0.0),
    ]
    rim = lathe(prefix + "_rim", rp, segs=rim_segs, axis="x", smooth=35, mat=rim_mat)
    main = [tire_all, rim]
    thin, fine = [], []
    if beadlock:
        ring = lathe(prefix + "_bead", [(a_out + o * 0.004, rim_r * 0.84), (a_out + o * 0.014, rim_r * 0.86),
                                       (a_out + o * 0.014, rim_r * 0.97), (a_out + o * 0.004, rim_r * 0.99)],
                     segs=rim_segs, axis="x", smooth=30, mat=hub_mat, closed=True)
        thin.append(ring)
        if bead_bolts:
            fine += bolts_ring(prefix + "_bb", (a_out + o * 0.015, 0, 0), "x", rim_r * 0.915, bead_bolts, 0.008,
                               thick=0.006, mat="steel")
    # 너트, 허브 캡 볼트, 공기 밸브(CTIS)
    fine += bolts_ring(prefix + "_nut", (a_out - o * 0.016, 0, 0), "x", hub_r * 1.35, nuts, 0.013, thick=0.014,
                       mat="steel", phase=math.pi / nuts)
    if hub_bolts:
        fine += bolts_ring(prefix + "_hb", (a_out + o * 0.031, 0, 0), "x", hub_r * 0.40, hub_bolts, 0.006,
                           thick=0.004, mat="steel")
    thin.append(xcyl(prefix + "_valve", 0.010, a_out + o * 0.030, a_out + o * 0.060, y=0, z=hub_r * 0.85, verts=8,
                     mat="steel"))
    return {"main": main, "thin": thin, "fine": fine}


# ------------------------------------------------------------------ tracks

def hull2d(points):
    """2D 볼록 껍질 (반시계)."""
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def track_path(circles, n=48):
    """circles: [(y, z, r)] → 감싸는 닫힌 경로 (YZ, 반시계). 궤도 중심선."""
    pts = []
    for (y, z, r) in circles:
        for i in range(n):
            t = 2 * math.pi * i / n
            pts.append((y + r * math.cos(t), z + r * math.sin(t)))
    return hull2d(pts)


def resample(loop, step):
    """닫힌 경로를 같은 간격 step으로 다시 샘플 → [(점, 접선)]."""
    segs = []
    total = 0.0
    n = len(loop)
    for i in range(n):
        a, b = loop[i], loop[(i + 1) % n]
        L = math.dist(a, b)
        segs.append((a, b, L))
        total += L
    count = max(3, int(round(total / step)))
    step = total / count
    out = []
    d = 0.0
    si = 0
    acc = 0.0
    for k in range(count):
        target = k * step
        while si < len(segs) - 1 and acc + segs[si][2] < target:
            acc += segs[si][2]
            si += 1
        a, b, L = segs[si]
        t = 0 if L == 0 else (target - acc) / L
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        tg = ((b[0] - a[0]) / (L or 1), (b[1] - a[1]) / (L or 1))
        out.append((p, tg))
    return out, step


def oboxes(name, boxes, *, mat=None):
    """여러 회전 박스를 한 메시로: boxes = [(중심, X축, Y축, Z축, (sx, sy, sz))]. 궤도 슈처럼 수백 개일 때."""
    bm = bmesh.new()
    corners = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for (c, X, Y, Z, (sx, sy, sz)) in boxes:
        C, X, Y, Z = Vector(c), Vector(X).normalized(), Vector(Y).normalized(), Vector(Z).normalized()
        vs = [bm.verts.new(C + X * (i * sx / 2) + Y * (j * sy / 2) + Z * (k * sz / 2)) for (i, j, k) in corners]
        for q in quads:
            bm.faces.new([vs[i] for i in q])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = cb._new_mesh_obj(name, bm)
    cb.smooth(obj, angle=30)
    if mat:
        setmat(obj, mat)
    return obj


# ------------------------------------------------------------------ elf traces

def tag(b, hole, *, scale=1.0, lines=("MNT", "V-0007", "모나티엄 창고"), yaw=0.0, cord_top=None, thick=None,
        f_add=None, fine_add=None):
    """모나티엄 창고 태그. hole = 끈 구멍(월드), 태그 면은 YZ 평면(법선 ±X)에 만든 뒤 Z축으로 yaw만큼 돌린다.
    무기 세트(M249)와 같은 문법: 크림 종이 + 청록 끈 + 양면 글자(영문 관리번호, 한글 부서명).
    b: s()/f()가 있는 빌더 (us.Build, VBuild). cord_top: 끈이 묶인 위치(없으면 구멍 위 0.02*scale)."""
    s = scale
    TAG_W, TAG_H = 0.024 * s, 0.038 * s
    th = thick if thick is not None else 0.0009 * max(1.0, s * 0.7)
    hx, hy, hz = hole
    top = cord_top if cord_top is not None else (hx, hy, hz + 0.02 * s)
    cord = sweep("tag_cord", [top, ((top[0] + hx) / 2 + 0.001 * s, (top[1] + hy) / 2, (top[2] + hz) / 2), hole],
                 circle_pts(0.0007 * max(1.0, s * 0.8), 6), mat="paint")
    tcx = (hx, hy, hz - TAG_H / 2 + 0.004 * s)
    c = 0.006 * s
    tag_pts = [(-TAG_W / 2, -TAG_H / 2), (TAG_W / 2, -TAG_H / 2), (TAG_W / 2, TAG_H / 2 - c),
               (TAG_W / 2 - c, TAG_H / 2), (-TAG_W / 2 + c, TAG_H / 2), (-TAG_W / 2, TAG_H / 2 - c)]
    paper = side("tag", [(tcx[1] + u, tcx[2] + v) for (u, v) in tag_pts], th, x=tcx[0], mat="paper")
    L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
    R_ = dict(right=(0, 1, 0), up=(0, 0, 1))
    fine = [xcyl("tag_eyelet", 0.0026 * s, tcx[0] - th * 0.7, tcx[0] + th * 0.7, y=hy, z=hz - 0.0005 * s, verts=12,
                 mat="paint")]
    for sx, kw in ((-1, L_), (1, R_)):
        xx = tcx[0] + sx * th / 2
        fine.append(boxr(f"tag_band{sx}", min(xx, xx + sx * 0.0002 * s), max(xx, xx + sx * 0.0002 * s),
                         tcx[1] - TAG_W / 2, tcx[1] + TAG_W / 2, tcx[2] - 0.004 * s, tcx[2] + 0.002 * s, mat="paint"))
        fine.append(text(f"tag_t1{sx}", lines[0], 0.0085 * s, (xx, tcx[1], tcx[2] + 0.0075 * s), mat="black",
                         lift=0.0002 * s, **kw))
        fine.append(text(f"tag_t2{sx}", lines[1], 0.0042 * s, (xx + sx * 0.0002 * s, tcx[1], tcx[2] - 0.001 * s),
                         mat="paper", lift=0.0002 * s, **kw))
        fine.append(text(f"tag_kr{sx}", lines[2], 0.0040 * s, (xx, tcx[1], tcx[2] - 0.0095 * s), mat="black",
                         font="kr", lift=0.0002 * s, **kw))
    for o in [paper] + fine:
        xform(o, rot=(0, 0, yaw), pivot=hole)
    b.s(paper, cord) if f_add is None else f_add(paper, cord)
    b.f(*fine) if fine_add is None else fine_add(*fine)
    return paper


def cushion(name, center, w, d, h, *, mat="cushion", tufts=True):
    """엘프 방석: 둥근 사각 쿠션 (위가 볼록). center = 바닥 중심. 반환 [쿠션, 단추들]."""
    cx, cy, cz = center
    pts = rrect(w, d, min(w, d) * 0.28, n=3)
    secs = []
    for (k, hz) in ((0.92, 0.0), (1.0, h * 0.35), (0.97, h * 0.8), (0.80, h)):
        secs.append((cz + hz, [(cx + u * k, cy + v * k) for (u, v) in pts]))
    o = loft(name, secs, axis="z", mat=mat, smooth=70)
    fine = []
    if tufts:
        for (u, v) in ((-w * 0.22, -d * 0.2), (w * 0.22, -d * 0.2), (-w * 0.22, d * 0.2), (w * 0.22, d * 0.2)):
            fine.append(radial_disc(name + f"_tuft{u:.2f}{v:.2f}", (cx + u, cy + v, cz + h - 0.002), (0, 0, 1),
                                    min(w, d) * 0.05, 0.004, verts=8, mat="paper"))
    return o, fine


def pintle(prefix, base, *, post_h=0.20, stem_r=0.034, mat="black"):
    """거치 무기 피벗: weapons/us/m2.glb 요람 아래 중앙 러그(폭 ±0.025, 고각 핀 지름 0.02)를 잡는 클레비스 + 기둥.
    base = 피벗 원점(무기 원점, 고각 핀 중심)의 월드 좌표. 기둥은 post_h만큼 아래로 내려간다.
    반환: dict(main=[...], fine=[...])  (요만 받는 부분: mount 노드의 자식으로 둔다)."""
    x, y, z = base
    main, fine = [], []
    for sx in (-1, 1):
        cl = side(f"{prefix}_clevis{sx}", [(y - 0.040, z - 0.070), (y + 0.040, z - 0.070), (y + 0.040, z - 0.004),
                                           (y + 0.026, z + 0.026), (y - 0.026, z + 0.026), (y - 0.040, z - 0.004)],
                  0.012, x=x + sx * 0.0335, bevel=0.003, mat=mat)
        main.append(cl)
        fine.append(xcyl(f"{prefix}_pinhead{sx}", 0.014, x + sx * 0.0395, x + sx * 0.0425, y=y, z=z, verts=10,
                         mat="bright"))
    main.append(boxr(f"{prefix}_clevis_base", x - 0.040, x + 0.040, y - 0.042, y + 0.042, z - 0.095, z - 0.066,
                     bevel=0.004, mat=mat))
    main.append(zcyl(f"{prefix}_stem", stem_r, z - post_h, z - 0.094, x=x, y=y, verts=14, mat=mat))
    main.append(zcyl(f"{prefix}_collar", stem_r + 0.012, z - 0.125, z - 0.100, x=x, y=y, verts=14, bevel=0.003,
                     mat="steel"))
    # 잠금 손잡이 (요 고정)
    main.append(xcyl(f"{prefix}_lock", 0.007, x + stem_r, x + stem_r + 0.07, y=y, z=z - 0.112, verts=8, mat="steel"))
    main.append(xcyl(f"{prefix}_lockknob", 0.013, x + stem_r + 0.06, x + stem_r + 0.085, y=y, z=z - 0.112, verts=10,
                     mat="black"))
    return {"main": main, "fine": fine}


# ------------------------------------------------------------------ builder

class VBuild:
    """차량 한 대 조립기.

    s(obj)  정지 파츠 (루트 outline)            → body
    t(obj)  정지 얇은 파츠 (outline=thin)        → body_thin  (손잡이, 난간, 그릴, 안테나)
    f(obj)  정지 세부 (noOutline)                → body_fine  (볼트, 패널선, 글자, 스티커)
    p(part, obj) / pt(part, obj) / pf(part, obj)  움직이는 파츠와 그 얇은/세부 자식
    part(name, pivot, parent=None, rest_rot=None, **props)  파츠 원점, 부모, 커스텀 속성
    empty(name, loc, parent=None, rot=None, **props)        빈 오브젝트 (seat, enter, mount, muzzle, exhaust ...)
    col(name, obj, parent=None)                             COL_ 충돌 전용 메시 (투명, 아웃라인 없음)
    """

    def __init__(self, name):
        self.name = name
        self.static, self.thin, self.fine = [], [], []
        self.parts: dict[str, dict] = {}
        self.empties: list[tuple] = []
        self.cols: list[tuple] = []
        us._cutters.clear()
        M("glass")   # 반투명 유리를 먼저 등록 → us.M("glass")도 같은 머티리얼을 쓴다

    def s(self, *objs):
        self.static.extend(o for o in objs if o is not None)
        return objs[0]

    def t(self, *objs):
        self.thin.extend(o for o in objs if o is not None)
        return objs[0]

    def f(self, *objs):
        self.fine.extend(o for o in objs if o is not None)
        return objs[0]

    def _p(self, part):
        return self.parts.setdefault(part, {"main": [], "thin": [], "fine": [], "pivot": (0, 0, 0), "props": {},
                                            "parent": None, "rest_rot": None})

    def p(self, part, *objs):
        self._p(part)["main"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def pt(self, part, *objs):
        self._p(part)["thin"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def pf(self, part, *objs):
        self._p(part)["fine"].extend(o for o in objs if o is not None)
        return objs[0] if objs else None

    def part(self, name, pivot, parent=None, rest_rot=None, **props):
        d = self._p(name)
        d["pivot"] = tuple(pivot)
        d["parent"] = parent
        d["rest_rot"] = rest_rot
        d["props"].update(props)

    def empty(self, name, loc, parent=None, rot=None, **props):
        self.empties.append((name, tuple(loc), parent, rot, props))

    def col(self, name, obj, parent=None):
        assert name.startswith("COL_")
        setmat(obj, "col")
        self.cols.append((name, obj, parent))

    def finish(self, rel_path, *, outline, thin=0.004, props=None):
        if os.environ.get("US_DEBUG"):
            dg = bpy.context.evaluated_depsgraph_get()
            rows = []
            for o in bpy.context.scene.objects:
                if o.type != "MESH" or o in us._cutters:
                    continue
                me = o.evaluated_get(dg).to_mesh()
                me.calc_loop_triangles()
                rows.append((len(me.loop_triangles), o.name))
                o.evaluated_get(dg).to_mesh_clear()
            rows.sort(reverse=True)
            print("[veh] heavy:", ", ".join(f"{n}={t}" for t, n in rows[:40]))
        root = cb.empty(self.name, size=0.3)
        report = {}
        nodes: dict[str, bpy.types.Object] = {}

        def grp(objs, name, parent, **p):
            o = us._join(objs, name)
            if o is None:
                return None
            for k, v in p.items():
                o[k] = v
            parent_keep(o, parent)
            report[name] = us._tris(o)
            return o

        grp(self.static, "body", root)
        grp(self.thin, "body_thin", root, outline=thin)
        grp(self.fine, "body_fine", root, noOutline=1)

        made = {}
        for name, d in self.parts.items():
            if d["main"]:
                o = us._join(d["main"], name)
                set_origin(o, d["pivot"])
            else:
                o = cb.empty(name, loc=d["pivot"], size=0.1)
            for k, v in d["props"].items():
                o[k] = v
            made[name] = o
            nodes[name] = o
            report[name] = us._tris(o) if o.type == "MESH" else 0
        for name, loc, parent, rot, eprops in self.empties:
            e = cb.empty(name, loc=loc, size=0.1)
            if rot:
                e.rotation_euler = [math.radians(a) for a in rot]
            for k, v in eprops.items():
                e[k] = v
            nodes[name] = e
        bpy.context.view_layer.update()
        # 부모 지정 (월드 위치 유지) → rest_rot은 부모 지정 후 로컬 회전으로
        for name, d in self.parts.items():
            parent_keep(made[name], nodes[d["parent"]] if d["parent"] else root)
        for name, loc, parent, rot, _ in self.empties:
            parent_keep(nodes[name], nodes[parent] if parent else root)
        for name, d in self.parts.items():
            o = made[name]
            if d["thin"]:
                grp(d["thin"], name + "_thin", o, outline=thin)
            if d["fine"]:
                grp(d["fine"], name + "_fine", o, noOutline=1)
        for name, obj, parent in self.cols:
            cb.apply_modifiers(obj)
            obj.name = name
            obj.data.name = name
            obj["noOutline"] = 1
            parent_keep(obj, nodes[parent] if parent else root)
            report[name] = us._tris(obj)
        bpy.context.view_layer.update()
        for name, d in self.parts.items():
            if d["rest_rot"]:
                o = made[name]
                o.rotation_euler = [o.rotation_euler[i] + math.radians(d["rest_rot"][i]) for i in range(3)]
        for c in us._cutters:
            if c.name in bpy.data.objects:
                bpy.data.objects.remove(c, do_unlink=True)
        us._cutters.clear()
        pr = {"outline": outline}
        if props:
            pr.update(props)
        print("[veh] part tris:", ", ".join(f"{k}={v}" for k, v in report.items()))
        print("[veh] materials:", sorted(m.name for m in bpy.data.materials if m.users))
        return cb.export(rel_path, props=pr, root=root)
