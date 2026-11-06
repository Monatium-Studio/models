"""요정 경비대 머스킷 (에르피엔 경비대 제식 화기).

[원작] 요정 왕국 에르피엔 경비대(대장 폴랑)의 화기. 나무위키 「요정(트릭컬 리바이브)」·「폴랑」: 폴랑이 테마극장
       '찬탈과 일탈 사이'에서 세계수의 신물 '코코'를 1년 만에 역설계해 머스킷을 양산했고, 시제품은 300 m에서 10 m쯤
       빗나갔다. 엘프(헤일리·칸나)에게 진법과 제식을 배운 뒤로 경비대가 일제 사격을 한다.
[원작 외형] 테마극장 PV 「여왕님의 마음으로 만든 나라」 2:40~2:55(요정 근위대 일제 사격), 폴랑 캐릭터 카드, 경비대 GIF:
       흰 개머리에 금색 덩굴 장식, 검은 총열 + 총열 아래 검은 꽂을대, 금색 총열 띠, 손목 위 금색 공이 곡선,
       옆으로 고리 결합한 금색 소켓 총검. 볼트 손잡이는 없다 → 전장식 플린트록 머스킷으로 판정했다.
[오리지널] 형태는 3D SD로 다시 그렸다. 덩굴은 세계수 잎을 본뜬 오리지널 문양이다.
[원작] 엠블럼 나비 = 에르피엔 군기의 나비 (lib/erpien_flag.py, 사용자 결정 2026-11-02: 샤코·부츠와 같은 요정 왕국 문장).
       엘프 로고는 엘프 진영 전용이라 쓰지 않는다.
근거와 수치: docs/art/fairy-faction.md

좌표: 원점 = 오른손 파지점(개머리 손목 중심), 총구 +Y, 위 +Z, 사수 오른쪽 +X (docs/art/ART_GUIDE.md 7장).
자물쇠(플린트록)는 오른쪽(+X), 1인칭에서 보이는 왼쪽(-X)에는 금색 곁판과 작은 엠블럼이 있다.

npm run model -- art/blender/weapons/fairy/fairy_guard_musket.py
npm run shot -- weapons/fairy/fairy_guard_musket.glb --views side,34,top,muzzle
npm run shot -- weapons/fairy/fairy_guard_musket.glb --mode fp
npm run shot -- weapons/fairy/fairy_guard_musket.glb --mode fp --ads 1
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import erpien_flag as ef  # noqa: E402

V = Vector
cb.reset()

# ================================================================== 팔레트 (원작 카드·경비대 GIF 실측을 툰 3단에 맞게 조정)
# 개머리 #f8f8f8~#f0e8e0(흰 래커), 금장 #e8c880, 총열 #504848, 샤코 초록 #305850~#386050.
LINE = "#4a2229"        # 원작 공통 붉은 갈색 먹선
LINE_DARK = "#24100f"
PAL = {
    "wood": ("#f3eee6", LINE),        # 흰 래커 개머리
    "gold": ("#e8c57c", LINE),        # 금장 (띠, 공이, 총검, 덩굴)
    "gold_d": ("#b98a44", LINE),      # 짙은 금 (각인, 홈, 나비 윤곽선·말린 선)
    "iron": ("#4a4449", LINE_DARK),   # 검은 총열, 꽂을대, 나사
    "dark": ("#2a2327", LINE_DARK),   # 총구 속, 홈
    "green": ("#33604f", LINE_DARK),  # 경비대 초록 (엠블럼 원판, 샤코와 같은 계열)
    "flint": ("#8d857c", LINE_DARK),  # 부싯돌, 부시 타격면
}


def M(key):
    c, ln = PAL[key]
    return cb.mat(f"fm_{key}", c, line=ln, roughness=0.55)


def mv(dx, dy, dz):
    """Blender 변위 → three.js 부모 공간 move 문자열 (x, z, -y)."""
    f = lambda v: f"{round(v + 0.0, 4):g}"  # noqa: E731
    return f"{f(dx)},{f(dz)},{f(-dy)}"


# ================================================================== 2D 도형
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def rrect(w, h, r, n=3, cx=0.0, cy=0.0):
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    for (ox, oy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                         (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def ellipse(cx, cy, rx, ry, n=20, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        u, v = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + u * c - v * s, cy + u * s + v * c))
    return out


def lens(p0, p1, width, n=6):
    """p0→p1 방향 잎(렌즈) 외곽선. 뿌리는 둥글고 끝은 뾰족하다."""
    p0, p1 = V(p0), V(p1)
    d = p1 - p0
    L = d.length
    t = d / L
    nrm = V((-t.y, t.x))
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        w = width / 2 * math.sin(math.pi * u) ** 0.8 * (1 - 0.35 * u)
        c = p0 + d * u
        top.append(tuple(c + nrm * w))
        bot.append(tuple(c - nrm * w))
    return top + list(reversed(bot[1:-1]))


def spiral(cx, cy, r0, r1, a0, turns, n=None, sgn=1):
    """나선 중심선 (a0도에서 시작, sgn=+1 반시계)."""
    n = n or max(7, int(12 * turns))
    pts = []
    for i in range(n + 1):
        u = i / n
        a = math.radians(a0) + sgn * 2 * math.pi * turns * u
        r = lerp(r0, r1, u)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def strip(path, thickness, taper=None):
    """2D 폴리라인 → 두께 있는 닫힌 외곽선. taper(u) → 두께 배율."""
    n = len(path)

    def off(d_sign):
        out = []
        for i, p in enumerate(path):
            a = V(path[max(i - 1, 0)])
            b = V(path[min(i + 1, n - 1)])
            t = (b - a).normalized()
            nr = V((-t.y, t.x))
            k = taper(i / (n - 1)) if taper else 1.0
            d = d_sign * thickness / 2 * k
            out.append((p[0] + nr.x * d, p[1] + nr.y * d))
        return out
    return off(1) + list(reversed(off(-1)))


def catmull2(pts, n_per=6):
    """2D 제어점을 지나는 부드러운 곡선."""
    P = [V(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]
        p1, p2 = P[i], P[i + 1]
        p3 = P[min(i + 2, len(P) - 1)]
        for j in range(n_per):
            t = j / n_per
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((q.x, q.y))
    out.append(tuple(P[-1]))
    return out


# ================================================================== 3D 기본 도형
def _obj(name, bm, mat=None, smooth=40.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=smooth)
    if mat:
        cb.assign(o, M(mat) if isinstance(mat, str) else mat)
    return o


def side(name, pts, width, x=0.0, *, bevel=0.0, seg=2, mat=None, angle=40.0):
    """옆모습 (y, z) 외곽선을 X 두께 width로 돌출."""
    o = cb.profile_extrude(name, pts, width, axis="X", loc=(x, 0, 0), material=M(mat) if mat else None)
    if bevel > 0:
        cb.add_bevel(o, bevel, seg, angle=angle)
    else:
        cb.smooth(o, angle=35)
    return o


def ycyl(name, r, y0, y1, x=0.0, z=0.0, *, verts=20, r2=None, bevel=0.0, mat=None, rot_y=0.0):
    return cb.cylinder(name, radius=r, radius2=r2, depth=y1 - y0, loc=(x, (y0 + y1) / 2, z), rot=(-90, rot_y, 0),
                       verts=verts, bevel=bevel, bevel_segments=2, material=M(mat) if mat else None)


def xcyl(name, r, x0, x1, y=0.0, z=0.0, *, verts=12, mat=None, bevel=0.0):
    return cb.cylinder(name, radius=r, depth=x1 - x0, loc=((x0 + x1) / 2, y, z), rot=(0, 90, 0), verts=verts,
                       bevel=bevel, bevel_segments=1, material=M(mat) if mat else None)


def zcyl(name, r, z0, z1, x=0.0, y=0.0, *, verts=12, mat=None, r2=None):
    return cb.cylinder(name, radius=r, radius2=r2, depth=z1 - z0, loc=(x, y, (z0 + z1) / 2), verts=verts,
                       material=M(mat) if mat else None)


def tube(name, r_out, r_in, y0, y1, *, c=(0.0, 0.0), verts=24, mat=None):
    """Y축 속 빈 관."""
    bm = bmesh.new()
    rings = []
    for (r, y) in ((r_out, y0), (r_out, y1), (r_in, y1), (r_in, y0)):
        rings.append([bm.verts.new((c[0] + r * math.cos(2 * math.pi * i / verts), y,
                                    c[1] + r * math.sin(2 * math.pi * i / verts))) for i in range(verts)])
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        for i in range(verts):
            j = (i + 1) % verts
            bm.faces.new((rings[a][i], rings[a][j], rings[b][j], rings[b][i]))
    return _obj(name, bm, mat)


def torus(name, R, r, loc, rot=(0, 0, 0), *, seg=16, rseg=6, mat=None, ry=None):
    bm = bmesh.new()
    ry = R if ry is None else ry
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new(((R + r * math.cos(b)) * ca, (ry + r * math.cos(b)) * sa, r * math.sin(b)))
                      for b in (2 * math.pi * j / rseg for j in range(rseg))])
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(rseg):
            j2 = (j + 1) % rseg
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))
    o = _obj(name, bm, mat, smooth=180)
    cb._place(o, loc, rot, (1, 1, 1))
    return o


def sweep(name, path, sec, *, side_vec=(1, 0, 0), cap=True, mat=None, smooth=180.0, scales=None):
    """단면 sec (u, v)를 3D 경로를 따라 쓸기. u = side_vec 방향."""
    bm = bmesh.new()
    S = V(side_vec).normalized()
    P = [V(p) for p in path]
    rings = []
    for i, p in enumerate(P):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, len(P) - 1)]
        T = (b - a).normalized()
        s = (S - T * S.dot(T)).normalized()
        N = s.cross(T).normalized()
        su, sv = scales(i / (len(P) - 1)) if scales else (1.0, 1.0)
        rings.append([bm.verts.new(p + s * (u * su) + N * (v * sv)) for (u, v) in sec])
    k = len(sec)
    for i in range(len(rings) - 1):
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    return _obj(name, bm, mat, smooth=smooth)


def xform(obj, *, loc=None, rot=None, pivot=(0, 0, 0)):
    cb.apply_modifiers(obj)
    M4 = Matrix.Identity(4)
    if rot:
        P = V(pivot)
        R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
             @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        M4 = Matrix.Translation(P) @ R @ Matrix.Translation(-P)
    if loc:
        M4 = Matrix.Translation(V(loc)) @ M4
    obj.matrix_world = M4 @ obj.matrix_world
    return obj


# ================================================================== 개머리 (흰 래커 목재): 단면 로프트
# 위·아래 윤곽선과 반폭을 y 함수로 정의한다. 손목(원점)은 가늘고 둥글게, 개머리는 넓고 납작한 옆면,
# 자물쇠 자리는 깊고 각지게, 앞 개머리는 총열을 받치는 홈 높이까지.
BZ = 0.050          # 총열 축 높이
Y_BUTT = -0.362     # 개머리 끝
Y_FORE = 0.520      # 앞 개머리 끝 (노즈캡)
Y_MUZ = 0.680       # 총구
Y_BREECH = 0.063    # 약실 끝 (총열 시작)
R_OCT = 0.0150      # 팔각 약실 외접 반경
R_B0, R_MUZ = 0.0136, 0.0122   # 둥근 총열 뒤·총구 반경 (원작처럼 굵게: 실물보다 약 25% 두툼)
SZ = BZ + R_MUZ + 0.0150       # 조준선 높이 = 가늠쇠 끝 (가늠자 홈 바닥은 조금 아래). 게임용으로 높고 굵게
RR_Z, RR_R = BZ - 0.0232, 0.0052   # 꽂을대 축 높이·반경

TOP = [(-0.362, 0.034), (-0.30, 0.032), (-0.20, 0.029), (-0.13, 0.026), (-0.085, 0.022), (-0.045, 0.0190),
       (-0.010, 0.0200), (0.020, 0.027), (0.045, 0.041), (0.070, 0.0525), (0.10, 0.0555), (0.16, 0.0560),
       (0.22, 0.0570), (0.52, 0.0570)]
BOT = [(-0.362, -0.097), (-0.30, -0.083), (-0.24, -0.069), (-0.18, -0.055), (-0.12, -0.041), (-0.08, -0.030),
       (-0.05, -0.0225), (-0.02, -0.0200), (0.02, -0.0190), (0.06, -0.0175), (0.10, -0.0135), (0.14, -0.0020),
       (0.18, 0.0100), (0.22, 0.0135), (0.52, 0.0140)]
HALF = [(-0.362, 0.0196), (-0.20, 0.0180), (-0.10, 0.0154), (-0.04, 0.0132), (0.0, 0.0134), (0.04, 0.0150),
        (0.07, 0.0166), (0.14, 0.0166), (0.20, 0.0155), (0.28, 0.0150), (0.52, 0.0146)]
PEXP = [(-0.362, 3.4), (-0.15, 3.0), (-0.06, 2.4), (0.0, 2.4), (0.05, 3.4), (0.14, 3.8), (0.22, 3.0), (0.52, 3.0)]


def rb(y):
    """총열 반경 (약실 팔각은 내접 반경)."""
    if y < 0.157:
        return R_OCT * math.cos(math.radians(22.5))
    return lerp(R_B0, R_MUZ, clamp((y - 0.157) / (Y_MUZ - 0.157)))


def fkey(tab, y):
    """비균일 키의 부드러운 보간 (카디널 에르미트)."""
    if y <= tab[0][0]:
        return tab[0][1]
    if y >= tab[-1][0]:
        return tab[-1][1]
    for i in range(len(tab) - 1):
        y0, v0 = tab[i]
        y1, v1 = tab[i + 1]
        if y0 <= y <= y1:
            h = y1 - y0
            t = (y - y0) / h
            ym, vm = tab[max(i - 1, 0)]
            yp, vp = tab[min(i + 2, len(tab) - 1)]
            m0 = (v1 - vm) / (y1 - ym) if i > 0 else (v1 - v0) / h
            m1 = (vp - v0) / (yp - y0) if i + 2 < len(tab) else (v1 - v0) / h
            t2, t3 = t * t, t * t * t
            return ((2 * t3 - 3 * t2 + 1) * v0 + (t3 - 2 * t2 + t) * h * m0 + (-2 * t3 + 3 * t2) * v1
                    + (t3 - t2) * h * m1)
    return tab[-1][1]


def stock_at(y):
    top, bot = fkey(TOP, y), fkey(BOT, y)
    return fkey(HALF, y), (top + bot) / 2, (top - bot) / 2, fkey(PEXP, y)


def sup(c, s, a, b, p):
    e = 2.0 / p
    return a * math.copysign(abs(c) ** e, c), b * math.copysign(abs(s) ** e, s)


def x_surf(y, z):
    a, zc, b, p = stock_at(y)
    u = clamp(abs(z - zc) / b, 0.0, 0.985)
    return a * (1 - u ** p) ** (1 / p)


def stock_loft(name, ys, segs=18, mat="wood"):
    bm = bmesh.new()
    rings = []
    for y in ys:
        a, zc, b, p = stock_at(y)
        ring = []
        for j in range(segs):
            th = 2 * math.pi * j / segs
            x, z = sup(math.cos(th), math.sin(th), a, b, p)
            ring.append(bm.verts.new((x, y, zc + z)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for j in range(segs):
            j2 = (j + 1) % segs
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _obj(name, bm, mat, smooth=50)


def sup_ring(name, y0, y1, a, zc, b, p, *, mat="gold", inset=0.0022, segs=18, closed_front=False,
             closed_back=False):
    """초타원 단면 고리 띠 (총열 띠, 노즈캡). closed_front면 앞면을 막는다."""
    bm = bmesh.new()

    def ring(y, da):
        out = []
        for j in range(segs):
            th = 2 * math.pi * j / segs
            x, z = sup(math.cos(th), math.sin(th), a + da, b + da, p)
            out.append(bm.verts.new((x, y, zc + z)))
        return out
    o0, o1 = ring(y0, 0.0), ring(y1, 0.0)
    i0, i1 = ring(y0, -inset), ring(y1, -inset)
    seqs = [(o0, o1), (o1, i1), (i1, i0), (i0, o0)]
    if closed_front:
        seqs = [(o0, o1), (i0, o0)]
    if closed_back:
        seqs = [(o0, o1), (o1, i1)]
    for A, B in seqs:
        for j in range(segs):
            j2 = (j + 1) % segs
            bm.faces.new((A[j], A[j2], B[j2], B[j]))
    if closed_front:
        bm.faces.new(o1)
    if closed_back:
        bm.faces.new(list(reversed(o0)))
    return _obj(name, bm, mat, smooth=60)


# ================================================================== 개머리 표면 부조 (금 덩굴, 곁판, 엠블럼)
def _relief_bm(poly, tris, sgn, lift, sink, xs, extra=None):
    """윗면 삼각형 + 옆벽. extra: 윗면에만 쓰는 추가 점(부채 중심 등)."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)) / 2
    bm = bmesh.new()
    pts = list(poly) + list(extra or [])
    top = [bm.verts.new((sgn * (xs(y, z) + lift), y, z)) for y, z in pts]
    bot = [bm.verts.new((sgn * (xs(y, z) - sink), y, z)) for y, z in poly]
    for tri in tris:
        f = bm.faces.new([top[i] for i in tri])
        f.normal_update()
        if f.normal.x * sgn < 0:
            f.normal_flip()
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((top[i], top[j], bot[j], bot[i]))
        f.normal_update()
        dy, dz = poly[j][0] - poly[i][0], poly[j][1] - poly[i][1]
        out = V((0, dz, -dy)) if area > 0 else V((0, -dz, dy))
        if f.normal.dot(out) < 0:
            f.normal_flip()
    return bm


def relief(name, poly, sgn, *, lift=0.0008, sink=0.0012, mat="gold", xs=x_surf, fan=False):
    """(y, z) 외곽선을 개머리 옆면(sgn=+1 오른쪽, -1 왼쪽)에 붙인 얇은 부조. 옆면 곡률을 따라간다.
    fan=True: 볼록한 도형(원판·잎)은 중심 부채로 채운다 (긴 삼각형이 곡면 아래로 가라앉지 않게)."""
    n = len(poly)
    if fan:
        cy = sum(p[0] for p in poly) / n
        cz = sum(p[1] for p in poly) / n
        tris = [(i, (i + 1) % n, n) for i in range(n)]
        bm = _relief_bm(poly, tris, sgn, lift, sink, xs, extra=[(cy, cz)])
    else:
        tris = tessellate_polygon([[V((y, z, 0.0)) for y, z in poly]])
        bm = _relief_bm(poly, tris, sgn, lift, sink, xs)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=35)
    cb.assign(o, M(mat))
    return o


def band_relief(name, ys, ztop, zbot, sgn, *, lift=0.0016, sink=0.0012, mat="gold", xs=x_surf):
    """길쭉한 판(자물쇠판, 곁판): 같은 y에서 위·아래 점을 이은 사각 띠로 채운다 (y 방향 긴 삼각형 없음).
    ys 양끝에서 ztop == zbot이면 뾰족하게 모인다."""
    n = len(ys)
    upper = [(y, ztop(y)) for y in ys]
    lower = [(y, zbot(y)) for y in ys]
    poly = upper + list(reversed(lower[1:-1]))
    m = len(poly)
    idx_lo = [0] + [m - i for i in range(1, n - 1)] + [n - 1]
    tris = []
    for i in range(n - 1):
        a_, b_ = i, i + 1
        c_, d_ = idx_lo[i + 1], idx_lo[i]
        if c_ == b_:
            tris.append((a_, b_, d_))
        elif d_ == a_:
            tris.append((a_, b_, c_))
        else:
            tris.append((a_, b_, c_))
            tris.append((a_, c_, d_))
    bm = _relief_bm(poly, tris, sgn, lift, sink, xs)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=35)
    cb.assign(o, M(mat))
    return o


def relief_ring(name, cy, cz, rx, ry, w, sgn, *, lift=0.0014, sink=0.0012, mat="gold", n=18, xs=x_surf):
    """타원 고리 부조 (엠블럼 금테)."""
    bm = bmesh.new()
    rows = []
    for (dr, l) in ((0, lift), (-w, lift), (-w, -sink), (0, -sink)):
        row = []
        for i in range(n):
            a = 2 * math.pi * i / n
            y, z = cy + (rx + dr) * math.cos(a), cz + (ry + dr) * math.sin(a)
            row.append(bm.verts.new((sgn * (xs(y, z) + l), y, z)))
        rows.append(row)
    for a_, b_ in ((0, 1), (1, 2), (3, 0)):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((rows[a_][i], rows[a_][j], rows[b_][j], rows[b_][i]))
    return _obj(name, bm, mat, smooth=35)


def vine(prefix, path, sgn, *, w=0.0021, lift=0.0008, mat="gold", taper=None):
    return relief(prefix, strip(path, w, taper), sgn, lift=lift, mat=mat)


def relief_grid(name, poly, sgn, *, step, lift=0.0008, sink=0.0012, mat="gold", xs=x_surf):
    """오목한 외곽선 부조 (에르피엔 나비): 안쪽 격자점을 넣은 제약 들로네 분할(erpien_flag.grid_tris)이라 긴 삼각형 없이
    개머리 곡면을 따라간다."""
    pts = [tuple(p) for p in poly]
    idx = {p: i for i, p in enumerate(pts)}
    tris = []
    for tri in ef.grid_tris(pts, step):
        f = []
        for p in tri:
            if p not in idx:
                idx[p] = len(pts)
                pts.append(p)
            f.append(idx[p])
        tris.append(tuple(f))
    bm = _relief_bm(pts[:len(poly)], tris, sgn, lift, sink, xs, extra=pts[len(poly):])
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=35)
    cb.assign(o, M(mat))
    return o


def butterfly(prefix, cy, cz, s, sgn, *, lift=0.0020, xs=x_surf, strokes=True):
    """경비대 문장 = 에르피엔 군기의 나비 (lib/erpien_flag: outline·edge_outline·STROKES, 사용자 결정 2026-11-02).
    개머리 곡면을 따르는 부조 세 겹: 짙은 금 윤곽선 판 → 금 바탕(0.4 mm 위) → 짙은 금 말린 선(0.8 mm 위).
    s = 예전 인자(나비 전체 폭의 절반쯤, m). 나비 반폭은 0.8 s (원판 금테 안에 들어간다)."""
    h = 0.8 * s
    T = lambda pts: [(cy + x * h, cz + z * h) for x, z in pts]  # noqa: E731
    step = 0.3 * h
    out = [relief_grid(f"{prefix}_edge", T(ef.edge_outline(1)), sgn, step=step, lift=lift, mat="gold_d", xs=xs),
           relief_grid(f"{prefix}_fill", T(ef.outline(1)), sgn, step=step, lift=lift + 0.0004, mat="gold", xs=xs)]
    if strokes:
        for i, st in enumerate(ef.STROKES):
            for sx in (1, -1):
                path = T([(sx * x, z) for x, z in st])
                out.append(relief(f"{prefix}_line{i}_{sx}", strip(path, ef.STROKE_W * h, lambda u: 1.0 - 0.55 * u), sgn,
                                  lift=lift + 0.0008, mat="gold_d", xs=xs))
    return out


# ================================================================== 조립기 (home_weapons.Gun과 같은 규약, 부조 그룹 추가)
class Gun:
    def __init__(self, name):
        self.name = name
        self.static, self.inlay, self.fine = [], [], []
        self.parts, self.pfine, self.pivots, self.pprops, self.parents = {}, {}, {}, {}, {}
        self.anchors = []

    def s(self, *o):
        self.static.extend(o)
        return o[0]

    def i(self, *o):
        self.inlay.extend(x for x in o if x is not None)
        return o[0]

    def f(self, *o):
        self.fine.extend(x for x in o if x is not None)
        return o[0]

    def p(self, part, *o):
        self.parts.setdefault(part, []).extend(o)
        return o[0]

    def pf(self, part, *o):
        self.pfine.setdefault(part, []).extend(o)
        return o[0]

    def pivot(self, part, pt, **props):
        self.pivots[part] = tuple(pt)
        self.pprops.setdefault(part, {}).update(props)

    def anchor(self, name, pt, parent=None):
        self.anchors.append((name, tuple(pt), parent))

    @staticmethod
    def _join(objs, name):
        for o in objs:
            cb.apply_modifiers(o)
        if len(objs) == 1:
            objs[0].name = name
            objs[0].data.name = name
            return objs[0]
        return cb.join(objs, name)

    @staticmethod
    def _keep(child, parent):
        bpy.context.view_layer.update()
        mw = child.matrix_world.copy()
        child.parent = parent
        child.matrix_parent_inverse = Matrix.Identity(4)
        child.matrix_world = mw

    @staticmethod
    def _origin(obj, pt):
        bpy.context.view_layer.update()
        mw = obj.matrix_world.copy()
        local = mw.inverted() @ V(pt)
        obj.data.transform(Matrix.Translation(-local))
        obj.matrix_world = mw @ Matrix.Translation(local)

    @staticmethod
    def _tris(o):
        o.data.calc_loop_triangles()
        return len(o.data.loop_triangles)

    def finish(self, rel, *, outline, inlay_outline, fp, fprot, extra=None, budget=12000, max_mats=8):
        root = cb.empty(self.name, size=0.1)
        rep = {}
        if os.environ.get("FM_DEBUG"):
            dg = bpy.context.evaluated_depsgraph_get()
            rows = []
            for o in self.static + self.inlay:
                me = o.evaluated_get(dg).to_mesh()
                me.calc_loop_triangles()
                rows.append((len(me.loop_triangles), o.name))
            for n_, nm in sorted(rows, reverse=True)[:60]:
                print(f"[fm]   {nm}: {n_}")
        body = self._join(self.static, "body")
        self._keep(body, root)
        rep["body"] = self._tris(body)
        if self.inlay:
            inl = self._join(self.inlay, "body_inlay")
            inl["outline"] = inlay_outline     # 금 덩굴·곁판·엠블럼: 원작처럼 가는 먹선
            self._keep(inl, root)
            rep["body_inlay"] = self._tris(inl)
        if self.fine:
            fn = self._join(self.fine, "body_fine")
            fn["noOutline"] = 1
            self._keep(fn, root)
            rep["body_fine"] = self._tris(fn)
        made = {}
        for part, objs in self.parts.items():
            o = self._join(objs, part)
            self._origin(o, self.pivots.get(part, (0, 0, 0)))
            for k, v in self.pprops.get(part, {}).items():
                o[k] = v
            made[part] = o
            rep[part] = self._tris(o)
        for part, o in made.items():
            self._keep(o, made[self.parents[part]] if part in self.parents else root)
        for part, objs in self.pfine.items():
            o = self._join(objs, part + "_fine")
            o["noOutline"] = 1
            self._keep(o, made[part])
            rep[part + "_fine"] = self._tris(o)
        for name, pt, par in self.anchors:
            e = cb.empty(name, loc=pt, size=0.02)
            self._keep(e, made[par] if par else root)
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        props = {"outline": outline, "fpOffset": fp, "fpRot": fprot}
        props.update(extra or {})
        total = sum(rep.values())
        mats = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                       for s in o.material_slots if s.material})
        print("[fm] part tris:", ", ".join(f"{k}={v}" for k, v in rep.items()))
        print(f"[fm] total tris {total} / {budget}, materials {len(mats)} / {max_mats}: {', '.join(mats)}")
        if total > budget or len(mats) > max_mats:
            raise RuntimeError(f"[fm] 예산 초과: tris {total}/{budget}, materials {len(mats)}/{max_mats}")
        return cb.export(rel, props=props, root=root)


g = Gun("fairy_guard_musket")

# ================================================================== 개머리
ys = []
y = Y_BUTT
while y < Y_FORE - 1e-6:
    ys.append(y)
    step = 0.0125 if -0.095 < y < 0.205 else 0.030     # 손목·자물쇠 자리(곡률 큰 곳)는 촘촘히
    y += step
ys.append(Y_FORE)
g.s(stock_loft("stock", ys, segs=18))


def edge_trim(name, y0, y1, n, where, *, th=0.0026, extra=0.0012, mat="gold", taper=None):
    """개머리 위(where='top')·아래('bot') 모서리를 감싸는 금테. 옆에서 보면 금색 테두리 선."""
    pts, sc = [], []
    for i in range(n):
        yy = lerp(y0, y1, i / (n - 1))
        a_, zc_, b_, p_ = stock_at(yy)
        zz = (zc_ + b_ + th * 0.30) if where == "top" else (zc_ - b_ - th * 0.30)
        pts.append((0.0, yy, zz))
        sc.append(2 * a_ * 0.92 + extra)
    sec = rrect(1.0, th, th * 0.45, 1)
    return sweep(name, pts, sec, mat=mat, smooth=50,
                 scales=lambda u: (sc[min(int(round(u * (n - 1))), n - 1)] * (taper(u) if taper else 1.0), 1.0))


# 개머리판 (금, 끝면) + 빗등·발끝 금테 (원작 개머리의 금색 테두리)
a, zc, b, p = stock_at(Y_BUTT)
g.s(sup_ring("butt_plate", Y_BUTT - 0.006, Y_BUTT + 0.004, a + 0.0010, zc, b + 0.0010, p, inset=0.004, mat="gold",
             closed_back=True))
g.s(edge_trim("comb_trim", Y_BUTT, -0.120, 12, "top", taper=lambda u: 1.0 - 0.25 * u))
g.s(edge_trim("toe_trim", Y_BUTT, -0.095, 12, "bot"))
g.s(edge_trim("fore_trim", 0.150, Y_FORE - 0.012, 11, "bot"))
# 개머리 발끝 금 소용돌이 (원작 개머리 끝의 금색 말림)
toe = [(-0.352, fkey(BOT, -0.352) - 0.0012), (-0.364, -0.1000), (-0.3725, -0.1055)]
toe += spiral(-0.3625, -0.1125, 0.0118, 0.0035, 160, 0.95, n=11, sgn=1)[1:]
g.s(sweep("toe_curl", [(0.0, yy, zz) for yy, zz in toe], ellipse(0, 0, 0.0060, 0.0024, 6), mat="gold",
          scales=lambda u: (lerp(1.0, 0.55, u ** 1.5), lerp(1.0, 0.7, u))))
# 노즈캡 (앞 개머리 끝, 금)
a, zc, b, p = stock_at(Y_FORE)
g.s(sup_ring("nose_cap", Y_FORE - 0.016, Y_FORE + 0.004, a + 0.0011, zc, b + 0.0011, p, inset=0.003,
             closed_front=True))

# ================================================================== 총열 (검정): 팔각 약실 + 둥근 총열
g.s(cb.cylinder("breech_oct", radius=R_OCT, depth=0.150 - Y_BREECH, loc=(0, (Y_BREECH + 0.150) / 2, BZ),
                rot=(-90, 22.5, 0), verts=8, material=M("iron")))
g.s(ycyl("breech_ring", R_OCT + 0.0012, 0.149, 0.158, z=BZ, verts=16, mat="gold"))
g.s(ycyl("barrel", R_B0, 0.156, Y_MUZ - 0.006, z=BZ, verts=20, r2=R_MUZ + 0.0001, mat="iron"))
g.s(tube("muzzle", R_MUZ, 0.0072, Y_MUZ - 0.0065, Y_MUZ, c=(0, BZ), verts=20, mat="iron"))
g.f(ycyl("bore", 0.0072, Y_MUZ - 0.020, Y_MUZ - 0.004, z=BZ, verts=12, mat="dark"))
# 약실 꼬리(탱, 금): 손목 윗면을 따라 뒤로 + 나사
tang = [(0.0, yy, fkey(TOP, yy) + 0.0010) for yy in (0.068, 0.050, 0.030, 0.012, -0.006, -0.024)]
g.s(sweep("tang", tang, rrect(0.012, 0.0028, 0.0012, 1), mat="gold", scales=lambda u: (lerp(1.0, 0.55, u), 1.0)))
g.f(zcyl("tang_screw", 0.0026, fkey(TOP, 0.004) + 0.0022, fkey(TOP, 0.004) + 0.0032, y=0.004, mat="iron"))
# 점화구 (오른쪽, 팬 옆)
FLAT = R_OCT * math.cos(math.radians(22.5))
g.f(xcyl("touch_hole", 0.0012, FLAT - 0.0004, FLAT + 0.0008, y=0.113, z=BZ - 0.002, verts=8, mat="dark"))

# 총열 띠 (금): 개머리를 감싸는 띠 2개 + 총열·꽂을대를 함께 묶는 위 띠
for nm, yb in (("band_rear", 0.240), ("band_mid", 0.395)):
    a, zc, b, p = stock_at(yb)
    top = BZ + rb(yb) + 0.0016
    bot = zc - b - 0.0015
    g.s(sup_ring(nm, yb - 0.006, yb + 0.006, a + 0.0018, (top + bot) / 2, (top - bot) / 2, 2.7, inset=0.0024))
    # 띠 윗면의 뾰족 장식 (PV에서 띠가 총열 위로 솟아 보이는 부분)
    g.s(side(f"{nm}_crest", [(yb - 0.006, top - 0.002), (yb + 0.006, top - 0.002), (yb + 0.0015, top + 0.0050),
                             (yb - 0.0015, top + 0.0050)], 0.0045, bevel=0.0008, seg=1, mat="gold"))
# 멜빵 고리 (가운데 띠 아래, 개머리 아래)
zsw = stock_at(0.395)[1] - stock_at(0.395)[2]
g.s(torus("swivel_front", 0.0060, 0.0013, (0, 0.395, zsw - 0.0100), rot=(0, 90, 0), seg=10, rseg=4, mat="gold"))
g.s(cb.box("swivel_base_f", size=(0.0040, 0.0090, 0.0050), loc=(0, 0.395, zsw - 0.0030), material=M("gold")))
g.s(torus("swivel_rear", 0.0064, 0.0013, (0, -0.205, fkey(BOT, -0.205) - 0.0095), rot=(0, 90, 0), seg=10, rseg=4,
          mat="gold"))
g.s(cb.box("swivel_base_r", size=(0.0040, 0.0090, 0.0050), loc=(0, -0.205, fkey(BOT, -0.205) - 0.0030),
           material=M("gold")))

UB = (0.590, 0.608)
ub_top, ub_bot = BZ + R_MUZ + 0.0014, RR_Z - RR_R - 0.0014
g.s(sup_ring("band_upper", UB[0], UB[1], R_MUZ + 0.0016, (ub_top + ub_bot) / 2, (ub_top - ub_bot) / 2, 2.3,
             inset=0.0030))
g.f(sup_ring("band_upper_groove", 0.5985, 0.5995, R_MUZ + 0.0019, (ub_top + ub_bot) / 2, (ub_top - ub_bot) / 2 + 0.0003,
             2.3, inset=0.0012, mat="gold_d"))

# ================================================================== 가늠쇠·가늠자 (정조준선 SZ)
FS_Y = 0.650
fs_base = BZ + rb(FS_Y) - 0.0020
# 가늠쇠: 어두운 쇠 날 (금색 소켓·하늘 앞에서 읽히게) + 금 받침
g.s(cb.box("front_sight", size=(0.0042, 0.010, SZ - fs_base), loc=(0, FS_Y, (SZ + fs_base) / 2),
           bevel=0.0008, bevel_segments=1, material=M("iron")))
g.s(cb.box("front_sight_base", size=(0.0062, 0.016, 0.0040), loc=(0, FS_Y, BZ + R_MUZ + 0.0036),
           bevel=0.0010, bevel_segments=1, material=M("gold")))
RS_Y = 0.090
oct_top = BZ + FLAT
NOTCH = SZ - 0.0060     # 가늠자 홈 바닥: 조준선보다 조금 낮아 홈 안에 가늠쇠가 보인다
g.s(cb.box("rear_sight_base", size=(0.0210, 0.0085, NOTCH - oct_top + 0.001),
           loc=(0, RS_Y, (NOTCH + oct_top - 0.001) / 2), bevel=0.0008, bevel_segments=1, material=M("gold")))
for sx in (1, -1):
    g.s(cb.box(f"rear_sight_ear{sx}", size=(0.0056, 0.0085, SZ + 0.0016 - NOTCH + 0.0006),
               loc=(sx * 0.0074, RS_Y, (SZ + 0.0016 + NOTCH - 0.0006) / 2), bevel=0.0008, bevel_segments=1,
               material=M("gold")))

# ================================================================== 자물쇠 (오른쪽, 플린트록)
PL_T = 0.0024


def x_plate(y, z):
    return x_surf(y, z) + PL_T


# 판 윤곽 (뒤 끝은 손목 높이까지 내려온다). 개머리 위·아래 모서리에서 5 mm 안쪽으로 제한한다
LOCK_TOP = [(-0.006, 0.0140), (0.010, 0.0200), (0.030, 0.0290), (0.050, 0.0405), (0.080, 0.0472), (0.120, 0.0478),
            (0.145, 0.0455), (0.157, 0.0408)]
LOCK_BOT = [(-0.006, 0.0140), (0.010, 0.0080), (0.030, 0.0110), (0.050, 0.0195), (0.080, 0.0270), (0.120, 0.0290),
            (0.145, 0.0330), (0.157, 0.0408)]


def plate_fns(tab_top, tab_bot, margin=0.005):
    def zt(y_):
        return min(fkey(tab_top, y_), fkey(TOP, y_) - margin)

    def zb(y_):
        return min(max(fkey(tab_bot, y_), fkey(BOT, y_) + margin), zt(y_))
    return zt, zb


ys_l = [lerp(-0.006, 0.157, i / 24) for i in range(25)]
g.i(band_relief("lock_plate", ys_l, *plate_fns(LOCK_TOP, LOCK_BOT), 1, lift=PL_T))
# 자물쇠판 각인선 (짙은 금)
g.i(relief("lock_line", strip(catmull2([(0.014, 0.0180), (0.045, 0.0340), (0.085, 0.0440), (0.135, 0.0446)], 4),
                              0.0011), 1, lift=PL_T + 0.0003, mat="gold_d"))
g.i(relief("lock_line2", strip(catmull2([(0.016, 0.0115), (0.060, 0.0228), (0.110, 0.0302), (0.142, 0.0340)], 4),
                               0.0011), 1, lift=PL_T + 0.0003, mat="gold_d"))
for yy, zz in ((0.008, 0.0140), (0.146, 0.0400)):
    xx = x_plate(yy, zz)
    g.f(xcyl(f"lock_screw{yy}", 0.0024, xx - 0.0003, xx + 0.0008, y=yy, z=zz, verts=10, mat="iron"))

# 팬 (화약 접시)과 불막이
PAN_Y = (0.103, 0.124)
PAN_X = max(x_plate(0.113, 0.047), FLAT + 0.0010)
g.s(side("pan", rrect(PAN_Y[1] - PAN_Y[0], 0.0060, 0.0022, 2, (PAN_Y[0] + PAN_Y[1]) / 2, 0.0470), 0.0095,
         x=PAN_X + 0.0035, bevel=0.0008, seg=1, mat="gold"))
g.s(side("pan_fence", rrect(0.0025, 0.0115, 0.0008, 1, PAN_Y[0] - 0.0005, 0.0508), 0.0090, x=PAN_X + 0.0030,
         bevel=0.0005, seg=1, mat="gold"))
# 부시 용수철 (앞, 정지)
g.s(side("frizzen_spring", strip(catmull2([(0.126, 0.0388), (0.138, 0.0352), (0.152, 0.0372)], 4), 0.0032,
                                 lambda u: 1 - 0.4 * u), 0.0030, x=x_plate(0.14, 0.037) + 0.0012, mat="gold"))

# ---- 공이 (코크): 백조 목 + 위아래 턱 + 부싯돌 + 턱나사 + 뒤 소용돌이. 원점 = 텀블러 축
HM = (x_plate(0.050, 0.036) + 0.0024, 0.050, 0.036)
hx = HM[0]
hm = []
hm.append(xcyl("hm_hub", 0.0064, hx - 0.0026, hx + 0.0016, y=HM[1], z=HM[2], verts=12, mat="gold"))
neck = catmull2([(0.051, 0.039), (0.0455, 0.0465), (0.0445, 0.0545), (0.0485, 0.0610), (0.0545, 0.0640)], 4)
hm.append(side("hm_neck", strip(neck, 0.0068, lambda u: 1 - 0.25 * math.sin(math.pi * u)), 0.0042, x=hx,
               bevel=0.0009, seg=1, mat="gold"))
hm.append(side("hm_curl", strip(spiral(0.0390, 0.0505, 0.0060, 0.0018, 350, 1.05, sgn=1), 0.0028,
                                lambda u: 1 - 0.5 * u), 0.0032, x=hx, mat="gold"))
hm.append(side("hm_jaw_lo", rrect(0.0150, 0.0046, 0.0016, 2, 0.0590, 0.0650), 0.0052, x=hx, bevel=0.0007, seg=1,
               mat="gold"))
hm.append(side("hm_jaw_up", rrect(0.0135, 0.0042, 0.0015, 2, 0.0595, 0.0748), 0.0050, x=hx, bevel=0.0007, seg=1,
               mat="gold"))
hm.append(side("hm_flint", [(0.0545, 0.0680), (0.0700, 0.0688), (0.0745, 0.0702), (0.0700, 0.0718),
                            (0.0545, 0.0724)], 0.0062, x=hx, mat="flint"))
hm.append(zcyl("hm_screw", 0.0017, 0.0630, 0.0835, x=hx, y=0.0565, verts=8, mat="iron"))
hm.append(cb.sphere("hm_knob", radius=0.0035, loc=(hx, 0.0565, 0.0842), segments=10, rings=6,
                    scale=(1, 1, 0.75), material=M("gold")))
g.p("hammer", *hm)
g.pf("hammer", xcyl("hm_hub_screw", 0.0030, hx + 0.0016, hx + 0.0022, y=HM[1], z=HM[2], verts=10, mat="iron"))
g.pivot("hammer", HM, rotAxis="x", rotDeg="0,-18,-44", note="FULL/HALF/FIRED (기본 = 장전된 full cock)")

# ---- 부시 (프리즌): 팬 덮개 + 타격면. 원점 = 앞 경첩
FZ = (PAN_X + 0.0035, 0.1275, 0.0444)
fz = []
fz.append(side("fz_cover", rrect(0.0235, 0.0034, 0.0012, 2, 0.1150, 0.0514), 0.0098, x=FZ[0], bevel=0.0006, seg=1,
               mat="gold"))
face = catmull2([(0.1055, 0.0522), (0.1040, 0.0612), (0.1015, 0.0702), (0.0990, 0.0757)], 3)
fz.append(side("fz_face", strip(face, 0.0042), 0.0090, x=FZ[0], bevel=0.0006, seg=1, mat="gold"))
strike = side("fz_strike", strip(face[1:], 0.0016), 0.0072, x=FZ[0], mat="flint")
xform(strike, loc=(0, -0.0025, 0))
fz.append(strike)
fz.append(xcyl("fz_hinge", 0.0028, FZ[0] - 0.0050, FZ[0] + 0.0050, y=FZ[1], z=FZ[2], verts=10, mat="gold"))
fz.append(side("fz_toe", rrect(0.0060, 0.0080, 0.0020, 2, 0.1255, 0.0482), 0.0060, x=FZ[0], mat="gold"))
g.p("frizzen", *fz)
g.pivot("frizzen", FZ, rotAxis="x", rotDeg="0,-68", note="CLOSED/OPEN (격발 때 공이에 맞아 앞으로 젖혀진다)")

# ================================================================== 왼쪽 곁판 (금, 1인칭에서 보이는 면) + 작은 엠블럼
SP_TOP = [(-0.010, 0.0105), (0.006, 0.0170), (0.030, 0.0280), (0.067, 0.0428), (0.100, 0.0415), (0.126, 0.0386),
          (0.140, 0.0332)]
SP_BOT = [(-0.010, 0.0105), (0.006, 0.0050), (0.030, 0.0090), (0.067, 0.0230), (0.100, 0.0245), (0.126, 0.0272),
          (0.140, 0.0332)]
ys_s = [lerp(-0.010, 0.140, i / 24) for i in range(25)]
g.i(band_relief("side_plate", ys_s, *plate_fns(SP_TOP, SP_BOT), -1, lift=0.0016))
g.i(vine("side_plate_curl", spiral(-0.0158, 0.0058, 0.0058, 0.0020, 70, 1.0, sgn=1), -1, w=0.0026, lift=0.0016))
for yy, zz in ((0.012, 0.0110), (0.122, 0.0330)):
    xx = -(x_surf(yy, zz) + 0.0016)
    g.f(xcyl(f"sp_screw{yy}", 0.0022, xx - 0.0008, xx + 0.0004, y=yy, z=zz, verts=10, mat="iron"))
    g.f(cb.box(f"sp_screw_slot{yy}", size=(0.0004, 0.0036, 0.0008), loc=(xx - 0.0009, yy, zz), rot=(35, 0, 0),
               material=M("dark")))
EM_S = (0.067, 0.0330)
g.i(relief("sp_emblem_disc", ellipse(EM_S[0], EM_S[1], 0.0104, 0.0076, 18), -1, lift=0.0024, mat="green",
           fan=True))
g.i(relief_ring("sp_emblem_rim", EM_S[0], EM_S[1], 0.0110, 0.0082, 0.0013, -1, lift=0.0030, n=16))
g.i(*butterfly("sp_bf", EM_S[0], EM_S[1] - 0.0003, 0.0082, -1, lift=0.0032, strokes=False))

# ================================================================== 개머리 왼쪽 큰 엠블럼 (3인칭용)
EM_B = (-0.222, -0.0140)
g.i(relief("emblem_disc", ellipse(EM_B[0], EM_B[1], 0.0290, 0.0225, 24), -1, lift=0.0010, mat="green", fan=True))
g.i(relief_ring("emblem_rim", EM_B[0], EM_B[1], 0.0305, 0.0240, 0.0028, -1, lift=0.0016))
g.i(*butterfly("emblem_bf", EM_B[0], EM_B[1] - 0.0008, 0.0220, -1, lift=0.0020))

# ================================================================== 금 덩굴 (세계수 잎: 오리지널 문양)
FZC = stock_at(0.35)[1]


def fore_vine(sgn):
    out = []
    y0, y1 = 0.168, 0.505
    path = [(yy, FZC + 0.0005 + 0.0036 * math.sin(2 * math.pi * (yy - y0) / 0.112))
            for yy in [y0 + (y1 - y0) * i / 30 for i in range(31)]]
    out.append(vine(f"fv{sgn}", path, sgn, w=0.0030, taper=lambda u: 1.0 - 0.35 * u))
    # 잎: 물결 마루마다 앞쪽(총구)으로 불꽃처럼 뻗는다 (PV의 앞으로 향한 금색 잎 무늬)
    for k in range(6):
        yy = y0 + 0.028 + k * 0.056
        up = 1 if k % 2 == 0 else -1
        zz = FZC + 0.0005 + up * 0.0036
        ln = 0.024 - 0.0014 * k
        out.append(relief(f"fl{sgn}_{k}", lens((yy - 0.002, zz), (yy + ln * 0.87, zz + up * ln * 0.46), 0.0090), sgn,
                          lift=0.0008, mat="gold", fan=True))
        if k in (1, 3):   # 작은 덩굴손
            out.append(vine(f"ft{sgn}_{k}", spiral(yy + 0.017, zz - up * 0.0062, 0.0040, 0.0013,
                                                   90 if up > 0 else 270, 0.85, sgn=-up), sgn, w=0.0017))
    out.append(vine(f"fs{sgn}", spiral(y0 - 0.0040, FZC + 0.0025, 0.0066, 0.0022, 270, 1.1, sgn=1), sgn, w=0.0028))
    return out


def butt_vine(sgn):
    out = []
    pts = []
    for i in range(23):
        yy = lerp(-0.082, -0.318, i / 22)
        pts.append((yy, fkey(BOT, yy) + 0.0175 + 0.0032 * math.sin(2 * math.pi * (yy + 0.082) / 0.090)))
    out.append(vine(f"bv{sgn}", pts, sgn, w=0.0030, taper=lambda u: 1.0 - 0.3 * u))
    for k in range(4):
        yy = -0.105 - k * 0.0450
        zz = fkey(BOT, yy) + 0.0175 + 0.0032 * math.sin(2 * math.pi * (yy + 0.082) / 0.090)
        up = 1 if k % 2 == 0 else -1
        out.append(relief(f"bl{sgn}_{k}", lens((yy + 0.002, zz), (yy - 0.020, zz + up * 0.0100), 0.0085), sgn,
                          lift=0.0008, mat="gold", fan=True))
    out.append(vine(f"be{sgn}", spiral(-0.3260, fkey(BOT, -0.326) + 0.0255, 0.0076, 0.0024, 300, 1.15, sgn=1), sgn,
                    w=0.0029))
    out.append(vine(f"bc{sgn}", spiral(-0.074, 0.0055, 0.0062, 0.0020, 200, 1.0, sgn=-1), sgn, w=0.0024))
    return out


for s_ in (1, -1):
    g.i(*fore_vine(s_))
    g.i(*butt_vine(s_))

# ================================================================== 각인 (약실 왼쪽·오른쪽 평면)
def text(name, s, size, center, *, right, up, mat="gold", font="/System/Library/Fonts/Supplemental/AppleGothic.ttf"):
    cu = bpy.data.curves.new(name + "_crv", "FONT")
    cu.body = s
    if os.path.exists(font):
        try:
            cu.font = bpy.data.fonts.load(font, check_existing=True)
        except Exception:  # noqa: BLE001
            pass
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 1
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    cb.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    o = bpy.data.objects.new("decal_" + name, me)
    cb.link(o)
    R, U = V(right).normalized(), V(up).normalized()
    N = R.cross(U).normalized()
    m4 = Matrix((R, U, N)).transposed().to_4x4()
    m4.translation = V(center) + N * 0.0003
    o.matrix_world = m4
    cb.assign(o, M(mat))
    return o


# 약실 팔각의 위 비스듬한 면 (1인칭에서 내려다보이는 면)
D45 = math.sqrt(0.5)
g.f(text("mk_erpien", "에르피엔 경비대", 0.0050, (-FLAT * D45, 0.124, BZ + FLAT * D45), right=(0, -1, 0),
         up=(D45, 0, D45)))
g.f(text("mk_serial", "No.120", 0.0052, (FLAT * D45, 0.124, BZ + FLAT * D45), right=(0, 1, 0), up=(-D45, 0, D45),
         font="/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"))

# ================================================================== 방아쇠울 (금) + 방아쇠
tg = spiral(-0.0890, fkey(BOT, -0.089) - 0.0045, 0.0042, 0.0012, 40, 0.8, n=6, sgn=-1)[::-1]
tg += [(yy, fkey(BOT, yy) - 0.0014) for yy in (-0.080, -0.060, -0.040, -0.020)]
tg += catmull2([(-0.010, -0.0225), (-0.002, -0.0300), (0.006, -0.0420), (0.020, -0.0510), (0.038, -0.0535),
                (0.055, -0.0480), (0.066, -0.0350), (0.072, -0.0215)], 3)[1:]
tg += [(yy, fkey(BOT, yy) - 0.0014) for yy in (0.082, 0.100, 0.118)]
g.s(sweep("trigger_guard", [(0.0, yy, zz) for yy, zz in tg], rrect(0.0085, 0.0032, 0.0012, 1), mat="gold",
          scales=lambda u: (lerp(0.75, 1.0, min(1.0, u * 3)), 1.0)))
TRIG = (0.0, 0.030, -0.0160)
trig = side("trigger_blade", strip(catmull2([(0.0300, -0.0150), (0.0335, -0.0270), (0.0365, -0.0370),
                                             (0.0335, -0.0440)], 4), 0.0044, lambda u: 1 - 0.35 * u), 0.0044,
            bevel=0.0008, seg=1, mat="gold")
g.p("trigger", trig)
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-14)

# ================================================================== 꽂을대 (총열 아래, 앞으로 뽑는다)
RR = (0.0, 0.618, RR_Z)
rr = [ycyl("rr_rod", RR_R, 0.070, 0.611, z=RR_Z, verts=10, mat="iron"),
      ycyl("rr_head", RR_R + 0.0002, 0.608, 0.6205, z=RR_Z, r2=0.0068, verts=14, mat="gold"),
      cb.sphere("rr_tip", radius=0.0068, loc=(0, 0.6205, RR_Z), segments=14, rings=6, scale=(1, 0.45, 1),
                material=M("gold"))]
g.p("ramrod", *rr)
g.pivot("ramrod", RR, move=mv(0, 0.52, 0), note="앞으로 뽑아 총구로 다져 넣고 되꽂는다")

# ================================================================== 소켓 총검 (금, 따로 떼어 낼 수 있다)
BAY = (0.0, 0.655, BZ)
S_IN, S_OUT = R_MUZ + 0.0004, R_MUZ + 0.0023
BX, BZB = 0.0062, BZ - 0.0300       # 날 중심선 (총열 아래 오른쪽)
bay = []
bay.append(tube("bay_socket", S_OUT, S_IN, 0.630, 0.679, c=(0, BZ), verts=16, mat="gold"))
bay.append(torus("bay_ring", S_OUT + 0.0001, 0.0018, (0, 0.6335, BZ), rot=(90, 0, 0), seg=14, rseg=5, mat="gold"))
bay.append(torus("bay_ring2", S_OUT + 0.0001, 0.0014, (0, 0.6765, BZ), rot=(90, 0, 0), seg=14, rseg=4, mat="gold"))
neck = [(0.0030, 0.665, BZ - S_OUT + 0.0012), (0.0052, 0.6705, BZ - 0.0195), (0.0060, 0.6785, BZ - 0.0262),
        (0.0062, 0.6880, BZ - 0.0292)]
bay.append(sweep("bay_neck", neck, ellipse(0, 0, 0.0036, 0.0032, 8), mat="gold"))
bay.append(cb.box("bay_shoulder", size=(0.0076, 0.0110, 0.0190), loc=(BX, 0.6930, BZB), bevel=0.0018,
                  bevel_segments=1, material=M("gold")))
# 날: 넓은 면이 옆을 향하는 육각 단면 (옆에서 보면 칼날 모양), 끝 28%에서 뾰족해진다
B0, B1 = 0.697, 0.950
bm = bmesh.new()
rings = []
for i in range(17):
    u = i / 16
    yy = lerp(B0, B1, u)
    tip = clamp((1 - u) / 0.28)
    h = max(0.0088 * (1 - 0.18 * u) * (tip ** 0.75 if u > 0.72 else 1.0), 0.00025)
    t = max(0.0032 * (1 - 0.3 * u) * (tip ** 0.6 if u > 0.72 else 1.0), 0.0002)
    sec = [(0, h), (t, 0.45 * h), (t, -0.45 * h), (0, -h), (-t, -0.45 * h), (-t, 0.45 * h)]
    rings.append([bm.verts.new((BX + x, yy, BZB + z)) for x, z in sec])
for i in range(len(rings) - 1):
    for j in range(6):
        j2 = (j + 1) % 6
        bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
bm.faces.new(list(reversed(rings[0])))
bm.faces.new(rings[-1])
bay.append(_obj("bay_blade", bm, "gold", smooth=30))
g.p("bayonet", *bay)
# 날 홈 (짙은 금, 양면) + 소켓 홈
for sx in (1, -1):
    pts = [(lerp(0.705, 0.880, i / 8), BZB) for i in range(9)]
    # 날 옆면 x = BX ± t(y) → relief 규약(sgn × xs)에 맞춘 xs = t(y) + sx·BX
    g.pf("bayonet", relief(f"bay_fuller{sx}", strip(pts, 0.0026, lambda u: 1 - 0.5 * u ** 2), sx, lift=0.00025,
                           sink=0.0003, mat="gold_d",
                           xs=lambda y_, z_, sx=sx: 0.0032 * (1 - 0.3 * (y_ - B0) / (B1 - B0)) + sx * BX))
g.pf("bayonet", cb.box("bay_slot", size=(0.0024, 0.018, 0.0008), loc=(0.0, 0.640, BZ + S_OUT), material=M("dark")))
g.pivot("bayonet", BAY, move=mv(0, 0.07, 0), detachable=1, note="소켓을 돌려 풀고 앞으로 뺀다")

# ================================================================== 앵커
g.anchor("muzzle", (0, Y_MUZ, BZ))
g.anchor("grip_support", (0, 0.275, stock_at(0.275)[1]))
g.anchor("sight_eye", (0, -0.085, SZ))
g.anchor("pan", (PAN_X + 0.0035, 0.113, 0.0525))
g.anchor("eject", (PAN_X + 0.0035, 0.113, 0.0525))     # 머스킷: 팬 점화 연기 분출점
g.anchor("mag_well", (0, Y_MUZ, BZ))                    # 전장식: 장전점 = 총구
g.anchor("bayonet_tip", (BX, B1, BZB), parent="bayonet")

g.finish("weapons/fairy/fairy_guard_musket.glb", outline=0.0018, inlay_outline=0.0007,
         fp="0.12,-0.15,-0.22", fprot="0,-2,0",
         extra={"loading": "muzzle", "capacity": 1})
