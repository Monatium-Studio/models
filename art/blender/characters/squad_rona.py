"""로나 (특수작전부 지정사수, 오리지널).

느긋하게 반쯤 감은 눈으로 거리·풍속·탄착을 쉬지 않고 중얼중얼 중계하는 '숫자 수다쟁이'.
실루엣: 분대에서 가장 작은 키, 넓은 챙의 정글모와 위장 천 조각, 어깨까지 덮는 두툼한 스카프 두건,
챙 아래로 내려오는 민트색 낮은 트윈테일, 가슴의 거리측정기와 몸을 가로지르는 소총 멜빵.
원작 '로네'(긴 갈색 머리, 머리띠, 한쪽으로 묶은 꼬리)와 겹치지 않게 머리색·머리 모양·모자를 모두 다르게 했다.

npm run model -- art/blender/characters/squad_rona.py
npm run shot -- characters/squad_rona.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402
from mathutils import Vector as V  # noqa: E402,F401

cb.reset()
e = elf.Elf("rona", height=1.14, limb=0.94, shoulders=0.94, chest=0.10, ear_len=0.104, ear_angle=20.0, segs=0.75,
            hand_q=0.6)
M = sop.mats("rona", {"cloth": "#8b8592", "pants": "#5f5966"})
k = e.k

e.face(eye_color="#cf9f34", lash="#2e3a36", brow="#4f7f72", blush_size=1.05,
       base={"eye": {"top": 0.019, "ktop": 2.6, "tilt_out": -0.003},
             "brow": {"ang": 4.0, "dz": 0.066, "arch": 0.004},
             "mouth": {"w": 0.020, "curve": 0.0036}})
# 머리 (헤어 v2): 정글모 챙 아래로 눈썹까지 오는 앞머리, 귀 앞 옆머리, 챙 아래 귀 뒤에서 묶어
# 어깨로 늘어진 민트색 낮은 트윈테일(청록 끈).
h = e.hair("#86cdb8", dark="#5fa894", light="#c3eadf")
h.cap(front=26, side=-12, back=-50, segs=18, rows=4)   # 모자 아래: 정수리는 성글게
h.bangs(n=6, spread=56, tip_el=-6.0, jag=0.15, seed=5.0)
h.sides(length=0.05, width=0.060, az=70, puff=1.2)
h.back(length=0.03, n=5, spread=86)
sop.hair_twintails(h, az=118, el=-10, length=0.24, width=0.088, out=0.65, droop=0.7, clumps=1, tie=M["scarf_d"])

sop.uniform(e, M, lean=True, arms_kw=dict(sleeve_len=0.95, rank_bars=1, elbow_pads=True))
sop.scarf(e, M, style="cowl")
sop.boonie(e, M, crown=M["pants"], brim_w=0.075, band_mat=M["scarf"], strips=(150, 200, 235, -40))
sop.ghillie(e, M, n=6)
sop.sling(e, M, side="R")
sop.rangefinder(e, M, ("torso", e.chest_z + 0.004 * k, 18, 0.040 * k))
for i, a in enumerate((-26, -6)):
    e.pouch(M["gear"], ("torso", e.chest_z - 0.004 * k, a, 0.030 * k), size=(0.030, 0.024, 0.070), flap=M["gear_l"],
            button=M["metal"], molle=M["gear_d"], name=f"dmr_mag{i}")
sop.harness(e, M)
sop.belt_kit(e, M, dump=True, canteen=True)
e.pouch(M["gear"], ("leg_L", 0.30, 80, 0.026 * k), size=(0.048, 0.024, 0.056), flap=M["gear_l"], button=M["metal"],
        strap=M["gear"], name="thigh_pouch")

e.finalize()
e.export("characters/squad_rona.glb")
