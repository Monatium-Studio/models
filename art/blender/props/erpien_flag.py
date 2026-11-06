"""에르피엔 깃발 소품 (props/erpien_flag.glb). 요정 왕국 군기를 든 기수·세워 둔 깃대에 쓴다. 도안: lib/erpien_flag.py.

npm run model -- art/blender/props/erpien_flag.py
npm run shot -- props/erpien_flag.glb --views front,34,side,back
EF_LINEUP=1 npm run model -- art/blender/props/erpien_flag.py   → props/erpien_flag_lineup.glb (변형 비교, 커밋 안 함)

[원작] 에르피엔 군기: 짙은 초록 바탕 + 노란 나비(짙은 금색 윤곽선, 말린 꼬리). 진군깃발의 금 술·깃대 쪽 금 줄·창끝.
규약 (무기·든 소품과 같다): 원점 = 오른손 파지점, 깃대 +Y, 천은 X-Y 면(앞뒤로 보인다), 위 +Z.
NPC가 세워 들 때는 자세의 _holdRrot을 [-90, 0, 0](깃대가 위)으로 둔다. 길이 2.6 m(엘프 키의 두 배 남짓).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_flag as ef  # noqa: E402
from mathutils import Matrix  # noqa: E402

cb.reset()
LINEUP = os.environ.get("EF_LINEUP") == "1"

if not LINEUP:
    C = mk.City("erpien_flag", prop=True)
    ef.carried(ef.city(C), grip=0.55, pole=2.6, W=1.12)     # 깃대 밑동에서 파지점까지 0.55 m
    C.marker("grip", (0, 0, 0))
    C.finish("props/erpien_flag.glb", root_props={"outline": 0.004, "prop": "banner"}, detail_outline=0.0025)
else:
    # 변형 비교: 큰 군기 · 세로 현수막 · 손깃발 · 원경 깃발 · 문장 (서 있는 자세, 정면 -Y)
    C = mk.City("erpien_flag_lineup", prop=True)
    S = ef.city(C)
    ef.standard(S, Matrix.Translation((-3.4, 0, 0)), pole=2.6, W=1.12)
    ef.standard(S, Matrix.Translation((-0.6, 0, 0)), pole=2.6, W=1.12, fly=-1)
    ef.banner(S, Matrix.Translation((0.6, 0, 2.6)), W=0.9, H=2.4)
    ef.hand_flag(S, Matrix.Translation((1.5, 0, 0.9)), W=0.16 * 1.6, stick=0.34 * 1.6)
    ef.far_flag(S, Matrix.Translation((2.0, 0, 0)), W=0.9, pole=2.2)
    ef.emblem(S, Matrix.Translation((3.4, 0, 1.2)), 0.8)
    C.finish("props/erpien_flag_lineup.glb", root_props={"outline": 0.004}, detail_outline=0.0025)
