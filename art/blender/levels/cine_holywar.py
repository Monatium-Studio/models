"""3막 시네마틱 「성전 개막 소식, 요정 성전군과 합류」 세트: 모나티엄-에르피엔 고속도로 동쪽 외곽, 동틀 녘 (M8 → M9).

npm run model -- art/blender/levels/cine_holywar.py   → public/models/levels/cine_holywar.glb
대본: docs/script/act3c.md (A3_HOLYWAR), 장면: src/game/missions/cine/a3Holywar.ts

[원작] 교주가 깨어나 R41과 흑뉴아를 상대로 성전을 선포하고, 손을 맞잡은 네르가 공명해 엘다인으로 각성한다. 교주와 네르가
성전군을 이끌고, 마카샤와 실라의 지휘로 요정들이 돌격하며, 우로스와 티그가 합세한다. 모나티엄-에르피엔 고속도로(1막 엘레나의
계획)가 원작에 나온다.
[오리지널] 분대가 복구된 회선으로 소식을 처음 듣고, 동쪽 능선을 넘어오는 요정 성전군과 고속도로에서 합류해 에르피엔으로 진군한다.
행렬 맨 앞은 교주(characters/kyoju.glb, 인간)와 각성한 네르(ner.glb), 양옆에 마카샤·실라 (2026-11-02 사용자 지시).

좌표: Blender Z-up. 고속도로는 x=0을 따라 +Y(북, 에르피엔 쪽. 왕도 한가운데 세계수 (-30, 1150))로 뻗는다. 분대는 서쪽 갓길(x -2~-5, y 0~4).
동쪽(+X)은 능선(x≈55, 높이 7 m)까지 오르막이고, 해가 그 너머에서 뜬다. 성전군은 능선 너머에서 흙길(WP_route_*)을 따라
내려와 고속도로에서 북쪽으로 꺾는다. 행렬은 장면이 경로를 따라 세운다(마커 자리는 처음 자리일 뿐).
컷: holy_a(갓길 분대) · holy_c2(능선의 선두, 망원 역광) · holy_c(분대 뒤에서 능선을 넘어오는 행렬) · holy_d(교주·네르와 분대)
    holy_e(크레인: 분대가 행렬 선두에서 북쪽으로)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import cine_kit as ck  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_kit as ek  # noqa: E402
import erpien_flag as ef  # noqa: E402
from mathutils import Matrix  # noqa: E402

cb.reset()
# 동틀 녘: 살구빛 쪽으로 가볍게 (정전 처리 없음: 도시에서 떨어진 외곽이다)
ck.night(t=0.16, k=0.95, tint="#7a5a66", blackout=False)
mk.PAL.update({"dirt_track": ck.shade("#b49a7a", "#7a5a66", 0.16, 0.95), "guard_g": "#2f6a4f", "guard_w": "#ece6e4",
               "guard_k": "#3a3439", "guard_gold": "#e0b870", "pole": "#6b4f3c", "cloth_c": "#f4ead2"})
mk.GLOW["sun_disc"] = "#fff1c8"
C = mk.City("cine_holywar")
EF = ef.city(C)
RIDGE_X = 55.0


def h(x, y):
    n = mk.noise2(x, y, 9)
    if x > 6:
        k = min(1.0, (x - 6) / (RIDGE_X - 6))
        k = k * k * (3 - 2 * k)
        z = 7.0 * k if x <= RIDGE_X else 7.0 - (x - RIDGE_X) * 0.12
        return z + n * 0.4 * k
    if x < -6:
        return n * 0.6 * min(1.0, (-6 - x) / 20)
    return 0.0


def heightfield(key, x0, x1, y0, y1, step):
    b = C.bm(key)
    nx = int((x1 - x0) / step) + 1
    ny = int((y1 - y0) / step) + 1
    vs = [[b.verts.new((x0 + i * step, y0 + j * step, h(x0 + i * step, y0 + j * step) - 0.02)) for i in range(nx)] for j in range(ny)]
    for j in range(ny - 1):
        for i in range(nx - 1):
            b.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))


# ---------------------------------------------------------------- 땅과 길
C.group("ground")
heightfield("grass", -60, 90, -40, 60, 3.0)
heightfield("grass_d", -300, -60, -300, 600, 20.0)
heightfield("grass_d", 90, 400, -300, 600, 20.0)
heightfield("grass_d", -60, 90, 60, 600, 12.0)
heightfield("grass_d", -560, 500, 600, 1560, 40.0)      # 북쪽 원경: 에르피엔 왕도가 선 들
heightfield("grass_d", -60, 90, -300, -40, 12.0)
C.group("road")
mk.road(C, "y", 0.0, -120.0, 520.0, lanes=2, lane_w=3.2, walk=1.2, col=False)
# 흙길: 능선에서 고속도로로 (성전군이 내려오는 길)
ROUTE = [(70.0, 2.0), (RIDGE_X, 2.5), (40.0, 3.2), (24.0, 4.0), (12.0, 4.8), (4.2, 6.4), (2.0, 11.0), (1.8, 30.0),
         (1.8, 80.0), (1.8, 200.0)]
for (x0, y0), (x1, y1) in zip(ROUTE[:5], ROUTE[1:6]):
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2))
    for i in range(n):
        ax, ay = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
        bx, by = x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n
        C.strip("dirt_track", (ax, ay, h(ax, ay) + 0.03), (bx, by, h(bx, by) + 0.03), 3.6, lift=0.0)
for i, (x, y) in enumerate(ROUTE, start=1):
    C.marker(f"WP_route_{i:02d}", (x, y, h(x, y)))

# ---------------------------------------------------------------- 갓길: 분대 자리 (모래주머니, 상자, 휴대 중계기)
C.group("post")
mk.sandbag_wall(C, -2.6, 5.6, yaw=0, n=4, rows=2)
mk.sandbag_wall(C, -5.4, 4.4, yaw=-35, n=3, rows=2)
mk.crate(C, -5.6, 1.4, s=0.6, yaw=12)
mk.crate(C, -5.3, 0.6, s=0.5, yaw=-20, key="tarp")
# 휴대 중계기 (안테나 + 작은 접시 + 시안 표시등: 3막이라 켜져 있다)
RX, RY = -5.05, -0.15
C.box("navy", RX - 0.25, RX + 0.25, RY - 0.2, RY + 0.2, 0.0, 0.42)
C.cyl("metal", (RX - 0.1, RY + 0.1, 0.42), (RX - 0.1, RY + 0.1, 1.9), 0.018, segs=6, kind="detail")
C.cyl("metal", (RX + 0.12, RY + 0.12, 0.42), (RX + 0.12, RY + 0.12, 0.9), 0.012, segs=6, kind="detail")
C.blob("glow", (RX + 0.2, RY - 0.21, 0.33), 0.03, segs=6, rings=4)
C.blob("glow", (RX - 0.1, RY + 0.1, 1.92), 0.04, segs=6, rings=4)
C.marker("MARK_radio", (RX, RY, 0.4))

# ---------------------------------------------------------------- 원경: 등 뒤의 모나티엄, 북쪽 에르피엔(한가운데 세계수), 능선 너머 성전군 본대
C.group("far")
ck.night_skyline(C, r=230.0, n=30, seed=4, fl=(6, 16), skip=lambda x, y: y > -90)
# [원작] 왕국 한가운데 세계수: 고속도로 끝 북쪽 지평선에 세계수와 그 밑동을 두른 왕궁·시가·성벽 (erpien_kit)
ek.erpien(C, -30.0, 1150.0, 0.0, 300.0, hfun=h, face=(30.0, -1150.0), kind="far", detail=0, seed=11, lit="win_lit",
          density=0.7)
mk.mountains(C, -30.0, 1150.0, count=6, dist=430.0, spread=120.0, h=(50, 110), seed=8)
rng = random.Random(3)
# 능선 너머 본대 (작은 실루엣 무리: 초록 샤코·흰 튜닉) + 깃발
for i in range(140):
    x = rng.uniform(RIDGE_X + 6, RIDGE_X + 40)
    y = rng.uniform(-30, 36)
    z = h(x, y)
    C.cyl("guard_w", (x, y, z), (x, y, z + 0.75), 0.17, segs=5, kind="far")
    C.cyl("guard_g", (x, y, z + 0.75), (x, y, z + 1.12), 0.15, segs=5, kind="far")
    if i % 9 == 0:   # [원작] 에르피엔 군기 (원경용 저분할, docs/art/erpien.md 5장)
        ef.far_flag(EF, Matrix.Translation((x + 0.3, y, z)) @ Matrix.Rotation(math.pi / 2, 4, "Z"), W=0.9, pole=2.6,
                    r=0.03, layers={"pole": "far", "cloth": "far"})
# 해: 능선 너머 동쪽 낮게 (원판 + 번짐)
SUN = (420.0, 10.0, 46.0)
ck.moon(C, SUN, r=20.0, key="sun_disc")
C.marker("MARK_sun", SUN)

# ---------------------------------------------------------------- 사람들
C.group("npc")
RIFLE = "weapons/us/m4a1.glb"
SHOTGUN = "weapons/us/m870.glb"
MUSKET = "weapons/fairy/fairy_guard_musket.glb"
BANNER = "props/cine_holywar_banner.glb"
EAST = (40.0, 3.0)
SQUAD = {
    "rita": ((-3.1, 3.1), "characters/rita.glb", "hold_rifle_ready", RIFLE, EAST),
    "sabre": ((-2.2, 1.7), "characters/squad_sabre.glb", "hold_rifle_ready", RIFLE, (-3.6, 0.3)),
    "rona": ((-5.4, 2.9), "characters/squad_rona.glb", "cine_kneel_rifle", RIFLE, (10.0, 3.0)),
    "jesty": ((-4.3, 0.2), "characters/squad_jesty.glb", "cine_kneel_radio", RIFLE, (2.0, -1.0)),
    "karen": ((-2.0, 3.9), "characters/squad_karen.glb", "hold_rifle_ready", SHOTGUN, (-3.6, 0.3)),
}
for nid, ((x, y), model, pose, gun, face) in SQUAD.items():
    C.npc(nid, (x, y, 0.0), model, pose=pose, face=face, name=nid, props={"hold_R": gun, "expr": "serious"})
# 성전군: 행렬 18명 (3열 × 6줄). 0줄 양 끝은 깃발 기수. 장면이 경로 위에 다시 세운다
for i in range(18):
    row, col = divmod(i, 3)
    x, y = RIDGE_X + 6 + row * 1.5, 1.4 + col * 1.1
    banner = row == 0 and col != 1
    C.npc(f"fairy_{i + 1:02d}", (x, y, h(x, y)), "characters/fairy_guard.glb" if i % 2 == 0 else "characters/fairy_guard_b.glb",
          pose="cine_holy_banner" if banner else "hold_rifle_ready", face=(0, 3), name="요정 경비대",
          props={"hold_R": BANNER if banner else MUSKET, "scene": "holy_c,holy_c2,holy_d,holy_e"})
C.npc("fairy_officer", (RIDGE_X + 3.5, 2.6, h(RIDGE_X + 3.5, 2.6)), "characters/fairy_guard_officer.glb", pose="idle", face=(0, 3),
      name="요정 장교", props={"expr": "serious", "scene": "holy_c,holy_c2,holy_d,holy_e"})
# 맨 앞의 교주와 각성한 네르 (교주는 말하지 않는다: 원작 플레이어 대리인. 네르가 교주의 뜻을 전한다)
C.npc("kyoju", (RIDGE_X + 0.4, 2.6, h(RIDGE_X + 0.4, 2.6)), "characters/kyoju.glb", pose="kyoju_stand", face=(0, 3),
      name="교주", props={"scene": "holy_c,holy_c2,holy_d,holy_e"})
C.npc("ner", (RIDGE_X + 0.6, 1.6, h(RIDGE_X + 0.6, 1.6)), "characters/ner.glb", pose="ner_lead", face=(0, 3),
      name="네르", props={"expr": "glare", "scene": "holy_c,holy_c2,holy_d,holy_e", "cameo": "ner"})
# 양 날개의 지휘관 (원작 카메오: 마카샤 = 前 벨리티엔 책략관, 실라 = 바람의 고위 정령. 요정 돌격 지휘). 대사 없음
C.npc("makasha", (RIDGE_X + 1.0, 1.8, h(RIDGE_X + 1, 1.8)), "characters/makasha.glb", pose="idle", face=(0, 3), name="마카샤",
      props={"expr": "smirk", "scene": "holy_c,holy_c2,holy_d,holy_e", "cameo": "makasha"})
C.npc("sila", (RIDGE_X + 1.0, 3.4, h(RIDGE_X + 1, 3.4)), "characters/sila.glb", pose="idle", face=(0, 3), name="실라",
      props={"expr": "serious", "scene": "holy_c,holy_c2,holy_d,holy_e", "cameo": "sila"})
C.marker("WP_officer_stop", (-1.0, 2.5, 0.0))
# 교주·네르가 분대 앞으로 와 서는 자리 (holy_d)
C.marker("WP_ner_stop", (-1.15, 2.35, 0.0))
C.marker("WP_kyoju_stop", (0.35, 2.05, 0.0))
# 분대가 행렬 선두로: 고속도로로 나가 북쪽으로
for i, p in enumerate(((-1.2, 6.0, 0.0), (-0.6, 14.0, 0.0), (-0.4, 40.0, 0.0), (-0.4, 120.0, 0.0)), start=1):
    C.marker(f"WP_squad_go_{i:02d}", p)

# ---------------------------------------------------------------- 카메라
C.cam("holy_a", [
    (0.0, (2.3, -3.6, 1.15), (-3.4, 1.4, 0.6), 40),
    (9.0, (1.7, -2.8, 1.05), (-3.5, 1.4, 0.6), 36),
])
# 능선의 선두: 망원, 해를 등진 실루엣
C.cam("holy_c2", [
    (0.0, (9.0, 5.0, 1.45), (RIDGE_X, 2.6, h(RIDGE_X, 2.6) + 0.9), 9),
    (6.0, (9.5, 5.2, 1.5), (RIDGE_X - 2.5, 2.7, h(RIDGE_X - 2.5, 2.7) + 0.8), 8.5),
])
# 비탈 중턱 흙길 옆에서 능선을 올려다봄: 해를 등지고 깃발과 행렬이 카메라 쪽으로 내려온다
C.cam("holy_c", [
    (0.0, (30.0, -0.9, h(30.0, -0.9) + 0.9), (48.0, 3.0, h(48.0, 3.0) + 1.5), 34),
    (12.0, (29.4, -1.2, h(29.4, -1.2) + 0.85), (35.0, 3.4, h(35.0, 3.4) + 1.1), 42),
])
# 교주·네르와 분대 (분대 남서쪽 어깨 너머로 북동을 봄: 분대를 보고 선 교주·네르의 앞모습, 교주 미트라까지)
C.cam("holy_d", [
    (0.0, (-3.9, -0.6, 1.65), (-0.5, 2.3, 1.20), 42),
    (10.0, (-3.6, -0.3, 1.60), (-0.5, 2.3, 1.15), 39),
])
# 크레인: 분대가 선두에서 북쪽으로, 뒤로 행렬, 멀리 세계수
C.cam("holy_e", [
    (0.0, (-6.0, -2.0, 1.6), (0.0, 26.0, 1.2), 42),
    (9.0, (-12.0, -12.0, 12.0), (0.0, 60.0, 0.0), 46),
])

C.group("city")
C.marker("SPAWN_player", (-3.0, 2.0, 0.0), face=EAST)
ROOT = {
    "sky": "#f0c4a6",
    "fog": "160,2300",
    "sun": "0.9,0.28,-0.05",
    "ambient": 1.25,
    "sunColor": "#ffd2a4",
    "sunIntensity": 2.0,
    "hemiSky": "#f6d8c4",
    "hemiGround": "#5a5248",
    "physics": 0,
    "near": 0.05,
    "far": 2000,
    "music": "cine_dawn",
    "timeOfDay": "dawn",
    "scene": "A3_HOLYWAR",
    "shots": "holy_a,holy_c2,holy_c,holy_d,holy_e",
}
C.finish("levels/cine_holywar.glb", root_props=ROOT, outline=0.02)
