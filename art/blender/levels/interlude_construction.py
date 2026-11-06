"""인터루드 5 「모나티엄 건설」: 같은 자리의 타임랩스. 천막 → 공장 → 도시 → 코어 AI 기동, 엘레나 시장 취임.

npm run model -- art/blender/levels/interlude_construction.py   → public/models/levels/interlude_construction.glb

원작: 불시착한 엘프들은 당장 먹고 살기 위해 테라포밍 장치로 엘프 도시 모나티엄을 세웠다(도시·공장·발전소 계획,
정령을 에너지원으로 우대). 모나티엄은 모나티엄 AI가 운영하는 도시이고, 초대 시장은 엘레나다.
자리는 인터루드 6·7의 시청 앞 광장과 같은 좌표다(시청 (0, 26), 코어 AI (32, 36), 광장 중심 (0, 0)).

단계 노드 (몽타주가 차례로 켠다):
  STAGE_0  천막: 천막촌, 모닥불, 테라포밍 장치(시청 자리)와 퍼지는 풀 고리, 짐 상자
  STAGE_1  공장: 흙길, 톱니 지붕 공장, 정령 발전소, 크레인, 비계에 둘러싸인 시청 기초와 코어 기단
  STAGE_2  도시: 광장·분수·시청·코어 AI 탑(꺼짐)·주변 건물·모노레일 한 구간·취임 연단
  STAGE_3  코어 AI 기동(겹침): 빛나는 코어 띠·빛기둥·바닥 네트워크 선·취임 축하 현수막. STAGE_2와 함께 켠다(showWith)
  (항상)   엘리아스 초원, 지평선의 세계수와 에르피엔(밑동을 두른 왕궁·시가), 산, 하늘
NPC 마커의 stage 속성 = 그 NPC가 보이는 단계.
CAM: build_a(타임랩스 고정 와이드, 모든 단계 공통), build_b(코어 기동), build_c(취임식)
문서: docs/art/interlude-elias.md
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_kit as ek  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("interlude_construction")
# 세계수 (북북서 지평선, 약 1.07 km). [원작] 요정 왕국 에르피엔이 세계수 둘레를 두른다 (erpien_kit, 모든 에르피엔 장면과 같은 디자인)
TREE = (-240.0, 1040.0)
TREE_H = 420.0
CIV = "characters/_kit_base.glb"
SOLDIER = "characters/_kit_elfinia_soldier.glb"
Z = 0.04          # 도시 바닥(판석)은 초원보다 4 cm 위 (겹침 깜빡임 방지)

# ================================================================ 항상 보이는 땅
C.group("land")
h = mk.terrain(C, radius=380, seed=8, amp=10.0, flat_r=95.0)
C.group("far")
C.cyl("grass", (TREE[0], TREE[1], -8.0), (TREE[0], TREE[1], h(*TREE) - 0.4), TREE_H * 0.95, segs=40, kind="far")
ek.erpien(C, TREE[0], TREE[1], h(*TREE) - 0.4, TREE_H, face=(-TREE[0], -TREE[1]), kind="far", detail=0, seed=11,
          density=0.7)
mk.mountains(C, 0, 0, count=4, dist=480, spread=40, h=(70, 150), seed=5, arc=(20, 82))
mk.mountains(C, 0, 0, count=2, dist=480, spread=40, h=(70, 150), seed=6, arc=(124, 160))
mk.mountains(C, TREE[0], TREE[1], count=6, dist=560, spread=60, h=(90, 170), seed=21, arc=(20, 180))
mk.mountains(C, 0, 0, count=5, dist=500, spread=40, h=(60, 120), seed=9, arc=(190, 330))
mk.haze_wall(C, radius=620, h=110)
for i, (x, y, z, s) in enumerate(((-160, 280, 130, 36), (140, 320, 150, 40), (260, 40, 120, 30), (-280, 60, 140, 32))):
    mk.cloud(C, x, y, z, size=s, seed=i + 20)
C.group("woods")
for i, (x, y, r, n) in enumerate(((-150, 90, 30, 12), (150, 120, 30, 12), (-170, -60, 26, 10), (160, -80, 26, 10),
                                  (40, 190, 30, 12))):
    mk.forest(C, x, y, r=r, n=n, seed=i + 11, hfun=h)

# ================================================================ STAGE_0: 천막
C.group("STAGE_0", stage=0, label="천막", timeOfDay="dawn", sky="#cfe4ea")
mk.terraformer(C, 0.0, 24.0, lit=True, rings=4)
rng = random.Random(5)
tents = []
for (fx, fy) in ((0.0, 0.0), (-17.0, 2.0), (16.0, -2.0)):
    mk.campfire(C, fx, fy)
for ring_r, n in ((9.0, 11), (16.0, 17), (24.0, 22)):
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.1, 0.1) + ring_r
        r = ring_r + rng.uniform(-1.4, 1.4)
        x, y = math.cos(a) * r, math.sin(a) * r - 2.0
        if y > 13 or (abs(x) < 3 and y < -6):
            continue          # 테라포밍 장치 자리, 남쪽 통로
        key = ("canvas", "tarp", "olive", "canvas")[i % 4]
        mk.tent(C, x, y, yaw=math.degrees(math.atan2(x, -(y + 2))) + 180, key=key)
        tents.append((x, y))
for i, (x, y) in enumerate(((5.0, 6.5), (5.8, 7.2), (-6.0, 7.5), (-6.8, 8.0), (8.5, -6.0), (-9.0, -7.0))):
    mk.crate(C, x, y, s=0.62, yaw=rng.uniform(0, 90), key=("olive", "tarp")[i % 2])
# 깃대 (엘피니아 남색 깃발 + 엘프 로고) — 정착의 첫 표식
C.cyl("steel", (3.0, 14.0, 0), (3.0, 14.0, 6.0), 0.05, segs=8, kind="detail")
C.plate("navy", [(0, 0), (1.6, 0), (1.6, -1.0), (0, -1.0)], (3.0, 14.0, 5.9), (0, -1, 0), 0.02, kind="detail")
C.logo((3.8, 13.97, 5.4), 0.7, (0, -1, 0), key="gold")
# 작업대 (상자 + 방수포)
C.box("wood", -3.2, -1.6, 4.6, 5.4, 0.55, 0.62, kind="detail")
for (x, y) in ((-3.1, 4.7), (-1.7, 4.7), (-3.1, 5.3), (-1.7, 5.3)):
    C.box("wood_d", x - 0.04, x + 0.04, y - 0.04, y + 0.04, 0, 0.55, kind="detail")
mk.scorch(C, 0.0, 30.0, 3.5, seed=9)
C.npc("elena_s0", (-1.0, 18.0, 0.0), "characters/elena.glb", pose="point_far", face=(0.0, 24.0), name="엘레나")
for i, (x, y, pose, face) in enumerate([
    (-2.4, 5.6, "work_bench", (-2.4, 4.6)), (2.0, 1.4, "sit_tired", (0, 0)), (-1.8, -1.4, "sit_tired", (0, 0)),
    (6.4, 6.0, "carry_box", (0, 20)), (-7.6, 2.0, "assemble", (-9.0, 1.0)), (1.4, 20.4, "kneel", (0, 24)),
]):
    C.npc(f"settler_s0_{i + 1:02d}", (x, y, h(x, y)), CIV if i % 2 else SOLDIER, pose=pose, face=face, name="엘프")
C.npc("rita_s0", (4.2, -4.0, 0.0), "characters/rita_prologue.glb", pose="carry_box", face=(5.8, 7.0), name="리타")

# ================================================================ STAGE_1: 공장
C.group("STAGE_1", stage=1, label="공장", timeOfDay="noon", sky="#bfe0ee")
for (p0, p1, w) in (((-80, -20.8), (80, -20.8), 9.0), ((0, -20.8), (0, 20), 6.0), ((-40, -20.8), (-40, 34), 5.0),
                    ((-40, 30), (40, 30), 5.0)):
    C.strip("soil", (p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), w, lift=0.035)
mk.factory_shed(C, -66, -46, -40, -28, h=4.4, teeth=5, seed=1)
mk.factory_shed(C, 30, 52, -40, -28, h=4.4, teeth=5, seed=2)
mk.factory_shed(C, -64, -48, 4, 16, h=4.0, teeth=4, key="warm", seed=3)
mk.spirit_plant(C, -44.0, 40.0)
mk.crane(C, -12.0, 34.0, h=26.0, jib=20.0, yaw=-20)
mk.crane(C, 40.0, 22.0, h=22.0, jib=16.0, yaw=200)
# 시청 기초 (기단 + 낮은 벽) + 비계
C.prism("stone_d", mk.hw.rrect(36, 16, 4.2, 4, 0, 26.0), 0, 0.9)
C.ring_prism("concrete", mk.hw.rrect(34, 14, 3.8, 4, 0, 26.0), mk.hw.rrect(33.2, 13.2, 3.4, 4, 0, 26.0), 0.9, 4.6)
C.prism("concrete", mk.hw.rrect(11, 11, 2.4, 3, 0, 25.0), 0.9, 12.0)
mk.scaffold(C, -18, 18, 18.4, 33.6, 5.4)
mk.scaffold(C, -6.2, 6.2, 18.8, 31.2, 13.0)
# 코어 기단 (둥근 받침만)
C.cyl("concrete_d", (32, 36, 0), (32, 36, 2.6), 7.0, segs=28)
mk.scaffold(C, 28.5, 35.5, 32.5, 39.5, 8.1)
# 자재 더미
for i, (x, y) in enumerate(((10, 12), (11, 13), (12, 12), (-14, 10), (-13, 11), (20, -6), (-22, -8))):
    mk.crate(C, x, y, s=0.9, yaw=i * 17, key=("wood", "olive", "steel")[i % 3])
for i, (x, y) in enumerate(((16, 8), (-18, 2))):
    for k in range(4):
        C.beam("steel", (x, y + k * 0.3, 0.15 + (k % 2) * 0.18), (x + 6, y + k * 0.3, 0.15 + (k % 2) * 0.18), 0.18, 0.18,
               kind="detail")
for (x, y) in tents[:3]:
    mk.tent(C, x - 30, y - 30, yaw=30, key="canvas")
for i, (x, y, pose, face) in enumerate([
    (8.0, 10.0, "carry_box", (0, 26)), (-12.0, 12.0, "carry_box", (0, 26)), (12.5, 12.5, "assemble", (11, 13)),
    (-4.0, 16.4, "assemble", (-4, 19)), (4.6, 16.2, "work_bench", (4.6, 19)), (-20, -6, "carry_box", (-50, -30)),
    (24.0, 30.0, "assemble", (32, 36)),
]):
    C.npc(f"worker_s1_{i + 1:02d}", (x, y, 0.0), CIV if i % 2 else SOLDIER, pose=pose, face=face, name="엘프")
C.npc("rita_s1", (2.0, 12.0, 0.0), "characters/rita_prologue.glb", pose="carry_box", face=(0, 20), name="리타")

# ================================================================ STAGE_2: 도시
C.group("STAGE_2", stage=2, label="도시", timeOfDay="afternoon", sky="#aed8f0")
mk.paving(C, -24, 24, -11, 18, z=Z, border="pave_r")
mk.paving(C, -24, 24, 18, 36, z=Z, grout=None)
mk.paving(C, 24, 42, 22, 48, z=Z, grout=None)
mk.fountain(C, 0, 2.0, z=Z)
for sx in (-1, 1):
    for k in range(3):
        y = -6 + k * 7.5
        x = sx * 17.5
        mk.planter(C, x - 1.4, x + 1.4, y - 1.4, y + 1.4, h=0.5, hedge=False, z=Z)
        mk.tree(C, x, y, h=4.0, seed=k * 3 + (sx + 1), z=0.5 + Z)
    mk.lamp(C, sx * 6.5, -9.5, z=Z)
    mk.lamp(C, sx * 6.5, 13.0, z=Z)
mk.city_hall(C, 0, 26.0, screen=False)
mk.core_ai(C, 32, 36, lit=False)
rd = mk.road(C, "x", mk.AVENUE_Y, -70, 70, lanes=4, median=2.0, z=Z, crossings=(-12.0, 12.0))
mk.monorail(C, [(-72.0, mk.AVENUE_Y), (72.0, mk.AVENUE_Y)], z=7.5)
# 초기 도시: 큰길 건너 상가는 아직 없다 (가판 몇 개만)
for i, x in enumerate((-30.0, -12.0, 10.0, 28.0)):
    mk.tree(C, x, rd["walk_lo"] + 1.4, h=4.2, seed=50 + i, z=Z)
    mk.lamp(C, x + 6, rd["walk_lo"] + 0.6, z=Z)
mk.building(C, 26, 42, -9, 9, floors=5, style="office", front="-x", sides="-x-y+y", seed=101)
mk.building(C, 26, 40, 11, 22, floors=4, style="apartment", front="-x", sides="-x-y", seed=102)
mk.building(C, -42, -26, -9, 9, floors=5, style="office", front="+x", sides="+x-y+y", seed=103, sign="EBI 진압반")
mk.building(C, -40, -26, 11, 22, floors=4, style="apartment", front="+x", sides="+x-y", seed=104)
for k, (x0, w, fl, st) in enumerate(((-46, 14, 6, "glass"), (-30, 12, 5, "apartment"), (44, 14, 7, "glass"))):
    mk.building(C, x0, x0 + w, 40, 52, floors=fl, style=st, front="-y", sides="-y-x+x", seed=200 + k, door=False,
                cctv=False)
# 취임 연단 (시청 포르티코 바닥 z=0.9, 광장을 바라봄). 군중은 분수와 계단 사이에 선다.
PODIUM = mk.podium(C, 0.0, 15.6, yaw=0.0, z=0.9)
for sx in (-1, 1):
    for k in range(3):
        C.cyl("steel", (sx * (4.4 + k * 2.0), 11.0, Z), (sx * (4.4 + k * 2.0), 11.0, Z + 0.9), 0.04, segs=6,
              kind="detail")
    C.beam("violet", (sx * 4.4, 11.0, Z + 0.85), (sx * 8.4, 11.0, Z + 0.85), 0.05, 0.08, kind="detail")

# ================================================================ STAGE_3: 코어 AI 기동 (겹침)
C.group("STAGE_3", stage=3, label="코어 AI 기동 · 시장 취임", showWith="STAGE_2", timeOfDay="dusk", sky="#f2c7a8")
mk.core_ai(C, 32, 36, glow_overlay=True)
# 시청 탑 로고 원판 둘레의 빛 고리, 분수 빛
C.ring("glow", mk.hw.circle(2.7, 32), mk.hw.circle(2.45, 32), (0, 26.0 - 1 - 5.5 - 0.06, 27 - 2.6), (0, -1, 0),
       lift=0.0)
C.cyl("holo", (0, 2.0, Z + 0.6), (0, 2.0, Z + 6.0), 0.5, r2=1.6, segs=16, kind="fine", cap=False)
# 축하 현수막 (광장 가로질러)
for sx in (-1, 1):
    C.cyl("gold", (sx * 14, -9.0, Z), (sx * 14, -9.0, Z + 6.5), 0.08, segs=8, kind="detail")
C.plate("violet", mk.hw.rrect(24, 1.6, 0.5, 3), (0, -9.0, Z + 5.4), (0, -1, 0), 0.06, kind="detail")
C.text("gold", "엘레나 시장 취임 · 모나티엄 원년", 0.75, (0, -9.08, Z + 5.5), (0, -1, 0), lift=0.0)
C.text("white", "MAYOR ELENA · MONATIUM YEAR ONE", 0.28, (0, -9.08, Z + 4.9), (0, -1, 0), lift=0.0)
# 종이꽃 (UNLIT 작은 조각)
rng = random.Random(33)
for i in range(70):
    x, y, z = rng.uniform(-16, 16), rng.uniform(-8, 12), rng.uniform(2.0, 9.0)
    key = ("hazard", "glow", "flower_p", "white", "mint")[i % 5]
    a = rng.uniform(0, 3)
    C.rbox(key, (x, y, z), (0.16, 0.02, 0.1), (rng.uniform(0, 90), rng.uniform(0, 90), a * 30), kind="fine")
C.marker("LIGHT_core_on", (32, 36, 20), props={"color": mk.GLOW["glow"], "intensity": 5.0, "range": 80.0,
                                                "pointLight": 1})
# 취임식 사람들
px, py, pz = PODIUM.x, PODIUM.y, PODIUM.z
C.npc("elena_s3", (px, py, pz), "characters/elena.glb", pose="speech", face=(px, py - 20), name="엘레나",
      props={"expr": "smile"})
C.npc("amelia_s3", (px - 2.4, py + 0.8, pz), "characters/amelia.glb", pose="attention", face=(px - 2.4, py - 20),
      name="아멜리아")
C.npc("rone_s3", (px + 2.4, py + 0.8, pz), "characters/rone.glb", pose="clap", face=(px + 2.4, py - 20), name="로네")
C.npc("haley_s3", (px + 5.4, 12.4, Z), "characters/haley.glb", pose="salute", face=(px, py), name="헤일리")
rng = random.Random(8)
k = 0
for row in range(3):
    for col in range(8):
        x = -8.4 + col * 2.4 + rng.uniform(-0.4, 0.4) + (1.2 if row % 2 else 0)
        y = 10.0 - row * 1.7 + rng.uniform(-0.25, 0.25)
        if row == 2 and abs(x) < 4.4:
            continue          # 분수 가장자리
        k += 1
        pose = ("cheer", "clap", "cheer", "wave", "clap")[k % 5]
        C.npc(f"crowd_s3_{k:02d}", (x, y, Z), CIV if k % 3 else SOLDIER, pose=pose, face=(px, py), name="시민")
C.npc("rita_s3", (-5.6, 7.2, Z), "characters/rita_prologue.glb", pose="clap", face=(px, py), name="리타")
C.npc("cathy_s3", (-4.4, 6.8, Z), "characters/cathy_prologue.glb", pose="cheer", face=(px, py), name="캐시")

# ================================================================ 카메라
C.group("land")
C.cam("build_a", [
    (0.0, (-32.0, -56.0, 30.0), (0.0, 10.0, 3.0), 46),
    (6.0, (-29.0, -57.5, 31.0), (1.0, 10.5, 3.5), 46),
    (12.0, (-26.0, -59.0, 32.0), (2.0, 11.0, 4.0), 46),
])
C.cam("build_b", [
    (0.0, (18.6, 13.2, 0.7), (31.0, 34.0, 10.0), 50),
    (3.0, (19.4, 14.4, 0.7), (31.5, 35.0, 24.0), 54),
    (6.0, (20.2, 15.6, 0.8), (32.0, 36.0, 42.0), 58),
])
C.cam("build_c", [
    (0.0, (-11.0, 5.2, 1.3), (0.0, 15.0, 2.0), 44),
    (4.0, (-6.0, 8.2, 1.75), (0.0, 15.4, 2.2), 36),
    # 끝: 엘레나 눈높이(단상 위 2.6 m)에 가깝게 올려 연설대(윗면 2.16 m) 위로 얼굴과 손이 보이게
    (8.0, (-1.75, 11.7, 2.2), (0.0, 15.45, 2.45), 30),
])
C.marker("SPAWN_player", (0, -6, 0), face=(0, 10))
ROOT = {
    "sky": "#b9dcee",
    "fog": "180,1500",
    "sun": "0.4,0.9,0.35",
    "ambient": 1.55,
    "near": 0.1,
    "far": 2000,
    "music": "interlude_construction",
    "sunIntensity": 2.3,
    "timeOfDay": "timelapse",
    "scene": "IL_CONSTRUCTION",
    "shots": "build_a,build_b,build_c",
    "stages": "STAGE_0,STAGE_1,STAGE_2,STAGE_3",
    "physics": 0,
    "sunColor": "#fff4e0",
}
C.finish("levels/interlude_construction.glb", root_props=ROOT, outline=0.022)
