"""에르핀(왕도): 엘다인으로 각성한 요정 여왕. 에필로그 '에르핀의 세 번째 대관식' 장면용.

원작 2.5주년 엘다인 이격 '에르핀(왕도)'와 그 대관식 복장(사복 '왕관의 주인공', 테마극장 「여왕님의 마음으로
만든 나라」에서 클로에가 만들어 준 대관식 옷)을 바탕으로 한다. 각성 이전 기본 모습(erpin.glb)의 식별 요소
(크리스털 티아라, 붉은 후드 케이프, 발목까지 풀어 내린 머리 + 한쪽 땋기, 별 동공)는 쓰지 않는다.
근거: docs/art/fairy-faction.md 에르핀 절.
- 식별 요소: 각성 날개(위 흰 깃털 큰 날개 + 아래 분홍 반투명 막 날개와 흰 맥), 금발 올림머리와 끝이 분홍으로 물드는
  양 갈래 땋은 머리, 바보털, 붉은 분홍 눈과 반짝임, 덧니, 흰 프릴 보닛(딸기·흰 꽃), 흰 프릴 드레스(두 단 치마,
  진주 테두리, 분홍 속치마), 붉은 줄무늬 어깨띠와 흰 꽃 훈장, 가슴 붉은 리본, 흰 털 테두리의 붉은 대관식 망토,
  흰 장갑, 흰 양말과 붉은 구두, 허벅지 붉은 띠.
- 왕관: 색을 되찾은 '축복의 왕관'(금관 + 붉은 보석 + 진주). 별도 노드 erpin_royal_crown → 대관 순간에 씌우거나 숨긴다.
- 막 날개: 별도 노드 erpin_royal_wing_membrane (반투명·약한 발광, 아웃라인 없음).
- 홀은 넣지 않는다(socket_hand_R).
- 표정: 키트 5종 + regal(위엄 있는 미소) + moved(감격) + cheer(퍼레이드 환호, 덧니) + blink 교정 키.

npm run model -- art/blender/characters/erpin_royal.py
npm run shot -- characters/erpin_royal.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, lerp, frame, clamp, smoothstep  # noqa: E402

cb.reset()
e = fairy.Fairy("erpin_royal", ears=None, height=1.18, chest=0.45, bust=0.70, hips=1.08, limb=1.05, segs=0.66, hand_q=0.40,
                cheek=0.12)
k = e.k
M_ = elf.mat
white = M_("rq_white", "#fdfafa")
white_d = M_("rq_white_d", "#ebe1e6")
pearl = M_("rq_pearl", "#f4ecf2")
pink = M_("rq_pink", "#f8cdd9")
red = M_("rq_red", "#d63c4d")
red_d = M_("rq_red_d", "#a92c3c")
sash_w = M_("rq_sash_w", "#ffe9ec")
gold = M_("rq_gold", "#f0c46a")
gold_d = M_("rq_gold_d", "#cc9844")
gem_red = M_("rq_gem", "#e2334b")
green = M_("rq_green", "#8fd0a0")
fur = M_("rq_fur", "#fffdfb")
straw = M_("rq_straw", "#e5414f")
leaf = M_("rq_leaf", "#5fae6a")
flow_c = M_("rq_flow_c", "#f5c94e")
membrane = M_("rq_membrane", "#f683b0", alpha=0.6, emission="#ffb3cf", emission_strength=0.5)
vein = M_("rq_vein", "#fff3f7")

# ---- 얼굴: 붉은 분홍 눈 + 흰 반짝임, 덧니, 기본은 'ω' 입의 능청스러운 얼굴 (원작 왕도 카드). 공용: ec.royal_face
ec.royal_face(e, expr={
    # 위엄 있는 미소: 눈을 반쯤 내리고 입을 다문 채 부드럽게
    "regal": {"eye": {"top": 0.017, "lift": 0.008, "ktop": 4.4},
              "brow": {"ang": 2.0, "dz": 0.068, "arch": 0.005},
              "mouth": {"w": 0.024, "curve": 0.0055, "wave": 0.0, "open": 0.0}},
    # 감격: 눈썹이 올라가고 눈이 커지며 입이 떨리는 웃음
    "moved": {"eye": {"top": 0.034, "lift": 0.012, "tilt_in": 0.010, "ktop": 2.4},
              "iris": {"pupil": 0.85},
              "brow": {"ang": 20.0, "dz": 0.074, "arch": 0.002},
              "mouth": {"w": 0.028, "curve": 0.0040, "open": 0.0080, "wave": 0.0018}},
    # 퍼레이드 환호: 크게 벌린 입과 덧니 (원작 대관식 퍼레이드 컷)
    "cheer": {"eye": {"top": 0.030, "lift": 0.010, "ktop": 3.0},
              "brow": {"ang": 6.0, "dz": 0.072, "arch": 0.006},
              "mouth": {"w": 0.038, "curve": 0.0080, "open": 0.0300, "top_arch": 0.0015, "wave": 0.0}},
})

# ---- 머리 (헤어 v2): 금발 올림머리(뒤 경단, 보닛에 가려짐) + 얼굴을 감싸는 짧은 옆머리 + 양 갈래 땋은 머리(끝 분홍)
# 공용: ec.royal_hair (각성 전투 판 erpin_awakened.py와 같은 머리)
h = ec.royal_hair(e, braid_tie=red)


# ---- 보닛: 머리 위·뒤를 덮는 흰 천 + 얼굴을 감싸는 프릴 + 딸기·흰 꽃 장식
def ruffle_el(az):
    a = abs(((az + 180) % 360) - 180)
    if a <= 100:
        return 46.0 - 18.0 * (a / 100.0) ** 1.5
    return 28.0 - 10.0 * smoothstep(100.0, 180.0, a)


def bonnet(buf):
    w = {"head": 1.0}
    n, rows = 20, 3
    lift = 0.010 * k
    grid = []
    for j in range(n):
        az = 360.0 * j / n
        se = h.s_of_el(az, ruffle_el(az))
        col = []
        for i in range(rows + 1):
            s = se * (i / rows) ** 0.9
            col.append(buf.vert(h.path(az, s, lift * (1.0 + 0.4 * math.sin(math.pi * i / rows)))[0], w))
        grid.append(col)
    top = buf.vert(h.path(0.0, 0.0, lift * 1.1)[0], w)
    for j in range(n):
        j2 = (j + 1) % n
        buf.face((top, grid[j2][0], grid[j][0]), white)
        for i in range(rows):
            buf.face((grid[j][i], grid[j2][i], grid[j2][i + 1], grid[j][i + 1]), white)
    # 안쪽 면 (가장자리 두께)
    inner = [buf.vert(h.path(360.0 * j / n, h.s_of_el(360.0 * j / n, ruffle_el(360.0 * j / n)), 0.0)[0], w)
             for j in range(n)]
    for j in range(n):
        j2 = (j + 1) % n
        buf.face((grid[j][-1], grid[j2][-1], inner[j2], inner[j]), white_d)
    # 프릴: 가장자리를 따라 볼록볼록한 띠
    pts = []
    for i in range(41):
        az = 360.0 * i / 40
        pts.append(h.path(az, h.s_of_el(az, ruffle_el(az)), lift * 1.3)[0])
    ec.bead_tube(buf, pts, 0.009 * k, 0.018 * k, 20, segs=5, n_per=2, mat=white, wfn=lambda q: w)


e.part("bonnet", "head", bonnet)


def bonnet_deco(buf):
    """보닛 왼쪽(+X) 위의 딸기 세 알과 흰 꽃 둘."""
    w = {"head": 1.0}
    for az, el, sc in ((46.0, 48.0, 1.0), (66.0, 36.0, 0.85)):
        p, n_ = h.path(az, h.s_of_el(az, el), 0.022 * k)
        up = V((0, 0, 1))
        A = n_.normalized()
        B = A.cross(up).normalized()
        F = A.cross(B).normalized()
        fairy.ellipsoid(buf, p + A * 0.008 * k, A, B, F, 0.020 * k * sc, 0.017 * k * sc, 0.017 * k * sc, segs=8,
                        rings=5, mat=straw, w=w)
        fairy.prism(buf, fairy.star_poly(0.013 * k * sc, 0.005 * k * sc, 5, 90.0), 0.003 * k,
                    Matrix.Translation(p - A * 0.008 * k * sc) @ frame(-A, F), mat=leaf, w=w)
    for az, el in ((28.0, 52.0),):
        p, n_ = h.path(az, h.s_of_el(az, el), 0.018 * k)
        ec.flower(buf, Matrix.Translation(p) @ frame(n_, (0, 0, 1)), 0.020 * k, white, flow_c, wts=w, depth=0.004 * k)


e.part("bonnet_deco", "head", bonnet_deco)


# ---- 축복의 왕관 (별도 노드): 보닛 위 금관, 앞 붉은 보석, 진주 끝 뾰족 장식
def crown(buf):
    w = {"head": 1.0}

    def el_fn(az):
        return 60.0 + 10.0 * (1 - math.cos(math.radians(az))) / 2

    n = 20
    lift = 0.024 * k
    base, top, nrm = [], [], []
    for i in range(n):
        az = 360.0 * i / n
        s = h.s_of_el(az, el_fn(az))
        p, nn = h.path(az, s, lift)
        base.append(p)
        nrm.append(nn)
    c = sum(base, V()) / n
    axis = V((0, 0.10, 1.0)).normalized()
    hgt = 0.030 * k
    for i, p in enumerate(base):
        out = V((p.x - c.x, p.y - c.y, 0)).normalized()
        top.append(p + axis * hgt + out * 0.008 * k)
    ob_ = [buf.vert(p, w) for p in base]
    ot = [buf.vert(p, w) for p in top]
    ib = [buf.vert(p - V((p.x - c.x, p.y - c.y, 0)).normalized() * 0.004 * k, w) for p in base]
    it = [buf.vert(p - V((p.x - c.x, p.y - c.y, 0)).normalized() * 0.004 * k, w) for p in top]
    for i in range(n):
        j = (i + 1) % n
        buf.face((ob_[i], ob_[j], ot[j], ot[i]), gold)
        buf.face((ib[i], it[i], it[j], ib[j]), gold_d)
        buf.face((ot[i], ot[j], it[j], it[i]), gold)
        buf.face((ob_[i], ib[i], ib[j], ob_[j]), gold)
    # 뾰족 장식 6개 (앞이 가장 높다) + 진주
    for i in range(6):
        az = 360.0 * i / 6
        jf = az / 360.0 * n
        p = top[int(jf) % n]
        out = V((p.x - c.x, p.y - c.y, 0)).normalized()
        tall = (0.034 if i == 0 else 0.024) * k
        Mx = Matrix.Translation(p - axis * 0.004 * k) @ frame(out, axis)
        fairy.prism(buf, [(-0.011 * k, 0.0), (0.011 * k, 0.0), (0.0, tall)], 0.005 * k, Mx, mat=gold, w=w,
                    chamfer=0.0018 * k)
        tip = p + axis * (tall - 0.002 * k) + out * 0.003 * k
        fairy.ellipsoid(buf, tip, axis, out.cross(axis).normalized(), out, 0.006 * k, 0.006 * k, 0.006 * k, segs=5,
                        rings=3, mat=pearl, w=w)
    # 앞 붉은 보석 + 양옆 작은 보석
    pf = (base[0] + top[0]) / 2
    outf = V((pf.x - c.x, pf.y - c.y, 0)).normalized()
    Mf = Matrix.Translation(pf + outf * 0.003 * k) @ frame(outf, axis)
    ec.gem(buf, Mf, 0.020 * k, 0.026 * k, gem_red, depth=0.006 * k, frame_mat=gold_d, frame_w=0.003 * k, wts=w)
    for i in (n // 4, 3 * n // 4):
        pp = (base[i] + top[i]) / 2
        oo = V((pp.x - c.x, pp.y - c.y, 0)).normalized()
        fairy.ellipsoid(buf, pp + oo * 0.004 * k, oo, axis, oo.cross(axis), 0.006 * k, 0.008 * k, 0.008 * k, segs=6,
                        rings=4, mat=gem_red, w=w)


ec.node_part(e, "crown", crown)

# ---- 드레스: 흰 몸판(프릴 목선) + 퍼프 소매 + 두 단 프릴 치마(진주 테두리) + 분홍 속치마
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(white, hem=wz - 0.01 * k, collar=None, flare=0.0)
neck = [e.torso_point(e.torso_top - 0.016 * k, a, 0.012 * k)[0] for a in range(0, 361, 12)]
e.part("neck_frill", "body", lambda b: ec.bead_tube(b, neck, 0.005 * k, 0.010 * k, 12, segs=4, n_per=2, mat=white,
                                                    wfn=lambda q: {"chest": 1.0}))
e.sleeves(white, length=0.30, off=0.012, puff=0.024, flare=0.006, cuff=(pearl, 0.010, 0.004))
under = fairy.Shell(e, pink, hz + 0.010 * k, 0.236 * k, off=0.022, th=0.004, skirt=True, cols=18, rows=3,
                    flare=[(0.0, 0.0), (0.5, 0.020), (1.0, 0.050)], ruffle=(0.006, 12, 0.5))
under.done("underskirt")
tier = fairy.Shell(e, white, wz + 0.006 * k, 0.300 * k, off=0.026, th=0.004, skirt=True, cols=20, rows=4,
                   flare=[(0.0, 0.0), (0.5, 0.020), (1.0, 0.058)], ruffle=(0.008, 11, 0.45), cover=True)
hem = [tier.surface(1.0, a, 0.006 * k)[0] for a in range(0, 361, 10)]
ec.bead_tube(tier.buf, hem, 0.006 * k, 0.011 * k, 22, segs=4, n_per=2, mat=pearl, wfn=lambda q: fairy.skirt_w(e, q))
tier.done("skirt")

# ---- 붉은 줄무늬 어깨띠 (오른 어깨 -X → 왼 엉덩이 +X) + 흰 꽃 훈장 + 가슴 붉은 리본
sash_path = [("torso", e.torso_top - 0.012 * k, -58, 0.016 * k), ("torso", cz + 0.030 * k, -26, 0.016 * k),
             ("torso", cz - 0.030 * k, 12, 0.017 * k), ("torso", wz - 0.004 * k, 46, 0.024 * k),
             ("torso", hz + 0.010 * k, 74, 0.034 * k)]
e.strap(red, sash_path, width=0.032, th=0.0035, name="sash")
e.strap(sash_w, [(a, z, ang, off + 0.0028 * k) for a, z, ang, off in sash_path], width=0.010, th=0.0012,
        name="sash_stripe")
e.gear("sash_medal", ("torso", hz + 0.012 * k, 72, 0.042 * k),
       lambda b, Mx, w: (ec.flower(b, Mx, 0.032 * k, white, flow_c, wts=w, depth=0.005 * k),
                         ec.gem(b, Mx @ Matrix.Translation((0, 0.002 * k, -0.030 * k)), 0.016 * k, 0.026 * k, red,
                                depth=0.004 * k, wts=w)))
e.gear("chest_bow", ("torso", e.torso_top - 0.032 * k, 0.0, 0.016 * k),
       lambda b, Mx, w: fairy.bow_geo(b, Mx, 0.060 * k, red, w=w, tails=0.9, knot_mat=red_d, segs=5))

# ---- 흰 장갑 + 손목 프릴, 흰 양말 + 붉은 구두, 허벅지 붉은 띠
e.gloves(white, inflate=0.0028)
for sd in ("L", "R"):
    e.ring(white, f"arm_{sd}", 0.93, h=0.016, th=0.005, off=0.010, name=f"glove_frill_{sd}")
    fairy.leg_tube(e, white, sd, 0.80, 0.93, off=0.006, name=f"sock_{sd}")
    e.ring(white, f"leg_{sd}", 0.81, h=0.020, th=0.005, off=0.010, name=f"sock_frill_{sd}")
    e.ring(red, f"leg_{sd}", 0.90, h=0.010, th=0.003, off=0.014, name=f"shoe_strap_{sd}")
e.boots(red, top=0.93, sole=(red_d, 0.012), off=0.010, toe=0.003)
e.ring(red, "leg_R", 0.34, h=0.016, th=0.004, off=0.004, name="thigh_band")    # 원작 대관식 옷의 허벅지 붉은 띠

# ---- 대관식 망토: 어깨 뒤에서 바닥까지, 흰 털(어민) 테두리 깃·앞단·밑단
MA0, MA1 = 100.0, 260.0


def mantle_a(a, u):
    g = 30.0
    return lerp(MA0, MA1, (a - g) / (360.0 - 2 * g))


mantle = fairy.Shell(e, red, e.shoulder_z + 0.012 * k, 0.012 * k, gap=30.0, off=0.032, th=0.005, skirt=True,
                     shoulder=1.0, cols=11, rows=8, flare=[(0.0, 0.0), (0.25, 0.026), (1.0, 0.150)], a_fn=mantle_a)


def fur_edge(pts, nrms, r0, r1, beads):
    P = [p + n_ * 0.008 * k for p, n_ in zip(pts, nrms)]
    ec.bead_tube(mantle.buf, P, r0, r1, beads, segs=5, n_per=2, mat=fur, wfn=lambda q: fairy.skirt_w(e, q))


R_, C_ = mantle.rows, mantle.cols
fur_edge([mantle.P[R_ - 1][j] for j in range(C_)], [mantle.N[R_ - 1][j] for j in range(C_)], 0.016 * k, 0.026 * k, 12)
for jj in (0, C_ - 1):
    fur_edge([mantle.P[i][jj] for i in range(R_)], [mantle.N[i][jj] for i in range(R_)], 0.014 * k, 0.022 * k, 9)
fur_edge([mantle.P[0][j] for j in range(C_)], [mantle.N[0][j] for j in range(C_)], 0.018 * k, 0.026 * k, 7)
# 망토 뒤 금 장식 띠 (밑단 위)
for a in (150.0, 210.0):
    p, n_ = mantle.surface(0.80, a, 0.003 * k)
    ec.gem(mantle.buf, Matrix.Translation(p) @ frame(n_, (0, 0, 1)), 0.030 * k, 0.040 * k, gold, depth=0.003 * k,
           wts=fairy.skirt_w(e, p))
mantle.done("mantle")

# ---- 각성 날개: 위 흰 깃털 큰 날개 + 아래 분홍 반투명 막 날개 (흰 맥). 공용: ec.royal_wings
ec.royal_wings(e, membrane, vein)

res = e.finalize()
# 땋은 머리 끝을 분홍으로 물들이기 (원작 왕도: 금발 끝이 분홍). 공용: ec.royal_hair_tint
ec.royal_hair_tint(e, res)
e.export("characters/erpin_royal.glb")
