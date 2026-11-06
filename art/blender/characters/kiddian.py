"""키디언: 용족 사도. 엘리아스 침공전에서 모나티엄 방어 전력(교주 차원)으로 배치됐다가, 리츠·칸나와 함께
흑뉴아에게 힘으로 제압된다(1막 M2 「방어선」 시청 방어선).

원작 키디언(트릭컬 리바이브, '자발적 아웃사이더', 우울 성격 용족)의 기본 복장으로 만든 카메오 모델.
- 유지한 식별 요소: 회보라 머리(헝클어진 단발 + 바보털), 귀 아래에서 낮게 묶어 무릎까지 늘어뜨린 양 갈래(짙은 묶음 띠 +
  밝은 고리), 머리에 박힌 둥근 흑요석 알, 바깥으로 휜 짙은 뿔과 뿔 뿌리의 돌 부스러기, 짧은 뾰족 귀, 졸린 반쯤 감은
  회보라 눈, 회색 누더기 튜닉(목둘레 끈, 들쭉날쭉한 밑단), 밧줄 허리끈과 작은 자루, 왼팔 소매의 밝은 줄 2개와
  손목 띠, 다리·발의 흰 붕대와 허벅지 띠, 갈색 막의 용 날개, 짙은 꼬리와 끝의 붕대.
- 재해석: 3D SD 비율에 맞춰 날개·꼬리에 본 사슬(wing_*, tail_*)을 넣었다. 흑요석(원작에서 좋아하는 것)은 머리 장식
  알로 두었다. 맨발이고 정강이에서 발목까지 붕대를 감았다.
- 표정: 키트 5종 + yawn(하품, 원작 카드) + gloomy(우울) + panic(허둥지둥) + dazed(제압된 뒤 멍한 얼굴) + blink 교정 키.
근거: docs/art/characters-cameo3.md

npm run model -- art/blender/characters/kiddian.py
npm run shot -- characters/kiddian.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import dragon_common as dc  # noqa: E402
from elf import V, Matrix, Buf, band, lerp  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("kiddian", height=1.10, head=0.45, leg=1.0, chest=0.18, segs=0.70, hand_q=0.55, cheek=0.10,
            ear_len=0.060, ear_width=0.046, ear_angle=8.0, ear_sweep=18.0)
k = e.k

# ---- 팔레트 (원작 카드 실측: 머리 #706274, 튜닉 #5f5d66, 막 #a78663, 붕대 #f1ebe6)
tunic = M_("kd_tunic", "#615e69")
tunic_d = M_("kd_tunic_d", "#46434e")
rope = M_("kd_rope", "#c3a47a")
rope_d = M_("kd_rope_d", "#97794f")
sack = M_("kd_sack", "#ad8a5f")
bandage = M_("kd_bandage", "#e6e3ea")
bandage_d = M_("kd_bandage_d", "#bdb4be")
band_dk = M_("kd_band", "#3d3a45")
horn_m = M_("kd_horn", "#4c4456")
rock = M_("kd_rock", "#c2b8aa")
rock_d = M_("kd_rock_d", "#9a8f83")
obsid = M_("kd_obsidian", "#3a3443")
mem = M_("kd_membrane", "#b38c60")
wbone = M_("kd_wingbone", "#4a4252")
tail_m = M_("kd_tail", "#564c62")
tail_b = M_("kd_tail_belly", "#7c718a")

# ---- 얼굴: 회보라 눈, 졸려서 반쯤 감긴 눈, 걱정스러운 눈썹, 작은 입
e.face(eye_color="#8d86a8", iris_dark="#4a4364", iris_light="#d9d3ec", pupil="#2a2438",
       lash="#3a3044", brow="#4f4560", brow_th=0.95, blush="#f6b0ac", blush_size=1.1,
       base={"eye": {"top": 0.007, "cin": 0.003, "cout": 0.007, "ktop": 5.0, "tilt_in": 0.002},
             "iris": {"cz": 0.0010},
             "brow": {"dz": 0.060, "ang": 6.0, "arch": 0.002},
             "mouth": {"w": 0.015, "curve": 0.0010}},
       expr={
           # 하품 (원작 카드): 눈을 감고 입을 동그랗게
           "yawn": {"eye": {"close": 1.0, "lift": 0.006},
                    "brow": {"ang": 10.0, "dz": 0.064},
                    "mouth": {"w": 0.022, "open": 0.032, "curve": -0.0005, "top_arch": 0.0060}},
           # 우울 (자발적 아싸): 더 내리깐 눈, 아래를 보는 홍채, 처진 눈썹, 물결 입
           "gloomy": {"eye": {"top": 0.003, "cin": 0.004, "cout": 0.000, "ktop": 5.0, "tilt_in": 0.004},
                      "iris": {"cz": -0.0030},
                      "brow": {"ang": 16.0, "dz": 0.058},
                      "mouth": {"w": 0.014, "curve": -0.0028, "wave": 0.0012}},
           # 허둥지둥: 동그래진 눈, 작은 동공, 물결 입
           "panic": {"eye": {"top": 0.034, "ktop": 2.3, "bot": 0.056},
                     "iris": {"pupil": 0.55, "rx": 0.025, "ry": 0.033},
                     "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                     "mouth": {"w": 0.024, "curve": -0.0025, "open": 0.0090, "wave": 0.0020}},
           # 제압된 뒤 (M2 시청 방어선): 초점 없는 반쯤 뜬 눈, 작은 동공, 살짝 벌린 입
           "dazed": {"eye": {"top": 0.010, "cin": 0.004, "cout": 0.004, "tilt_in": 0.006, "tilt_out": -0.004,
                             "ktop": 3.4},
                     "iris": {"pupil": 0.42, "cz": -0.0030},
                     "brow": {"ang": 18.0, "dz": 0.062},
                     "mouth": {"w": 0.020, "open": 0.0075, "curve": -0.0020, "wave": 0.0014}},
       })

# ---- 머리 (헤어 v2): 헝클어진 단발(끝이 바깥으로 뻗침), 바보털, 귀 아래 낮은 양 갈래
HAIR = "#6f6378"


def kd_locks(h, lk):
    if lk["region"] in ("side", "back"):
        lk["curl"] = 0.014 * k      # 끝이 바깥으로 뻗친다
        lk["p"] = 1.6
    if lk["region"] == "front":
        lk["p"] = 1.9


h = c2.hair(e, HAIR, dark="#4d4459", light="#9a8fab", lock_fn=c2.lock_edit(kd_locks), volume=1.14)
h.cap(front=28, side=-10, back=-50, part=-10)
h.bangs(n=7, spread=58, tip_el=-4, jag=0.35, sweep=-6, curl=0.9, seed=11.0)
h.sides(length=0.035, width=0.086, n=2, puff=1.5)
h.back(length=0.035, n=9, spread=98)
h.ahoge(az=-8, height=0.070, curl=1.4, width=0.017)
h.shine(el=52, spread=72, size=1.0)

# 양 갈래: 귀 뒤 아래에서 낮게 묶어 어깨 뒤로 늘어뜨린다. 끝은 무릎 근처에서 바깥으로 휘며 뾰족하게 모인다
o = h.vol
sz, cz, wz, hz = e.shoulder_z, e.chest_z, e.waist_z, e.hipj_z
TAILS = {}
for side, s in (("L", 1), ("R", -1)):
    az = s * 116.0
    root, rn = h.path(az, h.s_of_el(az, -20.0), -o * 0.3)
    ctrl = [root,
            V((s * 0.170 * k, 0.058 * k, e.chin - 0.030 * k)),
            V((s * 0.192 * k, 0.074 * k, sz - 0.020 * k)),
            V((s * 0.205 * k, 0.078 * k, cz - 0.040 * k)),
            V((s * 0.222 * k, 0.070 * k, wz - 0.040 * k)),
            V((s * 0.246 * k, 0.058 * k, hz - 0.060 * k)),
            V((s * 0.282 * k, 0.050 * k, e.knee_z + 0.040 * k)),
            V((s * 0.330 * k, 0.060 * k, e.knee_z - 0.004 * k))]
    tl = c2.Tail(h, f"hair_tail_{side}", ctrl, 0.086 * k, 0.040 * k, bones=3, parent="chest", root_bone="head",
                 t_hold=0.50, root_w=0.80, clumps=((0.30, 0.50, 0.84),),
                 ref_fn=lambda t, q, s=s: V((s * 1.0, 0.35, 0.0)))
    tl.tie(band_dk, t=0.05, size=1.0, h_=0.024, th=0.007)
    tl.tie(rope, t=0.11, size=0.92, h_=0.010, th=0.006)
    TAILS[side] = tl


# 흑요석 알: 앞머리 위 셋 + 양옆 하나씩 (원작 카드의 둥근 짙은 돌)
def obsidians(buf):
    for az, el, r in ((-12.0, 30.0, 0.0105), (4.0, 36.0, 0.0145), (18.0, 30.0, 0.0090), (-70.0, 6.0, 0.0100),
                      (74.0, -4.0, 0.0100)):
        p, n = h.path(az, h.s_of_el(az, el), 0.0015 * k)
        dc.stud(buf, p, n, r * k, obsid, w={"head": 1.0}, depth=0.55)


e.part("obsidian", "head", obsidians)

# ---- 뿔: 정수리 양옆에서 바깥으로 뻗었다가 끝이 위로 휜다. 뿌리에 돌 부스러기
for side, s in (("L", 1), ("R", -1)):
    az = s * 44.0
    P, r_at, base, nrm = dc.horn(e, h, f"horn_{side}", az=az, el=46.0, r0=0.034, mat=horn_m, flat=0.78,
                                 taper=0.95, segs=9,
                                 ctrl=[(s * 0.036, 0.008, 0.016), (s * 0.074, 0.012, 0.032),
                                       (s * 0.104, 0.002, 0.064), (s * 0.106, -0.016, 0.100)])

    def rubble(buf, base=base, nrm=nrm, s=s):
        a = V((0, 0, 1)) if abs(nrm.z) < 0.9 else V((1, 0, 0))
        A = nrm.cross(a).normalized()
        B = nrm.cross(A).normalized()
        for i in range(7):
            ang = 2 * math.pi * i / 7 + 0.4
            rr = (0.026 + 0.004 * ((i * 37) % 3) / 2) * k
            c = base + (A * math.cos(ang) + B * math.sin(ang)) * rr + nrm * 0.003 * k
            dc.stud(buf, c, nrm, (0.0085 + 0.0022 * (i % 3)) * k, rock if i % 2 else rock_d, w={"head": 1.0},
                    depth=0.80, segs=6, rings=4)
    e.part(f"horn_rubble_{side}", "head", rubble)

# ---- 튜닉: 회색 몸판 + 들쭉날쭉한 누더기 밑단 + 목둘레 밧줄 끈
e.shirt(tunic, hem=hz - 0.004 * k, collar=None, flare=0.012)
sk = c2.Shell(e, tunic, wz + 0.006 * k, e.crotch_z - 0.028 * k, off=0.016, th=0.004, skirt=True, cols=30, rows=6,
              flare=[(0.0, 0.0), (0.5, 0.010), (1.0, 0.024)])
# 밑단을 톱니처럼 (원작의 해진 삼각 자락): 마지막 두 줄의 높이를 방위에 따라 내린다
R_, C_ = sk.rows, sk.cols
TEETH = [0.034, 0.020, 0.040, 0.018, 0.030, 0.046, 0.022, 0.034, 0.016, 0.038]
for j in range(C_):
    a = j / C_ * len(TEETH)
    i0 = int(a)
    f = a - i0
    tri = 1.0 - abs(f - 0.5) * 2.0
    dz = TEETH[i0 % len(TEETH)] * tri * k
    for i, frac in ((R_ - 1, 1.0), (R_ - 2, 0.35)):
        for base_i in (0, R_ * C_):
            sk.buf.v[base_i + i * C_ + j].z -= dz * frac
sk.done("tunic_skirt")
e.ring(rope, "torso", e.torso_top - 0.016 * k, h=0.008, th=0.004, off=0.014, name="neck_cord")

# 소매: 왼팔만 긴 회색 소매 (밝은 줄 2개 + 짙은 손목 띠), 오른팔은 맨팔 + 짙은 손목 띠
c2.arm_tube(e, tunic, "L", 0.0, 0.90, off=0.011, name="sleeve_L")
for t in (0.40, 0.47):
    e.ring(rope, "arm_L", t, h=0.008, th=0.003, off=0.014, name=f"sleeve_stripe_{t}")
e.ring(band_dk, "arm_L", 0.90, h=0.020, th=0.005, off=0.012, name="cuff_L")
e.ring(band_dk, "arm_R", 0.88, h=0.022, th=0.005, off=0.004, name="cuff_R")

# 밧줄 허리끈 + 매듭 + 작은 자루 (왼쪽 앞)
e.ring(rope, "torso", wz - 0.006 * k, h=0.013, th=0.006, off=0.024, name="rope_belt")


def sack_geo(buf, Mx, w):
    R3 = Mx.to_3x3()
    c = Mx @ V((0, -0.022 * k, -0.030 * k))
    c2.ellipsoid(buf, c, (R3 @ V((0, 0, 1))).normalized(), (R3 @ V((1, 0, 0))).normalized(),
                 (R3 @ V((0, -1, 0))).normalized(), 0.032 * k, 0.029 * k, 0.021 * k, segs=10, rings=6, mat=sack, w=w)
    band(buf, Mx @ V((0, -0.020 * k, 0.000)), R3 @ V((0, 0, 1)), R3 @ V((1, 0, 0)), 0.012 * k, 0.010 * k,
         0.006 * k, 0.003 * k, segs=10, mat=rope_d, w=w)
    c2.ellipsoid(buf, Mx @ V((0, -0.020 * k, 0.008 * k)), (R3 @ V((0, 0, 1))).normalized(),
                 (R3 @ V((1, 0, 0))).normalized(), (R3 @ V((0, -1, 0))).normalized(), 0.007 * k, 0.010 * k,
                 0.007 * k, segs=8, rings=4, mat=sack, w=w)


e.gear("sack", ("torso", wz - 0.010 * k, 38.0, 0.022 * k), sack_geo)


def knot(buf, Mx, w):
    R3 = Mx.to_3x3()
    c2.ellipsoid(buf, Mx @ V((0, -0.006 * k, 0)), (R3 @ V((1, 0, 0))).normalized(), (R3 @ V((0, 0, 1))).normalized(),
                 (R3 @ V((0, -1, 0))).normalized(), 0.012 * k, 0.008 * k, 0.007 * k, segs=8, rings=4, mat=rope, w=w)
    for dx in (-0.006, 0.006):
        p0 = Mx @ V((dx * k, -0.006 * k, -0.004 * k))
        p1 = Mx @ V((dx * 2.2 * k, -0.008 * k, -0.040 * k))
        elf.loft(buf, [{"c": p0, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
                       {"c": p1, "rx": 0.0030 * k, "ry": 0.0030 * k, "w": w}], segs=6, cap0="flat", cap1="round",
                 mat=rope)


e.gear("rope_knot", ("torso", wz - 0.006 * k, -18.0, 0.030 * k), knot)

# ---- 다리: 맨다리 + 흰 붕대 (허벅지·정강이·발) + 허벅지 갈색 띠
q0 = e.q
e.q = 0.35    # 튜닉 속 반바지 (거의 안 보임)
e.pants(tunic_d, length=0.10, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
for sd in ("L", "R"):
    c2.leg_tube(e, bandage, sd, 0.38, 0.50, off=0.004, name=f"thigh_wrap_{sd}")
    c2.leg_tube(e, bandage, sd, 0.72, 0.97, off=0.004, name=f"shin_wrap_{sd}")
    for t in (0.44, 0.78, 0.86, 0.93):
        e.ring(bandage_d, f"leg_{sd}", t, h=0.004, th=0.0025, off=0.007, name=f"wrap_line_{sd}{t}")
e.ring(rope_d, "leg_L", 0.33, h=0.014, th=0.004, off=0.004, name="thigh_band_L")

# ---- 용 날개 (갈색 막) + 꼬리 (끝 근처 붕대)
dc.wings(e, span=0.33, height=0.32, mem=mem, bone=wbone, angle=138.0, sweep=18.0, raise_=10.0,
         z=e.chest_z + 0.070 * k)
bz = hz + 0.030 * k
bp, bn = e.torso_point(bz, 180.0, -0.012 * k)
ctrl = [bp,
        bp + V((0.0, 0.090 * k, -0.060 * k)),
        V((0.040 * k, bp.y + 0.170 * k, 0.170 * k)),
        V((0.110 * k, bp.y + 0.230 * k, 0.050 * k)),
        V((0.210 * k, bp.y + 0.235 * k, 0.034 * k)),
        V((0.300 * k, bp.y + 0.180 * k, 0.040 * k)),
        V((0.340 * k, bp.y + 0.110 * k, 0.066 * k))]


def tail_extra(buf, at, r_at, wfn):
    for t in (0.70, 0.745):
        dc.tail_band(buf, at, r_at, wfn, t, bandage, h=0.020, th=0.003, k=k)


dc.tail(e, ctrl, 0.052, mat=tail_m, belly=tail_b, bones=4, extra=tail_extra, segs=10, n=22)

e.finalize()
e.export("characters/kiddian.glb")
