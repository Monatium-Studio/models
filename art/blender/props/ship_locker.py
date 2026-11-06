"""엘피니아 함선 사물함 3칸 묶음 (프롤로그 병력 구획 B).

npm run model -- art/blender/props/ship_locker.py
npm run shot -- props/ship_locker.glb --views front,34,side,top

원점 = 바닥 중심, 정면(문) = -Y. 1.2 x 0.44 x 1.75 m (엘프 키 1.2 m, 맨 위에 헬멧과 더플백).
메시는 collider=0. 레벨이 COL_ 박스로 충돌을 맡는다.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
L = lk.Level("ship_locker")
L.zone("p")
W, D, H = 1.2, 0.44, 1.68
Y0 = -D / 2
F = (0, -1, 0)

L.bev("navy", (W, D - 0.02, 0.08), (0, 0.01, 0.04), bevel=0.01)                      # 받침
L.bev("helmet", (W, D, H - 0.08), (0, 0, 0.08 + (H - 0.08) / 2), bevel=0.012)          # 몸통
L.bev("navy", (W + 0.03, D + 0.03, 0.06), (0, 0, H + 0.03), bevel=0.012)                # 위 테
L.box("gold", -W / 2 - 0.016, W / 2 + 0.016, Y0 - 0.016, Y0 - 0.012, H + 0.005, H + 0.025, kind="detail")
for i, cx in enumerate((-0.4, 0.0, 0.4)):
    zc = 0.1 + 1.54 / 2
    L.bev("olive", (0.37, 0.025, 1.52), (cx, Y0 - 0.008, zc), bevel=0.01)
    fy = Y0 - 0.021
    for z in (1.46, 1.40, 1.34):
        L.decal("navy_d", hw.stadium(0.22, 0.026), (cx, fy, z), F, lift=0.002)
    for z in (0.32, 0.26, 0.20):
        L.decal("navy_d", hw.stadium(0.22, 0.026), (cx, fy, z), F, lift=0.002)
    L.decal("paper", hw.rrect(0.16, 0.06, 0.01, n=1), (cx, fy, 1.2), F, lift=0.002)
    L.text("navy_d", f"B-0{i + 1}", 0.032, (cx, fy, 1.2), F, lift=0.004)
    L.logo((cx, fy, 1.03), 0.09, F, disc="navy", lift=0.003)
    hx = cx + 0.14
    L.bev("steel", (0.03, 0.03, 0.16), (hx, Y0 - 0.03, 0.86), bevel=0.01, kind="detail")
    L.decal("steel", lk.octagon(0.012), (cx - 0.15, fy, 1.58), F, lift=0.002)
    L.decal("steel", lk.octagon(0.012), (cx - 0.15, fy, 0.16), F, lift=0.002)
# 위: 헬멧 둘, 더플백
for x, rz in ((-0.38, 15), (0.05, -20)):
    L.dome("helmet", (x, 0.0, H + 0.06), 0.13, scale=(1.0, 1.08, 0.85))
    L.obj("navy", hw.torus("rim", 0.128, 0.016, loc=(x, 0.0, H + 0.065), seg=12, rseg=4), kind="detail")
    L.bev("navy", (0.05, 0.05, 0.06), (x + 0.13, -0.02, H + 0.12), bevel=0.012, kind="detail")
    L.decal("glow", lk.octagon(0.01), (x + 0.156, -0.02, H + 0.13), (1, 0, 0), lift=0.002)
L.cyl("blanket", (0.22, 0.02, H + 0.12), (0.56, 0.02, H + 0.12), 0.1, verts=14)
L.cyl("navy", (0.3, 0.02, H + 0.12), (0.32, 0.02, H + 0.12), 0.103, verts=14, kind="detail")
L.cyl("navy", (0.46, 0.02, H + 0.12), (0.48, 0.02, H + 0.12), 0.103, verts=14, kind="detail")

L.finish("props/ship_locker.glb", root_props={"outline": 0.005}, outline=0.005, detail_outline=0.003, prop=True)
