"""엘피니아 원정함대 기함 「큰망치」 (선봉대 지휘관 헤일리의 기함, 함번 01).

[원작] 엘프 원정함대가 지구로 왔고, 헤일리가 함대의 모습을 드러내 통신한 뒤 함선을 지구에 착륙시켰다.
      헤일리는 함선 설계를 잘 알고 조타 실력이 뛰어나다. 함선 모습은 원작에 그림이 없다.
      엘레나 테마극장: 함대는 "날아다니던 중 미사일을 맞았다".
[오리지널] 이름은 대본(docs/script/prologue.md)의 「큰망치」(Sledgehammer). 공구 이름 명명 규칙.
      리타와 캐시의 정찰 침투조가 이 배의 병력 구획 B에 타고 있다 (사용자 확정 2026-11-01).
      프롤로그 함내 레벨(art/blender/levels/prologue_ship.py)이 이 배의 안이다.
      엔딩에서 지구의 ICBM이 푼 운동에너지 탄두가 함교 돔을 직격한다. 함교는 크게 부서지지만 완파되지 않는다.
형태
  - 통통한 고래형 선체(초타원 로프트). 길이:폭 ≈ 2.6:1로 짧고 둥글다 (SD 비율)
  - 함수에서 튀어나온 광자포와 앞으로 벌어진 금색 포구 고리 (칸나 대포·7식 소총의 금색 총구 고리 문법)
  - 엘피니아 헬멧을 닮은 함교 돔: 둥근 돔 + 테두리 챙, 챙 아래 따뜻한 함교 창 띠
  - 옆으로 뻗고 위로 들린 엘프 귀 지느러미(함대 공통), 귀 뿌리 뒤 보조 추진기
  - 함미 주추진기 3기(금테), 둥근 창 줄(병력 구획), 남색 원판 + 금테 + 원작 엘프 로고 엠블럼
노드
  elfinia_flagship_body/_fine/_glow/_plume   선체 (정적)
  bridge            함교 블록 (돔, 챙, 창, 함번, 돛대)
  bridge_damaged    피격 뒤 함교 (hidden=1: 엔진이 처음에 숨김). 함몰·찢긴 구멍·불씨·말려 나온 장갑판,
                    떨어져 나간 챙, 꺾인 돛대, 깨져 꺼진 창 + 붉은 비상등. 피격 순간 bridge를 숨기고 이것을 켠다
  anchor_bridge_hit 직격 지점 (돔 앞면, 지구 쪽)

함수 -Y, 좌현 +X, 위 +Z. 길이 약 72 m (포구 포함), 폭 약 80 m (귀 지느러미 포함).

npm run model -- art/blender/space/elfinia_flagship.py
npm run shot -- space/elfinia_flagship.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import space_kit as sk  # noqa: E402
from space_kit import Hull, st  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()
S = sk.Ship("elfinia_flagship")
PI = math.pi

# ================================================================== 주선체 (통통한 고래형)
hull = Hull([
    st(-34.0, 0.0, 0.0, 0.0, vc=0.0, n=2.2),
    st(-33.2, 5.0, 4.6, 3.8, vc=0.2, n=2.3),
    st(-31.0, 9.0, 8.6, 6.6, vc=0.6, n=2.5),
    st(-26.0, 12.0, 11.4, 8.4, vc=1.0, n=2.6),
    st(-17.0, 13.2, 12.4, 9.0, vc=1.2, n=2.8, nb=2.7),
    st(-6.0, 12.8, 11.6, 8.6, vc=1.0, n=2.9, nb=2.8),
    st(8.0, 11.0, 9.4, 7.4, vc=0.7, n=3.0, nb=2.9),
    st(20.0, 8.4, 7.0, 5.8, vc=0.4, n=3.0),
    st(28.0, 6.6, 5.4, 4.6, vc=0.3, n=3.0),
], ring=40, sub=2)
S.s(hull.mesh("hull", "hull"))
# 아랫배 판 (회녹 그림자)
S.f(hull.patch("belly", -32.2, 28.0, PI + 0.12, 2 * PI - 0.12, "hull_d", lift=0.1, nt=8))
for i, t in enumerate((-0.12, PI + 0.12)):
    S.f(hull.patch(f"waterline{i}", -32.5, 28.0, t - 0.025, t + 0.025, "navy", lift=0.12, nt=1))
# 함미 엔진 받침 (건메탈 치마)
skirt = Hull([st(27.4, 6.8, 5.6, 4.8, vc=0.3, n=3.1), st(30.4, 6.3, 5.1, 4.4, vc=0.3, n=3.1)], ring=40, sub=1)
S.s(skirt.mesh("skirt", "metal"))
# 남색 띠 (함수 뒤, 함미 앞): 살짝 부푼 짧은 로프트 = 아웃라인이 생기는 진짜 띠
for i, (a, b) in enumerate(((-28.4, -26.4), (19.6, 21.2))):
    S.s(hull.mesh(f"band{i}", "navy", grow=0.2, s_range=(a, b)))

# ================================================================== 함수 광자포 + 금색 포구 고리
BZ = 0.0
S.s(hw.ycyl("lance", 2.4, -40.0, -33.0, z=BZ, verts=24, mat=sk.M("metal")))
S.s(hw.ycyl("lance_sleeve", 2.65, -37.6, -35.8, z=BZ, verts=24, mat=sk.M("navy")))
S.s(hw.tube("muzzle_flare", 2.8, 2.0, -40.0, -42.6, c=(0, BZ), verts=32, r_out2=4.0, r_in2=3.2, mat=sk.M("gold")))
S.s(sk.ring_y("muzzle_ring", 3.95, 0.34, -42.6, z=BZ, seg=28, rseg=6))
S.s(hw.ycyl("muzzle_throat", 3.0, -41.0, -40.6, z=BZ, verts=24, mat=sk.M("dark")))
S.g(sk.disc("muzzle_glow", 2.5, (0, -41.1, BZ), (0, -1, 0), "glow", n=24))
S.g(sk.disc("muzzle_core", 1.25, (0, -41.25, BZ), (0, -1, 0), "core", n=16))

# ================================================================== 헬멧 함교 돔
TY, TZ0 = -9.0, 9.5
TOWER = [
    st(TZ0, 6.4, 6.6, 7.4, vc=TY, n=2.8),
    st(14.0, 6.6, 6.8, 7.8, vc=TY, n=2.8),
    st(16.6, 6.3, 6.5, 7.4, vc=TY, n=2.7),
    st(19.0, 5.3, 5.5, 6.2, vc=TY, n=2.5),
    st(20.8, 3.4, 3.6, 4.0, vc=TY, n=2.3),
    st(21.6, 0.0, 0.0, 0.0, vc=TY, n=2.2),
]
tower = Hull(TOWER, axis="Z", ring=28, sub=2)
# 직격 지점: 함교 돔 앞면(지구 쪽 -Y), 좌현으로 조금, 챙 바로 위
HIT_S, HIT_T = 17.4, 3 * PI / 2 + 0.38
HIT_P, _, _, HIT_N = tower.frame(HIT_S, HIT_T)


def ragged(r, n=14, seed=0, spike=0.35):
    """찢긴 구멍·그을음 외곽선 (들쭉날쭉한 별 모양)."""
    import random
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * PI * i / n + rnd.uniform(-0.12, 0.12)
        k = 1.0 + (spike if i % 2 == 0 else -spike * 0.5) * rnd.uniform(0.5, 1.0)
        pts.append((r * k * math.cos(a), r * k * math.sin(a) * 0.8))
    return pts


def dent(obj, center, normal, radius, depth):
    """반지름 안의 정점을 법선 반대로 밀어 움푹 꺼진 피탄 자국을 만든다."""
    cb.apply_modifiers(obj)
    mw = obj.matrix_world
    inv = mw.inverted()
    C = Vector(center)
    Nn = Vector(normal).normalized()
    for v in obj.data.vertices:
        w = mw @ v.co
        d = (w - C).length
        if d < radius:
            f = (1 - (d / radius) ** 2) ** 2
            v.co = inv @ (w - Nn * depth * f)
    obj.data.update()
    return obj


def bridge_block(B, damaged=False):
    """헬멧 함교 블록 (돔, 챙, 창, 함번, 돛대). damaged=True면 직격 뒤 모습 (크게 손상, 완파 아님)."""
    th = Hull(TOWER, axis="Z", ring=28 if not damaged else 24, sub=2)
    dome = th.mesh("tower", "metal")
    if damaged:
        dent(dome, HIT_P, HIT_N, 4.2, 1.7)
    B.s(dome)
    B.f(th.patch("vent", 19.2, 21.5, PI / 2 - 0.12, PI / 2 + 0.12, "dark", lift=0.05, ns=4, nt=1))
    B.f(th.patch("vent2", 19.2, 21.5, 3 * PI / 2 - 0.12, 3 * PI / 2 + 0.12, "dark", lift=0.05, ns=4, nt=1))
    # 챙 (손상 시 맞은 쪽 60°가 떨어져 나가고 한 조각이 처져 매달림)
    phi = math.degrees(math.atan2(HIT_P.y - (TY - 0.35), HIT_P.x))
    if not damaged:
        B.s(hw.torus("brim", 6.9, 0.55, (0, TY - 0.35, 16.0), ry=8.1, seg=28, rseg=6, mat=sk.M("navy")))
    else:
        brim = hw.torus("brim", 6.9, 0.55, (0, 0, 0), ry=8.1, seg=24, rseg=6, arc=300.0, mat=sk.M("navy"))
        B.s(sk.place(brim, (0, TY - 0.35, 16.0), rot=(0, 0, phi + 30)))
        piece = hw.torus("brim_piece", 6.9, 0.5, (0, 0, 0), ry=8.1, seg=4, rseg=6, arc=24.0, mat=sk.M("navy"))
        sk.place(piece, (0, 0, 0), rot=(0, 0, phi + 8))
        sk.place(piece, (0, 0, 0), rot=(18, -10, 0))
        B.s(sk.place(piece, (0.6, TY - 0.2, 14.9)))
    # 함교 창 (손상 시 맞은 쪽은 깨져 꺼지고 나머지는 붉은 비상등)
    B.f(th.patch("bridge_band", 14.0, 15.5, PI + 0.35, 2 * PI - 0.35, "navy", lift=0.05, ns=2, nt=14))
    for i in range(9):
        t = PI + 0.55 + (PI - 1.1) * i / 8
        win = th.decal(f"bridge_win{i}", hw.stadium(1.25, 0.8, 3, angle=90), 14.75, t,
                       "warm" if not damaged else ("lens" if abs(t - HIT_T) < 0.75 else "nav_r"), lift=0.08)
        (B.g if (not damaged or abs(t - HIT_T) >= 0.75) else B.f)(win)
    for side, t in ((1, 0.0), (-1, PI)):
        P, R, U, N = th.oriented(12.0, t)
        B.f(hw.text(f"hull_no{side}", "01", 2.4, P + N * 0.06, right=R, up=U, mat=sk.M("paper")))
    # 돛대
    B.s(hw.torus("mast_ring", 1.05, 0.2, (0, TY + 1.2, 22.0), seg=16, rseg=6, mat=sk.M("gold")))
    if not damaged:
        B.s(hw.zcyl("mast", 0.3, 21.0, 28.5, y=TY + 1.2, verts=8, mat=sk.M("gear")))
        B.s(cb.box("yard", size=(6.2, 0.36, 0.36), loc=(0, TY + 1.2, 26.0), material=sk.M("gear")))
        B.g(cb.sphere("mast_light", radius=0.42, loc=(0, TY + 1.2, 28.7), segments=8, rings=6,
                      material=sk.M("glow")))
        for sx in (-1, 1):
            B.g(cb.sphere(f"yard_light{sx}", radius=0.26, loc=(sx * 3.1, TY + 1.2, 26.0), segments=8, rings=4,
                          material=sk.M("nav_r" if sx > 0 else "nav_g")))
    else:
        B.s(hw.zcyl("mast", 0.3, 21.0, 24.6, y=TY + 1.2, verts=8, mat=sk.M("gear")))
        top = [hw.zcyl("mast_top", 0.28, 0.0, 3.6, verts=8, mat=sk.M("gear")),
               cb.box("yard", size=(6.2, 0.36, 0.36), loc=(0, 0, 1.4), rot=(0, 14, 0), material=sk.M("gear"))]
        for o in top:
            sk.place(o, (0, 0, 0), rot=(48, 0, -20))
            B.s(sk.place(o, (0, TY + 1.2, 24.5)))
        tip = Vector((0, TY + 1.2, 24.5)) + (Matrix.Rotation(math.radians(-20), 3, "Z")
                                             @ Matrix.Rotation(math.radians(48), 3, "X")) @ Vector((0, 0, 3.75))
        B.f(cb.sphere("mast_light_dead", radius=0.4, loc=tip, segments=8, rings=6, material=sk.M("lens")))
        # 그을음 · 찢긴 구멍 · 불씨 (표면을 따라 휜 데칼, 같은 함몰을 적용) + 말려 올라간 장갑판
        decs = [(th.conform("scorch", ragged(4.4, 18, 3, 0.45), HIT_S + 0.4, HIT_T, "dark", lift=0.08), B.f),
                (th.conform("soot0", ragged(1.4, 10, 12, 0.5), HIT_S - 2.6, HIT_T + 0.55, "dark", lift=0.08), B.f),
                (th.conform("soot1", ragged(1.1, 10, 13, 0.5), HIT_S + 2.2, HIT_T - 0.5, "dark", lift=0.08), B.f),
                (th.conform("hole", ragged(2.2, 14, 5, 0.4), HIT_S, HIT_T, "lens", lift=0.16), B.f),
                (th.conform("ember", ragged(1.45, 12, 7, 0.5), HIT_S, HIT_T, "flame", lift=0.24), B.g),
                (th.conform("ember_core", ragged(0.7, 10, 9, 0.4), HIT_S, HIT_T, "flame_core", lift=0.3), B.g)]
        for o, add in decs:
            dent(o, HIT_P, HIT_N, 4.2, 1.7)
            add(o)
        U0 = Vector((0, 0, 1))
        R0 = U0.cross(HIT_N).normalized()
        U0 = HIT_N.cross(R0).normalized()
        P = HIT_P - HIT_N * 1.1
        for k in range(6):
            a = 2 * PI * k / 6 + 0.3
            radial = (R0 * math.cos(a) + U0 * math.sin(a)).normalized()
            base = P + radial * 2.3
            plate = cb.box(f"petal{k}", size=(1.3, 0.14, 1.8), material=sk.M("metal"))
            # 판의 긴 변(Z)이 바깥·위로 말려 나오게
            Bm = sk.basis_from(radial.cross(HIT_N).normalized(), (radial * 0.6 + HIT_N).normalized())
            plate.matrix_world = Bm
            B.s(sk.place(plate, base + (radial * 0.6 + HIT_N).normalized() * 0.6))
    return B


bridge_block(S.part("bridge"))
bridge_block(S.part("bridge_damaged", hidden=1), damaged=True)

# ================================================================== 등 갑판 (함교 뒤 → 함미)
deck = Hull([
    st(-4.0, 0.0, 0.0, 0.0, vc=11.4, n=2.4),
    st(-1.0, 4.0, 1.8, 1.4, vc=11.2, n=3.0),
    st(9.0, 4.8, 2.0, 1.6, vc=10.0, n=3.4),
    st(19.0, 3.6, 1.5, 1.4, vc=7.4, n=3.2),
    st(24.0, 0.0, 0.0, 0.0, vc=6.0, n=2.6),
], ring=24, sub=2)
S.s(deck.mesh("deck", "hull_l"))
S.s(cb.sphere("dome", radius=1.6, loc=(0, 14.5, 9.6), segments=12, rings=6, material=sk.M("steel")))

# ================================================================== 엘프 귀 지느러미 + 보조 추진기
for side in (1, -1):
    fh = sk.fin("ear", 0.0, 21.0, 30.0, sweep=12.0, rise=11.0, thick=1.5, ring=16, sub=1)
    fh.O = Vector((side * 9.5, -7.0, 6.0))
    fh.A = Vector((side, 0, 0))          # 우현(-X)은 축을 뒤집어 거울상
    S.s(fh.mesh(f"ear{side}", "hull_l"))
    S.s(fh.mesh(f"ear_tip{side}", "navy_l", grow=0.04, s_range=(22.0, 30.0)))
    S.s(fh.mesh(f"ear_cuff{side}", "navy", grow=0.12, s_range=(4.4, 5.6)))
    S.g(cb.sphere(f"ear_light{side}", radius=0.55, loc=fh.point(29.7, 0.0) + Vector((side * 0.3, 0, 0)),
                  segments=8, rings=4, material=sk.M("nav_r" if side > 0 else "nav_g")))
    P, R, U, N = fh.oriented(12.5, PI / 2, up=(0, -1, 0))
    S.f(hw.text(f"ear_no{side}", "01", 3.6, P + N * 0.07, right=R, up=U, mat=sk.M("paper")))
    # 귀 뿌리 뒤 보조 추진기
    sk.engine(S, f"aux{side}", side * 12.5, 6.4, 7.0, 1.3, length=1.4, plume=2.6, seg=16, gold="lip")

# ================================================================== 함미 주추진기 3기
for x, z, r in ((3.0, -0.4, 2.3), (-3.0, -0.4, 2.3), (0.0, 3.4, 1.65)):
    sk.engine(S, f"main{x:+.0f}{z:+.0f}", x, z, 30.0, r, length=r * 0.9, plume=2.1, seg=24)

# ================================================================== 포탑
sk.turret(S, "t_fwd", 0, -23.5, 12.2, k=1.3)
sk.turret(S, "t_aft", 0, 10.0, 11.6, k=1.1, yaw=180)
sk.turret(S, "t_belly", 0, -14.0, -7.6, k=1.2, up=-1)

# ================================================================== 엠블럼 (남색 원판 + 금테 + 엘프 로고)
for side in (1, -1):
    t = hull.t_at(-20.0, 3.0, side)
    P, Ts, Tt, N = hull.frame(-20.0, t)
    sk.emblem_plate(S, f"emblem{side}", P, N, 3.8, up=(0, 0, 1), depth=0.7)
P, Ts, Tt, N = hull.frame(-29.0, PI / 2)
sk.emblem_plate(S, "emblem_top", P, N, 2.3, up=(0, -1, 0), depth=0.6, tolerance=0.006)

# ================================================================== 창 줄 · 격납고 · 패널선
for side in (1, -1):
    sk.window_row(S, hull, f"winA{side}", -12.0, 14.0, 5.0, side=side, r=0.45, pitch=2.0, skip=(6,))
    sk.window_row(S, hull, f"winB{side}", -11.0, 13.0, 1.8, side=side, r=0.45, pitch=2.0, skip=(6,))
    t = hull.t_at(20.5, -2.0, side)
    S.f(hull.decal(f"hangar{side}", hw.stadium(5.6, 2.6, 5), 21.0, t, "dark", lift=0.1))
    for k in range(4):
        y = 18.8 + k * 1.5
        S.g(hull.decal(f"hangar_led{side}{k}", hw.circle(0.2, 6), y, hull.t_at(y, -3.7, side), "glow", lift=0.08))
    for k, s in enumerate((-14.0, 4.0)):
        t = hull.t_at(s, 8.4, side)
        S.f(hull.decal(f"hatch{side}{k}", hw.rrect(2.8, 1.6, 0.5, 2), s, t, "hull_d", lift=0.1))
for i, s in enumerate((-23.0, -13.5, 0.0, 15.0)):
    S.f(hull.patch(f"seam_r{i}", s - 0.11, s + 0.11, -0.3, PI + 0.3, "seam", lift=0.1, ns=1, nt=14))
for i, t in enumerate((0.42, PI - 0.42)):
    S.f(hull.long_line(f"seam_l{i}", -25.0, 26.0, t, 0.018, "seam", lift=0.1))

S.anchor("anchor_bridge", (0, TY - 8.0, 13.8))
S.anchor("anchor_bridge_hit", tuple(HIT_P))
S.anchor("anchor_bow", (0, -42.6, BZ))
S.anchor("anchor_engines", (0, 32.0, 0.5))

S.finish("space/elfinia_flagship.glb", outline=0.16, budget=12000,
         extra={"shipClass": "flagship", "lengthM": 72})
