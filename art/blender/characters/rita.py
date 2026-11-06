"""리타 (주인공, 오리지널): 모나티엄 진압반 특수작전부 현장 복장 (1막~4막).

과묵한 정찰병. 구리빛 비대칭 단발 + 청록 부서 스카프(등 뒤로 긴 꼬리) + 접어 올린 HUD 렌즈가 실루엣 포인트.
설정과 디자인 근거: docs/scenario.md 1장, docs/art/characters-rita-squad.md
1인칭 몸 규약: socket_eye, fpHide(head/arms). 1인칭 팔은 art/blender/viewmodels/rita_fp_arms.py (같은 팔 함수).

npm run model -- art/blender/characters/rita.py
npm run shot -- characters/rita.glb
npm run shot -- characters/rita.glb --focus rita_face --views front,34
npm run shot -- characters/rita.glb --mode fpbody --pitch -60 --arms viewmodels/rita_fp_arms.glb --weapon weapons/us/m4a1.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402

cb.reset()
e = elf.Elf("rita", **sop.RITA_BODY, **sop.RITA_TRI)
M = sop.mats("rita")
k = e.k

sop.rita_face(e)
sop.rita_hair(e, tail_tie=M["scarf"])

# ---- 특수작전부 전투복 + 리타의 팔(1인칭 팔과 같은 함수)
sop.uniform(e, M, arms_kw=sop.RITA_ARMS)
sop.scarf(e, M, style="tails", knot_az=sop.RITA_SCARF_KNOT, tail_len=(0.25, 0.19), sway=1.3)
sop.headset(e, M, side="R", monocle=True)

# ---- 낮은 가슴 장비 (탄창 파우치 3, 칼) + 가슴 오른쪽 위 부서 휘장
sop.chest_rig(e, M, n_mags=3, spread=24.0, light=True)
sop.emblem(e, M, ("torso", e.shoulder_z - 0.020 * k, -30, 0.026 * k), size=0.030, name="chest_emblem")

# ---- 허리·다리: 오른 허벅지 권총집(M17), 물통, 덤프 파우치, 왼쪽 건빵 주머니
sop.holster(e, M, side="R", t=0.27)
sop.belt_kit(e, M, dump=True, canteen=True)
e.pouch(M["pants"], ("leg_L", 0.34, 85, 0.024 * k), size=(0.05, 0.010, 0.058), flap=M["pants_d"], button=M["pants_d"],
        name="cargo_L")

e.finalize()
e.export("characters/rita.glb")
