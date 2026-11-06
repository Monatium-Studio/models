"""모나티엄 화단 상자 + 다듬은 생울타리 (원작 배경). 1막 엄폐물. PROP_ 배치용.

npm run model -- art/blender/props/monatium_planter.py
규약: 원점 = 바닥 가운데. 2.4 × 0.9 m, 높이 약 1.1 m.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_planter", prop=True)
mk.planter(C, -1.2, 1.2, -0.45, 0.45, h=0.55, col=False)
C.finish("props/monatium_planter.glb", root_props={"outline": 0.006})
