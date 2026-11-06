"""에르핀(왕도) 각성 전투 복장: 엘다인으로 각성한 요정 여왕. 3막 M9 마지막 전투신(네르와 함께 흑뉴아를 제압)용.

원작 2.5주년 엘다인 이격 '에르핀(왕도)'의 기본 복장(카드·소개 이미지·로비 스탠딩)을 따른다. 대관식 복장
(erpin_royal.glb, 사복 '왕관의 주인공')과 각성 이전 기본 모습(erpin.glb)과는 다른 판이다. 근거: docs/art/characters-cameo3.md.
- 얼굴·머리·각성 날개는 erpin_royal.py와 같은 공용 코드(erpin_common.royal_face, royal_hair, royal_wings,
  royal_hair_tint)로 만든다.
- 식별 요소: 금발 높은 포니테일, 바닥까지 오는 양 갈래 땋은 머리(끝이 분홍·연보라로 물듦, 금 구슬), 왼쪽 머리의
  흰·분홍 꽃 핀과 파란 보석 잎, 머리 위 작은 금관(파란 보석), 붉은 눈 + 흰 반짝임과 덧니, 'ω' 입,
  흰 민소매 몸판(높은 깃, 금 테두리와 V선), 금 팔찌, 파란 마름모 귀걸이, 금 마름모 문장을 단 흰 앞자락(금 테두리),
  자홍빛 속치마, 양옆으로 벌어진 흰 겉자락(끝이 분홍으로 물듦), 허리의 분홍 꽃, 흰 프릴 속바지,
  정강이를 감싼 분홍 마름모 각반(금 테두리, 끝에 금 구슬과 파란 네 갈래 별), 큰 흰 깃털 날개 + 분홍 반투명 막 날개.
- 재해석: 금관은 별도 노드 erpin_awakened_crown(침공전 결전 장면에서 숨길 수 있다). 바닥까지 오는 땋은 머리는
  A 포즈 팔과 겹치지 않게 팔 뒤로 돌렸다(cameo3.Braid3, 뿌리는 head, 사슬은 chest).
- 표정: 키트 5종 + fierce(결의: 치켜 올린 눈썹과 'ω' 입, 원작 카드) + battle_cry("이걸로 끝이야!") + taunt
  (흑뉴아를 긁는 능청 웃음) + blink 교정 키.

npm run model -- art/blender/characters/erpin_awakened.py
npm run shot -- characters/erpin_awakened.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, loft, band, disc, lerp, frame, clamp, smoothstep  # noqa: E402

cb.reset()
e = fairy.Fairy("erpin_awakened", ears=None, height=1.18, chest=0.45, bust=0.70, hips=1.08, limb=1.05, segs=0.62, hand_q=0.40,
                cheek=0.12)
k = e.k
M_ = elf.mat
white = M_("ea_white", "#fdfafa")
white_d = M_("ea_white_d", "#eadfe5")
gold = M_("ea_gold", "#f0c46a")
gold_d = M_("ea_gold_d", "#cc9844")
magenta = M_("ea_magenta", "#c8336b")
magenta_d = M_("ea_magenta_d", "#9c2552")
pink = M_("ea_pink", "#f6a9c4")
pink_d = M_("ea_pink_d", "#e27fa6")
blue = M_("ea_blue", "#8fc6ec")
blue_d = M_("ea_blue_d", "#4f86c4")
flower_m = M_("ea_flower", "#fbe0ea")
membrane = M_("ea_membrane", "#f683b0", alpha=0.6, emission="#ffb3cf", emission_strength=0.5)
vein = M_("ea_vein", "#fff3f7")

# ---- 얼굴: 대관식 판과 같은 공용 얼굴 + 전투 표정
ec.royal_face(e, expr={
    # 결의: 치켜 올린 눈썹, 반쯤 내린 눈, 'ω' 입 (원작 왕도 카드)
    "fierce": {"eye": {"top": 0.020, "ktop": 4.0, "tilt_in": -0.010},
               "brow": {"ang": -16.0, "dz": 0.060, "th": 0.0072},
               "mouth": {"w": 0.024, "curve": 0.0020, "wave": 0.0020, "open": 0.0}},
    # 전투 함성: 크게 벌린 입과 덧니 ("이걸로⋯ 끝이야!")
    "battle_cry": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.012},
                   "brow": {"ang": -20.0, "dz": 0.058, "th": 0.0076},
                   "mouth": {"w": 0.040, "curve": -0.0010, "open": 0.0340, "top_arch": 0.0050, "wave": 0.0}},
    # 능청 웃음: 흑뉴아를 긁는 "네가 우리보다 약해서 그래"
    "taunt": {"eye": {"top": 0.016, "lift": 0.010, "ktop": 4.6},
              "brow": {"ang": 4.0, "dz": 0.070, "arch": 0.005},
              "mouth": {"w": 0.032, "curve": 0.0070, "open": 0.0080, "top_arch": -0.0010, "wave": 0.0}},
})

# ---- 머리: 공용 머리(땋은 머리 없이) + 높은 포니테일 + 팔 뒤로 바닥까지 오는 양 갈래 땋은 머리
h = ec.royal_hair(e, braids=False)
h.ponytail(height=46, length=0.34, width=0.13, clumps=2, lift=1.2, curve=1.1, tie=gold)

sz = e.shoulder_z
braids = []
for s in (1, -1):
    sd = "L" if s > 0 else "R"
    ctrl = [h.sp(s * 108, -8, h.off * 0.2), h.sp(s * 118, -30, h.off * 0.95),
            V((s * 0.190 * k, 0.118 * k, e.torso_top + 0.012 * k)), V((s * 0.214 * k, 0.128 * k, sz - 0.120 * k)),
            V((s * 0.236 * k, 0.130 * k, 0.360 * k)), V((s * 0.250 * k, 0.100 * k, 0.140 * k)),
            V((s * 0.272 * k, 0.040 * k, 0.050 * k))]
    bm = M_(f"ea_braid_{sd}", ec.ROYAL_HAIR)
    br = c3.Braid3(e, f"hair_braid_{sd}", ctrl, w0=0.066 * k, w1=0.046 * k, lobes=15, tilt=28,
                   face=(s * 0.55, 0.84, 0.0), mat=bm, bones=3, parent="chest", root_bone="head", root_t=0.10,
                   tie=gold, tie_at=0.92, tuft=0.026 * k, segs=7, rings=5)
    br.done()
    braids.append(br)


def braid_beads(buf):
    for br in braids:
        c, T, F = br.tip_c, br.tip_T, br.tip_F
        w = br.w_at(0.92)
        c2.ellipsoid(buf, c - T * 0.014 * k, T, F.cross(T).normalized(), F, 0.010 * k, 0.010 * k, 0.010 * k,
                     segs=8, rings=5, mat=gold, w=w)


e.part("braid_beads", "head", braid_beads)


# 왼쪽(+X) 머리 꽃 핀: 흰·분홍 꽃 둘 + 파란 보석 잎
def hair_flowers(buf):
    w = {"head": 1.0}
    for az, el, r in ((46.0, 30.0, 0.024), (64.0, 14.0, 0.019), (30.0, 40.0, 0.014)):
        p, nn = h.path(az, h.s_of_el(az, el), 0.008 * k)
        Mf = Matrix.Translation(p) @ frame(nn, (0, 0, 1))
        ec.flower(buf, Mf, r * k, flower_m, gold, wts=w)
        for ang in (-60.0, 60.0):
            Ml = Mf @ Matrix.Rotation(math.radians(ang + 180.0), 4, "Y") @ Matrix.Translation((0, 0.001 * k, r * k))
            ec.gem(buf, Ml, 0.012 * k, 0.022 * k, blue, depth=0.003 * k, wts=w)


e.part("hair_flowers", "head", hair_flowers)
h.shine(el=46, spread=70, n=2, size=1.1)


# ---- 작은 금관 (별도 노드 crown): 정수리 앞쪽에 얹은 작은 금관 (봉우리 다섯 + 앞 파란 보석)
def crown(buf):
    w = {"head": 1.0}
    top, tn = h.path(10.0, h.s_of_el(10.0, 66.0), 0.000)
    up = (tn * 0.75 + V((0, -0.10, 0.65))).normalized()
    fwd = V((0, -1, 0))
    fwd = (fwd - up * fwd.dot(up)).normalized()
    side = up.cross(fwd).normalized()
    r = 0.044 * k
    n = 20
    ring_b, ring_t = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = fwd * math.cos(a) + side * math.sin(a)
        ring_b.append(top + d * r - up * 0.004 * k)
        ring_t.append(top + d * r * 1.06 + up * 0.016 * k)
    elf._loop(buf, [q + up * 0.004 * k for q in ring_b], [(q - top).normalized() for q in ring_b], [up] * n,
              0.018 * k, 0.004 * k, mat=gold, w=w)
    for i in range(0, n, 4):
        a = 2 * math.pi * i / n
        d = fwd * math.cos(a) + side * math.sin(a)
        base = top + d * r * 1.04 + up * 0.012 * k
        hgt = (0.040 if i == 0 else 0.030) * k
        Mx = Matrix.Translation(base) @ frame(d, up)
        c2.prism(buf, [(-0.012 * k, 0.0), (0.012 * k, 0.0), (0.0, hgt)], 0.005 * k, Mx, mat=gold, w=w,
                 chamfer=0.0015 * k)
        c2.ellipsoid(buf, base + up * (hgt + 0.003 * k), up, side, d, 0.004 * k, 0.004 * k, 0.004 * k, segs=6,
                     rings=4, mat=gold_d, w=w)
    Mc = Matrix.Translation(top + fwd * r * 1.10 + up * 0.012 * k) @ frame(fwd, up)
    ec.gem(buf, Mc, 0.016 * k, 0.022 * k, blue, depth=0.005 * k, wts=w)


ec.node_part(e, "crown", crown)

# ---- 상의: 흰 민소매 몸판(높은 깃, 금 테두리와 V선), 맨팔 + 금 팔찌
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(white, hem=wz - 0.006 * k, collar="stand", collar_mat=white, flare=0.006)
e.part("collar_gold", "body", lambda buf: band(buf, (0, 0.004 * k, e.torso_top + 0.024 * k), (0, 0, 1), (1, 0, 0),
                                               0.0545 * k, 0.0505 * k, 0.005 * k, 0.003 * k, segs=14, mat=gold,
                                               w={"neck": 0.5, "chest": 0.5}))
for sg in (1, -1):
    e.strap(gold, [("torso", e.torso_top - 0.004 * k, sg * 36, 0.0115 * k), ("torso", cz + 0.010 * k, sg * 12, 0.012 * k),
                   ("torso", cz - 0.020 * k, 0.0, 0.012 * k)], width=0.006, th=0.002, name=f"bodice_v_{sg}")
    e.strap(gold, [("torso", e.torso_top - 0.004 * k, sg * 62, 0.0115 * k), ("torso", sz - 0.030 * k, sg * 84, 0.012 * k)],
            width=0.006, th=0.002, name=f"armhole_{sg}")
p_g, n_g = e.torso_point(cz - 0.026 * k, 0, 0.014 * k)
e.part("chest_gem", "body", lambda buf: ec.gem(buf, Matrix.Translation(p_g) @ frame(n_g, (0, 0, 1)), 0.016 * k,
                                               0.024 * k, gold, depth=0.004 * k, wts=e._torso_wfn(p_g, 0)))
for sd in ("L", "R"):
    e.ring(gold, f"arm_{sd}", 0.30, h=0.012, th=0.004, off=0.004, name=f"armlet_{sd}")
    e.ring(gold, f"arm_{sd}", 0.92, h=0.016, th=0.005, off=0.004, name=f"bracelet_{sd}")
    e.ring(gold_d, f"arm_{sd}", 0.86, h=0.005, th=0.003, off=0.004, name=f"bracelet_b_{sd}")

# ---- 하의: 흰 프릴 속바지, 자홍 속치마, 금 마름모 문장 흰 앞자락, 양옆으로 벌어진 흰 겉자락(끝 분홍), 분홍 꽃
q0 = e.q
e.q = 0.5
e.pants(white, waist=wz - 0.004 * k, length=0.16, bag=0.014, blouse=0.0, off=0.010,
        cuff=(white_d, 0.012, 0.004))
e.q = q0
under = c2.Shell(e, magenta, wz + 0.002 * k, 0.330 * k, gap=34.0, off=0.020, th=0.004, skirt=True, rows=7, cols=18,
                 flare=[(0.0, 0.0), (0.5, 0.020), (1.0, 0.048)], ruffle=(0.006, 7, 0.6))
under.hem_trim(magenta_d, width=0.008, th=0.002)
under.done("underskirt")
front = c2.Shell(e, white, wz + 0.006 * k, 0.300 * k, gap=150.0, back_only=True, off=0.026, th=0.004, skirt=True,
                 rows=7, cols=6, flare=[(0.0, 0.0), (1.0, 0.020)])
front.edge_trim(gold, width=0.006, th=0.002).hem_trim(gold, width=0.006, th=0.002)
pc, pn = front.surface(0.30, 0.0, 0.004 * k)
Mo = Matrix.Translation(pc) @ frame(pn, (0, 0, 1))
wo = c2.skirt_w(e, pc)
c2.prism(front.buf, [(0.0, 0.034 * k), (0.016 * k, 0.000), (0.006 * k, -0.006 * k), (0.0, -0.024 * k),
                     (-0.006 * k, -0.006 * k), (-0.016 * k, 0.0)], 0.004 * k, Mo, mat=gold, w=wo, chamfer=0.0012 * k)
c2.prism(front.buf, c2.diamond_poly(0.010 * k, 0.020 * k), 0.003 * k, Mo @ Matrix.Translation((0, -0.004 * k, 0.006 * k)),
         mat=magenta, w=wo)
front.done("front_panel")
outer = c2.Shell(e, white, wz + 0.010 * k, 0.250 * k, gap=[(0.0, 40.0), (1.0, 62.0)], off=0.032, th=0.004,
                 skirt=True, rows=8, cols=16, flare=[(0.0, 0.0), (0.4, 0.034), (1.0, 0.090)],
                 drop=[(0.0, 0.0), (1.0, 0.04)])
outer.edge_trim(gold, width=0.007, th=0.002, i0=1).hem_trim(gold, width=0.007, th=0.002)
outer.done("overskirt")
e.ring(gold, "torso", wz + 0.002 * k, h=0.012, th=0.004, off=0.034, name="waist_band")
p_f, n_f = e.torso_point(wz + 0.002 * k, 30, 0.040 * k)


def waist_flower(buf):
    w = e._torso_wfn(p_f, 0)
    Mf = Matrix.Translation(p_f) @ frame(n_f, (0, 0, 1))
    ec.flower(buf, Mf, 0.020 * k, flower_m, pink_d, wts=w)
    for ang in (-70.0, 70.0):
        ec.gem(buf, Mf @ Matrix.Rotation(math.radians(ang + 180.0), 4, "Y") @ Matrix.Translation((0, 0.001 * k, 0.020 * k)),
               0.010 * k, 0.018 * k, blue, depth=0.003 * k, wts=w)


e.part("waist_flower", "body", waist_flower)

# ---- 다리: 분홍 마름모 각반(금 테두리) + 끝의 금 구슬과 파란 네 갈래 별
e.boots(pink, top=0.56, sole=(pink_d, 0.012), cuff=gold, off=0.016, toe=0.010)
for sd in ("L", "R"):
    a = e.anchor((f"leg_{sd}", 0.70, 0, 0.030 * k))

    def greave(buf, a=a, sd=sd):
        Mx = a.matrix()
        dia = [(0.0, 0.090 * k), (0.036 * k, 0.0), (0.0, -0.100 * k), (-0.036 * k, 0.0)]
        c2.prism(buf, [(x * 1.18, z * 1.12) for x, z in dia], 0.004 * k, Mx, mat=gold, w=a.w, chamfer=0.001 * k)
        c2.prism(buf, dia, 0.008 * k, Mx @ Matrix.Translation((0, -0.003 * k, 0)), mat=pink, w=a.w,
                 chamfer=0.003 * k)
        c2.prism(buf, [(x * 0.42, z * 0.42) for x, z in dia], 0.003 * k,
                 Mx @ Matrix.Translation((0, -0.010 * k, 0.004 * k)), mat=white, w=a.w)
        tip = Mx @ V((0, -0.006 * k, -0.116 * k))
        c2.ellipsoid(buf, tip, V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), 0.008 * k, 0.008 * k, 0.008 * k, segs=8,
                     rings=4, mat=gold, w=a.w)
        Ms = Matrix.Translation(tip + V((0, -0.002 * k, -0.024 * k))) @ frame(V((0, -1, 0)), (0, 0, 1))
        c2.prism(buf, c2.star_poly(0.020 * k, 0.006 * k, n=4, rot=90.0), 0.005 * k, Ms, mat=blue, w=a.w,
                 chamfer=0.0015 * k)
    e.part(f"greave_{sd}", "body", greave)

# ---- 각성 날개: 공용 (위 흰 깃털 큰 날개 + 아래 분홍 반투명 막 날개)
ec.royal_wings(e, membrane, vein)

res = e.finalize()
# 땋은 머리 끝(무릎 아래)을 분홍으로, 겉자락 끝을 분홍으로 물들인다 (원작: 머리끝·자락 끝이 분홍)
ec.royal_hair_tint(e, res, z_lo=0.10 * k, z_hi=0.42 * k)
body = res.get("body")
if body is not None:
    c2.vc_gradient(body, "#fdfafa", [(0.26 * k, "#f7b6cc"), (0.46 * k, "#fdfafa")],
                   pred=lambda co: co.z < 0.48 * k and abs(co.x) > 0.075 * k)
e.export("characters/erpin_awakened.glb")
