"""모나티엄 광장 벤치 (나무 좌판 + 검은 다리, 엘프 좌판 높이 0.32 m). PROP_ 배치용.

npm run model -- art/blender/props/monatium_bench.py
규약: 원점 = 바닥 가운데, 정면 -Y(앉은 사람이 보는 방향). 앉는 NPC 마커는 seatZ=0.32.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_bench", prop=True)
mk.bench(C, 0, 0)
C.finish("props/monatium_bench.glb", root_props={"outline": 0.006, "seatZ": 0.32})
