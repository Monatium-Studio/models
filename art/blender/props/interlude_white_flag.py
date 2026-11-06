"""인터루드 투항 장면의 백기 (props/interlude_white_flag.glb).

[원작] 통신이 끊기고 전선이 무너지자 헤일리가 먼저 무기를 내려놓고 투항했다(나무위키 「엘프(트릭컬 리바이브)」 2.12.1).
[오리지널] 백기는 불시착한 기함에서 뜯어 온 안테나 막대에 흰 붕대 천을 묶은 것. 막대 끝에 엘피니아 금색 고리가
          남아 있고, 천 가장자리는 그을렸다. 실존 군 휘장·문자는 없다.

원점 = 막대 아래 끝(땅에 꽂히는 점). 위 +Z, 천은 +X 쪽으로 날린다.
grip: 손으로 쥘 때의 점(엘프 손높이). 소켓에 붙일 때는 grip이 손바닥에 오게 옮긴다.

npm run model -- art/blender/props/interlude_white_flag.py
npm run shot -- props/interlude_white_flag.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import interlude_kit as ik  # noqa: E402
from mathutils import Vector  # noqa: E402

L = ik.begin("interlude_white_flag")
H = 1.95            # 막대 길이
# 막대: 살짝 휜 안테나 (3마디) + 금색 고리 + 끝 구슬
pts = [(0, 0, -0.12), (0.0, 0.0, 0.7), (0.025, 0.0, 1.35), (0.06, 0.0, H)]
for a, b in zip(pts, pts[1:]):
    L.cyl("metal", a, b, 0.017, verts=8)
for p in pts[1:-1]:
    L.obj("metal", cb.sphere("j", radius=0.02, loc=p, segments=8, rings=5))
L.cyl("gold", (0.058, 0, H - 0.04), (0.06, 0, H + 0.0), 0.028, verts=12, kind="detail")
L.obj("gold", cb.sphere("tip", radius=0.026, loc=(0.06, 0, H + 0.03), segments=10, rings=6), kind="detail")
# 아래 끝: 꺾여 찢긴 단면 (어두운 색)
L.cyl("navy", (0, 0, -0.12), (0, 0, -0.06), 0.02, verts=8, kind="detail")
# 손잡이 자리: 감은 천 띠
for i in range(5):
    z = 0.62 + i * 0.035
    L.cyl("cloth_w", (0, 0, z), (0, 0, z + 0.028), 0.021, verts=8, kind="detail")

# 천: 물결치는 판 (두께 있게 위아래 면) — 가로 0.78, 세로 0.52
W, Hc, NX, NZ = 0.78, 0.52, 14, 8
top = H - 0.08


def wave(u, v):
    """천 표면 점 (u 0..1 막대에서 멀어짐, v 0..1 위에서 아래)."""
    x = 0.07 + u * W
    amp = 0.06 * u
    y = math.sin(u * 5.2 + v * 1.3) * amp + math.sin(u * 2.1) * 0.02 * u
    z = top - v * Hc - u * u * 0.09 + math.sin(u * 4.0) * 0.015 * u
    # 끝이 찢겨 들쭉날쭉
    return Vector((x, y, z))


import bmesh  # noqa: E402

def _cloth(b):
    _fill(b)


grid = [[None] * (NZ + 1) for _ in range(NX + 1)]


def _fill(b):
    for i in range(NX + 1):
        for j in range(NZ + 1):
            u, v = i / NX, j / NZ
            p = wave(u, v)
            if i == NX:
                p.x -= (0.05 if j % 3 == 1 else 0.0) + (0.03 if j % 4 == 2 else 0.0)
            grid[i][j] = b.verts.new(p)
    for i in range(NX):
        for j in range(NZ):
            f = b.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.smooth = True


cloth = ik.obj_from_bm(_cloth, "cloth")
cb.solidify(cloth, 0.008, offset=0.0)
cb.smooth(cloth, 180)
L.obj("cloth_w", cloth)
# 그을린 가장자리 (아래쪽 끝 띠) + 묶은 매듭 2개
bs = L.bm("scorch", "fine")
for i in range(NX // 2, NX):
    for j in (NZ - 1,):
        u0, u1, v0, v1 = i / NX, (i + 1) / NX, j / NZ + 0.03, 1.0
        for side in (-1, 1):
            q = [wave(u0, v0), wave(u1, v0), wave(u1, v1), wave(u0, v1)]
            q = [p + Vector((0, side * 0.004, 0)) for p in q]
            vs = [bs.verts.new(p) for p in q]
            bs.faces.new(vs if side < 0 else list(reversed(vs)))
for z in (top + 0.0, top - Hc + 0.02):
    L.obj("cloth_w", cb.sphere("knot", radius=0.035, loc=(0.04, 0, z), scale=(1.2, 1.0, 0.8), segments=8, rings=5),
          kind="detail")
    L.cyl("cloth_w", (0.04, 0, z), (0.1, 0.02, z - 0.12), 0.012, verts=5, kind="detail")

L.marker("grip", (0.0, 0.0, 0.7))
L.marker("cloth_tip", tuple(wave(1.0, 0.5)))
ik.finish(L, "props/interlude_white_flag.glb", root_props={"outline": 0.004}, prop=True, detail_outline=0.0025)
