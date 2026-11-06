"""제스티 (특수작전부 통신·폭파, 오리지널).

농담이 끊이지 않는 무전 담당. 폭약 얘기만 나오면 눈이 반짝인다. 리타의 침묵에 혼자 대사를 붙여 주는 분위기 메이커.
실루엣: 땅딸막한 체형, 큰 무전기 배낭과 뒤로 휜 채찍 안테나(분대에서 가장 높은 점), 진압 헬멧 위로 올린 고글,
걷어 올린 소매, 왼팔에 묶은 청록 스카프, 벨트 앞 폭약 블록과 기폭선 실패. 분홍 머리가 헬멧 밖으로 부풀어 나온다.

npm run model -- art/blender/characters/squad_jesty.py
npm run shot -- characters/squad_jesty.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402
from mathutils import Vector as V  # noqa: E402,F401

cb.reset()
e = elf.Elf("jesty", height=1.16, limb=1.10, hips=1.06, shoulders=1.02, cheek=0.14, chest=0.12, segs=0.75,
            hand_q=0.6)
M = sop.mats("jesty")
k = e.k

e.face(eye_color="#3d9c6c", lash="#3a2027", brow="#b8566e", blush_size=1.15,
       base={"eye": {"top": 0.034, "ktop": 2.6, "bot": 0.056},
             "iris": {"ry": 0.0470, "cz": 0.0045},   # 홍채 위쪽이 윗눈꺼풀(0.034+0.016)에 잘리게
             "brow": {"ang": 6.0, "dz": 0.072, "arch": 0.006},
             "mouth": {"w": 0.026, "curve": 0.0062, "open": 0.0060, "top_arch": -0.001}})
# 머리 (헤어 v2): 진압 헬멧 테 아래로 짧게 삐친 앞머리, 볼 옆으로 둥글게 부푼 옆머리(안으로 말림),
# 헬멧 뒤로 부풀어 나온 짧은 뒷머리. 덩어리 두께(volume)를 키워 헬멧 밖으로 부풀어 보이게 한다.
h = e.hair("#e98ca6", dark="#c96784", light="#f8c7d4", volume=1.15)
h.cap(front=24, side=-10, back=-46, segs=18, rows=4)   # 헬멧 아래: 정수리는 성글게
h.bangs(n=6, spread=58, tip_el=-10.0, jag=0.45, seed=7.0)
h.sides(length=0.02, width=0.070, az=74, flare=0.03, puff=1.8, curl=0.5)
h.back(length=0.0, n=5, flare=0.045)

sop.uniform(e, M, lean=True, arms_kw=dict(roll=True, rank_bars=1, emblem_on=True), knee_pads=True)
sop.riot_helmet(e, M)
sop.goggles(e, M, el=40.0, off=0.044)
sop.scarf(e, M, style="arm")
sop.backpack_radio(e, M, antenna_len=0.46)
sop.harness(e, M)
sop.handset(e, M, ("torso", e.shoulder_z - 0.012 * k, -32, 0.030 * k))
sop.charges(e, M, angles=(-34, 30))
sop.wire_spool(e, M, ("torso", lerp_z := e.waist_z - 0.03 * k, 110, 0.030 * k))
e.pouch(M["gear"], ("torso", e.chest_z - 0.004 * k, 0, 0.026 * k), size=(0.060, 0.024, 0.050), flap=M["gear_l"],
        button=M["metal"], molle=M["gear_d"], name="chest_pouch")
e.pouch(M["gear"], ("leg_R", 0.30, -80, 0.026 * k), size=(0.052, 0.026, 0.060), flap=M["gear_l"], button=M["metal"],
        strap=M["gear"], name="thigh_pouch")

e.finalize()
e.export("characters/squad_jesty.glb")
