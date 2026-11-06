"""엘피니아 원정함대 호위함 '송곳'.

[원작] 엘프 원정함대(함대 규모 묘사만 있고 함선 그림은 없음).
[오리지널] 함대 수를 채우는 가벼운 호위함. 기함과 같은 계보지만 날렵하다.
  - 송곳처럼 뾰족한 함수 + 금색 깃 고리를 두른 충각 가시
  - 작은 헬멧 함교 돔, 쌍열 포탑 1기, 엘프 귀 지느러미(작게, 뒤로 더 젖힘)
  - 함미 추진기 2기(금색 테), 둥근 창 줄 1열, 남색 원판 + 금테 + 원작 엘프 로고
여러 척을 한 장면에 놓으므로 삼각형 4k 안팎으로 가볍게 만든다.

함수 -Y, 좌현 +X, 위 +Z. 길이 약 36 m, 폭 약 30 m (귀 지느러미 포함).

npm run model -- art/blender/space/elfinia_cruiser.py
npm run shot -- space/elfinia_cruiser.glb --views front,34,side,top
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
S = sk.Ship("elfinia_cruiser")
PI = math.pi

# ================================================================== 선체 (뾰족한 함수, 통통한 허리)
hull = Hull([
    st(-16.0, 0.0, 0.0, 0.0, vc=-0.2, n=2.2),
    st(-15.0, 1.1, 1.0, 0.8, vc=-0.2, n=2.2),
    st(-12.0, 2.7, 2.5, 1.9, vc=0.0, n=2.4),
    st(-7.0, 4.0, 3.6, 2.7, vc=0.2, n=2.7),
    st(0.0, 4.5, 3.9, 3.0, vc=0.3, n=2.9),
    st(7.0, 4.0, 3.4, 2.8, vc=0.2, n=3.0),
    st(12.0, 3.2, 2.7, 2.3, vc=0.1, n=3.0),
], ring=28, sub=2)
S.s(hull.mesh("hull", "hull"))
S.f(hull.patch("belly", -14.5, 12.0, PI + 0.15, 2 * PI - 0.15, "hull_d", lift=0.05, nt=6))
# 등 줄 (남색 안장): 호위함은 윗면에 남색 띠를 둘러 기함과 구분
S.f(hull.patch("saddle", -9.5, 9.0, PI / 2 - 0.32, PI / 2 + 0.32, "navy", lift=0.06, nt=4))
S.s(hull.mesh("band", "navy", grow=0.1, s_range=(-10.4, -9.6)))
skirt = Hull([st(11.6, 3.3, 2.8, 2.4, vc=0.1, n=3.0), st(13.4, 3.0, 2.5, 2.2, vc=0.1, n=3.0)], ring=28, sub=1)
S.s(skirt.mesh("skirt", "metal"))

# 충각 가시 + 금색 깃 고리
S.s(hw.ycyl("ram", 0.55, -19.5, -15.2, z=-0.2, r2=0.0, verts=12, mat=sk.M("metal")))
S.s(hw.ycyl("ram_root", 0.75, -16.2, -15.0, z=-0.2, verts=12, mat=sk.M("metal")))
S.s(sk.ring_y("ram_collar", 0.78, 0.16, -16.3, z=-0.2, seg=16, rseg=6))

# ================================================================== 작은 헬멧 함교
TY = -2.0
tower = Hull([
    st(2.8, 2.2, 2.3, 2.6, vc=TY, n=2.7),
    st(4.8, 2.3, 2.4, 2.8, vc=TY, n=2.7),
    st(5.9, 1.9, 2.0, 2.3, vc=TY, n=2.5),
    st(6.6, 1.1, 1.2, 1.3, vc=TY, n=2.3),
    st(6.9, 0.0, 0.0, 0.0, vc=TY, n=2.2),
], axis="Z", ring=20, sub=1)
S.s(tower.mesh("tower", "metal"))
S.s(hw.torus("brim", 2.45, 0.2, (0, TY - 0.15, 5.2), ry=2.95, seg=20, rseg=5, mat=sk.M("navy")))
for i in range(5):
    t = PI + 0.7 + (PI - 1.4) * i / 4
    S.g(tower.decal(f"bridge_win{i}", hw.stadium(0.5, 0.34, 3, angle=90), 4.55, t, "warm", lift=0.04))
S.s(hw.zcyl("mast", 0.1, 6.6, 9.0, y=TY + 0.4, verts=6, mat=sk.M("gear")))
S.g(cb.sphere("mast_light", radius=0.16, loc=(0, TY + 0.4, 9.1), segments=6, rings=4, material=sk.M("glow")))

# ================================================================== 귀 지느러미
for side in (1, -1):
    fh = sk.fin("ear", 0.0, 8.0, 11.5, sweep=6.0, rise=4.2, thick=0.55, ring=14, sub=1)
    fh.O = Vector((side * 3.3, 2.0, 1.4))
    fh.A = Vector((side, 0, 0))
    S.s(fh.mesh(f"ear{side}", "hull_l"))
    S.s(fh.mesh(f"ear_tip{side}", "navy_l", grow=0.02, s_range=(8.6, 11.5)))
    S.g(cb.sphere(f"ear_light{side}", radius=0.22, loc=fh.point(11.35, 0.0) + Vector((side * 0.1, 0, 0)),
                  segments=6, rings=4, material=sk.M("nav_r" if side > 0 else "nav_g")))

# ================================================================== 추진기 2기
for x in (1.55, -1.55):
    sk.engine(S, f"eng{x:+.0f}", x, 0.2, 13.0, 1.2, length=1.2, plume=2.3, seg=18, gold="lip")

# ================================================================== 포탑 · 엠블럼 · 창
sk.turret(S, "t_fwd", 0, -8.0, 3.15, k=0.62)
for side in (1, -1):
    t = hull.t_at(-4.0, 0.6, side)
    P, Ts, Tt, N = hull.frame(-4.0, t)
    sk.emblem_plate(S, f"emblem{side}", P, N, 1.45, up=(0, 0, 1), depth=0.3, n=16, tolerance=0.006)
    sk.window_row(S, hull, f"win{side}", 0.5, 9.5, 0.9, side=side, r=0.22, pitch=1.15, lift=0.05)
    S.f(hull.decal(f"hatch{side}", hw.rrect(1.4, 0.8, 0.25, 2), -9.0, hull.t_at(-9.0, 1.2, side), "hull_d",
                   lift=0.05))
for i, s in enumerate((-6.5, 3.5)):
    S.f(hull.patch(f"seam{i}", s - 0.05, s + 0.05, -0.2, PI + 0.2, "seam", lift=0.05, ns=1, nt=10))

S.anchor("anchor_bridge", (0, TY - 2.8, 4.6))
S.anchor("anchor_engines", (0, 14.5, 0.2))

S.finish("space/elfinia_cruiser.glb", outline=0.07, budget=5000,
         extra={"shipClass": "cruiser", "lengthM": 36})
