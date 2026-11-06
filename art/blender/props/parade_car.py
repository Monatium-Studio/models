"""대관식 퍼레이드 오픈카 (props/parade_car.glb). 에필로그, 에르핀의 세 번째 대관식 뒤 에르피엔 시가 행진.

npm run model -- art/blender/props/parade_car.py
npm run shot -- props/parade_car.glb --views front,34,side,top
PC_PREVIEW=1 npm run model -- art/blender/props/parade_car.py   → props/parade_car_preview.glb (인물 크기 비교, 커밋 안 함)

[오리지널] 요정 왕실 의전차. 실존 차량을 옮기지 않았다. 크림색 차체에 금색 몰딩과 덩굴 소용돌이, 왕실 붉은 좌석(#bb3440),
          요정 경비대 초록(#2f6a4f) 포인트,
          분홍·흰 꽃 장식줄, 금색 살 바퀴(흰 띠 타이어). 엘프 기술은 보닛 장식의 수액빛 보석과 계기판 발광 화면 정도로만 넣었다.
[원작] 앞 펜더의 작은 깃발 둘 = 에르피엔 군기 (lib/erpien_flag.py, 사용자 결정 2026-11-02): 금 깃대, 뒤로 날린다.
      문·그릴·꽁무니 메달과 보닛 장식의 나비도 그 군기의 나비다 (erpien_flag.badge).
배치: 앞 운전석(벤치, 바닥 0.55 m) + 뒤 기립 단상(바닥 0.75 m, 낮은 장식 난간 +0.5 m). 서 있는 SD 인물(1.2 m)은
      거리에서 허리 위가 보인다.

규약 (차량과 같음, docs/art/VEHICLES.md): Blender Z-up, 1 BU = 1 m, 정면 -Y, 차의 왼쪽 = +X,
      원점 = 지면, 앞뒤 차축 가운데(x=0). 이 glb는 코드가 움직이는 컷신 소품이고 운전 물리는 없다.
노드
  body_<머티리얼>[_d|_f]   정지 메시 (_d = 얇은 아웃라인, _f = 아웃라인 없음)
  wheel_FL/FR/RL/RR       바퀴 메시. 원점 = 바퀴 중심, 차축 = 로컬 X (로컬 X 회전으로 굴린다). radius, steer
  stand_1, stand_2        뒤 단상 위 기립 인물의 발 위치 (-Y를 봄). stand_1 = 왼쪽(+X, 여왕), stand_2 = 오른쪽
  seat_driver             앞 벤치 운전수의 발/루트 위치 (바닥). seatZ = 그 점 위 좌석 윗면 높이
  flag_L, flag_R          앞 펜더 깃발 깃대 끝
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import cb  # noqa: E402
import erpien_flag as ef  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
PREVIEW = os.environ.get("PC_PREVIEW") == "1"
NAME = "parade_car"

# ================================================================== 치수
R, TW = 0.38, 0.20            # 바퀴 반지름, 타이어 폭
XW = 0.79                     # 바퀴 중심 x (윤거 1.58)
YF, YR = -1.38, 1.38          # 앞뒤 차축 (축거 2.76)
BW = 0.62                     # 차체(욕조) 반폭
WALL = 0.075                  # 벽 두께 → 안쪽 반폭 0.545
XI = BW - WALL
FLOOR = 0.55                  # 앞 운전석 바닥
DECK = 0.75                   # 뒤 단상 바닥
RAIL = DECK + 0.50            # 난간 윗선
CAB_Y0, CAB_Y1 = -0.90, 0.0   # 운전석 칸 (앞 계기판 벽 ~ 칸막이)
PLT_Y0 = 0.10                 # 단상 앞 벽
STERN_Y, STERN_RY = 1.75, 0.32
SEAT_TOP = FLOOR + 0.32       # 벤치 윗면
SEAT_FRONT = -0.47

# ================================================================== 팔레트
PAL = {
    "cream": "#f4ecda",     # 차체
    "gold": "#e8c178",      # 금 몰딩·바퀴 (요정 경비대 금과 같은 값)
    "gold_d": "#c49448",    # 부조 소용돌이 (크림 위에서 읽히게 어둡게)
    "red": "#bb3440",       # 왕실 붉은 가죽 (좌석, 안쪽 벽)
    "carpet": "#8e2633",    # 바닥 카펫
    "green": "#2f6a4f",     # 요정 경비대 초록 (문장 바탕, 발판, 그릴)
    "rubber": "#2f2a31",
    "chassis": "#3a3439",
    "white": "#fbf8f2",     # 흰 띠 타이어, 흰 꽃
    "pink": "#f2a7c3",
    "pink_d": "#e07fa5",
    "leaf": "#5fae6a",
    "leaf_d": "#468f57",
    "yellow": "#f6dc6e",
    **ef.PAL,               # 에르피엔 군기 (펜더 깃발)
}
LINE = "#4a2229"
LINES = {"gold": "#7a4f24", "gold_d": "#6a4320", "red": "#4a1018", "carpet": "#3a0c14", "green": "#15302a",
         "rubber": "#140c10", "chassis": "#140c10", "leaf": "#2b5a33", "leaf_d": "#22492a", "pink": "#9a4060",
         "pink_d": "#8a3050", "white": "#8a6a5a", "yellow": "#8a6a20", "erf_green": "#15302a", "erf_gold": "#6a4320"}
GLOW = {"jewel": "#a6f5da", "lamp": "#fff1c9", "tail": "#ff8a7a", "screen": "#7ff0d0"}
ALPHA = {"glass": ("#d6eef2", 0.25)}
_M = {}


def M(key):
    m = _M.get(key)
    if m is None:
        if key in GLOW:
            m = cb.mat(f"pc_{key}", GLOW[key], emission=GLOW[key], unlit=True)
        elif key in ALPHA:
            c, a = ALPHA[key]
            m = cb.mat(f"pc_{key}", c, emission=c, unlit=True, alpha=a)
        else:
            m = cb.mat(f"pc_{key}", PAL[key], line=LINES.get(key, LINE), roughness=0.6)
        _M[key] = m
    return m


# ================================================================== 누적기 (머티리얼·종류별 bmesh 하나)
ACC: dict = {}
OBJS: list = []
OUTLINE, DETAIL = 0.008, 0.0045


def _kind(key, kind):
    return "fine" if (key in GLOW or key in ALPHA) else kind


def B(key, kind="main"):
    k = (key, _kind(key, kind))
    if k not in ACC:
        ACC[k] = bmesh.new()
    return ACC[k]


def put(key, o, kind="main"):
    if isinstance(o, (list, tuple)):
        for x in o:
            put(key, x, kind)
        return None
    if o is not None:
        OBJS.append((key, _kind(key, kind), o))
    return o


def put_bm(key, src, kind="main"):
    me = bpy.data.meshes.new("tmp_put")
    src.to_mesh(me)
    src.free()
    B(key, kind).from_mesh(me)
    bpy.data.meshes.remove(me)


def bake_objs():
    dg = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    for key, kind, o in OBJS:
        eo = o.evaluated_get(dg)
        me = eo.to_mesh()
        me.transform(o.matrix_world)
        B(key, kind).from_mesh(me)
        eo.to_mesh_clear()
    for _, _, o in OBJS:
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)
    OBJS.clear()


# ================================================================== 작은 기하
def hermite(keys, y):
    """(y, 값) 키를 부드럽게 잇는다 (양 끝 기울기 0)."""
    n = len(keys)
    if y <= keys[0][0]:
        return keys[0][1]
    if y >= keys[-1][0]:
        return keys[-1][1]
    i = max(k for k in range(n - 1) if keys[k][0] <= y)

    def slope(k):
        if k == 0 or k == n - 1:
            return 0.0
        return (keys[k + 1][1] - keys[k - 1][1]) / (keys[k + 1][0] - keys[k - 1][0])
    (y0, v0), (y1, v1) = keys[i], keys[i + 1]
    h = y1 - y0
    t = (y - y0) / h
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * v0 + (t3 - 2 * t2 + t) * h * slope(i) + (-2 * t3 + 3 * t2) * v1
            + (t3 - t2) * h * slope(i + 1))


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append(tuple(a * p0[k] + b * p1[k] + c * p2[k] + d * p3[k] for k in range(len(p0))))
    return out


def ellipse(cx, cy, rx, ry, n=14, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def rot2(pts, deg, cx=0.0, cy=0.0):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                inside = not inside
    return inside


def plate_ru(key, pts2d, center, Rv, Uv, depth, *, kind="detail", back=0.002):
    """평면 (R, U) 위 2D 외곽선을 법선 R x U 방향으로 depth만큼 세운 판."""
    Rv, Uv = Vector(Rv).normalized(), Vector(Uv).normalized()
    N = Rv.cross(Uv).normalized()
    c = Vector(center)
    b = B(key, kind)
    f0 = [b.verts.new(c + Rv * u + Uv * v - N * back) for u, v in pts2d]
    f1 = [b.verts.new(c + Rv * u + Uv * v + N * (depth - back)) for u, v in pts2d]
    faces = [b.faces.new(list(reversed(f0))), b.faces.new(f1)]
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        faces.append(b.faces.new((f0[i], f0[j], f1[j], f1[i])))
    bmesh.ops.recalc_face_normals(b, faces=faces)


def plate(key, pts2d, center, normal, depth, *, up=(0, 0, 1), kind="detail", back=0.002):
    Rv, Uv, _ = mk.frame(normal, up)
    plate_ru(key, pts2d, center, Rv, Uv, depth, kind=kind, back=back)


def decal(key, pts2d, center, normal, *, up=(0, 0, 1), lift=0.002):
    Rv, Uv, N = mk.frame(normal, up)
    c = Vector(center) + N * lift
    mk._bm_poly(B(key, "fine"), [c + Rv * u + Uv * v for u, v in pts2d], N)


def side_vec_for(path):
    """쓸기 기준축: 경로 접선과 가장 덜 나란한 축 (접선과 나란하면 단면이 비틀려 접힌다)."""
    P = [Vector(p) for p in path]
    T = [(b - a).normalized() for a, b in zip(P, P[1:]) if (b - a).length > 1e-6]
    best = min(((1, 0, 0), (0, 0, 1), (0, 1, 0)), key=lambda ax: max(abs(t.dot(Vector(ax))) for t in T))
    return best


def tube(key, path, r, *, verts=8, kind="detail", cap=True, side_vec=None):
    sec = [(math.cos(2 * math.pi * k / verts) * r, math.sin(2 * math.pi * k / verts) * r) for k in range(verts)]
    sv = side_vec or side_vec_for(path)
    put(key, hw.sweep("tube", path, sec, side_vec=sv, cap=cap, smooth=60), kind)


def cyl(key, p0, p1, r, *, segs=10, r2=None, kind="main"):
    mk._bm_cyl(B(key, kind), p0, p1, r, segs=segs, r2=r2)


def blob(key, c, r, scale=(1, 1, 1), *, segs=10, rings=6, kind="main"):
    mk._bm_blob(B(key, kind), c, r, scale, segs=segs, rings=rings)


def rbox(key, x0, x1, y0, y1, z0, z1, *, bevel=0.0, seg=2, kind="main", rot=None, pivot=None):
    o = cb.box("rb", size=(x1 - x0, y1 - y0, z1 - z0), loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               bevel=bevel, bevel_segments=seg)
    if rot:
        ve.rot_about([o], pivot or o.location, rot[0], rot[1])
    return put(key, o, kind)


def sides():
    return (1, -1)


# ================================================================== 차체 단면 (y마다 반폭·윗선·아랫선·모서리)
W_KEYS = [(-2.0, 0.47), (-1.75, 0.52), (-1.3, 0.58), (-0.95, BW), (-0.6, BW), (STERN_Y, BW)]
ZT_KEYS = [(-2.0, 0.77), (-1.6, 0.86), (-1.05, 0.95), (-0.9, 0.96), (-0.3, 0.945), (0.2, 0.905), (1.2, 0.87),
           (STERN_Y, 0.855), (2.07, 0.80)]
ZB_KEYS = [(-2.0, 0.40), (-1.7, 0.33), (-1.2, 0.30), (1.5, 0.30), (1.9, 0.34), (2.07, 0.44)]
RT_KEYS = [(-2.0, 0.15), (-1.05, 0.13), (-0.85, 0.06), (2.07, 0.06)]
RB = 0.09
Y_END = 2.065


def body_w(y):
    if y <= STERN_Y:
        return hermite(W_KEYS, y)
    return BW * math.sqrt(max(1 - ((y - STERN_Y) / STERN_RY) ** 2, 0.0))


def zt(y):
    return hermite(ZT_KEYS, y)


def zb(y):
    return hermite(ZB_KEYS, y)


def rt(y):
    return hermite(RT_KEYS, y)


def section(y, n=3):
    w, b, t = body_w(y), zb(y), zt(y)
    r_t = min(rt(y), w * 0.95, (t - b) * 0.48)
    r_b = min(RB, w * 0.95, (t - b) * 0.48)
    pts = []
    for (cx, cz, r, a0) in ((w - r_b, b + r_b, r_b, -90), (w - r_t, t - r_t, r_t, 0),
                            (-w + r_t, t - r_t, r_t, 90), (-w + r_b, b + r_b, r_b, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def surf_x(y, z):
    """높이 z에서 차체 옆면의 x (모서리 둥근 부분 반영)."""
    w, b, t = body_w(y), zb(y), zt(y)
    r_t = min(rt(y), w * 0.95, (t - b) * 0.48)
    r_b = min(RB, w * 0.95, (t - b) * 0.48)
    if z > t - r_t:
        return w - r_t + math.sqrt(max(r_t ** 2 - (z - (t - r_t)) ** 2, 0.0))
    if z < b + r_b:
        return w - r_b + math.sqrt(max(r_b ** 2 - (b + r_b - z) ** 2, 0.0))
    return w


def loft_body():
    ys = [-2.0, -1.975, -1.94, -1.89, -1.82]
    ys += [-1.72 + 0.1 * i for i in range(9)]                 # -1.72 .. -0.92
    ys += [-0.8 + 0.2 * i for i in range(13)]                 # -0.8 .. 1.6
    ys += [1.68, STERN_Y, 1.82, 1.88, 1.93, 1.97, 2.0, 2.025, 2.045, 2.058, Y_END]
    bm = bmesh.new()
    rings = []
    for y in ys:
        rings.append([bm.verts.new((x, y, z)) for x, z in section(y)])
    k = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(k):
            j = (i + 1) % k
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.smooth = True
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("body_loft")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("body_loft", me)
    cb.link(o)
    cb.smooth(o, angle=40)
    return o


def plat_outline():
    """뒤 단상 바닥 외곽 (반시계, 위에서 본 x, y)."""
    r = 0.06
    ry = Y_END - 0.075 - STERN_Y
    pts = [(0.0, PLT_Y0)]
    for i in range(4):
        a = math.radians(-90 + 90 * i / 3)
        pts.append((XI - r + r * math.cos(a), PLT_Y0 + r + r * math.sin(a)))
    for i in range(1, 16):
        a = math.radians(180 * i / 16)
        pts.append((XI * math.cos(a), STERN_Y + ry * math.sin(a)))
    for i in range(4):
        a = math.radians(180 + 90 * i / 3)
        pts.append((-XI + r + r * math.cos(a), PLT_Y0 + r + r * math.sin(a)))
    return pts


PLAT = plat_outline()


def in_cabin(p):
    return abs(p.x) < XI and CAB_Y0 < p.y < CAB_Y1 and p.z > FLOOR


def in_plat(p):
    return p.z > DECK and point_in_poly(p.x, p.y, PLAT)


def build_body():
    body = loft_body()
    cab = cb.profile_extrude("cut_cab", hw.rrect(2 * XI, CAB_Y1 - CAB_Y0, 0.07, n=3, cy=(CAB_Y0 + CAB_Y1) / 2),
                             1.2, axis="Z", loc=(0, 0, FLOOR + 0.6))
    ve.cut(body, cab)
    plt = cb.profile_extrude("cut_plt", PLAT, 1.2, axis="Z", loc=(0, 0, DECK + 0.6))
    ve.cut(body, plt)
    # 면 나누기: 바깥 = 크림, 칸 안쪽 벽 = 붉은 가죽, 바닥 = 카펫
    bm = bmesh.new()
    bm.from_mesh(body.data)
    groups = {}
    for f in bm.faces:
        c = f.calc_center_median()
        n = f.normal
        q = c + n * 0.01
        key = "cream"
        if in_cabin(q) or in_plat(q):
            key = "carpet" if n.z > 0.9 else "red"
        groups.setdefault(key, set()).add(f.index)
    for key, idx in groups.items():
        b2 = bm.copy()
        b2.faces.ensure_lookup_table()
        dele = [f for i, f in enumerate(b2.faces) if i not in idx]
        bmesh.ops.delete(b2, geom=dele, context="FACES")
        put_bm(key, b2, "main")
    bm.free()
    bpy.data.objects.remove(body, do_unlink=True)


build_body()

# 차대 (아래 그림자 줄) + 차축
rbox("chassis", -0.45, 0.45, -1.5, 1.6, 0.24, 0.31)
for y in (YF, YR):
    cyl("chassis", (-XW + 0.06, y, R), (XW - 0.06, y, R), 0.035, segs=8)

# ================================================================== 펜더 + 발판 (한 줄로 흐르는 쓸기)
RF = 0.46
RB_Z = 0.36


def fender_path():
    pts = []
    for i in range(11):
        th = math.radians(192 - (192 - 30) * i / 10)
        pts.append((YF + RF * math.cos(th), R + RF * math.sin(th)))
    p0 = pts[-1]
    th = math.radians(30)
    d = (math.sin(th), -math.cos(th))
    pts += bez(p0, (p0[0] + 0.13 * d[0], p0[1] + 0.13 * d[1]), (-0.82, RB_Z), (-0.60, RB_Z), 4)[1:]
    pts += [(0.0, RB_Z), (0.6, RB_Z)]
    th = math.radians(150)
    q3 = (YR + RF * math.cos(th), R + RF * math.sin(th))
    dq = (math.sin(th), -math.cos(th))
    pts += bez((0.6, RB_Z), (0.82, RB_Z), (q3[0] - 0.13 * dq[0], q3[1] - 0.13 * dq[1]), q3, 4)[1:]
    for i in range(1, 11):
        th = math.radians(150 - (150 + 12) * i / 10)
        pts.append((YR + RF * math.cos(th), R + RF * math.sin(th)))
    return pts


FPATH = fender_path()
FSEC = [(-0.20, -0.03), (0.17, -0.012), (0.177, 0.002), (0.172, 0.018), (0.13, 0.038), (0.05, 0.052),
        (-0.05, 0.048), (-0.14, 0.03), (-0.20, 0.004)]
FX = 0.78
for s in sides():
    path = [(s * FX, y, z) for y, z in FPATH]
    put("cream", hw.sweep("fender", path, [(u * s, v) for u, v in FSEC], side_vec=(1, 0, 0), cap=True, smooth=50))
    bead = [(s * (0.176 + 0.011 * math.cos(2 * math.pi * k / 5)), 0.006 + 0.011 * math.sin(2 * math.pi * k / 5))
            for k in range(5)]
    put("gold", hw.sweep("bead", path, bead, side_vec=(1, 0, 0), cap=True, smooth=60), "detail")
    # 발판 매트 (초록) + 금 테
    x0, x1 = sorted((s * 0.64, s * 0.92))
    rbox("green", x0, x1, -0.56, 0.56, RB_Z + 0.04, RB_Z + 0.064, bevel=0.008, seg=1, kind="detail")
    for xe in (0.64, 0.92):
        cyl("gold", (s * xe, -0.56, RB_Z + 0.062), (s * xe, 0.56, RB_Z + 0.062), 0.008, segs=5, kind="detail")
    # 앞바퀴 안쪽 막이 (보닛 옆과 펜더 사이 틈)
    liner = [(y, z - 0.012) for y, z in FPATH[:11]] + [(-0.95, 0.30), (-1.84, 0.30)]
    put("chassis", hw.side("liner", [(p[0], p[1]) for p in liner], 0.02, x=s * 0.575))

# ================================================================== 바퀴 (금 살 + 흰 띠 타이어)
WHEELS = []


def wheel(name, hub, steer):
    s = 1 if hub[0] > 0 else -1
    h = TW / 2
    parts = []
    rr = R * 0.70
    tire = [(rr, -h * 0.8), (R * 0.86, -h), (R * 0.97, -h * 0.8), (R, -h * 0.35), (R, h * 0.35), (R * 0.97, h * 0.8),
            (R * 0.86, h), (rr, h * 0.8)]
    parts.append(("rubber", ve.lathe(name + "_tire", tire, (0, 0, 0), axis="X", seg=22, smooth=50)))
    for sx in (s,):
        xo = sx * (h + 0.004)
        ww = [(0.282, xo), (0.338, xo), (0.338, xo - sx * 0.014), (0.282, xo - sx * 0.014)]
        parts.append(("white", ve.lathe(name + "_ww", ww, (0, 0, 0), axis="X", seg=22, smooth=50)))
    rim = [(0.276, -0.06), (0.276, 0.06), (0.248, 0.05), (0.248, -0.05)]
    parts.append(("gold", ve.lathe(name + "_rim", rim, (0, 0, 0), axis="X", seg=22, smooth=40)))
    hub_p = [(0.068, -0.07), (0.068, 0.07), (0.04, 0.07), (0.04, -0.07)]
    parts.append(("gold", ve.lathe(name + "_hub", hub_p, (0, 0, 0), axis="X", seg=12, smooth=40)))
    for sx in (s,):
        cap = [(0.074, sx * 0.068), (0.06, sx * 0.096), (0.03, sx * 0.111), (0.006, sx * 0.114)]
        parts.append(("gold", ve.lathe(name + "_cap", cap, (0, 0, 0), axis="X", seg=12, smooth=60, closed=False)))
    parts.append(("green", ve.lathe(name + "_gem", [(0.03, s * 0.112), (0.004, s * 0.122)],
                                    (0, 0, 0), axis="X", seg=8, smooth=60, closed=False)))
    n = 12
    for i in range(n):
        a = 2 * math.pi * i / n
        off = 0.045 if i % 2 == 0 else -0.045
        p0 = (off, math.cos(a) * 0.066, math.sin(a) * 0.066)
        a2 = a + math.radians(6 if i % 2 else -6)
        p1 = (0.0, math.cos(a2) * 0.252, math.sin(a2) * 0.252)
        parts.append(("gold", ve.bar(name + "_spoke", p0, p1, 0.0085, verts=5)))
    objs = []
    for key, o in parts:
        cb.assign(o, M(key))
        objs.append(o)
    w = cb.join(objs, name)
    w.location = hub
    w["radius"] = R
    w["width"] = TW
    w["steer"] = steer
    w["outline"] = 0.006
    WHEELS.append(w)


wheel("wheel_FL", (XW, YF, R), 1)
wheel("wheel_FR", (-XW, YF, R), 1)
wheel("wheel_RL", (XW, YR, R), 0)
wheel("wheel_RR", (-XW, YR, R), 0)

# ================================================================== 금 몰딩
ZM_OFF = 0.075


def belt_path():
    """허리 몰딩: 왼쪽 앞 → 왼쪽 옆 → 꼬리 곡선 → 오른쪽 옆 → 오른쪽 앞."""
    left = []
    ys = [-1.97 + 0.15 * i for i in range(25)] + [STERN_Y]
    for y in ys:
        if y > STERN_Y:
            continue
        z = zt(y) - ZM_OFF
        left.append((surf_x(y, z) + 0.003, y, z))
    stern = []
    for i in range(1, 16):
        a = math.radians(180 * i / 16)
        y = STERN_Y + (STERN_RY + 0.003) * math.sin(a)
        stern.append(((BW + 0.003) * math.cos(a), y, zt(min(y, Y_END)) - ZM_OFF))
    right = [(-x, y, z) for x, y, z in reversed(left)]
    return left + stern + right


tube("gold", belt_path(), 0.012, verts=5)
# 보닛 가운데 금줄 + 보닛 옆 통풍 띠
hood = [(0, y, zt(y) + 0.002) for y in [-1.985 + 0.1 * i for i in range(11)]]
put("gold", hw.sweep("hood_strip", hood, [(0.018, -0.004), (0.018, 0.004), (0.01, 0.009), (-0.01, 0.009),
                                          (-0.018, 0.004), (-0.018, -0.004)], side_vec=(1, 0, 0), cap=True,
                     smooth=30), "detail")
for s in sides():
    for k in range(3):
        z = 0.62 + k * 0.06
        y0, y1 = -1.36, -1.08
        pts = [(s * (surf_x(y, z) + 0.002), y, z) for y in (y0, (y0 + y1) / 2, y1)]
        tube("gold", pts, 0.008, verts=5)

# 운전석 칸 테두리 (금 코밍)
cab_rim = hw.rrect(2 * XI + 0.028, CAB_Y1 - CAB_Y0 + 0.028, 0.08, n=3, cy=(CAB_Y0 + CAB_Y1) / 2)
cab_path = [(x, y, zt(y) + 0.006) for x, y in cab_rim]
tube("gold", cab_path + cab_path[:1], 0.017, verts=6)

# ================================================================== 나비 문장 (에르피엔 군기의 나비)


def face_m(center, normal, up=(0, 0, 1), lift=0.0):
    """면 위 점에 erpien_flag 로컬(X = 면의 오른쪽, -Y = normal, Z = 위)을 놓는 행렬."""
    Rv, Uv, N = mk.frame(normal, up)
    M = Matrix((Rv, -N, Uv)).transposed().to_4x4()
    M.translation = Vector(center) + N * lift
    return M


def emblem(center, normal, size, *, up=(0, 0, 1)):
    """초록 타원판 + 금테 + 에르피엔 나비 부조 (lib/erpien_flag.badge: 군기와 같은 도안, 노란 바탕·금 윤곽선·말린 선)."""
    rx, ry = 0.60 * size, 0.47 * size
    plate("gold", ellipse(0, 0, rx, ry, 20), center, normal, 0.010, up=up)
    plate("green", ellipse(0, 0.0, rx - 0.035 * size * 1.6, ry - 0.035 * size * 1.6, 20), center, normal, 0.015, up=up)
    ef.badge(ef.bm_sink(B), face_m(center, normal, up, 0.015), 0.72 * size, depth=0.006, res=1, low=True,
             sink_in=0.002)


def curl_scroll(center, normal, half_w, h, *, up=(0, 0, 1), key="gold_d", th=0.016):
    """좌우 대칭 덩굴 소용돌이 한 쌍 (가운데에서 바깥으로 뻗어 끝이 안으로 말림)."""
    r0 = min(0.32 * half_w, 0.45 * h)
    cx, cy = half_w - r0, 0.0
    for sx in (1, -1):
        tail = bez((0.02 * half_w, -0.35 * r0), (0.3 * half_w, -0.55 * r0), (cx - 0.9 * r0, r0), (cx, r0), 8)
        curl = []
        for i in range(1, 22):
            t = i / 21
            a = math.radians(90) - t * 1.35 * 2 * math.pi
            r = r0 * (1 - 0.72 * t)
            curl.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        path = [(sx * p[0], p[1]) for p in [(q[0], q[1]) for q in tail] + curl]
        decal(key, hw.strip(path, th), center, normal, up=up, lift=0.003)
    # 가운데 꽃잎 하나
    decal(key, ellipse(0, 0.0, 0.022, 0.03, 10), center, normal, up=up, lift=0.003)


# 문(운전석 옆) 판: 금 테 + 문장 + 소용돌이
for s in sides():
    n = (s, 0, 0)
    Rv, Uv, N = mk.frame(n)
    dc = Vector((s * BW, -0.40, 0.645))
    frame_pts = hw.rrect(0.64, 0.34, 0.06, n=2)
    put("gold", ve.loop_frame("door_frame", frame_pts, tuple(dc), tuple(Rv), tuple(Uv), r=0.008, lift=0.004, verts=5),
        "detail")
    emblem(tuple(dc), n, 0.26)
    # 단상 옆 판 (칸막이 뒤 ~ 뒤 펜더 앞)
    pc = Vector((s * BW, 0.40, 0.64))
    put("gold", ve.loop_frame("side_frame", hw.rrect(0.44, 0.28, 0.06, n=2), tuple(pc), tuple(Rv), tuple(Uv),
                              r=0.008, lift=0.004, verts=5), "detail")
    curl_scroll(tuple(pc), n, 0.17, 0.09)

# ================================================================== 앞: 그릴, 범퍼, 전조등, 보닛 장식
GY = -2.0
plate("gold", hw.rrect(0.62, 0.30, 0.09, n=3), (0, GY, 0.585), (0, -1, 0), 0.03, kind="main")
plate("green", hw.rrect(0.54, 0.23, 0.065, n=3), (0, GY, 0.585), (0, -1, 0), 0.036, kind="main")
for i in range(-5, 6):
    x = i * 0.045
    rbox("gold", x - 0.006, x + 0.006, GY - 0.044, GY - 0.03, 0.49, 0.68, kind="detail")
emblem((0, GY - 0.036, 0.585), (0, -1, 0), 0.20)

bump = [(0.80 * math.cos(math.radians(a)), -1.86 + 0.24 * math.sin(math.radians(a)), 0.38)
        for a in range(180, 361, 12)]
tube("gold", bump, 0.034, verts=8, kind="main")
for x in (-0.3, 0.3):
    blob("gold", (x, -2.10 + 0.005, 0.40), 0.045, (0.7, 0.7, 1.4), segs=8, rings=5, kind="detail")
    cyl("chassis", (x, -2.06, 0.38), (x, -1.95, 0.40), 0.018, segs=6)

for s in sides():
    lc = (s * 0.585, -1.80, 0.72)
    put("gold", cb.sphere("lamp", radius=0.095, loc=lc, scale=(1.0, 1.25, 1.0), segments=12, rings=7), "main")
    put("gold", hw.torus("lamp_rim", 0.082, 0.012, loc=(lc[0], lc[1] - 0.108, lc[2]), rot=(90, 0, 0), seg=14,
                         rseg=4), "detail")
    put("lamp", hw.ycyl("lamp_lens", 0.078, lc[1] - 0.112, lc[1] - 0.104, x=lc[0], z=lc[2], verts=16))
    cyl("chassis", (lc[0] * 0.8, lc[1] + 0.02, lc[2] - 0.06), (s * 0.45, -1.80, 0.64), 0.016, segs=6)

# 보닛 장식: 금 받침 + 수액빛 보석 + 서 있는 에르피엔 나비 (앞뒤 양면 조형)
HO = Vector((0, -1.93, zt(-1.93)))
cyl("gold", tuple(HO - Vector((0, 0, 0.01))), tuple(HO + Vector((0, 0, 0.035))), 0.026, segs=12, r2=0.018,
    kind="detail")
blob("jewel", tuple(HO + Vector((0, 0, 0.055))), 0.022, segs=10, rings=6)
bc = HO + Vector((0, -0.005, 0.10))
cyl("gold", tuple(HO + Vector((0, 0, 0.07))), tuple(bc), 0.006, segs=6, kind="detail")
ef.badge(ef.bm_sink(B), face_m(tuple(bc + Vector((0, 0, 0.045))), (0, -1, 0)), 0.10, depth=0.004, res=1, low=True,
         both=True)

# ================================================================== 앞 펜더 깃발 (에르피엔 군기)
FLAGS = []
EF = ef.bm_sink(B, remap={"under": "fine"})        # 이 소품의 종류: main / detail / fine (under → fine)


def pennant(s, base):
    """금 깃대 + 작은 에르피엔 군기. 천은 차 뒤(+Y)로 날린다 (깃발 로컬 +X → +Y)."""
    x, y, z = base
    top = z + 0.62
    cyl("gold", (x, y, z - 0.02), (x, y, z + 0.03), 0.024, segs=10, r2=0.018, kind="detail")
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.pi / 2, 4, "Z")    # 천은 양면에 나비가 있다
    ef.standard(EF, M, pole=0.62, W=0.36, r=0.011, cols=4, res=1, low=True, strokes=False, stripes=False,
                butt=False, wave=0.07, droop=0.04, phase=0.4 + (0.9 if s < 0 else 0.0), pole_key="gold",
                lift=0.004)     # 이 소품은 깊이 편향 등급이 없어 띄우는 거리로만 가른다 (4 mm → 약 60 m까지)
    FLAGS.append(("flag_L" if s > 0 else "flag_R", (x, y, top + 0.02)))


for s in sides():
    th = math.radians(116)
    pennant(s, (s * 0.86, YF + RF * math.cos(th), R + RF * math.sin(th) + 0.045))

# ================================================================== 운전석: 계기판, 운전대, 바람막이, 벤치
plate("cream", hw.rrect(0.96, 0.17, 0.05, n=2), (0, CAB_Y0, 0.80), (0, 1, 0), 0.03, kind="detail")
for x in (-0.24, 0.0, 0.24):
    if x == 0.0:
        decal("screen", hw.rrect(0.14, 0.07, 0.015, n=2), (0, CAB_Y0 + 0.03, 0.80), (0, 1, 0), lift=0.002)
        continue
    decal("gold", hw.circle(0.042, 16), (x, CAB_Y0 + 0.03, 0.80), (0, 1, 0), lift=0.002)
    decal("chassis", hw.circle(0.033, 16), (x, CAB_Y0 + 0.03, 0.80), (0, 1, 0), lift=0.003)
SW = Vector((0, -0.70, 1.13))
cyl("chassis", (0, CAB_Y0 + 0.02, 0.80), tuple(SW + Vector((0, -0.02, -0.01))), 0.02, segs=8)
put("gold", hw.torus("wheel_rim", 0.11, 0.013, loc=tuple(SW), rot=(-33, 0, 0), seg=16, rseg=5), "detail")
blob("gold", tuple(SW), 0.025, (1, 1, 0.6), segs=10, rings=5, kind="detail")
for a in (90, 210, 330):
    v = Matrix.Rotation(math.radians(-33), 3, "X") @ Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
    cyl("cream", tuple(SW), tuple(SW + v * 0.105), 0.008, segs=6, kind="detail")

# 낮은 바람막이 (금 테 + 유리)
WS_O = Vector((0, -0.935, zt(-0.935) - 0.005))
WS_U = Vector((1, 0, 0))
WS_V = Vector((0, 0.34, 0.94)).normalized()
ws = [(-0.50, 0.0), (0.50, 0.0)] + [(p[0], p[1]) for p in hw.arc_pts(0.40, 0.20, 0.10, 0, 90, 4)] \
    + [(p[0], p[1]) for p in hw.arc_pts(-0.40, 0.20, 0.10, 90, 180, 4)]
put("glass", ve.slab("ws_glass", ws, tuple(WS_O), tuple(WS_U), tuple(WS_V), 0.006))
put("gold", ve.loop_frame("ws_frame", ws, tuple(WS_O), tuple(WS_U), tuple(WS_V), r=0.014, lift=0.003), "detail")
for x in (-0.5, 0.5):
    cyl("gold", (x, -0.935, zt(-0.935) - 0.02), tuple(WS_O + WS_U * x + WS_V * 0.12), 0.012, segs=6, kind="detail")

# 벤치 (붉은 가죽, 세로 주름 등받이)
rbox("cream", -XI, XI, SEAT_FRONT, -0.06, FLOOR, SEAT_TOP - 0.08)
rbox("red", -XI + 0.01, XI - 0.01, SEAT_FRONT - 0.01, -0.15, SEAT_TOP - 0.10, SEAT_TOP, bevel=0.035, seg=2)
BACK_PIV = Vector((0, -0.14, SEAT_TOP - 0.03))
backs = []
o = cb.box("back", size=(2 * XI - 0.02, 0.15, 0.40), loc=(0, -0.08, SEAT_TOP + 0.17), bevel=0.02, bevel_segments=2)
backs.append(("red", o))
for i in range(6):
    x = -0.44 + i * 0.176
    o = cb.cylinder("pleat", radius=0.075, depth=0.36, loc=(x, -0.155, SEAT_TOP + 0.17), verts=10)
    o.scale = (1.0, 0.45, 1.0)
    backs.append(("red", o))
o = hw.xcyl("back_pipe", 0.02, -XI + 0.01, XI - 0.01, y=-0.10, z=SEAT_TOP + 0.37, verts=8)
backs.append(("gold", o))
ve.rot_about([o for _, o in backs], tuple(BACK_PIV), "X", -9)
for key, o in backs:
    put(key, o, "main" if key == "red" else "detail")

# ================================================================== 뒤 단상: 난간 (금 윗대 + 크림 기둥 + 금 고리)
RIM_X = BW - WALL / 2
RIM_RY = Y_END - WALL / 2 - STERN_Y - 0.01
SIDE_POSTS = [0.05, 0.47, 0.89, 1.31, STERN_Y]
STERN_POSTS = [45, 90, 135]
LOW = DECK + 0.26


def rim_pt(s, y=None, phi=None):
    if phi is None:
        return (s * RIM_X, y)
    a = math.radians(phi)
    return (RIM_X * math.cos(a) * s, STERN_Y + RIM_RY * math.sin(a))


POSTS = []
for s in sides():
    for y in SIDE_POSTS:
        POSTS.append(rim_pt(s, y))
for phi in STERN_POSTS:
    POSTS.append(rim_pt(1, phi=phi))


def wall_top(x, y):
    return zt(min(y, Y_END)) - 0.004


for (x, y) in POSTS:
    z0 = wall_top(x, y)
    h = RAIL - z0
    prof = [(0.030, 0.0), (0.030, 0.03), (0.016, 0.06), (0.022, 0.6 * h), (0.016, 0.75 * h), (0.024, h)]
    put("cream", ve.lathe("post", prof, (x, y, z0), axis="Z", seg=7, smooth=50, closed=False), "detail")
    blob("gold", (x, y, RAIL + 0.03), 0.028, (1, 1, 1.15), segs=7, rings=4, kind="detail")


def rail_loop(z, *, front=True):
    """단상 둘레 경로 (왼쪽 앞 → 왼쪽 옆 → 꼬리 → 오른쪽 옆 [→ 앞 가로대])."""
    pts = []
    for y in [0.05 + (STERN_Y - 0.05) * i / 8 for i in range(9)]:
        pts.append((RIM_X, y, z))
    for i in range(1, 16):
        x, y = rim_pt(1, phi=180 * i / 16)
        pts.append((x, y, z))
    for y in [STERN_Y - (STERN_Y - 0.05) * i / 8 for i in range(9)]:
        pts.append((-RIM_X, y, z))
    if front:
        r = 0.06
        pts[-1] = (-RIM_X, 0.05 + r, z)
        for i in range(1, 4):
            a = math.radians(180 + 90 * i / 4)
            pts.append((-RIM_X + r + r * math.cos(a), 0.05 + r + r * math.sin(a), z))
        pts += [(-RIM_X + r, 0.05, z), (0.0, 0.05, z), (RIM_X - r, 0.05, z)]
        for i in range(1, 4):
            a = math.radians(270 + 90 * i / 4)
            pts.append((RIM_X - r + r * math.cos(a), 0.05 + r + r * math.sin(a), z))
        pts[0] = (RIM_X, 0.05 + r, z)
        pts.append(pts[0])
    return pts


tube("gold", rail_loop(RAIL), 0.02, verts=7, kind="main")
tube("gold", rail_loop(LOW, front=False)[1:-1], 0.011, verts=5)
# 칸막이 위 가로대 받침 (가운데 짧은 기둥 둘)
for x in (-0.2, 0.2):
    cyl("gold", (x, 0.05, wall_top(x, 0.05)), (x, 0.05, RAIL), 0.012, segs=6, kind="detail")
# 꼬리 칸의 금 고리 장식
for k in range(4):
    a0, a1 = 45 * k, 45 * (k + 1)
    am = math.radians((a0 + a1) / 2)
    x, y = rim_pt(1, phi=(a0 + a1) / 2)
    nrm = Vector((math.cos(am) / RIM_X, math.sin(am) / RIM_RY, 0)).normalized()
    zc = (RAIL + LOW) / 2
    rr = (RAIL - LOW) / 2 - 0.012
    rot = Vector((0, 0, 1)).rotation_difference(nrm).to_euler()
    put("gold", hw.torus("medal", rr, 0.008, loc=(x, y, zc), rot=tuple(math.degrees(v) for v in rot), seg=14,
                         rseg=4), "detail")



def offset_poly(pts, d):
    """닫힌 다각형(반시계)을 안쪽으로 d만큼 (꼭짓점 이등분선 근사)."""
    n = len(pts)
    out = []
    for i in range(n):
        p, a, b = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[(i + 1) % n])
        e1, e2 = (p - a).normalized(), (b - p).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        m = (n1 + n2).normalized()
        k = d / max(m.dot(n1), 0.35)
        out.append((p.x + m.x * k, p.y + m.y * k))
    return out


# 단상 바닥 금 테두리 상감
_inl_o, _inl_i = offset_poly(PLAT, 0.05), offset_poly(PLAT, 0.075)
_b = B("gold_d", "fine")
_vo = [_b.verts.new((x, y, DECK + 0.002)) for x, y in _inl_o]
_vi = [_b.verts.new((x, y, DECK + 0.002)) for x, y in _inl_i]
for i in range(len(_vo)):
    j = (i + 1) % len(_vo)
    _f = _b.faces.new((_vo[i], _vo[j], _vi[j], _vi[i]))
    _f.normal_update()
    if _f.normal.z < 0:
        _f.normal_flip()

# ================================================================== 꽃 장식줄


def flower_pts(r, petals=5, n=None):
    n = n or petals * 2
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1.0 if i % 2 == 0 else 0.74
        out.append((r * k * math.cos(a), r * k * math.sin(a)))
    return out


def flower(c, nrm, r, key, *, spin=0.0, center="yellow", kind="detail"):
    pts = rot2(flower_pts(r, 5, 10), spin)
    plate(key, pts, c, nrm, 0.012, kind=kind, back=0.0)
    N = Vector(nrm).normalized()
    decal(center, ellipse(0, 0, r * 0.3, r * 0.3, 6), tuple(Vector(c) + N * 0.012), tuple(N), lift=0.0005)


def swag(A, Bp, sag, out, *, n_fl=5, seed=0):
    A, Bp, out = Vector(A), Vector(Bp), Vector(out).normalized()
    path = []
    for i in range(9):
        t = i / 8
        p = A.lerp(Bp, t) - Vector((0, 0, 4 * sag * t * (1 - t)))
        path.append(tuple(p))
    tube("leaf", path, 0.016, verts=5)
    nrm = (out * math.cos(math.radians(22)) + Vector((0, 0, math.sin(math.radians(22))))).normalized()
    for i in range(n_fl):
        t = (i + 0.5) / n_fl
        p = A.lerp(Bp, t) - Vector((0, 0, 4 * sag * t * (1 - t))) + out * 0.012
        key = "pink" if (i + seed) % 2 == 0 else "white"
        flower(tuple(p), tuple(nrm), 0.036 if key == "pink" else 0.031, key, spin=(i * 37 + seed * 11) % 72)
        # 잎 (꽃 사이)
        if i < n_fl - 1:
            t2 = (i + 1) / n_fl
            q = A.lerp(Bp, t2) - Vector((0, 0, 4 * sag * t2 * (1 - t2))) + out * 0.006
            dz = 0.022 if i % 2 == 0 else -0.022
            Rv, Uv, _ = mk.frame(tuple(nrm))
            leaf = rot2(ellipse(0, 0, 0.032, 0.012, 6), 30 if dz > 0 else -30)
            plate("leaf_d", leaf, tuple(q + Uv * dz), tuple(nrm), 0.006, back=0.0)


def rosette(c, out):
    out = Vector(out).normalized()
    nrm = (out * math.cos(math.radians(15)) + Vector((0, 0, math.sin(math.radians(15))))).normalized()
    flower(tuple(c), tuple(nrm), 0.058, "pink_d", spin=18)
    decal("white", rot2(flower_pts(0.034), 36), tuple(Vector(c) + nrm * 0.012), tuple(nrm), lift=0.001)


for s in sides():
    out = (s, 0, 0)
    # 단상 옆 난간 (기둥 사이)
    xs = s * (RIM_X + 0.035)
    for k, (y0, y1) in enumerate(zip(SIDE_POSTS, SIDE_POSTS[1:])):
        swag((xs, y0, RAIL - 0.02), (xs, y1, RAIL - 0.02), 0.10, out, n_fl=4, seed=k)
    for y in SIDE_POSTS:
        rosette((xs + s * 0.01, y, RAIL - 0.03), out)
    # 운전석 옆 (바람막이 기둥 → 문 가운데 → 칸막이)
    anchors = [-0.88, -0.42, 0.04]
    for k, (y0, y1) in enumerate(zip(anchors, anchors[1:])):
        z0, z1 = zt(y0) - 0.03, zt(y1) - 0.03
        swag((s * (surf_x(y0, z0) + 0.022), y0, z0), (s * (surf_x(y1, z1) + 0.022), y1, z1), 0.075, out, n_fl=4,
             seed=k + 1)
    for y in anchors:
        z = zt(y) - 0.035
        rosette((s * (surf_x(y, z) + 0.03), y, z), out)

# ================================================================== 뒤: 범퍼, 꼬리등, 문장
rb_pts = [(0.70 * math.cos(math.radians(a)), STERN_Y + 0.34 * math.sin(math.radians(a)), 0.40)
          for a in range(25, 156, 10)]
tube("gold", rb_pts, 0.032, verts=8, kind="main")
for s in sides():
    a = math.radians(58)
    p = Vector((s * BW * math.cos(a), STERN_Y + STERN_RY * math.sin(a), 0.60))
    nrm = Vector((s * math.cos(a) / BW, math.sin(a) / STERN_RY, 0)).normalized()
    cyl("gold", tuple(p - nrm * 0.01), tuple(p + nrm * 0.02), 0.042, segs=12, kind="detail")
    cyl("tail", tuple(p + nrm * 0.02), tuple(p + nrm * 0.026), 0.032, segs=12)
emblem((0, Y_END - 0.004, 0.595), (0, 1, 0), 0.15)

# ================================================================== 노드 (서 있는 자리, 운전석)
MARKERS = [
    ("stand_1", (0.35, 0.95, DECK), {}),
    ("stand_2", (-0.35, 0.95, DECK), {}),
    ("seat_driver", (0.0, SEAT_FRONT + 0.09, FLOOR), {"seatZ": round(SEAT_TOP - FLOOR, 3)}),
] + [(nm, p, {}) for nm, p in FLAGS]


# ================================================================== 미리보기용 인물 (PC_PREVIEW=1)
def preview_people():
    def mannequin(loc, *, seat=None):
        x, y, z = loc
        if seat is None:
            cyl("chassis", (x, y, z), (x, y, z + 0.42), 0.09, segs=10)
            cyl("cream", (x, y, z + 0.42), (x, y, z + 0.72), 0.13, segs=10)
            blob("pink", (x, y, z + 0.95), 0.25, segs=14, rings=8)
        else:
            hip = z + seat + 0.07
            cyl("chassis", (x, y, hip), (x, y - 0.24, hip), 0.08, segs=10)
            cyl("chassis", (x, y - 0.24, hip), (x, y - 0.26, z + 0.02), 0.07, segs=10)
            cyl("cream", (x, y, hip), (x, y, hip + 0.30), 0.13, segs=10)
            blob("pink", (x, y, hip + 0.53), 0.25, segs=14, rings=8)
    imported = False
    try:
        for path, (nm, loc) in (("characters/erpin_royal.glb", MARKERS[0][:2]),
                                ("characters/ner_coronation.glb", MARKERS[1][:2])):
            before = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=os.path.join(cb.MODELS_DIR, path))
            new = [o for o in bpy.data.objects if o not in before]
            for o in new:
                if o.parent is None:
                    o.location = Vector(loc) + o.location
        imported = True
    except Exception as e:  # noqa: BLE001
        print("[pc] preview import failed:", e)
    if not imported:
        mannequin(MARKERS[0][1])
        mannequin(MARKERS[1][1])
    mannequin(MARKERS[2][1], seat=SEAT_TOP - FLOOR)


# ================================================================== 마무리
def finish():
    bake_objs()
    root = cb.empty(NAME, size=0.5)
    tris = {}
    for (key, kind), b in sorted(ACC.items()):
        if not b.faces:
            b.free()
            continue
        suffix = {"main": "", "detail": "_thin", "fine": "_flat"}[kind]
        nm = f"body_{key}{suffix}"
        me = bpy.data.meshes.new(nm)
        b.to_mesh(me)
        b.free()
        o = bpy.data.objects.new(nm, me)
        cb.link(o, root)
        cb.assign(o, M(key))
        if kind == "detail":
            o["outline"] = DETAIL
        elif kind == "fine":
            o["noOutline"] = 1
        me.calc_loop_triangles()
        tris[nm] = len(me.loop_triangles)
    ACC.clear()
    for w in WHEELS:
        mw = w.matrix_world.copy()
        w.parent = root
        w.matrix_parent_inverse = Matrix.Identity(4)
        w.matrix_world = mw
        w.data.calc_loop_triangles()
        tris[w.name] = len(w.data.loop_triangles)
    for nm, loc, props in MARKERS:
        e = cb.empty(nm, loc=loc, parent=root, size=0.15)
        for k, v in props.items():
            e[k] = v
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    total = sum(tris.values())
    print("[pc] tris: " + ", ".join(f"{k}={v}" for k, v in sorted(tris.items(), key=lambda kv: -kv[1])))
    print(f"[pc] total tris {total} / 25000, materials {len([m for m in bpy.data.materials if m.users])}")
    if total > 25000:
        raise RuntimeError(f"[pc] 예산 초과 {total}")
    props = {"outline": OUTLINE, "prop": "parade_car", "wheelRadius": R, "wheelbase": round(YR - YF, 3),
             "track": round(2 * XW, 3), "deckZ": DECK, "floorZ": FLOOR}
    if PREVIEW:
        preview_people()
        bake_objs()
        for (key, kind), b in ACC.items():
            me = bpy.data.meshes.new("pv")
            b.to_mesh(me)
            o = bpy.data.objects.new(f"pv_{key}", me)
            cb.link(o)
            cb.assign(o, M(key))
        return cb.export(f"props/{NAME}_preview.glb", props=props, root=root)
    return cb.export(f"props/{NAME}.glb", props=props, root=root)


finish()
