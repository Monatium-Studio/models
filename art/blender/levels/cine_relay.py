"""3막 시네마틱 「뮤트의 우회 통신망」 세트: M7에서 되찾은 마지막 중계국 옥상, 아직 정전된 모나티엄의 밤 (M7 → M8).

npm run model -- art/blender/levels/cine_relay.py   → public/models/levels/cine_relay.glb
대본: docs/script/act3c.md (A3_BYPASS), 장면: src/game/missions/cine/a3Bypass.ts

[원작] R41의 전파 교란기로 무선망이 마비됐다. 뮤트의 제안으로 코어 AI가 다시 가동되고(엘레나가 목표를 '엘리아스의 보존'으로 바꿈),
엘레나가 교란 장치가 추적할 때마다 새 주파수를 만들어 통신망을 복구한다.
[오리지널] 리타가 M7에서 되찾은 전파 시설 다섯 곳(RELAY_1~5, 5번은 이 옥상)을 코어에 들어간 뮤트가 교란 구역(JAM_1~3)을
피해 가는 회선으로 엮는다. 꺼진 도시 위로 시안 실이 이어지고 리타의 HUD가 단계적으로 켜진다.

좌표: Blender Z-up. 옥상(바닥 z 18)은 원점, 북동쪽 (120, 170)에 코어 AI 탑(꺼짐 + 켜짐 겹침 CORE_on).
컷: bypass_a(옥상의 분대) · bypass_b(코어 탑이 켜짐) · bypass_c(도시 위 공중: 회선이 이어짐) · (리타 시점, 코드) · (리타 얼굴, 코드)
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
ck.night(t=0.48, k=0.66)
C = mk.City("cine_relay")
ROOF = 18.0
CORE = (120.0, 170.0)
RELAYS = [(60.0, 250.0, 30.0), (-140.0, 190.0, 34.0), (-95.0, 55.0, 28.0), (0.0, 0.0, ROOF + 8.6), (215.0, 70.0, 32.0)]
JAMS = [(-40.0, 140.0, 46.0), (95.0, 230.0, 34.0), (110.0, 30.0, 52.0)]

# ---------------------------------------------------------------- 중계국 건물과 옥상
C.group("station")
# 높이 = h0 + floors × fh = 3.5 + 5 × 2.9 = 18.0 (옥상 바닥과 같다: 벽이 옥상 위로 솟지 않게)
mk.building(C, -7, 7, -6, 6, floors=5, style="office", front="-y", sides="-y+y-x+x", seed=3, door=False, cctv=False,
            roof=False, fh=2.9, h0=3.5)
# 층: 건물 윗면(ROOF) → 옥상 판 윗면(+6 mm) → 바닥 판석(+12 mm). 셋이 같은 높이면 옥상 바닥이 깜빡인다
C.box("concrete_d", -7.2, 7.2, -6.2, 6.2, ROOF - 0.3, ROOF + 0.006, col=False)
mk.paving(C, -6.6, 6.6, -5.6, 5.6, z=ROOF + 0.012, grout="pave_d", tile=1.2, col=False, t=0.05)
for (x0, x1, y0, y1) in ((-7.2, 7.2, -6.2, -5.8), (-7.2, 7.2, 5.8, 6.2), (-7.2, -6.8, -6.2, 6.2), (6.8, 7.2, -6.2, 6.2)):
    C.box("concrete", x0, x1, y0, y1, ROOF + 0.006, ROOF + 0.7)     # 옥상 판 위에서 시작 (옆면이 겹치지 않게)
# 안테나 마스트 (격자) + 접시 + 꼭대기 등
MX, MY = -4.4, -3.0       # 남서쪽 구석 (북동쪽 코어를 보는 시선을 막지 않게)
for i in range(4):
    a = math.radians(45 + i * 90)
    C.beam("metal", (MX + math.cos(a) * 0.7, MY + math.sin(a) * 0.7, ROOF), (MX + math.cos(a) * 0.15, MY + math.sin(a) * 0.15, ROOF + 8.4),
           0.07, 0.07, kind="detail")
for k in range(8):
    z = ROOF + 0.6 + k * 1.0
    r = 0.7 - 0.55 * (z - ROOF) / 8.4
    C.ring("metal", [(math.cos(t / 8 * math.tau) * (r + 0.04), math.sin(t / 8 * math.tau) * (r + 0.04)) for t in range(8)],
           [(math.cos(t / 8 * math.tau) * r, math.sin(t / 8 * math.tau) * r) for t in range(8)], (MX, MY, z), (0, 0, 1), lift=0.0)
C.cyl("dark", (MX, MY, ROOF + 8.4), (MX, MY, ROOF + 8.9), 0.08, segs=6, kind="detail")
C.blob("glow_off", (MX, MY, ROOF + 8.95), 0.14, segs=8, rings=5)
C.cyl("steel", (MX - 0.4, MY - 0.2, ROOF + 5.0), (MX - 0.8, MY - 0.5, ROOF + 5.0), 0.04, segs=6, kind="detail")
C.cyl("steel", (MX - 0.9, MY - 0.6, ROOF + 4.7), (MX - 0.95, MY - 0.65, ROOF + 5.3), 0.6, r2=0.1, segs=14, kind="detail")
# 제어함 (리타가 패널을 닫는다) + 케이블 트레이 + 발전기
C.box("navy", -2.2, -0.9, 1.4, 1.95, ROOF, ROOF + 1.15)
C.box("metal", -2.15, -0.95, 1.36, 1.4, ROOF + 0.2, ROOF + 1.1, kind="detail")
C.rect("glow", (-1.55, 1.355, ROOF + 0.95), (0, -1, 0), 0.22, 0.05, lift=0.005)
C.box("metal", MX + 0.6, -2.2, MY + 0.2, MY + 0.4, ROOF + 0.05, ROOF + 0.18, kind="detail")
C.box("olive", 4.0, 5.4, -4.6, -3.6, ROOF, ROOF + 0.8)
C.cyl("dark", (4.7, -4.1, ROOF + 0.8), (4.7, -4.1, ROOF + 1.2), 0.05, segs=6, kind="detail")
mk.crate(C, 5.0, -2.2, s=0.6, z=ROOF, yaw=10)
mk.crate(C, 5.4, -1.4, s=0.5, z=ROOF, yaw=-15, key="tarp")
C.marker("MARK_relay_4", (MX, MY, ROOF + 8.95))

# ---------------------------------------------------------------- 꺼진 도시
C.group("city_dark")
rng = random.Random(11)
for i in range(70):
    a = rng.uniform(0, math.tau)
    d = rng.uniform(22, 170)
    x, y = math.cos(a) * d, math.sin(a) * d
    if math.hypot(x - CORE[0], y - CORE[1]) < 22:
        continue
    w, dd = rng.uniform(10, 18), rng.uniform(10, 16)
    # 옥상에서 코어 탑을 보는 시선(쐐기 ±16°, 또는 시선에서 건물 반폭 + 10 m 안)은 비운다
    da = math.atan2(y, x) - math.atan2(CORE[1], CORE[0])
    ux, uy = CORE[0] / math.hypot(*CORE), CORE[1] / math.hypot(*CORE)
    along = x * ux + y * uy
    perp = abs(-x * uy + y * ux)
    if abs(math.atan2(math.sin(da), math.cos(da))) < math.radians(16) or (0 < along < 230 and perp < max(w, dd) / 2 + 10):
        continue
    # 겹쳐 선 건물끼리 층 띠 윗면이 같은 높이가 되지 않게 건물마다 7 mm씩(0~28 mm) 땅에 묻는다. 키트의 띠·지붕 높이는
    # 1 cm 단위라 7 mm 간격이면 새로 겹치지 않는다 (난수는 그대로)
    mk.building(C, x - w / 2, x + w / 2, y - dd / 2, y + dd / 2, floors=rng.randint(3, 9), style=("office", "apartment", "glass")[i % 3],
                far=d > 60, seed=100 + i, door=False, cctv=False, col=False, sides="-y+y-x+x", z=-0.007 * (i % 5))
ck.night_skyline(C, r=260.0, n=40, seed=12, fl=(8, 22),
                 skip=lambda x, y: abs(math.atan2(math.sin(math.atan2(y, x) - math.atan2(CORE[1], CORE[0])),
                                                  math.cos(math.atan2(y, x) - math.atan2(CORE[1], CORE[0])))) < math.radians(12))
C.box("asphalt", -400, 400, -400, 400, -0.4, -0.02, kind="fine")
# 코어 AI 탑 (꺼짐) + 켜짐 겹침
C.group("core")
mk.core_ai(C, CORE[0], CORE[1], lit=False, col=False)
C.group("CORE_on", on=0)
mk.core_ai(C, CORE[0], CORE[1], glow_overlay=True)
C.group("core")
C.marker("MARK_core_top", (CORE[0], CORE[1], 34.0 + 7.3))
C.marker("MARK_core_base", (CORE[0], CORE[1], 3.0))

# ---------------------------------------------------------------- 전파 시설 다섯 곳 (리타가 M7에서 되찾음) + R41 교란기 셋
C.group("relays")
for i, (x, y, hgt) in enumerate(RELAYS, start=1):
    if i == 4:
        continue   # 4번이 이 옥상 (리타 자리)
    C.cyl("dark", (x, y, 0), (x, y, hgt), 0.5, r2=0.2, segs=6, kind="far")
    for k in range(3):
        z = hgt * (0.45 + k * 0.18)
        C.cyl("metal", (x, y, z), (x, y, z + 0.4), 1.2 - k * 0.25, segs=8, kind="far")
    C.blob("glow_off", (x, y, hgt + 0.4), 0.7, segs=8, rings=5, kind="fine")
    C.marker(f"MARK_relay_{i}", (x, y, hgt + 0.4))
C.group("jammers")
for i, (x, y, r) in enumerate(JAMS, start=1):
    C.cyl("r41_shell", (x, y, 0), (x, y, 24), 0.6, r2=0.3, segs=6, kind="far")
    C.rbox("r41_panel", (x, y, 24.5), (2.2, 2.2, 1.0), rot=(0, 0, 45), kind="far")
    C.blob("r41_lamp", (x, y, 25.4), 0.6, segs=8, rings=5, kind="fine")
    C.marker(f"MARK_jam_{i}", (x, y, 0.0), props={"radius": r})

# ---------------------------------------------------------------- 사람들
C.group("npc")
RIFLE = "weapons/us/m4a1.glb"
C.npc("rita", (-1.55, 0.78, ROOF), "characters/rita.glb", pose="assemble", face=(-1.55, 2.0), name="리타", props={"expr": "serious"})
C.npc("jesty", (-1.9, -1.7, ROOF), "characters/squad_jesty.glb", pose="cine_kneel_radio", face=(1.5, -0.5), name="제스티",
      props={"hold_R": RIFLE, "expr": "serious"})
C.npc("sabre", (-3.6, -0.9, ROOF), "characters/squad_sabre.glb", pose="hold_rifle_ready", face=(0.0, 4.0), name="사브르",
      props={"hold_R": RIFLE, "expr": "serious"})
C.npc("rona", (4.8, 4.4, ROOF), "characters/squad_rona.glb", pose="cine_kneel_aim", face=(CORE[0], CORE[1]), name="로나",
      props={"hold_R": RIFLE, "expr": "serious"})
C.npc("karen", (-0.8, -2.6, ROOF), "characters/squad_karen.glb", pose="hold_rifle_ready", face=(1.0, 4.0), name="케이트",
      props={"hold_R": "weapons/us/m870.glb", "expr": "serious"})
# 리타가 패널을 닫고 돌아서 코어 쪽을 보는 자리
C.marker("WP_rita_look", (0.6, -0.2, ROOF))

# ---------------------------------------------------------------- 카메라
C.cam("bypass_a", [
    (0.0, (2.6, -3.4, ROOF + 1.35), (-1.4, 1.2, ROOF + 0.75), 40),
    (8.0, (2.0, -2.6, ROOF + 1.25), (-1.3, 1.2, ROOF + 0.75), 36),
])
# 옥상 난간 너머 북동쪽 코어 탑 (분대 등 너머)
C.cam("bypass_b", [
    (0.0, (-2.6, -3.6, ROOF + 1.5), (CORE[0], CORE[1], 24.0), 26),
    (7.0, (-2.2, -3.0, ROOF + 1.7), (CORE[0], CORE[1], 27.0), 24),
])
# 도시 위 높은 곳에서 천천히 돈다: 코어 탑, 다섯 시설, 교란 구역이 한 화면에
C.cam("bypass_c", [
    (0.0, (-120.0, -110.0, 150.0), (40.0, 120.0, 0.0), 48),
    (14.0, (-40.0, -150.0, 160.0), (40.0, 120.0, 0.0), 48),
])

C.group("city")
C.marker("SPAWN_player", (-0.9, 1.2, ROOF), face=CORE)
ROOT = dict(ck.NIGHT_ROOT)
ROOT.update({
    "sky": "#0a0f22",
    "fog": "140,900",
    "ambient": 1.0,
    "sunIntensity": 1.0,
    "far": 1500,
    "music": "cine_net",
    "timeOfDay": "night_blackout",
    "scene": "A3_BYPASS",
    "shots": "bypass_a,bypass_b,bypass_c",
})
C.finish("levels/cine_relay.glb", root_props=ROOT, outline=0.022)
