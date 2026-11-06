"""인터루드 7 「R41 침공 개시」(D-7, 선언 방송 시점): 같은 시청 앞 광장, 이상한 하늘빛의 해 질 녘.

npm run model -- art/blender/levels/interlude_invasion.py   → public/models/levels/interlude_invasion.glb

원작: 흑뉴아가 부시장 자격으로 사멜리아의 배신을 알리고 교주 차원 침공을 선언한다. 차원문은 선언 1주일 뒤에 열린다.
R41 수색 진압반이 차원을 뒤지며 차원 미아가 생긴다. → 이 세트에는 대규모 차원문(GATE_)이 없다.
하늘에 R41 수색용 작은 차원 틈(RIFT_<n>)이 여러 개 깜빡이고, 그 틈을 타고 선언 방송이 도시 화면(SCREEN_*)에 끼어든다.
  invasion_a  리타가 고개를 든다 (얼굴 → 하늘의 틈)
  invasion_b  광장 와이드: 시청 화면의 방송, 하늘의 틈들
  invasion_c  광장 동쪽 대형 화면 앞 시민들, 켜지는 경보등
노드: RIFT_01..07 (각각 _open/_closed 상태 자식), SCREEN_plaza/cityhall/street, LIGHT_alert_01.., FX_siren_..
문서: docs/art/interlude-elias.md
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("interlude_invasion")
A = mk.downtown(C, variant="dusk", training=True, train=True, train_x=40.0)

CIV = "characters/_kit_base.glb"

# ---------------------------------------------------------------- 하늘의 차원 틈 (수색용, 작게)
C.group("RIFTS", rifts=7)
RIFTS = [
    # (id, 위치, 크기, yaw, tilt, 처음 상태)
    ("01", (-6.0, 46.0, 44.0), 11.0, 0, 35, True),     # 시청 탑 뒤 하늘 (리타 시선의 첫 틈)
    ("02", (26.0, 30.0, 58.0), 8.0, -25, 40, True),     # 코어 AI 탑 위
    ("03", (-38.0, 20.0, 30.0), 6.0, 53, 25, False),  # EBI 본부 위
    ("04", (12.0, -60.0, 36.0), 9.0, 180, 30, True),   # 큰길 건너 상가 위 (광장에서 뒤돌아볼 때)
    ("05", (-60.0, 70.0, 66.0), 15.0, 40, 45, True),  # 원경 고층 위, 큰 틈
    ("06", (8.0, -20.8, 13.5), 3.4, -150, 10, True),      # 모노레일 바로 위, 낮은 틈 (정찰 드론이 엿봄)
    ("07", (44.0, 4.0, 28.0), 5.0, -90, 25, False),     # 동쪽 대형 화면 건물 위
]
for rid, pos, size, yaw, tilt, op in RIFTS:
    mk.rift(C, rid, pos, size=size, yaw=yaw, tilt=tilt, seed=int(rid), open_state=op, flicker=0.25 + int(rid) * 0.07)
# 틈 너머로 언뜻 보이는 정찰 드론 (D-4 '하루살이' 한두 대)
C.prop("drone_recon_01", (8.3, -20.0, 13.2), "drones/drone_recon.glb", face=(4.0, 0.0),
       props={"collider": 0, "drift": "0.15,0,0.25", "rift": "RIFT_06"})
C.prop("drone_recon_02", (-5.2, 44.6, 42.5), "drones/drone_recon.glb", face=(0, 0), scale=1.0,
       props={"collider": 0, "drift": "-0.2,-0.05,0.1", "rift": "RIFT_01"})
C.marker("LIGHT_rift_glow", (-6.0, 46.0, 44.0), props={"color": mk.GLOW["magenta"], "intensity": 2.5, "range": 90.0,
                                                      "pointLight": 1})

# ---------------------------------------------------------------- 경보등 (미션이 켬)
C.group("ALERTS")
alerts = [(-6.5, -9.5), (6.5, -9.5), (-22.5, 14.5), (22.5, 14.5), (-22.8, -10.2), (22.8, -10.2)]
n = 0
for (x, y) in alerts:
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, 4.75 if abs(x) < 10 else 4.45), blink=0.6 + 0.07 * n)
    C.fx(f"siren_{n:02d}", (x, y, 4.2), sound="siren", group="alert")
for (x, y, z) in ((-15.0, 19.6, 12.4), (15.0, 19.6, 12.4), (0.0, 13.6, 9.6)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, z), blink=0.55 + 0.05 * n, siren=False)
for (x, y, z) in ((-27.6, 22.0, 16.9), (25.8, 0.0, 20.6)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, z), blink=0.7, siren=True)
    C.fx(f"siren_{n:02d}", (x, y, z), sound="siren", group="alert")

# ---------------------------------------------------------------- 사람들
C.group("npc_plaza")
rita = (-2.5, -4.0, 0.0)
# lookAt을 두지 않는다: look_up 자세(고개 약 50° 위)가 이미 RIFT_01 쪽을 본다. 시선 추적까지 더하면 고개가
# 하늘로 꺾여(약 95°) 얼굴이 어느 카메라에서도 보이지 않는다.
C.npc("rita", rita, "characters/rita.glb", pose="look_up", face=(-4.0, 10.0), name="리타",
      props={"scene": "invasion_a,invasion_b", "note": "RIFT_01을 올려다본다 (look_up 자세만으로)"})
C.npc("cathy", (-1.6, -5.0, 0.0), "characters/cathy.glb", pose="cower", face=(-3.2, 10.0), look="rita", name="캐시",
      props={"scene": "invasion_a,invasion_b"})
C.npc("jesty", (-4.0, -4.8, 0.0), "characters/squad_jesty.glb", pose="point_up", face=(-6.0, 10.0), name="제스티",
      props={"scene": "invasion_b"})
C.npc("rona", (-3.4, -6.0, 0.0), "characters/squad_rona.glb", pose="look_up", face=(-4.0, 10.0), name="로나",
      props={"scene": "invasion_b"})
crowd = [
    (5.5, -1.0, "look_up", (-4, 30)), (7.0, -2.0, "phone_up", (-4, 30)), (9.5, 0.5, "look_up", (20, 0)),
    (11.0, 3.5, "point_up", (26, 0)), (12.5, -0.5, "look_up", (26, 0)), (14.0, 2.0, "cover_mouth", (26, 0)),
    (10.5, 6.5, "look_up", (26, 0)), (13.5, 6.0, "phone_up", (26, 0)), (-9.0, 4.0, "look_up", (-6, 40)),
    (-12.0, 1.0, "hold_hands", (-6, 40)), (-11.2, 1.4, "hold_hands", (-6, 40)), (2.0, 9.5, "run", (-20, 0)),
    (-7.0, -9.8, "freeze", (-6, 40)), (16.0, -9.6, "look_up", (12, -60)),
]
for i, (x, y, pose, face) in enumerate(crowd):
    C.npc(f"civ_{i + 1:02d}", (x, y, 0.0), CIV, pose=pose, face=face, name="시민",
          props={"scene": "invasion_b,invasion_c"})

# ---------------------------------------------------------------- 카메라
sp = A["screen_plaza"]
# invasion_a: 리타 얼굴(앞 왼쪽 위, 올려다보는 얼굴) → 왼쪽 옆을 돌아 어깨 너머 로우 앵글(머리 실루엣 오른쪽 아래,
# 시청 탑과 RIFT_01 하늘) → 머리 뒤 위로 올라 리타 시점(3.6초부터 미션이 POV HUD를 띄운다).
# 머리(지름 약 0.5 m)에서 1.3 m 안으로 들어가지 않고, 마지막 시점으로 갈 때는 머리 위로 지나가 화면 아래로 빠진다.
# 캐시(리타 오른쪽 뒤 (-1.6, -5.0))를 피해 왼쪽으로 돈다.
C.cam("invasion_a", [
    (0.0, (rita[0] - 1.1, rita[1] + 1.05, 1.45), (rita[0] + 0.02, rita[1] - 0.12, 1.02), 34),
    (2.4, (rita[0] - 1.4, rita[1] - 0.75, 0.42), (9.06, 16.82, 16.77), 60),     # 방위 31°, 앙각 33° 쪽을 본다
    (3.6, (rita[0] - 0.53, rita[1] - 0.87, 1.40), (-6.0, 46.0, 44.0), 50),
    (6.0, (rita[0], rita[1] - 0.25, 1.28), (-6.0, 46.0, 44.0), 50),
])
C.cam("invasion_b", [
    (0.0, (2.0, -9.8, 0.6), (-1.0, 22.0, 13.0), 58),
    (5.0, (0.8, -8.6, 0.65), (-2.0, 26.0, 18.0), 56),
    (10.0, (-0.6, -7.6, 0.7), (-4.0, 36.0, 30.0), 54),
])
C.cam("invasion_c", [
    (0.0, (2.8, -4.6, 0.9), (sp.x - 4.0, sp.y + 0.5, sp.z - 4.5), 50),
    (4.0, (4.6, -4.2, 1.0), (sp.x, sp.y + 0.5, sp.z - 1.0), 44),
    (8.0, (6.0, -3.8, 1.1), (sp.x, sp.y, sp.z + 9.0), 50),
])

C.group("city")
C.marker("SPAWN_player", (-2.5, -6.5, 0), face=(-4, 10))
ROOT = {
    "sky": "#c3a7d4",           # 이상한 하늘빛: 해 질 녘의 라벤더·분홍
    "fog": "110,640",
    "sun": "-0.55,0.42,-0.5",
    "ambient": 1.2,
    "near": 0.1,
    "far": 900,
    "music": "interlude_invasion",
    # 확장 (엔진이 아직 읽지 않음: 몽타주 담당 참고, 지구 쪽 인터루드 세트와 같은 키)
    "sunIntensity": 1.7,
    "timeOfDay": "dusk_d7",
    "scene": "IL_INVASION",
    "shots": "invasion_a,invasion_b,invasion_c",
    "physics": 0,
    "sunColor": "#ffc6d9",
    "hemiSky": "#e9d4ff",
    "hemiGround": "#6a5470",
}
C.finish("levels/interlude_invasion.glb", root_props=ROOT, outline=0.025)
