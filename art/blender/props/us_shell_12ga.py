"""12게이지 산탄 1발 (M870 장전 애니메이션용 손 소품, 바닥 흩뿌림 소품).

npm run model -- art/blender/props/us_shell_12ga.py
원점 = 탄피 중심, 축 = +Y (탄두 쪽 = 크림프 = +Y). M870 사이드새들 탄과 같은 색.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("us_shell_12ga")
R = 0.0104
L = 0.070
y0 = -L / 2
b.s(us.ycyl("hull", R, y0 + 0.012, L / 2 - 0.002, verts=16, mat="red"))
b.s(us.ycyl("crimp", R, L / 2 - 0.002, L / 2, r2=R - 0.004, verts=16, mat="red"))
b.s(us.ycyl("head", R + 0.0004, y0 + 0.0015, y0 + 0.012, verts=16, mat="brass"))
b.s(us.ycyl("rim", R + 0.0011, y0, y0 + 0.0015, verts=16, mat="brass"))
b.f(us.ycyl("primer", 0.0028, y0 - 0.0002, y0, verts=10, mat="steel"))
b.f(us.text("mk", "12 GA  00 BUCK", 0.0050, (0, 0.006, R + 0.0002), right=(0, 1, 0), up=(-1, 0, 0), mat="black"))
b.anchor("socket_grip", (0, 0, 0))
b.finish("props/us_shell_12ga.glb", outline=0.0015, fp="0.08,-0.1,-0.2")
