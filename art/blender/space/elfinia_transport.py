"""엘피니아 원정함대 병력 수송함 '공구함' (함번 03).

[원작] 헤일리는 정찰 침투조를 보내지 않고 착륙부터 시켰다(힐데의 대사).
[오리지널] 선봉대 병력을 실어 나르는 수송함. 함대 구성용이다 (리타의 정찰 침투조는 기함에 탄다:
          사용자 확정 2026-11-01). 끝내 떨어지지 않은 강하 포드가 '정찰 없이 착륙'을 말없이 보여 준다.
  - 공구함처럼 각진 둥근 상자 선체(초타원 n=4.5, 평평한 배)와 등 위의 큰 D자 손잡이(통신 아치)
  - 앞쪽 작은 헬멧 함교 돔 (함대 공통)
  - 양 옆 침투 강하 포드 걸이 5개씩: 끝내 한 번도 떨어지지 않는다
  - 병력 구획: 옆면 둥근 사각 창 2열 (위 = 숙소·대기실, 아래 = 사격장·훈련 구획)
  - 옆 승강구(경고 노랑 테), 함미 강하 램프와 네 모서리 추진기, 작은 엘프 귀 지느러미
  - 남색 원판 + 금테 + 원작 엘프 로고 엠블럼, 함번 '03'

함수 -Y, 좌현 +X, 위 +Z. 길이 약 44 m, 폭 약 34 m (귀 포함), 높이 약 23 m (손잡이 포함).

npm run model -- art/blender/space/elfinia_transport.py
npm run shot -- space/elfinia_transport.glb --views front,34,side,top
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
S = sk.Ship("elfinia_transport")
PI = math.pi

# ================================================================== 상자형 선체
hull = Hull([
    st(-21.0, 0.0, 0.0, 0.0, vc=-0.6, n=2.4),
    st(-20.4, 3.8, 3.9, 3.2, vc=-0.5, n=2.6),
    st(-18.8, 6.2, 5.8, 4.8, vc=-0.3, n=3.2, nb=3.6),
    st(-15.5, 7.8, 6.9, 5.7, vc=-0.1, n=4.0, nb=4.6),
    st(-11.0, 8.3, 7.3, 6.0, vc=0.0, n=4.5, nb=5.0),
    st(10.0, 8.3, 7.3, 6.0, vc=0.0, n=4.5, nb=5.0),
    st(15.0, 7.7, 6.8, 5.6, vc=0.0, n=4.3, nb=4.8),
    st(19.0, 7.1, 6.2, 5.3, vc=0.0, n=4.0, nb=4.6),
], ring=32, sub=2)
S.s(hull.mesh("hull", "hull"))
S.f(hull.patch("belly", -20.0, 19.0, PI + 0.22, 2 * PI - 0.22, "hull_d", lift=0.07, nt=8))
# 윗면 덮개 판 (밝은 회녹) + 남색 띠
S.f(hull.patch("lid", -16.5, 17.5, 0.62, PI - 0.62, "hull_l", lift=0.07, nt=6))
for i, (a, b) in enumerate(((-13.6, -12.4), (12.0, 13.2))):
    S.s(hull.mesh(f"band{i}", "navy", grow=0.14, s_range=(a, b)))
# 앞 범퍼 띠 + 전조등 2개 (앞에서 볼 때 얼굴)
S.f(hull.patch("bumper", -20.2, -19.4, PI + 0.5, 2 * PI - 0.5, "navy", lift=0.14, ns=3, nt=16))
for sx in (1, -1):
    P, R, U, N = hull.oriented(-20.25, -PI / 2 + sx * 0.62)
    S.g(hw.decal(f"headlight{sx}", hw.circle(0.55, 10), P, right=R, up=U, lift=0.14, mat=sk.M("warm")))
skirt = Hull([st(18.6, 7.2, 6.3, 5.4, vc=0.0, n=4.0, nb=4.6), st(21.0, 6.8, 5.9, 5.1, vc=0.0, n=4.0, nb=4.6)],
             ring=32, sub=1)
S.s(skirt.mesh("skirt", "metal"))

# ================================================================== 작은 헬멧 함교 (앞쪽 위)
TY = -12.8
tower = Hull([
    st(6.2, 3.6, 3.7, 4.2, vc=TY, n=2.8),
    st(8.8, 3.7, 3.8, 4.4, vc=TY, n=2.8),
    st(10.2, 3.2, 3.3, 3.8, vc=TY, n=2.5),
    st(11.1, 1.9, 2.0, 2.2, vc=TY, n=2.3),
    st(11.5, 0.0, 0.0, 0.0, vc=TY, n=2.2),
], axis="Z", ring=24, sub=1)
S.s(tower.mesh("tower", "metal"))
S.s(hw.torus("brim", 3.9, 0.3, (0, TY - 0.2, 9.3), ry=4.5, seg=24, rseg=5, mat=sk.M("navy")))
for i in range(7):
    t = PI + 0.6 + (PI - 1.2) * i / 6
    S.g(tower.decal(f"bridge_win{i}", hw.stadium(0.75, 0.48, 3, angle=90), 8.45, t, "warm", lift=0.05))

# ================================================================== 공구함 손잡이 (D자 통신 아치)
HY = 0.0
arch = []
for i in range(17):
    a = PI * i / 16
    x = 6.2 * math.cos(a)
    z = 6.4 + 6.4 * math.sin(a) ** 0.8
    arch.append((x, HY, z))
sec = hw.rrect(0.9, 1.5, 0.35, 2)          # (u = 진행 옆(y), v = 두께)
S.s(hw.sweep("handle", arch, [(v, u) for u, v in sec], side_vec=(0, 1, 0), mat=sk.M("metal")))
for sx in (1, -1):
    S.s(hw.zcyl(f"handle_foot{sx}", 1.15, 5.6, 7.2, x=sx * 6.2, y=HY, verts=14, mat=sk.M("metal")))
    S.s(hw.torus(f"handle_ring{sx}", 1.15, 0.16, (sx * 6.2, HY, 7.2), seg=14, rseg=5, mat=sk.M("gold")))
S.s(hw.zcyl("antenna", 0.12, 12.6, 16.2, y=HY, verts=6, mat=sk.M("gear")))
S.s(cb.box("antenna_yard", size=(2.4, 0.18, 0.18), loc=(0, HY, 14.9), material=sk.M("gear")))
S.g(cb.sphere("antenna_light", radius=0.2, loc=(0, HY, 16.3), segments=6, rings=4, material=sk.M("glow")))
S.s(cb.sphere("radome", radius=0.9, loc=(0, HY, 12.7), segments=10, rings=5, material=sk.M("steel")))

# ================================================================== 침투 강하 포드 걸이 (양 옆 6개씩)
POD_Y = [-8.6, -4.3, 0.0, 4.3, 8.6]
for side in (1, -1):
    x0 = side * 8.95
    rail = Hull([st(-11.0, 0.45, 0.35, 0.35, vc=3.3, n=4.0, uc=side * 8.2),
                 st(11.0, 0.45, 0.35, 0.35, vc=3.3, n=4.0, uc=side * 8.2)], ring=8, sub=1)
    S.s(rail.mesh(f"pod_rail{side}", "metal"))
    for k, y in enumerate(POD_Y):
        pod = Hull([
            st(y - 1.9, 0.0, 0.0, 0.0, vc=2.2, n=2.2, uc=x0),
            st(y - 1.2, 0.85, 0.85, 0.85, vc=2.2, n=2.3, uc=x0),
            st(y + 1.5, 0.95, 0.95, 0.95, vc=2.2, n=2.4, uc=x0),
        ], ring=10, sub=1)
        S.s(pod.mesh(f"pod{side}_{k}", "hull_l"))
        S.f(pod.patch(f"pod_nose{side}_{k}", y - 1.75, y - 0.9, 0, 2 * PI, "navy_l", lift=0.03, ns=1, nt=10))
        S.s(hw.tube(f"pod_ring{side}_{k}", 1.02, 0.6, y + 1.45, y + 1.85, c=(x0, 2.2), verts=10, mat=sk.M("gold")))
        S.s(cb.box(f"pod_clamp{side}_{k}", size=(0.9, 0.5, 1.4), loc=(side * 8.45, y, 2.95), material=sk.M("dark")))

# ================================================================== 병력 구획 창 2열, 승강구, 엠블럼, 함번
for side in (1, -1):
    for row, (v, s0, s1) in enumerate(((-0.4, -10.0, 10.5), (-2.9, -9.5, 10.0))):
        count = 10 if row == 0 else 9
        for k in range(count):
            y = s0 + (s1 - s0) * k / (count - 1)
            if row == 1 and abs(y + 0.5) < 2.0:
                continue                      # 승강구 자리
            t = hull.t_at(y, v, side)
            S.f(hull.decal(f"win_fr{side}{row}{k}", hw.rrect(1.35, 1.0, 0.35, 2), y, t, "navy", lift=0.06))
            S.g(hull.decal(f"win{side}{row}{k}", hw.rrect(1.0, 0.68, 0.25, 2), y, t, "glow", lift=0.1))
    # 옆 승강구: 둥근 사각 문 + 경고 노랑 테
    t = hull.t_at(-0.5, -2.6, side)
    S.f(hull.decal(f"door_rim{side}", hw.rrect(3.4, 4.0, 0.7, 3), -0.5, t, "hazard", lift=0.06))
    S.f(hull.decal(f"door{side}", hw.rrect(2.8, 3.4, 0.5, 3), -0.5, t, "hull_d", lift=0.1))
    S.g(hull.decal(f"door_led{side}", hw.circle(0.16, 6), -2.6, hull.t_at(-2.6, -0.9, side), "glow", lift=0.12))
    # 엠블럼
    t = hull.t_at(-15.4, 0.8, side)
    P, Ts, Tt, N = hull.frame(-15.4, t)
    sk.emblem_plate(S, f"emblem{side}", P, N, 2.3, up=(0, 0, 1), depth=0.4, n=20)
    # 함번 03 (손잡이 뒤 옆면)
    P, R, U, N = hull.oriented(15.3, hull.t_at(15.3, 0.4, side))
    S.f(hw.text(f"hull_no{side}", "03", 2.6, P + N * 0.08, right=R, up=U, mat=sk.M("paper")))
# 윗면 함번
P, R, U, N = hull.oriented(-6.5, PI / 2, up=(0, -1, 0))
S.f(hw.text("hull_no_top", "03", 4.6, P + N * 0.1, right=R, up=U, mat=sk.M("paper")))
for i, s in enumerate((-6.4, 6.4)):
    S.f(hull.patch(f"seam{i}", s - 0.07, s + 0.07, -0.55, PI + 0.55, "seam", lift=0.07, ns=1, nt=14))

# ================================================================== 함미: 강하 램프 + 네 모서리 추진기
ramp = hw.rrect(5.6, 6.4, 0.9, 3, cy=-0.4)
S.f(hw.decal("ramp_rim", hw.rrect(6.4, 7.2, 1.2, 3, cy=-0.4), (0, 21.04, 0), right=(-1, 0, 0), up=(0, 0, 1),
             lift=0.0, mat=sk.M("hazard")))
S.f(hw.decal("ramp", ramp, (0, 21.10, 0), right=(-1, 0, 0), up=(0, 0, 1), lift=0.0, mat=sk.M("hull_d")))
for k in range(3):
    S.f(hw.decal(f"ramp_rib{k}", hw.rrect(4.6, 0.22, 0.1, 1, cy=1.6 - k * 2.0), (0, 21.16, 0), right=(-1, 0, 0),
                 up=(0, 0, 1), lift=0.0, mat=sk.M("seam")))
for x, z in ((4.7, 3.1), (-4.7, 3.1), (4.7, -2.8), (-4.7, -2.8)):
    sk.engine(S, f"eng{x:+.0f}{z:+.0f}", x, z, 20.7, 1.35, length=1.3, plume=2.3, seg=16, gold="lip")

# ================================================================== 작은 귀 지느러미
for side in (1, -1):
    fh = sk.fin("ear", 0.0, 9.5, 10.5, sweep=5.0, rise=4.0, thick=0.6, ring=14, sub=1)
    fh.O = Vector((side * 7.0, 11.5, 3.8))
    fh.A = Vector((side, 0, 0))
    S.s(fh.mesh(f"ear{side}", "hull_l"))
    S.s(fh.mesh(f"ear_tip{side}", "navy_l", grow=0.02, s_range=(7.8, 10.5)))
    S.g(cb.sphere(f"ear_light{side}", radius=0.24, loc=fh.point(10.35, 0.0) + Vector((side * 0.1, 0, 0)),
                  segments=6, rings=4, material=sk.M("nav_r" if side > 0 else "nav_g")))

S.anchor("anchor_bridge", (0, TY - 4.0, 7.8))
S.anchor("anchor_troop_deck", (0, 0.0, -1.8))
S.anchor("anchor_engines", (0, 23.0, 0.0))

S.finish("space/elfinia_transport.glb", outline=0.09, budget=9500,
         extra={"shipClass": "transport", "lengthM": 44, "hullNo": "03"})
