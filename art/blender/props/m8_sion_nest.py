"""M8 「관측수」 시온의 저격 자리 (props/m8_sion_nest.glb). 정령산 능선 감시초소 앞 바위 턱.

npm run model -- art/blender/props/m8_sion_nest.py
npm run shot -- props/m8_sion_nest.glb --views 34,top

[원작] 시온은 정령산 감시초소를 맡았고, 초장거리 저격으로 중성자탄을 아공간으로 보낸다(docs/art/characters-cameo2.md 5장).
[오리지널] 저격 자리의 모양: 초소(levels/m8_overlook.glb의 watch_post) 북쪽 비탈에 튀어나온 바위 턱, 엎드려쏴 양각대를 얹는 낮은 모래주머니,
       턱 뒤의 위장망 차양, 탄약통과 야전 무전기, 흩어진 바위와 풀.

좌표는 m8_overlook.glb와 같은 월드 좌표다(원점에 붙이면 제자리). 미션(src/game/missions/m8/stage.ts)이 레벨 dynamic에 붙인다.
- 원경 지형(m8_overlook의 heightfield)은 이 거리에서 칸이 150 m를 넘어 초소 둘레가 실제 높이 함수보다 15 m쯤 낮다.
  초소 망루는 높이 함수 위에 서 있어 가까이서 보면 떠 있다. 그래서 초소 둘레 약 300 m를 높이 함수 그대로(8 m 칸) 덮는
  덧지형(mount_rock, kind far)을 깔고, 가장자리에서 원경 칸 높이로 섞는다. 높이 함수는 m8_overlook.py에서 그대로 옮겼다.
- 마커: SION_nest (시온이 엎드리는 자리: 상체·턱 아래, -Y 정면 = 기본 조준 방위), SION_rest (양각대를 얹는 납작한 모래주머니 윗면)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bisect  # noqa: E402
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import overlook_kit as ok  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
mk.PAL.update({
    "net": "#5d6a50",        # 위장망
    "net_d": "#47533f",
    "nest_rock": "#8d93a4",  # 턱 바위 (mount_rock보다 조금 밝게: 가까이서 면이 갈리게)
    "nest_rock_d": "#6f7486",
    "moss": "#6f8a63",
    "brass": "#d0a85a",
    "radio_od": "#5b6450",
})
C = mk.City("m8_sion_nest", prop=True)

# ================================================================== 높이 함수 (m8_overlook.py 그대로)
PEAKS = [(-2600, -3500, 470, 800), (-1700, -2600, 420, 650), (-700, -2950, 560, 720), (300, -3500, 520, 650),
         (900, -2050, 250, 320), (1500, -3950, 380, 650), (2500, -2850, 600, 780), (3500, -3150, 520, 720),
         (4600, -2700, 470, 700), (5600, -3300, 540, 800)]


def mountains(x, y):
    s = 0.0
    for (px, py, H, R) in PEAKS:
        dd = ((x - px) ** 2 + (y - py) ** 2) / (R * R)
        if dd < 9:
            s += H * math.exp(-dd)
    s += 90 * ok.smooth(-1800, -3200, y)
    return s * ok.smooth(-1150, -1750, y)


def hz(x, y):
    d = math.hypot(x - 250.0, y * 1.3)
    base = ok.smooth(450, 1600, d) * (5.0 + 4.0 * math.sin(x / 530 + 1.1) * math.cos(y / 610 - 0.4)
                                      + 2.5 * math.sin(x / 233 + y / 311))
    base += 26 * math.exp(-((x - 3400) ** 2 + (y - 120) ** 2) / 640 ** 2)
    base += 15 * math.exp(-((x - 1100) ** 2 + (y - 70) ** 2) / 170 ** 2)
    return base + mountains(x, y)


XS = ok.grid_lines(-2600, 6200, 250.0, step0=40.0, k=0.075, step_max=420.0)
YS = ok.grid_lines(-5200, 4800, -20.0, step0=40.0, k=0.075, step_max=420.0)


def coarse(x, y):
    """원경 칸의 높이 (네 꼭짓점 쌍선형. 실제 삼각형과는 칸 대각선 차이만큼 다를 수 있다)."""
    i = max(0, min(len(XS) - 2, bisect.bisect(XS, x) - 1))
    j = max(0, min(len(YS) - 2, bisect.bisect(YS, y) - 1))
    x0, x1, y0, y1 = XS[i], XS[i + 1], YS[j], YS[j + 1]
    u, v = (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)
    z00, z10, z01, z11 = hz(x0, y0), hz(x1, y0), hz(x0, y1), hz(x1, y1)
    zmax = max(z00, z10, z01, z11)
    return z00 * (1 - u) * (1 - v) + z10 * u * (1 - v) + z01 * (1 - u) * v + z11 * u * v, zmax


# ================================================================== 덧지형 (초소 둘레)
POST = (900.0, -1980.0)
PX0, PX1, PY0, PY1 = 735.0, 1065.0, -2175.0, -1790.0
STEP = 7.5
BLEND = 70.0       # 가장자리에서 원경 칸 높이로 섞는 폭
LIFT = 0.9         # 원경 칸(대각선 차이)이 뚫고 나오지 않게 띄운다
nx = int(round((PX1 - PX0) / STEP))
ny = int(round((PY1 - PY0) / STEP))


def patch_h(x, y):
    edge = min(x - PX0, PX1 - x, y - PY0, PY1 - y)
    w = ok.smooth(0.0, BLEND, edge)
    c, cmax = coarse(x, y)
    # 원경 칸이 오목한 데서 높이 함수가 칸보다 낮으면 칸을 따른다 (덧지형이 원경 아래로 숨지 않게)
    return max(hz(x, y), c) * w + c * (1 - w) + LIFT


C.group("terrain", noOutline=1)
b = C.bm("mount_rock", "far")
grid = {}
for j in range(ny + 1):
    for i in range(nx + 1):
        x, y = PX0 + i * (PX1 - PX0) / nx, PY0 + j * (PY1 - PY0) / ny
        grid[i, j] = b.verts.new((x, y, patch_h(x, y)))
for j in range(ny):
    for i in range(nx):
        f = b.faces.new((grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]))
        f.smooth = True
# 가장자리 치마 (원경 칸과의 틈을 가린다)
ring = ([grid[i, 0] for i in range(nx + 1)] + [grid[nx, j] for j in range(1, ny + 1)]
        + [grid[i, ny] for i in range(nx - 1, -1, -1)] + [grid[0, j] for j in range(ny - 1, 0, -1)])
low = [b.verts.new((v.co.x, v.co.y, v.co.z - 6.0)) for v in ring]
for k in range(len(ring)):
    k2 = (k + 1) % len(ring)
    b.faces.new((ring[k], low[k], low[k2], ring[k2]))

# ================================================================== 저격 자리 (초소 북쪽 비탈의 바위 턱)
A = Vector((907.0, -1961.0, 0.0))
A.z = patch_h(A.x, A.y) + 0.35            # 턱 윗면 (엎드리는 자리)
AZ = math.radians(24.0)                   # 기본 조준 방위 (북에서 동으로): 하늘의 탄
F = Vector((math.sin(AZ), math.cos(AZ), 0.0))
R = Vector((F.y, -F.x, 0.0))              # 오른쪽 (동)
rng = random.Random(8)


def at(f, r, dz=0.0):
    p = A + F * f + R * r
    return Vector((p.x, p.y, A.z + dz))


def local_pts(pts):
    return [tuple((A + F * f + R * r).xy) for f, r in pts]


C.group("nest")
# 턱: 비탈에서 튀어나온 넓적한 바위 판 (윗면 = A.z), 아래는 비탈 속으로
slab = [(-2.6, -1.9), (-2.2, 0.3), (-1.5, 1.9), (0.2, 2.5), (1.6, 2.1), (2.5, 1.0), (2.9, -0.4), (2.2, -1.8),
        (0.9, -2.6), (-0.8, -2.7), (-2.0, -2.5)]
C.prism("nest_rock", local_pts([(f, r) for f, r in slab]), A.z - 6.0, A.z, smooth=False)
# 턱 둘레의 깨진 모서리 바위 (윤곽을 거칠게)
for (f, r, s, sz) in ((2.6, -1.6, 0.9, 0.55), (2.9, 0.6, 0.8, 0.5), (1.4, 2.3, 1.0, 0.6), (-1.6, 2.2, 1.2, 0.8),
                      (-2.4, -2.2, 1.3, 0.9), (0.4, -2.8, 1.0, 0.6), (-2.9, 0.2, 1.4, 1.0)):
    p = at(f, r, -0.25)
    C.blob("nest_rock_d", tuple(p), s, (1.0, rng.uniform(0.7, 1.0), sz), segs=7, rings=4, rot_z=rng.uniform(0, 3),
           kind="detail")
# 턱 윗면의 이끼 띠 (평평한 판에 색 갈림)
for (f, r, s) in ((-1.9, -1.2, 0.7), (-0.6, 1.6, 0.6), (1.7, -1.4, 0.5)):
    c = at(f, r, 0.012)
    pts = [(math.cos(k / 9 * math.tau) * s * rng.uniform(0.7, 1.1), math.sin(k / 9 * math.tau) * s * rng.uniform(0.6, 1.0))
           for k in range(9)]
    C.decal("moss", pts, tuple(c), (0, 0, 1), up=tuple(F), lift=0.0)

# 엎드려쏴: 양각대를 얹는 납작한 모래주머니 한 단 (앞쪽, 윗면 약 9 cm). '더 엑시트'는 조준경이 총열보다 23 cm 높아(원작 옆모습)
# 눈높이(약 38 cm)에 조준경을 맞추면 양각대 피벗이 바닥에서 25~30 cm라, 접었을 때 27 cm인 다리를 벌려 디디려면 윗면이 낮아야 한다
# (예전 23 cm 두 겹은 다리가 거의 눕는다)
REST_F = 0.80
REST_H = 0.088
for k in range(2):
    p = at(REST_F, -0.2 + k * 0.4, 0.044)
    C.blob("sand", tuple(p), 0.27, (1.0, 0.66, 0.17), segs=8, rings=4, rot_z=math.atan2(R.y, R.x))
# 팔꿈치 밑에 깐 접은 담요 (바위에 닿는 팔꿈치)
mat_c = at(0.28, 0.0, 0.0)
C.rbox("olive", (mat_c.x, mat_c.y, mat_c.z + 0.015), (0.62, 0.42, 0.03), (0, 0, -math.degrees(AZ)), kind="detail")
C.marker("SION_rest", tuple(at(REST_F, 0.0, REST_H)))
C.marker("SION_nest", tuple(at(0.0, 0.0, 0.0)), face=tuple((A + F * 10).xy))

# 탄약통·야전 무전기 (오른쪽 뒤), 빈 탄피
can = at(-0.55, 0.85, 0.0)
C.rbox("olive", (can.x, can.y, can.z + 0.11), (0.34, 0.16, 0.22), (0, 0, math.degrees(AZ) * -1 + 12))
C.rbox("metal", (can.x, can.y, can.z + 0.235), (0.2, 0.05, 0.03), (0, 0, math.degrees(AZ) * -1 + 12))
rad = at(-0.95, 0.55, 0.0)
C.rbox("radio_od", (rad.x, rad.y, rad.z + 0.13), (0.26, 0.2, 0.26), (0, 0, -math.degrees(AZ) - 20))
C.cyl("metal", (rad.x + 0.07, rad.y, rad.z + 0.25), (rad.x + 0.12, rad.y - 0.05, rad.z + 1.15), 0.006, segs=4,
      kind="detail")
C.rbox("soot", (rad.x, rad.y, rad.z + 0.2), (0.12, 0.21, 0.06), (0, 0, -math.degrees(AZ) - 20), kind="detail")
for k in range(5):
    p = at(rng.uniform(-0.2, 0.3), rng.uniform(0.45, 0.85), 0.018)
    a = rng.uniform(0, math.tau)
    d = Vector((math.cos(a), math.sin(a), 0)) * 0.05
    C.cyl("brass", tuple(p - d), tuple(p + d), 0.012, segs=6, kind="detail")

# 위장망 차양: 뒤쪽 두 기둥에서 비탈 쪽으로 늘어진 망 (구멍 뚫린 격자)
POLES = [(-1.1, -1.5), (-1.3, 1.5)]
PH = 1.75
for f, r in POLES:
    p = at(f, r, 0.0)
    C.cyl("wood_d", (p.x, p.y, p.z - 0.2), (p.x, p.y, p.z + PH), 0.035, segs=6, kind="detail")
nb = C.bm("net", "detail")
NU, NV = 9, 6
verts = {}
for v in range(NV + 1):
    for u in range(NU + 1):
        tu, tv = u / NU, v / NV
        r = -2.0 + 4.0 * tu
        f = -1.2 - 1.9 * tv
        sag = 0.22 * math.sin(math.pi * tu) * (1 - tv) + rng.uniform(-0.05, 0.05)
        z = PH * (1 - tv) ** 1.3 - sag - 0.05 * tv
        p = at(f, r, z)
        verts[u, v] = nb.verts.new(tuple(p))
for v in range(NV):
    for u in range(NU):
        if rng.random() < 0.16 and 0 < u < NU - 1 and v > 0:
            continue
        fc = nb.faces.new((verts[u, v], verts[u + 1, v], verts[u + 1, v + 1], verts[u, v + 1]))
        fc.smooth = True
# 망에 꽂은 잎 다발 (위장)
for k in range(16):
    tu, tv = rng.uniform(0.05, 0.95), rng.uniform(0.0, 0.85)
    r = -2.0 + 4.0 * tu
    f = -1.2 - 1.9 * tv
    z = PH * (1 - tv) ** 1.3 - 0.22 * math.sin(math.pi * tu) * (1 - tv) + 0.05
    C.blob(rng.choice(("leaf_d", "net_d", "moss")), tuple(at(f, r, z)), rng.uniform(0.16, 0.28), (1, 1, 0.45),
           segs=6, rings=3, rot_z=rng.uniform(0, 3), kind="detail")

# ================================================================== 둘레: 바위·풀 (비탈을 따라)
C.group("scatter")
for k in range(70):
    ang = rng.uniform(0, math.tau)
    d = 3.5 + 26 * rng.random() ** 1.4
    x, y = A.x + math.cos(ang) * d, A.y + math.sin(ang) * d
    if math.hypot(x - POST[0], y - POST[1]) < 6.0:
        continue
    z = patch_h(x, y)
    s = rng.uniform(0.25, 1.3) * (1.0 if d > 6 else 0.6)
    C.blob(rng.choice(("nest_rock", "nest_rock_d", "mount_rock")), (x, y, z + s * 0.12), s,
           (1.0, rng.uniform(0.6, 1.0), rng.uniform(0.4, 0.7)), segs=7, rings=4, rot_z=rng.uniform(0, 3), kind="detail")
for k in range(150):
    ang = rng.uniform(0, math.tau)
    d = 2.8 + 22 * rng.random() ** 1.2
    x, y = A.x + math.cos(ang) * d, A.y + math.sin(ang) * d
    z = patch_h(x, y)
    h = rng.uniform(0.18, 0.42)
    lean = Vector((rng.uniform(-0.12, 0.12) + 0.1, rng.uniform(-0.12, 0.12), 0))   # 서풍에 동쪽으로 눕는다
    for t in range(3):
        o = Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0))
        C.cyl(rng.choice(("moss", "leaf_d", "field_wheat")), (x + o.x, y + o.y, z - 0.02),
              (x + o.x + lean.x * h * 2, y + o.y + lean.y * h * 2, z + h), 0.035, r2=0.004, segs=4, kind="detail",
              smooth=False)
# 초소로 오르는 돌계단 자국 (턱 → 초소)
for k in range(7):
    t = k / 6
    p = Vector((A.x + (POST[0] - A.x) * t * 0.8 - 1.5 * t, A.y + (POST[1] - A.y) * t * 0.8, 0))
    z = patch_h(p.x, p.y)
    C.rbox("nest_rock_d", (p.x, p.y, z + 0.05), (1.1, 0.55, 0.3), (0, 0, rng.uniform(-20, 20)), kind="detail")

print(f"[nest] A ({A.x:.1f}, {A.y:.1f}, {A.z:.1f}) post ground {hz(*POST):.1f} coarse {coarse(*POST)[0]:.1f}")
C.finish("props/m8_sion_nest.glb", root_props={"outline": 0.02, "prop": "set"}, outline=0.02, far_outline=0.04)
