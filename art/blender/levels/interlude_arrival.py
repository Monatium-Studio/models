"""인터루드 4 「엘리아스 불시착」: 탈출 게이트가 연 구멍에서 엘프들이 낯선 초원으로 쏟아진다.

npm run model -- art/blender/levels/interlude_arrival.py   → public/models/levels/interlude_arrival.glb

원작: 엘레나가 빼돌린 칩으로 조립한 차원 게이트는 작동했지만, 엘프들은 모성이 아니라 엘리아스에 불시착했다.
엘리아스: 세계수 엘드르가 가운데 선 땅, 원래부터 식생이 나쁜 땅이 아니었다, 고기가 나무에서 열린다,
숲 너머는 안개로 둘러싸여 있다. 모나티엄은 엘리아스 동부(정령산·에르피엔 접경).
'낯선 하늘'은 오리지널 연출: 낮에도 떠 있는 두 개의 달, 지평선 위 세계수.
  arrival_a  와이드: 하늘의 구멍(GATE_escape)에서 떨어지는 엘프들, 지평선의 세계수
  arrival_b  리타: 주저앉은 채 낯선 하늘(두 달)을 올려다본다
  arrival_c  엘레나의 뒷모습 너머 세계수, 뒤로 빠지며 일행 전체
문서: docs/art/interlude-elias.md
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_kit as ek  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("interlude_arrival")
# 세계수 (불시착 자리에서 북쪽 지평선, 약 1.05 km). [원작] 요정 왕국 에르피엔이 세계수 둘레를 두르고 있다: 그 시절에도
# 지평선의 세계수 밑동에 왕궁과 성벽 두른 시가의 실루엣이 보인다 (erpien_kit, 모든 에르피엔 장면과 같은 디자인)
TREE = (80.0, 1050.0)
TREE_H = 420.0

# ---------------------------------------------------------------- 땅과 하늘
C.group("land")
h = mk.terrain(C, radius=360, seed=3, amp=12.0, flat_r=40.0)
C.group("far")
# 세계수 쪽은 지평선까지 낮은 들이다 (불시착 자리 둘레 언덕 밖)
C.cyl("grass", (TREE[0], TREE[1], -8.0), (TREE[0], TREE[1], h(*TREE) - 0.4), TREE_H * 0.95, segs=40, kind="far")
ek.erpien(C, TREE[0], TREE[1], h(*TREE) - 0.4, TREE_H, face=(-TREE[0], -TREE[1]), kind="far", detail=0, seed=11,
          density=0.7)
mk.mountains(C, 0, 0, count=5, dist=470, spread=40, h=(70, 150), seed=5, arc=(-30, 62))
mk.mountains(C, 0, 0, count=5, dist=500, spread=40, h=(60, 120), seed=9, arc=(150, 280))
mk.mountains(C, TREE[0], TREE[1], count=6, dist=560, spread=60, h=(90, 170), seed=21, arc=(10, 170))
mk.haze_wall(C, radius=1450, h=170)              # 엘리아스를 두른 안개 경계 (세계수 너머 지평선)
C.group("sky")
mk.sky_moons(C, (-330, 380, 230), (0.6, -0.65, -0.45), r=70.0, second=(0.42, 140.0, -50.0))
for i, (x, y, z, s) in enumerate(((-120, 260, 120, 34), (120, 330, 150, 40), (-20, 420, 170, 46), (-260, 120, 130, 30),
                                   (260, 60, 120, 30), (-40, -300, 140, 36), (200, -220, 150, 34))):
    mk.cloud(C, x, y, z, size=s, seed=i)
C.group("woods")
for i, (x, y, r, n) in enumerate(((-70, 80, 24, 14), (90, 110, 26, 14), (-120, -20, 22, 10), (110, -40, 22, 10),
                                  (-30, 150, 30, 16), (40, -110, 26, 10), (-90, -110, 26, 10))):
    mk.forest(C, x, y, r=r, n=n, seed=i + 1, hfun=h)

# ---------------------------------------------------------------- 가까운 초원
C.group("meadow")
rng_trees = [(-24, 18, 5.0), (-30, 6, 4.4), (22, 22, 5.2), (28, 10, 4.6), (-18, -20, 4.8), (26, -16, 5.0),
             (-40, 30, 6.0), (40, 34, 5.6), (-8, 40, 5.4), (12, 44, 5.0)]
for i, (x, y, hh) in enumerate(rng_trees):
    mk.tree(C, x, y, h=hh, seed=40 + i, z=h(x, y) - 0.05)
for i, (x, y) in enumerate(((-14, 24), (16, 30), (-26, -4))):
    mk.meat_tree(C, x, y, h=4.6, seed=70 + i, z=h(x, y) - 0.05)
for i, (x, y, r) in enumerate(((-6, -10, 3.5), (10, -6, 2.5), (-16, 10, 3.0), (6, 20, 3.0), (20, 2, 2.2))):
    mk.flowers(C, x, y, r=r, n=16, seed=i, z=h(x, y))
for i, (x, y, s) in enumerate(((-11, 14, 1.4), (13, 15, 1.0), (-20, -12, 1.6), (18, -10, 1.2), (3, 30, 1.8))):
    mk.rock(C, x, y, s=s, seed=i, z=h(x, y))
# 불시착 자국
mk.scorch(C, 0.5, 6.0, 4.0, seed=1)
mk.scorch(C, -4.5, 9.5, 1.6, seed=2)
mk.scorch(C, 4.8, 10.5, 1.3, seed=3)

# ---------------------------------------------------------------- 탈출 게이트의 출구 (하늘의 구멍)
C.group("portal")
PORTAL = (0.5, 11.0, 5.2)
gate = mk.portal_escape(C, "escape", PORTAL, radius=3.4, tilt=-58, yaw=-20)
gate["scenes"] = "arrival_a,arrival_b"        # arrival_c에서는 닫힘 (몽타주가 스케일 0으로)
# 같이 떨어진 짐: 엘피니아 회녹 상자, 지구제 탄약통, 파란 방수포 꾸러미
for i, (x, y, yaw, key) in enumerate(((2.8, 7.2, 20, "olive"), (3.6, 8.0, -15, "olive"), (-2.2, 5.0, 40, "olive"),
                                       (-1.0, 8.6, 70, "tarp"), (5.4, 4.8, 10, "olive"))):
    mk.crate(C, x, y, s=0.6, yaw=yaw, key=key)
C.blob("tarp", (-3.4, 7.2, 0.25), 0.5, (1.2, 0.8, 0.55), segs=10, rings=6)
C.prop("ammo_01", (1.6, 3.6, 0), "props/us_ammo_can.glb", yaw=35)
C.prop("ammo_02", (-0.6, 2.8, 0), "props/us_ammo_can.glb", yaw=-60)
# 떨어지는 중인 상자 (게이트 바로 아래, drift로 천천히 떨어짐 → 몽타주가 리셋)
C.group("FALLING", drift="0,-1.2,0")
mk.crate(C, 0.8, 9.6, s=0.55, yaw=30, z=3.4, key="olive")

# ---------------------------------------------------------------- 엘프들
C.group("npc")
# 탈출 직후라 모두 주황 죄수복 (docs/scenario.md 인터루드 2번). 무명 엘프는 prisoner_a/b/c를 돌려 쓴다
PA, PB, PC = ("characters/prisoner_a.glb", "characters/prisoner_b.glb", "characters/prisoner_c.glb")
cast = [
    # id, 위치, model, pose, 바라볼 곳, scene
    ("elena", (1.2, 2.4), "characters/elena_prisoner.glb", "look_far", TREE, "arrival_a,arrival_c", "엘레나"),
    ("rita", (-3.2, 0.6), "characters/rita_prisoner.glb", "sit_dazed", (-6, -10), "arrival_a,arrival_b,arrival_c", "리타"),
    ("cathy", (-4.6, 1.8), "characters/cathy_prisoner.glb", "lie_sprawl", (-8, -2), "arrival_a,arrival_b,arrival_c", "캐시"),
    ("haley", (3.8, 1.2), "characters/haley_prisoner.glb", "help_up", (5.2, 0.0), "arrival_a,arrival_c", "헤일리"),
    ("rone", (5.4, -0.2), "characters/rone_prisoner.glb", "il_arrival_sit_plate", (8, -8), "arrival_a,arrival_c", "로네"),
    ("amelia", (-1.6, -2.0), "characters/amelia_prisoner.glb", "kneel", (-1.6, -6), "arrival_a,arrival_c", "아멜리아"),
    ("elf_01", (-6.8, 4.2), PA, "look_up", (-6, -10), "arrival_a,arrival_c", "엘프"),
    ("elf_02", (7.0, 4.6), PB, "look_around", (20, 0), "arrival_a,arrival_c", "엘프"),
    ("elf_03", (-8.4, -1.6), PC, "point_far", TREE, "arrival_a,arrival_c", "엘프"),
    ("elf_04", (2.4, 6.2), PA, "lie_sprawl", (2.4, 2), "arrival_a", "엘프"),
    ("elf_05", (-2.6, 4.4), PB, "carry_box", (-2.6, 0), "arrival_a,arrival_c", "엘프"),
    ("elf_06", (9.2, -2.6), PC, "look_up", (9, -10), "arrival_a,arrival_c", "엘프"),
]
# 로네는 대탈주(interlude_escape.py)에서 먹으며 뛰던 돈까스 접시와 포크를 주저앉은 채 그대로 들고 있다 (2026-11-02 사용자 확정 코믹).
# 접시는 다 비웠다: 몽타주가 튀김·양배추를 숨기고 소스 자국과 레몬만 남긴다. 자세 il_arrival_sit_plate는 interlude.ts가 더한다
EXTRA = {"rone": {"hold_L": "props/cine_tonkatsu_plate.glb", "hold_R": "props/cine_fork.glb", "expr": "dreamy"}}
for nid, (x, y), model, pose, face, scene, nm in cast:
    C.npc(nid, (x, y, h(x, y)), model, pose=pose, face=face, name=nm, props={"scene": scene, **EXTRA.get(nid, {})})
# 게이트에서 막 떨어지는 엘프 (공중). NPC는 마커 위치에 한 번 놓이므로 낙하는 몽타주가 fallVel(three.js m/s)로 움직인다.
C.npc("elf_falling", (0.4, 9.8, 3.6), PB, pose="tumble", face=(0.4, 0), name="엘프",
      props={"scene": "arrival_a", "airborne": 1, "fallVel": "0.2,-2.2,0.4"})

# ---------------------------------------------------------------- 카메라
C.group("land")
C.cam("arrival_a", [
    (0.0, (8.5, -10.5, 0.7), (-1.5, 8.0, 5.0), 56),
    (4.0, (7.0, -8.8, 0.9), (-1.5, 9.0, 5.6), 54),
    (8.0, (5.6, -7.2, 1.1), (-1.0, 11.0, 6.2), 52),
])
# arrival_b: 리타 얼굴(머리 위 여백) → 낮게 물러나며 달 쪽으로 틸트. 얼굴은 내내 화면 아래 3분의 1 안에 남는다.
# LOOK_arrival_b_03은 미션이 리타의 시선 대상(달)으로도 쓴다: 옮기지 않는다.
C.cam("arrival_b", [
    (0.0, (-3.05, -0.85, 0.6), (-3.22, 0.56, 0.7), 38),
    (3.0, (-2.55, -1.0, 0.38), (-3.99, 1.5, 1.21), 44),     # 방위 -30°, 앙각 16°: 얼굴은 오른쪽 아래, 달은 왼쪽 위
    (6.0, (-2.45, -1.3, 0.3), (-380, 420, 210), 50),
])
# arrival_c: 엘레나 왼쪽 뒤 어깨 너머(머리가 오른쪽 아래) 세계수 → 뒤로 높이 빠지며 일행 전체가 아래 3분의 1에
C.cam("arrival_c", [
    (0.0, (0.2, 0.6, 1.0), (34.6, 194.95, 30.0), 44),
    (4.0, (0.3, -2.6, 1.6), (27.79, 193.02, 32.89), 50),     # 아멜리아 (-1.6, -2.0) 머리 위를 지나지 않게 동쪽으로
    (8.0, (-2.4, -10.6, 2.0), (18.37, 187.03, 24.64), 58),
])
C.marker("SPAWN_player", (0, -4, 0), face=(0, 10))
ROOT = {
    "sky": "#b8e3ee",
    "fog": "240,2600",
    "sun": "0.35,0.85,0.45",
    "ambient": 1.6,
    "near": 0.1,
    "far": 3000,
    "music": "interlude_arrival",
    # 확장 (엔진이 아직 읽지 않음: 몽타주 담당 참고, 지구 쪽 인터루드 세트와 같은 키)
    "sunIntensity": 2.3,
    "hemiSky": "#eefaff",
    "hemiGround": "#7f8a6a",
    "timeOfDay": "morning",
    "scene": "IL_ARRIVAL",
    "shots": "arrival_a,arrival_b,arrival_c",
    "physics": 0,
    "sunColor": "#fff8e6",
}
C.finish("levels/interlude_arrival.glb", root_props=ROOT, outline=0.02)
