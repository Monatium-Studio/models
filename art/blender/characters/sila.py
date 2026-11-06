"""실라: 정령산 꼭대기의 바람 고위 정령, 정령들의 수장. 엘리아스 침공전에서 정령산을 지키다가 성전에 합류하고,
에르피엔 결전에서 마카샤와 함께 요정 성전군의 돌격을 지휘한다(바람으로 R41의 시야를 가리고 요정들을 날라 근접전을
돕는다). 3막 M8 성전 합류 컷신, M9 종막.

원작 실라(트릭컬 리바이브, '최고 명사수')의 외형을 따른다. 근거: docs/art/characters-cameo3.md
- 식별 요소: 허벅지까지 오는 연민트빛 흰 생머리(끝이 연보라로 물듦), 옆으로 넘긴 앞머리와 오른쪽(-X) 바깥으로
  뻗친 옆머리, 양옆에서 위·뒤로 솟은 금색 줄무늬 날개 장식(서클릿), 위는 하늘색·아래는 노란빛인 반쯤 감은 도도한
  눈, 금색 목장식과 하늘색 보석, 가슴을 엇갈려 감은 금색 띠, 그리스풍 흰 드레스(짧은 치마 + 뒤로 길게 늘어진 자락),
  허리의 검은 끈과 금색 감은 띠·금색 잎 장식, 왼팔(+X) 긴 흰 토시(청록 바람 소용돌이 무늬), 오른팔(-X) 검은 팔찌와
  흰 팔보호대, 금색 끈을 엇갈려 감은 흰 샌들(윗단 금색 잎), 금색·나무 활(끝에 하늘색 결정)과 얼음 화살.
- 재해석: 활은 별도 노드 sila_bow(왼손 hand_L), 얼음 화살은 별도 노드 sila_arrow(오른손 hand_R, 발광)로 뺐다.
  배와 어깨를 드러내는 원작 상의는 흰 몸판으로 덮었다(전시 장면). 키는 다른 인물보다 큰 1.34 m(원작: 늘씬한 장신).
- 귀: 정령이라 엘프 귀가 없다. 긴 머리에 덮여 보이지 않으므로 귀를 만들지 않는다.
- 표정: 키트 5종 + shout(호통), fluster(당황), smug(도도한 미소), aim(조준: 왼눈 감음, 교정 키 없음)
  + blink 교정 키.

npm run model -- art/blender/characters/sila.py
npm run shot -- characters/sila.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import fairy  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame, catmull  # noqa: E402

cb.reset()
M_ = elf.mat
e = fairy.Fairy("sila", ears=None, height=1.34, head=0.44, leg=1.12, arm=1.04, limb=0.94, chest=0.55, bust=0.60, hips=1.04,
                segs=0.72, hand_q=0.45, cheek=0.09)
k = e.k

# ---- 팔레트 (원작 카드·소개 이미지 눈 실측)
white = M_("si_white", "#f7f6f4")
white_d = M_("si_white_d", "#dcdbe4")
gold = M_("si_gold", "#e6b878")
gold_d = M_("si_gold_d", "#b8834a")
black = M_("si_black", "#3a3640")
teal = M_("si_teal", "#7fd6d6")
gem = M_("si_gem", "#a9dcf2")

# ---- 얼굴: 위 하늘색·아래 노란빛 눈, 반쯤 감은 도도한 눈매, 눈꼬리 속눈썹이 굵다
e.face(eye_color="#9cc0e2", iris_dark="#5f80b2", iris_light="#f5e7a6", pupil="#3d5679",
       lash="#4a3a42", brow="#b8c6a8", brow_th=0.95, blush="#f6a8a8", blush_size=1.05,
       base={"eye": {"top": 0.017, "ktop": 4.3, "cout": 0.021, "tilt_out": 0.004, "tilt_in": -0.002},
             "brow": {"dz": 0.064, "ang": -4.0, "arch": 0.003},
             "mouth": {"w": 0.018, "curve": 0.0010}},
       expr={
           # 호통: 눈을 치켜뜨고 입을 크게 (코미·버터에게 "난 정령이야!")
           "shout": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.014},
                     "brow": {"ang": -22.0, "dz": 0.054, "th": 0.0070},
                     "mouth": {"w": 0.036, "open": 0.034, "curve": -0.0010, "top_arch": 0.006}},
           # 당황: 동그래진 눈, 작은 동공, 물결 입 (털리는 전투력 측정기)
           "fluster": {"eye": {"top": 0.034, "ktop": 2.4, "bot": 0.056},
                       "iris": {"pupil": 0.55},
                       "brow": {"ang": 18.0, "dz": 0.074, "arch": -0.002},
                       "mouth": {"w": 0.024, "curve": -0.0030, "open": 0.0060, "wave": 0.0022}},
       })
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.016, "lift": 0.008, "ktop": 4.4}, "mouth": {"w": 0.024, "curve": 0.0045}},
             L={"brow": {"dz": 0.066, "ang": 2.0}}, R={"brow": {"dz": 0.060, "ang": -8.0}},
             corner=(0.0070, 0.0020), mouth_dx=0.0010 * k)
c2.face_expr(e, "aim", both={"mouth": {"w": 0.016, "curve": -0.0006}},
             L={"eye": {"close": 1.0}, "brow": {"dz": 0.056, "ang": -12.0}},
             R={"eye": {"top": 0.024, "ktop": 3.6, "tilt_in": -0.008}, "brow": {"dz": 0.060, "ang": -10.0}},
             blink_fix=False)

# ---- 머리: 연민트빛 흰 긴 생머리 (허벅지), 옆으로 넘긴 앞머리, 오른쪽 바깥으로 뻗친 옆머리
HAIR, HAIR_D, HAIR_L, HAIR_TIP = "#e4eedb", "#b3c4a9", "#f4f8ee", "#d9d0e8"


def locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 1.9
    elif lk["region"] in ("side", "back"):
        lk["p"] = 1.9


h = c2.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.10, lock_fn=c2.lock_edit(locks))
h.cap(front=28, side=-8, back=-48, part=18, segs=16, rows=5)
h.bangs(n=7, spread=58, tip_el=-2, sweep=12, part=18, jag=0.30, curl=1.0, seed=6.0)
h.sides(length=0.40, width=0.074, az=64, curl=0.2, thick=1.0)
h.back(length=0.62, n=9, spread=98)
h.shine(el=50, spread=70, n=2, size=0.80)
o = h.off
# 오른쪽(-X) 볼 옆에서 바깥으로 뻗친 다발 (원작의 날리는 옆머리)
h.strand([h.sp(-62, 16, o * 1.05), h.sp(-74, 2, o * 1.35), h.sp(-84, -10, o * 1.8) + V((-0.020, 0.004, 0)) * k,
          h.sp(-88, -16, o * 2.2) + V((-0.050, 0.008, 0.012)) * k],
         0.052 * k, 0.014 * k, n=12, segs=8, taper=[(0, 0.8), (0.3, 1.0), (0.7, 0.75), (1, 0.0)])
h.ahoge(az=-6, height=0.045, curl=0.9, width=0.014)


# ---- 금색 날개 서클릿: 머리 덩어리를 두르는 띠 + 양옆에서 위·뒤로 솟는 줄무늬 날 두 개씩
def circlet_el(az):
    a = abs(az)
    return lerp(52.0, 22.0, smoothstep(0.0, 100.0, a))


for sg, nm in ((1, "circlet_L"), (-1, "circlet_R")):   # 관자놀이 위에서 뒤로 감기는 옆 띠 (앞은 앞머리에 묻힘)
    c2.on_hair_band(e, h, gold, az0=sg * 52.0 if sg > 0 else -128.0, az1=128.0 if sg > 0 else -52.0, el_fn=circlet_el,
                    width=0.016, th=0.006, lift=0.002, name=nm, n=18)


def wing_blades(buf):
    w = {"head": 1.0}
    for sg in (1, -1):
        for j, (az, ln, wd, rise) in enumerate(((70.0, 0.120, 0.046, 1.0), (94.0, 0.090, 0.036, 0.8))):
            a_ = sg * az
            s_ = h.s_of_el(a_, circlet_el(a_))
            p0, n0 = h.path(a_, s_, 0.004 * k)
            back = V((0, 1, 0))
            up = V((0, 0, 1))
            out = V((sg, 0, 0))
            ctrl = [p0 - n0 * 0.006 * k, p0 + n0 * 0.012 * k + up * 0.030 * k * rise,
                    p0 + n0 * 0.022 * k + up * 0.075 * k * rise + back * 0.020 * k,
                    p0 + n0 * 0.024 * k + up * ln * k * rise + back * 0.060 * k + out * 0.004 * k]
            P = catmull(ctrl, 14)
            # 넓은 면이 바깥(법선)을 보는 납작한 날. 띠 단위로 금·짙은 금을 번갈아 (원작 줄무늬)
            nseg = 6
            for sgi in range(nseg):
                i0 = sgi * (len(P) - 1) // nseg
                i1 = (sgi + 1) * (len(P) - 1) // nseg
                st = []
                for i in range(i0, i1 + 1):
                    t = i / (len(P) - 1)
                    r = wd * k * 0.5 * (math.sin(math.pi * min(1.0, 0.25 + t * 0.85)) ** 0.7) * (1 - t ** 3)
                    ref = (back + out * 0.8).normalized()   # 넓은 면이 옆·뒤를 비스듬히 본다 (앞에서도 폭이 읽히게)
                    st.append({"c": P[i], "rx": max(r, 0.0008 * k), "ry": 0.0036 * k, "w": w, "ref": tuple(ref)})
                loft(buf, st, segs=6, cap0="flat", cap1="flat", mat=gold if sgi % 2 == 0 else gold_d)


e.part("wing_blades", "head", wing_blades)

# ---- 몸판: 흰 상의 + 금색 목장식(하늘색 보석) + 가슴을 엇갈려 감은 금색 띠
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(white, hem=hz - 0.010 * k, collar=None, flare=0.010)


def neck_piece(buf):
    w = {"neck": 0.4, "chest": 0.6}
    z = e.torso_top + 0.006 * k
    band(buf, (0, 0.004 * k, z), (0, 0, 1), (1, 0, 0), 0.052 * k, 0.048 * k, 0.014 * k, 0.005 * k, segs=16, mat=gold,
         w=w)
    # 앞 가운데 마름모 보석 + 금테
    p, n = e.torso_point(e.torso_top - 0.012 * k, 0, 0.022 * k)
    Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    c2.prism(buf, c2.diamond_poly(0.030 * k, 0.034 * k), 0.004 * k, Mx, mat=gold, w=w)
    c2.prism(buf, c2.diamond_poly(0.020 * k, 0.024 * k), 0.004 * k, Mx @ Matrix.Translation((0, -0.003 * k, 0)),
             mat=gem, w=w, chamfer=0.0015 * k)
    # 목장식 양옆으로 내려오는 짧은 금색 판 (어깨 받침)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.010 * k, sg * 40, 0.016 * k)
        Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 20), 4, "Y")
        rbox(buf, (0.034 * k, 0.005 * k, 0.012 * k), Mx, mat=gold, w=w, r=0.4, segs=1)


e.part("neck_piece", "body", neck_piece)
for sg in (1, -1):   # 가슴을 엇갈려 감은 금색 띠 (어깨 → 반대쪽 허리)
    e.strap(gold, [("torso", e.torso_top - 0.010 * k, sg * 48, 0.012 * k), ("torso", cz + 0.020 * k, sg * 20, 0.014 * k),
                   ("torso", cz - 0.030 * k, -sg * 10, 0.014 * k), ("torso", wz + 0.004 * k, -sg * 40, 0.013 * k)],
            width=0.010, th=0.003, name=f"wrap_{'L' if sg > 0 else 'R'}")
e.ring(gold, "torso", cz - 0.040 * k, h=0.010, th=0.003, off=0.012, name="under_bust")

# ---- 허리: 검은 끈 + 금색 감은 띠 두 줄 + 금색 잎 장식
e.belt(black, z=wz - 0.014 * k, h=0.010, th=0.004, off=0.013)
for dz, nm in ((0.004, "wrap_a"), (-0.032, "wrap_b")):
    e.ring(gold, "torso", wz + dz * k, h=0.009, th=0.003, off=0.016, name=nm)


def leaf(buf, Mx, w):
    pts = []
    for i in range(12):
        t = i / 11
        a = math.pi * t
        pts.append((0.011 * k * math.sin(a) * (1.0 if i < 12 else 1), 0.026 * k * (0.5 - t)))
    poly = [(0.0, 0.016 * k), (0.010 * k, 0.004 * k), (0.008 * k, -0.008 * k), (0.0, -0.016 * k),
            (-0.008 * k, -0.008 * k), (-0.010 * k, 0.004 * k)]
    c2.prism(buf, poly, 0.004 * k, Mx, mat=gold, w=w, chamfer=0.0015 * k)
    _ = pts


e.gear("waist_leaf", ("torso", wz - 0.014 * k, 0.0, 0.018 * k), leaf)

# ---- 치마: 짧은 흰 치마 + 뒤로 길게 늘어진 자락 (그리스풍)
q0 = e.q
e.q = 0.40
e.pants(white_d, length=0.10, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
skirt = c2.Shell(e, white, wz - 0.006 * k, e.crotch_z - 0.024 * k, off=0.020, th=0.004, skirt=True, cols=26, rows=5,
                 flare=[(0.0, 0.0), (0.5, 0.014), (1.0, 0.030)], pleat=(0.006, 9, 0.2), pleat_mat=white_d, cover=True)
skirt.hem_trim(gold, width=0.008, th=0.002)
skirt.done("skirt", angle=30.0)
drape = c2.Shell(e, white, wz - 0.010 * k, e.knee_z - 0.050 * k, gap=105.0, off=0.030, th=0.004,
                 skirt=True, cols=14, rows=8, flare=[(0.0, 0.0), (0.4, 0.030), (1.0, 0.070)])
drape.hem_trim(white_d, width=0.008, th=0.002)
drape.done("drape", angle=35.0)

# ---- 팔: 왼팔(+X) 긴 흰 토시 + 청록 소용돌이, 오른팔(-X) 검은 팔찌 + 흰 팔보호대
c2.arm_tube(e, white, "L", 0.10, 0.96, off=0.008, extra=lambda t: 0.006 * smoothstep(0.5, 1.0, t), name="sleeve_L")
e.ring(gold, "arm_L", 0.12, h=0.012, th=0.003, off=0.010, name="sleeve_L_top")
for t in (0.88, 0.94):
    e.ring(gold, "arm_L", t, h=0.008, th=0.003, off=0.016, name=f"sleeve_L_cuff{t}")


def swirl(buf, Mx, w):
    c2.crescent(buf, Mx, 0.017 * k, width=0.30, th=0.14, a0=-60.0, a1=250.0, mat=teal, w=w, n=14, segs=5)
    c2.crescent(buf, Mx @ Matrix.Translation((0.004 * k, 0, -0.003 * k)), 0.008 * k, width=0.40, th=0.18, a0=100.0,
                a1=380.0, mat=teal, w=w, n=10, segs=5)


sw_buf = Buf()   # 무늬는 아웃라인 없는 노드로 (작은 장식에 먹선 테가 두껍게 끼지 않게)
for t in (0.36, 0.64):
    a = e.anchor(("arm_L", t, 90.0, 0.0115 * k))
    swirl(sw_buf, a.matrix(), a.w)
e.add(sw_buf.obj("sila_swirls", smooth=True), group="arms", tag="swirls", node="swirls", props={"noOutline": 1})
e.ring(black, "arm_R", 0.24, h=0.020, th=0.004, off=0.004, name="armlet_R")
for t in (0.18, 0.30):
    e.ring(gold, "arm_R", t, h=0.007, th=0.003, off=0.007, name=f"armlet_R_gold{t}")
c2.arm_tube(e, white, "R", 0.60, 0.95, off=0.006, extra=lambda t: 0.004 * smoothstep(0.6, 0.95, t), name="bracer_R")
for t in (0.64, 0.90):
    e.ring(gold, "arm_R", t, h=0.008, th=0.003, off=0.012, name=f"bracer_R_gold{t}")

# ---- 다리: 맨다리 + 흰 샌들 + 엇갈려 감은 금색 끈 (윗단 금색 잎)
e.boots(white, top=0.90, sole=(gold_d, 0.012), off=0.008, toe=0.003)
for sd, sg in (("L", 1), ("R", -1)):
    rows_t = (0.90, 0.80, 0.70)
    for i in range(len(rows_t) - 1):
        ta, tb = rows_t[i], rows_t[i + 1]
        for a0, a1 in ((-55.0, 55.0), (55.0, -55.0)):
            e.strap(gold, [(f"leg_{sd}", ta, a0, 0.010 * k), (f"leg_{sd}", (ta + tb) / 2, (a0 + a1) / 2, 0.011 * k),
                           (f"leg_{sd}", tb, a1, 0.010 * k)], width=0.010, th=0.0026,
                    name=f"lace_{sd}{i}{int(a0)}")
    e.ring(gold, f"leg_{sd}", 0.66, h=0.012, th=0.003, off=0.008, name=f"lace_top_{sd}")
    a = e.anchor((f"leg_{sd}", 0.65, sg * 70.0, 0.010 * k))
    e.part(f"lace_leaf_{sd}", "body", lambda buf, a=a: leaf(buf, a.matrix(tilt=-30.0), a.w))

# ---- 활 (별도 노드 sila_bow, 왼손) + 얼음 화살 (별도 노드 sila_arrow, 오른손, 발광)
e.finalize()
for nm in ("sila_hair", "sila_hair_in"):
    ob = bpy.data.objects.get(nm)
    if ob is not None:
        c2.vc_gradient(ob, HAIR if nm == "sila_hair" else HAIR_D,
                       [(0.20 * k, HAIR_TIP if nm == "sila_hair" else "#b0a6c2"),
                        (0.44 * k, HAIR if nm == "sila_hair" else HAIR_D)], tol=10)


def bow():
    buf = Buf()
    W, d, pn = e.W["L"], e.adir["L"], e.palm_n["L"]
    g = W + d * 0.036 * k + pn * 0.024 * k
    wood = M_("si_bow", "#e3b479")
    wood_d = M_("si_bow_d", "#c08a52")
    string_m = M_("si_string", "#f2efe6")
    H = 0.36 * k

    def limb(z):
        u = abs(z) / H
        y = -0.050 * k * (1 - u * u) + 0.030 * k * smoothstep(0.78, 1.0, u)   # 앞으로 휜 활 + 끝 되휨
        return V((g.x, g.y + y, g.z + z))
    pts = [limb(lerp(-H, H, i / 20)) for i in range(21)]
    st = []
    for i, q in enumerate(pts):
        u = abs(i / 20 - 0.5) * 2
        r = lerp(0.0105, 0.0055, u) * k
        st.append({"c": q, "rx": r * 1.2, "ry": r, "w": {}, "ref": (1, 0, 0)})
    loft(buf, st, segs=8, cap0="round", cap1="round", mat=wood)
    # 금색 감은 띠 (손잡이 + 사지 군데군데)
    for zz, hh in ((0.0, 0.050), (0.42, 0.016), (0.62, 0.014), (-0.42, 0.016), (-0.62, 0.014)):
        z = zz * H
        c = limb(z)
        T = (limb(z + 0.002 * k) - limb(z - 0.002 * k)).normalized()
        u = abs(zz)
        r = lerp(0.0105, 0.0055, u) * k
        band(buf, c, T, (1, 0, 0), r * 1.35, r * 1.18, hh * k, 0.003 * k, segs=10, mat=gold, w={})
    band(buf, limb(0.0), V((0, 0, 1)), (1, 0, 0), 0.0105 * k * 1.30, 0.0105 * k * 1.12, 0.036 * k, 0.002 * k, segs=10,
         mat=wood_d, w={})
    # 끝 하늘색 결정
    for sgz in (1, -1):
        tip = limb(sgz * H)
        T = (limb(sgz * H) - limb(sgz * (H - 0.01 * k))).normalized()
        loft(buf, [{"c": tip - T * 0.004 * k, "rx": 0.009 * k, "ry": 0.009 * k, "w": {}},
                   {"c": tip + T * 0.012 * k, "rx": 0.010 * k, "ry": 0.010 * k, "w": {}},
                   {"c": tip + T * 0.036 * k, "rx": 0.0008 * k, "ry": 0.0008 * k, "w": {}}], segs=6, cap0="flat",
             cap1="flat", mat=gem, p=1.0)
    # 시위
    a, b = limb(H - 0.004 * k), limb(-H + 0.004 * k)
    loft(buf, [{"c": a, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": {}},
               {"c": b, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": {}}], segs=4, cap0="flat", cap1="flat", mat=string_m)
    ob = buf.obj("sila_bow_tmp", angle=40.0)
    return c2.prop(e, "bow", ob, "hand_L", outline=0.0025)


def arrow():
    buf = Buf()
    W, d, pn = e.W["R"], e.adir["R"], e.palm_n["R"]
    g = W + d * 0.036 * k + pn * 0.024 * k
    ice = M_("UNLIT_si_ice", "#d6f6ff", unlit=True)
    ice_d = M_("si_ice_d", "#8fd6f2")
    ax = V((0.10, -0.25, -1.0)).normalized()        # 손에서 아래·앞으로 (원작 카드: 화살촉이 아래)
    a, b = g - ax * 0.22 * k, g + ax * 0.20 * k
    loft(buf, [{"c": a, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": {}},
               {"c": b, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": {}}], segs=5, cap0="flat", cap1="flat", mat=ice)
    loft(buf, [{"c": b - ax * 0.004 * k, "rx": 0.0055 * k, "ry": 0.0055 * k, "w": {}},
               {"c": b + ax * 0.012 * k, "rx": 0.010 * k, "ry": 0.010 * k, "w": {}},
               {"c": b + ax * 0.044 * k, "rx": 0.0006 * k, "ry": 0.0006 * k, "w": {}}], segs=4, cap0="flat",
         cap1="flat", mat=ice, p=1.0)
    side = ax.cross(V((0, 0, 1))).normalized()
    for sgn in (1, -1):    # 깃 (얼음 결정 깃 두 장)
        c = a + ax * 0.030 * k + side * sgn * 0.008 * k
        loft(buf, [{"c": c - ax * 0.026 * k, "rx": 0.0006 * k, "ry": 0.0006 * k, "w": {}},
                   {"c": c, "rx": 0.007 * k, "ry": 0.0015 * k, "w": {}, "ref": tuple(side)},
                   {"c": c + ax * 0.010 * k, "rx": 0.0006 * k, "ry": 0.0006 * k, "w": {}}], segs=4, cap0="flat",
             cap1="flat", mat=ice_d, p=1.0)
    ob = buf.obj("sila_arrow_tmp", angle=40.0)
    pr = c2.prop(e, "arrow", ob, "hand_R", outline=0.0)
    pr["noOutline"] = 1
    return pr


bow()
arrow()
e.export("characters/sila.glb")
