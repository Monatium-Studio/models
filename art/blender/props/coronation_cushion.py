"""대관식 왕관 받침 쿠션 (props/coronation_cushion.glb). 에필로그 EP_CROWN에서 왕관(props/coronation_crown.glb)을 얹어 든다.

[오리지널] 붉은 벨벳 정사각 쿠션 (0.36 × 0.36 m, 두께 0.08 m). 솜이 차서 위아래가 볼록하고 옆선은 조금 안으로 당겨진다.
      둘레 솔기를 금색 파이핑이 덮고, 네 귀퉁이에 금술이 늘어진다. 윗면 가운데에 왕관 띠 자리가 살짝 눌려 있다.
      색은 대관식 세트의 융단·현수막 붉은색과 같다 (art/blender/levels/epilogue_coronation.py royal / royal_d).

규약: Blender Z-up, 1 BU = 1 m. 원점 = 쿠션 바닥 가운데, 위 +Z. 정면 -Y (정사각이라 앞뒤 구분은 없다).
빈 노드: crown_seat = 왕관 원점(띠 아래 원 중심)이 앉는 점 (윗면 가운데, 눌린 자리 높이).
         grip (+0.19, 0, 0.03) 오른손, grip_support (-0.19, 0, 0.03) 왼손. 옆 가장자리를 두 손으로 든다.
금술 끝은 바닥보다 약 2 cm 아래까지 늘어진다 (탁자 위에 놓으면 술 끝이 탁자면에 묻힌다).

npm run model -- art/blender/props/coronation_cushion.py
npm run shot -- props/coronation_cushion.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import level_kit as lk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
lk._mats.clear()
lk.PAL.update({
    "cu_velvet": "#bb3440", "cu_velvet_d": "#8c2633",
    "cu_gold": "#f0c46a", "cu_gold_l": "#f7d888", "cu_gold_d": "#d7a752",
})
L = lk.Level("coronation_cushion")

TAU = math.tau
A = 0.18            # 반폭 (솔기 귀퉁이)
ZS = 0.04           # 솔기 높이
BT, BB = 0.04, 0.04  # 위·아래 부풂
CONC = 0.035        # 옆선이 안으로 당겨지는 비율
CROWN_R = 0.116     # 왕관 띠 반지름 (안 0.110, 바깥 0.122의 가운데쯤)
DENT, DENT_W = 0.003, 0.02
PIPE_R = 0.0045


def tmap(t):
    """격자 매개변수 → 면 좌표: 가장자리(둥근 솔기)에 촘촘하게."""
    return 0.5 * t + 0.5 * math.sin(t * math.pi / 2)


def xy(u, v):
    return A * u * (1 - CONC * (1 - v * v)), A * v * (1 - CONC * (1 - u * u))


def g_top(t):
    return max(0.0, 1 - abs(t) ** 3.0) ** 0.5


def g_bot(t):
    return max(0.0, 1 - abs(t) ** 3.5) ** 0.45


def z_top(u, v):
    x, y = xy(u, v)
    r = math.hypot(x, y)
    return ZS + BT * g_top(u) * g_top(v) - DENT * math.exp(-((r - CROWN_R) / DENT_W) ** 2)


def z_bot(u, v):
    return ZS - BB * g_bot(u) * g_bot(v)


def uv_of(x, y):
    """xy()의 역 (몇 번 고정점 반복)."""
    u, v = x / A, y / A
    for _ in range(8):
        u = x / (A * (1 - CONC * (1 - v * v)))
        v = y / (A * (1 - CONC * (1 - u * u)))
    return u, v


def surface(key, N, zf, up):
    b = bmesh.new()
    ts = [tmap(-1 + 2 * i / N) for i in range(N + 1)]
    vs = [[None] * (N + 1) for _ in range(N + 1)]
    for i, u in enumerate(ts):
        for j, v in enumerate(ts):
            x, y = xy(u, v)
            vs[i][j] = b.verts.new((x, y, zf(u, v)))
    for i in range(N):
        for j in range(N):
            q = (vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1])
            b.faces.new(q if up else tuple(reversed(q)))
    me = bpy.data.meshes.new(key)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(key, me)
    cb.link(o)
    cb.smooth(o, angle=180)
    L.obj(key, o)


# ------------------------------------------------------------------ 쿠션 몸 (위: 밝은 벨벳, 아래: 그늘 벨벳)
surface("cu_velvet", 20, z_top, True)
surface("cu_velvet_d", 12, z_bot, False)

# ------------------------------------------------------------------ 금 파이핑 (솔기를 따라 도는 관)
NS = 16
corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
path = []
for k in range(4):
    (u0, v0), (u1, v1) = corners[k], corners[(k + 1) % 4]
    for i in range(NS):
        s = tmap(-1 + 2 * i / NS)          # -1..1 (귀퉁이 근처에 촘촘)
        f = (s + 1) / 2
        u, v = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f
        x, y = xy(u, v)
        path.append(Vector((x, y, ZS)))
n = len(path)
SEC = 6
b = bmesh.new()
rings = []
Z = Vector((0, 0, 1))
for i in range(n):
    p0, p, p1 = path[i - 1], path[i], path[(i + 1) % n]
    d0, d1 = (p - p0).normalized(), (p1 - p).normalized()
    T = (d0 + d1).normalized()
    Nn = T.cross(Z).normalized()
    miter = 1.0 / max(0.5, math.cos(d0.angle(d1) / 2))
    rings.append([b.verts.new(p + Nn * (math.cos(TAU * k / SEC) * PIPE_R * miter) + Z * (math.sin(TAU * k / SEC) * PIPE_R))
                  for k in range(SEC)])
for i in range(n):
    r0, r1 = rings[i], rings[(i + 1) % n]
    for k in range(SEC):
        k1 = (k + 1) % SEC
        f = b.faces.new((r0[k], r1[k], r1[k1], r0[k1]))
        f.normal_update()
        c = (path[i] + path[(i + 1) % n]) / 2
        if f.normal.dot(f.calc_center_median() - c) < 0:
            f.normal_flip()
me = bpy.data.meshes.new("pipe")
b.to_mesh(me)
b.free()
o = bpy.data.objects.new("pipe", me)
cb.link(o)
cb.smooth(o, angle=180)
L.obj("cu_gold", o)


# ------------------------------------------------------------------ 금술 (귀퉁이마다): 고리 매듭 → 줄 → 머리 → 술
def lathe(key, c, prof, segs, *, kind="detail", star=None, cap_top=True, cap_bot=True, angle=40.0):
    """세로축 회전체. prof = [(r, dz)] 위에서 아래로. star = 홈 비율(술 가닥 골)."""
    bm_ = bmesh.new()
    rings_ = []
    for j, (r, dz) in enumerate(prof):
        ring = []
        for i in range(segs):
            a = TAU * i / segs
            rr = r * (star if (star and i % 2) else 1.0)
            jag = (-0.003 if (star and j == len(prof) - 1 and i % 2 == 0) else 0.0)
            ring.append(bm_.verts.new(c + Vector((math.cos(a) * rr, math.sin(a) * rr, dz + jag))))
        rings_.append(ring)
    for j in range(len(rings_) - 1):
        for i in range(segs):
            i1 = (i + 1) % segs
            bm_.faces.new((rings_[j][i], rings_[j + 1][i], rings_[j + 1][i1], rings_[j][i1]))
    if cap_top:
        bm_.faces.new(list(reversed(rings_[0])))
    if cap_bot:
        bm_.faces.new(rings_[-1])
    bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces)
    me_ = bpy.data.meshes.new(key)
    bm_.to_mesh(me_)
    bm_.free()
    o_ = bpy.data.objects.new(key, me_)
    cb.link(o_)
    cb.smooth(o_, angle=angle)
    L.obj(key, o_, kind=kind)


for sx in (1, -1):
    for sy in (1, -1):
        C = Vector((sx * A, sy * A, ZS))
        D = Vector((sx, sy, 0)).normalized()
        # 귀퉁이 매듭 (파이핑이 만나는 곳을 덮는다)
        L.obj("cu_gold", cb.sphere("knot", radius=0.0065, loc=tuple(C + D * 0.002), scale=(1, 1, 0.85),
                                   segments=8, rings=5), kind="detail")
        # 줄: 매듭에서 바깥 아래로
        top = C + D * 0.013 + Vector((0, 0, -0.011))
        L.cyl("cu_gold_d", C + D * 0.004, top, 0.0019, verts=6, kind="detail")
        # 머리 (방울 + 목 띠)
        lathe("cu_gold", top, [(0.0018, 0.0), (0.0052, -0.0025), (0.0070, -0.0065), (0.0062, -0.0105),
                               (0.0050, -0.0125)], 8, cap_top=True, cap_bot=False)
        lathe("cu_gold_l", top, [(0.0058, -0.0118), (0.0058, -0.0152)], 8, cap_top=True, cap_bot=True, angle=60.0)
        # 술: 아래로 퍼지며 골이 진 가닥 묶음, 끝은 들쭉날쭉
        lathe("cu_gold_d", top, [(0.0052, -0.0150), (0.0080, -0.030), (0.0100, -0.0455)], 16, star=0.78,
              cap_top=False, cap_bot=True, angle=50.0)

# ------------------------------------------------------------------ 빈 노드
# 왕관이 앉는 높이: 띠 안·가운데·바깥 반지름에서 윗면 높이의 평균, 조금 묻힌다
zs = []
for r in (0.110, CROWN_R, 0.122):
    for i in range(32):
        a = TAU * i / 32
        u, v = uv_of(r * math.cos(a), r * math.sin(a))
        zs.append(z_top(u, v))
SEAT_Z = round(sum(zs) / len(zs) - 0.0015, 4)
print(f"[cushion] crown_seat z={SEAT_Z:.4f} (top center {z_top(0, 0):.4f}, ring {min(zs):.4f}..{max(zs):.4f})")
L.marker("crown_seat", (0.0, 0.0, SEAT_Z))
L.marker("grip", (0.19, 0.0, 0.03))
L.marker("grip_support", (-0.19, 0.0, 0.03))
L.finish("props/coronation_cushion.glb", prop=True, outline=0.003, detail_outline=0.0018)
