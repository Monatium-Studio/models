"""모나티엄 가로등 (원작 배경의 검은 가로등 + 교주 차원 금색 고리). 1막 시가전 PROP_ 배치용.

npm run model -- art/blender/props/monatium_streetlamp.py
npm run shot -- props/monatium_streetlamp.glb
규약: 원점 = 밑동 가운데, 정면 -Y. 키트 함수 monatium_city_kit.lamp와 같은 형태 (docs/art/monatium-city.md).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_streetlamp", prop=True)
mk.lamp(C, 0, 0, lit=False)
C.finish("props/monatium_streetlamp.glb", root_props={"outline": 0.008, "lampHeight": 3.6, "lightOffset": "0,3.9,0"})
