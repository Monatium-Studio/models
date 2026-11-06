"""M9 로딩 브리핑의 생중계 세트: 수인 마을 동굴 집회장, 아침 (M8 → A3_M9_BRIEF → A3_HOLYWAR → M9).

npm run model -- art/blender/levels/cine_declare.py   → public/models/levels/cine_declare.glb
대본: docs/script/act3c.md 3.2c (A3_M9_BRIEF), 장면: src/game/missions/cine/a3M9Brief.ts

[원작] 유령 늪 전투 뒤 교주·뮤트·사도들이 한 동굴에 모여 있었다. 교주가 깨어나 리뉴아(흑뉴아)의 만행에 격노하고, 마카샤와
       실라가 말렸지만(마카샤가 가장 세게: 제2의 우로스 사태) 교주가 네르의 손을 붙잡자 둘의 격노가 공명해 네르가 엘다인으로
       각성한다. 교주가 R41과 리뉴아를 상대로 성전을 선포하고, 함께 피난 중이던 요정·수인·정령·유령이 모여 성전군이 된다.
[오리지널] 그 동굴을 수인 마을 끝 바위 언덕의 동굴로 두고, 동굴 앞 마당에 피난민이 모인 것으로 그렸다(원작은 동굴 이름·자리를
       밝히지 않는다). 뮤트가 교주를 데려다 놓을 때 남긴 단말기 카메라가 이 마당을 비추고, 엘레나의 위성 화면에 생중계로 들어온다.
       위성 화면은 이 세트를 충돌체 없이 한 벌 더 읽어 위에서 본다(MARK_village·MARK_cave·MARK_crowd).

좌표: Blender Z-up. 마당 가운데 (0, 0). 북쪽(+Y)이 바위 언덕과 동굴 입구(0, 11), 그 앞 바위 단(0, 7.4, 높이 0.5)에 교주와 네르가
남쪽(군중)을 보고 선다. 마카샤·실라는 단 아래 양옆에서 교주를 올려다보며 말린다. 군중은 남쪽 반원(y 0~-7), 그 뒤는 원경 실루엣.
서쪽·동쪽에 수인 마을의 둥근 초가 오두막과 피난 천막, 마당 양옆에 모닥불.
컷: feed_a(단말기 카메라 와이드) · feed_b(단 위 교주·네르, 마카샤·실라) · feed_c(교주와 네르 두 사람) · feed_d(각성: 단을 비스듬히)
    feed_e(선포: 군중 사이에서 올려다봄) · feed_f(단 뒤에서 군중) · feed_g(마지막 와이드)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import cine_kit as ck  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
mk.PAL.update({"thatch": "#c9a665", "thatch_d": "#9c7c48", "hut_wall": "#a77d55", "hut_wall_d": "#7c5a3e",
               "plaza": "#9a8064", "cliff": "#8f8790", "cliff_d": "#6d6672", "trunk": "#6b4f3c",
               "beast_cloth": "#c8705a", "beast_cloth2": "#6f8f5a"})
# 흐린 아침 (모닥불이 아직 타는 피난민 마당): 남청을 아주 조금만
ck.night(t=0.16, k=0.94, tint="#6a6a86", blackout=False)
mk.GLOW.update({"fire": "#ffb35a", "fire_c": "#fff0b0", "cave_glow": "#ffcf7a"})
C = mk.City("cine_declare")


def h(x, y):
    """바닥 높이: 마당은 평평, 북쪽은 언덕(동굴 위), 바깥은 완만한 둔덕."""
    n = mk.noise2(x, y, 5)
    z = 0.0
    if y > 9.0:
        k = min(1.0, (y - 9.0) / 8.0)
        z += 7.5 * k * k * (3 - 2 * k)
    r = math.hypot(x, y)
    if r > 18:
        z += min(2.5, (r - 18) * 0.08)
    return z + n * 0.25 * min(1.0, r / 14)


def heightfield(key, x0, x1, y0, y1, step, kind="main"):
    b = C.bm(key, kind)
    nx = int((x1 - x0) / step) + 1
    ny = int((y1 - y0) / step) + 1
    vs = [[b.verts.new((x0 + i * step, y0 + j * step, h(x0 + i * step, y0 + j * step) - 0.02)) for i in range(nx)]
          for j in range(ny)]
    for j in range(ny - 1):
        for i in range(nx - 1):
            b.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))


# ---------------------------------------------------------------- 땅
C.group("ground")
heightfield("grass", -30, 30, -24, 9, 1.5)
heightfield("cliff", -30, 30, 9, 30, 1.5)
# 바깥 원경 (격자가 안쪽 조각 가장자리에 정확히 닿게: 간격으로 나누어떨어지는 범위)
heightfield("grass_d", -158, 158, -152, -24, 16.0)
heightfield("grass_d", -158, -30, -24, 168, 16.0)
heightfield("grass_d", 30, 158, -24, 168, 16.0)
heightfield("grass_d", -30, 30, 30, 162, 12.0)
# 밟아 다진 마당 (흙 원판)
C.cyl("plaza", (0, -1.5, -0.01), (0, -1.5, 0.02), 9.5, segs=28, kind="fine")

# ---------------------------------------------------------------- 바위 언덕과 동굴 입구
C.group("cliff")
rng = random.Random(7)
for i in range(26):
    a = rng.uniform(-1.0, 1.0)
    x = a * 18.0
    y = 10.0 + rng.uniform(-0.6, 3.0) + abs(a) * 1.5
    if abs(x) < 3.2 and y < 12.5:
        continue  # 동굴 입구는 비운다
    s = rng.uniform(1.6, 3.4)
    C.blob("cliff_d" if i % 3 == 0 else "cliff", (x, y, h(x, y) + s * 0.25), s, (1.0, 0.8, 0.9), segs=8, rings=5,
           rot_z=rng.uniform(0, 3), kind="main")
# 동굴: 입구 둘레 큰 바위 둘 + 이마 바위, 안은 어두운 굴 (깊은 곳에 등불 빛)
C.blob("cliff", (-3.4, 11.4, 1.6), 2.6, (0.9, 1.0, 1.4), segs=10, rings=6, rot_z=0.3)
C.blob("cliff", (3.5, 11.6, 1.7), 2.7, (0.9, 1.0, 1.4), segs=10, rings=6, rot_z=-0.2)
C.blob("cliff_d", (0.0, 11.8, 4.4), 3.6, (1.3, 0.9, 0.55), segs=10, rings=6)
C.box("char", -2.2, 2.2, 11.2, 14.5, 0.0, 3.4)
C.blob("cave_glow", (0.0, 13.6, 1.0), 0.35, segs=8, rings=5, kind="fine")
C.blob("cave_glow", (-0.9, 13.2, 0.8), 0.22, segs=8, rings=5, kind="fine")
C.marker("MARK_cave", (0.0, 11.0, 0.0))
# 바위 단: 교주와 네르가 서는 낮은 너럭바위 (높이 0.5)
C.cyl("cliff", (0.0, 7.4, -0.2), (0.0, 7.4, 0.5), 2.4, r2=2.2, segs=14)
C.cyl("cliff_d", (0.0, 7.4, 0.48), (0.0, 7.4, 0.52), 2.15, segs=14, kind="detail")
for i, (x, y, s) in enumerate(((-2.3, 6.2, 0.7), (2.4, 6.4, 0.6), (-1.6, 9.1, 0.8), (1.9, 9.0, 0.7))):
    mk.rock(C, x, y, s=s, seed=20 + i, key="cliff")
C.marker("MARK_dais", (0.0, 7.4, 0.5))

# ---------------------------------------------------------------- 수인 마을: 둥근 초가 오두막, 피난 천막, 울타리, 모닥불
C.group("village")


def hut(x, y, r=2.0, wall=1.4, roof=1.9, door_yaw=0.0, seed=0):
    z = h(x, y)
    C.cyl("hut_wall", (x, y, z - 0.1), (x, y, z + wall), r, segs=14)
    C.cyl("thatch", (x, y, z + wall - 0.05), (x, y, z + wall + roof), r + 0.45, r2=0.08, segs=14)
    C.cyl("thatch_d", (x, y, z + wall - 0.12), (x, y, z + wall - 0.02), r + 0.48, segs=14, kind="detail")
    a = math.radians(door_yaw)
    dx, dy = math.sin(a), -math.cos(a)
    C.decal("dark", [(-0.45, 0), (0.45, 0), (0.45, 1.25), (0, 1.5), (-0.45, 1.25)], (x + dx * r, y + dy * r, z),
            (dx, dy, 0), lift=0.03)
    C.cyl("trunk", (x, y, z + wall + roof - 0.1), (x, y, z + wall + roof + 0.35), 0.05, segs=5, kind="detail")


for i, (x, y, r, yaw) in enumerate(((-13.5, 2.0, 2.2, 70), (-15.0, -5.5, 1.9, 60), (-10.5, 7.5, 1.8, 40),
                                    (13.0, 3.0, 2.1, -70), (15.5, -4.5, 2.0, -60), (11.0, 8.0, 1.7, -40),
                                    (-6.0, -15.0, 1.9, 180), (7.5, -15.5, 2.0, 180))):
    hut(x, y, r=r, door_yaw=yaw, seed=i)
C.marker("MARK_village", (-13.5, 0.0, 0.0))
for i, (x, y, yaw, key) in enumerate(((-9.0, -9.0, 30, "canvas"), (-11.5, -11.0, 50, "beast_cloth"),
                                      (9.5, -9.5, -30, "beast_cloth2"), (12.0, -11.5, -45, "canvas"),
                                      (-18.0, 0.5, 90, "canvas"), (18.5, -0.5, -90, "beast_cloth"))):
    mk.tent(C, x, y, yaw=yaw, w=2.4, d=2.8, h=1.7, key=key, z=h(x, y))
mk.fence(C, (-19.0, -8.0), (-12.0, -16.0), z=0.1)
mk.fence(C, (19.0, -8.0), (12.5, -16.0), z=0.1)
mk.crate(C, -7.4, 5.0, s=0.6, yaw=15, key="wood", stencil=False)
mk.crate(C, -7.9, 4.3, s=0.5, yaw=-10, key="wood", stencil=False)
mk.crate(C, 7.6, 5.2, s=0.55, yaw=-20, key="wood", stencil=False)
# 모닥불 둘 (마당 양옆) + 불빛 마커
for i, (x, y) in enumerate(((-5.2, 3.2), (5.4, 3.0))):
    mk.campfire(C, x, y, z=h(x, y))
    C.fx(f"fire_{i + 1}", (x, y, 0.8), kind="fire")
    C.marker(f"MARK_fire_{i + 1}", (x, y, 0.6))
# 마당 둘레 나무
for i, (x, y, s) in enumerate(((-20, 8, 1.2), (-23, -6, 1.0), (21, 9, 1.1), (23, -8, 1.3), (-17, -17, 1.0),
                               (17, -18, 1.1), (-24, 2, 0.9), (25, 1, 1.0))):
    mk.tree(C, x, y, h=5.2 * s, seed=30 + i, z=h(x, y))

# ---------------------------------------------------------------- 군중 원경: 앞줄 NPC 뒤에 선 피난민 실루엣 (요정·수인)
C.group("far")
rng = random.Random(11)
CAMS = ((-7.2, -4.6), (-0.5, -1.0), (8.4, -5.2), (1.2, 2.4), (-2.0, 4.2))   # 카메라 자리 둘레는 비운다 (코앞 실루엣 금지)
k = 0
while k < 120:
    a = rng.uniform(-1.05, 1.05)
    d = rng.uniform(12.0, 17.5)
    x = math.sin(a) * d
    y = 6.5 - math.cos(a) * d
    if any(math.hypot(x - cx, y - cy) < 4.5 for cx, cy in CAMS):
        continue
    i = k
    k += 1
    z = h(x, y)
    tone = ("beast_cloth", "beast_cloth2", "canvas", "guard_w" if "guard_w" in mk.PAL else "canvas")[i % 4]
    C.cyl(tone, (x, y, z), (x, y, z + 0.62), 0.17, r2=0.14, segs=6, kind="detail")
    C.blob("skin" if "skin" in mk.PAL else "canvas", (x, y, z + 0.82), 0.17, segs=6, rings=4, kind="detail")
C.marker("MARK_crowd", (0.0, -3.5, 0.0))

# ---------------------------------------------------------------- 사람들
C.group("npc")
DAIS = 0.5
FACE_S = (0.0, -6.0)
C.npc("kyoju", (0.45, 7.3, DAIS), "characters/kyoju.glb", pose="kyoju_stand", face=FACE_S, name="교주")
# 각성 전 네르 (ner_base) 와 각성한 네르 (ner): 같은 자리. 장면이 빛 속에서 바꿔 세운다
C.npc("ner_base", (-0.55, 7.1, DAIS), "characters/ner_base.glb", pose="feed_ner_clasp", face=FACE_S, name="네르",
      props={"expr": "fury", "cameo": "ner"})
C.npc("ner", (-0.55, 7.1, DAIS), "characters/ner.glb", pose="ner_lead", face=FACE_S, name="네르",
      props={"expr": "glare", "cameo": "ner"})
C.npc("makasha", (-3.0, 5.2, 0.0), "characters/makasha.glb", pose="idle", face=(0.0, 7.3), name="마카샤",
      props={"expr": "serious", "cameo": "makasha"})
C.npc("sila", (3.1, 5.3, 0.0), "characters/sila.glb", pose="idle", face=(0.0, 7.3), name="실라",
      props={"expr": "serious", "cameo": "sila"})
# 앞줄 피난민 (군중 키트 crowd_*: 요정 왕국 주민·수인, g·h는 아이) + 요정 경비대 몇
KIT = ["fairy_a", "beast_b", "fairy_c", "beast_c", "fairy_b", "beast_d", "fairy_g", "beast_e", "fairy_d",
       "beast_a", "fairy_e", "beast_f", "fairy_h", "beast_g", "fairy_f"]
rng = random.Random(5)
n = 0
for row, (d, cnt) in enumerate(((4.6, 7), (6.4, 9), (8.2, 8))):
    for j in range(cnt):
        a = (j - (cnt - 1) / 2) / ((cnt - 1) / 2) * 0.95
        x = math.sin(a) * d + rng.uniform(-0.2, 0.2)
        y = 6.6 - math.cos(a) * d + rng.uniform(-0.2, 0.2)
        if abs(x) < 3.2 and y > 3.6:
            continue
        kit = KIT[n % len(KIT)]
        C.npc(f"crowd_{n + 1:02d}", (x, y, h(x, y)), f"characters/crowd_{kit}.glb", pose="attention",
              face=(0.0, 7.3), name="피난민")
        n += 1
for i, (x, y) in enumerate(((-4.0, 0.2), (4.2, 0.0), (-6.6, -1.6), (6.8, -1.9))):
    C.npc(f"guard_{i + 1}", (x, y, h(x, y)), "characters/fairy_guard.glb" if i % 2 == 0 else "characters/fairy_guard_b.glb",
          pose="hold_rifle_ready", face=(0.0, 7.3), name="요정 경비대",
          props={"hold_R": "weapons/fairy/fairy_guard_musket.glb"})

# ---------------------------------------------------------------- 카메라 (단말기 카메라: 바위 위에 놓인 것처럼 낮게 흔들림 없이)
# 와이드: 마당 서남쪽 바위 위에서 단과 군중을 함께
C.cam("feed_a", [
    (0.0, (-7.2, -4.6, 2.3), (0.4, 6.6, 1.3), 46),
    (12.0, (-6.8, -4.2, 2.25), (0.3, 6.8, 1.35), 43),
])
# 단 위 교주·네르와 단 아래 마카샤·실라 (군중 가운데 뒤에서)
C.cam("feed_b", [
    (0.0, (-0.5, -1.0, 1.65), (0.0, 6.4, 1.2), 44),
    (14.0, (-0.4, -0.3, 1.6), (0.0, 6.5, 1.2), 41),
])
# 교주와 네르 두 사람 (손을 붙잡는 자리)
C.cam("feed_c", [
    (0.0, (0.5, 2.4, 1.15), (0.0, 7.2, 1.4), 36),
    (8.0, (0.4, 2.9, 1.15), (0.0, 7.2, 1.4), 33),
])
# 각성: 단을 비스듬히 (빛이 번지는 동안 천천히 물러남)
C.cam("feed_d", [
    (0.0, (-1.8, 4.4, 1.15), (-0.1, 7.2, 1.5), 38),
    (10.0, (-2.2, 3.9, 1.2), (-0.1, 7.2, 1.6), 42),
])
# 선포: 군중 사이에서 단 위 교주를 올려다봄
C.cam("feed_e", [
    (0.0, (1.2, 2.4, 0.95), (0.2, 7.3, 2.0), 40),
    (14.0, (1.1, 2.9, 0.95), (0.2, 7.3, 2.05), 36),
])
# 단 뒤 위에서 군중 (교주의 뒷모습 너머 함성)
C.cam("feed_f", [
    (0.0, (1.6, 9.6, 2.9), (-0.3, -3.0, 0.6), 50),
    (9.0, (1.3, 9.9, 3.1), (-0.3, -3.5, 0.6), 52),
])
# 마지막 와이드 (마당 동남쪽, 모닥불 너머)
C.cam("feed_g", [
    (0.0, (8.4, -5.2, 2.6), (-0.4, 6.0, 1.2), 44),
    (8.0, (8.0, -5.6, 2.8), (-0.4, 6.0, 1.3), 46),
])

C.group("city")
C.marker("SPAWN_player", (0.0, -6.0, 0.0), face=(0.0, 7.0))
ROOT = {
    "sky": "#b9bfcf",
    "fog": "40,420",
    "sun": "0.35,0.55,0.5",
    "ambient": 1.3,
    "sunColor": "#ffe2c0",
    "sunIntensity": 1.7,
    "hemiSky": "#d8dcea",
    "hemiGround": "#5a5248",
    "physics": 0,
    "near": 0.05,
    "far": 900,
    "timeOfDay": "morning",
    "scene": "A3_M9_BRIEF",
    "shots": "feed_a,feed_b,feed_c,feed_d,feed_e,feed_f,feed_g",
}
C.finish("levels/cine_declare.glb", root_props=ROOT, outline=0.02)
