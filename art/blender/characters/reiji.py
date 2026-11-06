"""레이지: 교주 차원 모나티엄 IT관리반의 잡일 담당(만능 말단). 1막 M2 시청 방어선에 투입된다(사용자 결정,
원작 침공전 모나티엄 배치).

원작 레이지(트릭컬 리바이브)의 로비 스탠딩·카드 차림을 따른다. 전투복 언어는 엘피니아 군 전투복 계열이다
(reference-notes 5장, 프롤로그 캐시의 전투복 기준). 근거: docs/art/characters-cameo3.md.
- 식별 요소: 붉은 갈색 어깨 길이 머리와 이마의 민트색 머리핀, 갈색 눈과 이를 드러낸 능글맞은 웃음·윙크,
  적갈색 철모(M1식 둥근 돔, 테두리), 회녹색 전투복 상의(덮개 있는 가슴 주머니 2), 검은 벨트 + 사각 버클,
  회녹색 카고 바지(허벅지 옆 큰 주머니, 덮개 + 단추)와 블라우징, 청회색 군화와 끈, 큰 불펍 소총.
- 재해석: 원작 상의의 디지털 위장 무늬는 옮기지 않았다(reference-notes 5.5: 한국군 디지털 위장 무늬를 닮아 복붙처럼
  보이고 텍스처가 필요하다). 대신 회녹 바탕에 큰 색 블록 몇 개를 얹어 위장복임만 읽히게 했다. 소총은 원작 'XG-레이저'의
  형태 언어(불펍, 긴 총열, 옆 긴 창, 개머리 옆 둥근 구멍 줄, 표시창)만 가져와 새로 그렸다(별도 노드 reiji_rifle,
  socket_hand_R, 무기 규약).
- 표정: 키트 5종 + grin(이를 드러낸 웃음) + wink(왼눈 윙크, 교정 키 없음) + smug(능글맞은 반쯤 감은 눈) + blink 교정 키.

npm run model -- art/blender/characters/reiji.py
npm run shot -- characters/reiji.glb
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
import elf_trio_common as tc  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp  # noqa: E402

cb.reset()
e = elf.Elf("reiji", height=1.20, segs=0.66, hand_q=0.45, cheek=0.12)
k = e.k
M_ = elf.mat
camo = M_("re_camo", "#a0aba2")          # 회녹 상의 (원작 위장 바탕 #a0aba2)
camo_l = M_("re_camo_l", "#bcc6b7")
camo_d = M_("re_camo_d", "#7e7c89")
camo_f = M_("re_camo_f", "#848f86")       # 덮개·소맷단
pants = M_("re_pants", "#9daba4")         # 회녹 카고 바지 (원작 #9daba4)
pants_d = M_("re_pants_d", "#7e8b85")
helm = M_("re_helmet", "#b36262")         # 적갈 철모 (원작 #b66464)
helm_d = M_("re_helmet_d", "#8a4747")
boot = M_("re_boot", "#5b6168")
boot_d = M_("re_boot_d", "#464b52")
mint = M_("re_mint", "#9ed8c4")

# ---- 얼굴: 갈색 눈, 능글맞은 반쯤 감은 눈, 이를 드러낸 웃음이 기본에 가깝다
e.face(eye_color="#8c5e3e", iris_dark="#4e3020", iris_light="#d8a77c", pupil="#33200f",
       lash="#3e2826", brow="#5a3330", brow_th=1.2, blush="#f6a0a4", blush_size=1.15,
       base={"eye": {"top": 0.024, "ktop": 3.8, "tilt_in": -0.004},
             "brow": {"ang": -8.0, "dz": 0.064, "arch": 0.002},
             "mouth": {"w": 0.024, "curve": 0.0060, "open": 0.0040}},
       expr={
           # 이를 드러낸 웃음: 넓고 납작하게 벌린 입 (원작 카드)
           "grin": {"eye": {"top": 0.020, "lift": 0.010},
                    "brow": {"ang": -10.0, "dz": 0.062},
                    "mouth": {"w": 0.040, "curve": 0.0080, "open": 0.0100, "top_arch": -0.0030}},
           # 능글맞음: 더 내린 눈꺼풀
           "smug": {"eye": {"top": 0.015, "ktop": 4.8, "lift": 0.006},
                    "brow": {"ang": -4.0, "dz": 0.066},
                    "mouth": {"w": 0.028, "curve": 0.0070}},
       })
c2.face_expr(e, "wink",
             both={"mouth": {"w": 0.036, "curve": 0.0080, "open": 0.0080, "top_arch": -0.0025}},
             L={"eye": {"close": 1.0}, "brow": {"dz": 0.060, "ang": -6.0}},
             R={"eye": {"top": 0.024, "lift": 0.006}, "brow": {"dz": 0.066, "ang": -12.0}},
             corner=(0.0050, 0.0020), blink_fix=False)

# ---- 머리: 붉은 갈색, 어깨까지 오는 옆·뒷머리 (헬멧 아래) + 이마의 민트 머리핀
h = e.hair("#94574c", dark="#6a3a34", light="#bd8070")
h.cap(front=28, side=-10, back=-50, segs=16, rows=4)
h.bangs(n=6, spread=54, tip_el=-1, sweep=8, seed=12.0)
h.sides(length=0.16, width=0.078, curl=0.4)
h.back(length=0.14, n=7)

# ---- 적갈 철모 (M1식: 둥근 돔 + 테두리) + 앞 세로 이음 두 줄 + 민트 핀
e.helmet(helm, off=0.040, front=12.0, side=-2.0, back=-28.0, rim=helm_d, strap=M_("re_strap", "#6a5a52"))


def helmet_bits(buf):
    w = {"head": 1.0}
    for az in (-30.0, -20.0):
        pts, nrm, ups = [], [], []
        for el in (24.0, 44.0, 62.0, 76.0):
            p, n = e.head_point(az, el, 0.0425 * k)
            pts.append(p)
            nrm.append(n)
            ups.append(V((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0)))
        elf._loop(buf, pts, nrm, ups, 0.004 * k, 0.002 * k, mat=helm_d, w=w, closed=False)
    # 이마의 민트색 머리핀 (헬멧 테두리 바로 아래, 캐릭터 오른쪽)
    p, n = e.head_point(-30.0, 6.0, 0.034 * k)
    rbox(buf, (0.040 * k, 0.012 * k, 0.014 * k), Matrix.Translation(p) @ elf.frame(n, (0.35, 0, 1)), mat=mint, w=w,
         r=0.45, segs=1)


e.part("helmet_bits", "head", helmet_bits)

# ---- 상의: 회녹 전투복 + 덮개 있는 가슴 주머니 2 + 큰 색 블록(단순화한 위장)
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(camo, collar="stand", collar_mat=camo_f, placket=camo_f, flare=0.014)
e.sleeves(camo, length=0.94, off=0.012, flare=0.008, cuff=(camo_f, 0.020, 0.004))
for i, a in enumerate((-30, 30)):
    e.pouch(camo, ("torso", cz + 0.010 * k, a, 0.012 * k), size=(0.040, 0.008, 0.044), flap=camo_f,
            button=M_("re_btn", "#5a5660"), name=f"chest_pocket_{i}")
# [오리지널] 단순화한 위장: 큰 색 블록 (원작 디지털 무늬는 옮기지 않음)
blocks = [("torso", wz + 0.030 * k, -58, camo_d, (0.052, 0.034)), ("torso", cz - 0.034 * k, 66, camo_l, (0.056, 0.040)),
          ("torso", cz + 0.036 * k, 150, camo_d, (0.060, 0.040)), ("torso", wz + 0.004 * k, -150, camo_l, (0.058, 0.036)),
          ("torso", cz + 0.046 * k, -64, camo_l, (0.044, 0.032)), ("torso", wz - 0.010 * k, 100, camo_d, (0.050, 0.034)),
          ("torso", cz - 0.010 * k, -120, camo_d, (0.048, 0.036)), ("torso", e.torso_top - 0.030 * k, 180, camo_l, (0.050, 0.030)),
          ("arm_L", 0.30, 90, camo_d, (0.040, 0.030)), ("arm_R", 0.52, -90, camo_l, (0.040, 0.028)),
          ("arm_R", 0.20, 20, camo_d, (0.036, 0.028)), ("arm_L", 0.62, 10, camo_l, (0.036, 0.026)),
          ("arm_L", 0.15, 180, camo_l, (0.036, 0.026)), ("arm_R", 0.70, 180, camo_d, (0.034, 0.026))]
for i, (where, pos_, ang, mt, sz_) in enumerate(blocks):
    off = 0.011 * k if where == "torso" else 0.012 * k
    e.patch(mt, (where, pos_, ang, off), size=sz_, shape="rect", th=0.0012, name=f"camo_{i}")

# ---- 하의: 회녹 카고 바지 + 허벅지 옆 큰 주머니 + 블라우징, 청회색 군화
m = tc.base_gear(e, "re", pants=pants, pants_d=pants_d, boots=boot, boots_d=boot_d, bag=0.018, blouse=0.024,
                 boots_top=0.70)
for sd, s in (("L", 1), ("R", -1)):
    e.pouch(pants, (f"leg_{sd}", 0.36, s * 85, 0.022 * k), size=(0.056, 0.014, 0.064), flap=pants_d,
            button=pants_d, name=f"cargo_{sd}")

e.finalize()

# ---- 불펍 소총 (별도 노드 rifle): 오른손에 쥐고 총구를 위로 세워 든다 (원작 카드처럼 세운 자세)
rf = tc.xg_rifle(e)
sock = bpy.data.objects["socket_hand_R"]
pos = sock.matrix_world.translation.copy()
Mw = tc.frame_world(V((0.0, 0.0, 1.0)), V((-1.0, 0.0, 0.0)))
Mw.translation = pos
tc.attach(e, rf, "socket_hand_R", Mw, "rifle", props={"muzzle": "0,%.3f,%.3f" % (0.54 * k, 0.062 * k)})

e.export("characters/reiji.glb")
