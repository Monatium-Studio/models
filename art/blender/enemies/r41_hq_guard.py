"""R41 지휘부 직속 경호대 (r41_hq_guard). 현장 지휘부를 지키는 정예 (오리지널 무명 엘프).

근거와 해석 (docs/art/r41-style.md 7.3 '소총병 장비 + ceramic 한쪽 어깨 망토', docs/art/enemies-r41.md 2.5)
  - 바탕은 PV 소총병(3:00~3:03): 전투복, 연기색 고글, 헤드셋, 손가락 없는 장갑
  - 정예 표식: 본 화이트 베레모 + 제국 흑 머리띠 + 앰버 휘장(흑 테), 왼 어깨 본 화이트 망토(앰버 테, 등에 엘프 로고)
  - 제국 흑 판 조끼 + 본 화이트 앞판, 오른팔 원형 휘장(본 화이트 테), 무릎 보호대
무장: L-11 '잠자리' 지정사수 소총(socket_hand_R)

npm run model -- art/blender/enemies/r41_hq_guard.py
npm run shot -- enemies/r41_hq_guard.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41_troops as T  # noqa: E402

cb.reset()
t = T.Trooper("r41_hq_guard", variant=dict(eye="#7f86a8", hair="#26222c", style="bob", goggles="down"),
              body=dict(shoulders=1.05, limb=1.04),
              face=dict(base={"eye": {"top": 0.027}, "brow": {"ang": -4.0}}))
M, k, e = t.M, t.k, t.e

t.hair()
t.uniform(knee=False, thigh_pouch=True, pockets=False)
t.plate_vest(M["shell"], front=(-60, 60), off=0.019, th=0.010, bulge=0.010)
fo = t._front_off
# 본 화이트 앞판 (가슴 위쪽) + 흑 로고
zc = e.chest_z + 0.022 * k
t.panel(M["ceramic"], zc - 0.030 * k, zc + 0.034 * k, -30, 30, off=fo - 0.004, th=0.006, cols=7, rows=3, bulge=0.004,
        name="front_plate")
t.chest_logo(("torso", zc + 0.002 * k, 0, (fo + 0.008) * k), size=0.040, plate=M["ceramic"], logo_mat=M["shell"],
             plate_size=0.001)
# 판 아래 L-11 탄창 파우치 셋
for i, a in enumerate((-26, 0, 26)):
    e.pouch(M["dark2"], ("torso", e.waist_z - 0.004 * k, a, (fo - 0.006) * k), size=(0.034, 0.022, 0.046),
            flap=M["dark"], button=M["steel"], name=f"mag_pouch_{i}")
t.pads(M["shell"], knees=True, elbows=False)
t.capelet(M["ceramic"], side="L", lining=M["shell"], trim=M["amber"], logo_mat=M["shell"], off=0.044)
t.shoulder_insignia(sides=("R",), t=0.20, ang=64, ring=M["ceramic"], bars=3)
t.beret(M["ceramic"], band=M["shell"], rib=M["metal"], badge="round", badge_ring=M["shell"])
t.goggles("down")
t.headset()
t.export("enemies/r41_hq_guard.glb", props={"unit": "hq_guard"},
         preview={"socket_hand_R": "weapons/r41/r41_dmr.glb", "pose": "rifle"})
