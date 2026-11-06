"""인터루드 2 「포로 생활」 디오라마 세트 (IL_CAMP, docs/script/interlude.md 4.2).

[원작] 엘프들은 수십 년 동안 지구인의 지배 아래 기술과 노동력을 착취당했다. 노동은 납땜과 부품 조립 같은 단순 노동,
      주 5일·하루 8시간. 크리스마스 장난감을 1년 내내 조립·포장·상하차했다(엘레나 테마극장). 점심 돈까스는 맛있었지만
      저녁은 메뉴판과 달리 콩자반이 나왔다는 불평, 붕붕드링크를 억지로 마셨다는 이야기, 크리스마스·산타 트라우마
      (나무위키 「엘프(트릭컬 리바이브)」 포로 생활·주석, 「엘레나(트릭컬 리바이브)/작중 행적」 2.2.3).
[오리지널] 미군식 수용소: 퀀셋(반원통) 막사와 인간 규격 이층 침대, 골함석 작업장의 긴 작업대(엘프는 나무 상자를 딛고
      선다), 선물 상자가 흐르는 컨베이어, 한여름 창빛, 벽 달력, 이중 철망과 감시탑. 해 질 녘 철망 너머 하늘을 보는 리타.

세 구역 (카메라 컷 하나씩)
  barracks  퀀셋 막사 안: 이층 침대 줄, 매단 전등              → camp_a
  work      작업장 안: 작업대·컨베이어·포장대, 동쪽 벽 달력·창    → camp_b (끝에서 달력으로 돈다)
  yard      운동장과 이중 철망, 감시탑, 해 질 녘 하늘 배경판     → camp_c

npm run model -- art/blender/levels/interlude_camp.py   → public/models/levels/interlude_camp.glb
npm run shot -- levels/interlude_camp.glb --views top,34

좌표: 철망이 y=-8에서 X를 따라 서고 바깥(남쪽)이 -Y. 막사는 y≈6, 작업장은 (6, 22) 중심.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import interlude_kit as ik  # noqa: E402
from mathutils import Vector  # noqa: E402

L = ik.begin("interlude_camp", mode="day")
rnd = random.Random(11)
# 포로 생활부터 탈출 직후까지 엘프들은 주황 죄수복 (docs/scenario.md 인터루드 2번). 무명 엘프는 A/B/C를 돌려 쓴다
RITA_M = "characters/rita_prisoner.glb"
CATHY_M = "characters/cathy_prisoner.glb"


def crowd(nid):
    """무명 엘프 포로 모델: soldier_NN의 번호로 prisoner_a/b/c를 돌린다."""
    return f"characters/prisoner_{'abc'[(int(nid[-2:]) - 1) % 3]}.glb"


FENCE_Y = -8.0
RITA = (2.0, -7.35, 0.0)


W = ik.Frame((6.0, 22.0, 0))                # 작업장 (camp_b)
WW, WD, WH = 16.0, 10.0, 3.6
GRID = 3.0                                  # 가까운 땅 격자 간격 (ik.grid_lines fine)


# ================================================================ 땅
def under_shed(x, y):
    """작업장 바닥 판(ik.shed: 방 ±(w/2+0.2, d/2+0.2), 윗면 z=0)과 겹치는 땅 칸의 정점: 1 cm 낮춰 바닥 판과
    같은 평면에 놓이지 않게 한다 (판 밖으로 한 칸까지 완만히 내려간다)."""
    return abs(x - W.o.x) <= WW / 2 + 0.2 + GRID and abs(y - W.o.y) <= WD / 2 + 0.2 + GRID


def height(x, y):
    if under_shed(x, y):
        return -0.01
    if y > FENCE_Y - 5:
        return 0.0
    k = min(1.0, (FENCE_Y - 5 - y) / 30)
    return k * (1.2 + 1.6 * ik.vnoise(x, y, 2))


def keyf(cx, cy):
    if cy > FENCE_Y - 0.4 and -24 < cx < 28:
        return "gravel" if ik.vnoise(cx * 3, cy * 3, 4) > -0.3 else "gravel_d"
    if FENCE_Y - 4.6 < cy <= FENCE_Y - 0.4:
        return "dirt_l"                      # 철망 사이 맨땅
    n = ik.vnoise(cx * 1.4, cy * 1.4, 6)
    return "grass" if n > -0.1 else ("grass_d" if n > -0.5 else "wheat_d")


L.zone("yard")
xs = ik.grid_lines(-200, 200, near=(-26, 30), fine=GRID, grow=1.35, maxstep=40)
ys = ik.grid_lines(-220, 120, near=(-14, 32), fine=GRID, grow=1.35, maxstep=40)
ik.terrain(L, xs, ys, height, keyf)
for i in range(60):
    x, y = rnd.uniform(-24, 28), rnd.uniform(FENCE_Y - 18, FENCE_Y - 4.8)
    ik.tuft(L, (x, y, height(x, y)), s=rnd.uniform(0.25, 0.45), seed=i, key=rnd.choice(("grass_d", "wheat_d")))
for i in range(16):
    x, y = rnd.uniform(-20, 26), rnd.uniform(FENCE_Y + 0.3, FENCE_Y + 0.9)
    ik.tuft(L, (x, y, 0.0), s=rnd.uniform(0.15, 0.3), seed=100 + i, key="grass_d")

# 이중 철망: 안쪽(리타 앞, 촘촘한 마름모 + 윤형 철조망) + 바깥쪽
FI = ik.Frame((-24, FENCE_Y, 0))
ik.chain_fence(L, FI, 52, h=2.7, dense=(22.5, 29.0), concertina=(20.0, 31.0))
FO = ik.Frame((-24, FENCE_Y - 4.6, 0))
ik.chain_fence(L, FO, 52, h=2.9, net=True, sp=0.3, barbs=False)
for x0, yaw in ((-24, 90), (28, 90)):        # 옆 울타리 (북쪽으로)
    ik.chain_fence(L, ik.Frame((x0, FENCE_Y, 0), yaw), 40, h=2.7, barbed=False, sp=0.4)
# 철망 경고판 (글자만, 실존 기관 표기 없음)
for i, x in enumerate((-12.0, 12.0)):
    c = (x, FENCE_Y - 0.06, 1.35)
    L.box("toy_white", x - 0.32, x + 0.32, FENCE_Y - 0.05, FENCE_Y - 0.03, 1.12, 1.58)
    L.decal("toy_red", hw.rrect(0.6, 0.1, 0.01), (x, FENCE_Y - 0.05, 1.5), (0, -1, 0), lift=0.004)
    L.text("ink", "RESTRICTED AREA", 0.055, (x, FENCE_Y - 0.05, 1.33), (0, -1, 0), lift=0.004)
    L.text("ink", "NO ENTRY", 0.07, (x, FENCE_Y - 0.05, 1.22), (0, -1, 0), lift=0.004)

# 감시탑 2기 (해 질 녘: 서치라이트 꺼짐) + 탑 위 인간 경비 실루엣
ik.watchtower(L, ik.Frame((-20.0, FENCE_Y + 1.8, 0), yaw=-20), light="search_01", light_on=False,
              aim=(0.3, 1.0, -0.4))
ik.watchtower(L, ik.Frame((24.5, FENCE_Y + 1.8, 0), yaw=25), light="search_02", light_on=False, aim=(-0.3, 1.0, -0.4))
ik.human(L, (-20.0, FENCE_Y + 1.6, 6.65), 160, pose="stand", tone=1)
# 운동장 가로등 (꺼짐) 두 개
for x, y in ((-6.0, -1.0), (12.0, -1.5)):
    L.cyl("pipe", (x, y, 0), (x, y, 5.2), 0.07, verts=8)
    L.cyl("pipe", (x, y, 5.2), (x, y - 0.8, 5.5), 0.05, verts=6, kind="detail")
    L.cyl("lampshade", (x, y - 0.85, 5.5), (x, y - 0.85, 5.35), 0.05, r2=0.28, verts=10)
    L.obj("lamp_off", cb.sphere("b", radius=0.1, loc=(x, y - 0.85, 5.32), segments=8, rings=5))
# 빨랫줄 (막사 옆): 엘프 크기 작업복
for x0 in (-15.5,):
    L.cyl("pipe", (x0, 1.3, 0), (x0, 1.3, 1.9), 0.04, verts=6)
    L.cyl("pipe", (x0 + 5, 1.3, 0), (x0 + 5, 1.3, 1.9), 0.04, verts=6)
    L.cyl("cable", (x0, 1.3, 1.85), (x0 + 5, 1.3, 1.8), 0.01, verts=4, kind="fine")
    for i in range(6):
        x = x0 + 0.5 + i * 0.75
        k = rnd.choice(("hull", "olive", "blanket", "toy_white"))
        L.rbox(k, (x, 1.3, 1.55), (0.42, 0.04, 0.5 if i % 2 else 0.36), (0, 0, rnd.uniform(-4, 4)))

# 바깥 풍경: 나무, 언덕, 전봇대, 하늘 배경판, 구름, 새
L.zone("land")
for i, (x, y) in enumerate([(-40, -40), (-28, -55), (30, -48), (48, -38), (-60, -30), (12, -70), (-8, -82),
                            (70, -60), (-80, -70), (40, 60), (-50, 50), (10, 80)]):
    s = rnd.uniform(0.8, 1.3)
    ik.tree(L, (x, y, height(x, y)), h=7 * s, r=3.2 * s, seed=i)
ik.hills_ring(L, (0, 0), 150, 190, 9, h=(10, 26), seed=8, arc=(15, 165))
ik.power_line(L, [(x, -30 + 0.05 * x) for x in range(-120, 140, 40)], height)
SKY_C = Vector((RITA[0], RITA[1], 0))
ik.sky_backdrop(L, SKY_C, 78, 192, 348, -4, [("sky_dusk_0", 7), ("sky_dusk_1", 9), ("sky_dusk_2", 13),
                                               ("sky_dusk_3", 17), ("sky_dusk_4", 30)], seg=28)
# 지는 해 (서남서, 지평선 바로 위) + 번짐
SUN = Vector((-58, -46, 5.5))
sd = (SKY_C - SUN).normalized()
L.decal("sun_disc", hw.circle(4.2, 20), tuple(SUN), tuple(sd), lift=0.0)
L.decal("haze", hw.circle(9, 20), tuple(SUN + sd * 0.5), tuple(sd), lift=0.0)
for i, (x, y, z, s) in enumerate([(-30, -66, 22, 12), (10, -70, 30, 16), (40, -58, 18, 10), (-55, -45, 14, 9),
                                  (60, -40, 26, 12)]):
    ik.cloud(L, (x, y, z), size=s, seed=20 + i, keys=("sky_dusk_1", "sky_dusk_3"))
for i in range(7):  # 새 (철망 너머 자유의 상징)
    x, y, z = -6 + i * 2.3 + rnd.uniform(-1, 1), -40 + rnd.uniform(-4, 4), 15 + rnd.uniform(-2, 3)
    s = rnd.uniform(0.35, 0.55)
    L.poly("hum_1", [(x - s, y, z + s * 0.35), (x, y, z), (x - s * 0.15, y, z - s * 0.12)], normal=(0, 1, 0))
    L.poly("hum_1", [(x, y, z), (x + s, y, z + s * 0.35), (x + s * 0.15, y, z - s * 0.12)], normal=(0, 1, 0))
L.marker("FX_birds", (0, -40, 15), props={"kind": "birds", "dir": "-1,0,0.1"})

# ================================================================ 막사 (퀀셋) — camp_a
L.zone("barracks")
HR = 3.6
FA = ik.Frame((-15.0, 6.0, 0))
ik.quonset(L, FA, length=14.0, R=HR, door_ends=(True, True), windows=3, lit=True)
ik.quonset(L, ik.Frame((1.5, 6.0, 0)), length=14.0, R=HR, door_ends=(True, False), windows=3, interior=False)
BUNK_X = [2.0, 5.0, 8.0, 11.0]
for i, bx in enumerate(BUNK_X):
    for side, yy, yaw in ((0, -2.35, 180), (1, 2.35, 0)):
        ik.bunk_bed(L, FA.sub(bx, yy, 0, yaw), messy=(i + side) % 3, seed=i * 2 + side)
        # 침대 밑 개인 상자 + 벽 못에 건 수건
        S = FA.sub(bx + 0.55, yy * 0.86, 0, yaw)
        S.box(L, "od", -0.25, 0.25, -0.2, 0.2, 0.0, 0.26)
        S.box(L, "od_d", -0.26, 0.26, -0.21, 0.21, 0.22, 0.26, kind="detail")
for lx in (2.5, 7.0, 11.5):
    ik.hanging_lamp(L, FA.p(lx, 0, HR - 0.05), drop=0.9, on=True)
# 가운데 통로 끝의 난로와 연통 (퀀셋 막사의 상징)
st = FA.p(13.0, 0.0, 0)
L.cyl("can_k", st, (st[0], st[1], 0.75), 0.32, verts=12)
L.cyl("pipe", (st[0], st[1], 0.75), (st[0], st[1], HR + 0.6), 0.08, verts=8)
L.obj("ember", cb.sphere("glow", radius=0.06, loc=(st[0] - 0.33, st[1], 0.3), segments=6, rings=4))
# 침대 옆 의자와 붕붕드링크 빈 캔
for i, (x, y) in enumerate(((3.6, -1.3), (9.4, 1.4))):
    S = FA.sub(x, y, 0, 30 * i)
    S.box(L, "wood", -0.2, 0.2, -0.2, 0.2, 0.4, 0.44)
    for sx in (-0.17, 0.17):
        for sy in (-0.17, 0.17):
            S.box(L, "wood_d", sx - 0.02, sx + 0.02, sy - 0.02, sy + 0.02, 0, 0.4, kind="detail")
    ik.drink_can(L, S, 0.05, 0.0, 0.44)
ik.drink_can(L, FA, 6.2, -0.8, 0.0, lie=True, rot=40)
L.npc("soldier_01", FA.p(5.0, -1.45, 0.0), crowd("soldier_01"), yaw=FA.yaw + 180,
      props={"pose": "sit_tired", "seatZ": 0.54, "expr": "pained", "group": "barracks", "scene": "camp_a"})
L.npc("soldier_02", FA.p(8.0, 2.35, 1.62), crowd("soldier_02"), yaw=FA.yaw + 90,
      props={"pose": "lie_sleep", "group": "barracks", "scene": "camp_a", "note": "위 칸 매트리스 위에 눕는다 (머리 = 마커 -Y)"})
L.npc("soldier_03", FA.p(11.0, -1.5, 0.0), crowd("soldier_03"), yaw=FA.yaw + 190,
      props={"pose": "sit_tired", "seatZ": 0.54, "group": "barracks", "scene": "camp_a",
             "prop": "props/interlude_santa_doll.glb",
             "note": "무릎에 만들다 만 산타 인형"})

# ================================================================ 작업장 — camp_b
L.zone("work")
ik.shed(L, W, WW, WD, WH, ridge=1.5,
        wins=[("n", -5.5, 1.35, 2.65, 1.6), ("n", -2.0, 1.35, 2.65, 1.6), ("n", 2.0, 1.35, 2.65, 1.6),
              ("n", 5.5, 1.35, 2.65, 1.6), ("e", -1.6, 1.2, 2.5, 1.3), ("w", 1.0, 1.35, 2.65, 1.6)],
        doors=[("s", -6.0, 1.1, 2.15)], pane="sunwin", beam="sunbeam", beam_dir=(0.35, -1.0, -0.75),
        lamps=[(-5, -1.5), (0, -1.5), (5, -1.5), (-2.5, 2.4), (2.5, 2.4)], lamp_on=True)

# 긴 작업대 (작업자는 +Y 쪽에 서서 카메라(-Y)를 본다)
B = W.sub(0.0, 0.55, 0, 180)
ik.workbench(L, B, 11.0, back=False)
WORK_X = [-4.2, -1.8, 0.6, 3.0]            # 작업자 자리 (작업장 지역 X)
for x in WORK_X:
    ik.step_crate(L, W, x, 0.95, h=0.28)
# 작업대 위: 기판, 부품통, 납땜 인두 받침, 돋보기 등, 인형 몸통·머리, 붕붕드링크
BT = 0.86
for i in range(12):
    x = -5.2 + i * 0.95 + rnd.uniform(-0.1, 0.1)
    ik.pcb(L, W, x, 0.28 + rnd.uniform(-0.05, 0.05), BT, rot=rnd.uniform(-20, 20), chips=rnd.choice((2, 3)), seed=i)
for i, x in enumerate((-4.8, -2.4, 0.0, 2.4, 4.6)):
    ik.parts_bin(L, W, x, -0.05, BT, key=("od", "toy_red", "od", "toy_green", "od")[i],
                 fill=("pcb", "toy_skin", "copper", "toy_white", "chip")[i])
for x in WORK_X:
    # 인두 받침 + 인두
    S = W.sub(x + 0.35, 0.12, BT, 0)
    S.cyl(L, "solder", (0, 0, 0), (0, 0, 0.03), 0.05, verts=8)
    S.cyl(L, "can_k", (0, 0, 0.03), (0.0, 0.09, 0.1), 0.012, verts=5, kind="detail")
    S.cyl(L, "solder", (0.0, 0.09, 0.1), (0.0, 0.16, 0.12), 0.004, verts=4, kind="fine")
    L.cyl("cable_r", S.p(0, 0.0, 0.05), W.p(x + 0.6, -0.25, BT), 0.006, verts=4, kind="fine")
    # 반쯤 된 인형들
    ik.santa_doll(L, W, x - 0.25, 0.3, BT, stage="body", rot=rnd.uniform(-30, 30))
    ik.santa_doll(L, W, x - 0.05, 0.42, BT, stage="head", rot=rnd.uniform(-60, 60))
# 다 된 인형 줄 + 인형 눈 접시 (검은 점) + 붕붕드링크
for i in range(6):
    ik.santa_doll(L, W, -5.4 + i * 0.16, -0.12, BT, rot=180 + rnd.uniform(-10, 10))
for x in (-3.0, 1.7):
    W.cyl(L, "tray", (x, 0.1, BT), (x, 0.1, BT + 0.012), 0.11, verts=12)
    for k in range(9):
        a = k * 0.7
        L.decal("can_k", hw.circle(0.009, 6), W.p(x + math.cos(a) * 0.06 * (k % 3) / 2, 0.1 + math.sin(a) * 0.06 *
                                                   (k % 3) / 2, BT + 0.013), (0, 0, 1), lift=0.001)
for i, x in enumerate((-3.6, -1.1, 2.1, 3.9, 4.15)):
    ik.drink_can(L, W, x, 0.05 + 0.03 * i, BT, lie=i == 4, rot=60 * i)
# 돋보기 스탠드 등
for x in (-3.0, 1.2):
    W.cyl(L, "can_k", (x, -0.15, BT), (x, -0.15, BT + 0.02), 0.07, verts=10)
    W.cyl(L, "pipe", (x, -0.15, BT + 0.02), (x, 0.05, BT + 0.45), 0.012, verts=5, kind="detail")
    W.cyl(L, "pipe", (x, 0.05, BT + 0.45), (x, 0.3, BT + 0.38), 0.012, verts=5, kind="detail")
    W.cyl(L, "lampshade", (x, 0.3, BT + 0.38), (x, 0.3, BT + 0.32), 0.09, verts=12)
    W.cyl(L, "lamp_on", (x, 0.3, BT + 0.315), (x, 0.3, BT + 0.31), 0.075, verts=12)

# 컨베이어 (작업자 뒤, 북쪽 창 아래): 선물 상자와 인형이 흐른다
CY, CZ = 2.75, 0.74
W.box(L, "belt", -6.6, 6.2, CY - 0.32, CY + 0.32, CZ - 0.04, CZ)
for sy in (-1, 1):
    W.box(L, "od", -6.7, 6.2, CY + sy * 0.36 - 0.04, CY + sy * 0.36 + 0.04, CZ - 0.14, CZ + 0.06)   # 모터 상자 면까지
for i in range(14):
    x = -6.4 + i * 0.95
    for sy in (-1, 1):
        W.box(L, "pipe", x - 0.03, x + 0.03, CY + sy * 0.3 - 0.03, CY + sy * 0.3 + 0.03, 0.0, CZ - 0.12)
    W.cyl(L, "roller", (x, CY - 0.33, CZ - 0.06), (x, CY + 0.33, CZ - 0.06), 0.035, verts=6, kind="detail")
W.box(L, "od_d", 6.2, 6.8, CY - 0.4, CY + 0.4, 0.0, CZ + 0.1)     # 모터 상자
W.box(L, "hazard", 6.195, 6.805, CY - 0.41, CY + 0.41, CZ - 0.02, CZ + 0.04, kind="detail")
for i in range(11):
    x = -6.0 + i * 1.12 + rnd.uniform(-0.1, 0.1)
    if i % 3 == 1:
        ik.santa_doll(L, W, x, CY, CZ, rot=rnd.uniform(0, 360), s=1.1)
    else:
        ik.gift(L, W, x, CY + rnd.uniform(-0.08, 0.08), CZ, w=rnd.uniform(0.26, 0.4), d=rnd.uniform(0.26, 0.36),
                h=rnd.uniform(0.16, 0.3), rot=rnd.uniform(-15, 15), wrap=rnd.choice(("toy_red", "toy_green")),
                ribbon=rnd.choice(("ribbon", "toy_white")))
# 포장대 (동쪽): 상자 탑, 크리스마스 나무 견본, 선풍기(한여름)
P0 = W.sub(5.6, -2.4, 0, 0)
P0.box(L, "bench", -1.0, 1.0, -0.5, 0.5, 0.82, 0.88)
for sx in (-0.92, 0.92):
    for sy in (-0.42, 0.42):
        P0.box(L, "pipe", sx - 0.03, sx + 0.03, sy - 0.03, sy + 0.03, 0, 0.82)
ik.cardboard(L, P0, -0.45, 0.05, 0.88, open_=True, w=0.5, d=0.42, h=0.3)
ik.santa_doll(L, P0, -0.45, 0.05, 1.08, s=1.0)
P0.cyl(L, "can_k", (0.35, -0.15, 0.88), (0.35, -0.15, 0.96), 0.07, verts=10)        # 테이프 디스펜서
P0.cyl(L, "tape", (0.35, -0.15, 0.96), (0.35, -0.15, 0.99), 0.05, verts=10)
# 선풍기
P0.cyl(L, "pipe", (0.6, 0.25, 0.88), (0.6, 0.25, 1.2), 0.015, verts=6, kind="detail")
P0.cyl(L, "can_k", (0.6, 0.25, 0.88), (0.6, 0.25, 0.9), 0.09, verts=10)
P0.cyl(L, "plastic_g", (0.6, 0.2, 1.3), (0.6, 0.31, 1.3), 0.15, verts=14)
P0.cyl(L, "pipe", (0.6, 0.18, 1.3), (0.6, 0.19, 1.3), 0.155, verts=14, kind="detail", r2=0.155)
# 쌓인 완성 상자 (상하차 대기)
for i in range(3):
    for j in range(3 - (i == 2)):
        ik.cardboard(L, W, 7.0 - 0.0 * i, -4.1 + j * 0.46, 0.36 * i, w=0.55, d=0.44, h=0.36,
                     rot=rnd.uniform(-4, 4), label="XMAS" if (i + j) % 2 == 0 else None)
# 크리스마스 나무 견본 (원뿔 3단 + 금별 + 전구)
T = W.sub(-6.8, -3.6, 0, 0)
T.box(L, "box", -0.25, 0.25, -0.25, 0.25, 0, 0.22)
for k, (r, z0, z1) in enumerate(((0.55, 0.25, 0.85), (0.43, 0.7, 1.2), (0.3, 1.05, 1.5))):
    T.cyl(L, "leaf_d" if k % 2 else "toy_green", (0, 0, z0), (0, 0, z1), r, r2=0.04, verts=10)
L.obj("toy_gold", T.place(cb.sphere("star", radius=0.07, loc=(0, 0, 1.55), scale=(1, 0.4, 1), segments=5, rings=3)))
for k in range(10):
    a = k * 1.3
    z = 0.4 + k * 0.1
    r = 0.5 - k * 0.04
    L.obj(("bulb_r", "bulb_y", "bulb_g")[k % 3],
          T.place(cb.sphere("b", radius=0.03, loc=(math.cos(a) * r, math.sin(a) * r, z), segments=5, rings=3)))
# 서쪽 벽 선반
ik.shelf_unit(L, W.sub(-7.6, 2.4, 0, -90), w=1.8, d=0.45, h=2.0, seed=4)
ik.shelf_unit(L, W.sub(-7.6, -0.2, 0, -90), w=1.8, d=0.45, h=2.0, seed=9, fill=("box", "od", "box_d"))

# 벽: 근무 안내, 크리스마스 D-day, 저녁 메뉴(돈까스 → 콩자반), 화환, 장식 줄
Fn = ik.Frame(W.p(0, WD / 2 - 0.0, 0), W.yaw)     # 북쪽 벽 면 y=0, 앞(-Y) = 남쪽 = 방 안 (지역 X = 월드 X)
ik.board(L, Fn, 0.0, 3.12, 1.4, 0.55, [("크리스마스까지", 0.42, 1.0, None), ("D-173", -0.35, 2.4, "toy_red")],
         size=0.1, key="chalk")
ik.board(L, Fn, -3.7, 3.12, 1.2, 0.5, [("근무: 주 5일", 0.4, 1.0, None), ("1일 8시간", -0.35, 1.0, None)],
         size=0.1, key="toy_white", text_key="ink", frame="od_d")
# 화환 (북쪽 벽, 창 사이)
for xw in (-3.75, 3.75):
    c = Fn.p(xw, -0.03, 2.25)
    ring_o = hw.circle(0.24, 14)
    ring_i = hw.circle(0.14, 14)
    L.ring("toy_green", ring_o, ring_i, c, Fn.d(0, -1, 0), lift=0.0)
    L.decal("toy_red", hw.circle(0.05, 8), Fn.p(xw, -0.035, 2.03), Fn.d(0, -1, 0), lift=0.002)
# 반짝이 장식 줄 (북쪽 벽 위, 처짐)
for i in range(16):
    x0, x1 = -7.5 + i * 0.94, -7.5 + (i + 1) * 0.94
    # 게시판(위 끝 3.44) 위로 지나가게 트러스 높이에 건다
    za = 3.5 - 0.04 * math.sin(math.pi * ((i % 4) / 4))
    zb = 3.5 - 0.04 * math.sin(math.pi * (((i + 1) % 4) / 4 if (i + 1) % 4 else 0))
    L.cyl("toy_gold" if i % 2 else "toy_red", Fn.p(x0, -0.06, za), Fn.p(x1, -0.06, zb), 0.025, verts=5, kind="detail")
# 동쪽 벽: 달력(CAL_page_01..12, 7월부터), 저녁 메뉴판
Fe = ik.Frame(W.p(WW / 2, 0, 0), W.yaw - 90)    # 동쪽 벽 면, 앞(-Y) = 서쪽 = 방 안. 지역 X = 월드 -Y
ik.calendar(L, Fe, -0.55, 2.45, 12, first=6, crossed=[31, 31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 12])
ik.board(L, Fe, -1.95, 1.88, 0.9, 0.62, [("오늘의 저녁", 0.5, 0.85, None), ("돈까스", 0.0, 1.5, None),
                                       ("(콩자반)", -0.55, 0.9, "toy_red")], size=0.085, key="chalk")
# 메뉴판 아래 실제 저녁: 식판 위 콩자반
S = W.sub(6.7, 1.95, 0, 0)
S.box(L, "bench", -0.35, 0.35, -0.25, 0.25, 0.7, 0.74)
S.box(L, "pipe", -0.03, 0.03, -0.03, 0.03, 0, 0.7)
S.box(L, "tray", -0.22, 0.22, -0.16, 0.16, 0.74, 0.76)
S.cyl(L, "toy_white", (-0.08, 0, 0.76), (-0.08, 0, 0.8), 0.08, verts=10)
for k in range(9):
    a = k * 2.1
    L.obj("bean", S.place(cb.sphere("bean", radius=0.016, loc=(-0.08 + math.cos(a) * 0.035 * (k % 3) / 2,
                                                                 math.sin(a) * 0.035 * (k % 3) / 2, 0.805),
                                     scale=(1.2, 1, 0.8), segments=5, rings=3)), kind="fine")
S.cyl(L, "solder", (0.1, 0.05, 0.76), (0.12, -0.1, 0.77), 0.006, verts=4, kind="fine")      # 숟가락
ik.drink_can(L, S, 0.15, 0.08, 0.76)

# NPC: 작업자 (나무 상자를 딛고 인간 높이 작업대에서 일함)
WORKERS = [("soldier_04", "work_bench", {}), ("cathy", "work_doll",
           {"model": CATHY_M, "expr": "smirk", "gesture": "인형들기",
            "hold_R": "props/interlude_santa_doll.glb", "holdRot_R": "-90,0,0",
            "note": "IL_CAMP_01~02: 만들던 산타 인형을 오른손에 세워 들고 있다가(work_doll) 들어 보인다"}),
           ("soldier_05", "work_bench", {}), ("soldier_06", "work_bench", {})]
for (nid, pose, extra), x in zip(WORKERS, WORK_X):
    model = extra.pop("model", None) or crowd(nid)
    props = {"pose": pose, "group": "work", "standOn": "crate", "standZ": 0.28, "scene": "camp_b"}
    props.update(extra)
    L.npc(nid, W.p(x, 0.95, 0.28), model, yaw=W.yaw + rnd.uniform(-5, 5), props=props)
L.npc("soldier_07", W.p(5.0, 1.75, 0.0), crowd("soldier_07"), yaw=W.yaw + 90,
      props={"pose": "carry_box", "group": "work", "scene": "camp_b", "prop": "gift", "note": "선물 상자를 안고 포장대로"})
L.npc("soldier_08", W.p(-6.2, -1.5, 0.0), crowd("soldier_08"), yaw=W.yaw - 70,
      props={"pose": "sit_tired", "seatZ": 0.28, "group": "work", "scene": "camp_b", "note": "상자에 앉아 붕붕드링크를 든 채 졸음"})
ik.step_crate(L, W, -6.2, -1.45 + 0.3, h=0.28)

# ================================================================ 철망 앞 리타 — camp_c
L.zone("yard")
L.npc("rita", RITA, RITA_M, yaw=-4,
      props={"pose": "look_up", "expr": "weary", "group": "fence", "scene": "camp_c",
             "note": "해 질 녘 철망 너머 하늘을 본다. IL_ARRIVAL에서 같은 구도로 반복"})
# 리타 발치: 작은 돌 몇 개, 철망 아래 들풀 한 송이 (밖)
for i in range(5):
    x, y = RITA[0] + rnd.uniform(-0.8, 0.8), RITA[1] + rnd.uniform(-0.2, 0.5)
    ik.rock(L, (x, y, 0.0), s=rnd.uniform(0.04, 0.09), seed=50 + i, key="gravel_d")
L.cyl("grass_d", (RITA[0] + 0.3, FENCE_Y - 0.25, 0), (RITA[0] + 0.32, FENCE_Y - 0.25, 0.32), 0.008, verts=4,
      kind="detail")
L.obj("can_y", cb.sphere("flower", radius=0.03, loc=(RITA[0] + 0.32, FENCE_Y - 0.25, 0.33), segments=6, rings=4),
      kind="detail")

# ================================================================ 카메라 (3컷, 합계 약 22초)
L.zone("cams")
# a. 막사 안: 문 쪽에서 통로를 따라 (6초)
L.cam_rail("camp_a", [
    (0.0, FA.p(0.9, 0.35, 1.3), FA.p(9.0, -0.4, 0.95), 52),
    (3.0, FA.p(2.2, 0.1, 1.2), FA.p(10.0, -0.6, 0.85), 50),
    (6.0, FA.p(3.4, -0.1, 1.1), FA.p(11.0, -1.2, 0.8), 46),
])
# b. 작업장: 작업대를 따라 옆으로 → 동쪽 벽 달력 (8초)
L.cam_rail("camp_b", [
    (0.0, W.p(-6.2, -2.4, 1.05), W.p(-4.0, 1.0, 1.05), 44),
    (3.5, W.p(-2.0, -2.6, 1.1), W.p(0.2, 1.0, 1.05), 42),
    (6.0, W.p(2.6, -2.2, 1.25), W.p(5.4, 0.4, 1.35), 40),
    # 끝: 메뉴판 정면 쪽에서 (벽 기둥이 메뉴판 글씨를 가리지 않게) 메뉴판과 달력을 함께
    (8.0, W.p(5.3, 2.0, 1.8), Fe.p(-1.25, 0.0, 2.1), 40),
])
# c. 철망 앞 리타: 등 뒤 낮은 곳에서 하늘 → 옆으로 돌아 얼굴 (8초)
RF = (RITA[0], RITA[1], 1.02)
L.cam_rail("camp_c", [
    (0.0, (2.55, -5.2, 0.62), (1.4, -40.0, 9.5), 40),
    (4.0, (2.9, -5.6, 0.66), (1.2, -30.0, 6.5), 38),
    # 6초: 왼쪽 뒤에서 리타 머리 너머 하늘을 보며 돈다 (시선 점이 리타 가까이에 있어 도는 동안 리타가 화면에 남는다)
    (6.0, (3.1, -6.6, 0.72), (1.0, -9.5, 1.9), 38),
    # 끝: 철망(y=-8.0) 안쪽에서 3/4 얼굴. 눈높이를 화면 가운데에 두어 턱이 잘리지 않게
    (8.0, (3.3, -7.86, 0.76), (RF[0], RF[1] + 0.05, RF[2] - 0.03), 40),
])

ROOT = {
    "sky": "#5b5e93",
    "fog": "90,320",
    "sun": "-1.0,0.28,0.35",
    "ambient": 1.15,
    "music": "interlude_strings",
    "sunColor": "#ffb27e",
    "sunIntensity": 1.7,
    "hemiSky": "#d9a6a6",
    "hemiGround": "#5a5560",
    "timeOfDay": "dusk",
    "scene": "IL_CAMP",
    "shots": "camp_a,camp_b,camp_c",
    "physics": 0,
}
ik.finish(L, "levels/interlude_camp.glb", root_props=ROOT, outline=0.01)
