"""엘피니아 탐사선 '돋보기'.

[원작] 헤일리는 망원 카메라로 지구를 살펴보고 인간들이 평화로워 보인다고 판단했다(헤일리(멀쩡)의 대사).
[오리지널] 함대보다 먼저 지구 가까이 나가 망원 카메라로 지구를 관측하는 무인 탐사선. 오프닝 2의 주인공.
  - 둥근 상자 몸통 + 앞으로 길게 뻗은 망원 경통(금색 후드 고리 2개, 시안 렌즈)
  - 등 위 접시 안테나, 옆 센서 꼬투리 줄(시안 끝), 아래 보조 렌즈
  - 엘프 귀 모양 광자 전지판 2장 (남색 판 + 시안 전지 줄): 함대 공통 귀 지느러미 문법
  - 함미 작은 추진기와 자세 제어 노즐, 남색 원판 + 금테 + 원작 엘프 로고

경통(망원 카메라)은 -Y를 본다. 장면에서는 경통을 북미에 맞춘다.
길이 약 7 m, 폭 약 10 m (전지판 포함).

npm run model -- art/blender/space/elfinia_probe.py
npm run shot -- space/elfinia_probe.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import space_kit as sk  # noqa: E402
from space_kit import Hull, st  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
S = sk.Ship("elfinia_probe")
PI = math.pi

# ================================================================== 몸통 (둥근 상자)
body = Hull([
    st(-1.5, 1.0, 0.95, 0.85, vc=0.0, n=3.0),
    st(-1.2, 1.25, 1.2, 1.05, vc=0.0, n=3.6),
    st(1.2, 1.25, 1.2, 1.05, vc=0.0, n=3.8),
    st(1.7, 1.05, 1.0, 0.9, vc=0.0, n=3.4),
    st(2.0, 0.0, 0.0, 0.0, vc=0.0, n=2.6),
], ring=24, sub=2)
S.s(body.mesh("body", "hull"))
S.s(body.mesh("body_band", "navy", grow=0.04, s_range=(0.35, 0.75)))
S.f(body.patch("belly", -1.3, 1.6, PI + 0.4, 2 * PI - 0.4, "hull_d", lift=0.012, nt=6))

# ================================================================== 망원 경통 (망원 카메라)
TZ = 0.25
S.s(hw.tube("scope", 0.82, 0.7, -1.3, -4.6, c=(0, TZ), verts=28, mat=sk.M("metal")))
S.s(hw.ycyl("scope_back", 0.9, -1.8, -1.2, z=TZ, verts=28, mat=sk.M("metal")))
S.s(hw.tube("scope_sleeve", 0.88, 0.75, -2.4, -3.3, c=(0, TZ), verts=28, mat=sk.M("hull_l")))
S.s(hw.tube("hood", 0.9, 0.78, -4.6, -5.6, c=(0, TZ), verts=28, r_out2=1.08, r_in2=0.98, mat=sk.M("hull_l")))
S.s(sk.ring_y("hood_ring", 1.08, 0.08, -5.6, z=TZ, seg=28, rseg=6))
S.s(sk.ring_y("scope_ring", 0.86, 0.07, -4.6, z=TZ, seg=28, rseg=6))
S.s(hw.ycyl("lens_cell", 0.72, -4.0, -3.9, z=TZ, verts=24, mat=sk.M("dark")))
S.g(sk.disc("lens", 0.6, (0, -4.02, TZ), (0, -1, 0), "glow", n=24))
S.g(sk.disc("lens_hl", 0.18, (0.22, -4.04, TZ + 0.24), (0, -1, 0), "core", n=10))
S.f(sk.annulus("lens_ring", 0.6, 0.48, (0, -4.03, TZ), (0, -1, 0), "lens", n=24))
# 경통 위 초점 손잡이·보조 망원경
S.s(hw.ycyl("finder", 0.2, -3.0, -1.6, x=0.0, z=TZ + 1.0, verts=10, mat=sk.M("metal")))
S.s(cb.box("finder_mount", size=(0.18, 0.5, 0.22), loc=(0, -2.3, TZ + 0.86), material=sk.M("gear")))
S.s(sk.ring_y("finder_ring", 0.21, 0.035, -3.0, z=TZ + 1.0, seg=10, rseg=4))
S.g(sk.disc("finder_lens", 0.15, (0, -3.01, TZ + 1.0), (0, -1, 0), "glow", n=8))

# ================================================================== 접시 안테나 (등 위, 앞으로 기움)
dish_c = Vector((0.0, 0.7, 1.95))
S.s(hw.zcyl("dish_post", 0.09, 1.0, 1.8, y=0.7, verts=8, mat=sk.M("gear")))
dish = cb.cylinder("dish", radius=0.85, radius2=0.18, depth=0.32, verts=20, cap=True, material=sk.M("steel"))
sk.place(dish, dish_c, rot=(-40, 0, 0))
S.s(dish)
S.s(sk.place(hw.zcyl("dish_feed", 0.035, 0.0, 0.55, verts=6, mat=sk.M("gear")), dish_c, rot=(-40, 0, 0)))
S.g(sk.place(cb.sphere("dish_tip", radius=0.07, segments=6, rings=4, material=sk.M("glow")),
             dish_c + Vector((0, -0.55 * math.sin(math.radians(40)), 0.55 * math.cos(math.radians(40))))))

# ================================================================== 옆 센서 꼬투리 줄 (센서 배열)
for side in (1, -1):
    for k in range(3):
        y = -0.8 + k * 0.62
        z = 0.55
        S.s(hw.ycyl(f"sensor{side}{k}", 0.13, y - 0.25, y + 0.25, x=side * 1.38, z=z, verts=8, mat=sk.M("metal")))
        S.g(sk.disc(f"sensor_tip{side}{k}", 0.1, (side * 1.38, y - 0.26, z), (0, -1, 0), "glow", n=8))
    t = body.t_at(0.0, -0.35, side)
    P, Ts, Tt, N = body.frame(0.0, t)
    sk.emblem_plate(S, f"emblem{side}", P, N, 0.42, up=(0, 0, 1), depth=0.06, n=16, tolerance=0.006)
# 아래 보조 렌즈 (광각 카메라)
S.s(hw.zcyl("cam_mount", 0.3, -1.25, -0.9, y=-0.4, verts=12, mat=sk.M("metal")))
S.g(sk.disc("cam_lens", 0.2, (0, -0.4, -1.26), (0, 0, -1), "glow", n=10))

# ================================================================== 귀 모양 광자 전지판
for side in (1, -1):
    fh = sk.fin("panel", 0.4, 2.6, 4.6, sweep=1.4, rise=0.9, thick=0.07, ring=10, sub=1)
    fh.O = Vector((side * 1.0, 0.0, 0.1))
    fh.A = Vector((side, 0, 0))
    S.s(fh.mesh(f"panel{side}", "navy"))
    S.s(fh.mesh(f"panel_root{side}", "gold", grow=0.03, s_range=(0.3, 0.55)))
    for k, a in enumerate((0.25, 0.45, 0.65)):
        s = 4.6 * a
        w = fh.sec(s)["w"] * 0.8
        P, R, U, N = fh.oriented(s, PI / 2, up=(0, -1, 0))
        S.g(hw.decal(f"cell{side}{k}", hw.rrect(0.05, 2 * w, 0.02, 1), P, right=R, up=U, lift=0.03,
                     mat=sk.M("glow")))
    S.g(cb.sphere(f"panel_light{side}", radius=0.07, loc=fh.point(4.55, 0.0) + Vector((side * 0.04, 0, 0)),
                  segments=6, rings=4, material=sk.M("nav_r" if side > 0 else "nav_g")))

# ================================================================== 추진기 + 자세 제어 노즐 + 안테나
sk.engine(S, "main", 0, -0.1, 1.9, 0.42, length=0.4, plume=2.2, seg=16, gold="lip")
for sx, sz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
    S.s(hw.ycyl(f"rcs{sx}{sz}", 0.09, 1.05, 1.35, x=sx * 1.18, z=sz * 0.95, verts=6, r2=0.13, mat=sk.M("dark")))
S.s(hw.zcyl("whip", 0.03, 0.9, 2.6, x=-0.7, y=1.2, verts=5, mat=sk.M("gear")))
S.g(cb.sphere("whip_tip", radius=0.06, loc=(-0.7, 1.2, 2.65), segments=6, rings=4, material=sk.M("nav_r")))
for side, t in ((1, 0.0), (-1, PI)):
    P, R, U, N = body.oriented(1.0, t)
    S.f(hw.text(f"code{side}", "관측-1", 0.26, P + N * 0.02 + Vector((0, 0, 0.55)), right=R, up=U,
                mat=sk.M("paper")))

S.anchor("anchor_lens", (0, -5.6, TZ))
S.anchor("anchor_dish", tuple(dish_c))

S.finish("space/elfinia_probe.glb", outline=0.025, budget=5000,
         extra={"shipClass": "probe", "lengthM": 7.6})
