"""엘피니아 함선 대기 벤치.

npm run model -- art/blender/props/ship_bench.py
npm run shot -- props/ship_bench.glb --views front,34,side,top

원점 = 바닥 중심, 긴 축 = X. 1.5 x 0.36 x 0.34 m (엘프 앉은키 기준 낮은 좌판).
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_bench")
L.zone("p")

L.bev("seat", (1.46, 0.34, 0.07), (0, 0, 0.305), bevel=0.025, seg=3)
for sx in (-1, 1):
    L.bev("gold", (0.03, 0.35, 0.075), (sx * 0.735, 0, 0.305), bevel=0.01, kind="detail")
    L.bev("metal", (0.05, 0.28, 0.27), (sx * 0.58, 0, 0.135), bevel=0.012)
    L.bev("rubber", (0.07, 0.32, 0.02), (sx * 0.58, 0, 0.01), bevel=0.006)
L.cyl("metal", (-0.58, 0, 0.1), (0.58, 0, 0.1), 0.018, verts=8)
L.box("navy", -0.7, 0.7, -0.15, 0.15, 0.255, 0.27)
for x in (-0.36, 0.0, 0.36):
    L.strip("navy", (x, -0.16, 0.341), (x, 0.16, 0.341), 0.012, (0, 0, 1), lift=0.002)
L.logo((0.0, -0.172, 0.305), 0.05, (0, -1, 0), disc=None, lift=0.002)

L.finish("props/ship_bench.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
