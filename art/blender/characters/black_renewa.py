"""흑뉴아 (리뉴아/R41): R41 침공군 수장. 리타가 절대 이길 수 없는 존재.

원작 리뉴아(R41)의 외형을 바탕으로 한 카메오 모델. 원작 외형이 먼저이고, R41 장비는 개정된
docs/art/r41-style.md의 팔레트(제국 흑 #2a2733, 시그널 마젠타 발광 #ff4fd8)와 차가운 보라 먹선을 따른다.
- 유지한 식별 요소: 흰 머리에 왼쪽 앞머리의 마젠타 브릿지(왼눈을 덮음), 끝이 마젠타로 물드는 긴 낮은 트윈테일,
  바보털, 붉은 눈과 반쯤 감은 냉소적인 눈매, 머리 뒤에서 솟은 검은 판 모양 뿔 헤드기어 한 쌍(마젠타 줄),
  검은 호흡 마스크(볼의 마젠타 고리), 어깨를 드러낸 검은 바디슈트와 초커, 긴 검은 장갑, 왼팔의 갈퀴 건틀릿
  (마젠타 고리 표시등), 허벅지까지 오는 검은 장갑 부츠(무릎의 마젠타 화살촉 문양, 종아리 뒤 마젠타 결정).
- 재해석: 하이컷 레오타드는 짧은 반바지형 바디슈트로 바꿨다. 헤드기어·마스크·건틀릿·부츠 장갑은 R41 형태
  언어(45° 모따기 판, 짧은 발광 막대)로 다시 그렸고 원작 문양은 옮기지 않았다. 키 1.30 m + 뿔로 다른 엘프보다 크다.
- 노드: black_renewa_mask(마스크, 숨기면 맨얼굴 연출), black_renewa_gear_*(R41 장비, 보라 먹선), black_renewa_marks
  (볼의 마젠타 표식, noOutline). 마스크를 벗긴 장면에서 표정을 쓴다.
- 표정: 기본이 무표정(차가운 반쯤 감은 눈) + 키트 5종 + sneer(비웃음), rage(분노) + blink 교정 키.
근거: docs/art/characters-cameo.md

npm run model -- art/blender/characters/black_renewa.py
npm run shot -- characters/black_renewa.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo  # noqa: E402
import r41  # noqa: E402  (팔레트·먹선 값만 읽는다)
from elf import V, Matrix, Buf  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("black_renewa", height=1.30, leg=1.12, chest=0.55, bust=0.50, hips=1.08, limb=0.95, segs=0.78, hand_q=0.7,
            cheek=0.07)
k = e.k
P, L = r41.PAL, r41.LINE

# ---- 팔레트
suit = M_("br_suit", "#26232c")            # 바디슈트 천 (원작 실측 검정에 보랏빛)
suit_d = M_("br_suit_d", "#3a3642")
skin_mark = M_("br_mark", "#ffffff", emission=P["glow"], unlit=True)
# R41 장비: 따로 남기는 메시라 머티리얼 lineColor(차가운 보라 먹선)가 살아 있다
shell = cb.mat("br_shell", P["shell"], line=L["shell"], roughness=0.4)
metal = cb.mat("br_metal", P["metal"], line=L["metal"], roughness=0.4)
rubber = cb.mat("br_rubber", P["rubber"], line=L["rubber"])
glow = cb.mat("br_glow", P["glow"], emission=P["glow"], unlit=True)
crystal = cb.mat("br_crystal", "#ff7be4", emission="#ff7be4", unlit=True)

# ---- 얼굴: 붉은 눈, 차갑게 반쯤 감은 눈 (기본 = 무표정)
e.face(eye_color="#c41a2c", iris_dark="#4e0610", iris_light="#ff8a8a", pupil="#22040a",
       lash="#2a2228", brow="#7c7486", brow_th=1.1, blush="#f3b1b6", blush_size=0.75,
       base={"eye": {"top": 0.013, "ktop": 5.2, "tilt_in": -0.008, "tilt_out": 0.003, "bot": 0.048, "cout": 0.017},
             "iris": {"pupil": 0.85},
             "brow": {"ang": -10.0, "dz": 0.058, "arch": 0.0},
             "mouth": {"w": 0.017, "curve": -0.0004}},
       expr={
           # 분노: 눈을 치켜뜨고 동공이 작아지며 이를 드러내듯 입을 벌린다
           "rage": {"eye": {"top": 0.027, "ktop": 3.4, "tilt_in": -0.017, "tilt_out": 0.004},
                    "iris": {"pupil": 0.55},
                    "brow": {"ang": -26.0, "dz": 0.052, "th": 0.0074},
                    "mouth": {"w": 0.031, "open": 0.017, "curve": -0.0060, "top_arch": -0.002, "wave": 0.0010}},
       })
# 비웃음: 한쪽 입꼬리만 올리고 눈을 더 가늘게, 한쪽 눈썹을 치켜든다
cameo.face_expr(e, "sneer",
                both={"eye": {"top": 0.012, "lift": 0.010, "ktop": 5.0},
                      "mouth": {"w": 0.030, "curve": 0.0040, "open": 0.0035}},
                L={"brow": {"dz": 0.066, "ang": -4.0, "arch": 0.004}},
                R={"brow": {"dz": 0.054, "ang": -16.0}},
                corner=(0.0090, -0.0022), mouth_dx=0.0030 * k)

# ---- 머리 (헤어 v2): 흰 머리, 왼눈을 덮는 큰 앞머리와 마젠타 브릿지, 바보털, 끝이 마젠타로 물드는 긴 낮은 트윈테일
WHITE = "#ece8ef"
h = e.hair(WHITE, dark="#c9c2d0", light="#ffffff")
mag = M_("br_hair_mag", "#d354c4")
h.cap(front=28, side=-6, back=-46, part=-14, segs=18, rows=5)   # 예산: 셸을 조금 성글게
h.bangs(n=7, spread=56, tip_el=-5, sweep=10, part=-16, jag=0.35, seed=4.0)
o = h.off
# 왼눈(+X) 위로 쓸어내린 큰 앞머리 + 그 위의 마젠타 브릿지 (셸 바깥에 얹는 다발, 브릿지는 mat=)
cameo.strand(h, [h.sp(-12, 72, o * 0.5), h.sp(14, 46, o * 1.30), h.sp(30, 18, o * 1.40), h.sp(40, -6, o * 1.20),
                 h.sp(46, -22, o * 0.95)], 0.088 * k, 0.022 * k, n=12, segs=8,
             taper=[(0, 0.7), (0.3, 1.0), (0.75, 0.75), (1, 0.0)])
cameo.strand(h, [h.sp(12, 50, o * 1.45), h.sp(22, 38, o * 1.74), h.sp(34, 16, o * 1.82), h.sp(42, -4, o * 1.58),
                 h.sp(47, -16, o * 1.25)], 0.050 * k, 0.014 * k, n=12, segs=8, mat=mag,
             taper=[(0, 0.3), (0.25, 1.0), (0.8, 0.7), (1, 0.0)])
h.sides(length=0.05, width=0.068, puff=1.6)
h.back(length=0.03, n=7)
cameo.ahoge(h, az=-6, height=0.10, curl=1.5, width=0.022)

# 트윈테일: 귀 뒤 턱 높이에서 묶어(묶은 자리는 옆머리 안에 묻힌다) 어깨·팔 뒤로 늘어져 무릎 높이에서 끝이 바깥으로 말린다.
# 한 덩어리 볼륨 + 끝 다발 3개, 본 3개 (hair_tail_L/R_01..03). 끝 색은 finalize 뒤 정점색 그라데이션.
tails = []
sz = e.shoulder_z
for s in (1, -1):
    base, nb = h.path(s * 118.0, h.s_of_el(s * 118.0, -16.0))
    ctrl = [base - nb * 0.030 * k, base + nb * 0.016 * k,
            base + nb * 0.036 * k + V((0, 0, -0.050)) * k,
            V((s * 0.212, 0.124, e.torso_top / k - 0.010)) * k,
            V((s * 0.236, 0.112, sz / k - 0.13)) * k,
            V((s * 0.266, 0.090, sz / k - 0.29)) * k,
            V((s * 0.300, 0.064, 0.250)) * k,
            V((s * 0.330, 0.044, 0.205)) * k]
    tl = cameo.Tail(e, h, f"hair_tail_{'L' if s > 0 else 'R'}", ctrl, width=0.112 * k, thick=0.080 * k,
                    lat=(s * 0.7, 0.7, 0), bones=3, tie_at=0.045, root=0.72, puff=0.22, hold=0.55, body_end=0.90,
                    ends=3, split=0.70, spread=0.70, end_w=0.46, end_len=(0.93, 1.0, 0.95),
                    curl=(0.80, (s * 0.050 * k, -0.010 * k, 0.030 * k)), tie=None, n=22, segs=10)
    tl.done()
    tails.append(tl)

# ---- 바디슈트: 어깨를 드러낸 상의 + 반바지형 하의, 앞 지퍼선, 엉덩이 끈, 초커
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.pants(suit, length=0.11, bag=0.0, blouse=0.0, off=0.007)
bod = cameo.Shell(e, suit, cz + 0.060 * k, hz + 0.01 * k, off=0.008, th=0.004, cover=True, cols=22)
bod.top_trim(suit_d, width=0.008, th=0.002).done("bodysuit")
e.strap(metal, [("torso", z, 0.0, 0.0125 * k) for z in (cz + 0.050 * k, cz, wz, hz + 0.02 * k)], width=0.004,
        th=0.0015, name="zip")
# 옆 솔기 패널 (허리선을 잡아 주는 짙은 띠)
for sg in (1, -1):
    e.strap(suit_d, [("torso", z, sg * 84, 0.0115 * k) for z in (cz + 0.055 * k, cz, wz - 0.01 * k, hz + 0.02 * k)],
            width=0.016, th=0.0015, name=f"side_panel_{'L' if sg > 0 else 'R'}")
for i, t in enumerate((0.05, 0.10)):
    e.ring(suit_d, "leg_R", t, h=0.008, th=0.003, off=0.010, name=f"hip_strap_{i}")
e.part("choker", "head", lambda buf: elf.band(buf, (0, 0.004 * k, e.torso_top + 0.024 * k), (0, 0, 1), (1, 0, 0),
                                              0.051 * k, 0.046 * k, 0.014 * k, 0.004 * k, segs=16, mat=suit,
                                              w={"neck": 1.0}))

# ---- 긴 장갑 + 허벅지 장갑 부츠
for side in ("L", "R"):
    cameo.arm_tube(e, suit, side, 0.40, 0.985, off=0.006, cap0=None, name=f"long_glove_{side}")
    e.ring(suit_d, f"arm_{side}", 0.41, h=0.014, th=0.003, off=0.008, name=f"glove_band_{side}")
e.gloves(suit, inflate=0.0024)
e.boots(suit, top=0.30, sole=(M_("br_sole", P["rubber"]), 0.020), toe=0.006, off=0.012)

# ---- R41 장비 (따로 남기는 메시: 그룹별로 하나씩)
gear = {"head": Buf(), "arms": Buf(), "body": Buf()}


def head_fin(s):
    """머리 뒤 양옆에서 솟는 판 모양 뿔 (모따기 판 + 마젠타 줄 + 받침)."""
    b = gear["head"]
    w = {"head": 1.0}
    base = h.sp(s * 112, 16, o * 1.6)
    up = V((s * 0.40, 0.16, 1.0)).normalized()
    n0 = V((s, 0, 0))
    n = (n0 - up * n0.dot(up)).normalized()
    Mf = Matrix.Translation(base) @ elf.frame(n, up)
    sx = 1 if s > 0 else -1          # 왼쪽 판은 로컬 +X가 뒤, 오른쪽은 앞 → 모양을 뒤집어 앞 모서리를 맞춘다
    poly = [(-0.034, 0.0), (0.060, 0.0), (0.078, 0.215), (0.050, 0.320), (0.006, 0.280), (-0.028, 0.090)]
    poly = [(sx * x * k, z * k) for x, z in poly]
    if sx < 0:
        poly = list(reversed(poly))
    cameo.prism(b, poly, 0.026 * k, Mf @ Matrix.Translation((0, 0.010 * k, 0)), mat=shell, w=w, chamfer=0.007 * k)
    # 바깥면 마젠타 줄 (판 앞 모서리를 따라 비스듬히)
    a0, a1 = V((sx * 0.012 * k, 0, 0.050 * k)), V((sx * 0.034 * k, 0, 0.262 * k))
    mid = (a0 + a1) / 2
    d = (a1 - a0)
    ang = math.atan2(d.x, d.z)
    Ms = Mf @ Matrix.Translation((mid.x, -0.0175 * k, mid.z)) @ Matrix.Rotation(-ang, 4, "Y")
    cameo.rrbox(b, (0.007 * k, 0.003 * k, d.length), Ms, mat=glow, w=w, r=0.3, segs=1)
    # 받침 (머리에 붙는 모따기 블록)
    cameo.rrbox(b, (0.070 * k, 0.040 * k, 0.050 * k), Mf @ Matrix.Translation((sx * 0.010 * k, 0.012 * k, 0.010 * k)),
                mat=metal, w=w, r=0.18, segs=1)


for s in (1, -1):
    head_fin(s)

# 볼의 마젠타 표식 두 줄 (오른쪽 볼, noOutline 발광)
mk = Buf()
fx = e.face_builder
for j in range(2):
    x0 = -(fx.ex + 0.036 * fx.sz) + (j - 0.5) * 0.010 * k
    zc = fx.ez - 0.044 * fx.sz
    pts = [e.face_project(x0 + dx, zc + dz, 0.0045)[0] for dx, dz in ((-0.0018, -0.010), (0.0018, -0.010),
                                                                       (0.0018, 0.010), (-0.0018, 0.010))]
    ids = [mk.vert(p, {"head": 1.0}) for p in pts]
    mk.face(tuple(ids), skin_mark)
marks = mk.obj("black_renewa_marks", smooth=False)


def mask():
    """아래 얼굴을 덮는 검은 호흡 마스크: 가운데가 솟은 셸 + 볼의 마젠타 고리 필터 + 가운데 능선."""
    b = Buf()
    w = {"head": 1.0}
    xm = 0.102 * k

    def proj(x, z, off):
        """얼굴 정면 투영. 턱 옆에서 광선이 머리를 빗나가면 x를 안쪽으로 당겨 다시 쏜다 (가장자리 가시 방지)."""
        for _ in range(12):
            hit = e.head_bvh.ray_cast(V((x, -2.0, z)), V((0, 1, 0)))
            if hit[0] is not None:
                return hit[0] + hit[1].normalized() * off
            x *= 0.92
        return e.face_project(0.0, z, off)[0]

    ez = fx.ez
    R, C = 7, 13
    outer, inner = [], []
    for i in range(R):
        ro, ri = [], []
        u = i / (R - 1)
        for j in range(C):
            x = lerp_(-xm, xm, j / (C - 1))
            a = abs(x) / xm
            zt = ez - 0.040 * k - 0.012 * k * a * a
            zb = e.chin + 0.010 * k + 0.030 * k * a
            z = lerp_(zt, zb, u)
            bul = 0.010 * k + 0.016 * k * (1 - a * a) * math.sin(math.pi * (0.25 + 0.75 * u))
            p_out = proj(x, z, bul)
            p_in = proj(x, z, 0.004 * k)
            ro.append(b.vert(p_out, w))
            ri.append(b.vert(p_in, w))
        outer.append(ro)
        inner.append(ri)
    for i in range(R - 1):
        for j in range(C - 1):
            b.face((outer[i][j], outer[i + 1][j], outer[i + 1][j + 1], outer[i][j + 1]), shell)
            b.face((inner[i][j], inner[i][j + 1], inner[i + 1][j + 1], inner[i + 1][j]), shell)
    for j in range(C - 1):
        b.face((outer[0][j], outer[0][j + 1], inner[0][j + 1], inner[0][j]), shell)
        b.face((outer[R - 1][j], inner[R - 1][j], inner[R - 1][j + 1], outer[R - 1][j + 1]), shell)
    for i in range(R - 1):
        b.face((outer[i][0], inner[i][0], inner[i + 1][0], outer[i + 1][0]), shell)
        b.face((outer[i][C - 1], outer[i + 1][C - 1], inner[i + 1][C - 1], inner[i][C - 1]), shell)
    # 가운데 능선
    for i in range(R - 3):
        pa = b.v[outer[i][C // 2]]
        pb = b.v[outer[i + 1][C // 2]]
        d = pb - pa
        Mr = Matrix.Translation((pa + pb) / 2 + V((0, -0.002 * k, 0))) @ elf.frame((0, -1, 0), d)
        cameo.rrbox(b, (0.010 * k, 0.006 * k, d.length * 1.15), Mr, mat=metal, w=w, r=0.3, segs=1)
    # 볼 필터: 모따기 원통 + 마젠타 고리 + 검은 점
    for sg in (1, -1):
        x = sg * 0.074 * k
        z = lerp_(ez - 0.048 * k, e.chin + 0.03 * k, 0.45)
        p, nrm = e.face_project(x, z, 0.012 * k)
        nrm = (nrm + V((sg * 0.5, 0, 0))).normalized()
        up = V((0, 0, 1))
        elf.disc(b, p, nrm, up, 0.024 * k, 0.024 * k, 0.010 * k, segs=10, mat=shell, w=w)
        elf.disc(b, p + nrm * 0.010 * k, nrm, up, 0.018 * k, 0.018 * k, 0.0015 * k, segs=10, mat=glow, w=w)
        elf.disc(b, p + nrm * 0.0112 * k, nrm, up, 0.011 * k, 0.011 * k, 0.0015 * k, segs=8, mat=shell, w=w)
    return b.obj("black_renewa_mask", angle=40.0)


def lerp_(a, c, t):
    return a + (c - a) * t


mask_obj = mask()


def gauntlet():
    """왼팔 갈퀴 건틀릿: 팔뚝 모따기 셸 + 팔꿈치 판 + 마젠타 고리 표시등 + 손등 판 + 손가락 갈퀴."""
    b = gear["arms"]
    side = "L"
    ch = e.arm_chain(side)
    st = []
    for i in range(7):
        t = lerp_(0.50, 0.99, i / 6)
        c, tan = ch.at(t)
        rx, ry = e.arm_r(t)
        g = 0.020 * k + 0.010 * k * math.sin(math.pi * (t - 0.5) / 0.5)
        st.append({"c": c, "rx": rx + g, "ry": ry + g, "w": ch.weights(t), "p": 1.7})
    elf.loft(b, st, segs=8, cap0="flat", cap1="flat", mat=shell, ref=(0, -1, 0), p=1.7)
    for t0 in (0.62, 0.86):     # 마디 띠
        c, tan = ch.at(t0)
        rx, ry = e.arm_r(t0)
        elf.band(b, c, tan, (0, -1, 0), rx + 0.028 * k, ry + 0.028 * k, 0.010 * k, 0.003 * k, segs=8, mat=metal,
                 w=ch.weights(t0), p=1.7)
    a = e.anchor(("arm_L", 0.74, 90, 0.034 * k))
    elf.disc(b, a.pos, a.n, a.up, 0.018 * k, 0.018 * k, 0.003 * k, segs=12, mat=glow, w=a.w)
    elf.disc(b, a.pos + a.n * 0.0032 * k, a.n, a.up, 0.012 * k, 0.012 * k, 0.0015 * k, segs=12, mat=shell, w=a.w)
    elf.disc(b, a.pos + a.n * 0.0050 * k, a.n, a.up, 0.005 * k, 0.005 * k, 0.0015 * k, segs=8, mat=glow, w=a.w)
    # 팔꿈치 판
    a2 = e.anchor(("arm_L", 0.48, 180, 0.020 * k))
    cameo.prism(b, [(-0.026 * k, -0.02 * k), (0.026 * k, -0.02 * k), (0.018 * k, 0.04 * k), (-0.018 * k, 0.04 * k)],
                0.014 * k, a2.matrix(), mat=shell, w=a2.w, chamfer=0.004 * k)
    # 손등 판 + 손가락 갈퀴 (손가락 본에 강체)
    W, Ld, Pn = e.W[side], e.adir[side], e.palm_n[side]
    back_n = -Pn
    hb = {f"hand_{side}": 1.0}
    Mh = Matrix.Translation(W + Ld * (e.hand_len * 0.55) + back_n * 0.020 * k) @ elf.frame(back_n, Ld)
    cameo.rrbox(b, (0.060 * k, 0.012 * k, 0.050 * k), Mh, mat=shell, w=hb, r=0.2, segs=1)
    for nm, base_, mid, tip in e._finger_joints(side):
        if nm == "thumb":
            continue
        d = (tip - mid).normalized()
        wb = {f"{nm}_02_{side}": 1.0}
        st2 = [{"c": mid + back_n * 0.006 * k, "rx": 0.009 * k, "ry": 0.007 * k, "w": wb},
               {"c": tip + d * 0.010 * k + back_n * 0.004 * k, "rx": 0.006 * k, "ry": 0.004 * k, "w": wb},
               {"c": tip + d * 0.032 * k - Pn * 0.004 * k, "rx": 0.0008 * k, "ry": 0.0008 * k, "w": wb}]
        elf.loft(b, st2, segs=6, cap0="flat", cap1="flat", mat=metal, ref=tuple(back_n))


gauntlet()


def boot_armor(side):
    """무릎 판(마젠타 화살촉), 정강이 판, 부츠 윗단 테, 종아리 뒤 마젠타 결정 두 개."""
    b = gear["body"]
    s = 1 if side == "L" else -1
    ch = e.leg_chain(side)
    leg = f"leg_{side}"
    # 부츠 윗단 두꺼운 테
    c, tan = ch.at(0.31)
    rx, ry = e.leg_r(0.31)
    elf.band(b, c, tan, (0, -1, 0), rx + 0.016 * k, ry + 0.016 * k, 0.026 * k, 0.006 * k, segs=10, mat=shell,
             w=ch.weights(0.31), p=1.8)
    # 무릎 판
    a = e.anchor((leg, 0.53, 0, 0.022 * k))
    poly = [(-0.040 * k, -0.034 * k), (0.040 * k, -0.034 * k), (0.046 * k, 0.020 * k), (0.0, 0.060 * k),
            (-0.046 * k, 0.020 * k)]
    cameo.prism(b, poly, 0.022 * k, a.matrix(), mat=shell, w=a.w, chamfer=0.007 * k)
    # 마젠타 화살촉 (아래를 향한 쐐기 두 획)
    Mk = a.matrix(lift=0.0225 * k)
    for sg in (1, -1):
        R_ = Mk @ Matrix.Translation((sg * 0.012 * k, -0.0005 * k, 0.004 * k)) @ \
            Matrix.Rotation(math.radians(sg * 38), 4, "Y")
        cameo.rrbox(b, (0.030 * k, 0.003 * k, 0.008 * k), R_, mat=glow, w=a.w, r=0.3, segs=1)
    # 정강이 판
    a3 = e.anchor((leg, 0.74, 0, 0.020 * k))
    cameo.prism(b, [(-0.030 * k, -0.07 * k), (0.030 * k, -0.07 * k), (0.036 * k, 0.05 * k), (-0.036 * k, 0.05 * k)],
                0.014 * k, a3.matrix(), mat=shell, w=a3.w, chamfer=0.005 * k)
    for j in range(3):          # 정강이 슬릿 3개
        a4 = e.anchor((leg, 0.70 + 0.045 * j, 0, 0.0345 * k))
        cameo.rrbox(b, (0.018 * k, 0.002 * k, 0.005 * k), a4.matrix(), mat=glow, w=a4.w, r=0.3, segs=1)
    # 종아리 뒤 결정 두 개 (뒤·바깥으로 비스듬히)
    for j, (t, ln, ang) in enumerate(((0.56, 0.17, 125), (0.70, 0.12, 150))):
        a5 = e.anchor((leg, t, 180 - s * 40, 0.010 * k))
        Mc = a5.matrix() @ Matrix.Rotation(math.radians(ang), 4, "X") @ Matrix.Rotation(math.radians(s * 18), 4, "Y")
        pc = [(-0.016 * k, 0.0), (0.0, -0.014 * k), (0.016 * k, 0.0), (0.004 * k, ln * 0.6 * k), (0.0, ln * k)]
        pc = [(-0.016 * k, 0.0), (0.0, -0.014 * k), (0.016 * k, 0.0), (0.0, ln * k)]
        cameo.prism(b, pc, 0.014 * k, Mc @ Matrix.Translation((0, 0.007 * k, 0)), mat=crystal, w=a5.w,
                    chamfer=0.005 * k)


for side in ("L", "R"):
    boot_armor(side)

# ---- 등록: R41 장비와 마스크·표식은 합치지 않고 따로 남긴다 (먹선 색, 표시 전환)
for g, b in gear.items():
    e.add(b.obj(f"black_renewa_gear_{g}", angle=40.0), group=g, keep=True)
NOMASK = "nomask" in sys.argv     # 검토용: npm run model -- black_renewa.py -- nomask (커밋하지 않는 임시 파일)
if NOMASK:
    import bpy
    bpy.data.objects.remove(mask_obj, do_unlink=True)
else:
    e.add(mask_obj, group="head", keep=True)
e.add(marks, group="head", keep=True)

e.finalize()
marks["noOutline"] = 1
if not NOMASK:
    mask_obj["outline"] = 0.004
print("[black_renewa] tails vcol corners:",
      cameo.shade_braids(cameo.hair_obj(e), tails, WHITE,
                         [(0.0, WHITE), (0.55, WHITE), (0.72, "#efc6ea"), (0.86, "#e185d5"), (0.97, "#cf4fbf")]))
e.export("characters/black_renewa_nomask_review.glb" if NOMASK else "characters/black_renewa.glb")
