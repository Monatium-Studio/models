"""골디: 금의 용족. 요정 왕국 에르피엔의 상점·부동산 주인이자 에르피엔 소상인 협회 회원. 엘리아스 침공전 뒤 클로에와 함께
협회를 이끌고 에르핀의 3차 대관식을 후원했다(원작). 이 작품에서는 에필로그 대관식의 귀빈석에 둔다.

원작 골디(트릭컬 리바이브 NPC)의 초상·기억조각 그림을 따른다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 금빛 긴 생머리(옆으로 넘긴 큰 앞머리 다발, 캐릭터 왼쪽 위 경단 + 큰 붉은 리본), 호박색 눈과 활짝 웃는 입,
  머리 위의 금괴 모양 뿔 한 쌍, 짧은 뾰족 귀와 금 술 귀걸이, 흰 부푼 소매와 붉은 몸판(금 테, 목의 금 브로치와 붉은 보석),
  검정·금 지그재그 무늬 넓은 허리띠(캐릭터 왼쪽으로 늘어진 끝자락과 금 술), 금빛 앞자락, 붉은 바지, 금 장화, 금 팔찌,
  금빛 막 날개(관절의 금괴 장식, 손가락 끝 금 추), 크고 굵은 금빛 꼬리, 마름모 머리에 붉은 보석을 박은 금 홀.
- 재해석: 금괴 뿔에 새겨진 원작 글자 문양은 옮기지 않고 기하 각인(테 + 동전 원)으로 바꿨다. 홀은 별도 노드 goldie_scepter
  (socket_hand_R, 로컬: 원점 = 파지점, 자루 = +Z).
- 체형: 성인 상인이지만 원작 그림은 몸판 위 볼륨이 아주 작다 → bust 0.15 (양식화).
- 표정: 키트 5종 + merchant(눈웃음 '고객님!' 영업 미소) + appraise(금을 감정하는 가는 눈) + fluster(허둥지둥)
  + polite(다문 입의 정중한 미소) + blink 교정 키.

npm run model -- art/blender/characters/goldie.py
npm run shot -- characters/goldie.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
import dragon_common as dc  # noqa: E402
from elf import V, Matrix, Buf, band, loft, rbox, disc, lerp, smoothstep, frame  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("goldie", height=1.20, head=0.45, leg=1.0, chest=0.28, bust=0.15, hips=1.02, segs=0.62, hand_q=0.45,
            cheek=0.12, ear_len=0.060, ear_width=0.044, ear_angle=-4.0, ear_sweep=16.0)
k = e.k

# ---- 팔레트 (원작 초상에서 눈으로 뽑음)
HAIR, HAIR_D, HAIR_L = "#f2cb74", "#c99a52", "#ffe8b0"
gold = M_("gd_gold", "#e8b648")
gold_d = M_("gd_gold_d", "#b98326")
gold_l = M_("gd_gold_l", "#f8dc8a")
red = M_("gd_red", "#c63a3e")
red_d = M_("gd_red_d", "#9a2a30")
white = M_("gd_white", "#fbf8f4")
white_d = M_("gd_white_d", "#e6ded6")
black = M_("gd_black", "#2c2830")
gem_red = M_("gd_gem", "#e2334b")
mem = M_("gd_membrane", "#e8bb62")
wbone = M_("gd_wingbone", "#c48a2c")
tail_m = M_("gd_tail", "#e2ad4e")
tail_b = M_("gd_tail_belly", "#f6dc98")

# ---- 얼굴: 호박색 눈, 활짝 웃는 입이 기본, 갈색 눈썹
e.face(eye_color="#f2a72a", iris_dark="#a8601a", iris_light="#ffe38a", pupil="#6a3a10",
       lash="#5a3a26", brow="#a86e34", brow_th=1.05, blush="#f7a2a4", blush_size=1.2,
       base={"eye": {"top": 0.028, "ktop": 3.2},
             "brow": {"ang": 4.0, "dz": 0.068, "arch": 0.004},
             "mouth": {"w": 0.030, "curve": 0.0070, "open": 0.0170, "top_arch": -0.0012}},
       expr={
           # 영업 미소: 눈을 감고 활짝 ("안녕하세요, 고객님!")
           "merchant": {"eye": {"lift": 0.032, "top": 0.026, "kbot": 2.6},
                        "brow": {"ang": 10.0, "dz": 0.072, "arch": 0.005},
                        "mouth": {"w": 0.034, "curve": 0.0090, "open": 0.0200, "top_arch": -0.0015}},
           # 금 감정: 가늘게 뜬 눈, 다문 입꼬리
           "appraise": {"eye": {"top": 0.012, "ktop": 5.4, "tilt_in": -0.006},
                        "brow": {"ang": -10.0, "dz": 0.060},
                        "mouth": {"w": 0.020, "curve": 0.0030, "open": 0.0}},
           # 허둥지둥: 동그란 눈, 안쪽이 올라간 눈썹, 물결 입 (원작 기억조각)
           "fluster": {"eye": {"top": 0.034, "ktop": 2.4, "bot": 0.056},
                       "iris": {"pupil": 0.6},
                       "brow": {"ang": 20.0, "dz": 0.072},
                       "mouth": {"w": 0.022, "curve": -0.0040, "open": 0.0080, "wave": 0.0020}},
           # 정중한 미소: 다문 입
           "polite": {"eye": {"top": 0.022, "lift": 0.008, "ktop": 3.8},
                      "brow": {"ang": 6.0, "dz": 0.068},
                      "mouth": {"w": 0.022, "curve": 0.0060, "open": 0.0}},
       })


# ---- 머리 (헤어 v2): 금빛 긴 생머리, 가르마 캐릭터 왼쪽(+X) → 오른쪽으로 크게 넘긴 앞머리, 왼쪽 위 경단
def soft(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.0
        lk["free"] *= 0.7


h = c2.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.12, lock_fn=c2.lock_edit(soft))
h.cap(front=30, side=-6, back=-46, part=28, segs=16, rows=5)
h.bangs(n=6, spread=60, tip_el=-6, sweep=-22, part=28, jag=0.12, curl=1.2, seed=4.0)
h.sides(length=0.36, width=0.080, az=60, curl=0.4, thick=1.1)
h.back(length=0.46, n=7, spread=98)
h.bun(az=124.0, el=40.0, size=0.084)
o = h.off
# 오른눈(-X) 위로 크게 휘어 내려오는 앞머리 다발 (원작 초상의 큰 스윕)
h.strand([h.sp(24, 40, o * 0.70), h.sp(4, 30, o * 1.18), h.sp(-24, 16, o * 1.34),
          h.sp(-46, 4, o * 1.30) + V((0, -0.004, 0)) * k, h.sp(-64, -12, o * 1.10) + V((-0.006, -0.006, 0)) * k],
         0.088 * k, 0.018 * k, n=16, segs=10, taper=[(0, 0.35), (0.25, 1.0), (0.7, 0.8), (1, 0.0)])
h.shine(el=50, spread=74, n=2, size=1.15)

# ---- 금괴 뿔 한 쌍 (머리 위, 바깥으로 살짝 기움) + 기하 각인 [오리지널: 원작 글자 문양 대신]


def ingot_horns(buf):
    w = {"head": 1.0}
    for s, az, tilt in ((1, 34.0, 14.0), (-1, -40.0, -10.0)):
        p, nn = h.path(az, h.s_of_el(az, 54.0), -0.006 * k)
        up = (nn * 0.55 + V((0, 0, 1)) * 0.45).normalized()
        out = V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0.0))
        fwd = (out - up * out.dot(up)).normalized()
        Mx = Matrix.Translation(p) @ frame(fwd, up) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
        Wb, Wt, D, H = 0.090 * k, 0.068 * k, 0.036 * k, 0.110 * k
        # 사다리꼴 금괴 (아래가 넓다): 2D 윤곽을 앞뒤(로컬 Y)로 돌출
        poly = [(-Wb / 2, 0.0), (Wb / 2, 0.0), (Wt / 2, H), (-Wt / 2, H)]
        c2.prism(buf, poly, D, Mx @ Matrix.Translation((0, D / 2, 0)), mat=gold, w=w, chamfer=0.004 * k)
        # 앞면 각인: 테두리 + 동전 원 (짙은 금)
        Mf = Mx @ Matrix.Translation((0, -D / 2 - 0.0005 * k, 0))
        c2.prism(buf, [(-Wt * 0.36, H * 0.16), (Wt * 0.36, H * 0.16), (Wt * 0.30, H * 0.86), (-Wt * 0.30, H * 0.86)],
                 0.0012 * k, Mf, mat=gold_d, w=w)
        disc(buf, Mf @ V((0, -0.0014 * k, H * 0.52)), Mf.to_3x3() @ V((0, -1, 0)), Mf.to_3x3() @ V((0, 0, 1)),
             0.016 * k, 0.016 * k, 0.0014 * k, segs=12, mat=gold_l, w=w)
        disc(buf, Mf @ V((0, -0.0029 * k, H * 0.52)), Mf.to_3x3() @ V((0, -1, 0)), Mf.to_3x3() @ V((0, 0, 1)),
             0.006 * k, 0.006 * k, 0.0010 * k, segs=6, mat=gold_d, w=w)


e.part("ingot_horns", "head", ingot_horns)


# ---- 경단 아래 큰 붉은 리본 (캐릭터 왼쪽 뒤) + 금 술 귀걸이 (양쪽)
def ribbon_earrings(buf):
    w = {"head": 1.0}
    p, nn = h.path(98.0, h.s_of_el(98.0, 22.0), 0.020 * k)
    nn = (nn + V((0, -0.35, 0))).normalized()          # 옆·앞을 보게 (정면에서 리본이 읽힌다)
    Mr = Matrix.Translation(p) @ frame(nn, (0, 0, 1)) @ Matrix.Rotation(math.radians(-24), 4, "Y")
    c2.bow_geo(buf, Mr, 0.170 * k, red, w=w, tails=1.2, knot_mat=red_d, segs=7)
    for sd in ("L", "R"):
        eb, et = e._ear_axis(sd)
        hook = eb.lerp(et, 0.35) + V((0, -0.002 * k, -0.010 * k))
        for i, dx in enumerate((-0.006, 0.0, 0.006)):
            top = hook + V((dx * k, 0, 0))
            ln = (0.022 if i == 1 else 0.016) * k
            loft(buf, [{"c": top, "rx": 0.0028 * k, "ry": 0.0028 * k, "w": w},
                       {"c": top - V((0, 0, ln)), "rx": 0.0034 * k, "ry": 0.0034 * k, "w": w}], segs=6,
                 cap0="round", cap1="round", mat=gold)


e.part("ribbon_earrings", "head", ribbon_earrings)

# ---- 상의: 붉은 몸판(금 여밈 띠, 금 테) + 흰 부푼 소매 + 금 팔찌
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(red, hem=wz - 0.006 * k, collar="stand", collar_mat=white, flare=0.008, placket=gold)
e.sleeves(white, length=0.86, off=0.012, flare=0.012, puff=0.020, cuff=(white_d, 0.014, 0.004))
for sd in ("L", "R"):
    e.ring(gold, f"arm_{sd}", 0.86, h=0.018, th=0.005, off=0.022, name=f"bracelet_{sd}")
    e.ring(gold_d, f"arm_{sd}", 0.90, h=0.006, th=0.004, off=0.024, name=f"bracelet_b_{sd}")
# 몸판 어깨 금 테 (진동 둘레)
for s in (1, -1):
    e.strap(gold, [("torso", e.torso_top - 0.004 * k, s * 40, 0.0115 * k), ("torso", sz - 0.010 * k, s * 66, 0.012 * k),
                   ("torso", sz - 0.050 * k, s * 86, 0.012 * k)], width=0.006, th=0.002,
            name=f"armhole_{'L' if s > 0 else 'R'}")
# 목의 금 브로치 + 붉은 보석
p_b, n_b = e.torso_point(e.torso_top - 0.010 * k, 0, 0.016 * k)


def brooch(buf):
    w = {"neck": 0.3, "chest": 0.7}
    Mx = Matrix.Translation(p_b) @ frame(n_b, (0, 0, 1))
    for i in range(4):
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.020, 0.014, n=4)], 0.003 * k,
                 Mx @ Matrix.Rotation(math.radians(45 + 90 * i), 4, "Y"), mat=gold, w=w)
    c3.gem_drop(buf, Mx @ Matrix.Translation((0, -0.003 * k, 0.0)), 0.009 * k, gem_red, depth=0.005 * k,
                frame_mat=gold_d, frame_w=0.0025 * k, w=w)


e.part("brooch", "body", brooch)

# ---- 하의: 붉은 바지 + 금빛 앞자락(앞 가운데가 트여 붉은 바지가 보임, 짙은 금 무늬 테) + 금 장화
e.pants(red, length=0.86, bag=0.010, blouse=0.008, off=0.012)
apron = c2.Shell(e, gold, wz + 0.004 * k, 0.300 * k, gap=[(0.0, 4.0), (0.5, 10.0), (1.0, 18.0)], off=0.022, th=0.004,
                 skirt=True, rows=6, cols=22, flare=[(0.0, 0.0), (0.5, 0.016), (1.0, 0.036)], ruffle=(0.004, 8, 0.6))
apron.edge_trim(gold_d, width=0.010, th=0.002, i0=1).hem_trim(gold_d, width=0.014, th=0.002)
# 앞자락 무늬: 짙은 금 쐐기 판 (양쪽 앞)
for a_ in (-34.0, 34.0, -70.0, 70.0):
    pc, pn = apron.surface(0.62, a_, 0.003 * k)
    c2.prism(apron.buf, [(-0.016 * k, 0.012 * k), (0.016 * k, 0.012 * k), (0.0, -0.022 * k)], 0.002 * k,
             Matrix.Translation(pc) @ frame(pn, (0, 0, 1)), mat=gold_d, w=c2.skirt_w(e, pc))
apron.done("apron")
e.boots(gold, top=0.86, sole=(gold_d, 0.014), cuff=gold_d, off=0.012, toe=0.006)

# ---- 검정·금 지그재그 무늬 넓은 허리띠 + 캐릭터 왼쪽으로 늘어진 끝자락(금 테, 금 술)
e.ring(black, "torso", wz + 0.002 * k, h=0.050, th=0.006, off=0.030, name="sash")
for dz in (0.022, -0.022):
    e.ring(gold, "torso", wz + 0.002 * k + dz * k, h=0.006, th=0.003, off=0.036, name=f"sash_edge{dz}")
zig = []
for i in range(19):
    a_ = lerp(-100.0, 100.0, i / 18)
    zig.append(("torso", wz + 0.002 * k + (0.010 if i % 2 == 0 else -0.010) * k, a_, 0.037 * k))
e.strap(gold, zig, width=0.0045, th=0.0015, name="sash_zig")


def sash_tail(buf):
    pts, nrm, ups = [], [], []
    for i in range(7):
        t = i / 6
        z = lerp(wz - 0.010 * k, 0.330 * k, t)
        a_ = lerp(44.0, 58.0, t)
        p, n = e.torso_point(min(z, wz), a_, 0.040 * k + 0.012 * k * t)
        if z < wz:
            p = V((p.x + 0.010 * k * t, p.y - 0.006 * k * t, z))
        pts.append(p)
        nrm.append(n)
        ups.append(V((0, 0, 1)))
    ws = [c2.skirt_w(e, q) for q in pts]
    side = [nrm[i].cross(ups[i]).normalized() for i in range(len(pts))]
    elf._loop(buf, pts, nrm, side, 0.050 * k, 0.004 * k, mat=black, closed=False,
              w=lambda tt: ws[min(int(round(tt * 6)), 6)])
    for sg in (1, -1):    # 금 테두리 (양 가장자리)
        edge = [q + s_ * (sg * 0.024 * k) + nn * 0.0025 * k for q, s_, nn in zip(pts, side, nrm)]
        elf._loop(buf, edge, nrm, side, 0.005 * k, 0.002 * k, mat=gold, closed=False,
                  w=lambda tt: ws[min(int(round(tt * 6)), 6)])
    for i in range(1, 6):    # 금 지그재그 가로 줄
        q = pts[i] + nrm[i] * 0.0028 * k
        c2.prism(buf, [(-0.018 * k, 0.0), (0.0, 0.010 * k), (0.018 * k, 0.0), (0.0, 0.004 * k)], 0.0012 * k,
                 Matrix.Translation(q) @ frame(nrm[i], (0, 0, 1)), mat=gold, w=ws[i])
    # 끝 금 술
    tipp = pts[-1] - V((0, 0, 0.006 * k))
    for j in range(5):
        x = (j - 2) * 0.010 * k
        b0 = tipp + side[-1] * x
        loft(buf, [{"c": b0, "rx": 0.003 * k, "ry": 0.003 * k, "w": ws[-1]},
                   {"c": b0 - V((0, 0, 0.026 * k)), "rx": 0.0018 * k, "ry": 0.0018 * k, "w": ws[-1]}], segs=5,
             cap0="flat", cap1="round", mat=gold_l)


e.part("sash_tail", "body", sash_tail)

# ---- 금빛 막 날개 + 관절 금괴 장식 + 손가락 끝 금 추
WS, WH = 0.46, 0.36
wm = dc.wings(e, span=WS, height=WH, mem=mem, bone=wbone, angle=136.0, sweep=14.0, raise_=10.0,
              z=e.chest_z + 0.050 * k, spar=0.0105)


def wing_gold(buf):
    L, H = WS * k, WH * k
    for sd, Mw in wm.items():
        R3 = Mw.to_3x3()
        up = (R3 @ V((0.0, 0.0, 1.0))).normalized()
        out = (R3 @ V((1.0, 0.0, 0.0))).normalized()
        nrm = (R3 @ V((0.0, -1.0, 0.0))).normalized()
        # 팔 위 금괴 장식 (팔꿈치·손목·팔 중간)
        for (x, z), bn, sc in (((0.30, 0.52), f"wing_{sd}_01", 1.0), ((0.58, 0.96), f"wing_{sd}_02", 1.1),
                               ((0.44, 0.74), f"wing_{sd}_02", 0.8)):
            c = Mw @ V((x * L, 0.0, z * H))
            Mx = Matrix.Translation(c) @ frame(nrm, up)
            rbox(buf, (0.040 * k * sc, 0.024 * k * sc, 0.030 * k * sc), Mx, mat=gold, w={bn: 1.0}, r=0.2, segs=1)
        # 손가락 끝 금 추 (막대 + 뾰족 추)
        for i, (x, z) in enumerate(((1.00, 0.62), (0.86, 0.04), (0.50, -0.30))):
            c = Mw @ V((x * L, 0.0, z * H))
            bn = f"wing_{sd}_f{i + 1}"
            w = {bn: 1.0}
            loft(buf, [{"c": c, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
                       {"c": c - V((0, 0, 0.040 * k)), "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w}], segs=5,
                 cap0="flat", cap1="flat", mat=gold_d)
            loft(buf, [{"c": c - V((0, 0, 0.040 * k)), "rx": 0.0090 * k, "ry": 0.0090 * k, "w": w},
                       {"c": c - V((0, 0, 0.052 * k)), "rx": 0.0100 * k, "ry": 0.0100 * k, "w": w},
                       {"c": c - V((0, 0, 0.078 * k)), "rx": 0.0008 * k, "ry": 0.0008 * k, "w": w}], segs=6,
                 cap0="flat", cap1="flat", mat=gold)
        _ = out


e.part("wing_gold", "body", wing_gold)

# ---- 크고 굵은 금빛 꼬리: 엉덩이 뒤에서 아래로, 캐릭터 왼쪽 옆으로 크게 말린다
bp, bn_ = e.torso_point(hz + 0.030 * k, 180.0, -0.012 * k)
ctrl = [bp,
        bp + V((0.0, 0.080 * k, -0.080 * k)),
        V((0.040 * k, bp.y + 0.150 * k, 0.140 * k)),
        V((0.150 * k, bp.y + 0.200 * k, 0.070 * k)),
        V((0.270 * k, bp.y + 0.150 * k, 0.060 * k)),
        V((0.340 * k, bp.y + 0.060 * k, 0.110 * k)),
        V((0.350 * k, bp.y - 0.010 * k, 0.190 * k))]
dc.tail(e, ctrl, 0.088, mat=tail_m, belly=tail_b, r1=0.020, bones=4, segs=10, n=20)

e.finalize()


# ---- 금 홀 (별도 노드 scepter): 금 자루 + 감은 띠 + 마름모 머리(붉은 보석) + 아래 구슬 고리
def scepter():
    S = k
    b = Buf()
    w = {}
    loft(b, [{"c": V((0, 0, -0.10 * S)), "rx": 0.009 * S, "ry": 0.009 * S, "w": w},
             {"c": V((0, 0, 0.30 * S)), "rx": 0.009 * S, "ry": 0.009 * S, "w": w}], segs=8, cap0="round",
         cap1="flat", mat=gold)
    for z in (-0.06, -0.02, 0.18, 0.26):
        loft(b, [{"c": V((0, 0, (z - 0.008) * S)), "rx": 0.0125 * S, "ry": 0.0125 * S, "w": w},
                 {"c": V((0, 0, (z + 0.008) * S)), "rx": 0.0125 * S, "ry": 0.0125 * S, "w": w}], segs=8,
             cap0="flat", cap1="flat", mat=gold_d)
    for i in range(6):    # 구슬 고리
        a = 2 * math.pi * i / 6
        c2.ellipsoid(b, V((math.cos(a) * 0.014 * S, math.sin(a) * 0.014 * S, 0.30 * S)), V((0, 0, 1)), V((1, 0, 0)),
                     V((0, 1, 0)), 0.006 * S, 0.006 * S, 0.006 * S, segs=6, rings=4, mat=gold_l, w=w)
    # 마름모 머리 (앞뒤 두께) + 붉은 보석
    Mh = Matrix.Translation(V((0, 0, 0.36 * S))) @ frame(V((0, -1, 0)), (0, 0, 1))
    c2.prism(b, [(0.0, -0.060 * S), (0.044 * S, 0.0), (0.0, 0.060 * S), (-0.044 * S, 0.0)], 0.018 * S,
             Mh @ Matrix.Translation((0, 0.009 * S, 0)), mat=gold, w=w, chamfer=0.004 * S)
    c2.prism(b, [(0.0, -0.040 * S), (0.028 * S, 0.0), (0.0, 0.040 * S), (-0.028 * S, 0.0)], 0.003 * S,
             Mh @ Matrix.Translation((0, -0.009 * S, 0)), mat=gold_d, w=w)
    c3.gem_drop(b, Mh @ Matrix.Translation((0, -0.012 * S, 0.0)), 0.014 * S, gem_red, depth=0.005 * S, w=w)
    c3.gem_drop(b, Matrix.Translation(V((0, 0.009 * S, 0.36 * S))) @ frame(V((0, 1, 0)), (0, 0, 1)), 0.014 * S,
                gem_red, depth=0.005 * S, w=w)
    return b.obj("goldie_scepter_geo", angle=35.0)


sc = scepter()
sock = bpy.data.objects["socket_hand_R"]
bpy.context.view_layer.update()
# 손 소켓 로컬(+Y 손가락, +Z 엄지 쪽)에서 자루(+Z)가 엄지 쪽으로 서게: 원작 초상처럼 비스듬히 든다
Mw = sock.matrix_world @ Matrix.Rotation(math.radians(-50.0), 4, "X")
c3.socket_prop(e, sc, "socket_hand_R", Mw, name="scepter", outline=0.003)

e.export("characters/goldie.glb")
