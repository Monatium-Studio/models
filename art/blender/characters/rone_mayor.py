"""로네(시장): 본편(1막~에필로그)의 로네. 모나티엄 부시장 겸 첩보반장. 2막에서 흑뉴아에게 붙잡혀(M4) 외래종
수용소에 갇히고(M5, 돈까스 접시를 들고 나온다), 탈출로(M6)를 거쳐 3막에서 중성자탄 발사를 보고한다.

원작 로네(시장)(트릭컬 리바이브 이격 사도, 2025-07-31, 테마극장 「믿을 녀석 하나 없는 차가운 도시」)를 바탕으로 한
카메오 모델. 원작에서 이 테마극장 에필로그부터 '그림자 속의 시장'을 맡으며 시장 옷이 사실상 기본 복장이 되었고,
「여왕님의 마음으로 만든 나라」(침공전)에서도 부시장 겸 첩보반장이다. 갑옷 차림(rone.glb)은 그 이전(모나티엄 건설 회상).
- 유지한 식별 요소 (rone.py와 같은 얼굴·표정·머리색): 회갈색 졸린 눈, 걱정 많은 눈썹, 갈색 긴 생머리, 옆으로 쓸린
  앞머리, 머리띠, 왼쪽에 모은 머리. 표정: 키트 5종 + fluster, cry, dreamy, smug.
- 원작 시장 복장: 검은 머리띠, 왼쪽 높은 경단(사과머리) + 검은 리본 + 돈까스 브로치(접시 위 돈까스·양배추·토마토),
  허리까지 오는 긴 생머리, 짙은 남흑색 정장 재킷(허벅지 위까지, 허리에서 여밈, 금색 단추), 흰 셔츠 깃 + 보라 넥타이,
  주황 시장 어깨띠(오른 어깨 → 왼 엉덩이, 끝에 돈까스·포크 문장), 소맷부리 주황 줄과 주황 톱니 장식, 왼쪽 깃 주황
  배지, 재킷에 가려진 짧은 검은 치마, 검은 스타킹, 검은 구두. 갑옷·검·건틀릿은 없다(맨손).
- 체형: bust 0.20 (로네(시장) 문서: "빈유인 것을 제외하면 의외로 글래머", docs/art/characters-cameo3.md 9.8절).
- 재해석: 어깨띠 글자는 엘프 글자를 흉내 낸 짧은 막대 표식으로만 둔다. 손에 드는 돈까스 접시·포크는 소품
  (props/cine_tonkatsu_plate.glb, props/cine_fork.glb)이고 hold 시스템이 socket_hand_L/R에 붙인다.
근거: docs/art/characters-cameo2.md 3.1절

npm run model -- art/blender/characters/rone_mayor.py
npm run shot -- characters/rone_mayor.glb
npm run shot -- characters/rone_mayor.glb --focus rone_mayor_face --views front,34 --morph dreamy:1
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, loft, band, rbox, disc, lerp  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("rone_mayor", height=1.20, head=0.45, leg=1.02, chest=0.15, bust=0.20, segs=0.76, hand_q=0.6, cheek=0.10)
k = e.k
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z

# ---- 팔레트 (원작 카드 실측: 재킷 #2f3040, 넥타이 #5a4ad0, 어깨띠 #f2a83c, 스타킹 #3c3437, 머리띠 #262838)
jacket = M_("rnm_jacket", "#33343f")
jacket_d = M_("rnm_jacket_d", "#24252e")
shirt = M_("rnm_shirt", "#f6f3f1")
tie = M_("rnm_tie", "#5b4ccc")
tie_d = M_("rnm_tie_d", "#4637a6")
orange = M_("rnm_orange", "#f2a83c")
orange_d = M_("rnm_orange_d", "#d9802a")
gold = M_("rnm_gold", "#e0ad4e")
skirt_m = M_("rnm_skirt", "#2a2a33")
tights = M_("rnm_tights", "#3e3639")
shoe = M_("rnm_shoe", "#25232b")
sole = M_("rnm_sole", "#17161b")
band_m = M_("rnm_band", "#272939")
ribbon = M_("rnm_ribbon", "#222436")
plate_w = M_("rnm_plate", "#f4f1ea")
katsu = M_("rnm_katsu", "#d79a3e")
sauce = M_("rnm_sauce", "#5a2f1e")
cabbage = M_("rnm_cabbage", "#8fcf5e")
tomato = M_("rnm_tomato", "#e0453a")
ink = M_("rnm_ink", "#8a4a1c")

# ---- 얼굴 (rone.py와 같다): 회갈색 졸린 눈 (윗눈꺼풀이 무겁게 내려옴), 살짝 벌린 입, 걱정 많은 눈썹
e.face(eye_color="#8c7d77", iris_dark="#4a3c38", iris_light="#e0d6cf", pupil="#2a2020",
       lash="#4a2e2a", brow="#6e4c40", blush="#f7a7a4", blush_size=1.1,
       base={"eye": {"top": 0.016, "ktop": 3.8, "tilt_out": -0.004, "cout": 0.012},
             "iris": {"cz": 0.0020},
             "brow": {"dz": 0.062, "ang": 7.0, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0020, "open": 0.0035, "top_arch": 0.0010}},
       expr={
           # 허둥지둥: 동그래진 눈, 작은 동공, 올라간 눈썹, 물결 입
           "fluster": {"eye": {"top": 0.034, "ktop": 2.4, "bot": 0.056},
                       "iris": {"pupil": 0.55, "rx": 0.026, "ry": 0.034},
                       "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                       "mouth": {"w": 0.024, "curve": -0.0020, "open": 0.0080, "wave": 0.0018}},
           # 오열 (돈까스가 날아갔을 때): 처진 눈썹, 가늘게 젖은 눈, 크게 벌린 입
           "cry": {"eye": {"top": 0.008, "tilt_in": 0.012, "tilt_out": -0.012, "lift": 0.016},
                   "brow": {"ang": 26.0, "dz": 0.062},
                   "mouth": {"w": 0.032, "curve": -0.0070, "open": 0.020, "wave": 0.0020}},
           # 돈까스 상상: 반달 눈웃음, 벌린 입
           "dreamy": {"eye": {"top": 0.014, "lift": 0.026, "kbot": 2.6},
                      "brow": {"ang": 10.0, "dz": 0.068, "arch": 0.006},
                      "mouth": {"w": 0.030, "curve": 0.0070, "open": 0.012, "top_arch": -0.001}},
       })
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.013, "lift": 0.010}, "mouth": {"w": 0.026, "curve": 0.0035, "open": 0.0}},
             L={"brow": {"dz": 0.066, "ang": -2.0}}, R={"brow": {"dz": 0.060, "ang": -8.0}},
             corner=(0.0070, -0.0005), mouth_dx=0.0020 * k)


# ---- 머리: 갈색 긴 생머리(허리 아래), 옆으로 쓸린 앞머리(rone.py와 같음), 양옆 긴 옆머리, 검은 머리띠,
# 왼쪽 높은 경단 + 검은 리본 + 돈까스 브로치
HAIR = "#8b6456"


def rone_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 1.7


h = c2.hair(e, HAIR, dark="#664539", light="#b48d7c", lock_fn=c2.lock_edit(rone_locks))
h.cap(front=30, side=-8, back=-48, part=16)
h.bangs(n=6, spread=60, tip_el=0, jag=0.25, sweep=-12, seed=3.0)
h.sides(length=0.20, width=0.082, curl=0.35)
h.back(length=0.36, n=9, spread=104)
h.shine(el=50, spread=70, size=1.1)
c2.on_hair_band(e, h, band_m, az0=-104, az1=104, el_fn=lambda az: 56.0 - 46.0 * (abs(az) / 104.0) ** 1.8,
                width=0.022, th=0.005, lift=-0.003)

# 경단 (왼쪽 뒤 위): 원작의 사과머리. 감아 올린 결을 한 가닥 띠로 낸다
BUN_AZ, BUN_EL, BUN_SIZE = 118.0, 22.0, 0.104
h.bun(az=BUN_AZ, el=BUN_EL, size=BUN_SIZE)
_bb, _bn = h.path(BUN_AZ, h.s_of_el(BUN_AZ, BUN_EL))
_bc = _bb + _bn * BUN_SIZE * 0.32 * k
_bx = _bn.cross(V((0, 0, 1))).normalized()
_by = _bn.cross(_bx).normalized()
coil = []
for i in range(15):
    t = i / 14
    a = math.radians(-30 + 330 * t)
    r = BUN_SIZE * 0.50 * k * (1.0 - 0.18 * t)
    coil.append(_bc + _bn * (BUN_SIZE * (0.10 + 0.20 * t) * k) + _bx * (math.cos(a) * r) + _by * (math.sin(a) * r))
h.strand(coil, 0.030 * k, 0.012 * k, n=16, segs=7, taper=[(0, 0.6), (0.2, 1.0), (0.8, 0.9), (1, 0.2)],
         normal=tuple(_bn), w={"head": 1.0})


def head_frame(az, el, lift):
    """머리 덩어리 바깥 면 위 배치 행렬 (로컬 -Y = 바깥 법선, +Z = 정수리 쪽)."""
    s = h.s_of_el(az, el)
    p, n = h.path(az, s, lift * k)
    p2, _ = h.path(az, max(s - 0.01 * k, 0.0), lift * k)
    up = p2 - p
    up = (up - n * up.dot(n)).normalized()
    return Matrix.Translation(p) @ elf.frame(n, up), p, n


def bun_bow(buf):
    """경단 앞 위의 검은 리본 (돈까스 브로치 받침)."""
    M, p, n = head_frame(100.0, 27.0, 0.008)
    c2.bow_geo(buf, M @ Matrix.Rotation(math.radians(-28), 4, "Y"), 0.096 * k, ribbon, w={"head": 1.0}, tails=0.80,
               knot_mat=ribbon, segs=6)


BR = 1.70     # 브로치 크기 배율 (원작 SD에서 접시 폭이 머리 폭의 4분의 1쯤)


def brooch(buf):
    """돈까스 브로치: 흰 접시 위 돈까스 두 조각 + 소스 + 양배추 + 방울토마토. 머리 왼쪽 위, 리본 위에 얹힌다."""
    w = {"head": 1.0}
    _, p, n = head_frame(76.0, 40.0, 0.010)
    out = (n + V((0.0, -0.55, 0.25))).normalized()          # 머리 바깥에서 앞·위로 조금 돌려 정면에서 접시가 보이게
    upv = V((0, 0, 1))
    upv = (upv - out * upv.dot(out)).normalized()
    upv = (Matrix.Rotation(math.radians(-14), 3, out) @ upv).normalized()
    sd = upv.cross(out).normalized()
    s = BR * k
    c = p + out * 0.004 * k
    disc(buf, c, out, upv, 0.036 * s, 0.031 * s, 0.006 * s, segs=16, mat=plate_w, w=w)
    band(buf, c + out * 0.006 * s, out, upv, 0.033 * s, 0.028 * s, 0.004 * s, 0.0025 * s, segs=16, mat=plate_w, w=w)
    top = c + out * 0.007 * s
    for i, (dx, dz, rot) in enumerate(((-0.010, -0.003, 16.0), (0.008, 0.004, -12.0))):
        cc = top + sd * (dx * s) + upv * (dz * s) + out * 0.006 * s
        A = (Matrix.Rotation(math.radians(rot), 3, out) @ upv).normalized()
        B = A.cross(out).normalized()
        c2.ellipsoid(buf, cc, A, B, out, 0.019 * s, 0.012 * s, 0.0075 * s, segs=10, rings=5, mat=katsu, w=w)
        Ms = Matrix.Translation(cc + out * 0.0072 * s) @ elf.frame(out, A)
        c3.box12(buf, (0.006 * s, 0.0016 * s, 0.022 * s), Ms, sauce, w)
    c2.ellipsoid(buf, top + sd * 0.021 * s + upv * 0.012 * s + out * 0.004 * s, upv, sd, out, 0.012 * s, 0.010 * s,
                 0.007 * s, segs=8, rings=5, mat=cabbage, w=w)
    for dx, dz in ((0.026, 0.000), (0.018, -0.009)):
        c2.ellipsoid(buf, top + sd * (dx * s) + upv * (dz * s) + out * 0.006 * s, upv, sd, out, 0.0058 * s,
                     0.0058 * s, 0.0058 * s, segs=8, rings=5, mat=tomato, w=w)


e.part("bun_bow", "head", bun_bow)
e.part("brooch", "head", brooch)

# ---- 셔츠 + 넥타이
e.shirt(shirt, hem=hz - 0.004 * k, collar=None, flare=0.010)


def shirt_collar(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.012 * k), (0, 0, 1), (1, 0, 0), 0.054 * k, 0.050 * k, 0.026 * k,
         0.005 * k, segs=16, mat=shirt, w=w, taper=-0.03)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.004 * k, sg * 22, 0.014 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 12), 4, "Y")
        c2.prism(buf, [(-sg * 0.020 * k, 0.010 * k), (sg * 0.014 * k, 0.012 * k), (sg * 0.004 * k, -0.026 * k)],
                 0.004 * k, M, mat=shirt, w=w, chamfer=0.0)


def necktie(buf):
    # 매듭 (깃 사이)
    p, n = e.torso_point(e.torso_top - 0.010 * k, 0.0, 0.020 * k)
    wk = e._torso_wfn(p, 0)
    rbox(buf, (0.020 * k, 0.012 * k, 0.018 * k), Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)), mat=tie_d, w=wk,
         r=0.45, segs=1, taper=0.25)
    # 날: 매듭 아래에서 넓어지며 재킷 여밈까지
    st = []
    zs = [e.torso_top - 0.020 * k, cz + 0.020 * k, cz - 0.020 * k, cz - 0.050 * k]
    ws = [0.010, 0.014, 0.016, 0.003]
    for z, hw in zip(zs, ws):
        q, nn = e.torso_point(z, 0.0, 0.017 * k)
        st.append({"c": q, "rx": hw * k, "ry": 0.0028 * k, "w": e._torso_wfn(q, 0), "ref": (1, 0, 0)})
    loft(buf, st, segs=6, cap0="flat", cap1="round", mat=tie)


e.part("shirt_collar", "body", shirt_collar)
e.part("necktie", "body", necktie)

# ---- 짧은 검은 치마 (재킷 밑단 아래로 조금만 보인다), 검은 스타킹, 검은 구두
sk = c2.Shell(e, skirt_m, wz - 0.016 * k, hz - 0.088 * k, off=0.016, th=0.004, skirt=True, cols=22, rows=5,
              flare=[(0.0, 0.0), (0.5, 0.012), (1.0, 0.026)], pleat=(0.003, 14, 0.3))
sk.done("skirt")
e.pants(tights, waist=wz - 0.010 * k, length=0.96, off=0.002, bag=0.0, blouse=0.0)
e.boots(shoe, top=0.97, sole=(sole, 0.012), toe=0.004, off=0.008)

# ---- 짙은 남흑색 정장 재킷: 허리에서 여미고 위는 V로 열려 셔츠·넥타이가 보인다. 허벅지 위까지
J_TOP, J_HEM = e.torso_top - 0.004 * k, hz - 0.066 * k
jk = c2.Shell(e, jacket, J_TOP, J_HEM,
              gap=[(0.0, 34.0), (0.22, 20.0), (0.42, 4.0), (0.70, 3.0), (1.0, 11.0)], off=0.024, th=0.005,
              skirt=True, rows=15, cols=22, flare=[(0.0, 0.0), (0.45, 0.010), (1.0, 0.030)], shoulder=0.85)
jk.edge_trim(jacket, width=0.022, th=0.004, i1=6)                  # 접힌 깃 (라펠)
jk.edge_trim(jacket_d, width=0.006, th=0.002, i0=6)
jk.hem_trim(jacket_d, width=0.008, th=0.002)
jk.done("jacket")
jc = c2.Shell(e, jacket, e.torso_top + 0.028 * k, e.torso_top - 0.006 * k, gap=44.0, off=0.026, th=0.005, rows=3,
              cols=18, flare=[(0.0, 0.008), (1.0, 0.0)])
jc.done("jacket_collar")
SLV_OFF, SLV_FLARE, CUFF_H, CUFF_TH, SLV_LEN = 0.016, 0.016, 0.024, 0.0045, 0.97
e.sleeves(jacket, length=SLV_LEN, off=SLV_OFF, flare=SLV_FLARE, puff=0.004, cuff=(jacket_d, CUFF_H, CUFF_TH))


def u_of(z):
    return (J_TOP - z) / (J_TOP - J_HEM)


def jacket_bits(buf):
    # 금색 단추 2개 (여밈), 허리 주머니 덮개
    for zz in (wz + 0.010 * k, wz - 0.030 * k):
        Mx = jk.frame_at(u_of(zz), 7.0, 0.002 * k)
        w = c2.skirt_w(e, Mx.to_translation())
        q = Mx.to_translation()
        nn = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        disc(buf, q, nn, (0, 0, 1), 0.0062 * k, 0.0062 * k, 0.0030 * k, segs=10, mat=gold, w=w)
    for sg in (1, -1):
        Mx = jk.frame_at(u_of(hz + 0.004 * k), sg * 52, 0.001 * k)
        w = c2.skirt_w(e, Mx.to_translation())
        rbox(buf, (0.054 * k, 0.005 * k, 0.015 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0)), mat=jacket_d, w=w,
             r=0.2, segs=1)
    # 왼쪽 깃 주황 배지 (원작의 둥근 배지)
    Mi = jk.frame_at(u_of(cz + 0.040 * k), 26, 0.003 * k)
    q = Mi.to_translation()
    nn = (Mi.to_3x3() @ V((0, -1, 0))).normalized()
    w = e._torso_wfn(q, 0)
    disc(buf, q, nn, (0, 0, 1), 0.010 * k, 0.009 * k, 0.003 * k, segs=12, mat=orange, w=w)
    disc(buf, q + nn * 0.003 * k, nn, (0, 0, 1), 0.006 * k, 0.005 * k, 0.0015 * k, segs=10, mat=orange_d, w=w)


e.part("jacket_bits", "body", jacket_bits)


def cog_poly(r_out, r_in, n=8):
    pts = []
    for i in range(n * 4):
        a = math.radians(90.0 + 360.0 * i / (n * 4))
        r = r_out if (i % 4) in (0, 1) else r_in
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


# 소맷부리: 주황 줄 + 금색 단추 + 바깥쪽 주황 톱니 장식 (원작 소맷부리의 주황 톱니)
for sd, s in (("L", 1), ("R", -1)):
    ch = e.arm_chain(sd)
    c_, tan = ch.at(SLV_LEN)
    rx, ry = e.arm_r(SLV_LEN)
    r_out = SLV_OFF * k + SLV_FLARE * k + CUFF_TH * k

    def cuff_line(buf, ch=ch, c_=c_, tan=tan, rx=rx, ry=ry, r_out=r_out):
        band(buf, c_ - tan * (CUFF_H + 0.002) * k, tan, (0, -1, 0), rx + r_out - 0.001 * k, ry + r_out - 0.001 * k,
             0.0055 * k, 0.0022 * k, segs=16, mat=orange, w=ch.weights(SLV_LEN - 0.05))

    e.part(f"cuff_line_{sd}", "arms", cuff_line)
    t_cog = SLV_LEN - (CUFF_H * 0.5 / 0.25)
    e.gear(f"cuff_cog_{sd}", (f"arm_{sd}", t_cog, s * 90.0, r_out + 0.001 * k),
           lambda buf, Mx, w: (c2.prism(buf, cog_poly(0.016 * k, 0.012 * k), 0.003 * k, Mx, mat=orange, w=w),
                               disc(buf, Mx @ V((0, -0.0032 * k, 0)), (Mx.to_3x3() @ V((0, -1, 0))).normalized(),
                                    (Mx.to_3x3() @ V((0, 0, 1))).normalized(), 0.0055 * k, 0.0055 * k, 0.0015 * k,
                                    segs=10, mat=gold, w=w)))

# ---- 주황 시장 어깨띠 (오른 어깨 -X → 왼 엉덩이 +X, 앞뒤 한 줄), 글자 표식, 끝 자락 + 돈까스·포크 문장
# 재킷 셸 위를 따라간다: (u: 0=재킷 윗단, 1=밑단, 방위: 0=앞, 90=왼쪽)
SASH = [(0.80, 64.0), (0.66, 44.0), (0.52, 22.0), (0.38, -2.0), (0.25, -26.0), (0.13, -46.0), (0.04, -64.0),
        (0.00, -90.0), (0.04, -116.0), (0.13, -136.0), (0.25, -156.0), (0.38, -180.0), (0.52, -204.0),
        (0.66, -226.0), (0.80, -246.0)]
SASH_W, SASH_LIFT = 0.040, 0.0065


def sash_path(n_per=3, lift=SASH_LIFT):
    pts, nrm = [], []
    for (u0, a0), (u1, a1) in zip(SASH, SASH[1:]):
        for i in range(n_per):
            t = i / n_per
            p, nn = jk.surface(lerp(u0, u1, t), lerp(a0, a1, t), lift * k)
            pts.append(p)
            nrm.append(nn)
    p, nn = jk.surface(SASH[-1][0], SASH[-1][1], lift * k)
    return pts + [p], nrm + [nn]


def sash(buf):
    pts, nrm = sash_path()
    ups = []
    for i in range(len(pts)):
        tan = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        ups.append(tan.cross(nrm[i]).normalized())
    ws = [c2.skirt_w(e, p) for p in pts]
    wf = lambda t: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)]  # noqa: E731
    elf._loop(buf, pts, nrm, ups, SASH_W * k, 0.0035 * k, mat=orange, closed=False, w=wf)
    # 가장자리 짙은 주황 줄 두 가닥
    for sg in (1, -1):
        pe = [p + u * (sg * SASH_W * 0.40 * k) + nn * 0.0034 * k for p, u, nn in zip(pts, ups, nrm)]
        elf._loop(buf, pe, nrm, ups, 0.0045 * k, 0.0010 * k, mat=orange_d, closed=False, w=wf)
    # 엘프 글자 표식: 짧은 막대 묶음 3개 (가슴 쪽, 띠 방향으로 기울임)
    for (u, a) in ((0.20, -34.0), (0.29, -18.0), (0.38, -2.0)):
        p, nn = jk.surface(u, a, (SASH_LIFT + 0.0036) * k)
        p2, _ = jk.surface(u - 0.02, a - 4.0, (SASH_LIFT + 0.0036) * k)
        along = (p2 - p)
        along = (along - nn * along.dot(nn)).normalized()
        M = Matrix.Translation(p) @ elf.frame(nn, along)
        w = c2.skirt_w(e, p)
        for dx, hh in ((-0.006, 0.014), (0.0, 0.009), (0.006, 0.014)):
            c3.box12(buf, (0.0028 * k, 0.0014 * k, hh * k), M @ Matrix.Translation((dx * k, 0, 0)), ink, w)


e.part("sash", "body", sash)


def sash_end(buf):
    """왼 엉덩이의 띠 끝: 아래로 늘어진 제비꼬리 자락 두 장 + 둥근 문장 (흰 접시에 돈까스, 포크)."""
    u, a = SASH[0]
    M = jk.frame_at(u, a, (SASH_LIFT + 0.003) * k)
    w = c2.skirt_w(e, M.to_translation())
    for dx, rot, L in ((-0.010, 7.0, 0.084), (0.012, -9.0, 0.070)):
        Mt = M @ Matrix.Translation((dx * k, -0.001 * k, 0.004 * k)) @ Matrix.Rotation(math.radians(rot), 4, "Y")
        poly = [(-0.016 * k, 0.004 * k), (0.016 * k, 0.004 * k), (0.016 * k, -L * k), (0.0, -(L - 0.016) * k),
                (-0.016 * k, -L * k)]
        c2.prism(buf, poly, 0.0035 * k, Mt, mat=orange, w=w)
    Me = M @ Matrix.Translation((0, -0.0075 * k, -0.002 * k))
    q = Me @ V((0, 0, 0))
    nn = (Me.to_3x3() @ V((0, -1, 0))).normalized()
    upv = (Me.to_3x3() @ V((0, 0, 1))).normalized()
    sd = (Me.to_3x3() @ V((1, 0, 0))).normalized()
    disc(buf, q, nn, upv, 0.025 * k, 0.025 * k, 0.004 * k, segs=14, mat=orange_d, w=w)
    disc(buf, q + nn * 0.004 * k, nn, upv, 0.020 * k, 0.020 * k, 0.002 * k, segs=14, mat=plate_w, w=w)
    c2.ellipsoid(buf, q + nn * 0.006 * k - sd * 0.004 * k, upv, sd, nn, 0.012 * k, 0.008 * k, 0.003 * k, segs=8,
                 rings=5, mat=katsu, w=w)
    # 포크 (오른쪽, 세로)
    fx = q + nn * 0.0065 * k + sd * 0.010 * k
    c3.box12(buf, (0.0024 * k, 0.0016 * k, 0.020 * k), Matrix.Translation(fx - upv * 0.003 * k) @ elf.frame(nn, upv),
             gold, w)
    for ddx in (-0.0026, 0.0, 0.0026):
        c3.box12(buf, (0.0012 * k, 0.0016 * k, 0.007 * k),
                 Matrix.Translation(fx + upv * 0.0095 * k + sd * ddx * k) @ elf.frame(nn, upv), gold, w)


e.part("sash_end", "body", sash_end)

e.finalize()
e.export("characters/rone_mayor.glb")
