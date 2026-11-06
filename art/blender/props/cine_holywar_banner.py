"""성전군 깃발 (props/cine_holywar_banner.glb). 3막 「성전 개막」 컷신에서 요정 성전군 기수가 든다.

npm run model -- art/blender/props/cine_holywar_banner.py
npm run shot -- props/cine_holywar_banner.glb --views top,bottom,34,side

[원작] 에르피엔 군기 (도안·근거: lib/erpien_flag.py, 공용 소품 props/erpien_flag.glb와 같은 깃발): 짙은 초록 천 + 노란 나비,
       금 술·깃대 쪽 금 줄·창끝(폴랑 어사이드 '에르피엔 진군깃발'). 사용자 결정(2026-11-02)으로 원작 문양을 쓴다.
규약 (무기·든 소품과 같다): 원점 = 오른손 파지점, 깃대 +Y, 천은 X-Y 면(앞뒤로 보인다, +X 쪽으로 날림), 위 +Z.
NPC가 세워 들 때는 자세의 _holdRrot을 [-90, 0, 0](깃대가 위)으로 둔다. 깃대 2.6 m(파지점 아래 0.55 m), 천 1.12 × 0.65 m.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_flag as ef  # noqa: E402

cb.reset()
C = mk.City("cine_holywar_banner", prop=True)
ef.carried(ef.city(C), grip=0.55, pole=2.6, W=1.12)
C.marker("grip", (0, 0, 0))
C.finish("props/cine_holywar_banner.glb", root_props={"outline": 0.004, "prop": "banner"}, detail_outline=0.0025)
