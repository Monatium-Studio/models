"""아멜리아 (교주 차원): 모나티엄 시장 비서. 2막 외래종 수용소(엘레나·로네와 함께 갇힘), 에필로그 대관식(엘레나와
비서로 참석)에 나온다.

원작 아멜리아(트릭컬 리바이브, '자타공인 최고 비서')의 복장을 바탕으로 한 카메오 모델.
- 유지한 식별 요소: 옅은 분홍빛 베이지 머리와 끝이 분홍빛 갈색으로 물드는 가슴까지 오는 옆머리, 머리를 두르는
  땋은 머리와 뒤통수 경단(크라운 브레이드), 가운데 가르마의 커튼 앞머리, 왼쪽 위 하늘색 초승달 머리핀,
  연두빛 초록 눈과 반쯤 감은 무표정, 검은 정장 재킷(걸쳐 입음)과 흰 셔츠 깃, 검은 상의, 짙은 갈색 통바지와 신,
  초승달 로고 태블릿.
- 재해석: 재킷 왼쪽 깃에 시장 비서 신분증(클립), 귀에 통신 이어피스를 더했다. 태블릿은 왼손에 든 별도 노드다.
- 아멜리아(R41)와의 구분: 단정한 크라운 브레이드, 하늘색 초승달 핀, 검은 정장. (R41은 헝클어진 앞머리·바보털,
  금색 별+초승달 핀, 흰 더블 연구 코트)
- 표정: 키트 5종 + annoyed(짜증), tired(지친 눈, 수용소), glare(째려봄), smug(한쪽 입꼬리) + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/amelia.py
npm run shot -- characters/amelia.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import amelia_common as am  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = am.body("amelia")
k = e.k

# ---- 팔레트 (원작 실측: 재킷 #3a3438, 바지 #5e4440, 신 #4a3330)
jacket = M_("am_jacket", "#3b363c")
jacket_d = M_("am_jacket_d", "#2b272d")
top = M_("am_top", "#2f2b31")
shirt = M_("am_shirt", "#f7f3f2")
pants = M_("am_pants", "#614643")
pants_d = M_("am_pants_d", "#4e3735")
shoe = M_("am_shoe", "#4a3330")
sole = M_("am_sole", "#2e2224")
card = M_("am_card", "#ffffff")
blue = M_("am_blue", "#5b8fd0")
metal = M_("am_metal", "#c9c6cc")
ear_m = M_("am_earpiece", "#2a2730")

# ---- 얼굴
am.face(e, expr={
    # 짜증: 눈을 더 가늘게, 눈썹 안쪽 내림, 입은 ∩
    "annoyed": {"eye": {"top": 0.013, "ktop": 4.6, "tilt_in": -0.006},
                "brow": {"ang": -14.0, "dz": 0.054, "th": 0.0062},
                "mouth": {"w": 0.019, "curve": -0.0032}},
    # 지친 눈 (수용소): 처진 눈꼬리와 눈썹, 시무룩한 입
    "tired": {"eye": {"top": 0.011, "tilt_out": -0.007, "ktop": 3.4, "lift": 0.004},
              "brow": {"ang": 14.0, "dz": 0.058},
              "mouth": {"w": 0.016, "curve": -0.0016, "open": 0.0015}},
    # 째려봄: 눈을 조금 뜨고 동공이 작아진다, 입은 꾹
    "glare": {"eye": {"top": 0.021, "ktop": 3.8, "tilt_in": -0.010, "bot": 0.050},
              "iris": {"pupil": 0.70},
              "brow": {"ang": -20.0, "dz": 0.052, "th": 0.0066},
              "mouth": {"w": 0.014, "curve": -0.0010}},
})
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.015, "lift": 0.010}, "mouth": {"w": 0.024, "curve": 0.0030}},
             L={"brow": {"dz": 0.064, "ang": 4.0}}, R={"brow": {"dz": 0.058, "ang": -4.0}},
             corner=(0.0075, -0.0005), mouth_dx=0.0020 * k)


# ---- 머리 (amelia_common.secretary_hair: amelia.py, amelia_prisoner.py 공용): 가운데 가르마 커튼 앞머리 + 가슴까지
# 오는 넓은 옆머리 + 크라운 브레이드 + 경단(뒷머리는 올림) + 하늘색 초승달 핀
h = am.secretary_hair(e, "am_braid")

# ---- 옷: 검은 상의 + 흰 셔츠 깃, 짙은 갈색 통바지, 짙은 갈색 신
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(top, hem=hz - 0.004 * k, collar=None, flare=0.010)
e.pants(pants, length=0.97, bag=0.016, blouse=0.0, off=0.010, cuff=(pants_d, 0.010, 0.003))
e.boots(shoe, top=0.95, sole=(sole, 0.012), toe=0.003, off=0.010)


def shirt_collar(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.012 * k), (0, 0, 1), (1, 0, 0), 0.054 * k, 0.050 * k, 0.026 * k,
         0.005 * k, segs=16, mat=shirt, w=w, taper=-0.03)
    for sg in (1, -1):
        # 깃 끝 (아래로 뾰족한 삼각 판)
        p, n = e.torso_point(e.torso_top - 0.004 * k, sg * 22, 0.014 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 12), 4, "Y")
        c2.prism(buf, [(-sg * 0.020 * k, 0.010 * k), (sg * 0.014 * k, 0.012 * k), (sg * 0.004 * k, -0.026 * k)],
                 0.004 * k, M, mat=shirt, w=w, chamfer=0.0)


e.part("shirt_collar", "body", shirt_collar)

# ---- 검은 정장 재킷: 앞이 열리고 허벅지 위까지, 접힌 깃, 허리 주머니 덮개
jk = c2.Shell(e, jacket, e.torso_top - 0.004 * k, hz - 0.070 * k,
              gap=[(0.0, 30.0), (0.22, 19.0), (0.55, 17.0), (1.0, 23.0)], off=0.024, th=0.005, skirt=True,
              rows=15, cols=22, flare=[(0.0, 0.0), (0.45, 0.010), (1.0, 0.030)], shoulder=0.85)
jk.edge_trim(jacket, width=0.022, th=0.004, i1=6)                  # 접힌 깃 (라펠): 고른 폭 (계단 없음)
jk.edge_trim(jacket_d, width=0.006, th=0.002, i0=6)
jk.hem_trim(jacket_d, width=0.008, th=0.002)
jk.done("jacket")
# 뒷깃: 목 뒤와 옆을 두르고 앞은 열린 세운 깃 (닫힌 고리는 목을 감싼 띠처럼 보였다)
jc = c2.Shell(e, jacket, e.torso_top + 0.028 * k, e.torso_top - 0.006 * k, gap=44.0, off=0.026, th=0.005, rows=3,
              cols=18, flare=[(0.0, 0.008), (1.0, 0.0)])
jc.done("jacket_collar")
e.sleeves(jacket, length=0.97, off=0.016, flare=0.018, puff=0.004, cuff=(jacket_d, 0.020, 0.0045))
uW = (e.torso_top - (wz - 0.070 * k)) / (e.torso_top - (hz - 0.070 * k))
uC = (e.torso_top - (cz + 0.030 * k)) / (e.torso_top - (hz - 0.070 * k))


def pockets(buf):
    for sg in (1, -1):
        Mx = jk.frame_at(uW, sg * 50, 0.001 * k)
        w = c2.skirt_w(e, Mx.to_translation())
        rbox(buf, (0.058 * k, 0.005 * k, 0.016 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0)), mat=jacket_d, w=w,
             r=0.2, segs=1)
    # 시장 비서 신분증 (왼쪽 깃 아래, 클립)
    Mi = jk.frame_at(uC, 34, 0.003 * k) @ Matrix.Rotation(math.radians(-5), 4, "Y")
    w = e._torso_wfn(Mi.to_translation(), 0)
    rbox(buf, (0.030 * k, 0.004 * k, 0.040 * k), Mi @ Matrix.Translation((0, -0.002 * k, -0.022 * k)), mat=card, w=w,
         r=0.15, segs=1)
    rbox(buf, (0.030 * k, 0.005 * k, 0.010 * k), Mi @ Matrix.Translation((0, -0.003 * k, -0.008 * k)), mat=blue, w=w,
         r=0.15, segs=1)
    rbox(buf, (0.010 * k, 0.006 * k, 0.012 * k), Mi @ Matrix.Translation((0, -0.004 * k, 0.002 * k)), mat=metal, w=w,
         r=0.25, segs=1)


e.part("pockets", "body", pockets)

# ---- 통신 이어피스 (오른쪽 귀 뿌리)
eb, et = e._ear_axis("R")


def earpiece(buf):
    w = {"head": 1.0}
    c = eb.lerp(et, 0.10) + V((0, -0.012 * k, -0.010 * k))
    rbox(buf, (0.016 * k, 0.014 * k, 0.020 * k), Matrix.Translation(c), mat=ear_m, w=w, r=0.45, segs=1)
    loft(buf, [{"c": c + V((0, -0.006 * k, -0.006 * k)), "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w},
               {"c": c + V((0.012 * k, -0.026 * k, -0.026 * k)), "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w}],
         segs=6, cap0="round", cap1="round", mat=ear_m)


e.part("earpiece", "head", earpiece)

am.done_hair(e)
e.finalize()
am.tip_gradient(e, 0.21)
am.tablet(e, "L")
e.export("characters/amelia.glb")
