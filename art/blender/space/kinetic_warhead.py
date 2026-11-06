"""운동에너지 탄두 (ICBM 탄두 버스가 푸는 관통체, 프롤로그 엔딩).

[오리지널] 폭약 없이 속도로만 뚫는 길쭉한 다트형 관통체. 기함 함교를 직격한다.
  - 짙은 금속 막대 동체 + 뾰족한 원뿔 촉 + 꼬리 안정 날개 4장 + 꼬리 띠
  - 재진입 열 발광 (UNLIT): 촉을 감싼 흰·주황 열 덮개(heat_glow)와 반투명 플라스마 꼬리(heat_glow_trail)
  - earth_icbm.glb의 warhead_slot_<n>에 붙여 날린다.

노드
  kinetic_warhead           루트 (원점 = 무게 중심, 진행 방향 = Blender -Y = three.js +Z)
    kinetic_warhead_body    동체 (정점색 툰, 아웃라인 O)
    kinetic_warhead_fine    띠 (noOutline)
    heat_glow               촉 열 발광 (UNLIT). 버스에서 풀린 직후에는 숨겼다가 돌입하며 켜도 된다
      heat_glow_trail       반투명 플라스마 꼬리 (UNLIT, 단면 컬링)
길이 3.6 m (발광 제외), 지름 0.3 m.

npm run model -- art/blender/space/kinetic_warhead.py
npm run shot -- space/kinetic_warhead.glb --views side,34,front,back
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import space_kit as sk  # noqa: E402
from space_kit import Hull, st  # noqa: E402
from mathutils import Matrix  # noqa: E402

cb.reset()
PI = math.pi
LINE = "#26242a"
M = sk.M
R = 0.15

root = cb.empty("kinetic_warhead", size=0.5)
rod = Hull([st(-1.9, 0.0, 0.0, 0.0, n=2.0), st(-1.2, R * 0.92, R * 0.92, R * 0.92, n=2.0),
            st(-1.0, R, R, R, n=2.0), st(1.45, R, R, R, n=2.0), st(1.7, R * 0.8, R * 0.8, R * 0.8, n=2.0)],
           ring=14, sub=1)
body = [rod.mesh("rod", "m_gray"),
        rod.mesh("tip", "m_black", grow=0.006, s_range=(-1.9, -1.15))]
fin = [(1.0, R - 0.01), (1.7, R - 0.01), (1.72, R + 0.26), (1.45, R + 0.28)]
for k in range(4):
    f = hw.side(f"fin{k}", fin, 0.025, mat=M("m_black"))
    body.append(sk.place(f, (0, 0, 0), basis=Matrix.Rotation(math.radians(45 + 90 * k), 4, "Y")))
fine = [rod.patch("band0", 0.2, 0.36, 0, 2 * PI, "m_yellow", lift=0.004, ns=1, nt=14),
        rod.patch("band1", 1.15, 1.3, 0, 2 * PI, "m_black", lift=0.004, ns=1, nt=14)]
sk.vc_join(body, "kinetic_warhead_body", "body", line=LINE, parent=root)
sk.vc_join(fine, "kinetic_warhead_fine", "fine", line=LINE, parent=root)

# 재진입 열 발광: 촉을 덮는 흰 심 + 주황 겉, 뒤로 끌리는 반투명 플라스마
glow = [hw.ycyl("heat_core", R * 1.35, -1.25, -2.05, r2=0.02, verts=12, mat=M("flame_core"), cap=False),
        hw.ycyl("heat_skin", R * 1.55, -1.05, -2.15, r2=0.04, verts=14, mat=M("flame"), cap=True)]
g = sk.vc_join(glow, "heat_glow", "glow", line=LINE)
sk.set_origin(g, (0, -1.9, 0))
trail = sk.vc_join([hw.ycyl("trail", R * 1.9, -1.0, -0.2, r2=R * 1.25, verts=14, mat=M("flame_haze"), cap=False),
                    hw.ycyl("wake", R * 1.6, 1.75, 6.5, r2=R * 0.2, verts=14, mat=M("flame_haze"), cap=False)],
                   "heat_glow_trail", "plume", line=LINE)
sk.set_origin(trail, (0, -1.9, 0))
sk._parent_keep(trail, g)
sk._parent_keep(g, root)

sk.purge_materials()
tris = cb.tri_count()
print(f"[sk] kinetic_warhead tris {tris} / 1500")
assert tris <= 1500, tris
cb.export("space/kinetic_warhead.glb", props={"outline": 0.008, "collider": 0, "lengthM": 3.6}, root=root)
