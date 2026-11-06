"""사브르 (특수작전부 분대장, 오리지널).

칼처럼 짧게 끊어 명령하는 분대장. 말수 적은 리타 몫까지 판단을 소리 내어 말한다("리타, 먼저. 둘 따라붙어").
실루엣: 분대에서 가장 큰 키와 넓은 어깨, 범프 헬멧(앞에 금줄 = 지휘관), 판 조끼와 지도 창, 붐 마이크,
헬멧 아래로 길게 늘어진 검푸른 포니테일. 스카프는 목 앞에서 단정하게 맨다.
근거: docs/art/characters-rita-squad.md

npm run model -- art/blender/characters/squad_sabre.py
npm run shot -- characters/squad_sabre.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402
from mathutils import Vector as V  # noqa: E402,F401

cb.reset()
e = elf.Elf("sabre", height=1.25, shoulders=1.07, limb=1.03, chest=0.30, ear_angle=10.0, segs=0.75, hand_q=0.6)
M = sop.mats("sabre")
k = e.k

e.face(eye_color="#5b7ea8", lash="#232634", brow="#232634", brow_th=1.25, blush_size=0.8,
       base={"eye": {"top": 0.025, "ktop": 3.6, "tilt_in": -0.004, "cout": 0.019},
             "brow": {"ang": -9.0, "dz": 0.060, "arch": 0.001, "len": 0.044},
             "mouth": {"w": 0.021, "curve": 0.0018}})
# 머리 (헤어 v2): 범프 헬멧(앞 테 12도) 아래로 왼쪽 가르마에서 쓸어 넘긴 앞머리가 눈썹까지 나오고,
# 귀 앞 짧은 옆머리, 헬멧 뒤 테 아래에서 묶어 등으로 길게 늘어진 낮은 포니테일(금색 끈).
h = e.hair("#2f3344", dark="#22252f", light="#5d6680")
h.cap(front=26, side=-12, back=-50, part=22, segs=18, rows=4)   # 헬멧 아래: 정수리는 성글게
h.bangs(n=5, spread=52, tip_el=-7.0, part=22, sweep=18, jag=0.25, seed=2.0)
h.sides(length=0.035, width=0.058, az=72)
h.back(length=0.02, n=3, spread=95)
sop.hair_tail(h, el=-33, length=0.34, width=0.085, out=0.55, droop=0.35, clumps=2, tie=M["gold"])

sop.uniform(e, M, lean=True, arms_kw=dict(sleeve_len=0.95, rank_bars=2, gold=True))
sop.plate_carrier(e, M)
sop.scarf(e, M, style="neat")
sop.bump_helmet(e, M, gold=True)
sop.headset(e, M, side="L", monocle=False, mic=True, band=False, pod_off=0.044)
sop.rank(e, M, ("torso", e.shoulder_z - 0.030 * k, -26, 0.040 * k), bars=2, gold=True, name="chest_rank")
sop.handset(e, M, ("torso", e.shoulder_z - 0.010 * k, 34, 0.040 * k))
sop.holster(e, M, side="R", t=0.27)
sop.belt_kit(e, M, dump=False, canteen=True, pouches=((-40, (0.040, 0.022, 0.046)), (40, (0.040, 0.022, 0.046))))
e.pouch(M["gear"], ("leg_L", 0.30, 80, 0.026 * k), size=(0.050, 0.014, 0.066), flap=M["gear_l"], button=M["metal"],
        strap=M["gear"], name="map_case")

e.finalize()
e.export("characters/squad_sabre.glb")
