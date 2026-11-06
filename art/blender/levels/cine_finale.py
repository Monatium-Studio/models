"""3막 시네마틱 「에르핀/네르 vs 흑뉴아」 세트: 에르피엔 바깥 성문 앞, 해 질 녘 (M9 「종막」 끝 자리에서 이어진다).

npm run model -- art/blender/levels/cine_finale.py   → public/models/levels/cine_finale.glb
대본: docs/script/act3c.md (A3_FINALE), 장면: src/game/missions/cine/a3Finale.ts, 이어지는 미션 끝: art/blender/levels/m9_assault.py

[원작] (나무위키 「엘리아스 침공전」) 흑뉴아가 각성한 에르핀(왕도)을 에르피엔 하늘로 들어 올려 공격한다. 네르(엘다인)가
       도끼로 뒤에서 기습하고, 우로스·티그가 합세한다. 흑뉴아는 시온에게 다시 격추되어 숲에 떨어지고, 네르와 에르핀이 제압한다.
       세계수는 에르피엔 한가운데에 있고 왕궁과 왕국이 둘레를 두른다 (erpien_kit).
[오리지널] M9 끝과 같은 자리: 리타의 분대는 바깥 남문 앞 포석 마당(성문루 앞 약 43 m)에서 R41이 버린 모래주머니 둥지 뒤에
       무릎을 꿇고, 성벽 너머 세계수 수관 앞 하늘의 결전을 올려다본다 (규칙 3: 싸우지 않는다). 결전은 시가지 위, 수관 바로 아래.
       흑뉴아가 떨어지는 숲 빈터는 성문 진입로 서쪽, 성벽 밖 숲 띠 속 (성벽에서 약 34 m, 분대에서 서쪽으로 약 65 m).
       성문루·성벽·탑·현수막·문장은 M9와 같은 공용 키트(erpien_kit.city_gate + erpien_flag), R41 포위 진지·불탄 차량·
       성전군 M1A1 셋(동쪽 차선)도 M9 끝의 배치를 옮겼다.

좌표: Blender Z-up. M9 레벨 좌표를 끝 자리(MARK_end)가 원점이 되게 평행 이동했다 (회전 없음: +Y ≈ 북쪽 = 성문·세계수).
  M9 (x, y, z) = 이 세트 (x, y, z) + (-31.75, 721.25, M9 끝 자리 높이).
  세계수 (-28.3, 318.8) 높이 380 m, 바깥 성벽 반지름 273.6 m (성문루 앞면 (−3.8, 43.2), 분대에서 약 43 m), 분대 (−3.9, −0.1).
  하늘 결전 MARK_sky (−21.7, 153.7, 125) = M9 MARK_finale (분대에서 올려다보는 각 약 38°, 수관 밑 약 13 m).
  숲 빈터 FX_crash (−68.4, 13.8) = M9 (−100.2, 735.1): M9에서도 이 자리는 진입로 서쪽 보이지 않는 벽 밖 숲 띠다.
컷: fin_a(분대 뒤 낮은 곳: 성문과 하늘) · fin_b(하늘: 흑뉴아와 에르핀) · fin_c(하늘 와이드: 네르의 기습) · fin_d(옆: 빛의 충돌)
    fin_d2(성문 앞 망원: 시온 탄, 서쪽 숲으로 추락) · fin_e(숲 빈터: 제압, 뒤로 성벽과 세계수) · fin_f(앞에서: 분대 얼굴)
"""
import math
import os
import random
import sys

import bmesh

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import battlefield_kit as bk  # noqa: E402
import erpien_kit as ek  # noqa: E402
import erpien_flag as ef  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()
mk.PAL.setdefault("char", "#3a3036")          # 그을린 땅 (빈터)
mk.PAL.setdefault("rock_d", "#857a74")
mk.PAL.setdefault("splinter", "#c9a57a")      # 부러진 줄기 속살
C = mk.City("cine_finale")
S = bk.S
NZ = mk.noise2
rng = random.Random(7)

# ================================================================== M9와 같은 배치 (끝 자리 = 원점)
ERP_H = 380.0
FACE = (62.0, -699.5)                 # M9: 세계수 → 능선 전망대. gate_plan이 같은 성벽 마디·문루를 고른다
_f = Vector((FACE[0], FACE[1], 0.0)).normalized()
FO = Vector((_f.x, _f.y))             # 바깥 (세계수 → 성문 → 분대 → 다리)
TT = Vector((-FO.y, FO.x))            # 성문을 볼 때 오른쪽 (동쪽)
EX, EY = -FO.x * 320.0, -FO.y * 320.0  # 세계수 = 에르피엔 한가운데 (M9 END = radial 320)


def P(r, lat=0.0):
    """세계수에서 성문 방사선으로 r m, 성문을 볼 때 오른쪽으로 lat m (M9 radial()과 같다)."""
    return (EX + FO.x * r + TT.x * lat, EY + FO.y * r + TT.y * lat)


GP = ek.gate_plan(EX, EY, ERP_H, FACE)
R_W = GP["r_wall"]
SKY = Vector((*P(165.0, -8.0), 125.0))             # M9 MARK_finale (EZ + 125)
_a = math.radians(262.5)
CLEAR = (EX + math.cos(_a) * (R_W + 34.0), EY + math.sin(_a) * (R_W + 34.0))   # 숲 빈터 (성벽 밖 34 m)
SQ0 = Vector((*P(319.75, -3.85), 0.0))             # 분대 가운데
Q_E = math.radians(-20.0)                           # 빈터 컷의 축: 북북동 (성벽 고리 탑과 세계수가 뒤에 오게)
STABLE = (-30.25, 20.75)                            # M9 문지기 마구간
IFV3 = (25.75, 16.75)                               # M9 장갑차 3 자리 (동쪽 둔덕 뒤): 불탄 차량
WRECK_W = (-14.0, -12.5)                            # 분대 남서쪽 불탄 R41 차량 (M9 장갑차 4가 몰려 나온 서쪽 길)
# 성문 앞 포석 마당 (M9와 같은 반원)
PC = P(R_W + 18.0)


def d_clear(x, y):
    return math.hypot(x - CLEAR[0], y - CLEAR[1])


# ================================================================== 땅
def h(x, y):
    """분지 바닥(0) → 남쪽 능선(M9 전망대, 약 380 m 남쪽 +45 m) / 먼 언덕. 성 안과 포석 마당은 평평하다."""
    r = math.hypot(x - EX, y - EY)
    z = 9.0 * S((-110.0 - y) / 150.0) + 36.0 * S((-260.0 - y) / 120.0)
    out = max(abs(x - EX) - 520.0, 0.0) + max(y - EY - 640.0, 0.0) * 0.8
    z += 70.0 * S(out / 800.0) * (0.75 + 0.25 * NZ(x * 0.3, y * 0.3, 3))
    # 들판의 낮은 기복: 성 안·포석 마당·가까운 조각 가장자리(먼 조각과 이음)에서는 0
    fade = S((r - R_W - 8.0) / 14.0) * S((math.hypot(x - PC[0], y - PC[1]) - 28.0) / 14.0)
    edge = min(x + 150.0, 100.0 - x, y + 100.0, 75.0 - y)
    fade *= S(edge / 20.0)
    z += 0.42 * fade * (NZ(x * 1.1, y * 1.1, 5) + 0.6)
    dc = d_clear(x, y)
    if dc < 10.0:
        z -= 0.55 * (1 - S(dc / 10.0))                  # 떨어진 자리는 얕게 패였다
    return z


G = bk.Ground(h)
C.group("ground")
NEAR = (-150.0, 100.0, -100.0, 75.0)
MID = (-800.0, 800.0, -800.0, 1200.0)


def inside(b, x, y):
    return b[0] < x < b[1] and b[2] < y < b[3]


def rng_axis(a, b, step):
    n = int(round((b - a) / step))
    return [a + (b - a) * i / n for i in range(n + 1)]


G.patch(C, "far", rng_axis(-3000.0, 3000.0, 200.0), rng_axis(-3000.0, 3400.0, 200.0), key="far_grass", collider=False,
        skip=lambda x, y: inside(MID, x, y), kind="far")
G.patch(C, "mid", rng_axis(MID[0], MID[1], 25.0), rng_axis(MID[2], MID[3], 25.0), key="meadow_d", collider=False,
        skip=lambda x, y: inside(NEAR, x, y))
G.patch(C, "near", rng_axis(NEAR[0], NEAR[1], 2.5), rng_axis(NEAR[2], NEAR[3], 2.5), key="meadow", collider=False)

# ================================================================== 성문 (M9와 같은 키트·같은 자리)
# [오리지널] 바깥 성문루·성벽·탑, 문 위 둥근 판의 에르피엔 군기 나비, 문루 탑 현수막과 지붕 깃발 (erpien_kit.city_gate)
C.group("gate", outline=0.03)
GATE = ek.city_gate(C, GP, G.h, kind="main", scorch=0.8, lit="lamp_warm", seed=9, cols=False)
GFRONT = GATE["front"]

# ================================================================== 성문 앞 마당·진입로 (M9 3구역 「성문」 끝 모습)
C.group("forecourt")
bk.drape(C, "earth", [P(471.0), P(420.0), P(380.0), P(347.0)], 4.0, G, lift=0.045, step=2.0)
bk.drape(C, "erk_pave", [P(348.0), P(282.0)], 6.4, G, lift=0.06, step=2.0)
pv = []
for k in range(25):
    a = math.atan2(FO.y, FO.x) + math.radians(-90 + 180 * k / 24)
    pv.append((PC[0] + math.cos(a) * 24.0 - FO.x * 14.0, PC[1] + math.sin(a) * 24.0 - FO.y * 14.0))
pz = G.h(*PC)
C.poly("erk_pave", [(x, y, pz + 0.045) for x, y in pv], normal=(0, 0, 1), kind="detail")
for k in range(8):
    a, b = P(R_W + 8.0 + k * 4.0, -22.0), P(R_W + 8.0 + k * 4.0, 22.0)
    C.strip("stone_vd", (a[0], a[1], pz + 0.05), (b[0], b[1], pz + 0.05), 0.12, (0, 0, 1), lift=0.012)
# 문지기 마구간 (흰 돌, 청록 지붕)
SB = bk.Local((STABLE[0], STABLE[1], G.h(*STABLE)), math.degrees(math.atan2(FO.x, -FO.y)))
SB.box(C, "erk_wall", -5.5, 5.5, -3.2, 3.2, -0.5, 4.2)
SB.box(C, "erk_wall_d", -5.7, 5.7, -3.4, 3.4, -0.55, 0.9)   # 밑면을 몸통(-0.5)과 다른 높이에 (같은 평면 겹침 방지)
rb = C.bm("erk_roof", "main")
rv = [rb.verts.new(SB.p(*q)) for q in ((-6.0, -3.8, 4.1), (6.0, -3.8, 4.1), (6.0, 3.8, 4.1), (-6.0, 3.8, 4.1),
                                         (-6.0, 0.0, 6.6), (6.0, 0.0, 6.6))]
rfs = [rb.faces.new((rv[0], rv[1], rv[5], rv[4])), rb.faces.new((rv[2], rv[3], rv[4], rv[5])),
       rb.faces.new((rv[3], rv[0], rv[4])), rb.faces.new((rv[1], rv[2], rv[5]))]
bmesh.ops.recalc_face_normals(rb, faces=rfs)
for u in (-3.0, 0.5, 3.6):
    SB.rect(C, "erk_slit", (u, -3.2, 2.2), (0, -1, 0), 1.2, 1.6, lift=0.03)
SB.rect(C, "erk_door_d", (-0.9, -3.2, 1.3), (0, -1, 0), 1.6, 2.4, lift=0.03)
ef.far_flag(ef.city(C), SB.M @ Matrix.Translation((5.4, 3.0, 4.2)), W=1.2, pole=3.2, layers={"cloth": "detail"})
# 성문 앞 돌 기둥 둘 (작은 에르피엔 깃발)
for sx in (-1, 1):
    x, y = P(R_W + 30.0, sx * 15.0)
    z = G.h(x, y)
    C.box("erk_wall_d", x - 0.6, x + 0.6, y - 0.6, y + 0.6, z - 0.3, z + 0.6)
    C.cyl("erk_wall", (x, y, z + 0.6), (x, y, z + 4.2), 0.38, segs=10)
    C.cyl("erk_gold", (x, y, z + 4.2), (x, y, z + 4.5), 0.46, segs=10, kind="detail")
    ef.far_flag(ef.city(C), Matrix.Translation((x, y, z + 4.5)) @ Matrix.Rotation(math.atan2(FO.y, FO.x) + math.pi / 2, 4, "Z"),
                W=1.3, pole=2.2, layers={"cloth": "detail"})

# ---- R41 포위 진지 (버려졌다): 차단벽 줄, 모래주머니 둥지, 컨테이너, 상자, 연료통, 철조망, 구덩이, 불탄 차량, 연기
C.group("siege")
YAW_OUT = math.degrees(math.atan2(FO.x, -FO.y))      # 로컬 -Y = 바깥(남쪽)
for k, lat in enumerate((-14.0, -8.5, 6.5, 12.0)):
    p = P(352.0, lat)
    bk.r41_barrier(C, p[0], p[1], G.h(*p), yaw=YAW_OUT + rng.uniform(-6, 6), w=2.2, col=False)
# 분대가 든 둥지 (-4, 318)는 아래 '분대 엄폐'에서 따로 쌓는다
for (lat, rr) in ((-26.0, 340.0), (20.0, 338.0), (-40.0, 322.0)):
    bk.bag_row(C, P(rr, lat - 2.0), P(rr, lat + 2.0), 0.0, rows=3, zfn=G.h, seed=int(rr + lat) + 500, col=False)
    bk.bag_row(C, P(rr, lat - 2.2), P(rr - 1.6, lat - 2.2), 0.0, rows=2, zfn=G.h, seed=int(rr + lat) + 501, col=False)
    bk.bag_row(C, P(rr, lat + 2.2), P(rr - 1.6, lat + 2.2), 0.0, rows=2, zfn=G.h, seed=int(rr + lat) + 502, col=False)
CPOS = P(330.0, -30.0)
bk.r41_container(C, CPOS[0], CPOS[1], G.h(*CPOS), axis="x", L=5.6, door="+y", label="R41-91", col=False)
for (lat, rr, st) in ((-18.0, 326.0, 2), (-17.0, 325.0, 1), (14.0, 330.0, 1), (24.0, 312.0, 2)):
    x, y = P(rr, lat)
    bk.r41_crate(C, x, y, G.h(x, y), yaw=rng.uniform(-20, 20), stack=st, col=False)
for (lat, rr) in ((26.0, 318.0), (26.6, 318.8), (-36.0, 336.0)):
    x, y = P(rr, lat)
    bk.drum_r41(C, x, y, G.h(x, y), col=False)
x, y = P(321.5, 3.4)
bk.drum_r41(C, x, y, G.h(x, y), lie=True, yaw=YAW_OUT + 70.0, col=False)
sol = bk.Solid("berm")
p3 = (IFV3[0] + FO.x * 4.6, IFV3[1] + FO.y * 4.6)
bk.berm(sol, (p3[0] - TT.x * 3.4, p3[1] - TT.y * 3.4), (p3[0] + TT.x * 3.4, p3[1] + TT.y * 3.4), G.h(*p3) - 0.05,
        (FO.x, FO.y), w=2.4, h=0.75, crest=0.7)
for i, (lat, rr, r) in enumerate(((-10.0, 304.0, 2.4), (14.0, 296.0, 2.2), (-30.0, 300.0, 2.6), (2.0, 330.0, 2.2),
                                  (9.0, 312.0, 1.8))):
    x, y = P(rr, lat)
    bk.crater(C, G, sol, x, y, r, seed=160 + i)
sol.flush(C)
bk.wire_coil(C, G, P(360.0, -30.0), P(360.0, -16.0), seed=93, col=False)
bk.wire_coil(C, G, P(360.0, 9.0), P(360.0, 16.0), seed=94, col=False)
# 불탄 R41 차량 둘 (M9에서 부순 장갑차 자리): 그을린 차체, 불씨, 연기
bk.wreck_raider(C, IFV3[0], IFV3[1], G.h(*IFV3), yaw=YAW_OUT + 12.0, col=False)
bk.wreck_raider(C, WRECK_W[0], WRECK_W[1], G.h(*WRECK_W), yaw=YAW_OUT - 118.0, col=False)
for (x, y, r, s) in ((IFV3[0], IFV3[1], 3.2, 3), (WRECK_W[0], WRECK_W[1], 3.0, 4)):
    bk.ground_disc(C, "soot", x, y, r, G, n=12, rings=2, lift=0.035, seed=s)
bk.smoke(C, *P(296.0, 14.0), G.h(*P(296.0, 14.0)) + 1.0, h=60.0, r=3.0, seed=41, dark=0.55, kind="fine", segs=8, rings=5)
bk.smoke(C, WRECK_W[0] + 0.4, WRECK_W[1], G.h(*WRECK_W) + 1.3, h=22.0, r=1.4, drift=(0.3, 0.12), seed=44, dark=0.7, fire=False,
         kind="fine", segs=7, rings=4)
bk.smoke(C, IFV3[0], IFV3[1] + 0.5, G.h(*IFV3) + 1.4, h=26.0, r=1.5, drift=(0.3, 0.12), seed=45, dark=0.7, fire=False,
         kind="fine", segs=7, rings=4)

# ---- 분대 엄폐: R41이 버린 모래주머니 둥지 (M9 (-4, 318), 남쪽 면을 앞으로 삼는다) + 넘어진 차단벽
C.group("cover")
bk.bag_row(C, P(318.0, -6.0), P(318.0, -2.0), 0.0, rows=3, zfn=G.h, seed=814, col=False)
bk.bag_row(C, P(318.0, -6.2), P(316.4, -6.2), 0.0, rows=2, zfn=G.h, seed=815, col=False)
bk.bag_row(C, P(318.0, -1.8), P(316.4, -1.8), 0.0, rows=2, zfn=G.h, seed=816, col=False)
# 둥지 오른쪽 끝: 한 줄 낮게 터진 주머니 (케이트 앞)
bk.bag_row(C, P(318.25, -1.5), P(318.6, 0.2), 0.0, rows=1, zfn=G.h, seed=817, col=False)
# 왼쪽 (제스티 옆): 옆으로 넘어진 차단벽
L0 = bk.Local((*P(318.9, -8.2), G.h(*P(318.9, -8.2))), YAW_OUT + 78.0)
L0.chbox(C, "r41_shell", (0, 0, 0.21), (2.0, 0.95, 0.42), 0.06)
L0.chbox(C, "r41_light", (0, 0.05, 0.47), (1.86, 0.62, 0.12), 0.04, kind="detail")
L0.rect(C, "amber", (0, -0.476, 0.24), (0, -1, 0), 1.8, 0.07, lift=0.006)
# 터진 주머니에서 쏟아진 모래
bk.ground_disc(C, "sand_spill", *P(318.5, -0.6), 0.55, G, n=9, rings=1, lift=0.03, seed=12)

# ---- 진입로 (성문 → 다리): 생울타리, 건초, 밭담, 철조망 (fin_f 뒤쪽 배경)
C.group("approach")
for side in (-1, 1):
    for r0, r1 in ((462.0, 430.0), (405.0, 372.0)):
        bk.hedgerow(C, G, [P(r0, side * 9.0), P(r1, side * 9.0)], seed=int(r0) + side, h=1.4, col=False)
for i, (lat, rr) in enumerate(((14.0, 440.0), (-8.0, 395.0), (19.0, 380.0), (-14.0, 362.0))):
    x, y = P(rr, lat)
    bk.hay_bale(C, x, y, G.h(x, y), yaw=rng.uniform(0, 90), col=False)
bk.stone_wall(C, G, [P(410.0, 16.0), P(410.0, 46.0)], seed=47, h=0.8, seg=6.0, col=False)
for i in range(4):
    for j in range(3):
        x, y = P(445.0 - i * 13.0, -22.0 - j * 8.5)
        bk.tree_round(C, x, y, G.h(x, y), h=rng.uniform(5.0, 6.2), seed=300 + i * 3 + j, keys=("foliage", "foliage_l", "foliage_d"))

# ---- 성전군 전차 셋 (동쪽 차선 끝, M9 WP_tankN_c 끝점): 승무원은 하늘을 본다
C.group("tanks")
for i, (rr, lat) in enumerate(((358.0, 22.0), (364.0, 34.0), (374.0, 28.0)), 1):
    x, y = P(rr, lat)
    C.prop(f"tank{i}", (x, y, G.h(x, y)), "vehicles/us/m1a1.glb", face=P(rr - 30.0, lat - 3.0), props={"collider": 0})
    bk.ground_disc(C, "mud", x, y, 3.4, G, n=10, rings=2, lift=0.03, seed=20 + i)

# ================================================================== 숲: 진입로 양옆 숲 띠, 성벽 밖 숲 (빈터 주변)
C.group("forest")


def lane_ne(x, y):
    """빈터에서 성벽·세계수 쪽(북북동)으로 트인 숲길 (fin_e 배경): 가운데 폭 약 5 m, 멀수록 조금 넓다."""
    dx, dy = x - CLEAR[0], y - CLEAR[1]
    fwd = dx * math.sin(-Q_E) + dy * math.cos(-Q_E)
    side = dx * math.cos(-Q_E) - dy * math.sin(-Q_E)
    return fwd > 0 and abs(side) < 2.6 + fwd * 0.1


def forest_avoid(x, y):
    r = math.hypot(x - EX, y - EY)
    if r < R_W + 9.0:
        return True                                   # 성벽 바로 밖은 비운다
    if -56.0 < x < 58.0 and y > -170.0:
        return True                                   # 진입로 통로 (M9 보이지 않는 벽 안)
    if d_clear(x, y) < 11.5:
        return True                                   # 빈터
    return lane_ne(x, y)


def sightline(x, y, w=9.0):
    """분대 자리에서 빈터까지의 시선 (fin_d2 끝): 이 띠의 나무는 줄기 높은 활엽수라 줄기 사이로 떨어진 자리가 보인다."""
    a, b = Vector((0.0, 0.6)), Vector(CLEAR)
    p = Vector((x, y))
    t = max(0.0, min(1.0, (p - a).dot(b - a) / (b - a).length_squared))
    return (p - (a + (b - a) * t)).length < w and x < -40.0


NEAR_T = bk.scatter((-150.0, 140.0, -170.0, 72.0), 260, seed=51, min_d=6.5, avoid=forest_avoid)
for i, (x, y) in enumerate(NEAR_T):
    z = G.h(x, y)
    near = math.hypot(x - CLEAR[0], y - CLEAR[1]) < 45.0 or math.hypot(x, y) < 70.0
    kind = "main" if near else "far"
    if sightline(x, y):
        bk.tree_round(C, x, y, z, h=rng.uniform(10.0, 12.5), seed=400 + i, kind=kind)
    elif i % 3:
        bk.conifer(C, x, y, z, h=rng.uniform(9.0, 13.5), seed=400 + i, kind=kind)
    else:
        bk.tree_round(C, x, y, z, h=rng.uniform(8.0, 10.5), seed=400 + i, kind=kind)
# 빈터 둘레: 빽빽한 숲 (반지름 11.5~40 m). 성벽·세계수 쪽(북북동) 숲길만 성기게
GROVE = bk.scatter(lambda r: (CLEAR[0] + r.uniform(-40.0, 40.0), CLEAR[1] + r.uniform(-34.0, 40.0)), 120, seed=61,
                   min_d=3.6, avoid=lambda x, y: (d_clear(x, y) < 11.5 or d_clear(x, y) > 40.0 or x > -55.0
                                                  or math.hypot(x - EX, y - EY) < R_W + 7.0 or lane_ne(x, y)
                                                  or any(math.hypot(x - a, y - b) < 3.0 for a, b in NEAR_T)))
for i, (x, y) in enumerate(GROVE):
    z = G.h(x, y)
    if sightline(x, y):
        bk.tree_round(C, x, y, z, h=rng.uniform(10.0, 12.5), seed=600 + i, keys=("foliage", "foliage_au", "foliage_d"))
    elif i % 4:
        bk.conifer(C, x, y, z, h=rng.uniform(9.5, 14.0), seed=600 + i)
    else:
        bk.tree_round(C, x, y, z, h=rng.uniform(8.0, 10.5), seed=600 + i, keys=("foliage", "foliage_au", "foliage_d"))
# 먼 숲: 성벽 둘레 숲 띠, 남쪽 능선(M9 전망대·숲 내리막), 동서 언덕
C.group("far")


def far_avoid(x, y):
    if inside((-152.0, 142.0, -172.0, 74.0), x, y):
        return True
    if math.hypot(x - EX, y - EY) < R_W + 18.0:
        return True
    return -60.0 < x < 60.0 and -260.0 < y < 74.0


FAR = []
FAR += bk.scatter((-420.0, 360.0, -60.0, 140.0), 150, seed=11, avoid=far_avoid, min_d=10.0)
FAR += bk.scatter((-500.0, 500.0, -560.0, -150.0), 170, seed=12, avoid=far_avoid, min_d=14.0)
FAR += bk.scatter((-1000.0, -320.0, -500.0, 900.0), 70, seed=13, avoid=far_avoid, min_d=30.0)
FAR += bk.scatter((300.0, 1000.0, -500.0, 900.0), 70, seed=14, avoid=far_avoid, min_d=30.0)
bk.far_trees(C, G, FAR[:150], seed=3, h=(14, 22))
bk.far_trees(C, G, FAR[150:], seed=4, h=(12, 19))

# ================================================================== 숲 빈터 (흑뉴아가 떨어진 자리)
C.group("clearing")
cx, cy = CLEAR
hc = G.h(cx, cy)
bk.ground_disc(C, "scorch_e", cx, cy, 4.2, G, n=14, rings=2, lift=0.03, seed=3)
bk.ground_disc(C, "mud", cx, cy, 2.0, G, n=10, rings=1, lift=0.045, seed=4)
# 바깥으로 쓰러진 나무 (부러진 그루터기 + 누운 줄기 + 잎 덩어리)
for i, (dx, dy, L) in enumerate(((-6.5, 3.0, 6.0), (5.5, 5.5, 5.5), (7.5, -2.6, 6.5), (-5.6, -5.0, 5.0), (-1.0, 8.4, 5.5))):
    x, y = cx + dx, cy + dy
    a = math.atan2(dy, dx) + rng.uniform(-0.25, 0.25)
    z = G.h(x, y)
    # 그루터기: 쪼개진 끝 (밝은 속살 원뿔)
    C.cyl("bark_d", (x, y, z - 0.2), (x, y, z + 0.55), 0.26, r2=0.24, segs=7)
    for k in range(3):
        b = a + 2.1 * k
        sx, sy = x + math.cos(b) * 0.1, y + math.sin(b) * 0.1
        C.cyl("splinter", (sx, sy, z + 0.5), (sx + math.cos(a) * 0.08, sy + math.sin(a) * 0.08, z + 0.72 + 0.12 * (k == 0)),
              0.11, r2=0.0, segs=5, smooth=False, kind="detail")
    # 줄기: 그루터기 바깥에서 땅을 따라 눕는다 (땅에 반쯤 걸친 높이)
    x0, y0 = x + math.cos(a) * 0.6, y + math.sin(a) * 0.6
    x1, y1 = x + math.cos(a) * (0.6 + L), y + math.sin(a) * (0.6 + L)
    C.cyl("bark_d", (x0, y0, G.h(x0, y0) + 0.2), (x1, y1, G.h(x1, y1) + 0.14), 0.24, r2=0.14, segs=7)
    C.cyl("splinter", (x0 - math.cos(a) * 0.25, y0 - math.sin(a) * 0.25, G.h(x0, y0) + 0.2), (x0, y0, G.h(x0, y0) + 0.2),
          0.24, segs=7, kind="detail")
    for k in range(3):
        u = 0.55 + 0.2 * k
        bx, by = x + math.cos(a) * (0.6 + L * u), y + math.sin(a) * (0.6 + L * u)
        C.blob(("pine", "pine_d", "foliage_d")[k % 3], (bx, by, G.h(bx, by) + 0.55), rng.uniform(0.9, 1.3), (1.2, 1.0, 0.6),
               segs=7, rings=4, rot_z=a)
# 패인 자리 둘레로 튄 흙덩이·돌 (땅에 반쯤 묻힌다)
for i in range(16):
    a = rng.uniform(0, 2 * math.pi)
    d = rng.uniform(2.6, 5.4)
    x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
    s = rng.uniform(0.16, 0.34)
    C.blob(("rock", "rock_d", "earth")[i % 3], (x, y, G.h(x, y) + s * 0.15), s, (1.3, 1.0, 0.6), segs=7, rings=4,
           rot_z=rng.uniform(0, 3))
mk.flowers(C, cx - 6.5, cy - 6.0, r=1.6, n=5, seed=8, z=G.h(cx - 6.5, cy - 6.0))
C.fx("crash", (cx, cy, hc + 0.3))

# ================================================================== 원경: 에르피엔 왕도 (한가운데 세계수), 연기, 산, 구름
# [원작] 왕국 한가운데 세계수, 밑동을 두른 왕궁, 이중 성벽 (erpien_kit). 성문 둘레는 가까운 세트(city_gate)가 대신한다
C.group("erpien")
ek.haze("#e9b79c", 0.2)          # 해 질 녘 원경 (M9와 같다)
ERP = ek.erpien(C, EX, EY, 0.0, ERP_H, hfun=G.h, face=FACE, kind="far", detail=0, seed=11, lit="lamp_warm", density=0.85,
                skip=GP["skip"])
# 결전 자리 위 수관 밑면: 원경 수관의 밑판은 납작해서 가까운 하늘 컷(올려다봄·망원)에 평평한 벽처럼 보인다.
# 결전 둘레에만 같은 잎 색의 덩어리를 매달아 밑면에 결을 준다 (밑은 결전보다 6 m 넘게 위, 네르가 내려오는 길은 비운다)
a_sky = math.atan2(SKY.y - EY, SKY.x - EX)
r_sky = math.hypot(SKY.x - EX, SKY.y - EY)
NER0 = Vector((SKY.x, SKY.y + 15.0, SKY.z + 13.0))
for i in range(16):
    for _t in range(30):
        a = a_sky + rng.uniform(-0.2, 0.2)
        rr = rng.uniform(r_sky - 70.0, r_sky + 26.0)
        x, y = EX + math.cos(a) * rr, EY + math.sin(a) * rr
        lr = rng.uniform(14.0, 26.0)
        bottom = rng.uniform(131.5, 136.0)
        zc = bottom + lr * 0.32
        q = Vector((x, y, zc))
        # 하늘 기준점 바로 위·네르 길 위는 비운다
        if (q.xy - SKY.xy).length < lr + 7.0 and bottom < 134.0:
            continue
        d = (q - SKY)
        along = d.dot((NER0 - SKY).normalized())
        if 0 < along < (NER0 - SKY).length + lr and (d - (NER0 - SKY).normalized() * along).length < lr + 3.0:
            continue
        C.blob(("eld_leaf_d", "eld_leaf", "eld_leaf_d", "eld_leaf")[i % 4], (x, y, zc), lr, (1.3, 1.0, 0.32), segs=12,
               rings=6, kind="far", rot_z=rng.uniform(0, 3))
        break
for i, (dx, dy, hh) in enumerate(((-90.0, -70.0, 170.0), (200.0, -100.0, 150.0), (-20.0, 130.0, 190.0))):
    bk.smoke(C, EX + dx, EY + dy, 0.0, h=hh, r=12.0, drift=(0.25, 0.06), seed=20 + i, dark=0.6, segs=6, rings=3, kind="fine")
C.group("far")
bk.far_mountains(C, [((-1870, 380), (-470, 1330), 7, (150, 260)), ((-270, 1430), (1130, 1330), 7, (190, 330)),
                     ((1330, 1180), (2180, -20), 6, (140, 240)), ((-2170, -520), (-1870, -1620), 4, (100, 170)),
                     ((2130, -920), (2030, -1720), 4, (100, 160))], G.h, seed=7)
C.group("sky")
for i, (x, y, z, s) in enumerate(((-620, 780, 420, 220), (450, 580, 370, 170), (1280, 230, 340, 190),
                                  (-1420, 100, 310, 180), (-120, 1330, 470, 260))):
    bk.cloud(C, x, y, z, size=s, seed=i)

# ================================================================== 사람들
C.group("npc")
RIFLE = "weapons/us/m4a1.glb"
SHOTGUN = "weapons/us/m870.glb"
LOOK = (SKY.x, SKY.y)
# 분대: 둥지 뒤에 무릎을 꿇고 성벽 너머 하늘을 본다 (lat, r)
SQUAD = {
    "rita": ((-3.9, 319.35), "characters/rita.glb", "cine_crouch_rifle", RIFLE),
    "sabre": ((-5.3, 319.6), "characters/squad_sabre.glb", "cine_kneel_rifle", RIFLE),
    "rona": ((-2.2, 319.5), "characters/squad_rona.glb", "cine_kneel_aim", RIFLE),
    "jesty": ((-6.75, 320.45), "characters/squad_jesty.glb", "cine_kneel_rifle", RIFLE),
    "karen": ((-0.45, 320.2), "characters/squad_karen.glb", "cine_kneel_rifle", SHOTGUN),
}
for nid, ((lat, rr), model, pose, gun) in SQUAD.items():
    x, y = P(rr, lat)
    C.npc(nid, (x, y, G.h(x, y)), model, pose=pose, face=(LOOK[0] + lat * 3.0, LOOK[1]), name=nid,
          props={"hold_R": gun, "expr": "serious", "scene": "fin_a,fin_d2,fin_f"})

# 하늘: 예전 세트에서 맞춘 인물·카메라 간격을 그대로 옮긴다 (예전 하늘 기준점 (6.2, 112.6, 23), 분대가 정남쪽).
# 지금 분대는 하늘에서 남남동(약 8°)이라 그만큼 돌린다
_D = Vector((-SKY.x, -SKY.y)).normalized()           # 하늘 → 분대
ROT = math.atan2(_D.y, _D.x) - math.atan2(-1.0, 0.0)
_c, _s = math.cos(ROT), math.sin(ROT)


def sky(x, y, z):
    """예전 세트 좌표 → 지금 하늘 (기준점 기준으로 옮기고 돌린다)."""
    dx, dy, dz = x - 6.2, y - 112.6, z - 23.0
    return (SKY.x + dx * _c - dy * _s, SKY.y + dx * _s + dy * _c, SKY.z + dz)


def sky2(x, y):
    return sky(x, y, 23.0)[:2]


# 흑뉴아가 에르핀을 들어 올렸다 (분대 쪽을 본다)
C.npc("black_renewa", sky(6.2, 113.3, 22.6), "characters/black_renewa.glb", pose="cine_br_raise", face=sky2(6.2, 100.0),
      name="흑뉴아", props={"expr": "rage", "scene": "fin_a,fin_b,fin_c,fin_d,fin_d2"})
C.npc("erpin", sky(6.2, 112.35, 22.3), "characters/erpin.glb", pose="cine_fin_dangle", face=sky2(6.2, 130.0), name="에르핀",
      props={"expr": "pained", "scene": "fin_a,fin_b"})
# 각성한 에르핀 (사용자 확정 2026-11-01: 각성 전투복 erpin_awakened.glb. 대관식 복장 erpin_royal.glb는 에필로그 전용).
# 모델이 아직 없으면 erpin.glb로 대신하고 장면이 빛 날개를 붙인다 (자리표시, placeholder=1). 섬광 뒤에 바꿔 세운다
C.npc("erpin_awakened", sky(6.2, 110.9, 22.25), "characters/erpin_awakened.glb", pose="cine_awaken", face=sky2(6.2, 130.0),
      name="에르핀", fallback="characters/erpin.glb",
      props={"expr": "serious", "scene": "none", "cameo": "erpin_awakened", "placeholder": 1})
# 네르(엘다인): 흑뉴아 뒤 위에서 내려꽂는다 (장면이 보인다)
C.npc("ner", sky(6.2, 114.7, 23.4), "characters/ner.glb", pose="cine_cast", face=sky2(6.2, 100.0), name="네르",
      props={"expr": "rage", "scene": "none", "cameo": "ner"})
# 빈터: 떨어진 흑뉴아(북쪽을 보고 무릎), 그 앞(북북동, 성벽 쪽)에 내려선 둘
_q = Q_E


def cl(u, v):
    """빈터 로컬 (u = 오른쪽, v = 앞(북북동)) → 월드 xy."""
    return (cx + u * math.cos(_q) - v * math.sin(_q), cy + u * math.sin(_q) + v * math.cos(_q))


for nm, (u, v) in (("br_down", (0.0, 0.2)), ("erpin_land", (-1.45, 2.3)), ("ner_land", (1.55, 2.5))):
    x, y = cl(u, v)
    C.marker(f"WP_{nm}", (x, y, G.h(x, y)))
# 효과 기준점
C.marker("MARK_sky", tuple(SKY))
C.marker("MARK_ner_from", sky(5.0, 128.0, 36.0))
# 우로스의 불꽃: 서쪽에서 동쪽으로 결전 앞을 가로지른다 (수관 밑면 아래로: 예전보다 낮게)
C.marker("MARK_uros_from", sky(-60.0, 96.0, 29.0))
C.marker("MARK_uros_to", sky(40.0, 128.0, 26.0))
# 시온의 탄: 동북동 먼 곳에서 (망원 화면 오른쪽에서 들어와 흑뉴아를 서남서, 성벽 밖 숲으로 밀어낸다)
C.marker("MARK_sion_from", (SKY.x + 620.0, SKY.y + 170.0, SKY.z + 70.0))
C.marker("MARK_clash", sky(6.2, 112.0, 23.4))

# ================================================================== 카메라
z0 = G.h(*SQ0.xy)


def sq(u, v, z):
    """분대 로컬 (u = 오른쪽, v = 성문 쪽) → 월드."""
    p = SQ0.xy + TT * u - FO * v
    return (p.x, p.y, z0 + z)


def sk(dx, dy, dz):
    """하늘 기준점에서 (dx, dy, dz)."""
    return (SKY.x + dx, SKY.y + dy, SKY.z + dz)


# fin_a: 분대 뒤 낮은 곳 (제스티 어깨 너머): 아래에 둥지 뒤 분대, 가운데 성문루, 위쪽 세계수 수관 밑 하늘에 먼 충돌 (앙각 약 38°)
C.cam("fin_a", [
    (0.0, sq(-3.0, -2.4, 0.85), (SKY.x + 6.0, SKY.y, 55.0), 66),
    (8.0, sq(-2.75, -2.0, 0.82), (SKY.x + 5.0, SKY.y, 57.0), 62),
])
# fin_b: 남서쪽 조금 아래에서: 흑뉴아 얼굴, 들린 에르핀 등. 뒤는 수관 밑면과 세계수 큰 가지
C.cam("fin_b", [
    (0.0, sk(-4.35, -8.3, -1.8), sk(0.0, 0.0, 0.4), 34),
    (10.0, sk(-3.35, -7.1, -1.4), sk(0.0, -0.1, 0.4), 30),
])
# fin_c: 남남서 와이드: 뒤로 세계수 줄기와 왕궁 첨탑, 아래 시가 (네르는 뒤 위 수관 밑에서 내리꽂힌다)
C.cam("fin_c", [
    (0.0, sk(-6.15, -16.9, 3.0), sk(0.0, 0.0, 1.3), 42),
    (9.0, sk(-5.6, -15.6, 2.6), sk(0.0, 0.2, 1.0), 40),
])
C.cam("fin_d", [
    (0.0, sky(-3.2, 111.6, 21.0), sky(6.2, 112.0, 23.5), 44),
    (6.0, sky(-2.4, 111.8, 21.3), sky(6.2, 112.0, 23.4), 40),
])
# fin_d2: 성문 앞 망원 (분대 동쪽 끝, 서쪽 문루 탑 깃발을 비켜): 흑뉴아 → 0.8초 시온 탄 → 서남서로 떨어지는 줄기를
#         따라 내려와 성벽 밖 숲에 멈춘다 (빈터 쪽 띠는 줄기 높은 활엽수라 줄기 사이로 마젠타 섬광·흙먼지가 보인다)
FALL = [SKY.lerp(Vector((cx, cy, hc + 1.5)), k) for k in (0.25,)]
C.cam("fin_d2", [
    (0.0, sq(8.0, 0.4, 1.3), sk(0.0, 0.0, -0.6), 6.5),
    (0.85, sq(8.0, 0.4, 1.29), sk(-0.5, -0.3, -1.2), 7.5),
    (1.45, sq(7.95, 0.38, 1.28), tuple(FALL[0]), 20),
    (2.15, sq(7.9, 0.36, 1.27), (cx, cy, hc + 5.0), 30),
    (5.0, sq(7.8, 0.32, 1.25), (cx + 1.0, cy, hc + 4.0), 28),
])
# fin_e: 빈터, 남남서에서: 처음엔 낮게 올려다봐 숲 사이 성벽·왕궁 첨탑·세계수와 위에서 내려오는 둘을 담고,
#        내려선 둘과 앞에 무릎 꿇은 흑뉴아(등)에게로 내려온다
C.cam("fin_e", [
    (0.0, (*cl(0.5, -8.0), hc + 1.6), (*cl(0.0, 5.0), hc + 5.0), 50),
    (3.4, (*cl(0.7, -6.6), hc + 1.45), (*cl(0.0, 1.8), hc + 1.6), 40),
    (10.0, (*cl(0.6, -4.6), hc + 1.45), (*cl(0.0, 1.2), hc + 0.75), 34),
])
# fin_f: 둥지 앞(성문 쪽)에서 분대 얼굴: 뒤로 진입로, 버려진 포위 진지, 동쪽(화면 왼쪽)에 성전군 전차
C.cam("fin_f", [
    (0.0, sq(-0.9, 5.2, 1.2), sq(0.2, 0.3, 0.7), 46),
    (8.0, sq(-0.8, 4.6, 1.15), sq(0.2, 0.35, 0.7), 42),
])

C.group("city")
C.marker("SPAWN_player", sq(0.0, -1.4, 0.0), face=(SKY.x, SKY.y))
ROOT = {
    "sky": "#efb592",              # M9 끝과 같은 해 질 녘 (복숭아빛 하늘 = 안개색)
    "fog": "140,2600",
    "sun": "-0.93,0.24,0.27",      # 서남서의 낮은 해
    "sunColor": "#ffb877",
    "sunIntensity": 2.25,
    "ambient": 1.1,
    "hemiSky": "#cdb8d8",
    "hemiGround": "#6f5d55",
    "physics": 0,
    "near": 0.05,
    "far": 5000,
    "music": "cine_final",
    "timeOfDay": "dusk",
    "scene": "A3_FINALE",
    "shots": "fin_a,fin_b,fin_c,fin_d,fin_d2,fin_e,fin_f",
}
print(f"[cine_finale] 세계수 ({EX:.2f}, {EY:.2f}) 성문 앞면 ({GFRONT.x:.2f}, {GFRONT.y:.2f}) 분대 ({SQ0.x:.2f}, {SQ0.y:.2f}) "
      f"하늘 ({SKY.x:.2f}, {SKY.y:.2f}, {SKY.z:.1f}) 빈터 ({cx:.1f}, {cy:.1f}, {hc:.2f}) "
      f"성벽까지 {math.hypot(cx - EX, cy - EY) - R_W:.1f} m")
for (nm, loc, *_r) in C.markers:
    if nm.startswith(("MARK_", "FX_", "WP_")):
        print(f"[cine_finale] {nm} blender ({loc[0]:.2f}, {loc[1]:.2f}, {loc[2]:.2f}) three ({loc[0]:.2f}, {loc[2]:.2f}, {-loc[1]:.2f})")
C.finish("levels/cine_finale.glb", root_props=ROOT, outline=0.02)
