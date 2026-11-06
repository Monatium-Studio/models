"""엘피니아 정찰 침투조 장비 거치대 (벽 붙박이): 7식 소총 3정, 헬멧 3개, 탄띠.

npm run model -- art/blender/props/ship_gear_rack.py
npm run shot -- props/ship_gear_rack.glb --views front,34,side,top

원점 = 바닥 중심, 정면 = -Y(등판이 +Y 벽에 붙음). 1.5 x 0.42 x 1.55 m.
소총은 weapons/elfinia/elfinia_rifle(7식 '톱니')의 실루엣을 줄인 거치용 모형이다(회녹 몸통, 불펍, 금색 총구 고리).
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_gear_rack")
L.zone("p")
F = (0, -1, 0)
W = 1.5

L.box("navy", -W / 2 + 0.04, W / 2 - 0.04, 0.14, 0.19, 0.06, 1.5)                       # 등판
L.ring("hull_d", hw.rrect(W - 0.2, 1.3, 0.08, n=2), hw.rrect(W - 0.24, 1.26, 0.06, n=2), (0, 0.14, 0.8), F,
       lift=0.002)
for sx in (-1, 1):
    L.bev("metal", (0.06, 0.4, 1.55), (sx * (W / 2 - 0.03), 0.0, 0.775), bevel=0.015)
    L.cyl("gold", (sx * (W / 2 - 0.03), -0.17, 1.55), (sx * (W / 2 - 0.03), -0.17, 1.57), 0.04, verts=10,
          kind="detail")
L.bev("navy_d", (W - 0.12, 0.36, 0.1), (0, 0.0, 0.05), bevel=0.015)                  # 아래 받침 (개머리 홈)
L.bev("navy", (W - 0.12, 0.3, 0.04), (0, 0.03, 1.22), bevel=0.012)                   # 위 선반
L.box("gold", -W / 2 + 0.06, W / 2 - 0.06, -0.125, -0.12, 1.2, 1.24, kind="detail")
L.logo((0, -0.126, 1.36), 0.12, F, disc="navy", ring="gold", lift=0.003)
L.text("paper", "7식", 0.05, (0.2, 0.14, 1.36), F, lift=0.003)

# 소총 3정 (세워 둠, 총구 위, 옆면이 앞을 본다). 옆모습 (u = 총의 위아래(+u = 조준기), v = 길이 방향 위)
body = [(-0.045, 0.06), (0.05, 0.06), (0.055, 0.36), (0.04, 0.40), (0.035, 0.56), (0.02, 0.60), (-0.02, 0.60),
        (-0.03, 0.56), (-0.035, 0.40), (-0.05, 0.36)]
for i, x in enumerate((-0.42, 0.0, 0.42)):
    L.obj("olive", cb.profile_extrude("rifle", [(x + u, v) for u, v in body], 0.045, axis="Y", loc=(0, 0.0, 0)))
    L.box("metal", x - 0.05, x + 0.056, -0.026, 0.026, 0.27, 0.4)                       # 리시버
    L.bev("rubber", (0.07, 0.04, 0.12), (x - 0.085, 0.0, 0.22), rot=(0, -10, 0), bevel=0.01)   # 탄창 (손잡이 뒤)
    L.bev("rubber", (0.06, 0.036, 0.05), (x - 0.075, 0.0, 0.335), rot=(0, 20, 0), bevel=0.01)  # 손잡이
    L.bev("olive", (0.016, 0.04, 0.14), (x - 0.115, 0.0, 0.33), bevel=0.006)                  # D자 고리 앞 기둥
    L.cyl("rubber", (x, 0.0, 0.6), (x, 0.0, 0.72), 0.011, verts=8)                     # 총열
    L.cyl("gold", (x, 0.0, 0.7), (x, 0.0, 0.73), 0.016, verts=10, kind="detail")        # 금색 총구 고리
    L.bev("metal", (0.035, 0.03, 0.16), (x + 0.075, 0.0, 0.36), bevel=0.008)            # 운반 손잡이 + 조준기
    L.decal("glow", hw.circle(0.008, 6), (x + 0.075, -0.016, 0.43), (0, -1, 0), lift=0.002)
    L.decal("navy", hw.circle(0.02, 12), (x - 0.005, -0.023, 0.47), (0, -1, 0), lift=0.002)
    L.logo((x - 0.005, -0.023, 0.47), 0.026, (0, -1, 0), disc=None, lift=0.004)
    L.box("gold", x - 0.07, x + 0.07, -0.05, -0.03, 0.78, 0.81, kind="detail")          # 거치 고리
    L.box("navy", x - 0.07, x - 0.055, -0.05, 0.14, 0.78, 0.81, kind="detail")
    L.box("navy", x + 0.055, x + 0.07, -0.05, 0.14, 0.78, 0.81, kind="detail")
# 헬멧 3개 (선반 위) + 통신기 LED
for x in (-0.45, 0.0, 0.45):
    L.dome("helmet", (x, 0.02, 1.24), 0.125, scale=(1.0, 1.08, 0.85))
    L.obj("navy", hw.torus("rim", 0.122, 0.015, loc=(x, 0.02, 1.255), seg=12, rseg=4), kind="detail")
    L.bev("navy", (0.045, 0.045, 0.05), (x + 0.125, 0.0, 1.31), bevel=0.01, kind="detail")
    L.decal("glow", lk.octagon(0.009), (x + 0.148, 0.0, 1.32), (1, 0, 0), lift=0.002)
# 걸이에 건 탄띠·주머니
for x in (-0.6, 0.6):
    L.bev("navy_d", (0.14, 0.06, 0.32), (x, 0.08, 0.95), bevel=0.02)
    L.bev("helmet", (0.11, 0.05, 0.08), (x, 0.045, 0.9), bevel=0.015)
    L.cyl("steel", (x, 0.14, 1.12), (x, 0.06, 1.12), 0.01, verts=6, kind="detail")

L.finish("props/ship_gear_rack.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
