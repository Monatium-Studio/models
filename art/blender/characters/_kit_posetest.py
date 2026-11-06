"""키트 리그 검증: 본을 돌린 포즈를 액션으로 넣어 내보낸다 (three.js 스키닝이 실제로 따라오는지 확인).

npm run model -- art/blender/characters/_kit_posetest.py
npm run shot -- characters/_kit_posetest.glb --mode single --view 34
npm run shot -- characters/_kit_posetest.glb --mode single --view front

확인 항목: 팔·팔꿈치·손목·손가락(주먹), 고개 돌림·숙임, 허리 굽힘, 다리 들기·무릎, 귀, 포니테일 본, 표정(smile)
본 회전 규칙(로컬 오일러, 도)은 docs/art/ELF_KIT.md '리그' 절.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402

cb.reset()
e = elf.Elf("posetest")
suit = elf.mat("pt_suit", "#7f8aa3")
e.face(eye_color="#4f78b0")
h = e.hair("#c9a15e")
h.cap()
h.bangs(n=7)
h.sides(length=0.04)
h.back(length=0.0)
h.ponytail(height=28, length=0.26)
e.shirt(suit, off=0.004, flare=0.0, collar="stand")
e.sleeves(suit, length=0.9, off=0.004, flare=0.0)
e.pants(suit, off=0.004, bag=0.0, blouse=0.0, length=0.86)
e.gloves(elf.mat("pt_glove", "#4b4844"), cuff=elf.mat("pt_cuff", "#3a3836"))   # 오른손: 장갑 낀 주먹
e.finalize()

fist = {f"{f}_01_R": (70, 0, 0) for f in ("f1", "f2", "f3")}
fist.update({f"{f}_02_R": (80, 0, 0) for f in ("f1", "f2", "f3")})
fist.update({"thumb_01_R": (25, 0, 0), "thumb_02_R": (40, 0, 0)})
e.pose({
    "upperarm_L": (70, 0, 0),     # 왼팔 앞으로 들기
    "forearm_L": (60, 0, 0),      # 왼 팔꿈치 굽힘
    "hand_L": (30, 0, 0),         # 손목 손바닥 쪽으로
    "upperarm_R": (0, 0, -35),    # 오른팔 옆으로 더 내리기
    "forearm_R": (25, 0, 0),
    **fist,
    "head": (15, 25, 0),          # 고개 숙이고 왼쪽으로
    "spine": (12, 0, 0),          # 허리 앞으로
    "thigh_L": (45, 0, 0),        # 왼다리 앞으로
    "shin_L": (-60, 0, 0),        # 무릎 굽힘 (뒤로 = 음수)
    "ear_L": (25, 0, 0),
    "hair_tail_01": (30, 0, 0),
})
for kb in e.face_obj.data.shape_keys.key_blocks:
    if kb.name == "smile":
        kb.value = 1.0
e.export("characters/_kit_posetest.glb")
