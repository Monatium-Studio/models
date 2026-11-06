"""타이다: 교주 차원 모나티엄 시청 경비원. 1막 M2 시청 방어선에 투입된다(사용자 결정, 원작 침공전 모나티엄 배치).
R41 진압반장 '타이다(R41)'와는 다른 인물이다(사용자 확인). 이 모델은 교주 차원 타이다다.

원작 타이다(트릭컬 리바이브)의 로비 스탠딩·카드 차림을 따른다. 전투복 언어는 엘피니아 군 전투복 계열이다
(reference-notes 5장, 프롤로그 캐시의 전투복 기준). 근거: docs/art/characters-cameo3.md.
- 식별 요소: 짙은 갈색 단발, 갈색 눈과 능청스러운 윙크·메롱, 어두운 둥근 헬멧(세로 골, 앞 띠와 사각 버클),
  오른쪽 귀의 통신기(원통 귀덮개 + 앞으로 뻗은 원뿔, 청록 발광 줄), 밝은 웜그레이 작업복(점프수트형, 앞 지퍼, 어두운 깃),
  검은 벨트 + 사각 은색 버클 + 고리, 오른 허벅지에 끈으로 묶은 파우치(작은 원형 표식), 통 넓은 바지의 블라우징, 회색 군화,
  두 갈래 막대 무기(안쪽 금색 레일).
- 재해석: 통신기는 원작 형태(원통 + 원뿔 + 청록 줄)를 유지하되 3D로 다시 그렸다. 무기는 원작 형태 언어만 가져와
  장봉형 전기충격기로 새로 그렸다(별도 노드 taida_baton, socket_hand_R). 주말농장 법칙 아래의 모나티엄 제식(고전압).
- 표정: 키트 5종 + wink(오른눈 윙크, 교정 키 없음) + tongue(메롱) + lazy(놈팡이의 졸린 눈) + blink 교정 키.

npm run model -- art/blender/characters/taida.py
npm run shot -- characters/taida.glb
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
e = elf.Elf("taida", height=1.20, segs=0.66, hand_q=0.45, cheek=0.13)
k = e.k
M_ = elf.mat
suit = M_("ta_suit", "#b1aca6")          # 웜그레이 작업복 (원작 #b1aca6)
suit_d = M_("ta_suit_d", "#8c8781")
collar_m = M_("ta_collar", "#4f4850")
helm = M_("ta_helmet", "#4f4a53")        # 어두운 헬멧 (원작 #655d64보다 어둡게: 카드 실측)
helm_d = M_("ta_helmet_d", "#38343c")
web = M_("ta_web", "#4b444b")
boot = M_("ta_boot", "#5c5860")
boot_d = M_("ta_boot_d", "#45414a")
cyan = M_("ta_cyan", "#ffffff", emission="#8ff6ff", unlit=True)
mark = M_("ta_mark", "#9b949b")

# ---- 얼굴: 갈색 눈, 능청스러운 반쯤 감은 눈, 살짝 벌린 입
e.face(eye_color="#9a6236", iris_dark="#5a3218", iris_light="#e4b07a", pupil="#3a2010",
       lash="#3e2a26", brow="#4e342c", brow_th=1.1, blush="#f6a0a4", blush_size=1.2,
       base={"eye": {"top": 0.024, "ktop": 3.8, "tilt_in": 0.002},
             "brow": {"ang": 2.0, "dz": 0.066, "arch": 0.003},
             "mouth": {"w": 0.020, "curve": 0.0040, "open": 0.0040}},
       expr={
           # 메롱: 혀를 내민 능청 (원작 카드)
           "tongue": {"eye": {"top": 0.022, "lift": 0.008},
                      "brow": {"ang": 4.0, "dz": 0.068},
                      "mouth": {"w": 0.026, "curve": 0.0050, "open": 0.0170, "top_arch": 0.0012}},
           # 놈팡이: 졸린 눈, 늘어진 입
           "lazy": {"eye": {"top": 0.010, "ktop": 5.6},
                    "brow": {"ang": 8.0, "dz": 0.064},
                    "mouth": {"w": 0.018, "curve": -0.0010}},
       })
c2.face_expr(e, "wink",
             both={"mouth": {"w": 0.026, "curve": 0.0060, "open": 0.0150, "top_arch": 0.0012}},
             R={"eye": {"close": 1.0}, "brow": {"dz": 0.062, "ang": -6.0}},
             L={"eye": {"top": 0.026, "lift": 0.006}, "brow": {"dz": 0.070, "ang": 6.0}},
             corner=(0.0030, 0.0050), blink_fix=False)

# ---- 머리: 짙은 갈색 단발 (헬멧 아래, 끝이 바깥으로 살짝 뻗침)
h = e.hair("#6b4a3d", dark="#4a3229", light="#93705f")
h.cap(front=28, side=-10, back=-50, segs=16, rows=4)
h.bangs(n=6, spread=54, tip_el=-1, sweep=-6, seed=8.0)
h.sides(length=0.07, width=0.080, curl=0.9, puff=1.2)
h.back(length=0.05, n=7)

# ---- 헬멧: 어두운 둥근 돔 + 앞 띠와 사각 버클 + 세로 골 + 오른쪽 통신기
e.helmet(helm, off=0.038, front=12.0, side=2.0, back=-22.0, rim=helm_d, band_mat=helm_d, band_el=24.0,
         buckle=M_("ta_metal", tc.METAL), strap=web)


def helmet_bits(buf):
    w = {"head": 1.0}
    # 세로 골 (정수리에서 앞 띠 위까지 4줄)
    for az in (-36.0, -12.0, 12.0, 36.0):
        pts, nrm, ups = [], [], []
        for el in (32.0, 50.0, 66.0, 80.0):
            p, n = e.head_point(az, el, 0.0405 * k)
            pts.append(p)
            nrm.append(n)
            ups.append(V((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0)))
        elf._loop(buf, pts, nrm, ups, 0.005 * k, 0.0025 * k, mat=helm_d, w=w, closed=False)
    # 통신기: 오른쪽(-X) 귀 위 원통 귀덮개 + 앞으로 뻗은 원뿔 (청록 발광 줄)
    p, n = e.head_point(-80.0, -8.0, 0.030 * k)      # 헬멧 테두리 아래, 귀 뿌리 위 (헬멧 셸 밖)
    ax = n.normalized()
    loft(buf, [{"c": p - ax * 0.006 * k, "rx": 0.036 * k, "ry": 0.036 * k, "w": w},
               {"c": p + ax * 0.014 * k, "rx": 0.036 * k, "ry": 0.036 * k, "w": w},
               {"c": p + ax * 0.022 * k, "rx": 0.028 * k, "ry": 0.028 * k, "w": w}], segs=12, cap0="flat",
         cap1="flat", mat=web, ref=(0, 0, 1))
    tip0 = p + ax * 0.020 * k
    fwd = V((-0.50, -0.84, -0.18)).normalized()      # 앞·바깥·살짝 아래 (원작: 볼 옆으로 뻗은 뿔)
    loft(buf, [{"c": tip0, "rx": 0.022 * k, "ry": 0.022 * k, "w": w},
               {"c": tip0 + fwd * 0.050 * k, "rx": 0.014 * k, "ry": 0.014 * k, "w": w},
               {"c": tip0 + fwd * 0.100 * k, "rx": 0.002 * k, "ry": 0.002 * k, "w": w}], segs=8, cap0="flat",
         cap1="flat", mat=helm_d, ref=(0, 0, 1))
    loft(buf, [{"c": tip0 + fwd * 0.012 * k + V((0, 0, 0.0185 * k)), "rx": 0.004 * k, "ry": 0.003 * k, "w": w},
               {"c": tip0 + fwd * 0.078 * k + V((0, 0, 0.0065 * k)), "rx": 0.0025 * k, "ry": 0.002 * k, "w": w}],
         segs=6, cap0="flat", cap1="round", mat=cyan)
    disc(buf, p + ax * 0.017 * k + V((0, -0.006 * k, -0.010 * k)), ax, (0, 0, 1), 0.004 * k, 0.004 * k,
         0.0015 * k, segs=8, mat=cyan, w=w)


e.part("helmet_bits", "head", helmet_bits)

# ---- 작업복: 밝은 웜그레이 점프수트형 상의(앞 지퍼, 어두운 깃) + 같은 천 바지
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(suit, collar="stand", collar_mat=collar_m, placket=suit_d, flare=0.014)
e.sleeves(suit, length=0.94, off=0.012, flare=0.008, cuff=(suit_d, 0.020, 0.004))
m = tc.base_gear(e, "ta", pants=suit, pants_d=suit_d, boots=boot, boots_d=boot_d, bag=0.020, blouse=0.026,
                 boots_top=0.70)
e.pouch(suit, ("torso", cz - 0.030 * k, 40, 0.010 * k), size=(0.040, 0.006, 0.040), flap=suit_d,
        button=m["metal"], name="chest_pocket_L")
# 오른 허벅지 파우치 (끈 2줄, 덮개의 작은 원형 표식)
e.pouch(web, ("leg_R", 0.30, -80, 0.026 * k), size=(0.050, 0.026, 0.060), flap=collar_m, strap=m["belt"],
        name="thigh_pouch")
e.patch(mark, ("leg_R", 0.27, -80, 0.054 * k), size=(0.016, 0.016), shape="round", name="pouch_mark")

e.finalize()

# ---- 장봉형 전기충격기 (별도 노드 baton): 오른손에 쥐고 전극을 아래 앞쪽으로 기울여 든다 (원작 카드 자세)
bt = tc.rail_baton(e)
sock = bpy.data.objects["socket_hand_R"]
pos = sock.matrix_world.translation.copy()
Mw = tc.frame_world(V((-0.25, -0.40, -0.88)), V((0.0, -1.0, 0.4)))
Mw.translation = pos
tc.attach(e, bt, "socket_hand_R", Mw, "baton", props={"tip": "0,%.3f,%.3f" % (0.56 * k, 0.03 * k)})

e.export("characters/taida.glb")
