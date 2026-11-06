"""네르(빡침) 대관식 복장: 에필로그 '에르핀의 세 번째 대관식'에 왕관 수여자로 선 네르.

원작: 침공전이 끝나고 한 달 뒤의 대관식에 네르는 왕관 수여자로서 갈아입고 나온다(테마극장 「여왕님의 마음으로 만든
나라」). 그 옷이 네르(빡침)의 사복 '왕관의 수여자'(클로에가 대관식을 위해 만들어 준 옷)다. 근거: docs/art/characters-cameo3.md.
- 얼굴·머리·땋은 머리는 전투 판 ner.glb와 같은 공용 코드(cameo3.ner_face, ner_hair, ner_braid)로 만든다.
- 식별 요소: 높이 솟은 부채꼴 금관(가운데가 가장 높은 다섯 봉우리, 크림색 판에 붉은 딸기 보석, 아래 흰 꽃 띠와
  가운데 금 꽃, 옆으로 늘어진 술), 흰 긴 예복(금 테두리), 목의 금 나비 브로치와 붉은 보석, 가슴에서 늘어진 긴 금
  펜던트, 넓게 퍼진 소매와 금 리본, 엷은 금빛 겉자락, 연두·흰 줄무늬 리본, 큰 흰 날개, 흰 꽃과 딸기를 단 잎 가지.
- 재해석: 금관은 별도 노드 ner_coronation_crown(장면에 따라 숨김). 잎 가지는 별도 노드 ner_coronation_branch
  (socket_hand_R, 로컬: 원점 = 파지점, 줄기 = 로컬 +Z). 원작 금관의 세밀한 문양은 옮기지 않고 판·테·보석·꽃으로 다시 그렸다.
- 표정: 공용 세트(키트 5종 + rage, glare, teary, smug) + solemn(의식의 고요한 얼굴) + beam(감격한 미소) + blink 교정 키.

npm run model -- art/blender/characters/ner_coronation.py
npm run shot -- characters/ner_coronation.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame  # noqa: E402

cb.reset()
e = c3.ner_body("ner_coronation")
k = e.k
M_ = elf.mat

white = M_("nc_white", "#fdfaf4")
white_d = M_("nc_white_d", "#ece2d2")
sheer = M_("nc_sheer", "#f1e4c6")
cream = M_("nc_cream", "#fbf1df")
gold = M_("nc_gold", "#e9bf62")
gold_d = M_("nc_gold_d", "#c4923f")
silver = M_("nc_silver", "#c6cad9")
red = M_("nc_red", "#e2455e")
green = M_("nc_green", "#a9d68e")
green_d = M_("nc_green_d", "#6fa05c")
flower_c = M_("nc_flower_c", "#f2c94c")

# ---- 얼굴·머리: 전투 판과 같은 공용 코드 + 대관식 표정 둘
c3.ner_face(e, expr={
    # 의식의 고요한 얼굴: 눈을 조금 더 뜨고 입꼬리를 살짝 올림
    "solemn": {"eye": {"top": 0.018, "ktop": 4.6},
               "brow": {"ang": 2.0, "dz": 0.066, "arch": 0.003},
               "mouth": {"w": 0.016, "curve": 0.0025}},
    # 감격한 미소: 눈이 휘고 입이 벌어진 웃음 (울고 있는 에르핀을 보며)
    "beam": {"eye": {"top": 0.020, "lift": 0.014, "kbot": 2.4, "tilt_in": 0.006},
             "brow": {"ang": 14.0, "dz": 0.070, "arch": 0.004},
             "mouth": {"w": 0.030, "curve": 0.0080, "open": 0.0110, "top_arch": -0.0010}},
})
h = c3.ner_hair(e)

# ---- 부채꼴 금관 (별도 노드 crown): 머리 위로 솟은 다섯 봉우리 판 + 금 테 + 딸기 보석 + 꽃 띠 + 옆 술
EL0 = 42.0
AZ = 70.0


def crown_geo(buf):
    w = {"head": 1.0}
    n = 25
    base, nrm, ups, tops = [], [], [], []
    peaks = [(-0.80, 0.50), (-0.42, 0.74), (0.0, 1.0), (0.42, 0.74), (0.80, 0.50)]

    def height(u):
        # 봉우리마다 뾰족하게 솟는 윗변 (u: -1..1)
        hgt = 0.0
        for pc, ph in peaks:
            d = abs(u - pc) / 0.21
            hgt = max(hgt, ph * max(0.0, 1.0 - d) ** 1.1)
        return (0.060 + 0.200 * hgt) * (1.0 - 0.30 * abs(u) ** 2)

    for i in range(n):
        u = -1 + 2 * i / (n - 1)
        az = u * AZ
        el = EL0 - 8.0 * u * u
        s = h.s_of_el(az, el)
        p, nn = h.path(az, s, 0.008 * k)
        up = (V((0, 0.18, 1.0)) - nn * V((0, 0.18, 1.0)).dot(nn)).normalized()
        base.append(p)
        nrm.append(nn)
        ups.append(up)
        tops.append(p + up * height(u) * k + nn * 0.030 * k * (height(u) / 0.26))
    th = 0.006 * k
    of = [buf.vert(p, w) for p in base]
    ot = [buf.vert(p, w) for p in tops]
    inf = [buf.vert(p - nn * th, w) for p, nn in zip(base, nrm)]
    int_ = [buf.vert(p - nn * th, w) for p, nn in zip(tops, nrm)]
    for i in range(n - 1):
        buf.face((of[i], of[i + 1], ot[i + 1], ot[i]), cream)
        buf.face((inf[i], int_[i], int_[i + 1], inf[i + 1]), gold_d)
        buf.face((ot[i], ot[i + 1], int_[i + 1], int_[i]), gold)
        buf.face((of[i], inf[i], inf[i + 1], of[i + 1]), gold)
    buf.face((of[0], ot[0], int_[0], inf[0]), gold)
    buf.face((of[-1], inf[-1], int_[-1], ot[-1]), gold)
    # 금 테: 윗변 + 아랫변 + 봉우리 사이 골을 따라 내려오는 살
    elf._loop(buf, [p + nn * 0.0015 * k for p, nn in zip(tops, nrm)], nrm,
              [(t - b).normalized() for t, b in zip(tops, base)], 0.012 * k, 0.004 * k, mat=gold, w=w, closed=False)
    elf._loop(buf, [p + nn * 0.0015 * k + up * 0.006 * k for p, nn, up in zip(base, nrm, ups)], nrm, ups,
              0.012 * k, 0.003 * k, mat=gold, w=w, closed=False)
    for uv in (-0.61, -0.21, 0.21, 0.61):
        i = int(round((uv + 1) / 2 * (n - 1)))
        a, b = base[i], tops[i]
        nn = nrm[i]
        side = nn.cross(ups[i]).normalized()
        elf._loop(buf, [a.lerp(b, t) + nn * 0.002 * k for t in (0.05, 0.95)], [nn, nn], [side, side], 0.006 * k,
                  0.0025 * k, mat=gold, w=w, closed=False)
    # 봉우리마다 붉은 딸기 보석 (+ 금 테)
    for pc, ph in peaks:
        i = int(round((pc + 1) / 2 * (n - 1)))
        a, b = base[i], tops[i]
        nn = nrm[i]
        c = a.lerp(b, 0.58) + nn * 0.004 * k
        c3.gem_drop(buf, Matrix.Translation(c) @ frame(nn, (b - a).normalized()), (0.012 + 0.010 * ph) * k, red,
                    depth=0.005 * k, frame_mat=white, frame_w=0.004 * k, w=w)
    # 아래 흰 꽃 띠 + 가운데 금 꽃
    for j in range(9):
        u = -0.90 + 1.80 * j / 8
        i = int(round((u + 1) / 2 * (n - 1)))
        p, nn, up = base[i], nrm[i], ups[i]
        center = abs(u) < 0.05
        r = (0.024 if center else 0.016) * k
        Mf = Matrix.Translation(p + nn * 0.007 * k + up * 0.014 * k) @ frame(nn, up)
        petals = []
        for t in range(20):
            a = 2 * math.pi * t / 20 + math.pi / 2
            rr = r * (0.55 + 0.45 * abs(math.cos(5 * (a - math.pi / 2) / 2)) ** 0.7)
            petals.append((rr * math.cos(a), rr * math.sin(a)))
        c2.prism(buf, petals, 0.003 * k, Mf, mat=gold if center else white, w=w)
        disc(buf, Mf @ V((0, -0.0035 * k, 0)), nn, up, r * 0.32, r * 0.32, 0.0015 * k, segs=6,
             mat=red if center else flower_c, w=w)
    # 옆으로 늘어진 금 술 (양쪽 끝)
    for i in (0, n - 1):
        p = base[i]
        st = [{"c": p - V((0, 0, 0.004 * k)), "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
              {"c": p - V((0, 0, 0.040 * k)), "rx": 0.0030 * k, "ry": 0.0030 * k, "w": w}]
        loft(buf, st, segs=6, cap0="flat", cap1="flat", mat=gold)
        loft(buf, [{"c": p - V((0, 0, 0.040 * k)), "rx": 0.004 * k, "ry": 0.004 * k, "w": w},
                   {"c": p - V((0, 0, 0.050 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
                   {"c": p - V((0, 0, 0.074 * k)), "rx": 0.010 * k, "ry": 0.010 * k, "w": w}], segs=8,
             cap0="flat", cap1="flat", mat=white_d)


_cb = Buf()
crown_geo(_cb)
e.add(_cb.obj("ner_coronation_crown_src", angle=40.0), group="head", tag="crown", node="crown")

# ---- 땋은 머리(공용) + 연두·흰 줄무늬 리본
br = c3.ner_braid(e, h, silver, red, ribbon=(green, white))
h.shine(el=52, spread=76, n=2, size=1.2)

# ---- 흰 긴 예복: 몸판 + 금 목선, 넓게 퍼진 소매(금 소맷단, 금 리본)
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(white, hem=hz - 0.010 * k, collar="stand", collar_mat=white, flare=0.008)
e.sleeves(white, length=0.90, off=0.012, flare=0.040, puff=0.012, cuff=(gold, 0.012, 0.004))
e.gloves(white, cuff=white_d)
for sd in ("L", "R"):
    a = e.anchor((f"arm_{sd}", 0.86, 0, 0.056 * k))
    e.part(f"sleeve_bow_{sd}", "arms",
           lambda buf, a=a: c2.bow_geo(buf, a.matrix(), 0.040 * k, gold, w=a.w, tails=0.8, segs=5))
# 금 목선 V + 에르피엔 나비 브로치(붉은 보석) + 긴 금 펜던트
for sg in (1, -1):
    e.strap(gold, [("torso", e.torso_top - 0.002 * k, sg * 30, 0.012 * k), ("torso", cz + 0.030 * k, sg * 12, 0.013 * k)],
            width=0.008, th=0.0025, name=f"neckline_{sg}")
p_b, n_b = e.torso_point(e.torso_top - 0.006 * k, 0, 0.018 * k)


def brooch(buf):
    w = {"neck": 0.3, "chest": 0.7}
    Mx = Matrix.Translation(p_b) @ frame(n_b, (0, 0, 1))
    fairy.emblem(buf, Mx, 0.046 * k, gold, depth=0.004 * k, w=w, n=24, line=gold_d, low=True)    # 에르피엔 나비
    c3.gem_drop(buf, Mx @ Matrix.Translation((0, -0.004 * k, 0.0)), 0.008 * k, red, depth=0.004 * k, w=w)


e.part("brooch", "body", brooch)
e.strap(gold, [("torso", e.torso_top - 0.020 * k, 0, 0.016 * k), ("torso", cz, 0, 0.016 * k),
               ("torso", wz, 0, 0.020 * k), ("torso", hz - 0.020 * k, 0, 0.026 * k)], width=0.009, th=0.003,
        name="pendant_chain")
p_p, n_p = e.torso_point(hz - 0.040 * k, 0, 0.028 * k)
e.part("pendant", "body", lambda buf: c2.prism(
    buf, [(0.0, 0.022 * k), (0.010 * k, 0.004 * k), (0.004 * k, 0.0), (0.0, -0.032 * k), (-0.004 * k, 0.0),
          (-0.010 * k, 0.004 * k)], 0.004 * k, Matrix.Translation(p_p) @ frame(n_p, (0, 0, 1)), mat=gold,
    w=e._torso_wfn(p_p, 0), chamfer=0.0012 * k))

# ---- 하의: 바닥까지 오는 흰 치마(금 밑단) + 앞이 트인 엷은 금빛 겉자락 + 허리 연두 리본
dress = c2.Shell(e, white, wz + 0.006 * k, 0.020 * k, off=0.016, th=0.004, skirt=True, rows=10, cols=22,
                 flare=[(0.0, 0.0), (0.35, 0.020), (1.0, 0.064)], cover=True)
dress.hem_trim(gold, width=0.010, th=0.002)
dress.done("dress")
over = c2.Shell(e, sheer, wz + 0.010 * k, 0.010 * k, gap=[(0.0, 18.0), (0.4, 30.0), (1.0, 44.0)], off=0.026,
                th=0.004, skirt=True, rows=10, cols=16, flare=[(0.0, 0.0), (0.35, 0.030), (1.0, 0.090)],
                drop=[(0.0, 0.0), (1.0, 0.0)])
over.edge_trim(gold, width=0.008, th=0.002, i0=1).hem_trim(gold, width=0.008, th=0.002)
over.done("overskirt")
e.ring(gold, "torso", wz + 0.004 * k, h=0.014, th=0.004, off=0.030, name="sash")
for sg in (1, -1):
    a = e.anchor(("torso", wz + 0.004 * k, sg * 62, 0.034 * k))
    e.part(f"waist_bow_{sg}", "body",
           lambda buf, a=a: c2.bow_geo(buf, a.matrix(), 0.050 * k, green, w=a.w, tails=1.2, knot_mat=white,
                                       segs=5))
q0 = e.q
e.q = 0.45
e.boots(white, top=0.86, sole=(white_d, 0.012), off=0.010, toe=0.004)
e.q = q0

# ---- 큰 흰 날개 (전투 판과 같은 엘다인 날개)
fairy.wings(e, span=0.52, height=0.22, sweep=22.0, raise_=2.0, prim=4, cov=2, color="#ffffff", color2="#c8daf3",
            z=wz + 0.080 * k, style="feather")

e.finalize()


# ---- 잎 가지 (별도 노드 branch): 흰 꽃 + 딸기 + 긴 잎. 로컬: 원점 = 파지점, 줄기 = +Z(위), 꽃 쪽 = +Z
def branch():
    S = k
    b = Buf()
    w = {}
    stem = M_("nc_stem", "#5f9a55")
    loft(b, [{"c": V((0, 0, -0.06 * S)), "rx": 0.006 * S, "ry": 0.006 * S, "w": w},
             {"c": V((0, 0.004 * S, 0.12 * S)), "rx": 0.005 * S, "ry": 0.005 * S, "w": w},
             {"c": V((0, 0.010 * S, 0.24 * S)), "rx": 0.004 * S, "ry": 0.004 * S, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=stem)
    for i, (z, ang, ln) in enumerate(((0.10, 30.0, 0.16), (0.14, -36.0, 0.15), (0.06, 150.0, 0.13),
                                      (0.18, -150.0, 0.12))):
        Ml = Matrix.Translation(V((0, 0, z * S))) @ Matrix.Rotation(math.radians(ang), 4, "Z") @ \
            Matrix.Rotation(math.radians(-58), 4, "Y")
        c2.prism(b, [(x * S, zz * S) for x, zz in c3.leaf_poly(ln, 0.030, n=6, tip=1.1)], 0.003 * S, Ml,
                 mat=green_d if i % 2 else green, w=w)
    top = V((0, 0.010 * S, 0.24 * S))
    petals = []
    for t in range(20):
        a = 2 * math.pi * t / 20 + math.pi / 2
        rr = 0.030 * S * (0.55 + 0.45 * abs(math.cos(5 * (a - math.pi / 2) / 2)) ** 0.7)
        petals.append((rr * math.cos(a), rr * math.sin(a)))
    Mf = Matrix.Translation(top) @ frame(V((0, -1, 0.4)), V((0, 0.4, 1)))
    c2.prism(b, petals, 0.004 * S, Mf, mat=white, w=w)
    disc(b, Mf @ V((0, -0.004 * S, 0)), Mf.to_3x3() @ V((0, -1, 0)), Mf.to_3x3() @ V((0, 0, 1)), 0.009 * S,
         0.009 * S, 0.002 * S, segs=8, mat=flower_c, w=w)
    sb = V((0.020 * S, -0.006 * S, 0.200 * S))
    c2.ellipsoid(b, sb, V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), 0.016 * S, 0.013 * S, 0.013 * S, segs=8, rings=5,
                 mat=red, w=w)
    c2.prism(b, c2.star_poly(0.012 * S, 0.005 * S, n=5, rot=90.0), 0.002 * S,
             Matrix.Translation(sb + V((0, 0, 0.015 * S))) @ frame(V((0, 0, 1)), V((0, 1, 0))), mat=green, w=w)
    return b.obj("ner_coronation_branch_geo", angle=35.0)


br_ob = branch()
sock = bpy.data.objects["socket_hand_R"]
pos = sock.matrix_world.translation.copy()
Zd = V((-0.25, -0.35, 1.0)).normalized()        # 줄기는 위·앞·바깥으로 비스듬히
Yd = V((0.0, -1.0, 0.0))
Yd = (Yd - Zd * Yd.dot(Zd)).normalized()
Xd = Yd.cross(Zd).normalized()
Mw = Matrix((Xd, Yd, Zd)).transposed().to_4x4()
Mw.translation = pos
c3.socket_prop(e, br_ob, "socket_hand_R", Mw, name="branch", outline=0.0025)

e.export("characters/ner_coronation.glb")
