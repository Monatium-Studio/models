"""모나티엄 진압반 바리케이드 (남보라 판 + 청록 비살상 띠). 1막 시가전 엄폐물. PROP_ 배치용.

npm run model -- art/blender/props/monatium_barricade.py
규약: 원점 = 바닥 가운데, 정면 -Y. 폭 1.6 m, 높이 0.95 m (엘프가 앉으면 몸이 숨는 높이).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_barricade", prop=True)
mk.barricade(C, 0, 0)
C.cols.clear()
C.finish("props/monatium_barricade.glb", root_props={"outline": 0.006})
