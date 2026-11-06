"""2막 시네마틱 「뮤트 조우」 출연진 겹침 세트: M4 「폐허」 끝 고가 밑(B7), 정전된 밤.

npm run model -- art/blender/levels/cine_ruins.py   → public/models/levels/cine_ruins.glb
대본: docs/script/act2c.md (A2_MUTE), 장면: src/game/missions/cine/a2Mute.ts

무대는 M4 레벨(levels/m4_ruins.glb) 그 자체다. 이 세트에는 지형이 없고 출연진(리타·분대 넷·뮤트)만 M4 좌표 그대로 서 있다.
본편 흐름은 M4가 끝난 그 자리(레벨이 붙은 채)에서 컷신이 이어지고, 이 세트를 위에 겹친다 (예전에는 시청 서쪽 상가 골목을 본뜬
따로 지은 세트였다: 플레이가 끝난 고가 밑과 컷신 장소가 달랐다, 2026-11-04 사용자 지적). 챕터 선택처럼 M4 없이 들어오면 장면이
M4 레벨을 무대로만(물리·인물·전투 없이) 읽는다.

[원작] 둠스데이 프로토콜로 모나티엄의 인프라가 꺼졌다. 흑뉴아(R41)가 시청을 장악했다.
[오리지널] 시청 밖까지 철수한 분대가 고가 밑 남쪽 통로에서 멈춘다(북쪽 끝은 잔해에 막혔다). 1막 내내 HUD를 흔들던 뮤트가
모닥불 곁 무너진 상판 더미에 걸터앉아 있다가 리타 앞에 뛰어내리고, 실로 동쪽(수용소 쪽) 길을 긋는다.

좌표: Blender Z-up, M4 레벨과 같다 (art/blender/lib/m4_mute_stage.py). 리타·분대 자리는 기준점이다: 본편 흐름에서는 실제로 멈춘
리타·분대 자리를 쓴다. 카메라·경로점은 M4 레벨에 있다 (CAM_mute_*, WP_mute_*, WP_thread_*, WP_rita_go_*).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import m4_mute_stage as ms  # noqa: E402

cb.reset()
C = mk.City("cine_ruins")

C.group("npc")
RIFLE = "weapons/us/m4a1.glb"
SHOTGUN = "weapons/us/m870.glb"
RX, RY, _ = ms.RITA
NORTH = (RX, RY + 20.0)                      # 북쪽 끝 잔해 (막힌 길)
# 리타: 분대 앞, 북쪽(막힌 길)을 본다
C.npc("rita", ms.RITA, "characters/rita.glb", pose="cine_kneel_rifle", face=(RX + 0.4, RY + 20.0), name="리타",
      props={"hold_R": RIFLE, "expr": "serious"})
# 분대: 리타 뒤·옆에 웅크림 (m4.ts squadAround 자리). 제스티는 사브르를 보고, 케이트는 뒤(남쪽 뒷골목)를 지킨다
C.npc("sabre", ms.SQUAD["sabre"], "characters/squad_sabre.glb", pose="cine_kneel_rifle", face=(RX - 0.6, RY + 20.0),
      name="사브르", props={"hold_R": RIFLE, "expr": "serious"})
C.npc("jesty", ms.SQUAD["jesty"], "characters/squad_jesty.glb", pose="cine_kneel_rifle", face=ms.SQUAD["sabre"][:2],
      name="제스티", props={"hold_R": RIFLE, "expr": "serious", "lookAt": "NPC_sabre"})
C.npc("rona", ms.SQUAD["rona"], "characters/squad_rona.glb", pose="cine_kneel_rifle", face=(RX + 2.6, RY + 18.0),
      name="로나", props={"hold_R": RIFLE})
C.npc("karen", ms.SQUAD["karen"], "characters/squad_karen.glb", pose="cine_kneel_rifle", face=(RX + 2.0, RY - 14.0),
      name="케이트", props={"hold_R": SHOTGUN})
# 뮤트: 모닥불 곁 무너진 상판 더미 남동쪽 끝에 걸터앉음 (seatZ = 판 윗면). 리타 쪽(남동)을 내려다본다
C.npc("mute", ms.MUTE, "characters/mute.glb", pose="cine_ledge_sit", face=(RX, RY), name="뮤트",
      props={"seatZ": ms.MUTE_SEAT, "expr": "smirk"})

C.group("city")
C.marker("SPAWN_player", ms.RITA, face=NORTH)
# 환경은 M4 레벨과 같다 (붙이면 장면이 M4 레벨의 환경을 다시 건다)
C.finish("levels/cine_ruins.glb", root_props={
    "sky": "#0d1220", "fog": "16,130", "sun": "-0.35,0.8,0.45", "sunColor": "#9fb2e6", "sunIntensity": 0.8,
    "ambient": 1.05, "hemiSky": "#4a5a86", "hemiGround": "#2a2430", "timeOfDay": "night", "music": "act2_ruins",
    "scene": "A2_MUTE", "stage": "m4_ruins", "shots": "mute_a,mute_c,mute_d,mute_e,mute_f",
}, outline=0.022)
