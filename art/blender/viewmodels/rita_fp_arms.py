"""리타 1인칭 팔 뷰모델 (1막~4막 특수작전부 복장). 소매·장갑·손목 단말은 전신 모델(characters/rita.py)과 같은 함수.

- 루트(아마추어) = 카메라 원점(socket_eye), 정면 = Blender +Y (three.js -Z)
- 클립: hold_rifle(M4A1), hold_pistol(M17), ads_rifle, ads_pistol. 레스트 포즈 = hold_rifle
  (엔진이 클립을 재생하지 않아도 소총을 쥔 자세로 보인다)
- 오른손 소켓 = 무기 원점(파지점), 왼손 소켓 = 무기 grip_support. 무기 glb의 fpOffset·fpRot를 읽어 맞춘다.

npm run model -- art/blender/viewmodels/rita_fp_arms.py
npm run shot -- weapons/us/m4a1.glb --mode fp --arms viewmodels/rita_fp_arms.glb --armsanim hold_rifle
npm run shot -- weapons/us/m4a1.glb --mode fp --ads 1 --arms viewmodels/rita_fp_arms.glb --armsanim ads_rifle
npm run shot -- weapons/us/m17.glb --mode fp --arms viewmodels/rita_fp_arms.glb --armsanim hold_pistol
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402

cb.reset()
e = elf.Elf("rita_fp", hand_q=1.2, **sop.RITA_BODY)
M = sop.mats("rita")      # 전신과 같은 머티리얼 이름·색
sop.rita_arms(e, M)

# 포즈 표: 무기별 손 목표·손목 꺾기·팔 방향 (monatium_sop.RITA_FP_POSES, 프롤로그 팔과 공용)
POSES = sop.RITA_FP_POSES

vm = sop.build_fp_arms(e, POSES, "hold_rifle", "viewmodels/rita_fp_arms.glb", outline=0.0022)

if os.environ.get("VM_DEBUG"):
    sop.debug_scene(vm, "hold_rifle", "weapons/us/m4a1.glb", "viewmodels/_debug_rita_rifle.glb")
    sop.debug_scene(vm, "hold_pistol", "weapons/us/m17.glb", "viewmodels/_debug_rita_pistol.glb")
