"""뮤트: 모나티엄의 전 첩보반장이자 '정보의 정령'. 엘리아스 침공전에서 교주를 기절시켜 데리고 나가고, 수용소의
엘레나 일행에게 다가가 모나티엄 복구를 제안한다. 이 작품에서는 화면 밖에서 HUD와 환경 이상 현상으로 개입한다.

원작 뮤트(트릭컬 리바이브, '배후에 숨은 전략가')의 대표 외형 하나로 만든 카메오 모델.
(원작에는 '원래의 뮤트'와 지금의 뮤트 구분이 있지만, 사용자 결정에 따라 대표 외형 하나만 만든다.)
- 유지한 식별 요소: 검은 단발(끝이 바깥으로 뻗침)과 일자 앞머리, 앞머리를 가로지르는 청록 띠, 바보털, 청록 눈과
  능글맞은 메롱 표정, 왼쪽 귀의 청록 귀걸이, 검은 초커, 검은 깃 셔츠와 넥타이, 가슴 멜빵, 검은 벨트와 은색 버클,
  남회색 바지, 은색 X 버클 부츠, 손가락 없는 검은 장갑, 어깨에 걸친 긴 검은 코트, 손가락에서 늘어진 청록 실과
  가시 추, 벨트 아래 청록 마름모 표식 주머니.
- 재해석: 정보의 정령다운 데이터 실은 UNLIT 청록 발광(별도 노드 mute_threads)으로, 실 끝 추는 은색 가시로 했다.
  코트는 소매에 팔을 넣지 않고 어깨에 걸친 망토형으로 단순화했다.
- 체형: 원작에서 엘프로 위장해 지냈고 스탠딩도 엘프 귀·엘프 체격이라 엘프 키트 기본 체형을 그대로 쓴다.
- 표정: 키트 5종 + tongue(메롱), calc(확률 계산 중), shock(뭐, 뭐라고?!), smirk(한쪽 입꼬리) + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/mute.py
npm run shot -- characters/mute.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("mute", height=1.22, head=0.45, leg=1.03, chest=0.40, bust=0.65, segs=0.78, hand_q=0.6, cheek=0.09)
k = e.k

# ---- 팔레트 (원작 실측: 머리 #25232a, 청록 #3fcfc0, 셔츠 #2b2a31, 바지 #3b405a, 코트 #26242b)
shirt = M_("mu_shirt", "#3a3842")
shirt_d = M_("mu_shirt_d", "#1f1d24")
tie_m = M_("mu_tie", "#18171c")
pants = M_("mu_pants", "#3d425c")
pants_d = M_("mu_pants_d", "#2c3046")
coat = M_("mu_coat", "#28262d")
coat_in = M_("mu_coat_in", "#3a3741")
belt = M_("mu_belt", "#1c1b20")
silver = M_("mu_silver", "#c9ccd6")
boot = M_("mu_boot", "#1f1e24")
sole = M_("mu_sole", "#121116")
glove = M_("mu_glove", "#1e1d22")
teal = M_("mu_teal", "#3fcfc0")
teal_d = M_("mu_teal_d", "#279c94")
red = M_("mu_red", "#d23a4a")
glow = M_("mu_glow", "#ffffff", emission="#5ff5e4", unlit=True)

# ---- 얼굴: 청록 눈, 눈꼬리가 올라간 능글맞은 반쯤 감은 눈, 기본 입은 살짝 올라감
e.face(eye_color="#3fd2c6", iris_dark="#0d6a70", iris_light="#c2fff5", pupil="#0a2e33",
       lash="#1e1a22", brow="#2c2832", brow_th=1.1, blush="#f6a3a8", blush_size=1.05,
       base={"eye": {"top": 0.020, "ktop": 3.8, "tilt_out": 0.004, "tilt_in": -0.003, "cout": 0.018},
             "brow": {"dz": 0.064, "ang": -4.0, "arch": 0.003},
             "mouth": {"w": 0.022, "curve": 0.0040}},
       expr={
           # 메롱: 원작 대표 표정 (한쪽으로 내민 혀)
           "tongue": {"eye": {"top": 0.016, "lift": 0.010},
                      "brow": {"dz": 0.066, "ang": -2.0},
                      "mouth": {"w": 0.030, "curve": 0.0060, "open": 0.0175, "top_arch": 0.0012}},
           # 확률 계산 중: 가늘게 뜬 눈, 무표정한 입
           "calc": {"eye": {"top": 0.012, "ktop": 4.6, "tilt_in": -0.004},
                    "iris": {"pupil": 0.80},
                    "brow": {"ang": -10.0, "dz": 0.058},
                    "mouth": {"w": 0.016, "curve": -0.0004}},
           # 뭐, 뭐라고?!: 동그란 눈, 작은 동공, 올라간 눈썹, 이를 악문 물결 입
           "shock": {"eye": {"top": 0.036, "ktop": 2.2, "bot": 0.058, "tilt_out": 0.0},
                     "iris": {"pupil": 0.50, "rx": 0.025, "ry": 0.033},
                     "brow": {"ang": 16.0, "dz": 0.076, "arch": 0.004},
                     "mouth": {"w": 0.026, "curve": -0.0030, "open": 0.0070, "wave": 0.0020}},
       })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.015, "lift": 0.010}, "mouth": {"w": 0.028, "curve": 0.0035}},
             L={"brow": {"dz": 0.068, "ang": 2.0, "arch": 0.004}}, R={"brow": {"dz": 0.060, "ang": -12.0}},
             corner=(0.0090, -0.0012), mouth_dx=0.0025 * k)

# ---- 머리: 검은 단발 (끝이 바깥으로 뻗침), 일자 앞머리, 청록 띠, 바보털
HAIR = "#28252d"


def mute_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.8            # 뭉툭한 일자 앞머리
        lk["free"] *= 0.5
    elif lk["region"] in ("side", "back"):
        lk["curl"] = 0.016 * k   # 끝이 바깥으로 뻗친다
        lk["p"] = 1.5


h = c2.hair(e, HAIR, dark="#16141a", light="#5a5566", lock_fn=c2.lock_edit(mute_locks), volume=1.22)
h.cap(front=30, side=-8, back=-50, part=0)
bang_m = M_("mu_bangs", HAIR)     # 앞머리 영역 표시용 (색은 머리와 같다)
h.bangs(n=8, spread=58, tip_el=1, jag=0.12, sweep=0, curl=0.6, seed=5.0, mat=bang_m)
h.sides(length=0.07, width=0.090, n=2, puff=1.6)
h.back(length=0.06, n=9, spread=96)
h.ahoge(az=6, height=0.075, curl=1.3, width=0.018)
h.shine(el=54, spread=72, size=1.0)
hc = e.head_c
# 앞머리 윗부분의 청록 브릿지: 정면 ±75°만 (원작은 앞머리 다발 위쪽이 청록으로 물듦)
c2.stripe(h, teal, hc.z + 0.046 * k, hc.z + 0.084 * k, tilt=(0.0, 0.0), only=bang_m)

# 귀걸이 (왼쪽 귀, 청록 둥근 알)
eb, et = e._ear_axis("L")
e.part("earring", "head", lambda buf: c2.ellipsoid(buf, eb.lerp(et, 0.40) + V((0, -0.004 * k, -0.012 * k)),
                                                   V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.0065 * k, 0.0065 * k,
                                                   0.0065 * k, segs=8, rings=5, mat=teal, w={"head": 1.0}))

# ---- 셔츠 + 넥타이 + 초커 + 가슴 멜빵
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(shirt, hem=hz - 0.010 * k, collar=None, flare=0.010, placket=shirt_d, buttons=silver)
e.sleeves(shirt, length=0.86, off=0.010, flare=0.010, cuff=(shirt_d, 0.018, 0.004))


def collar_tie(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.010 * k), (0, 0, 1), (1, 0, 0), 0.055 * k, 0.051 * k, 0.022 * k,
         0.005 * k, segs=16, mat=shirt, w=w, taper=-0.04)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.004 * k, sg * 24, 0.015 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 16), 4, "Y")
        c2.prism(buf, [(-sg * 0.020 * k, 0.010 * k), (sg * 0.014 * k, 0.012 * k), (sg * 0.004 * k, -0.026 * k)],
                 0.004 * k, M, mat=shirt, w=w)
    # 넥타이: 매듭 + 아래로 넓어지는 판
    p0, n0 = e.torso_point(e.torso_top - 0.010 * k, 0, 0.016 * k)
    rbox(buf, (0.018 * k, 0.010 * k, 0.016 * k), Matrix.Translation(p0) @ elf.frame(n0, (0, 0, 1)), mat=tie_m, w=w,
         r=0.35, segs=1)
    pts = []
    for i, z in enumerate((e.torso_top - 0.020 * k, cz + 0.020 * k, cz - 0.030 * k, wz + 0.010 * k)):
        p, n = e.torso_point(z, 0, 0.017 * k + 0.002 * k * i)
        pts.append((p, n, 0.008 + 0.006 * i / 3))
    st = [{"c": p, "rx": wd * k, "ry": 0.0022 * k, "w": e._torso_wfn(p, 0), "ref": (1, 0, 0)} for p, n, wd in pts]
    loft(buf, st, segs=6, cap0="flat", cap1="flat", mat=tie_m)
    tip = pts[-1][0] - V((0, 0, 0.014 * k))
    c2.prism(buf, [(-0.014 * k, 0.0), (0.014 * k, 0.0), (0.0, -0.014 * k)], 0.004 * k,
             Matrix.Translation(pts[-1][0] + pts[-1][1] * 0.002 * k) @ elf.frame(pts[-1][1], (0, 0, 1)), mat=tie_m,
             w=e._torso_wfn(tip, 0))


e.part("collar_tie", "body", collar_tie)
e.part("choker", "head", lambda buf: (band(buf, (0, 0.004 * k, e.torso_top + 0.026 * k), (0, 0, 1), (1, 0, 0),
                                           0.050 * k, 0.046 * k, 0.012 * k, 0.004 * k, segs=16, mat=belt,
                                           w={"neck": 1.0}),
                                      c2.ellipsoid(buf, V((0, -0.050 * k, e.torso_top + 0.026 * k)), V((0, 0, 1)),
                                                   V((1, 0, 0)), V((0, -1, 0)), 0.0055 * k, 0.0055 * k, 0.004 * k,
                                                   segs=8, rings=4, mat=red, w={"neck": 1.0})))
sz = e.shoulder_z
for s in (1, -1):   # 가슴 멜빵 (어깨 → 가슴 아래 → 등)
    e.strap(belt, [("torso", cz + 0.050 * k, s * 40, 0.014 * k), ("torso", sz + 0.010 * k, s * 56, 0.014 * k),
                   ("torso", sz - 0.010 * k, s * 120, 0.014 * k), ("torso", cz - 0.010 * k, s * 156, 0.016 * k)],
            width=0.016, th=0.004, name=f"harness_{'L' if s > 0 else 'R'}")
e.ring(belt, "torso", cz - 0.030 * k, h=0.016, th=0.004, off=0.014, name="harness_band")
for s in (1, -1):
    a = e.anchor(("torso", cz - 0.030 * k, s * 40, 0.019 * k))
    e.part(f"harness_ring_{s}", "body", lambda buf, a=a: band(buf, a.pos, a.n, (0, 0, 1), 0.007 * k, 0.007 * k,
                                                               0.003 * k, 0.0025 * k, segs=10, mat=silver, w=a.w))

# ---- 하의: 남회색 바지, 벨트 + 은색 버클, 청록 마름모 주머니, X 버클 부츠
e.pants(pants, length=0.86, bag=0.012, blouse=0.010, off=0.010)
e.strap(pants_d, [("leg_L", 0.05, 0, 0.012 * k), ("leg_L", 0.80, 0, 0.012 * k)], width=0.004, th=0.0015,
        name="seam_L")
e.strap(pants_d, [("leg_R", 0.05, 0, 0.012 * k), ("leg_R", 0.80, 0, 0.012 * k)], width=0.004, th=0.0015,
        name="seam_R")
e.belt(belt, z=hz + 0.020 * k, h=0.024, buckle=silver, buckle_size=(0.032, 0.026), loops=belt)


def data_pouch(buf, Mx, w):
    elf.pouch_geo(buf, Mx, (0.044 * k, 0.020 * k, 0.050 * k), belt, flap=belt, w=w)
    c2.prism(buf, c2.diamond_poly(0.022 * k, 0.026 * k), 0.003 * k,
             Mx @ Matrix.Translation((0, -0.026 * k, -0.006 * k)), mat=teal, w=w)


e.gear("data_pouch", ("leg_R", 0.06, -10, 0.020 * k), data_pouch)
e.boots(boot, top=0.66, sole=(sole, 0.016), toe=0.004, off=0.012)
for sd in ("L", "R"):
    for t in (0.74, 0.86):     # X 버클 띠
        e.ring(belt, f"leg_{sd}", t, h=0.010, th=0.004, off=0.024, name=f"boot_strap_{sd}{t}")
        a = e.anchor((f"leg_{sd}", t, 0 if sd == "L" else 0, 0.030 * k))
        e.part(f"boot_x_{sd}{t}", "body",
               lambda buf, a=a: c2.prism(buf, c2.star_poly(0.011 * k, 0.003 * k, n=4, rot=45), 0.003 * k,
                                         a.matrix(), mat=silver, w=a.w))

# ---- 손가락 없는 장갑 + 손목 은색 징
e.gloves(glove, cuff=belt, inflate=0.0026)


def stud(buf, Mx, w):
    R = Mx.to_3x3()
    c2.ellipsoid(buf, Mx.to_translation(), (R @ V((0, -1, 0))).normalized(), (R @ V((1, 0, 0))).normalized(),
                 (R @ V((0, 0, 1))).normalized(), 0.0045 * k, 0.0038 * k, 0.0038 * k, segs=6, rings=4, mat=silver,
                 w=w)


for sd in ("L", "R"):
    for a_ in (0, 120, 240):
        e.gear(f"stud_{sd}{a_}", (f"arm_{sd}", 0.93, a_, 0.020 * k), stud)

# ---- 어깨에 걸친 긴 검은 코트 (소매 없이 망토처럼), 세운 깃, 은색 단추
cape = c2.Shell(e, coat, e.torso_top - 0.002 * k, 0.140 * k, gap=[(0.0, 50.0), (0.25, 58.0), (1.0, 70.0)], off=0.030,
                th=0.006, rows=14, cols=20, flare=[(0.0, 0.012), (0.25, 0.030), (1.0, 0.078)], shoulder=1.10)
cape.edge_trim(coat_in, width=0.012, th=0.002, i0=2)
cape.hem_trim(coat_in, width=0.010, th=0.002)
cape.done("coat")
e.part("coat_collar", "body", lambda buf: band(buf, (0, 0.020 * k, e.torso_top + 0.006 * k), (0, -0.30, 1), (1, 0, 0),
                                               0.088 * k, 0.082 * k, 0.040 * k, 0.006 * k, segs=16, mat=coat,
                                               w={"neck": 0.3, "chest": 0.7}, taper=0.16))
for s in (1, -1):
    for z in (cz + 0.010 * k, wz):
        p, n = cape.surface((e.torso_top - z) / (e.torso_top - 0.140 * k), s * 54, 0.002 * k)
        e.part(f"coat_btn_{s}{z:.2f}", "body",
               lambda buf, p=p, n=n: disc(buf, p, n, (0, 0, 1), 0.0060 * k, 0.0060 * k, 0.0025 * k, segs=8,
                                          mat=silver, w=e._torso_wfn(p, 0)))

# ---- 데이터 실 (UNLIT 청록, 별도 노드): 손가락 끝에서 늘어져 끝에 은색 가시 추
th_buf = Buf()
spk = Buf()
for sd in ("L", "R"):
    W, d, pn = e.W[sd], e.adir[sd], e.palm_n[sd]
    s = 1 if sd == "L" else -1
    for i, (fx, ln) in enumerate(((-0.010, 0.13), (0.004, 0.17), (0.016, 0.11))):
        tip = W + d * (e.hand_len + e.finger_len * 0.9) + V((0, fx * k, 0)) + pn * 0.006 * k
        end = tip + V((s * 0.010 * k * (i - 1), -0.010 * k * (i - 1), -ln * k))
        w = {f"hand_{sd}": 1.0}
        mid = tip.lerp(end, 0.5) + V((s * 0.006 * k, 0, 0))
        st = [{"c": q, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w} for q in elf.catmull([tip, mid, end], 6)]
        loft(th_buf, st, segs=4, cap0="flat", cap1="flat", mat=glow)
        # 가시 추 (위가 넓은 사각뿔 두 개를 맞댄 쐐기)
        st2 = [{"c": end + V((0, 0, 0.002 * k)), "rx": 0.0006 * k, "ry": 0.0006 * k, "w": w},
               {"c": end - V((0, 0, 0.006 * k)), "rx": 0.0050 * k, "ry": 0.0050 * k, "w": w},
               {"c": end - V((0, 0, 0.022 * k)), "rx": 0.0004 * k, "ry": 0.0004 * k, "w": w}]
        loft(spk, st2, segs=4, cap0="flat", cap1="flat", mat=silver, p=1.0)
e.add(th_buf.obj("mute_threads_geo", smooth=False), group="arms", tag="threads", node="threads",
      props={"noOutline": 1})
e.add(spk.obj("mute_spikes", smooth=False, angle=30.0), group="arms", tag="spikes")

e.finalize()
e.export("characters/mute.glb")
