"""엘피니아 군 보급·탄약 상자 (프롤로그 함내).

npm run model -- art/blender/props/ship_crate.py
npm run shot -- props/ship_crate.glb --views front,34,side,top

원점 = 바닥 중심, 정면(-Y)에 엘프 로고와 스텐실. 0.6 x 0.45 x 0.42 m.
튜토리얼 T04의 '높이 0.4 m쯤의 탄약 상자'로 쓴다(docs/script/prologue.md). 세 개 쌓으면 1.26 m.
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_crate")
L.zone("p")
W, D, H = 0.6, 0.45, 0.42
F, B = (0, -1, 0), (0, 1, 0)

L.bev("olive", (W - 0.02, D - 0.02, H - 0.02), (0, 0, H / 2), bevel=0.02, seg=2)
# 뚜껑 이음매, 세로 보강 띠
L.box("navy_d", -W / 2 + 0.005, W / 2 - 0.005, -D / 2 + 0.005, D / 2 - 0.005, H - 0.075, H - 0.065)
for x in (-0.17, 0.17):
    L.box("hull_d", x - 0.025, x + 0.025, -D / 2 - 0.004, D / 2 + 0.004, 0.02, H - 0.02)
# 모서리 덧쇠 8개
for x in (-W / 2 + 0.03, W / 2 - 0.03):
    for y in (-D / 2 + 0.03, D / 2 - 0.03):
        for z in (0.03, H - 0.03):
            L.bev("navy", (0.075, 0.075, 0.075), (x, y, z), bevel=0.012, kind="detail")
# 잠금쇠 (앞), 양끝 손잡이
for x in (-0.17, 0.17):
    L.bev("steel", (0.05, 0.02, 0.07), (x, -D / 2 - 0.012, H - 0.07), bevel=0.006, kind="detail")
for sx in (-1, 1):
    L.bev("navy", (0.03, 0.18, 0.04), (sx * (W / 2 + 0.01), 0, H - 0.13), bevel=0.01, kind="detail")
# 앞: 남색 원판 + 금색 엘프 로고, 스텐실
L.logo((0.0, -D / 2 - 0.005, 0.2), 0.15, F, disc="navy", ring="gold", lift=0.002)
L.text("paper", "7식 탄약", 0.04, (0.0, -D / 2 - 0.005, 0.07), F, lift=0.002)
L.text("paper", "보급", 0.06, (0.0, D / 2 + 0.005, 0.2), B, lift=0.002)
L.text("paper", "1-0412", 0.032, (0.0, D / 2 + 0.005, 0.1), B, lift=0.002)
L.text("paper", "엘피니아 원정군 사령부", 0.036, (0.0, 0.0, H + 0.002), (0, 0, 1), up=(0, 1, 0), lift=0.002)

L.finish("props/ship_crate.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
