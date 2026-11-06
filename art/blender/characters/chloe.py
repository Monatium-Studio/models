"""클로에: 요정 왕국의 재단사 요정(영원살이). 에필로그 에르핀 3차 대관식의 하객.

원작: 에르핀의 대관식 복장(사복 「왕관의 주인공」)과 네르의 「왕관의 수여자」를 무료로 만들어 주었고, 골디와 함께
에르피엔 소상공회의 대관식 후원을 이끌었다(「엘리아스 침공전」, 「에르핀(왕도)」 문서). 요정이지만 종족 특유의 날개가 없다.
근거: docs/art/characters-cameo3.md.
- 식별 요소: 발목까지 오는 아주 연한 금발(이마를 드러낸 가운데 가르마, 얼굴 양옆으로 늘어져 끝이 바깥으로 말리는 긴
  다발, 진주 구슬), 별 동공이 든 붉은 주황 눈과 'ω' 입, 캐릭터 왼쪽(+X) 볼의 별 문양, 머리 위의 거대한 흰 곰 인형
  '세바스티안'(하트 볼, 박음질 선, 청록 귀, 분홍 퀼팅 뿔, 보라 하트 고리, 색색 고리 사슬, 바닥까지 늘어진 몸과 분홍 퀼팅
  팔), 흰 털 테두리의 노란 코트(보라 안감), 크림 원피스, 갈색·크림 줄무늬 큰 리본과 분홍 보석 금 브로치, 흰 프릴 속바지,
  허벅지·발목 털 띠, 갈색 리본의 노란 신. 날개 없음.
- 재해석: 원작은 두 팔로 인형을 머리 위에 받쳐 들지만, A 포즈 모델이라 인형을 머리 위에 얹었다(별도 노드 chloe_doll:
  장면에 따라 숨길 수 있다). [오리지널] 재단사 표식으로 목에 줄자를 걸고 오른손에 금색 재단 가위(별도 노드
  chloe_scissors)를 쥐었다(원작 좋아하는 것: 재봉도구).
- 체형: 원작 디자인이 아이 같은 체형이라 bust=0.
- 표정: 키트 5종 + proud(재단사의 자부심: 반쯤 내린 눈과 'ω'), grin(별 눈의 이 드러낸 웃음, 원작 소개), pout(뾰로통),
  dazzled(새 옷감을 본 반짝이는 눈) + blink 교정 키.

npm run model -- art/blender/characters/chloe.py
npm run shot -- characters/chloe.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame  # noqa: E402

cb.reset()
e = fairy.Fairy("chloe", ears=None, height=1.12, head=0.45, chest=0.20, hips=1.0, bust=0.0, segs=0.62,
                hand_q=0.40, cheek=0.13)
k = e.k
M_ = elf.mat
yellow = M_("cl_yellow", "#f2c24e")
yellow_d = M_("cl_yellow_d", "#d89a2e")
cream = M_("cl_cream", "#fbf1d6")
white = M_("cl_white", "#ffffff")
fur = M_("cl_fur", "#fffdf8")
purple = M_("cl_purple", "#8a5fb8")
brown = M_("cl_brown", "#7a3e34")
gold = M_("cl_gold", "#f2c84a")
pink_gem = M_("cl_gem", "#e0508a")
pearl = M_("cl_pearl", "#fff8ee")
star_m = M_("cl_star", "#f6cf3e")
doll_w = M_("cl_doll", "#fbf8f6")
doll_d = M_("cl_doll_d", "#e4dcdc")
doll_pink = M_("cl_doll_pink", "#f6a2a6")
doll_heart = M_("cl_doll_heart", "#ee7a86")
doll_eye = M_("cl_doll_eye", "#2a2228")
teal = M_("cl_teal", "#7cc8d0")
quilt = M_("cl_quilt", "#ef9ab0")
quilt_d = M_("cl_quilt_d", "#d27890")
lilac = M_("cl_lilac", "#b39ad8")
chain_cols = [M_("cl_chain_g", "#8ad08a"), M_("cl_chain_y", "#f2d46a"), M_("cl_chain_b", "#7ab8e8")]
tape = M_("cl_tape", "#f6e8a0")

# ---- 얼굴: 별 동공이 든 붉은 주황 눈, 기본 'ω' 입의 자신만만한 얼굴
fairy.face(e, eye_color="#e8583a", iris_dark="#a82a2a", iris_light="#ffb04a", pupil="#8a1e24",
           lash="#5a2a24", brow="#e0c080", brow_th=0.9, blush="#f7a2a8", blush_size=1.2,
           star="pupil", star_color="#ffd84a", star_size=1.05,
           base={"eye": {"top": 0.022, "ktop": 3.8, "cout": 0.018, "tilt_in": -0.002},
                 "brow": {"ang": -4.0, "dz": 0.070, "arch": 0.003},
                 "mouth": {"w": 0.022, "curve": 0.0030, "wave": 0.0018, "open": 0.0}},
           expr={
               # 재단사의 자부심: 반쯤 내린 눈, 올린 눈썹, 'ω'
               "proud": {"eye": {"top": 0.015, "lift": 0.010, "ktop": 4.6},
                         "brow": {"ang": 6.0, "dz": 0.074, "arch": 0.005},
                         "mouth": {"w": 0.026, "curve": 0.0050, "wave": 0.0020, "open": 0.0}},
               # 별 눈의 이 드러낸 웃음 (원작 소개 이미지)
               "grin": {"eye": {"top": 0.032, "ktop": 2.8},
                        "iris": {"pupil": 1.15},
                        "brow": {"ang": 8.0, "dz": 0.074},
                        "mouth": {"w": 0.040, "curve": 0.0100, "open": 0.0180, "top_arch": -0.0020, "wave": 0.0}},
               # 뾰로통
               "pout": {"eye": {"top": 0.018, "ktop": 4.4, "tilt_in": -0.008},
                        "brow": {"ang": -14.0, "dz": 0.062},
                        "mouth": {"w": 0.016, "curve": -0.0035, "open": 0.0, "top_arch": 0.0020, "wave": 0.0}},
               # 새 옷감을 본 반짝이는 눈
               "dazzled": {"eye": {"top": 0.036, "ktop": 2.4, "bot": 0.058},
                           "iris": {"pupil": 1.25},
                           "brow": {"ang": 14.0, "dz": 0.078, "arch": 0.004},
                           "mouth": {"w": 0.022, "curve": 0.0060, "open": 0.0120, "wave": 0.0}},
           })
# 캐릭터 왼쪽(+X) 볼의 노란 별 문양 (아웃라인 없는 별도 노드)
fb = e.face_builder
cx, cz_ = fb.ex * 1.40, fb.ez - 0.080 * k      # 눈꼬리에서 떨어진 볼 위 (볼터치 바깥 아래)
sp = c2.star_poly(0.016 * k, 0.0070 * k, n=5, rot=90.0, cx=cx, cz=cz_)
c2.face_marks(e, "cheek_star", [[(cx, cz_), sp[i], sp[(i + 1) % len(sp)]] for i in range(len(sp))], star_m,
              off=0.0042)


# ---- 머리 (헤어 v2): 아주 연한 금발, 이마를 드러낸 가운데 가르마, 긴 뒷머리
HAIR, HAIR_D, HAIR_L = "#f8e8b6", "#dcc48a", "#fffaea"


def part_bangs(h, lk):
    """가운데 가르마: 앞머리 다발을 양옆으로 쓸어 넘겨 이마를 드러낸다 (원작)."""
    if lk["region"] == "front":
        mid = (lk["a0"] + lk["a1"]) / 2
        lk["sweep"] = 34.0 if mid > 0 else -34.0
        lk["curl"] = 0.004 * k
        lk["p"] = 2.0
        lk["free"] *= 0.5
        lk["th"] *= 0.45          # 앞 가장자리를 얇게: 이마 위 두꺼운 선반이 보이지 않게


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.10, lock_fn=fairy.lock_edit(part_bangs))
h.cap(front=50, side=-6, back=-46, part=0, segs=14, rows=5)   # 앞 머리선을 가르마 다발 아래로 올림
# 앞머리 없이 가운데 가르마: 이마 위 머리선에서 양옆으로 갈라져 얼굴 옆을 감싸는 다발 (원작)
o = h.off
for s_ in (1, -1):
    h.strand([h.sp(s_ * 4, 58, o * 0.9), h.sp(s_ * 18, 44, o * 1.15), h.sp(s_ * 40, 26, o * 1.20),
              h.sp(s_ * 58, 6, o * 1.10)], 0.070 * k, 0.014 * k, n=12, segs=8,
             taper=[(0, 0.7), (0.3, 1.0), (0.8, 0.85), (1, 0.35)])
h.sides(length=0.12, width=0.070, az=64, curl=0.6, thick=1.05)
h.back(length=0.52, n=7, spread=100)

# 얼굴 양옆으로 늘어진 긴 다발 (발목 높이에서 끝이 바깥·위로 말림) + 진주 구슬
sz = e.shoulder_z
locks = []
for s in (1, -1):
    sd = "L" if s > 0 else "R"
    ctrl = [h.sp(s * 68, 4, h.off * 0.4), h.sp(s * 76, -22, h.off * 1.05),
            V((s * 0.205 * k, 0.020 * k, e.chin - 0.020 * k)), V((s * 0.230 * k, 0.050 * k, sz - 0.100 * k)),
            V((s * 0.250 * k, 0.060 * k, 0.320 * k)), V((s * 0.270 * k, 0.040 * k, 0.110 * k)),
            V((s * 0.330 * k, 0.010 * k, 0.050 * k)), V((s * 0.380 * k, -0.004 * k, 0.090 * k))]
    t = c2.Tail(h, f"hair_lock_{sd}", ctrl, 0.090 * k, 0.050 * k, bones=3, parent="chest", root_bone="head",
                root_t=0.10, t_hold=0.80, root_w=0.80, clumps=((0.30, 0.55, 0.94),), segs=10, n=26)
    locks.append(t)


def pearls(buf):
    for t in locks:
        for u in (0.22, 0.46, 0.70):
            c, T = t.at(u)
            out = V((c.x, 0, 0)).normalized()
            c2.ellipsoid(buf, c + out * (t.width * 0.36), V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), 0.008 * k,
                         0.008 * k, 0.008 * k, segs=6, rings=4, mat=pearl, w=t.w_at(u))
    for az, el in ((40.0, 50.0), (-40.0, 50.0), (60.0, 30.0)):
        p, n = h.path(az, h.s_of_el(az, el), 0.004 * k)
        c2.ellipsoid(buf, p, n, V((1, 0, 0)), V((0, 0, 1)), 0.008 * k, 0.008 * k, 0.008 * k, segs=6, rings=4,
                     mat=pearl, w={"head": 1.0})


e.part("pearls", "head", pearls)
h.shine(el=50, spread=74, n=2, size=1.1)

# ---- 옷: 크림 원피스 + 흰 털 테두리의 노란 코트(앞트임) + 뒤 보라 안감 망토
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(cream, hem=wz - 0.010 * k, collar="stand", collar_mat=white, flare=0.008)
e.sleeves(yellow, length=0.84, off=0.014, flare=0.020, puff=0.010)
for sd in ("L", "R"):
    ch = e.arm_chain(sd)
    rx, ry = e.arm_r(0.84)
    pts = []
    c, T = ch.at(0.84)
    A = (V((0, -1, 0)) - T * V((0, -1, 0)).dot(T)).normalized()
    B = T.cross(A).normalized()
    for i in range(13):
        a = 2 * math.pi * i / 12
        pts.append(c + (A * math.cos(a) + B * math.sin(a)) * (max(rx, ry) + 0.030 * k))
    e.part(f"cuff_fur_{sd}", "arms", lambda buf, pts=pts, ch=ch: ec.bead_tube(
        buf, pts, 0.010 * k, 0.016 * k, 6, segs=6, n_per=3, mat=fur, wfn=lambda q: ch.weights(0.84)))
dress = c2.Shell(e, cream, wz + 0.004 * k, 0.330 * k, off=0.014, th=0.004, skirt=True, rows=5, cols=18,
                 flare=[(0.0, 0.0), (1.0, 0.034)], cover=True)
dress.done("dress")
coat = c2.Shell(e, yellow, e.torso_top - 0.004 * k, 0.300 * k, gap=[(0.0, 22.0), (0.35, 26.0), (1.0, 44.0)],
                off=0.026, th=0.005, skirt=True, rows=9, cols=20, flare=[(0.0, 0.0), (0.4, 0.024), (1.0, 0.070)])
coat.edge_trim(yellow_d, width=0.006, th=0.002, i0=1)
hem = [coat.surface(0.98, lerp(22.0 + 16.0, 360.0 - 38.0, i / 22), 0.008 * k)[0] for i in range(23)]
ec.bead_tube(coat.buf, hem, 0.013 * k, 0.024 * k, 11, segs=6, n_per=3, mat=fur, wfn=lambda q: c2.skirt_w(e, q))
coat.done("coat")
cape = c2.Shell(e, purple, e.torso_top + 0.002 * k, 0.360 * k, gap=96.0, off=0.032, th=0.004, skirt=True,
                shoulder=1.04, rows=8, cols=12, flare=[(0.0, 0.010), (0.4, 0.040), (1.0, 0.090)],
                a_fn=lambda a, u: a + 180.0 - 96.0 + 96.0 if False else a)
cape.done("cape_lining")
# 흰 프릴 속바지 + 허벅지·발목 털 띠 + 노란 신 (갈색 리본)
q0 = e.q
e.q = 0.5
e.pants(white, length=0.20, bag=0.020, blouse=0.0, off=0.012, cuff=(white, 0.010, 0.003))
e.q = q0
for sd in ("L", "R"):
    ch = e.leg_chain(sd)
    for t, r0, r1 in ((0.26, 0.012, 0.020), (0.84, 0.010, 0.016)):  # 털 띠
        c, T = ch.at(t)
        rx, ry = e.leg_r(t)
        A = (V((0, -1, 0)) - T * V((0, -1, 0)).dot(T)).normalized()
        B = T.cross(A).normalized()
        pts = [c + (A * math.cos(2 * math.pi * i / 12) + B * math.sin(2 * math.pi * i / 12)) * (max(rx, ry) + 0.012 * k)
               for i in range(13)]
        e.part(f"leg_fur_{sd}{t}", "body", lambda buf, pts=pts, ch=ch, t=t, r0=r0, r1=r1: ec.bead_tube(
            buf, pts, r0 * k, r1 * k, 6, segs=5, n_per=2, mat=fur, wfn=lambda q: ch.weights(t)))
e.boots(yellow, top=0.90, sole=(yellow_d, 0.012), off=0.012, toe=0.004)
for sd in ("L", "R"):
    a = e.anchor((f"leg_{sd}", 0.96, 0, 0.026 * k))
    e.part(f"shoe_bow_{sd}", "body", lambda buf, a=a: c2.bow_geo(buf, a.matrix(), 0.036 * k, brown, w=a.w,
                                                                    tails=0.5, segs=5))

# ---- 가슴: 갈색·크림 줄무늬 큰 리본 + 분홍 보석 금 브로치 (긴 꼬리)
p_b, n_b = e.torso_point(e.torso_top - 0.016 * k, 0, 0.022 * k)


def chest_bow(buf):
    w = {"neck": 0.2, "chest": 0.8}
    Mx = Matrix.Translation(p_b) @ frame(n_b, (0, 0, 1))
    c2.bow_geo(buf, Mx, 0.120 * k, brown, w=w, tails=1.9, knot_mat=gold, segs=6)
    for sg in (1, -1):      # 날개 위 크림 줄
        c2.ellipsoid(buf, Mx @ V((sg * 0.030 * k, -0.013 * k, 0.000)), Mx.to_3x3() @ V((1, 0, 0)),
                     Mx.to_3x3() @ V((0, 0, 1)), Mx.to_3x3() @ V((0, -1, 0)), 0.014 * k, 0.006 * k, 0.004 * k,
                     segs=6, rings=3, mat=cream, w=w)
    flower = [(0.017 * k * (0.78 + 0.22 * math.cos(6 * a)) * math.cos(a),
               0.017 * k * (0.78 + 0.22 * math.cos(6 * a)) * math.sin(a)) for a in
              [2 * math.pi * i / 24 for i in range(24)]]
    c2.prism(buf, flower, 0.004 * k, Mx @ Matrix.Translation((0, -0.019 * k, 0)), mat=gold, w=w)
    c2.ellipsoid(buf, Mx @ V((0, -0.024 * k, 0)), Mx.to_3x3() @ V((0, 0, 1)), Mx.to_3x3() @ V((1, 0, 0)),
                 Mx.to_3x3() @ V((0, -1, 0)), 0.010 * k, 0.007 * k, 0.004 * k, segs=8, rings=4, mat=pink_gem, w=w)


e.part("chest_bow", "body", chest_bow)


# [오리지널] 목에 건 줄자 (크림 띠, 앞으로 늘어진 두 끝)
def tape_measure(buf):
    w = {"neck": 0.3, "chest": 0.7}
    for sg in (1, -1):
        pts = [e.torso_point(e.torso_top + 0.004 * k, sg * 150, 0.020 * k)[0],
               e.torso_point(e.torso_top - 0.004 * k, sg * 70, 0.030 * k)[0],
               e.torso_point(cz + 0.010 * k, sg * 34, 0.034 * k)[0],
               e.torso_point(wz + 0.004 * k, sg * 30, 0.040 * k)[0]]
        P = elf.catmull(pts, 10)
        nrm = [V((q.x, q.y, 0)).normalized() for q in P]
        ups = []
        for i in range(len(P)):
            d = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
            ups.append(nrm[i].cross(d).normalized())
        elf._loop(buf, P, nrm, ups, 0.012 * k, 0.0015 * k, mat=tape, w=w, closed=False)
    back = [e.torso_point(e.torso_top + 0.004 * k, a, 0.020 * k)[0] for a in range(150, 211, 15)]
    nrm = [V((q.x, q.y, 0)).normalized() for q in back]
    elf._loop(buf, back, nrm, [V((0, 0, 1))] * len(back), 0.012 * k, 0.0015 * k, mat=tape, w=w, closed=False)


e.part("tape_measure", "body", tape_measure)


# ---- 인형 세바스티안 (별도 노드 doll): 머리 위의 흰 곰 머리 + 등 뒤로 늘어진 몸·분홍 퀼팅 팔
def doll(buf):
    wh = {"head": 1.0}
    wc = {"chest": 1.0}
    hc = e.head_c
    C = hc + V((0.0, 0.030 * k, e.hh / 2 + 0.105 * k))     # 아래쪽이 머리카락 정수리에 얹힌다
    RX, RY, RZ = 0.310 * k, 0.225 * k, 0.190 * k
    c2.ellipsoid(buf, C, V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), RZ, RX, RY, segs=16, rings=8, mat=doll_w, w=wh)
    # 주둥이 + 코 + 눈 + 하트 볼
    fr = C + V((0, -RY * 0.92, -RZ * 0.18))
    c2.ellipsoid(buf, fr, V((0, -1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.040 * k, 0.090 * k, 0.062 * k, segs=10,
                 rings=5, mat=doll_w, w=wh)
    c2.ellipsoid(buf, fr + V((0, -0.036 * k, 0.010 * k)), V((0, -1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.012 * k,
                 0.020 * k, 0.014 * k, segs=8, rings=4, mat=doll_eye, w=wh)
    for sg in (1, -1):
        pe = C + V((sg * 0.105 * k, -RY * 0.90, RZ * 0.10))
        c2.ellipsoid(buf, pe, V((0, -1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.008 * k, 0.020 * k, 0.020 * k, segs=8,
                     rings=4, mat=doll_eye, w=wh)
        pc = C + V((sg * 0.205 * k, -RY * 0.72, -RZ * 0.25))
        nc = V((sg * 0.55, -0.80, -0.20)).normalized()
        c2.ellipsoid(buf, pc, nc, V((1, 0, 0)), V((0, 0, 1)), 0.020 * k, 0.062 * k, 0.062 * k, segs=10, rings=4,
                     mat=doll_pink, w=wh)
        c2.prism(buf, [(x * 0.026 * k, z * 0.026 * k) for x, z in
                       [(0, -0.9), (0.6, -0.15), (0.75, 0.35), (0.45, 0.65), (0.0, 0.40), (-0.45, 0.65), (-0.75, 0.35),
                        (-0.6, -0.15)]], 0.003 * k,
                 Matrix.Translation(pc + nc * 0.019 * k) @ frame(nc, (0, 0, 1)), mat=doll_heart, w=wh)
    # 박음질 선 (정수리 가운데 세로 점선)
    for i in range(7):
        a = math.radians(lerp(-70.0, 60.0, i / 6))
        p = C + V((0, -RY * math.cos(a) * 1.0, RZ * math.sin(a) * 1.0)) * 1.004
        nn = V((0, -math.cos(a) / RY, math.sin(a) / RZ)).normalized()
        c3.box12(buf, (0.006 * k, 0.003 * k, 0.020 * k), Matrix.Translation(p) @ frame(nn, (0, math.sin(a), math.cos(a))),
                 doll_d, wh)
    # 귀: 캐릭터 오른쪽(-X) 청록 귀, 왼쪽(+X)은 분홍 퀼팅 뿔
    pe = C + V((-RX * 0.78, 0.020 * k, RZ * 0.62))
    c2.ellipsoid(buf, pe, V((0, 1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.030 * k, 0.078 * k, 0.074 * k, segs=10,
                 rings=4, mat=teal, w=wh)
    horn = []
    for i in range(14):
        t = i / 13
        a = math.radians(lerp(-20.0, 250.0, t))
        r = lerp(0.105, 0.030, t) * k
        horn.append(C + V((RX * 0.70 + 0.060 * k * math.cos(a) * (1 - 0.3 * t), 0.020 * k,
                           RZ * 0.55 + 0.070 * k * math.sin(a) * (1 - 0.3 * t) + 0.030 * k * t)))
    st = []
    for i, q in enumerate(horn):
        t = i / 13
        r = lerp(0.050, 0.010, t ** 0.8) * k * (1.0 + 0.10 * math.sin(i * 1.6))
        st.append({"c": q, "rx": r, "ry": r, "w": wh})
    loft(buf, st, segs=10, cap0="flat", cap1="round", mat=quilt)
    for i in range(1, 12, 2):
        c, _ = horn[i], None
        c2.ellipsoid(buf, c + (c - C).normalized() * st[i]["rx"] * 0.95, V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)),
                     0.006 * k, 0.006 * k, 0.006 * k, segs=6, rings=3, mat=gold, w=wh)
    # 보라 하트 고리 (정수리)
    hp = C + V((-0.040 * k, 0.010 * k, RZ * 0.98))
    pts = []
    for i in range(25):
        a = 2 * math.pi * i / 24
        x = 16 * math.sin(a) ** 3
        z = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append(hp + V((x * 0.0042 * k, 0, (z + 6) * 0.0042 * k)))
    loft(buf, [{"c": q, "rx": 0.009 * k, "ry": 0.009 * k, "w": wh} for q in pts], segs=6, cap0="flat",
         cap1="flat", mat=lilac)
    # 색색 고리 사슬 (분홍 뿔 아래, 캐릭터 왼쪽)
    for i in range(4):
        q = C + V((RX * 0.98 + 0.012 * k * (i % 2), 0.0, RZ * 0.10 - 0.052 * k * i))
        band(buf, q, V((0, 0, 1)), V((1, 0, 0)) if i % 2 == 0 else V((0, 1, 0)), 0.024 * k, 0.016 * k, 0.034 * k,
             0.008 * k, segs=10, mat=chain_cols[i % 3], w=wh)
    # 등 뒤로 바닥까지 늘어진 흰 몸 + 캐릭터 왼쪽 분홍 퀼팅 팔 + 오른쪽 청록 발
    body_pts = [V((0, 0.170 * k, e.torso_top + 0.020 * k)), V((0, 0.200 * k, e.waist_z)), V((0, 0.215 * k, 0.260 * k)),
                V((0, 0.205 * k, 0.040 * k))]
    st = [{"c": q, "rx": r * k, "ry": r * 0.8 * k, "w": wc} for q, r in
          zip(elf.catmull(body_pts, 5)[::1], (0.120, 0.150, 0.165, 0.160, 0.140))]
    loft(buf, st, segs=14, cap0="round", cap1="round", mat=doll_w, cap_len0=0.04 * k, cap_len1=0.04 * k)
    arm = [V((0.200 * k, 0.190 * k, e.torso_top - 0.040 * k)), V((0.310 * k, 0.200 * k, e.waist_z)),
           V((0.330 * k, 0.170 * k, 0.200 * k)), V((0.300 * k, 0.140 * k, 0.050 * k))]
    P = elf.catmull(arm, 6)
    st = [{"c": q, "rx": (0.070 - 0.010 * i / (len(P) - 1)) * k, "ry": 0.060 * k, "w": wc} for i, q in enumerate(P)]
    loft(buf, st, segs=12, cap0="round", cap1="round", mat=quilt, cap_len0=0.03 * k, cap_len1=0.04 * k)
    for i in range(1, len(P) - 1, 2):     # 퀼팅 금 징
        for a in (-60.0, 0.0, 60.0):
            d = V((math.sin(math.radians(a)) * 0.0, -math.cos(math.radians(a)), math.sin(math.radians(a))))
            c2.ellipsoid(buf, P[i] + V((0.0, -0.068 * k * math.cos(math.radians(a)), 0.060 * k * math.sin(math.radians(a)))),
                         V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), 0.006 * k, 0.006 * k, 0.006 * k, segs=6, rings=3,
                         mat=gold, w=wc)
            _ = d


ec.node_part(e, "doll", doll, group="head")

e.finalize()


# ---- 금색 재단 가위 (별도 노드 scissors): 오른손. 로컬: 원점 = 파지점(손잡이 고리), +Y = 날 끝
def scissors():
    S = k
    b = Buf()
    w = {}
    for sg in (1, -1):
        ring = [V((sg * 0.016 * S + 0.012 * S * math.cos(2 * math.pi * i / 12), -0.010 * S,
                   0.012 * S * math.sin(2 * math.pi * i / 12))) for i in range(13)]
        loft(b, [{"c": q, "rx": 0.003 * S, "ry": 0.003 * S, "w": w} for q in ring], segs=6, cap0="flat",
             cap1="flat", mat=gold)
        loft(b, [{"c": V((sg * 0.010 * S, 0.004 * S, 0)), "rx": 0.004 * S, "ry": 0.0025 * S, "w": w,
                  "ref": (0, 0, 1)},
                 {"c": V((sg * 0.002 * S, 0.030 * S, 0)), "rx": 0.006 * S, "ry": 0.0025 * S, "w": w, "ref": (0, 0, 1)},
                 {"c": V((-sg * 0.004 * S, 0.090 * S, 0)), "rx": 0.0015 * S, "ry": 0.0015 * S, "w": w,
                  "ref": (0, 0, 1)}], segs=6, cap0="flat", cap1="flat", mat=M_("cl_steel", "#d8dce4"))
    disc(b, V((0, 0.030 * S, 0.003 * S)), (0, 0, 1), (0, 1, 0), 0.004 * S, 0.004 * S, 0.002 * S, segs=8,
         mat=pink_gem, w=w)
    return b.obj("chloe_scissors_geo", angle=35.0)


sc = scissors()
sock = bpy.data.objects["socket_hand_R"]
bpy.context.view_layer.update()
c3.socket_prop(e, sc, "socket_hand_R", sock.matrix_world.copy(), name="scissors", outline=0.002)

e.export("characters/chloe.glb")
