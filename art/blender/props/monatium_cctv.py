"""모나티엄 감시 카메라 기둥 (원작: 모나티엄에 감시 카메라 214,090대). PROP_ 배치용. 2막 은신 구간의 시선 표식으로도 쓴다.

npm run model -- art/blender/props/monatium_cctv.py
규약: 원점 = 밑동, 카메라가 -Y를 본다. 앵커 lens(렌즈 위치)를 둔다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
C = mk.City("monatium_cctv", prop=True)
mk.cctv_pole(C, 0, 0, yaw=0.0, h=4.2)
C.marker("lens", (0, -0.62, 4.0))
C.finish("props/monatium_cctv.glb", root_props={"outline": 0.006})
