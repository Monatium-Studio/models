"""리타 프롤로그 1인칭 팔 (엘피니아 군 전투복). 소매·소맷단·장갑·부대 패치는 characters/rita_prologue.py와 같은
monatium_sop.elfinia_arms 함수. 포즈 표는 1막 팔과 같다 (monatium_sop.RITA_FP_POSES).

- 루트 = 카메라 원점(socket_eye), 정면 = Blender +Y (three.js -Z). 레스트 포즈 = hold_rifle
- 클립: hold_rifle(M4A1), ads_rifle, hold_pistol(M17), ads_pistol

npm run model -- art/blender/viewmodels/rita_prologue_fp_arms.py
npm run shot -- weapons/us/m4a1.glb --mode fp --arms viewmodels/rita_prologue_fp_arms.glb --armsanim hold_rifle
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402

cb.reset()
e = elf.Elf("rita_prologue_fp", hand_q=1.2, **sop.RITA_BODY)
EM = sop.elfinia_mats("ritap")
sop.elfinia_arms(e, EM)

sop.build_fp_arms(e, sop.RITA_FP_POSES, "hold_rifle", "viewmodels/rita_prologue_fp_arms.glb", outline=0.0022)
