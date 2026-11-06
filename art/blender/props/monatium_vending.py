"""모나티엄 25 자판기 (원작: 모나티엄 자판기에는 500원을 넣는다, 편의점 모나티엄 25). PROP_ 배치용.

npm run model -- art/blender/props/monatium_vending.py
규약: 원점 = 바닥 가운데, 정면 -Y. 머티리얼 4개(몸체·짙은 판·유리·발광).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_vending", prop=True)
mk.vending(C, 0, 0, simple=True)
C.finish("props/monatium_vending.glb", root_props={"outline": 0.006})
