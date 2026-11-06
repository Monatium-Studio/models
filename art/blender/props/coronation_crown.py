"""에르핀의 3차 대관식 왕관 '축복의 왕관' (props/coronation_crown.glb). 에필로그 EP_CROWN에서 쓴다.

[원작] 시즌 2에서 힘을 잃고 빛바랜 에르핀의 왕관은 침공전 종전 뒤 골디의 도움과 정령들의 가호로 색을 되찾아
      다시 수여된다. 되찾은 왕관은 금관에 붉은 보석과 진주 (docs/art/fairy-faction.md 1·5장).
[오리지널] 형태: 고른 두께의 둥근 금 띠(위아래 테두리 몰딩), 띠 둘레 금 베젤에 박은 붉은 보석(정면 큰 타원 하나 +
      작은 원형 일곱), 그 사이 진주 알. 띠 위로 큰 창끝 장식 8개(정면이 가장 높고 뒤로 갈수록 조금씩 낮다, 좌우 대칭)와
      그 사이 작은 잎 장식 8개, 모든 끝에 진주. 정면 장식에는 작은 붉은 보석을 하나 더 박았다.
      원작 일러스트를 옮기지 않은 새 디자인이다. 캐릭터에 구운 erpin_royal_crown(머리에 붙은 납작한 관)을 대신한다.

규약: Blender Z-up, 1 BU = 1 m. 원점 = 띠 아래 테두리 원의 중심, 위 +Z, 정면(큰 붉은 보석) -Y.
치수: 띠 안 반지름 0.110, 바깥 0.119(테두리 몰딩 0.122), 띠 높이 0.045, 전체 높이(정면 진주 끝) 약 0.124.
빈 노드: grip (+0.125, 0, 0.03) 오른손(왕관 +X 옆), grip_support (-0.125, 0, 0.03) 왼손(-X 옆).
         두 손으로 상자처럼 든다.

npm run model -- art/blender/props/coronation_crown.py
npm run shot -- props/coronation_crown.glb --views front,34,side,top
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
# 에르핀(왕도) 캐릭터와 같은 금·진주·보석 색 (art/blender/characters/erpin_royal.py)
lk.PAL.update({
    "cr_gold": "#f0c46a", "cr_gold_l": "#f7d888", "cr_gold_d": "#cc9844",
    "cr_pearl": "#f4ecf2",
    "cr_gem": "#e2334b", "cr_gem_d": "#b31f3a", "cr_gem_l": "#f2697b",
})
lk.GLOW.update({"cr_glint": "#ffffff"})
L = lk.Level("coronation_crown")

TAU = math.tau
Z = Vector((0, 0, 1))

# ------------------------------------------------------------------ 치수
RI, RO, RL = 0.110, 0.119, 0.122      # 띠 안, 바깥 면, 테두리 몰딩
BH = 0.045                             # 띠 높이
ZF = (0.009 + 0.036) / 2               # 띠 앞면 가운데 높이 (보석 줄)
SEGS = 40                              # 띠 둘레 분할


def radial(th):
    """방위각 th(0 = 정면 -Y, +90° = +X)의 바깥 방향."""
    return Vector((math.sin(th), -math.cos(th), 0.0))


def tangent(th):
    return Vector((math.cos(th), math.sin(th), 0.0))


def P(r, th, z):
    return radial(th) * r + Vector((0, 0, z))


# ------------------------------------------------------------------ 조각 빌더 (재질별 bmesh, 면 방향을 기대 법선으로 맞춤)

class Piece:
    def __init__(self, kind="main", angle=40.0):
        self.kind = kind
        self.angle = angle
        self.bms = {}

    def face(self, key, pts, expect=None):
        b = self.bms.get(key)
        if b is None:
            b = self.bms[key] = bmesh.new()
        f = b.faces.new([b.verts.new(Vector(p)) for p in pts])
        f.normal_update()
        if expect is not None and f.normal.dot(expect) < 0:
            f.normal_flip()
        return f

    def emit(self):
        for key, b in self.bms.items():
            bmesh.ops.remove_doubles(b, verts=b.verts, dist=1e-6)
            me = bpy.data.meshes.new("piece")
            b.to_mesh(me)
            b.free()
            o = bpy.data.objects.new("piece", me)
            cb.link(o)
            cb.smooth(o, angle=self.angle)
            L.obj(key, o, kind=self.kind)
        self.bms = {}


def ccw_normal(a, b):
    """반시계 2D 외곽선의 변 a→b 바깥 법선."""
    d = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*d) or 1.0
    return (d[1] / n, -d[0] / n)


# ------------------------------------------------------------------ 띠 (둥근 고리, 위아래 몰딩)

def band():
    # (r, z) 단면, 반시계 (안쪽 아래 → 바닥 → 바깥 → 위 → 안쪽)
    prof = [
        (RI, 0.000, "cr_gold_d"),
        (RL - 0.0015, 0.000, "cr_gold"),
        (RL, 0.0015, "cr_gold_l"),
        (RL, 0.0065, "cr_gold"),
        (RO, 0.0090, "cr_gold"),
        (RO, 0.0360, "cr_gold"),
        (RL, 0.0385, "cr_gold_l"),
        (RL, 0.0435, "cr_gold"),
        (RL - 0.0015, BH, "cr_gold"),
        (RI, BH, "cr_gold_d"),
    ]
    pc = Piece(angle=40.0)
    n = len(prof)
    for k in range(n):
        r0, z0, key = prof[k]
        r1, z1, _ = prof[(k + 1) % n]
        nr, nz = ccw_normal((r0, z0), (r1, z1))
        for i in range(SEGS):
            a0, a1 = TAU * i / SEGS, TAU * (i + 1) / SEGS
            am = (a0 + a1) / 2
            exp = radial(am) * nr + Z * nz
            pc.face(key, [P(r0, a0, z0), P(r0, a1, z0), P(r1, a1, z1), P(r1, a0, z1)], exp)
    pc.emit()


# ------------------------------------------------------------------ 장식 (창끝·잎): 띠 곡면을 따라 휜 판을 가로 단면으로 쌓는다

def spire(th0, H, W, shape, *, t=0.0045, r0=0.1135, flare=0.006, embed=0.005, kind="main", chamfer=True):
    """th0 방위 장식 하나. shape: [(u 0..1 높이 비율, 반폭 비율)], 아래는 띠 속에 embed만큼 묻는다.
    chamfer=False면 모따기 없는 네모 단면 (작은 잎). 반환: 꼭대기 (반지름, 높이)."""
    pc = Piece(kind=kind, angle=40.0)
    rows = []
    rows_u = [(-embed / H, shape[0][1])] + list(shape)
    for u, s in rows_u:
        uu = max(u, 0.0)
        z = BH + u * H
        w = W * s
        c = min(0.0016, w * 0.45, t * 0.4)
        rin = r0 + flare * uu ** 1.5
        rm = rin + t / 2
        if chamfer:
            sec = [(-w, 0.0), (w, 0.0), (w, t - c), (w - c, t), (-w + c, t), (-w, t - c)]
        else:
            sec = [(-w, 0.0), (w, 0.0), (w, t), (-w, t)]
        rows.append([(P(rin + d, th0 + sx / rm, z)) for sx, d in sec])
        rows[-1].append((rin, z, sec))
    nsec = len(sec)
    for i in range(len(rows) - 1):
        _, _, sec = rows[i][-1]
        for k in range(nsec):
            a, b = sec[k], sec[(k + 1) % nsec]
            ns, nd = ccw_normal(a, b)
            exp = tangent(th0) * ns + radial(th0) * nd
            key = "cr_gold_d" if k == 0 else "cr_gold"
            pc.face(key, [rows[i][k], rows[i][(k + 1) % nsec], rows[i + 1][(k + 1) % nsec], rows[i + 1][k]], exp)
    top = rows[-1]
    pc.face("cr_gold", top[:nsec], Z)
    pc.emit()
    rin, z, _ = top[-1]
    return rin + t / 2, z


def pearl(c, r, segs=8, rings=5, kind="detail"):
    L.obj("cr_pearl", cb.sphere("pearl", radius=r, loc=tuple(c), segments=segs, rings=rings), kind=kind)


# ------------------------------------------------------------------ 보석 + 금 베젤

def gem(c, n, up, rx, rz, *, depth, bw, bh, segs, glint=0.0, chamfer=True, star=True):
    """c = 바탕면 위 점, n = 바깥 법선, up = 위. 타원 rx(가로)·rz(세로). 금 베젤(폭 bw, 높이 bh) 안에 깎은 보석."""
    n = Vector(n).normalized()
    up = Vector(up)
    up = (up - n * up.dot(n)).normalized()
    lat = up.cross(n).normalized()

    def at(s_x, s_z, h, a):
        return c + lat * (s_x * math.cos(a)) + up * (s_z * math.sin(a)) + n * h

    # 베젤: 안벽 → 윗면 → 바깥 모따기 → 바깥벽 (바닥은 띠 속)
    bz = Piece(kind="detail", angle=40.0)
    ch = min(0.0009, bw * 0.4)
    if chamfer:
        prof = [((0.0, -0.002), "cr_gold_d"), ((0.0, bh), "cr_gold"), ((bw - ch, bh), "cr_gold"),
                ((bw, bh - ch), "cr_gold"), ((bw, -0.002), None)]
    else:
        prof = [((0.0, -0.002), "cr_gold_d"), ((0.0, bh), "cr_gold"), ((bw, bh), "cr_gold"), ((bw, -0.002), None)]
    for i in range(segs):
        a0, a1 = TAU * i / segs, TAU * (i + 1) / segs
        am = (a0 + a1) / 2
        rdir = (lat * (math.cos(am) / rx) + up * (math.sin(am) / rz)).normalized()
        for k in range(len(prof) - 1):
            (q0, h0), key = prof[k]
            (q1, h1), _ = prof[k + 1]
            if key is None:
                continue
            # 단면 (q 바깥, h 위): 안벽은 안쪽(-rdir), 윗면은 n, 바깥벽은 rdir
            dq, dh = q1 - q0, h1 - h0
            ln = math.hypot(dq, dh)
            exp = rdir * (-dh / ln) + n * (dq / ln)
            if k == 0:
                exp = -rdir
            pc = [at(rx + q0, rz + q0, h0, a0), at(rx + q0, rz + q0, h0, a1),
                  at(rx + q1, rz + q1, h1, a1), at(rx + q1, rz + q1, h1, a0)]
            bz.face(key, pc, exp)
    bz.emit()
    # 보석: 바깥 깎은 면 (짙은) → 안 깎은 면 → 평평한 윗면 (밝은)
    g = Piece(kind="detail", angle=8.0)
    h0 = bh * 0.55
    rings = [(1.0, h0), (0.80, h0 + depth * 0.62), (0.46, h0 + depth)]
    keys = ["cr_gem_d", "cr_gem"]
    for j in range(len(rings) - 1):
        s0, z0 = rings[j]
        s1, z1 = rings[j + 1]
        for i in range(segs):
            a0, a1 = TAU * (i + 0.5 * j) / segs, TAU * (i + 1 + 0.5 * j) / segs
            b0, b1 = TAU * (i + 0.5 * (j + 1)) / segs, TAU * (i + 1 + 0.5 * (j + 1)) / segs
            am = (a0 + a1) / 2
            exp = n + (lat * math.cos(am) + up * math.sin(am)) * 0.8
            # 엇갈린 링 → 삼각 면 두 장 (브릴리언트 컷처럼 보인다)
            g.face(keys[j], [at(rx * s0, rz * s0, z0, a0), at(rx * s0, rz * s0, z0, a1),
                             at(rx * s1, rz * s1, z1, b0)], exp)
            g.face(keys[j], [at(rx * s0, rz * s0, z0, a1), at(rx * s1, rz * s1, z1, b1),
                             at(rx * s1, rz * s1, z1, b0)], exp)
    s2, z2 = rings[-1]
    g.face("cr_gem_l", [at(rx * s2, rz * s2, z2, TAU * (i + 1.0) / segs) for i in range(segs)], n)
    g.emit()
    if glint > 0:
        gc = c + n * (h0 + depth + 0.0003) + up * (rz * 0.30) - lat * (rx * 0.28)
        pts = []
        npt = 8 if star else 4
        for i in range(npt):
            a = TAU * i / npt + math.pi / 2
            rr = glint if (i % 2 == 0 or not star) else glint * 0.32
            pts.append((math.cos(a) * rr * (1.0 if star else 0.6), math.sin(a) * rr))
        L.decal("cr_glint", pts, tuple(gc), tuple(n), up=tuple(up), lift=0.0)


# ------------------------------------------------------------------ 조립
band()

# 큰 창끝 8개: 정면(0°)이 가장 높고 뒤로 갈수록 조금 낮다 (좌우 대칭)
SPIRE = [(0.0, 0.86), (0.10, 1.0), (0.24, 0.97), (0.38, 0.78), (0.53, 0.54), (0.68, 0.34), (0.84, 0.19),
         (1.0, 0.09)]
LEAF = [(0.0, 0.80), (0.28, 1.0), (0.58, 0.72), (0.82, 0.32), (1.0, 0.12)]

for i in range(8):
    th = TAU * i / 8
    f = ((1 + math.cos(th)) / 2) ** 2
    H = 0.050 + 0.016 * f
    W = 0.0172 + 0.0022 * f
    rp = 0.0062 + 0.0012 * f
    r_top, z_top = spire(th, H, W, SPIRE)
    pearl(P(r_top, th, z_top + rp * 0.78), rp, segs=10 if i == 0 else 8, rings=6 if i == 0 else 5)
    # 띠 보석 (정면은 큰 타원)
    if i == 0:
        gem(P(RO, th, ZF), radial(th), Z, 0.0102, 0.0122, depth=0.0062, bw=0.0026, bh=0.0034, segs=14, glint=0.0034)
        # 정면 창끝의 작은 보석
        uu = 0.27
        rin = 0.1135 + 0.006 * uu ** 1.5
        gem(P(rin + 0.0045, th, BH + uu * H), radial(th), Z, 0.0052, 0.0070, depth=0.0034, bw=0.0016, bh=0.0018,
            segs=10, glint=0.0016, chamfer=False, star=False)
    else:
        gem(P(RO, th, ZF), radial(th), Z, 0.0058, 0.0058, depth=0.0040, bw=0.0019, bh=0.0026, segs=8, glint=0.0017,
            chamfer=False, star=False)

# 작은 잎 장식 8개 (큰 창끝 사이) + 띠 진주
for i in range(8):
    th = TAU * (i + 0.5) / 8
    r_top, z_top = spire(th, 0.021, 0.0085, LEAF, t=0.004, kind="detail", chamfer=False)
    pearl(P(r_top, th, z_top + 0.0042 * 0.75), 0.0042, segs=6, rings=4)
    pearl(P(RO + 0.0008, th, ZF), 0.0040, segs=6, rings=4)

# 두 손 자리 (오른손 = +X 옆, 왼손 = -X 옆)
L.marker("grip", (0.125, 0.0, 0.03))
L.marker("grip_support", (-0.125, 0.0, 0.03))
L.finish("props/coronation_crown.glb", prop=True, outline=0.0025, detail_outline=0.0015)
