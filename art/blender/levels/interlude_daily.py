"""인터루드 6 「평화로운 일상」: 모나티엄 시청 앞 광장 일대, 진압반 훈련장 한쪽.

npm run model -- art/blender/levels/interlude_daily.py   → public/models/levels/interlude_daily.glb

원작: 엘리아스 정착 약 100년 뒤의 모나티엄(교주 등장 직전). 오리지널: 리타의 진압반 특수작전부 생활.
배치는 도시 키트의 downtown()을 그대로 쓴다(인터루드 7, 1막 M1·M2와 같은 장소).
장면(컷)마다 NPC 마커에 scene 속성이 있다. 몽타주는 그 컷의 NPC만 보이게 한다.
  daily_a  거리: 큰길 건너에서 본 광장과 시청, 머리 위로 모노레일이 지나간다
  daily_b  훈련장: 분대 사격 자세 훈련, 칸나의 잔소리
  daily_c  광장: 자판기 앞에서 캐시와 재회, 벤치에서 먹는 분대원
문서: docs/art/interlude-elias.md
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("interlude_daily")
A = mk.downtown(C, variant="day", training=True, train=True)

CIV = "characters/_kit_base.glb"
RITA = "characters/rita.glb"
SQ = {k: f"characters/squad_{k}.glb" for k in ("rona", "sabre", "jesty", "karen")}
CARBINE = "weapons/monatium/monatium_riot_carbine.glb"   # 훈련 사수들이 손에 든 진압 카빈 (hold_R)
NAMES = {"rona": "로나", "sabre": "사브르", "jesty": "제스티", "karen": "케이트"}
Y = mk.AVENUE_Y

# ---------------------------------------------------------------- daily_a: 거리
C.group("npc_street")
walk_hi = A["road"]["walk_hi"]          # 광장 쪽 보도 바깥 끝 (y=-11)
for i, (x, y, pose, face, look) in enumerate([
    (-7.0, walk_hi - 1.4, "walk", (-30, walk_hi - 1.4), None),
    (-4.2, walk_hi - 2.2, "walk", (30, walk_hi - 2.2), None),
    (3.0, -7.5, "chat", (4.0, -7.0), "civ_04"),
    (4.0, -7.0, "chat", (3.0, -7.5), "civ_03"),
    (7.9, -3.0, "sit_bench", (8.0, -8.0), None),
    (-10.5, -8.6, "phone", (-10.5, -12), None),
    (14.0, walk_hi - 1.0, "wave", (8, walk_hi - 1.0), None),
    (-15.5, -3.0, "eat", (-12.0, -3.0), None),
]):
    C.npc(f"civ_{i + 1:02d}", (x, y, 0), CIV, pose=pose, face=face, look=look, name="시민",
          props={"scene": "daily_a", "seatZ": 0.32 if pose == "sit_bench" else 0.0})
# 큰길 건너편 보도 시민 (전경)
for i, (x, dy, pose, fx) in enumerate([(-6.5, 2.6, "walk", 30), (5.0, 2.4, "carry_box", -30), (9.0, 1.6, "chat", 9.9),
                                       (9.9, 1.8, "chat", 9.0)]):
    yy = A["road"]["walk_lo"] + dy
    C.npc(f"civ_s{i + 1:02d}", (x, yy, 0), CIV, pose=pose, face=(fx, yy), name="시민", props={"scene": "daily_a"})
# 모노레일 기둥(x = ±8)에서 6 m 넘게 떨어진 가운데 구간만 옆으로 민다 (끝점 x=3에서는 오른쪽 기둥이 화면 가장자리를 크게 가렸다)
C.cam("daily_a", [
    (0.0, (-2.0, -29.6, 1.0), (-1.2, 8.0, 5.0), 52),
    (4.0, (0.0, -29.7, 1.1), (0.4, 10.0, 7.5), 50),
    (8.0, (2.0, -29.6, 1.2), (1.2, 14.0, 11.0), 48),
])

# ---------------------------------------------------------------- daily_b: 진압반 훈련장
C.group("npc_yard")
yd = A["yard"]
dx, dy = yd["drill"].x, yd["drill"].y                # 사수 선 (표적은 +Y)
line = [("rona", -3.6), ("sabre", -1.8), ("rita", 0.0), ("jesty", 1.8), ("karen", 3.6)]
for nid, ox in line:
    model = RITA if nid == "rita" else SQ[nid]
    pose = "train_drill"
    props = {"scene": "daily_b", "hold_R": CARBINE}     # 카빈을 들고 겨눈다 (빈손 견착 자세였다)
    if nid == "jesty":
        pose = "sheepish"           # 혼나는 중 (카빈 없이 뒤통수를 긁는다)
        props = {"scene": "daily_b"}
    C.npc(f"{nid}_drill", (dx + ox, dy, 0), model, pose=pose, face=(dx + ox, dy + 10),
          name="리타" if nid == "rita" else NAMES[nid], props=props)
# 칸나는 사수 선 **뒤**(표적 반대쪽) 4 m에서 사수들을 지켜본다. 사로 앞(+Y)은 사선이라 사람을 두지 않는다.
# 어깨 너머 카메라(drillCam: 사수 선 2.8 m 뒤를 옆으로 흐름)가 칸나 머리를 지나가지 않게 그보다 더 뒤에 둔다
C.npc("kanna_drill", (dx + 2.4, dy - 4.0, 0), "characters/kanna.glb", pose="scold", face=(dx + 1.8, dy),
      look="jesty_drill", name="칸나", props={"scene": "daily_b"})
C.npc("riot_drill_01", (dx - 6.5, dy, 0), "characters/_kit_elfinia_soldier.glb", pose="train_drill",
      face=(dx - 6.5, dy + 12), name="진압반원", props={"scene": "daily_b", "hold_R": CARBINE})
C.cam("daily_b", [
    (0.0, (dx - 2.5, dy + 7.0, 0.8), (dx - 0.5, dy, 0.85), 45),
    (4.0, (dx + 1.5, dy + 6.4, 0.9), (dx + 1.6, dy + 0.4, 0.85), 40),
    (8.0, (dx + 4.8, dy + 4.6, 1.0), (dx + 2.0, dy + 1.2, 0.9), 36),
])

# ---------------------------------------------------------------- daily_c: 광장 (캐시와 재회)
C.group("npc_plaza")
vx, vy = A["vending"].x, A["vending"].y
C.npc("cathy_plaza", (vx - 1.0, vy - 1.6, 0), "characters/cathy.glb", pose="wave", face=(vx - 1.6, vy - 5.0),
      look="rita_plaza", name="캐시", props={"scene": "daily_c"})
C.npc("rita_plaza", (vx - 1.6, vy - 5.0, 0), RITA, pose="idle", face=(vx - 1.0, vy - 1.6), look="cathy_plaza",
      name="리타", props={"scene": "daily_c"})
# 벤치(광장 동쪽 x=17.5-2.6, y=-6 / 1.5)에서 먹는 분대원
C.npc("rona_plaza", (14.9, 1.0, 0), SQ["rona"], pose="eat", face=(10, 1.0), name="로나",
      props={"scene": "daily_c", "seatZ": 0.32})
C.npc("karen_plaza", (14.9, 2.0, 0), SQ["karen"], pose="eat", face=(10, 2.0), name="케이트",
      props={"scene": "daily_c", "seatZ": 0.32})
C.npc("sabre_plaza", (13.6, 3.6, 0), SQ["sabre"], pose="chat", face=(14.9, 2.0), look="karen_plaza", name="사브르",
      props={"scene": "daily_c"})
C.npc("jesty_plaza", (12.6, 0.4, 0), SQ["jesty"], pose="laugh", face=(14.9, 1.0), name="제스티",
      props={"scene": "daily_c"})
C.cam("daily_c", [
    (0.0, (vx + 3.4, vy - 8.6, 1.4), (vx - 2.6, vy - 3.2, 0.8), 46),
    (3.5, (vx + 0.6, vy - 9.0, 1.1), (vx - 1.6, vy - 2.6, 0.85), 38),
    (7.0, (vx - 0.3, vy - 7.2, 1.0), (vx - 1.0, vy - 1.6, 0.9), 32),
])

C.group("city")
C.marker("SPAWN_player", (0, -6, 0), face=(0, 10))
ROOT = {
    "sky": "#a6d8f4",
    "fog": "140,760",
    "sun": "0.45,1,0.35",
    "ambient": 1.55,
    "near": 0.1,
    "far": 900,
    "music": "interlude_daily",
    # 확장 (엔진이 아직 읽지 않음: 몽타주 담당 참고, 지구 쪽 인터루드 세트와 같은 키)
    "sunIntensity": 2.4,
    "hemiSky": "#eaf4ff",
    "hemiGround": "#8a8070",
    "timeOfDay": "noon",
    "scene": "IL_DAILY",
    "shots": "daily_a,daily_b,daily_c",
    "physics": 0,
    "sunColor": "#fff4e0",
}
C.finish("levels/interlude_daily.glb", root_props=ROOT, outline=0.025)
