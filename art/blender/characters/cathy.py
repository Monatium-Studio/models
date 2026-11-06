"""캐시 (1막 이후): 모나티엄 진압반 정찰병. 원작 복장 기반의 카메오 모델.

원작 캐시(트릭컬 리바이브)의 '유령 위장' 복장을 전시 정찰병 차림으로 다시 짰다.
- 유지한 식별 요소: 회흑색 머리 + 은회색 브릿지, 바보털 두 가닥, 양 갈래 땋은 머리(끝이 밝은 회색, 검은 리본),
  주황빛 붉은 눈, 흰 해골 머리핀, 흰 프릴 원피스 + 검은 조끼 + 검은 리본, 등에 멘 큰 검은 자루 가방, 전기충격기,
  흰 헐렁한 양말과 회색 신발.
- 재해석: 원피스는 무릎 위 길이의 활동복으로 줄이고 속바지를 넣었다. 가방은 정찰 장비 자루(조임끈 + 리본)로,
  전기충격기는 오른쪽 허리 권총집에 넣었다. 왼팔에 진압반 완장(자줏빛 회색 띠 + 은색 마름모)을 둘러 소속을 밝힌다.
- 표정: 키트 5종 + freeze, smirk, tease (+ blink 교정 키). cathy_common.py 참고.
근거: docs/art/characters-cameo.md

npm run model -- art/blender/characters/cathy.py
npm run shot -- characters/cathy.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "characters"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo  # noqa: E402
import cathy_common as cc  # noqa: E402
from elf import V, Matrix, Buf  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("cathy", segs=0.68, hand_q=0.6, cheek=0.11)
k = e.k

# ---- 팔레트 (원작 실측: 흰 원피스는 회색 그늘, 리본·조끼는 거의 검정)
white = M_("ca_white", "#f3eff0")
white_d = M_("ca_white_d", "#d6d0d4")     # 프릴 테두리, 속바지
black = M_("ca_black", "#2e2a31")         # 조끼, 리본, 가방
black_l = M_("ca_black_l", "#45404a")     # 가방 조임끈·끈
sock = M_("ca_sock", "#f6f3f3")
shoe = M_("ca_shoe", "#8c8790")
sole = M_("ca_sole", "#4a4550")
metal = M_("ca_metal", "#cfcac4")
riot = M_("ca_riot", "#655d64")           # 진압반 장비색 (reference-notes 6장)
led = M_("ca_led", "#ffffff", emission="#ff5a5a", unlit=True)

# ---- 얼굴, 머리
cc.face(e)
h = cc.hair(e, helmet=False)
bs = cc.braids(e, h, end_z=0.30)
cc.skull_pin(e, h, az=56, el=46, size=0.060)

# ---- 원피스: 몸판 + 검은 조끼 + 치마 자락(프릴)
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(white, hem=wz - 0.02 * k, collar="stand", collar_mat=white_d, flare=0.0)
e.pants(white_d, length=0.10, bag=0.004, blouse=0.0)          # 속바지
vest = cameo.Shell(e, black, cz + 0.035 * k, wz - 0.012 * k, off=0.019, th=0.004, cols=16)
vest.top_trim(black_l, width=0.007).hem_trim(black_l, width=0.007).done("vest")
skirt = cameo.Shell(e, white, wz + 0.004 * k, 0.255 * k, off=0.016, th=0.004, skirt=True, cols=18,
                    flare=[(0.0, 0.0), (0.35, 0.010), (1.0, 0.050)], ruffle=(0.0085, 9, 0.55))
skirt.hem_trim(white_d, width=0.014, th=0.003).done("skirt")
# 조끼 앞 단추 3개
for i in range(3):
    z = lerp_z = cz + 0.012 * k - i * 0.03 * k
    a = e.anchor(("torso", z, 0.0, 0.019 * k + 0.004 * k))
    e.part(f"vest_btn{i}", "body", lambda buf, a=a: elf.disc(buf, a.pos, a.n, (0, 0, 1), 0.0045 * k, 0.0045 * k,
                                                               0.0018 * k, segs=8, mat=white, w=a.w))
# 목 리본
e.gear("neck_bow", ("torso", e.torso_top - 0.012 * k, 0.0, 0.030 * k),
       lambda buf, Mx, w: cameo.bow(buf, Mx, 0.070 * k, black, w=w, tails=1.0, segs=6))

# ---- 소매 (살짝 부풀고 프릴 소맷단)
e.sleeves(white, length=0.96, puff=0.007, flare=0.010, cuff=(white_d, 0.020, 0.0055))
# 진압반 완장 (왼팔 위)
e.ring(riot, "arm_L", 0.30, h=0.026, th=0.004, off=0.013, name="riot_band")
e.patch(metal, ("arm_L", 0.30, 70, 0.018 * k), size=(0.016, 0.016), shape="diamond", name="riot_mark")

# ---- 헐렁한 흰 양말 + 회색 신발
for side in ("L", "R"):
    cameo.leg_tube(e, sock, side, 0.56, 0.93, off=0.012,
                   extra=lambda t: 0.0035 * math.sin((t - 0.56) * 60) ** 2 + 0.004 * elf.smoothstep(0.56, 0.62, t),
                   cap0=None, name=f"sock_{side}")
    e.ring(black, f"leg_{side}", 0.585, h=0.012, th=0.003, off=0.017, name=f"sock_band_{side}")
e.boots(shoe, top=0.88, sole=(sole, 0.013), cuff=shoe, toe=0.004)

# ---- 등에 멘 큰 검은 자루 가방 + 대각선 멜빵
def sack(buf, w):
    st = []
    base = V((0.015 * k, 0.0, 0.0))
    prof = [(0.36, 0.035, 0.030), (0.40, 0.085, 0.060), (0.47, 0.112, 0.082), (0.55, 0.112, 0.084),
            (0.61, 0.090, 0.070), (0.645, 0.050, 0.040), (0.665, 0.030, 0.026)]
    for z, rx, ry in prof:
        st.append({"c": V((base.x, 0.0, z * k)), "rx": rx * k, "ry": ry * k, "w": w})
    rows = elf.loft(buf, st, segs=12, cap0="round", cap1=None, mat=black, cap_len0=0.02 * k)
    # 조임끈 매듭 + 주둥이 주름
    elf.band(buf, V((base.x, 0.0, 0.640 * k)), (0, 0, 1), (1, 0, 0), 0.050 * k, 0.040 * k, 0.012 * k, 0.004 * k,
             segs=12, mat=black_l, w=w)
    top = [{"c": V((base.x, 0.0, 0.655 * k)), "rx": 0.034 * k, "ry": 0.028 * k, "w": w},
           {"c": V((base.x + 0.004 * k, 0.0, 0.690 * k)), "rx": 0.046 * k, "ry": 0.036 * k, "w": w},
           {"c": V((base.x + 0.010 * k, 0.0, 0.705 * k)), "rx": 0.036 * k, "ry": 0.028 * k, "w": w}]
    elf.loft(buf, top, segs=10, cap0=None, cap1="round", mat=black, cap_len1=0.008 * k)
    _ = rows


bk = V((0, e.torso_at(0.5 * k)[2] + e.torso_at(0.5 * k)[1] + 0.105 * k, 0))
sw = e._torso_wfn(V((0, 0, cz)), 0)
buf = Buf()
sack(buf, {"chest": 0.7, "spine": 0.3})
ob = buf.obj("cathy_sack", angle=60)
ob.location = bk
ob.rotation_euler = (math.radians(4), 0, math.radians(-8))
e.add(ob, group="body", tag="sack")
bb = Buf()
cameo.bow(bb, Matrix.Translation(bk + V((0.020 * k, 0.050 * k, 0.640 * k))) @ elf.frame((0.15, 1, 0)), 0.080 * k,
          riot, w={"chest": 1.0}, tails=0.9, segs=6)
e.add(bb.obj("cathy_sack_bow", angle=50), group="body", tag="sack_bow")
# 멜빵: 오른쪽 어깨 → 가슴 → 왼쪽 옆구리 → 가방
sz = e.shoulder_z
e.strap(black_l, [("torso", sz + 0.025 * k, -58, 0.020 * k), ("torso", sz - 0.02 * k, -30, 0.026 * k),
                  ("torso", cz, 10, 0.028 * k), ("torso", wz + 0.03 * k, 55, 0.024 * k),
                  ("torso", wz + 0.02 * k, 120, 0.030 * k), ("torso", wz + 0.06 * k, 160, 0.06 * k)],
        width=0.020, th=0.004, name="sack_strap")
e.strap(black_l, [("torso", sz + 0.025 * k, -58, 0.020 * k), ("torso", sz + 0.01 * k, -110, 0.024 * k),
                  ("torso", cz + 0.02 * k, -150, 0.05 * k), ("torso", cz, -168, 0.09 * k)],
        width=0.020, th=0.004, name="sack_strap_b")

# ---- 전기충격기 (오른쪽 허리 권총집)
def stun(buf, Mx, w):
    elf.rbox(buf, (0.040 * k, 0.020 * k, 0.060 * k), Mx @ Matrix.Translation((0, -0.010 * k, -0.004 * k)), mat=black,
             w=w, r=0.2, segs=1)
    cameo.rrbox(buf, (0.034 * k, 0.026 * k, 0.050 * k), Mx @ Matrix.Translation((0, -0.033 * k, 0.010 * k)),
                mat=black_l, w=w, r=0.3, segs=1)
    for sg in (1, -1):
        b0 = Mx @ V((sg * 0.009 * k, -0.033 * k, 0.034 * k))
        elf.loft(buf, [{"c": b0, "rx": 0.0028 * k, "ry": 0.0028 * k, "w": w},
                       {"c": b0 + Mx.to_3x3() @ V((0, 0, 0.016 * k)), "rx": 0.0022 * k, "ry": 0.0022 * k, "w": w}],
                 segs=6, cap0="flat", cap1="round", mat=metal)
    n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
    elf.disc(buf, Mx @ V((0, -0.047 * k, 0.012 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.005 * k, 0.005 * k,
             0.0015 * k, segs=8, mat=led, w=w)


e.gear("stun_gun", ("torso", wz - 0.035 * k, -100, 0.036 * k), stun)

e.finalize()
print("[cathy] braid vcol corners:", cc.shade(e, bs))
e.export("characters/cathy.glb")
