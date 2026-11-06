"""엘피니아 함선 2층 침상 (프롤로그 병력 구획 B).

npm run model -- art/blender/props/ship_bunk.py
npm run shot -- props/ship_bunk.glb --views front,34,side,top

원점 = 바닥 중심. 긴 축 = X (1.58 m), 폭 Y 0.86 m, 높이 1.62 m. 정면(사다리·통로 쪽) = -Y, 머리 = -X(벽 쪽).
엘프 키 1.2 m 기준: 아래 칸 매트리스 윗면 0.45 m, 위 칸 1.23 m.
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_bunk")
L.zone("p")

X0, X1, Y0, Y1 = -0.79, 0.79, -0.43, 0.43
DECKS = (0.30, 1.08)                # 침대 판 윗면 높이
TOP = 1.62
FRONT = (0, -1, 0)

# 기둥 4개 (건메탈, 둥근 모서리) + 금색 고리 + 볼트
for x in (X0 + 0.03, X1 - 0.03):
    for y in (Y0 + 0.03, Y1 - 0.03):
        L.bev("metal", (0.06, 0.06, TOP), (x, y, TOP / 2), bevel=0.012)
        L.cyl("gold", (x, y, TOP - 0.01), (x, y, TOP + 0.02), 0.036, verts=10, kind="detail")
        L.bev("rubber", (0.08, 0.08, 0.03), (x, y, 0.015), bevel=0.008)
        L.cyl("gold", (x, y, 0.72), (x, y, 0.76), 0.034, verts=10, kind="detail")

for zt in DECKS:
    # 옆 테 (남색) + 판 + 매트리스
    for y in (Y0 + 0.03, Y1 - 0.03):
        L.bev("navy", (X1 - X0 - 0.1, 0.04, 0.08), (0, y, zt - 0.04), bevel=0.01)
    for x in (X0 + 0.03, X1 - 0.03):
        L.bev("navy", (0.04, Y1 - Y0 - 0.1, 0.08), (x, 0, zt - 0.04), bevel=0.01)
    L.box("navy_d", X0 + 0.06, X1 - 0.06, Y0 + 0.06, Y1 - 0.06, zt - 0.05, zt - 0.02)
    L.bev("mattress", (X1 - X0 - 0.12, Y1 - Y0 - 0.12, 0.12), (0, 0, zt + 0.04), bevel=0.035, seg=2)
    # 베개 (머리 쪽 -X)
    L.bev("pillow", (0.24, 0.5, 0.08), (X0 + 0.22, 0.02, zt + 0.13), rot=(0, -8, 0), bevel=0.035, seg=2)
    # 판 앞면 볼트
    for x in (-0.5, 0.0, 0.5):
        L.decal("steel", lk.octagon(0.011), (x, Y0 + 0.01, zt - 0.04), FRONT, lift=0.002)

# 아래 칸: 덮은 모포 + 접힌 끝 / 위 칸: 각 잡아 개어 둔 모포
L.bev("blanket", (0.98, Y1 - Y0 - 0.1, 0.05), (0.26, 0, DECKS[0] + 0.12), bevel=0.02, seg=2)
L.cyl("blanket", (-0.23, Y0 + 0.06, DECKS[0] + 0.14), (-0.23, Y1 - 0.06, DECKS[0] + 0.14), 0.035, verts=10)
L.strip("paper", (-0.18, Y0 + 0.06, DECKS[0] + 0.146), (-0.18, Y1 - 0.06, DECKS[0] + 0.146), 0.03, (0, 0, 1),
        lift=0.002)
L.bev("blanket", (0.32, 0.56, 0.12), (X1 - 0.3, 0.0, DECKS[1] + 0.16), bevel=0.02, seg=2)
L.bev("helmet", (0.22, 0.2, 0.05), (0.15, 0.1, DECKS[1] + 0.125), bevel=0.02)       # 개인 소지품 주머니

# 머리판·발판 (남색, 스타디움 구멍, 발판 바깥에 로고와 이름표)
for x, sgn in ((X0 + 0.03, -1), (X1 - 0.03, 1)):
    for (z0, z1) in ((DECKS[0] + 0.02, DECKS[0] + 0.42), (DECKS[1] + 0.02, DECKS[1] + 0.4)):
        L.box("navy", x - 0.015, x + 0.015, Y0 + 0.06, Y1 - 0.06, z0, z1)
        for k in (-1, 1):
            L.decal("navy_d", hw.stadium(0.2, 0.06), (x + sgn * 0.016, k * 0.16, z1 - 0.1), (sgn, 0, 0),
                    lift=0.002)
L.logo((X1 + 0.002, 0.0, DECKS[1] + 0.22), 0.16, (1, 0, 0), disc="navy_l", ring="gold", lift=0.003)
L.decal("paper", hw.rrect(0.22, 0.07, 0.01, n=1), (X1 + 0.002, 0.0, DECKS[0] + 0.3), (1, 0, 0), lift=0.003)
L.text("navy_d", "정찰 침투조", 0.03, (X1 + 0.002, 0.0, DECKS[0] + 0.3), (1, 0, 0), lift=0.005)

# 위 칸 안전 난간 (정면, 사다리 쪽은 비움)
for x in (X0 + 0.25, 0.1):
    L.cyl("metal", (x, Y0 + 0.03, DECKS[1]), (x, Y0 + 0.03, DECKS[1] + 0.26), 0.015, verts=8, kind="detail")
L.bev("navy", (0.82, 0.04, 0.05), (X0 + 0.43, Y0 + 0.03, DECKS[1] + 0.27), bevel=0.012)
L.bev("navy", (0.82, 0.04, 0.05), (X0 + 0.43, Y1 - 0.03, DECKS[1] + 0.27), bevel=0.012)

# 사다리 (정면 발 쪽): 은색 봉 두 개 + 발판 4개
LX0, LX1, LY = 0.38, 0.68, Y0 - 0.02
for x in (LX0, LX1):
    L.cyl("steel", (x, LY, 0.04), (x, LY, DECKS[1] + 0.3), 0.016, verts=8, kind="detail")
    L.cyl("steel", (x, LY, DECKS[1] + 0.3), (x, Y0 + 0.03, DECKS[1] + 0.3), 0.016, verts=8, kind="detail")
for z in (0.22, 0.5, 0.78, 1.0):
    L.cyl("metal", (LX0, LY, z), (LX1, LY, z), 0.016, verts=8, kind="detail")
    L.box("hazard", LX0 + 0.04, LX1 - 0.04, LY - 0.017, LY - 0.012, z - 0.012, z + 0.012, kind="fine")

# 침대 밑 서랍 (남색 + 은색 손잡이 + 금색 단추)
L.bev("navy_l", (1.1, 0.04, 0.18), (-0.1, Y0 + 0.05, 0.13), bevel=0.012)
L.bev("steel", (0.24, 0.025, 0.025), (-0.1, Y0 + 0.02, 0.15), bevel=0.008, kind="detail")
L.decal("gold", lk.octagon(0.012), (0.36, Y0 + 0.03, 0.15), FRONT, lift=0.002)
L.decal("paper", hw.rrect(0.12, 0.04, 0.008, n=1), (-0.48, Y0 + 0.03, 0.15), FRONT, lift=0.002)
# 위 칸 아래 독서등 (머리 쪽)
L.bev("navy", (0.12, 0.08, 0.025), (X0 + 0.22, Y0 + 0.14, DECKS[1] - 0.065), bevel=0.008, kind="detail")
L.decal("glow", hw.stadium(0.08, 0.035), (X0 + 0.22, Y0 + 0.14, DECKS[1] - 0.078), (0, 0, -1), up=(1, 0, 0),
        lift=0.002)

L.finish("props/ship_bunk.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
