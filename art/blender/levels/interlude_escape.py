"""인터루드 3 「대탈주」 디오라마 세트 (IL_ESCAPE, docs/script/interlude.md 4.3).

[원작] 엘레나가 노역 중 특별한 칩을 빼돌려 차원 게이트를 조립했고, 그것으로 지구를 탈출했다. 모두가 빠져나가지는
      못했고(남겨진 엘프), 엘레나는 혼자 갈 수도 있었지만 동족을 한 명이라도 더 데려가려 했다. 지구식 화기 약 20정을
      들고 나왔다(나무위키 「엘프(트릭컬 리바이브)」 탈출·주석, 「엘레나(트릭컬 리바이브)/작중 행적」 2.2.10·2.2.13).
[오리지널] 밤의 작업장 창고. 앞쪽은 낮의 그 작업장(작업대·컨베이어), 상자 벽 뒤 빈 공간이 비밀 작업장이다.
      게이트는 고철 고리에 컨베이어 롤러, 빼돌린 칩 기판, 자동차 배터리, 크리스마스 전구 줄, 포장 리본으로 묶은 케이블을
      엮어 만들었다(장난감 공장에서 나올 수 있는 재료만). 리타는 서쪽 큰 문 옆에서 망을 보고, 엘프들은 경보와 서치라이트
      속에 운동장에서 문 → 작업장 → 상자 벽 틈 → 게이트로 뛰어든다. 막사 문 앞에 남는 엘프들의 실루엣.
      마지막에 인간 경비 둘이 운동장에서 큰 문으로 달려와 틈으로 뛰어들지만, 엘레나가 저쪽에서 게이트를 닫아 고리는
      꺼진 고철이 된다.

노드
  GATE_off  꺼진 상태 (어두운 램프, 꺼진 전구, 꺼진 화면, 대기 LED). 처음에 보인다
  GATE_on   켜진 상태 (발광 램프·전구, 문 면, 바닥 빛, 화면). hidden=1: 로드 직후 숨긴다. 자식 GATE_on_swirl은 spin으로 돈다
  (게이트 몸체는 zone_secret의 일반 메시로 늘 보인다)
  LIGHT_search_01/02 (서치라이트, sweep), LIGHT_alarm_01..04 (경광등, spin), LIGHT_worklamp (작업등)
  HUMAN_rush_01..02 쫓아오는 인간 경비 플립북 (hidden=1, escape_c·escape_d). 자식 _run_a/_run_b/_<멈춘 자세>,
            경로 WP_yard_nn_01..(escape_c), WP_rush_nn_01..(escape_d)

npm run model -- art/blender/levels/interlude_escape.py   → public/models/levels/interlude_escape.glb
npm run shot -- levels/interlude_escape.glb --views top,34

좌표: 창고 가운데가 원점. 서쪽(-X) 벽에 큰 문, 운동장은 그 너머 서쪽. 게이트는 동쪽(+X) 빈 공간에서 서쪽을 본다.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import interlude_kit as ik  # noqa: E402
import level_kit as lk  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

L = ik.begin("interlude_escape", mode="night")
rnd = random.Random(23)
# 포로 생활부터 탈출 직후까지 엘프들은 주황 죄수복 (docs/scenario.md 인터루드 2번). 무명 엘프는 A/B/C를 돌려 쓴다
RITA_M = "characters/rita_prisoner.glb"
ELENA_M = "characters/elena_prisoner.glb"


def crowd(i):
    """무명 엘프 포로 모델: 번호 i로 prisoner_a/b/c를 돌린다."""
    return f"characters/prisoner_{'abc'[i % 3]}.glb"
W = ik.Frame((0, 0, 0))
WW, WD, WH = 20.0, 12.0, 3.8
GRID = 4.0                                  # 가까운 땅 격자 간격 (ik.grid_lines fine)
GATE_C = Vector((8.2, 0.0, 1.38))
GATE_R = 1.22
BOXWALL_X = 3.8


# ================================================================ 운동장 (서쪽) + 땅
def under_shed(x, y):
    """창고 바닥 판(ik.shed: 방 ±(w/2+0.2, d/2+0.2), 윗면 z=0)과 겹치는 땅 칸의 정점: 1 cm 낮춰 바닥 판과
    같은 평면에 놓이지 않게 한다 (판 밖으로 한 칸까지 완만히 내려간다)."""
    return abs(x - W.o.x) <= WW / 2 + 0.2 + GRID and abs(y - W.o.y) <= WD / 2 + 0.2 + GRID


def height(x, y):
    if under_shed(x, y):
        return -0.01
    if x > -48:
        return 0.0
    return min(1.0, (-48 - x) / 30) * (1.0 + 1.4 * ik.vnoise(x, y, 3))


def keyf(cx, cy):
    if -46 < cx < 12 and -24 < cy < 24:
        return "gravel" if ik.vnoise(cx * 3, cy * 3, 5) > -0.25 else "gravel_d"
    return "grass_d" if ik.vnoise(cx, cy, 7) > -0.2 else "grass"


L.zone("yard")
xs = ik.grid_lines(-220, 120, near=(-40, 12), fine=GRID, grow=1.4, maxstep=50)
ys = ik.grid_lines(-160, 160, near=(-22, 22), fine=GRID, grow=1.4, maxstep=50)
ik.terrain(L, xs, ys, height, keyf)
# 바퀴 자국·물웅덩이(달빛 반사) 데칼
for i in range(6):
    x, y = rnd.uniform(-36, -14), rnd.uniform(-14, 14)
    pts = [(math.cos(a) * rnd.uniform(0.8, 1.3) * 1.6, math.sin(a) * rnd.uniform(0.7, 1.1)) for a in
           [k * math.pi / 6 for k in range(12)]]
    L.decal("moonwin" if i % 2 else "dirt_d", pts, (x, y, 0.0), (0, 0, 1), lift=0.012)
# 철망 (서쪽 끝) + 감시탑 2기 (서치라이트 켜짐, 창고 쪽으로 쓸어 온다)
ik.chain_fence(L, ik.Frame((-46, -30, 0), 90), 60, h=2.7, sp=0.3, barbs=False)
# 서치라이트는 망루의 지역 -Y 쪽에 달린다: 탑을 돌려 빛이 운동장을 향하게 한다
# 01은 막사 문 앞(남는 엘프들)을 비춘다 → 창고 안에서 보면 역광 실루엣
ik.watchtower(L, ik.Frame((-40.0, 14.0, 0), yaw=51.5), light="search_01", light_on=True,
              aim=(0.0, -1.0, -0.31), sweep=(-35, 35))
ik.watchtower(L, ik.Frame((-38.0, -18.0, 0), yaw=137.8), light="search_02", light_on=True, aim=(0.0, -1.0, -0.34),
              sweep=(-30, 30))
ik.human(L, (-40.0, 14.2, 6.65), -110, pose="aim", tone=1)
ik.human(L, (-38.2, -18.0, 6.65), -60, pose="stand", tone=1)
# 막사 (운동장 건너편) — 창에 불, 문 앞에 남는 엘프들
L.zone("barracks")
for i, (x, y) in enumerate(((-34.0, -1.0), (-34.0, 12.5))):
    F = ik.Frame((x, y, 0), yaw=0)
    ik.quonset(L, F, length=12.0, R=3.2, door_ends=(False, True), windows=3, interior=False, lit=True)
# 운동장 경광등 기둥 + 가로등
L.zone("yard")
for i, (x, y) in enumerate(((-24.0, 9.0), (-22.0, -11.0))):
    L.cyl("pipe", (x, y, 0), (x, y, 4.2), 0.07, verts=8)
    ik.alarm_light(L, f"alarm_{i + 3:02d}", (x, y, 4.2), on=True)
for x, y in ((-16.0, 6.5), (-16.0, -6.5)):
    L.cyl("pipe", (x, y, 0), (x, y, 5.0), 0.07, verts=8)
    L.cyl("pipe", (x, y, 5.0), (x + 0.8, y, 5.3), 0.05, verts=6, kind="detail")
    L.cyl("lampshade", (x + 0.85, y, 5.3), (x + 0.85, y, 5.15), 0.05, r2=0.28, verts=10)
    L.obj("lamp_on", cb.sphere("b", radius=0.1, loc=(x + 0.85, y, 5.12), segments=8, rings=5))
    L.decal("haze", hw.circle(2.6, 16), (x + 0.85, y, 0.0), (0, 0, 1), lift=0.02)
# 인간 경비들 (초점 나간 실루엣): 막사 쪽에서 뛰어온다
for i, (x, y, yaw, pose) in enumerate(((-30.0, 13.5, -100, "walk"), (-29.0, 15.2, -95, "ready"),
                                       (-31.5, -16.0, -70, "walk"))):
    ik.human(L, (x, y, 0.0), yaw, pose=pose, tone=1)
# 밤하늘: 달 + 별 (안개에 반쯤 묻힘) + 먼 언덕·나무
L.zone("land")
MOON = Vector((-120, 70, 70))
md = (Vector((0, 0, 0)) - MOON).normalized()
L.decal("moonwin", hw.circle(7, 20), tuple(MOON), tuple(md), lift=0.0)
L.decal("moonbeam", hw.circle(16, 20), tuple(MOON - md * 1), tuple(md), lift=0.0)
for i in range(130):
    a = rnd.uniform(math.radians(100), math.radians(260))
    e = rnd.uniform(math.radians(8), math.radians(70))
    r = 125
    p = Vector((math.cos(a) * math.cos(e) * r, math.sin(a) * math.cos(e) * r, math.sin(e) * r))
    n = (-p).normalized()
    L.decal("star_w", hw.circle(rnd.uniform(0.18, 0.45), 4), tuple(p), tuple(n), lift=0.0)
ik.hills_ring(L, (0, 0), 120, 150, 10, h=(10, 24), seed=12, arc=(110, 250))
for i, (x, y) in enumerate(((-70, 30), (-64, -40), (-80, 0), (-90, 50), (-75, -70), (-95, -20))):
    s = rnd.uniform(0.9, 1.3)
    ik.tree(L, (x, y, height(x, y)), h=7 * s, r=3.2 * s, seed=i)

# ================================================================ 창고 (작업장 + 비밀 공간)
L.zone("work")
ik.shed(L, W, WW, WD, WH, ridge=1.6,
        wins=[("n", -6.5, 1.5, 2.7, 1.6), ("n", -2.5, 1.5, 2.7, 1.6), ("s", -6.5, 1.5, 2.7, 1.6),
              ("s", -2.5, 1.5, 2.7, 1.6), ("s", 1.5, 1.5, 2.7, 1.6)],
        doors=[("w", 0.0, 3.2, 2.8)], pane="moonwin", beam="moonbeam", beam_dir=(0.45, 1.0, -0.9),
        lamps=[(-6.0, 0.0), (-1.0, 0.0)], lamp_on=False, truss_pitch=3.3, beam_sides="s")
# 큰 미닫이 문짝 (열려서 바깥 북쪽으로 밀려 있음) + 레일
F = W.sub(-WW / 2 - 0.16, 0, 0, 0)
F.box(L, "corr_d", -0.06, 0.06, 1.7, 5.0, 0.05, 2.95)
for k in range(8):
    F.box(L, "corr", -0.08, -0.06, 1.75 + k * 0.4, 1.95 + k * 0.4, 0.1, 2.9, kind="detail")
F.box(L, "pipe", -0.12, 0.12, -1.8, 5.2, 3.0, 3.08, kind="detail")
# 문 위 경광등 2개 (안·밖)
ik.alarm_light(L, "alarm_01", W.p(-WW / 2 - 0.2, -2.1, 3.1), on=True)
ik.alarm_light(L, "alarm_02", W.p(-WW / 2 + 0.25, 2.1, 3.1), on=True)
# 작업대 (북쪽, 작업자 쪽 = 남쪽 통로). 그 아래 엘레나가 칩을 숨긴다
B = W.sub(-4.6, 1.6, 0, 0)
ik.workbench(L, B, 7.0, back=True)
BT = 0.86
for i in range(8):
    x = -7.6 + i * 0.85
    ik.pcb(L, W, x, 2.05 + rnd.uniform(-0.05, 0.05), BT, rot=rnd.uniform(-20, 20), seed=40 + i)
for i, x in enumerate((-7.2, -5.0, -2.8)):
    ik.parts_bin(L, W, x, 2.3, BT, key="od", fill=("pcb", "toy_skin", "chip")[i])
for x in (-6.4, -3.6):
    ik.santa_doll(L, W, x, 1.85, BT, stage="body", rot=rnd.uniform(-40, 40))
    ik.santa_doll(L, W, x + 0.3, 1.95, BT, stage="head", rot=rnd.uniform(-60, 60))
ik.drink_can(L, W, -5.3, 1.9, BT, lie=True, rot=70)
# 작업대 위 작업등 (LIGHT_worklamp: 켜짐, 낮게)
WL = W.p(-4.2, 2.25, BT)
L.cyl("can_k", WL, (WL[0], WL[1], WL[2] + 0.02), 0.07, verts=10)
L.cyl("pipe", (WL[0], WL[1], WL[2] + 0.02), (WL[0], WL[1] - 0.2, WL[2] + 0.42), 0.012, verts=5, kind="detail")
L.cyl("lampshade", (WL[0], WL[1] - 0.2, WL[2] + 0.42), (WL[0], WL[1] - 0.42, WL[2] + 0.33), 0.06, r2=0.11, verts=12)
g = ik.Group(L, "LIGHT_worklamp", pivot=(WL[0], WL[1] - 0.44, WL[2] + 0.32),
             props={"kind": "lamp", "on": 1, "emissiveToggle": 1, "color": ik.EGLOW["lamp_on"], "group": "work"})
g.obj("lamp_on", cb.sphere("wl", radius=0.07, loc=(WL[0], WL[1] - 0.43, WL[2] + 0.33), scale=(1, 1, 0.5),
                           segments=10, rings=5))
lkb = g.bm("sunbeam")
lk.bm_cone(lkb, (WL[0], WL[1] - 0.45, WL[2] + 0.3), (0, -0.45, -1), 0.08, 0.45, 0.42, segs=12)
g.done()
L.decal("haze", hw.circle(0.42, 14), W.p(-4.2, 1.85, BT), (0, 0, 1), lift=0.003)
# 컨베이어 (남쪽, 멈춤): 선물 상자 몇 개
CY, CZ = -3.6, 0.74
W.box(L, "belt", -8.4, 1.6, CY - 0.32, CY + 0.32, CZ - 0.04, CZ)
for sy in (-1, 1):
    W.box(L, "od", -8.5, 1.7, CY + sy * 0.36 - 0.04, CY + sy * 0.36 + 0.04, CZ - 0.14, CZ + 0.06)
for i in range(10):
    x = -8.2 + i * 1.0
    for sy in (-1, 1):
        W.box(L, "pipe", x - 0.03, x + 0.03, CY + sy * 0.3 - 0.03, CY + sy * 0.3 + 0.03, 0.0, CZ - 0.12)
for i in range(6):
    x = -7.6 + i * 1.5 + rnd.uniform(-0.2, 0.2)
    ik.gift(L, W, x, CY, CZ, w=0.32, d=0.3, h=0.24, rot=rnd.uniform(-20, 20), wrap=("toy_red", "toy_green")[i % 2])
# 쓰러진 의자, 바닥에 떨어진 장갑·인형 (급히 떠난 흔적)
ik.santa_doll(L, W, -1.0, -1.6, 0.0, lie=True, rot=40)
ik.santa_doll(L, W, 1.8, 0.9, 0.0, lie=True, rot=-70)
W.rbox(L, "wood", (0.6, -1.9, 0.2), (0.4, 0.4, 0.04), (80, 0, 30))
W.rbox(L, "wood_d", (0.6, -1.7, 0.05), (0.36, 0.04, 0.1), (0, 0, 30), kind="detail")

# 상자 벽 (x≈3.8): 포장 상자를 천장 가까이 쌓아 뒤 공간을 가린다. 가운데 틈에 반쯤 걷힌 방수포
L.zone("boxwall")
GAP = (-0.85, 0.85)
for row in range(7):
    z = row * 0.42
    y = -WD / 2 + 0.05
    while y < WD / 2 - 0.3:
        w = rnd.uniform(0.5, 0.85)
        if row < 5 and y < GAP[1] and y + w > GAP[0]:
            y = GAP[1] + 0.02
            continue
        jitter = rnd.uniform(-0.06, 0.06)
        ik.cardboard(L, W, BOXWALL_X + jitter, y + w / 2, z, w=0.6, d=w - 0.03, h=0.4, rot=rnd.uniform(-3, 3),
                     label="XMAS" if rnd.random() < 0.18 else None)
        y += w
# 틈 위 가로대 + 방수포
W.box(L, "wood_d", BOXWALL_X - 0.35, BOXWALL_X + 0.35, GAP[0] - 0.3, GAP[1] + 0.3, 2.05, 2.15)
# 방수포: 틈의 왼쪽 절반을 덮고 아래 끝이 옆으로 걷혀 있다 (두께 있는 판)
def _tarp(b):
    top, bot = [], []
    for k in range(9):
        t = k / 8
        y = GAP[1] + 0.3 - t * 0.95
        dz = math.sin(t * 9) * 0.04
        zb = 0.08 + 1.7 * t ** 1.4            # 아래 끝이 비스듬히 걷혀 올라간다
        top.append(b.verts.new(W.p(BOXWALL_X - 0.38 + dz, y, 2.04)))
        bot.append(b.verts.new(W.p(BOXWALL_X - 0.4 + dz, y + 0.15 * (1 - t), zb)))
    for i in range(8):
        b.faces.new((top[i], top[i + 1], bot[i + 1], bot[i]))


tarp = ik.obj_from_bm(_tarp, "tarp")
cb.solidify(tarp, 0.02, offset=0.0)
L.obj("tarp", tarp)
L.text("toy_white", "XMAS", 0.16, W.p(BOXWALL_X - 0.42, GAP[1] + 0.12, 1.6), (-1, 0, 0), lift=0.01)

# ================================================================ 비밀 작업장: 차원 게이트
L.zone("secret")
C = GATE_C
R = GATE_R
AX = Matrix.Rotation(math.radians(90), 4, "Y")   # 고리 축 = X (서쪽을 본다)


def on_ring(r, a, dx=0.0):
    """고리 면(YZ) 위 점: 각 a(라디안, 0 = 위)."""
    return Vector((C.x + dx, C.y + math.sin(a) * r, C.z + math.cos(a) * r))


# 고리 몸체: 굵은 고철 관 + 안쪽 구리 코일 + 바깥 롤러
L.obj("metal", hw.torus("ring", R, 0.15, loc=tuple(C), rot=(0, 90, 0), seg=32, rseg=8, mat=None))
L.obj("copper", hw.torus("coil", R - 0.17, 0.045, loc=tuple(C + Vector((-0.06, 0, 0))), rot=(0, 90, 0), seg=32,
                         rseg=6, mat=None), kind="detail")
for i in range(16):       # 구리 감은 띠
    a = i / 16 * 2 * math.pi
    p = on_ring(R, a)
    t = Vector((0, math.cos(a), -math.sin(a)))
    L.cyl("copper", tuple(p - t * 0.06), tuple(p + t * 0.06), 0.175, verts=10, kind="detail")
for i in range(12):       # 바깥 롤러 (컨베이어에서 뜯어 옴)
    a = (i + 0.5) / 12 * 2 * math.pi
    p = on_ring(R + 0.24, a)
    t = Vector((0, math.cos(a), -math.sin(a)))
    L.cyl("roller", tuple(p - t * 0.2), tuple(p + t * 0.2), 0.06, verts=8, kind="detail")
    L.cyl("pipe", tuple(on_ring(R + 0.12, a)), tuple(p), 0.025, verts=4, kind="detail", cap=False)
# 칩 기판 8장 (고리 앞면에 방사형으로) — 빼돌린 칩
for i in range(8):
    a = (i + 0.5) / 8 * 2 * math.pi
    p = on_ring(R + 0.02, a, dx=-0.17)
    n = Vector((-1, 0, 0))
    up = Vector((0, math.sin(a), math.cos(a)))
    rt = n.cross(up)
    M3 = Matrix((rt, up, -n)).transposed()
    o = cb.box("pcbr", size=(0.22, 0.14, 0.012), loc=(0, 0, 0))
    o.matrix_world = Matrix.Translation(p) @ M3.to_4x4()
    L.obj("pcb", o, kind="detail")
    for k in (-1, 1):
        o = cb.box("chipr", size=(0.05, 0.05, 0.012), loc=(k * 0.05, 0, -0.01))
        o.matrix_world = Matrix.Translation(p) @ M3.to_4x4() @ o.matrix_basis
        L.obj("chip", o, kind="fine")
# 받침: 팔레트 2단 + A자 다리 + 모래주머니(포장 자루)
for k in range(2):
    z = k * 0.14
    for j in range(5):
        W.box(L, "plank", C.x - 0.6, C.x + 0.6, -0.95 + j * 0.45, -0.75 + j * 0.45, z + 0.1, z + 0.14)
    for j in range(3):
        W.box(L, "wood_d", C.x - 0.6 + j * 0.55, C.x - 0.5 + j * 0.55, -1.0, 1.0, z, z + 0.1)
for sy in (-1, 1):
    L.cyl("pipe", (C.x - 0.4, sy * 1.0, 0.28), (C.x, sy * 0.55, C.z - R - 0.05), 0.04, verts=6)
    L.cyl("pipe", (C.x + 0.4, sy * 1.0, 0.28), (C.x, sy * 0.55, C.z - R - 0.05), 0.04, verts=6)
    for k in range(3):
        L.obj("tarp", cb.sphere("bag", radius=0.22, loc=(C.x - 0.3 + k * 0.3, sy * 1.15, 0.38),
                                 scale=(1.2, 0.8, 0.55), segments=8, rings=5))
# 포장 리본으로 묶은 케이블 다발 (고리 → 배터리, 고리 → 콘솔)
BAT = [(C.x + 1.1, -2.0 + k * 0.45) for k in range(4)] + [(C.x + 1.1, 1.0 + k * 0.45) for k in range(3)]
for i, (bx, by) in enumerate(BAT):
    W.box(L, "battery", bx - 0.18, bx + 0.18, by - 0.13, by + 0.13, 0.0, 0.24)
    W.cyl(L, "cable_r", (bx - 0.08, by, 0.24), (bx - 0.08, by, 0.28), 0.025, verts=6)
    W.cyl(L, "can_k", (bx + 0.08, by, 0.24), (bx + 0.08, by, 0.28), 0.025, verts=6)
    W.box(L, "can_y", bx - 0.181, bx + 0.181, by - 0.08, by + 0.0, 0.1, 0.16, kind="fine")


def cable(key, pts, r=0.03):
    for a, b in zip(pts, pts[1:]):
        L.cyl(key, a, b, r, verts=5, kind="detail", cap=False)
    for p in pts[1:-1]:
        L.obj(key, cb.sphere("cj", radius=r, loc=p, segments=5, rings=3), kind="detail")


for i, (bx, by) in enumerate(BAT):
    key = ("cable", "cable_r", "cable_y")[i % 3]
    cable(key, [(bx - 0.1, by, 0.27), (bx - 0.5, by * 0.7, 0.03), (C.x + 0.2, by * 0.35, 0.03),
                (C.x + 0.1, by * 0.15, 0.32), (C.x + 0.05, math.copysign(0.4, by), C.z - R + 0.1)])
CON = Vector((C.x - 1.8, -3.45, 0))
cable("cable", [(C.x - 0.05, -0.6, C.z - R + 0.05), (C.x - 0.3, -0.9, 0.03), (CON.x + 0.3, CON.y + 0.25, 0.03),
                (CON.x + 0.25, CON.y + 0.2, 0.5)], r=0.035)
cable("cable_y", [(C.x - 0.05, 0.6, C.z - R + 0.05), (C.x - 0.6, 0.9, 0.03), (C.x - 1.6, 0.4, 0.03),
                  (CON.x + 0.1, CON.y + 0.3, 0.03), (CON.x, CON.y + 0.25, 0.45)], r=0.03)
for i in range(6):        # 리본 매듭 (케이블 묶음)
    p = Vector((C.x + 0.2 - i * 0.35, -0.75 - 0.1 * i, 0.05))
    L.obj("ribbon" if i % 2 else "toy_red", cb.sphere("rb", radius=0.05, loc=tuple(p), scale=(1.4, 0.6, 0.6),
                                                       segments=6, rings=4), kind="detail")
# 콘솔: 나무 상자 책상 + CRT + 자판 + 칼날 스위치 + 산타 인형 마스코트
Fc = ik.Frame(tuple(CON), 35)
Fc.box(L, "wood", -0.45, 0.45, -0.3, 0.3, 0.0, 0.6)
for zz in (0.2, 0.4):
    Fc.box(L, "wood_d", -0.46, 0.46, -0.31, 0.31, zz - 0.015, zz + 0.015, kind="detail")
Fc.box(L, "plastic_g", -0.22, 0.22, -0.05, 0.3, 0.6, 0.98)
Fc.box(L, "plastic_g", -0.16, 0.16, 0.18, 0.36, 0.64, 0.92)
Fc.box(L, "can_k", -0.18, 0.18, -0.06, -0.05, 0.66, 0.94, kind="fine")
Fc.box(L, "plastic_g", -0.25, 0.15, -0.3, -0.12, 0.6, 0.63)
for k in range(10):
    Fc.box(L, "toy_white", -0.23 + k * 0.038, -0.2 + k * 0.038, -0.27, -0.15, 0.63, 0.645, kind="fine")
Fc.box(L, "can_k", 0.22, 0.38, -0.25, -0.1, 0.6, 0.66)
Fc.cyl(L, "pipe", (0.3, -0.18, 0.66), (0.3, -0.05, 0.95), 0.015, verts=5, kind="detail")
L.obj("toy_red", Fc.place(cb.sphere("knob", radius=0.035, loc=(0.3, -0.05, 0.96), segments=8, rings=5)),
      kind="detail")
ik.santa_doll(L, Fc, 0.0, 0.15, 0.98, s=0.9, rot=180)
for k in range(3):
    Fc.box(L, "tape", -0.24, 0.24, 0.1 + k * 0.05 - 0.01, 0.1 + k * 0.05 + 0.01, 0.975, 0.985, kind="fine")
# 크리스마스 전구 줄이 고리를 감는다 (켜고 끄는 전구는 GATE_off/on에)
BULBS = []
for i in range(40):
    t = i / 40
    a = t * 2 * math.pi
    tw = t * 2 * math.pi * 9
    base = on_ring(R, a)
    off = Vector((math.cos(tw) * 0.2, 0, 0)) + Vector((0, math.sin(a), math.cos(a))) * (math.sin(tw) * 0.2)
    BULBS.append(base + off)
for a, b in zip(BULBS, BULBS[1:] + BULBS[:1]):
    L.cyl("toy_green", tuple(a), tuple(b), 0.008, verts=3, kind="fine", cap=False)

# 게이트 꺼짐 상태
LAMPS = [(i + 0.25) / 10 * 2 * math.pi for i in range(10)]
goff = ik.Group(L, "GATE_off", pivot=tuple(C), props={"state": "off", "toggle": "GATE_on",
                                                      "note": "처음에 보인다. 가동 순간 숨기고 GATE_on을 켠다"})
for a in LAMPS:
    goff.obj("gate_off", cb.sphere("lp", radius=0.075, loc=tuple(on_ring(R - 0.09, a, dx=-0.13)), scale=(0.6, 1, 1),
                                   segments=8, rings=5))
for k, p in enumerate(BULBS):
    goff.obj("bulb_off", cb.sphere("bo", radius=0.028, loc=tuple(p), segments=5, rings=3))
o = cb.box("scr", size=(0.3, 0.012, 0.22), loc=(0, -0.058, 0.79))
o.matrix_world = Fc.M @ o.matrix_basis
goff.obj("screen_off", o)
goff.obj("led_r", Fc.place(cb.sphere("led", radius=0.015, loc=(0.36, -0.2, 0.67), segments=6, rings=4)))
goff.done()
# 게이트 켜짐 상태 (처음엔 숨김)
gon = ik.Group(L, "GATE_on", pivot=tuple(C), props={"state": "on", "toggle": "GATE_off", "hidden": 1,
                                                    "note": "처음에 숨긴다. 켤 때 GATE_off를 숨긴다"})
for a in LAMPS:
    gon.obj("gate_core", cb.sphere("lp", radius=0.085, loc=tuple(on_ring(R - 0.09, a, dx=-0.135)),
                                   scale=(0.6, 1, 1), segments=8, rings=5))
for k, p in enumerate(BULBS):
    gon.obj(("bulb_r", "bulb_y", "bulb_g")[k % 3], cb.sphere("bn", radius=0.031, loc=tuple(p), segments=5, rings=3))
o = cb.box("scr", size=(0.3, 0.012, 0.22), loc=(0, -0.06, 0.79))
o.matrix_world = Fc.M @ o.matrix_basis
gon.obj("gate", o)
gon.obj("led_g", Fc.place(cb.sphere("led", radius=0.016, loc=(0.36, -0.2, 0.67), segments=6, rings=4)))
# 문 면 (원판) + 안쪽 빛 테 + 바닥 빛 + 빛기둥
disc = gon.bm("portal")
lk.bm_ring(disc, hw.circle(R - 0.14, 32), hw.circle(0.001, 32), tuple(C + Vector((-0.02, 0, 0))), (-1, 0, 0))
lk.bm_ring(gon.bm("gate"), hw.circle(R - 0.11, 32), hw.circle(R - 0.17, 32), tuple(C + Vector((-0.04, 0, 0))),
           (-1, 0, 0))
spill = gon.bm("spill")
pts = [(math.cos(a) * 1.4 - 1.5, math.sin(a) * 2.0) for a in [k * math.pi / 12 for k in range(24)]]
lk.bm_ring(spill, [(u, v) for u, v in pts], [(u * 0.02 - 1.5, v * 0.02) for u, v in pts],
           tuple(Vector((C.x, 0, 0.03))), (0, 0, 1), up=(0, 1, 0))
lk.bm_cone(gon.bm("gate_beam"), tuple(C + Vector((-0.05, 0, 0))), (-1, 0, -0.12), R * 0.9, R * 1.45, 3.2, segs=20)
gon_root = gon.done()
# 소용돌이 (GATE_on_swirl: spin으로 돈다)
gsw = ik.Group(L, "GATE_on_swirl", pivot=tuple(C), props={"spin": "140,0,0", "note": "문 면 소용돌이"})
for k in range(4):
    r0 = 0.18 + k * 0.24
    for j in range(3):
        a0 = j * 2 * math.pi / 3 + k * 0.7
        arc_o = [(math.sin(a0 + t * 1.5) * (r0 + 0.07 + t * 0.12), math.cos(a0 + t * 1.5) * (r0 + 0.07 + t * 0.12))
                 for t in [i / 8 for i in range(9)]]
        arc_i = [(math.sin(a0 + t * 1.5) * (r0 + t * 0.12), math.cos(a0 + t * 1.5) * (r0 + t * 0.12))
                 for t in [i / 8 for i in reversed(range(9))]]
        bsw = gsw.bm("portal_w")
        vs = [bsw.verts.new((C.x - 0.05, C.y + u, C.z + v)) for (u, v) in arc_o + arc_i]
        f = bsw.faces.new(vs)
        f.normal_update()
        if f.normal.x > 0:
            f.normal_flip()
sw_root = gsw.done()
L.ik_groups.remove(sw_root)
bpy = __import__("bpy")
bpy.context.view_layer.update()
mw = sw_root.matrix_world.copy()
sw_root.parent = gon_root
sw_root.matrix_parent_inverse = Matrix.Identity(4)
sw_root.matrix_world = mw
# 연출 마커
L.marker("FX_gate_core", tuple(C), props={"kind": "portal", "radius": R})
for i, a in enumerate((0.6, 2.2, 3.9, 5.3)):
    L.marker(f"FX_gate_spark_{i + 1:02d}", tuple(on_ring(R + 0.1, a)), props={"kind": "spark"})
L.marker("FX_alarm", W.p(-WW / 2, 0, 3.0), props={"kind": "alarm_sound"})
L.marker("FX_search_sweep", (-30, 0, 0.0), props={"kind": "searchlight_pool"})

# ================================================================ NPC
L.zone("npc")
# 엘레나: 고리 앞에 서서 아래쪽 칩 기판(5번, 손 높이)에 칩을 꽂는다
BOARD5 = on_ring(R + 0.02, (5 + 0.5) / 8 * 2 * math.pi, dx=-0.17)
# 칩은 왼손에 든 채 시작해(hold_L) 몸을 기울여(assemble_insert) 기판 자리 DROP_elena에 꽂는다. 짧은 팔이 닿게 고리에 0.1 m 더 붙였다
CHIP = "props/interlude_chip.glb"
L.npc("elena", (C.x - 0.52, BOARD5.y - 0.12, 0.0), ELENA_M, face=(BOARD5.x + 0.4, BOARD5.y),
      props={"pose": "assemble", "placePose": "assemble_insert", "expr": "serious", "group": "gate", "scene": "escape_b",
             "hold_L": CHIP,
             "note": "서서 두 손을 앞으로: 왼손의 칩을 고리의 칩 기판에 꽂는다. 가동 뒤 IL_ESCAPE_02 '뛰어!' (gesture 손짓)"})
# 꽂힌 칩 자리 (예전 PROP_chip_elena 자리에서 칩의 grip 노드 만큼 옮김: 손이 쥐는 점이 원점이 된다)
L.markers.append(("DROP_elena", (BOARD5.x - 0.052, BOARD5.y + 0.02, BOARD5.z - 0.05),
                  Euler((0, math.radians(-90), 0)), {"slot": "L", "group": "elena_chip",
                                                     "note": "기판에 반쯤 꽂힌 칩 (엘레나가 왼손으로 꽂는다)"}))
L.npc("elena_hide", W.p(-4.4, 2.05, 0.0), ELENA_M, face=W.p(-4.4, 4.0),
      props={"pose": "hide_chip", "expr": "wink", "group": "work", "scene": "escape_a", "hold_R": CHIP,
             "note": "작업대 아래 웅크려 칩을 작업복 안에 숨긴다 (camp_a 컷. NPC_elena와 같은 컷에 쓰지 않는다)"})
L.npc("rita", W.p(-WW / 2 + 0.45, -1.95, 0.0), RITA_M, face=W.p(-WW / 2 - 3, -1.0),
      props={"pose": "lookout", "expr": "serious", "group": "door", "scene": "escape_a,escape_c",
             "note": "큰 문 옆 벽에 등을 붙이고 바깥을 엿본다. IL_ESCAPE_01을 듣는다"})
RUN = [  # 달리는 엘프: 운동장 → 문 → 통로 → 틈 → 게이트
    ("soldier_01", (6.3, 0.15)), ("soldier_02", (3.0, -0.3)), ("soldier_03", (1.0, 0.5)),
    ("soldier_04", (-1.6, -0.4)), ("soldier_05", (-5.0, 0.3)), ("soldier_06", (-9.2, -0.6)),
    ("rita_run", (-12.6, 0.4)), ("soldier_07", (-14.4, -0.8)),
]
for i, (nid, (x, y)) in enumerate(RUN):
    model = RITA_M if nid == "rita_run" else crowd(i)
    nxt = (C.x, 0.0) if x > BOXWALL_X - 0.5 else ((BOXWALL_X, 0.0) if x > -WW / 2 else (-WW / 2, 0.0))
    props = {"pose": "run", "group": "run", "order": i + 1, "scene": "escape_c"}
    if nid == "rita_run":
        props.update({"expr": "serious", "note": "리타는 마지막 무리에 섞여 뛰어든다"})
    L.npc(nid, (x, y, 0.0), model, face=nxt, props=props)
# 로네 (2026-11-02 사용자 확정, 코믹): 무리의 맨 끝. 포로 배식으로 인간 음식(돈까스)에 맛을 들여, 탈출하는 와중에도
# 접시(왼손)와 포크(오른손)를 놓지 못하고 먹으면서 종종걸음으로 뛴다. 무리가 모두 지나간 뒤 홀로 상자 벽 틈 남쪽 절반으로
# 나와 카메라 오른쪽으로 빠진다(몽타주가 걷게 하고 화면 밖에서 숨긴다). 자세 il_escape_run_eat는 interlude.ts가 더한다
L.npc("rone", (-6.8, -0.25, 0.0), "characters/rone_prisoner.glb", face=(BOXWALL_X, -0.3),
      props={"pose": "il_escape_run_eat", "group": "rone", "scene": "escape_c", "expr": "dreamy",
             "hold_L": "props/cine_tonkatsu_plate.glb", "hold_R": "props/cine_fork.glb",
             "note": "돈까스 접시와 포크를 든 채 먹으며 무리 맨 끝에서 게이트로 (escape_c)"})
L.npc("soldier_08", (C.x - 2.0, 0.9, 0.0), crowd(7), face=(BOXWALL_X - 2, 0.0),
      props={"pose": "wave_beckon", "group": "gate", "scene": "escape_b,escape_c", "note": "틈 쪽을 보며 손짓 (빨리!)"})
for i, (x, y) in enumerate(((-21.3, -1.55), (-21.0, -0.7), (-21.5, 0.1))):
    L.npc(f"left_{i + 1:02d}", (x, y, 0.0), crowd(i + 1), face=(-WW / 2, 0.0),
          props={"pose": "stand_watch", "group": "left_behind", "silhouette": 1, "scene": "escape_c",
                 "note": "막사 문 앞에 남는 엘프 (원작: 전원이 탈출하지 못했다). 서치라이트 역광 실루엣"})
for i, (x, y) in enumerate(((-24.0, -1.5), (-26.0, 1.2))):     # 달려오는 무리 (운동장)
    L.npc(f"soldier_{9 + i:02d}", (x, y, 0.0), crowd(8 + i), face=(-WW / 2, 0.0),
          props={"pose": "run", "group": "run", "scene": "escape_c"})

# ================================================================ 뛰어드는 인간 경비 (escape_c 끝 → escape_d)
# 엘프가 모두 넘어간 뒤 경비 둘이 쫓아온다. 초점 나간 실루엣 플립북(ik.human_runner, 역광 tone n):
# HUMAN_rush_nn 아래 run_a/run_b(걸음)와 멈춘 자세. 컷마다 길이 다르다 (첫 경로점에서 나타나 마지막 점에서 멈춘다).
#   escape_c (path_escape_c = yard_nn): 막사 사이에서 나와 서치라이트 속 남는 엘프들 앞을 지나 큰 문으로 달려온다
#   escape_d (path = rush_nn): 작업장을 가로질러 상자 벽 틈(남쪽 절반: 북쪽 절반은 방수포가 머리 높이까지 내려와 있다)으로
#            들어와 게이트로 달려들고, 게이트가 꺼진 뒤 고리 앞에 멈춘다
# 둘 다 총에 전등을 달았다(빛줄기). 맨 앞은 고리 앞에서 총을 내리고, 왼쪽 경비가 겨눠 빈 고리를 비춘다.
# delay(컷 시작 기준, 초)·speed(m/s)·decel(멈추기 전 줄이는 거리, m): 맨 앞이 게이트가 꺼진 직후(2.2초) 고리 앞에 닿게 맞췄다
L.zone("humans")
RUSH = [  # escape_d 경로 (첫 점 = 나타나는 자리, 마지막 = 멈춤), 멈춘 자세, delay, speed, decel, escape_c 경로, delay, speed
    ([(1.2, -0.35), (3.8, -0.35), (5.0, -0.25), (7.35, 0.0)], "ready", 0.2, 4.4, 2.2,
     [(-21.0, 9.2), (-19.4, 3.6), (-14.0, 1.0), (-9.6, 0.35), (-3.0, 0.1)], 6.75, 5.2),
    ([(0.2, -0.35), (3.8, -0.3), (5.1, 0.15), (6.95, 1.15)], "aim", 0.4, 4.4, 1.8,
     [(-21.6, 9.6), (-18.9, 4.4), (-13.6, 1.6), (-9.6, 0.9), (-3.0, 0.6)], 7.05, 5.2),
]
for i, (path, stop, delay, speed, decel, yard, ydelay, yspeed) in enumerate(RUSH):
    hid = f"rush_{i + 1:02d}"
    ik.human_runner(L, f"HUMAN_{hid}", (path[0][0], path[0][1], 0.0), 90, frames=("run_a", "run_b", stop), tone="n", torch=True,
                    props={"path": hid, "stop": stop, "delay": delay, "speed": speed, "decel": decel,
                           "path_escape_c": f"yard_{i + 1:02d}", "delay_escape_c": ydelay, "speed_escape_c": yspeed,
                           "scene": "escape_c,escape_d",
                           "note": "쫓아오는 인간 경비 (플립북). 운동장 → 큰 문(escape_c), 틈 → 게이트(escape_d)"})
    for k, (x, y) in enumerate(path):
        L.marker(f"WP_{hid}_{k + 1:02d}", (x, y, 0.0), props={"kind": "waypoint"})
    for k, (x, y) in enumerate(yard):
        L.marker(f"WP_yard_{i + 1:02d}_{k + 1:02d}", (x, y, 0.0), props={"kind": "waypoint"})

# ================================================================ 카메라 (4컷, 합계 약 30초)
L.zone("cams")
EH = W.p(-4.4, 2.05, 0.55)       # 엘레나(숨김) 머리 높이
RD = W.p(-WW / 2 + 0.45, -1.95, 0.95)
# a. 작업대 밑: 칩을 숨기는 엘레나 → 문 옆에서 망보는 리타 (7초)
L.cam_rail("escape_a", [
    (0.0, W.p(-3.3, 4.6, 0.5), (EH[0], EH[1], 0.45), 36),
    (3.5, W.p(-3.5, 4.7, 0.55), (EH[0] - 0.6, EH[1] - 0.8, 0.5), 36),
    # 작업대 상판 아래로 리타 얼굴이 보이게 낮게 (0.6이면 상판 앞 모서리가 리타 눈높이를 가린다)
    (7.0, W.p(-3.7, 4.75, 0.3), (RD[0] - 0.02, RD[1] + 0.05, RD[2] + 0.05), 26),
])
# b. 상자 벽 틈으로 밀고 들어가 게이트 (7초, 이 컷에서 GATE_off → GATE_on)
L.cam_rail("escape_b", [
    (0.0, (BOXWALL_X - 1.6, 0.1, 1.15), (C.x, 0.0, C.z), 44),
    (2.5, (BOXWALL_X + 0.8, -0.6, 1.05), (C.x - 0.2, -0.3, C.z - 0.1), 42),
    (5.0, (C.x - 2.2, -2.6, 1.05), (C.x - 0.6, -1.0, 0.95), 40),
    # 끝: 고리 남쪽 바깥에서 엘레나 오른쪽 앞 3/4 (2.5 m). 얼굴과 칩 꽂는 손, 오른쪽에 켜진 게이트 빛.
    # 1.2 m에서 옆얼굴을 잡으면 머리카락이 화면 절반을 덮는다
    (7.0, (C.x + 0.7, -3.4, 1.2), (C.x - 0.5, -1.2, 1.05), 40),
])
# c. 게이트 옆에서 뒤돌아본다: 틈으로 뛰어드는 무리, 문 너머 운동장의 서치라이트와 남는 실루엣 (8초) →
#    경비 둘이 남는 엘프들 앞을 지나 큰 문으로 달려오는 동안 줌이 조금 풀린다 (+2초)
L.cam_rail("escape_c", [
    (0.0, (C.x - 1.2, -0.4, 1.05), (-10.0, 0.0, 1.1), 42),
    (4.0, (C.x - 1.3, -0.5, 1.0), (-16.0, -0.6, 1.1), 34),
    (8.0, (C.x - 1.4, -0.6, 0.95), (-21.3, -0.75, 0.75), 15),
    (10.0, (C.x - 1.45, -0.6, 0.95), (-13.0, 0.2, 0.95), 21),
])
# d. 게이트 문 면 클로즈업: 소용돌이 바로 앞 → 경비들이 카메라 밑으로 지나 게이트로 달려드는 동안 뒤 위로 물러나며 내려다본다
#    (사람이 문 면을 가리지 않게) → 게이트가 꺼지고(저쪽에서 닫힘) 꺼진 고리 앞에 멈춘 실루엣들 (5.6초 + 암전)
L.cam_rail("escape_d", [
    (0.0, (C.x - 2.15, 0.22, 1.72), (C.x, -0.02, C.z + 0.04), 36),
    (2.0, (C.x - 3.45, 0.45, 2.8), (C.x - 0.35, 0.0, C.z - 0.26), 48),
    (5.6, (C.x - 3.6, 0.52, 2.92), (C.x - 0.35, 0.0, C.z - 0.33), 50),
])

ROOT = {
    "sky": "#0e1428",
    "fog": "35,240",
    "sun": "-0.45,0.8,-0.4",
    "ambient": 0.9,
    "music": "interlude_strings",
    "sunColor": "#9fb2e0",
    "sunIntensity": 0.9,
    "hemiSky": "#4a5a8a",
    "hemiGround": "#191a24",
    "timeOfDay": "night",
    "scene": "IL_ESCAPE",
    "shots": "escape_a,escape_b,escape_c,escape_d",
    "physics": 0,
}
ik.finish(L, "levels/interlude_escape.glb", root_props=ROOT, outline=0.01)
