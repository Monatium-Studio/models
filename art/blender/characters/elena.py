"""엘레나: 모나티엄 시장. 둠스데이 프로토콜(1막 끝), 외래종 수용소(2막), 대관식(에필로그)에 나온다.

원작 엘레나(트릭컬 리바이브, '엘프의 참리더')의 복장을 바탕으로 한 카메오 모델. 체격·얼굴·머리는 elena_common.py.
- 유지한 식별 요소: 바깥으로 넓게 퍼지는 장밋빛 분홍 긴 생머리(A라인)와 뭉툭한 일자 앞머리, 정수리 크림색 광택 둘,
  위는 하늘색·아래는 크림 노랑인 반쯤 감은 눈과 메롱 표정, 흰 연구 가운(앞이 열리고 단추 없음, 크고 헐렁한 소매),
  그 안에 원피스처럼 입은 연보랏빛 하늘색 박스티(허리선 없음), 맨다리와 짙은 갈색 신. 다른 인물보다 키가 큰 성인 체형
  (원작 실측 3.25등신, 가슴 볼륨 bust 0.60).
- 재해석: 가운에 시장 신분증과 펜 꽂은 가슴 주머니, 허리 주머니의 태블릿(둠스데이 프로토콜 단말)을 더했다.
  긴 머리는 등 뒤 가운 위로 흐르게 하고 가슴 본에 붙은 본 사슬로 흔든다.
- 표정: 키트 5종 + tongue(메롱), tired(지친 눈, 수용소), wink(윙크 메롱) + blink 교정 키.
근거: docs/art/characters-cameo.md

npm run model -- art/blender/characters/elena.py
npm run shot -- characters/elena.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cameo  # noqa: E402
import elena_common as ec  # noqa: E402
from elf import V, Matrix, Buf  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("elena", **ec.BODY, **ec.TRI)
k = e.k

# ---- 팔레트 (원작 실측: 머리 #d7928a, 박스티 #aebde3 근처(연보랏빛 하늘색), 가운 #f7edf3, 신 #592a2b)
coat = M_("el_coat", "#f6f2f4")
coat_d = M_("el_coat_d", "#d9d3da")
dress = M_("el_dress", "#aabbe4")
dress_d = M_("el_dress_d", "#8b9fd0")
shoe = M_("el_shoe", "#5a2c2c")
sole = M_("el_sole", "#3a2224")
card = M_("el_card", "#ffffff")
blue = M_("el_blue", "#4a78c2")
pen_r = M_("el_pen_r", "#d8494f")
pen_b = M_("el_pen_b", "#3d5ea8")
dark = M_("el_dark", "#3a3946")
screen = M_("el_screen", "#ffffff", emission="#8fe8ff", unlit=True)

# ---- 얼굴·머리 (elena_common: elena_prisoner와 같다)
ec.face(e)
h = ec.hair(e)

# ---- 연보랏빛 하늘색 박스티 (원작: 단추 없는 헐렁한 티셔츠 한 장을 원피스처럼): 목에서 허벅지 중간까지 허리선 없이
# 곧게 떨어지는 닫힌 셸. 가슴(bust) 아래로 천이 걸쳐 내려가고 밑단만 살짝 퍼진다. 같은 색 속바지.
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.pants(dress_d, length=0.07, bag=0.004, blouse=0.0)
tee = cameo.Shell(e, dress, e.torso_top + 0.004 * k, 0.300 * k, off=0.012, th=0.004, skirt=True, cols=22, rows=14,
                  flare=[(0.0, -0.004), (0.12, 0.0), (0.55, 0.006), (1.0, 0.020)], cover=True)
tee.hem_trim(dress_d, width=0.008, th=0.002)
tee.done("dress")
# 둥근 목선 테두리 (티셔츠 시보리)
e.part("dress_neck", "body", lambda buf: elf.band(buf, (0, 0.004 * k, e.torso_top + 0.002 * k), (0, 0, 1), (1, 0, 0),
                                                  0.060 * k, 0.054 * k, 0.010 * k, 0.004 * k, segs=16, mat=dress_d,
                                                  w={"chest": 1.0}))

# ---- 흰 연구 가운: 앞이 열리고 무릎 위까지, 넓은 깃, 크고 헐렁한 소매
Z_COAT = 0.250 * k     # 원작: 허벅지 중간~무릎 위
coat_sh = cameo.Shell(e, coat, e.torso_top - 0.004 * k, Z_COAT,
                      gap=[(0.0, 32.0), (0.22, 18.0), (0.5, 16.0), (1.0, 22.0)], off=0.030, th=0.005, skirt=True,
                      rows=18, cols=26, flare=[(0.0, 0.0), (0.45, 0.014), (1.0, 0.046)])
coat_sh.edge_trim(coat, width=0.024, th=0.004, i1=6)                         # 접힌 깃 (라펠): 고른 폭 (계단 없음)
coat_sh.edge_trim(coat_d, width=0.007, th=0.002, i0=5)                        # 여밈단
coat_sh.hem_trim(coat_d, width=0.010, th=0.0025)
coat_sh.done("coat")


# 뒷깃: 목 뒤와 옆을 두르고 앞은 열린 세운 깃 (닫힌 고리는 목 보호대처럼 보였다)
col = cameo.Shell(e, coat, e.torso_top + 0.034 * k, e.torso_top - 0.006 * k, gap=46.0, off=0.030, th=0.005, rows=3,
                  cols=18, flare=[(0.0, 0.010), (1.0, 0.0)])
col.hem_trim(coat_d, width=0.006, th=0.002, row=0)
col.done("coat_collar")
e.sleeves(coat, length=1.0, off=0.020, flare=0.026, puff=0.006, cuff=(coat_d, 0.030, 0.005))

# 가슴 주머니 + 펜 2자루, 시장 신분증 (왼쪽 가슴), 허리 주머니 + 태블릿 (오른쪽)
uC = (e.torso_top - (cz + 0.02 * k)) / (e.torso_top - Z_COAT)
uW = (e.torso_top - (wz - 0.08 * k)) / (e.torso_top - Z_COAT)


def chest_pocket(buf):
    Mx = coat_sh.frame_at(uC, 42, 0.001 * k)
    w = coat_sh.W[0][0]
    w = e._torso_wfn(Mx.to_translation(), 0)
    cameo.rrbox(buf, (0.050 * k, 0.004 * k, 0.048 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0)), mat=coat_d, w=w,
                r=0.15, segs=1)
    for j, (dx, m) in enumerate(((-0.010, pen_r), (0.008, pen_b))):
        b0 = Mx @ V((dx * k, -0.006 * k, 0.012 * k))
        elf.loft(buf, [{"c": b0, "rx": 0.0042 * k, "ry": 0.0042 * k, "w": w},
                       {"c": b0 + Mx.to_3x3() @ V((0, 0, 0.030 * k)), "rx": 0.0042 * k, "ry": 0.0042 * k, "w": w}],
                 segs=6, cap0="flat", cap1="round", mat=m)
    Mi = coat_sh.frame_at(uC + 0.10, 40, 0.002 * k) @ Matrix.Rotation(math.radians(-6), 4, "Y")
    cameo.rrbox(buf, (0.040 * k, 0.004 * k, 0.054 * k), Mi @ Matrix.Translation((0.004 * k, -0.002 * k, -0.034 * k)),
                mat=card, w=w, r=0.15, segs=1)
    cameo.rrbox(buf, (0.040 * k, 0.005 * k, 0.012 * k), Mi @ Matrix.Translation((0.004 * k, -0.003 * k, -0.016 * k)),
                mat=blue, w=w, r=0.15, segs=1)
    cameo.rrbox(buf, (0.016 * k, 0.006 * k, 0.012 * k), Mi @ Matrix.Translation((0.004 * k, -0.003 * k, -0.004 * k)),
                mat=dark, w=w, r=0.2, segs=1)


def hip_pockets(buf):
    for sg in (1, -1):
        Mx = coat_sh.frame_at(uW, sg * 52, 0.001 * k)
        w = cameo.skirt_w(e, Mx.to_translation())
        cameo.rrbox(buf, (0.064 * k, 0.004 * k, 0.060 * k), Mx @ Matrix.Translation((0, -0.002 * k, 0)), mat=coat_d,
                    w=w, r=0.15, segs=1)
        if sg < 0:   # 태블릿 (둠스데이 프로토콜 단말): 주머니에서 위로 삐져나옴
            Mt = Mx @ Matrix.Translation((0.004 * k, -0.006 * k, 0.020 * k)) @ Matrix.Rotation(math.radians(8), 4, "Y")
            cameo.rrbox(buf, (0.048 * k, 0.006 * k, 0.066 * k), Mt, mat=dark, w=w, r=0.15, segs=1)
            cameo.rrbox(buf, (0.040 * k, 0.002 * k, 0.030 * k), Mt @ Matrix.Translation((0, -0.0035 * k, 0.012 * k)),
                        mat=screen, w=w, r=0.1, segs=1)


e.part("chest_pocket", "body", chest_pocket)
e.part("hip_pockets", "body", hip_pockets)

# ---- 짙은 갈색 단화
e.boots(shoe, top=0.93, sole=(sole, 0.012), toe=0.003, off=0.010)

e.finalize()
e.export("characters/elena.glb")
