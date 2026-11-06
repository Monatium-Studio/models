"""R41 돌격 편대 (r41_assault). 중무장 돌격병 (오리지널 무명 엘프).

원작: 에르피엔 결전에서 중성자탄이 자기들을 향했다는 사실에 동요하고, 죠안과 아멜리아(R41)의 설득으로 대거 이탈한
바로 그 부대다(docs/scenario.md M8). 그래서 고글을 헬멧에 올려 얼굴(동요·겁먹음 표정)이 늘 보이게 했다.

근거와 해석 (docs/art/enemies-r41.md 2.3)
  - 바탕은 소총병과 같은 PV 군복·베레모(3:00~3:03). 돌격 편대 표식 = 짙은 회색 베레모 + 머리띠 앰버 테 + 꺾쇠 휘장,
    어깨에도 앰버 꺾쇠 휘장
  - 중무장: 제국 흑 판 조끼 + 본 화이트 가로 띠(R41 드론의 흑백 띠와 같은 언어), 큰 본 화이트 어깨 장갑,
    본 화이트 무릎 보호대, 탄약 등짐, 판 앞 G-5 '땅벌' 3개
무장: K-7 '쐐기벌'(socket_hand_R)

npm run model -- art/blender/enemies/r41_assault.py
npm run shot -- enemies/r41_assault.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41_troops as T  # noqa: E402

cb.reset()
t = T.Trooper("r41_assault", variant=dict(eye="#6a8ab0", hair="#2f2c35", style="short", goggles="up"),
              body=dict(shoulders=1.08, limb=1.06, hips=1.04))
M, k, e = t.M, t.k, t.e

t.hair(tip_el=6, sweep=-10)
t.uniform(thigh_pouch=False, pockets=False)
t.plate_vest(M["shell"], front=(-66, 66), off=0.020, th=0.012, bulge=0.012)
# 흑백 띠: 판 가운데를 가로지르는 본 화이트 띠
fo = t._front_off
zb = e.waist_z + 0.035 * k
t.panel(M["ceramic"], zb, zb + 0.022 * k, -64, 64, off=fo - 0.006, th=0.0075, cols=11, rows=2, bulge=0.0,
        name="plate_band")
t.pads(M["ceramic"], knees=True, elbows=False, shoulders=True, shoulder_size=(0.104, 0.022, 0.090))
t.shoulder_insignia(shape="chevron", t=0.27, ang=72, bars=3)
# 판 앞: 엘프 로고(앰버) + G-5 3개
t.chest_logo(("torso", e.chest_z + 0.028 * k, 0, (fo + 0.001) * k), size=0.042, plate=M["dark"], plate_size=0.032)
for i, a in enumerate((-24, 0, 24)):
    t.grenade(("torso", e.waist_z + 0.002 * k, a, (fo - 0.004) * k), name=f"g5_{i}")
for i, a in enumerate((-48, 48)):
    e.pouch(M["dark2"], ("torso", e.waist_z - 0.016 * k, a, (fo - 0.006) * k), size=(0.044, 0.024, 0.046),
            flap=M["dark"], button=M["steel"], name=f"ammo_pouch_{i}")
t.backpack(band=M["ceramic"], logo_mat=M["amber"])
t.beret(M["beret_dark"], piping=M["amber"], badge="chevron", badge_az=64)
t.goggles("up")
t.headset()
t.export("enemies/r41_assault.glb", props={"unit": "assault"},
         preview={"socket_hand_R": "weapons/r41/r41_carbine.glb", "pose": "rifle"})
