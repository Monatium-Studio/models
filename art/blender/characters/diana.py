"""디아나: 수인 마을의 촌장이자 수인들의 최고 어른(노루 수인). 에필로그 '에르핀의 세 번째 대관식'에서 이웃 지도자 헌사를
가장 먼저 맡는다(원작 테마극장 「여왕님의 마음으로 만든 나라」 에피소드 12, 헌사 순서는 디아나 → 엘레나 → 실라 →
셰이디 → 다야 → 벨리타).

원작 디아나(트릭컬 리바이브, '세월이 준 현명함')의 기본 모습이다. 전성기 모습인 디아나(왕년)은 별도 모델 wangdi.glb다.
두 판은 같은 사람이라 머리색 계열(장밋빛 갈색)과 붉은 눈을 같이 쓰지만, 이 판은 뿔이 짧게 깎였고 눈을 늘 감고 있다.
근거: docs/art/characters-cameo3.md.
- 식별 요소: 바닥 가까이 오는 풍성한 장밋빛 갈색 긴 머리(정수리 곱슬, 헝클어진 앞머리, 어깨 앞으로 늘어진 옆머리),
  아이들을 다치게 할까 봐 스스로 깎아 낸 짧은 뿔 그루터기(크림색 붕대 감기 + 늘어진 끈과 술), 옆으로 눕힌 사슴 귀(안쪽
  흰 털), 늘 감고 있는 눈(뜨면 붉은 눈), 크림색 긴 원피스(목 아래 X자 끈, 가슴의 금빛 매듭 장식, 왼쪽 다리 트임),
  트임 사이로 보이는 다리의 끈 띠, 끈을 엇갈려 묶은 샌들, 손목 감기, 등불을 매단 굽은 지팡이.
- 재해석: 지팡이와 등불은 별도 노드 diana_staff(socket_hand_R, 로컬: 원점 = 파지점, 자루 = +Z). 매듭 장식은 원작 도안
  대신 네 잎 매듭 윤곽 + 엇갈린 고리로 다시 그렸다. 원작의 굽은 허리 자세는 A 포즈 모델이라 런타임 포즈로 낸다.
  꼬리는 원작 스탠딩에서 보이지 않아 만들지 않았다.
- [오리지널] 대관식 축하 장식으로 왼쪽 뿔 붕대에 작은 흰 꽃 하나를 꽂았다.
- 표정: 기본(눈 감은 온화한 미소) + 키트 5종 + open(눈을 뜬 붉은 눈) + stern(싸늘하게 뜬 눈, "눈 감아주는 것도 한계가
  있답니다") + tribute(헌사를 말하는 따뜻한 얼굴) + laugh(후후) + blink 교정 키(눈을 뜬 표정만 의미가 있다).

npm run model -- art/blender/characters/diana.py
npm run shot -- characters/diana.glb
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
M_ = elf.mat
e = elf.Elf("diana", height=1.25, head=0.45, leg=1.04, chest=0.55, bust=0.5, hips=1.06, limb=1.0, segs=0.64, hand_q=0.50,
            cheek=0.11)
k = e.k
# 키트의 뾰족한 엘프 귀 대신 넓은 사슴 귀를 따로 만든다 (ear_L/R 본은 리그 호환을 위해 남는다)
e.remove("ear_L")
e.remove("ear_R")

# ---- 팔레트 (원작 카드·소개 이미지에서 눈으로 뽑음)
HAIR, HAIR_D, HAIR_L = "#a9746e", "#7c4c4a", "#cf9c90"
HAIR_TIP, HAIR_TIP_D = "#cf9f90", "#a3716a"
cream = M_("di_cream", "#f4e7dd")
cream_d = M_("di_cream_d", "#dcc6ba")
trim = M_("di_trim", "#b98a74")
knot_m = M_("di_knot", "#dfbd86")
knot_d = M_("di_knot_d", "#b58e5a")
band_m = M_("di_band", "#c9a596")
band_d = M_("di_band_d", "#8a6458")
antler = M_("di_antler", "#dab2a2")
wrap = M_("di_wrap", "#f3e9e0")
string = M_("di_string", "#8e5f55")
fluff = M_("di_fluff", "#ffffff")
ear_m = M_("di_ear", "#dcae9e")
ear_in = M_("di_ear_in", "#f2c0b8")
wood = M_("di_wood", "#5e4038")
wood_d = M_("di_wood_d", "#3f2a26")
iron = M_("di_iron", "#4a3c3c")
glow = M_("di_glow", "#ffffff", emission="#ffd98a", unlit=True)
flower_m = M_("di_flower", "#ffffff")
flower_c = M_("di_flower_c", "#f2c94c")
leaf_m = M_("di_leaf", "#7fae6a")

# ---- 얼굴: 늘 감고 있는 눈(∪), 온화한 미소, 굵은 짙은 눈썹. 뜨면 붉은 눈 (왕년과 같은 색)
OPEN = {"close": 0.0}
e.face(eye_color="#d6343c", iris_dark="#6e1820", iris_light="#ff9c78", pupil="#3a0a10",
       lash="#5a2c2c", brow="#7a4a46", brow_th=1.25, blush="#f6a2a2", blush_size=1.18, blush_lines=2,
       base={"eye": {"close": 1.0, "top": 0.022, "ktop": 4.2, "cin": 0.010, "cout": 0.012},
             "brow": {"dz": 0.050, "ang": 2.0, "arch": 0.002, "len": 0.038},
             "mouth": {"w": 0.020, "curve": 0.0045}},
       expr={
           # 눈을 뜬 디아나: 반쯤 뜬 붉은 눈, 온화한 입
           "open": {"eye": dict(OPEN, top=0.020, ktop=4.4, cout=0.014),
                    "iris": {"cz": 0.0010},
                    "brow": {"dz": 0.054, "ang": 0.0},
                    "mouth": {"w": 0.018, "curve": 0.0030}},
           # 싸늘하게 뜬 눈: 가는 눈, 작은 동공, 내린 눈썹, 일자 입 ("눈 감아주는 것도 한계가 있답니다")
           "stern": {"eye": dict(OPEN, top=0.014, ktop=5.2, tilt_in=-0.008),
                     "iris": {"pupil": 0.55, "cz": 0.0005},
                     "brow": {"ang": -12.0, "dz": 0.050, "th": 0.0074},
                     "mouth": {"w": 0.016, "curve": -0.0010}},
           # 헌사: 눈을 감은 채 따뜻하게 웃으며 말하는 얼굴
           "tribute": {"eye": {"lift": 0.004},
                       "brow": {"ang": 8.0, "dz": 0.054, "arch": 0.004},
                       "mouth": {"w": 0.024, "curve": 0.0060, "open": 0.0080, "top_arch": -0.0005}},
           # 후후: 눈이 더 휘고 입을 벌린 웃음 (원작 소개 이미지)
           "laugh": {"eye": {"lift": 0.010, "cin": 0.014, "cout": 0.016},
                     "brow": {"ang": 6.0, "dz": 0.056, "arch": 0.005},
                     "mouth": {"w": 0.030, "curve": 0.0085, "open": 0.0150, "top_arch": -0.0015}},
       })


# ---- 머리 (헤어 v2): 풍성한 긴 머리, 헝클어진 앞머리, 정수리 곱슬, 어깨 앞으로 늘어진 긴 옆머리
def di_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.1
        lk["free"] *= 0.70
    elif lk["region"] in ("side", "back"):
        lk["p"] = 2.0
        lk["curl"] = lk.get("curl", 0.0) + 0.012 * k
        lk["free"] *= 0.60


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.22, lock_fn=fairy.lock_edit(di_locks))
h.cap(front=30, side=-6, back=-46, part=-6, segs=14, rows=5)
h.bangs(n=7, spread=60, tip_el=-6, sweep=4, part=-6, jag=0.30, curl=1.3, seed=21.0)
h.sides(length=0.42, width=0.088, az=62, curl=0.4, thick=1.25, puff=1.2)
h.back(length=0.66, n=9, spread=110, thick=1.15)
h.shine(el=46, spread=60, n=2, size=1.0)
o = h.off


# ---- 깎아 낸 뿔 그루터기: 굵은 그루터기 + 짧은 곁가지 그루터기, 크림색 붕대 감기, 늘어진 끈과 술
def antler_geo(buf, s):
    w = {"head": 1.0}
    root = h.sp(s * 42.0, 48.0, o * 0.3)
    out = V((s * 1.0, 0.0, 0.0))
    up = V((0, 0, 1))
    beam = [root - (root - e.head_c).normalized() * 0.010 * k, root + out * 0.020 * k + up * 0.045 * k,
            root + out * 0.040 * k + up * 0.098 * k + V((0, 0.006 * k, 0)),
            root + out * 0.050 * k + up * 0.135 * k + V((0, 0.008 * k, 0))]
    P = elf.catmull([V(p) for p in beam], 10)
    st = [{"c": q, "rx": lerp(0.026, 0.021, i / (len(P) - 1)) * k, "ry": lerp(0.026, 0.021, i / (len(P) - 1)) * k,
           "w": w} for i, q in enumerate(P)]
    loft(buf, st, segs=8, cap0="flat", cap1="round", mat=antler, cap_len1=0.004 * k)
    # 곁가지 그루터기 (안쪽 앞, 짧게)
    c0 = P[4]
    tip = c0 + V((s * 0.040 * k, -0.006 * k, 0.040 * k))
    loft(buf, [{"c": c0, "rx": 0.016 * k, "ry": 0.016 * k, "w": w},
               {"c": c0.lerp(tip, 0.5), "rx": 0.015 * k, "ry": 0.015 * k, "w": w},
               {"c": tip, "rx": 0.014 * k, "ry": 0.014 * k, "w": w}], segs=7, cap0="flat", cap1="round", mat=antler,
         cap_len1=0.004 * k)
    # 크림색 붕대 두 겹 + 갈색 끈 한 줄 (붕대 사이)
    for i0, m_, wd, r_ in ((2, wrap, 0.024, 0.029), (6, wrap, 0.020, 0.025), (4, string, 0.006, 0.028)):
        c, T = P[i0], (P[i0 + 1] - P[i0]).normalized()
        band(buf, c, T, V((0, -1, 0)), r_ * k, r_ * k, wd * k, 0.003 * k, segs=10, mat=m_, w=w)
    # 늘어진 끈 두 가닥 + 끝 술
    c = P[4]
    for j, (dy, ln) in enumerate(((-0.006, 0.075), (0.008, 0.058))):
        a = c + out * 0.020 * k + V((0, dy * k, 0))
        tip = a + V((s * 0.006 * k, -0.002 * k, -ln * k))
        Q = elf.catmull([a, a.lerp(tip, 0.5) + V((s * 0.004 * k, 0, 0)), tip], 6)
        loft(buf, [{"c": q, "rx": 0.0028 * k, "ry": 0.0012 * k, "w": w, "ref": (1, 0, 0)} for q in Q], segs=4,
             cap0="flat", cap1="flat", mat=string, p=1.0)
        loft(buf, [{"c": tip + V((0, 0, 0.004 * k)), "rx": 0.004 * k, "ry": 0.004 * k, "w": w},
                   {"c": tip - V((0, 0, 0.004 * k)), "rx": 0.0065 * k, "ry": 0.0065 * k, "w": w},
                   {"c": tip - V((0, 0, 0.014 * k)), "rx": 0.0055 * k, "ry": 0.0055 * k, "w": w}], segs=6,
             cap0="round", cap1="flat", mat=wrap)
    if s > 0:
        # [오리지널] 대관식 축하: 왼쪽 뿔 붕대에 꽂은 작은 흰 꽃과 잎
        cf, Tf = P[2], (P[3] - P[2]).normalized()
        n_ = V((0.35, -1.0, 0.1)).normalized()
        Mf = Matrix.Translation(cf + n_ * 0.024 * k) @ frame(n_, (0, 0, 1))
        pts = []
        for t in range(20):
            a = 2 * math.pi * t / 20 + math.pi / 2
            rr = 0.016 * k * (0.55 + 0.45 * abs(math.cos(5 * (a - math.pi / 2) / 2)) ** 0.7)
            pts.append((rr * math.cos(a), rr * math.sin(a)))
        c2.prism(buf, pts, 0.003 * k, Mf, mat=flower_m, w=w)
        disc(buf, Mf @ V((0, -0.0032 * k, 0)), n_, (0, 0, 1), 0.0050 * k, 0.0050 * k, 0.0015 * k, segs=8,
             mat=flower_c, w=w)
        for ang in (-50.0, 40.0):
            c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.022, 0.010, n=4)], 0.002 * k,
                     Mf @ Matrix.Translation((0, 0.0015 * k, 0)) @ Matrix.Rotation(math.radians(180 + ang), 4, "Y"),
                     mat=leaf_m, w=w)


for s in (1, -1):
    e.part(f"antler_{'L' if s > 0 else 'R'}", "head", lambda buf, s=s: antler_geo(buf, s))


# ---- 사슴 귀: 머리카락 바깥 옆으로 눕혀 살짝 처진 넓은 잎 모양 (바깥 베이지 털, 안쪽 분홍, 뿌리 흰 털 뭉치)
def deer_ear(buf, s):
    sd = "L" if s > 0 else "R"
    w = {f"ear_{sd}": 1.0}
    az, el = s * 96.0, 4.0
    root, n0 = h.path(az, h.s_of_el(az, el), -0.004 * k)
    ax = V((s * 1.0, 0.10, -0.30)).normalized()          # 옆으로 뻗고 살짝 처진다
    face = V((0.0, -1.0, 0.35)).normalized()             # 안쪽 면이 앞·위를 본다
    face = (face - ax * face.dot(ax)).normalized()
    side = ax.cross(face).normalized()
    L, W = 0.105 * k, 0.062 * k
    st = []
    n = 9
    for i in range(n):
        t = i / (n - 1)
        wd = W / 2 * (math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.75) * (1.0 - 0.15 * t)
        st.append({"c": root + ax * (L * t), "rx": max(wd, 0.0012 * k), "ry": max(0.0065 * k * (1 - 0.6 * t),
                                                                           0.0012 * k),
                   "w": w, "ref": tuple(side)})
    loft(buf, st, segs=8, cap0="flat", cap1="round", mat=ear_m, cap_len1=0.004 * k)
    # 안쪽 분홍 판
    Mi = Matrix((side, -face, ax)).transposed().to_4x4()
    Mi.translation = root + ax * (0.045 * k) - face * (-0.0055 * k)
    c2.prism(buf, [(x * 0.62, z * 0.62 - 0.030 * k) for x, z in
                   [(px * k, pz * k) for px, pz in c3.leaf_poly(0.105, 0.062, n=5)]], 0.0015 * k,
             Matrix.Translation(Mi.translation) @ frame(face, ax), mat=ear_in, w=w)
    # 뿌리 쪽 흰 털 뭉치
    c2.ellipsoid(buf, root + ax * (0.030 * k) + face * 0.006 * k, ax, side, face, 0.022 * k, 0.012 * k,
                 0.008 * k, segs=8, rings=4, mat=fluff, w=w)


for s in (1, -1):
    e.part(f"deer_ear_{'L' if s > 0 else 'R'}", "head", lambda buf, s=s: deer_ear(buf, s))

# ---- 크림색 긴 원피스: 몸판 + 목 아래 X자 끈 + 윗단 띠 + 금빛 매듭 장식
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(cream, hem=wz - 0.010 * k, collar=None, flare=0.006)
e.ring(cream_d, "torso", e.torso_top - 0.018 * k, h=0.012, th=0.003, off=0.012, name="neck_band")
for s in (1, -1):
    # 목 뒤에서 내려와 가슴 위에서 엇갈리는 X자 끈
    e.strap(cream_d, [("torso", e.torso_top - 0.004 * k, s * 70, 0.012 * k), ("torso", e.torso_top - 0.016 * k, s * 34, 0.013 * k),
                      ("torso", cz + 0.040 * k, -s * 6, 0.0135 * k), ("torso", cz + 0.008 * k, -s * 44, 0.013 * k)],
            width=0.008, th=0.0025, name=f"cross_strap_{'L' if s > 0 else 'R'}")


def knot(buf, Mx, w):
    """네 잎 매듭 윤곽 (원작 켈트 매듭 장식을 단순화): 바탕 판 + 짙은 윤곽 고리 네 개 + 가운데 마름모."""
    R = Mx.to_3x3()
    n = (R @ V((0, -1, 0))).normalized()
    up = (R @ V((0, 0, 1))).normalized()
    sd = (R @ V((1, 0, 0))).normalized()
    pts = []
    for i in range(32):
        a = 2 * math.pi * i / 32
        r = 0.030 * k * (0.62 + 0.38 * abs(math.cos(2 * a)) ** 0.8)
        pts.append((r * math.cos(a), r * math.sin(a) * 1.25))
    c2.prism(buf, pts, 0.0025 * k, Mx, mat=knot_m, w=w)
    c = Mx.to_translation() + n * 0.0026 * k
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        cc = c + sd * (math.cos(a) * 0.016 * k) + up * (math.sin(a) * 0.020 * k)
        band(buf, cc, n, up, 0.010 * k, 0.010 * k, 0.0012 * k, 0.0022 * k, segs=10, mat=knot_d, w=w)
    c2.prism(buf, c2.diamond_poly(0.012 * k, 0.016 * k), 0.0012 * k, Mx @ Matrix.Translation((0, -0.0025 * k, 0)),
             mat=knot_d, w=w)


e.gear("knot", ("torso", cz - 0.024 * k, -14.0, 0.013 * k), knot)

# 바닥까지 오는 치마 (왼쪽 앞 트임, 테두리)
SLIT = 34.0
skirt = c2.Shell(e, cream, wz + 0.002 * k, 0.030 * k, gap=[(0.0, 1.0), (0.18, 3.0), (0.45, 13.0), (1.0, 20.0)],
                 a_fn=lambda a, u: a + SLIT, off=0.016, th=0.004, skirt=True, rows=11, cols=24,
                 flare=[(0.0, 0.0), (0.35, 0.016), (1.0, 0.048)], cover=True)
skirt.edge_trim(trim, width=0.006, th=0.002, i0=2).hem_trim(trim, width=0.007, th=0.002)
skirt.done("skirt")

# ---- 다리: 트임 사이로 보이는 왼다리 끈 띠, 끈을 엇갈린 크림색 샌들
for t in (0.46, 0.60, 0.74):
    e.ring(band_m, "leg_L", t, h=0.012, th=0.003, off=0.003, name=f"leg_band_{t}")
q0 = e.q
e.q = 0.55
e.boots(cream, top=0.90, sole=(band_d, 0.012), off=0.008, toe=0.004)
e.q = q0
for sd in ("L", "R"):
    for t in (0.84, 0.90):
        e.ring(band_m, f"leg_{sd}", t, h=0.008, th=0.0025, off=0.010, name=f"sandal_strap_{sd}{t}")
    # 발등 X자 끈
    for s in (1, -1):
        e.strap(band_m, [(f"leg_{sd}", 0.92, s * 55, 0.012 * k), (f"leg_{sd}", 0.98, -s * 20, 0.020 * k)],
                width=0.006, th=0.0022, name=f"sandal_x_{sd}{s}")

# ---- 팔: 맨팔 + 손목 감기 두 줄
for sd in ("L", "R"):
    for t in (0.86, 0.93):
        e.ring(wrap, f"arm_{sd}", t, h=0.012, th=0.0035, off=0.002, name=f"wrist_wrap_{sd}{t}")

e.finalize()

# 머리끝 살구빛 그라데이션 (정점색, 왕년 판과 같은 계열)
hob = e.result.get("hair")
zmin = min(v.co.z for v in hob.data.vertices)
for node, base, tip in (("hair", HAIR, HAIR_TIP), ("hair_in", HAIR_D, HAIR_TIP_D)):
    ob = e.result.get(node)
    if ob is not None:
        c2.vc_gradient(ob, base, [(zmin + 0.03 * k, tip), (zmin + 0.30 * k, base)])


# ---- 지팡이 + 등불 (별도 노드 staff): 로컬 원점 = 오른손 파지점, 자루 = +Z(위), 굽은 머리 = +Y(앞)
def staff(grip_z):
    S = k
    b = Buf()
    w = {}
    z0 = -grip_z                       # 바닥
    top = 0.80 * S                     # 파지점 위 자루 길이
    loft(b, [{"c": V((0, 0, z0)), "rx": 0.011 * S, "ry": 0.011 * S, "w": w},
             {"c": V((0, 0, z0 * 0.4)), "rx": 0.012 * S, "ry": 0.012 * S, "w": w},
             {"c": V((0, 0, top * 0.6)), "rx": 0.012 * S, "ry": 0.012 * S, "w": w},
             {"c": V((0, 0, top)), "rx": 0.011 * S, "ry": 0.011 * S, "w": w}], segs=7, cap0="flat",
         cap1="flat", mat=wood)
    # 굽은 머리: 위로 올라갔다 앞으로 꺾여 내려온다
    hook = [V((0, 0, top)), V((0, 0.020 * S, top + 0.050 * S)), V((0, 0.075 * S, top + 0.070 * S)),
            V((0, 0.130 * S, top + 0.050 * S)), V((0, 0.150 * S, top + 0.010 * S))]
    Q = elf.catmull(hook, 12)
    loft(b, [{"c": q, "rx": 0.011 * S, "ry": 0.011 * S, "w": w} for q in Q], segs=7, cap0="flat", cap1="round",
         mat=wood)
    # 감은 띠 (크림 + 짙은 갈색)
    for zz, m_ in ((-0.04, wrap), (0.02, wrap), (0.08, wood_d), (top / S - 0.02, wrap)):
        band(b, V((0, 0, zz * S)), V((0, 0, 1)), V((0, -1, 0)), 0.013 * S, 0.013 * S, 0.016 * S, 0.003 * S,
             segs=8, mat=m_, w=w)
    band(b, Q[7], (Q[8] - Q[6]).normalized(), V((0, 0, 1)), 0.013 * S, 0.013 * S, 0.014 * S, 0.003 * S, segs=8,
         mat=wrap, w=w)
    # 등불: 굽은 끝에서 고리로 매달린 사각 등 (짙은 철 테 + 노란 빛 창)
    hang = Q[-1] + V((0, 0, -0.012 * S))
    loft(b, [{"c": Q[-1], "rx": 0.002 * S, "ry": 0.002 * S, "w": w},
             {"c": hang, "rx": 0.002 * S, "ry": 0.002 * S, "w": w}], segs=4, cap0="flat", cap1="flat", mat=iron)
    lc = hang + V((0, 0, -0.058 * S))
    rbox(b, (0.054 * S, 0.054 * S, 0.012 * S), Matrix.Translation(lc + V((0, 0, 0.046 * S))), mat=iron, w=w, r=0.3,
         segs=1)
    rbox(b, (0.060 * S, 0.060 * S, 0.010 * S), Matrix.Translation(lc - V((0, 0, 0.046 * S))), mat=iron, w=w, r=0.3,
         segs=1)
    loft(b, [{"c": lc + V((0, 0, 0.052 * S)), "rx": 0.020 * S, "ry": 0.020 * S, "w": w},
             {"c": lc + V((0, 0, 0.064 * S)), "rx": 0.004 * S, "ry": 0.004 * S, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=iron)
    c3.box12(b, (0.042 * S, 0.042 * S, 0.078 * S), Matrix.Translation(lc), glow, w)
    for x in (-1, 1):
        for y in (-1, 1):
            c3.box12(b, (0.007 * S, 0.007 * S, 0.084 * S), Matrix.Translation(lc + V((x * 0.022 * S, y * 0.022 * S, 0))),
                     iron, w)
    for f in range(4):                 # 창 가운데 가로살
        a = math.pi / 2 * f
        d = V((math.cos(a), math.sin(a), 0))
        c3.box12(b, (0.044 * S if abs(d.y) > 0.5 else 0.003 * S, 0.003 * S if abs(d.y) > 0.5 else 0.044 * S,
                     0.004 * S), Matrix.Translation(lc + d * 0.0215 * S), iron, w)
    return b.obj("diana_staff_geo", angle=35.0)


sock = bpy.data.objects["socket_hand_R"]
pos = sock.matrix_world.translation.copy()
st = staff(pos.z)
Zd = V((0.0, 0.0, 1.0))
Yd = V((-0.25, -1.0, 0.0)).normalized()        # 굽은 머리와 등불이 앞(살짝 바깥)으로
Xd = Yd.cross(Zd).normalized()
Mw = Matrix((Xd, Yd, Zd)).transposed().to_4x4()
Mw.translation = pos
c3.socket_prop(e, st, "socket_hand_R", Mw, name="staff", outline=0.0028,
               props={"lantern": "0,%.3f,%.3f" % (0.150 * k, 0.80 * k - 0.07 * k)})

e.export("characters/diana.glb")
