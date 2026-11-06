"""모래주머니 벽 (진압반 훈련장, 1막 엄폐). PROP_ 배치용.

npm run model -- art/blender/props/monatium_sandbags.py
규약: 원점 = 바닥 가운데, 정면 -Y. 폭 약 2.5 m, 높이 0.8 m.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_sandbags", prop=True)
mk.sandbag_wall(C, 0, 0)
C.finish("props/monatium_sandbags.glb", root_props={"outline": 0.006})
