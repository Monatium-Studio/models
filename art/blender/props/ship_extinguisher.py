"""엘피니아 함선 벽걸이 소화기 (사격장 대기실, 튜토리얼 T01 재시도 대사 '그건 소화기야').

npm run model -- art/blender/props/ship_extinguisher.py
npm run shot -- props/ship_extinguisher.glb --views front,34,side,top

원점 = 벽 아래 바닥, 정면 = -Y(등판이 +Y 벽에 붙음). 0.26 x 0.2 x 0.86 m. 일부러 발광부가 없다.
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_extinguisher")
L.zone("p")
F = (0, -1, 0)
CY = -0.03

L.bev("navy", (0.22, 0.03, 0.62), (0, 0.085, 0.5), bevel=0.012)                        # 벽 판
L.bev("navy", (0.18, 0.12, 0.03), (0, 0.03, 0.2), bevel=0.008)                          # 받침
L.cyl("red", (0, CY, 0.215), (0, CY, 0.62), 0.072, verts=20)
L.obj("red", cb.sphere("dome", radius=0.072, loc=(0, CY, 0.62), scale=(1, 1, 0.55), segments=20, rings=8))
for z in (0.3, 0.55):                                                                    # 고정 띠
    L.cyl("navy", (0, CY, z - 0.012), (0, CY, z + 0.012), 0.075, verts=20, kind="detail")
    L.box("navy", -0.02, 0.02, CY + 0.06, 0.085, z - 0.012, z + 0.012, kind="detail")
L.cyl("metal", (0, CY, 0.65), (0, CY, 0.72), 0.022, verts=10)                           # 밸브
L.bev("gold", (0.03, 0.12, 0.016), (0, CY - 0.04, 0.735), rot=(-12, 0, 0), bevel=0.006, kind="detail")
L.bev("gold", (0.026, 0.1, 0.014), (0, CY - 0.035, 0.705), rot=(8, 0, 0), bevel=0.005, kind="detail")
L.cyl("paper", (0.0, CY - 0.024, 0.69), (0.0, CY - 0.034, 0.69), 0.016, verts=10, kind="detail")   # 압력계
L.strip("red", (0.0, CY - 0.0345, 0.69), (0.008, CY - 0.0345, 0.698), 0.003, F, lift=0.001)
L.obj("rubber", hw.sweep("hose", [(0.02, CY, 0.7), (0.07, CY - 0.02, 0.66), (0.09, CY - 0.03, 0.5),
                                  (0.085, CY - 0.04, 0.33), (0.07, CY - 0.05, 0.28)],
                         hw.circle(0.011, 6)))
L.cyl("steel", (0.07, CY - 0.05, 0.29), (0.07, CY - 0.05, 0.24), 0.014, verts=8, kind="detail")
# 앞 이름표 (흰 판 + 붉은 글자 + 작은 금색 로고)
L.decal("paper", hw.rrect(0.1, 0.16, 0.015, n=2), (0, CY - 0.0725, 0.43), F, lift=0.001)
L.text("red", "소화기", 0.028, (0, CY - 0.0735, 0.47), F, lift=0.001)
L.logo((0, CY - 0.0735, 0.405), 0.04, F, disc=None, lift=0.001)

L.finish("props/ship_extinguisher.glb", root_props={"outline": 0.004}, outline=0.004, detail_outline=0.0025,
         prop=True)
