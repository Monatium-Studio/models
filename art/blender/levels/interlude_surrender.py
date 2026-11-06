"""인터루드 1 「투항」 디오라마 세트 (IL_SURRENDER, docs/script/interlude.md 4.1).

[원작] 함선을 지구(미국 땅)에 착륙시킨 뒤 일부 말단 병사가 먼저 공격했고, 반격으로 함선의 항법·통신 장비가 망가져
      침공군이 고립됐다. 헤일리는 무기를 내려놓고 먼저 투항해 인명 피해를 줄였다(나무위키 「엘프(트릭컬 리바이브)」
      2.12.1, 「엘레나(트릭컬 리바이브)/작중 행적」 4.2.4).
[오리지널] 새벽의 착륙지 들판. 프롤로그에서 함교를 맞은 기함(space/elfinia_flagship.glb, 함번 01)이 고개를 처박고
      연기를 피운다. 엘프 병사들은 한 줄로 서서 총을 내려놓고, 헤일리가 줄 앞으로 나와 먼저 무릎을 꿇는다.
      리타와 캐시가 그 줄에 있다. 인간 병사는 얼굴·휘장이 없는 초점 나간 실루엣으로만 보인다.

npm run model -- art/blender/levels/interlude_surrender.py   → public/models/levels/interlude_surrender.glb
npm run shot -- levels/interlude_surrender.glb --views top,34

좌표: 엘프 줄이 y=0에서 X를 따라 서고 -Y(남쪽)의 인간 쪽을 본다. 기함 잔해는 +Y(북쪽) 멀리. 해는 동쪽(+X) 지평선.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import interlude_kit as ik  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

L = ik.begin("interlude_surrender", mode="dawn")
rnd = random.Random(7)

SOLDIER = "characters/_kit_elfinia_soldier.glb"
RIFLE = "weapons/elfinia/elfinia_rifle.glb"
PISTOL = "weapons/elfinia/elfinia_pistol.glb"

# ================================================================ 지형
WRECK = Vector((-6.0, 96.0, 0.0))      # 기함 잔해 중심 (땅 위치)
FURROW_DIR = Vector((-1.0, -0.12, 0)).normalized()   # 미끄러져 온 반대 방향 (고랑이 뻗는 쪽)


def furrow_d(x, y):
    """고랑 중심선까지 거리와 고랑을 따라간 거리."""
    p = Vector((x, y, 0)) - WRECK
    t = p.dot(FURROW_DIR)
    perp = (p - FURROW_DIR * t).length
    return perp, t


def height(x, y):
    d = math.hypot(x, y - 4)
    flat = min(1.0, max(0.0, (d - 26) / 70))
    h = flat * flat * (2.2 + 2.8 * ik.vnoise(x, y, 1) + 1.6 * ik.vnoise(x * 2.3, y * 2.3, 5))
    perp, t = furrow_d(x, y)
    if t > 20 and perp < 16:          # 고랑: 가운데가 파이고 양옆이 솟는다
        k = min(1.0, (t - 20) / 15) * max(0.0, 1 - t / 220)
        h += k * (-1.2 * max(0.0, 1 - perp / 7) + 1.4 * math.exp(-((perp - 9) / 3.0) ** 2))
    dw = (Vector((x, y, 0)) - WRECK).length
    if dw < 50:                        # 잔해 주변 흙 둔덕
        h += 2.2 * math.exp(-((dw - 30) / 7) ** 2)
    return h


def keyf(cx, cy):
    perp, t = furrow_d(cx, cy)
    dw = (Vector((cx, cy, 0)) - WRECK).length
    if (t > 8 and perp < 11 and t < 230) or dw < 40:
        return "dirt" if perp < 6 or dw < 34 else "dirt_l"
    if -24.5 < cy < -20.5 and abs(cx) < 140:       # 농로
        return "dirt_l"
    n = ik.vnoise(cx * 1.7, cy * 1.7, 9)
    far = math.hypot(cx, cy) > 34
    if far and n > 0.38:
        return "grass"
    if far and n < -0.45:
        return "grass_d"
    # 밀밭 줄무늬 (먼 곳)
    if math.hypot(cx, cy) > 40 and int((cx + 400) / 7) % 2 == 0:
        return "wheat_d"
    return "wheat"


L.zone("field")
xs = ik.grid_lines(-320, 320, near=(-22, 22), fine=2.2, grow=1.32, maxstep=40)
ys = ik.grid_lines(-140, 330, near=(-24, 14), fine=2.2, grow=1.3, maxstep=40)
ik.terrain(L, xs, ys, height, keyf)

# 가까운 땅: 밟힌 풀·이슬 젖은 풀 얼룩 (모양 있는 데칼)
for i in range(18):
    x, y = rnd.uniform(-22, 22), rnd.uniform(-26, 12)
    r = rnd.uniform(1.2, 3.6)
    pts = []
    for k in range(12):
        a = k / 12 * 6.283
        rr = r * (0.7 + 0.3 * math.sin(a * 3 + i) + rnd.uniform(-0.08, 0.08))
        pts.append((math.cos(a) * rr * 1.3, math.sin(a) * rr))
    L.decal(rnd.choice(("grass", "grass_d", "wheat_d")), pts, (x, y, height(x, y)), (0, 0, 1), lift=0.015)
# 밀밭 이랑 (가까운 곳에도 줄무늬): 줄 뒤에서 북쪽으로 뻗는 띠
for k in range(-9, 10):
    x = k * 2.4 + 0.6
    L.strip("wheat_d", (x, 3.2, 0.0), (x + 1.2, 60.0, height(x + 1.2, 60.0)), 0.9, (0, 0, 1), lift=0.02)
# 풀 덤불 (가까운 곳 2·3차 디테일)
for i in range(170):
    x, y = rnd.uniform(-20, 20), rnd.uniform(-22, 10)
    if abs(y) < 0.9 and abs(x) < 7:
        continue
    ik.tuft(L, (x, y, height(x, y)), s=rnd.uniform(0.22, 0.42), seed=i,
            key=rnd.choice(("grass_d", "wheat_d", "grass_d")))
for i in range(14):
    x, y = rnd.uniform(-30, 30), rnd.uniform(-30, 30)
    if abs(x) < 9 and -5 < y < 3:
        continue
    ik.rock(L, (x, y, height(x, y)), s=rnd.uniform(0.12, 0.35), seed=i)

# 농로 울타리, 전봇대, 먼 농가, 나무, 언덕
L.zone("land")
ik.rail_fence(L, [(-90, -25.2), (-20, -25.6), (40, -25.0), (110, -25.8)], height)
ik.power_line(L, [(x, -46 + 0.04 * x) for x in range(-240, 260, 42)], height)
ik.barn(L, ik.Frame((-128, 150, height(-128, 150)), yaw=-8))
ik.barn(L, ik.Frame((168, 196, height(168, 196)), yaw=20), w=8, d=12, h=4.2, roof_h=3.2)
for i, (x, y) in enumerate([(-150, 165), (-142, 172), (-110, 168), (-98, 160), (-160, 140), (150, 210), (186, 214),
                            (198, 190), (60, 210), (-60, 236), (120, 120), (-210, 90),
                            (240, 100), (-70, -90), (90, -100), (-30, 180)]):
    s = rnd.uniform(0.8, 1.35)
    ik.tree(L, (x, y, height(x, y)), h=7.5 * s, r=3.4 * s, seed=i)
ik.hills_ring(L, (0, 60), 250, 300, 16, h=(14, 34), seed=4)

# 구름 (낮게 깔린 새벽 구름)
for i, (x, y, z, s) in enumerate([(-60, 220, 46, 22), (40, 260, 58, 30), (150, 230, 40, 20), (-170, 200, 52, 26),
                                  (110, 150, 70, 16), (-20, 160, 78, 14), (230, 150, 36, 22)]):
    ik.cloud(L, (x, y, z), size=s, seed=i)
# 동쪽 지평선의 해 (조명 없는 원판 + 흐린 테)
SUN = Vector((300, 70, 20))
sd = (Vector((0, 0, 4)) - SUN).normalized()
L.decal("sun_disc", [(math.cos(a) * 9, math.sin(a) * 9) for a in [i * math.pi / 12 for i in range(24)]],
        tuple(SUN), tuple(sd), lift=0.0)
L.decal("haze", [(math.cos(a) * 18, math.sin(a) * 18) for a in [i * math.pi / 12 for i in range(24)]],
        tuple(SUN - sd * 2), tuple(sd), lift=0.0)

# ================================================================ 기함 잔해 (space/elfinia_flagship.glb)
L.zone("wreck")
WM = (Matrix.Translation(WRECK + Vector((0, 0, 4.2))) @ Matrix.Rotation(math.radians(96), 4, "Z")
      @ Matrix.Rotation(math.radians(7.0), 4, "X") @ Matrix.Rotation(math.radians(-14.0), 4, "Y"))
holder, parts = ik.import_glb(L, "space/elfinia_flagship.glb", name="wreck_flagship", matrix=WM,
                              drop=("bridge", "elfinia_flagship_plume"),
                              props={"outline": 0.07, "note": "space/elfinia_flagship.glb 재사용: 함교 피격형"})
anchors = {}
for o in parts:
    if o.type == "EMPTY" and o.name.startswith("anchor_"):
        anchors[o.name] = o
    if o.name == "bridge_damaged":
        o["hidden"] = 0
        if "hidden" in o.keys():
            del o["hidden"]
    if o.name == "elfinia_flagship_glow":
        # 꺼진 창: 시안 발광을 어두운 남색으로 (전력 없음)
        ca = o.data.color_attributes.get("Color") or o.data.color_attributes[0]
        for d in ca.data:
            c = d.color_srgb
            if c[2] > 0.5 and c[0] < 0.7:        # 시안·흰 시안 → 꺼짐
                d.color_srgb = (0.17, 0.2, 0.26, 1.0)
            elif c[0] > 0.8 and c[1] > 0.6:       # 따뜻한 창 → 어두운 주황 (비상 전력 몇 칸)
                d.color_srgb = (0.55, 0.32, 0.2, 1.0)
bpy_update = __import__("bpy").context.view_layer.update
bpy_update()


def apos(name, fallback):
    o = anchors.get(name)
    return Vector(o.matrix_world.translation) if o else Vector(fallback)


P_BRIDGE = apos("anchor_bridge_hit", WRECK + Vector((10, 0, 18)))
P_ENG = apos("anchor_engines", WRECK + Vector((-34, 0, 8)))
P_BOW = apos("anchor_bow", WRECK + Vector((36, 0, 2)))
print("[surrender] anchors", {k: tuple(round(c, 1) for c in v.matrix_world.translation) for k, v in anchors.items()})

# 연기 기둥 + FX 마커
ik.smoke_column(L, "bridge", tuple(P_BRIDGE + Vector((0, 0, 1))), height=58, r0=3.5, r1=13, lean=(0.42, 0.18),
                n=12, seed=1)
ik.smoke_column(L, "engines", tuple(P_ENG), height=42, r0=3.0, r1=10, lean=(0.5, 0.25), n=9, seed=2)
ik.smoke_column(L, "bow", tuple(P_BOW + Vector((-2, -4, 0))), height=30, r0=2.4, r1=8, lean=(0.55, 0.2), n=7,
                seed=3)
# 땅에 처박힌 쪽 흙 둔덕과 흙덩이
for i in range(26):
    a = rnd.uniform(-1.2, 1.2) + (0 if i % 2 else math.pi)
    r = rnd.uniform(22, 38)
    p = WRECK + Vector((math.cos(a) * r * 1.3 + 24, math.sin(a) * r * 0.5, 0))
    L.obj("dirt" if i % 3 else "dirt_d", cb.sphere("mound", radius=rnd.uniform(2.5, 5.5),
                                                    loc=(p.x, p.y, height(p.x, p.y) - 0.8),
                                                    scale=(1.4, 1.0, 0.45), segments=9, rings=5,
                                                    rot=(0, 0, rnd.uniform(0, 180))))

# 잔해 조각: 선체 판, 남색 띠, 금색 고리 토막, 보급 상자 (기함 디자인 언어)
L.zone("debris")
DEBRIS = []


def hull_plate(c, size, rot, *, band=False, key="hull_d"):
    L.rbox(key, c, size, rot)
    if band:
        L.rbox("navy", (c[0], c[1], c[2] + size[2] * 0.6), (size[0] * 0.25, size[1] * 1.02, size[2] * 0.4), rot,
               kind="detail")
    DEBRIS.append(c)


for i in range(16):
    t = rnd.uniform(14, 70)
    side = rnd.choice((-1, 1)) * rnd.uniform(4, 22)
    base = WRECK + FURROW_DIR * t * 0.6 + Vector((rnd.uniform(-10, 10), -rnd.uniform(12, 46), 0))
    if base.y < 22:
        base.y = 22 + rnd.uniform(0, 8)
    z = height(base.x, base.y)
    s = rnd.uniform(1.2, 3.8)
    hull_plate((base.x, base.y, z + 0.15), (s, s * rnd.uniform(0.5, 0.9), 0.22),
               (rnd.uniform(-25, 25), rnd.uniform(-35, 35), rnd.uniform(0, 180)), band=i % 3 == 0,
               key=rnd.choice(("hull_d", "olive", "hull")))
# 부러진 금색 고리 토막 (함수 광자포 포구 고리)
for i, (x, y, a) in enumerate([(14, 58, 20), (-22, 52, 70)]):
    for k in range(5):
        aa = math.radians(a + k * 14)
        p0 = (x + math.cos(aa) * 2.4, y, 1.0 + math.sin(aa) * 2.4 * 0.4)
        aa2 = math.radians(a + (k + 1) * 14)
        p1 = (x + math.cos(aa2) * 2.4, y, 1.0 + math.sin(aa2) * 2.4 * 0.4)
        L.cyl("gold", p0, p1, 0.32, verts=8)
# 엘프 보급 상자 (줄 뒤): 둥근 상자 + 남색 띠 + 금색 걸쇠
for i, (x, y, yaw) in enumerate([(-9.5, 4.2, 12), (-8.4, 5.6, -20), (8.8, 4.6, 30), (10.3, 3.8, -8), (9.6, 6.4, 64)]):
    F = ik.Frame((x, y, height(x, y)), yaw)
    F.rbox(L, "olive", (0, 0, 0.32), (1.0, 0.62, 0.62))
    F.rbox(L, "navy", (0, 0, 0.36), (1.02, 0.64, 0.14), kind="detail")
    F.rbox(L, "gold", (0, -0.32, 0.47), (0.12, 0.03, 0.1), kind="detail")
    F.rbox(L, "hull", (0, 0, 0.65), (0.9, 0.55, 0.06))
# 그을음과 불씨 (FX_fire 마커)
for i, (x, y) in enumerate([(12, 40), (-16, 48), (2, 64), (24, 70), (-30, 62)]):
    z = height(x, y)
    ik.scorch(L, (x, y, z), r=rnd.uniform(2.0, 4.0), seed=i)
    ik.embers(L, (x, y, z), r=1.2, n=6, seed=i)
    L.marker(f"FX_fire_{i + 1:02d}", (x, y, z), props={"kind": "fire", "scale": 1.0})

# ================================================================ 엘프 줄 + 헤일리
# 모두 무기를 손에 든 채 시작한다 (hold_R: 손 소켓에 붙는 소총, 원점 = 오른손 파지점). 바닥에 미리 놓인 총은 없다.
# 몽타주가 줄을 헤일리 가까운 쪽부터 물결처럼 무릎 꿇리고(placePose) 숙여 발 앞 DROP_<id> 자리에 내려놓게 한 뒤 poseNext로.
L.zone("line")
LINE_X = [-5.85 + 0.9 * i for i in range(14)]
ROSTER = [  # (id, 내려놓은 뒤 자세, model, extra)
    ("soldier_01", "surrender_hands_up", SOLDIER, {}),
    ("soldier_02", "kneel_hands_up", SOLDIER, {}),
    ("soldier_03", "kneel_head_down", SOLDIER, {}),
    ("soldier_04", "surrender_hands_up", SOLDIER, {}),
    ("soldier_05", "attention_head_down", SOLDIER, {}),
    ("soldier_06", "kneel_hands_up", SOLDIER, {}),
    ("soldier_07", "kneel_head_down", SOLDIER, {}),
    ("soldier_08", "surrender_hands_up", SOLDIER, {}),
    ("cathy", "stand_attention", "characters/cathy_prologue.glb",
     {"lookAt": "NPC_rita", "expr": "serious",
      "note": "캐시가 먼저 총을 내려놓고 일어서 리타를 본다"}),
    ("rita", "kneel_head_down", "characters/rita_prologue.glb",
     {"expr": "held_back", "delay": 1.0,
      "note": "리타는 한 박자 늦게 내려놓고 무릎 꿇은 채 고개를 숙인다 (held_back)"}),
    ("soldier_09", "kneel_hands_up", SOLDIER, {}),
    ("soldier_10", "attention_head_down", SOLDIER, {}),
    ("soldier_11", "sit_slumped", SOLDIER,
     {"pose": "sit_slumped_rifle", "placePose": "sit_place", "note": "부상병 (앉음): 무릎 위 총을 오른쪽 옆 바닥에"}),
    ("soldier_12", "surrender_hands_up", SOLDIER, {}),
]


def laid(yaw):
    """옆으로 눕힌 무기 회전 (총구 +Y가 yaw 방향, 오른 옆면이 땅)."""
    return Euler((0, math.radians(90), math.radians(yaw)))


def drop_at(npc_xy, npc_yaw, left, fwd):
    """NPC 기준 오프셋(인물 왼쪽 +, 앞 +) → 월드 xy. NPC는 yaw 0에서 -Y를 본다(왼쪽 = +X)."""
    a = math.radians(npc_yaw)
    dx, dy = left, -fwd
    return (npc_xy[0] + dx * math.cos(a) - dy * math.sin(a), npc_xy[1] + dx * math.sin(a) + dy * math.cos(a))


for i, (nid, after, model, extra) in enumerate(ROSTER):
    x = LINE_X[i] + rnd.uniform(-0.08, 0.08)
    y = rnd.uniform(-0.15, 0.15)
    yaw = rnd.uniform(-6, 6)
    props = {"pose": "hold_rifle_ready", "placePose": "kneel_place", "poseNext": after, "hold_R": RIFLE,
             "group": "line", "order": i + 1, "scene": "surrender_a,surrender_b,surrender_c"}
    props.update(extra)
    L.npc(nid, (x, y, 0.0), model, yaw=yaw, props=props)
    # 내려놓을 자리: 무릎 꿇고 숙인 손(kneel_place의 쥔 자리) 바로 앞 땅, 총구가 왼쪽으로 옆으로 눕는다.
    # 앉은 부상병은 오른쪽 옆 땅에 총구를 앞으로. (난수 호출 수는 예전 PROP_rifle_*과 같게 둔다: 뒤의 배치가 바뀌지 않게)
    if props["placePose"] == "sit_place":
        gx, gy = drop_at((x, y), yaw, -0.3, 0.2)
        rifle_yaw = 180 + yaw + rnd.uniform(-14, 14) * 0.3
    else:
        gx, gy = drop_at((x, y), yaw, -0.1 + rnd.uniform(-0.05, 0.05) * 0.6, 0.36)
        rifle_yaw = -84 + yaw + rnd.uniform(-14, 14) * 0.6
    L.markers.append((f"DROP_{nid}", (gx, gy, 0.035), laid(rifle_yaw), {"slot": "R", "group": "laid_weapons"}))

HALEY = (-0.35, -2.75, 0.0)
HALEY_YAW = 4
L.npc("haley", HALEY, "characters/haley.glb", yaw=HALEY_YAW,
      props={"pose": "stand_flag", "placePose": "kneel_place_flag", "poseNext": "kneel_flag",
             "hold_R": PISTOL, "hold_L": "props/interlude_white_flag.glb",
             "holdGrip_L": "0,0.42,0", "holdRot_L": "0,180,0",
             "expr": "serious", "group": "haley", "scene": "surrender_a,surrender_b",
             "note": "백기(왼손)와 권총(오른손)을 들고 줄 앞으로 걸어 나와 권총을 먼저 내려놓고 무릎을 꿇는다 "
                     "(IL_SURRENDER_02). 백기는 땅에 세워 쥔 채"})
L.wp("haley_from", (-0.3, -0.9, 0.0), yaw=0)        # 줄에서 걸어 나오는 출발점
hx, hy = drop_at(HALEY, HALEY_YAW, -0.08, 0.34)
L.markers.append(("DROP_haley", (hx, hy, 0.02), laid(-70 + HALEY_YAW), {"slot": "R", "group": "laid_weapons"}))
# 줄 앞 발자국·밟힌 풀 (헤일리가 걸어 나온 길)
for k in range(5):
    t = k / 4
    p = (-0.3 + rnd.uniform(-0.05, 0.05), -0.9 - t * 1.6)
    L.decal("dirt_l", [(math.cos(a) * 0.09, math.sin(a) * 0.14) for a in [j * math.pi / 5 for j in range(10)]],
            (p[0] + (0.1 if k % 2 else -0.1), p[1], 0.0), (0, 0, 1), lift=0.02)

# ================================================================ 인간 병사 (초점 나간 실루엣)
L.zone("humans")
HUMANS = [  # (x, y, pose, tone)
    (6.3, -13.3, "ready", 0),     # 카메라 a 바로 앞 오른쪽 (크게 흐림)
    (0.9, -12.0, "aim", 0),       # 왼쪽 앞
    (-4.6, -10.6, "aim", 1),
    (9.6, -10.4, "aim", 1),
    (-8.8, -9.8, "stand", 1),
    (13.2, -11.6, "ready", 1),
    (-2.4, -16.4, "walk", 1),
    (-14.5, -12.5, "ready", 2),
    (18.0, -14.5, "stand", 2),
]
for i, (x, y, pose, tone) in enumerate(HUMANS):
    yaw = 180 + math.degrees(math.atan2(-x * 0.35, 10)) + rnd.uniform(-5, 5)
    ik.human(L, (x, y, height(x, y)), yaw, pose=pose, tone=tone)
for i, (x, y, yaw, kind, tone) in enumerate([(-9.5, -27, 160, "truck", 2), (8.0, -31, 205, "apc", 2),
                                              (19.0, -24, 235, "truck", 2), (-24.0, -33, 140, "apc", 2)]):
    ik.vehicle_silhouette(L, (x, y, height(x, y)), yaw, tone=tone, kind=kind)
ik.helicopter_silhouette(L, (-26, 34, 24), 75, tone=2)
ik.helicopter_silhouette(L, (34, 52, 31), 250, tone=2, tilt=6)
L.marker("FX_heli_01", (-26, 34, 24), props={"kind": "rotor", "path": "orbit"})
L.marker("FX_heli_02", (34, 52, 31), props={"kind": "rotor", "path": "orbit"})

# ================================================================ 카메라 (3컷, 합계 약 20초)
L.zone("cams")
# a. 인간 실루엣 어깨 너머로 보는 들판과 잔해 (7초)
L.cam_rail("surrender_a", [
    (0.0, (5.3, -17.6, 1.7), (1.4, 14.0, 4.6), 42),
    (3.5, (4.5, -16.4, 1.6), (1.0, 10.0, 3.4), 39),
    (7.0, (3.7, -15.2, 1.5), (0.6, 6.0, 2.2), 36),
])
# b. 헤일리: 줄 앞, 낮은 각도에서 밀고 들어간다 (7초). 뒤로 줄과 연기 나는 잔해
HF = (HALEY[0], HALEY[1], 0.82)
L.cam_rail("surrender_b", [
    (0.0, (-2.9, -6.9, 0.55), (HF[0], HF[1], HF[2] + 0.25), 32),
    (3.5, (-2.3, -6.1, 0.52), (HF[0], HF[1], HF[2] + 0.12), 29),
    (7.0, (-1.75, -5.35, 0.5), HF, 26),
])
# c. 줄을 따라 옆으로 → 캐시와 리타 (6초)
RC = ((LINE_X[8] + LINE_X[9]) / 2, 0.0, 0.72)
L.cam_rail("surrender_c", [
    (0.0, (-3.6, -1.75, 0.95), (-1.8, 0.0, 0.78), 38),
    (3.0, (-1.0, -1.85, 0.9), (0.6, 0.0, 0.8), 36),
    # 끝: 리타 쪽 앞에서 낮게. 리타를 돌아보는 캐시의 얼굴과, 고개 숙인 리타의 철모 아래 얼굴이 보이게
    (6.0, (RC[0] + 0.58, -2.6, 0.5), (RC[0] - 0.05, 0.0, 0.74), 34),
])

ROOT = {
    "sky": "#d9c2b6",
    "fog": "70,360",
    "sun": "1.0,0.34,-0.18",
    "ambient": 1.25,
    "music": "interlude_strings",
    # 확장 (엔진이 아직 읽지 않음: 몽타주 담당 참고)
    "sunColor": "#ffd6b0",
    "sunIntensity": 2.1,
    "hemiSky": "#f1d9cc",
    "hemiGround": "#7d6b5c",
    "timeOfDay": "dawn",
    "scene": "IL_SURRENDER",
    "shots": "surrender_a,surrender_b,surrender_c",
    "physics": 0,
}
ik.finish(L, "levels/interlude_surrender.glb", root_props=ROOT, outline=0.012)
