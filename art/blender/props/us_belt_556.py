"""5.56 mm 링크 탄띠 한 토막 (노획 미군 물자 소품, 바닥 줍기·M249 탄약 보급).

npm run model -- art/blender/props/us_belt_556.py
원점 = 바닥 중심. 탄띠가 바닥에서 S자로 놓인 모양, 24발 (4발마다 예광탄: 빨간 탄두 끝).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("us_belt_556")
N = 24
PITCH = 0.0102
RC = 0.0048
for k in range(N):
    t = k / (N - 1)
    x = (t - 0.5) * N * PITCH * 0.92
    y = 0.035 * math.sin(t * math.pi * 1.6)
    ang = math.degrees(math.atan2(0.035 * math.pi * 1.6 * math.cos(t * math.pi * 1.6), N * PITCH * 0.92))
    z = RC + 0.0004
    parts = [us.ycyl(f"case{k}", RC, -0.030, 0.015, z=0, verts=8, r2=0.0046, mat="brass"),
             us.ycyl(f"bullet{k}", 0.0029, 0.015, 0.031, z=0, verts=8, r2=0.0008, mat="brass"),
             us.ycyl(f"link{k}", 0.0055, -0.024, -0.016, z=0, verts=8, mat="black"),
             us.ycyl(f"link2{k}", 0.0055, -0.004, 0.002, z=0, verts=8, mat="black")]
    if k % 4 == 3:
        parts.append(us.ycyl(f"tracer{k}", 0.0014, 0.027, 0.0315, z=0, verts=8, r2=0.0006, mat="red"))
    for o in parts:
        us.xform(o, rot=(0, 0, ang), loc=(x, y, z))
    b.s(*parts)
b.anchor("socket_carry", (0, 0, 0.02))
b.finish("props/us_belt_556.glb", outline=0.002, fp="0,0,0")
