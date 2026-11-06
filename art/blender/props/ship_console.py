"""엘피니아 함교 승무원 콘솔 (선 채로 쓰는 엘프 키 높이).

npm run model -- art/blender/props/ship_console.py
npm run shot -- props/ship_console.glb --views front,34,side,top

원점 = 바닥 중심, 조작하는 쪽 = -Y. 0.72 x 0.6 x 1.3 m. 책상 0.72 m(엘프 허리), 화면 0.85~1.28 m.
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
L = lk.Level("ship_console")
L.zone("p")
F = (0, -1, 0)

L.bev("navy_d", (0.62, 0.48, 0.04), (0, 0.04, 0.02), bevel=0.012)                 # 바닥판
L.bev("navy", (0.46, 0.32, 0.6), (0, 0.06, 0.34), bevel=0.04, seg=3)              # 받침대
L.box("gold", -0.235, 0.235, -0.105, -0.095, 0.56, 0.58, kind="detail")
L.logo((0, -0.1, 0.36), 0.14, F, disc="navy_l", ring="gold", lift=0.003)
# 기울어진 조작면 (앞이 낮다)
TILT = 16
L.bev("navy_l", (0.72, 0.4, 0.05), (0, -0.04, 0.7), rot=(TILT, 0, 0), bevel=0.018)
nz = Vector((0, -0.2756, 0.9613))             # 조작면 법선 (X축 16° 기울임)
up = Vector((0, 0.9613, 0.2756))
top_c = Vector((0, -0.04, 0.7)) + nz * 0.026
L.decal("navy_d", hw.rrect(0.62, 0.3, 0.03, n=2), tuple(top_c), tuple(nz), up=tuple(up), lift=0.002)
for r in range(2):
    for c in range(5):
        p = top_c + Vector((-0.22 + c * 0.11, 0, 0)) + up * (-0.07 + r * 0.09)
        L.decal("glow" if (r + c) % 3 else "paper", hw.rrect(0.07, 0.04, 0.008, n=1), tuple(p), tuple(nz),
                up=tuple(up), lift=0.004)
L.decal("glow", hw.circle(0.035, 12, 0.24, 0.07), tuple(top_c), tuple(nz), up=tuple(up), lift=0.004)
L.cyl("gold", (-0.36, -0.245, 0.64), (0.36, -0.245, 0.64), 0.014, verts=8, kind="detail")       # 앞 손잡이
for x in (-0.33, 0.33):
    L.cyl("metal", (x, -0.245, 0.64), (x, -0.19, 0.66), 0.012, verts=6, kind="detail")
# 세운 화면 (뒤로 8° 젖힘)
SC = Vector((0, 0.16, 1.06))
nS = Vector((0, -0.990, 0.139))
upS = Vector((0, 0.139, 0.990))
L.extrude("navy_l", hw.rrect(0.66, 0.46, 0.05, n=2), tuple(SC), tuple(nS), 0.05, up=tuple(upS), kind="main")
fc = SC + nS * 0.05
L.ring("gold", hw.rrect(0.64, 0.44, 0.045, n=2), hw.rrect(0.6, 0.4, 0.035, n=2), tuple(fc), tuple(nS), up=tuple(upS),
       lift=0.002)
L.decal("screen", hw.rrect(0.58, 0.38, 0.03, n=2), tuple(fc), tuple(nS), up=tuple(upS), lift=0.003)
R = Vector(lk.frame(tuple(nS), tuple(upS))[0])
pts = [(-0.24, -0.08), (-0.16, 0.02), (-0.08, -0.03), (0.0, 0.09), (0.08, 0.04), (0.16, 0.12), (0.24, 0.06)]
for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
    L.strip("glow", tuple(fc + R * u0 + upS * v0), tuple(fc + R * u1 + upS * v1), 0.01, tuple(nS), lift=0.005)
for k in range(4):
    L.decal("glow", hw.rrect(0.5, 0.004, 0.002, n=1, cy=-0.14 + k * 0.08), tuple(fc), tuple(nS), up=tuple(upS),
            lift=0.004)
L.decal("glow", hw.rrect(0.12, 0.03, 0.01, n=1, cx=0.18, cy=-0.14), tuple(fc), tuple(nS), up=tuple(upS), lift=0.005)
L.bev("navy", (0.44, 0.24, 0.12), (0, 0.08, 0.66), bevel=0.02)                   # 조작면 받침 (뒤쪽 틈 메움)
L.bev("navy", (0.1, 0.06, 0.34), (0, 0.17, 0.86), bevel=0.02)                    # 화면 받침 목
L.cyl("metal", (-0.07, 0.16, 0.9), (0.07, 0.16, 0.9), 0.025, verts=10, kind="detail")   # 경첩
L.decal("navy_d", hw.rrect(0.64, 0.44, 0.04, n=2), tuple(SC), tuple(-nS), up=tuple(upS), lift=0.002)

L.finish("props/ship_console.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
