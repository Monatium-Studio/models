"""케이트 (특수작전부 의무·후방 경계, 오리지널).

규정과 안전 수칙을 하나하나 짚는 잔소리꾼 의무병. 대답 없는 리타에게도 꼬박꼬박 상태 보고를 받아 낸다.
실루엣: 청록 부서 스카프를 두건처럼 동여맨 머리(뒤통수 매듭), 둥근 안경, 일자 앞머리의 연보라 단발,
의무 배낭(청록 원 안의 흰 더하기)과 위에 묶은 천 롤, 허벅지·허리의 의무 파우치.
원작 '카렌'(긴 갈색 머리, 머리띠, 앞치마)과 머리색·머리 모양·복장이 겹치지 않게 했다.

npm run model -- art/blender/characters/squad_karen.py
npm run shot -- characters/squad_karen.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402
from mathutils import Vector as V  # noqa: E402,F401

cb.reset()
e = elf.Elf("karen", height=1.19, limb=0.98, shoulders=0.98, chest=0.20, segs=0.8, hand_q=0.6)
M = sop.mats("karen")
k = e.k

e.face(eye_color="#4a66ad", lash="#2c2238", brow="#7d6aa0", blush_size=0.9,
       base={"eye": {"top": 0.028, "ktop": 3.0, "tilt_in": 0.003},
             "brow": {"ang": 7.0, "dz": 0.066, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0006}})
# 머리 (헤어 v2): 두건 아래 눈썹 위에서 가지런히 자른 일자 앞머리, 턱선까지 오는 연보라 단발.
# 키트 앞머리는 다발 끝이 뾰족하게 모이므로, 앞머리 다발만 끝을 뭉툭하게(p) 하고 길이를 고르게 맞춘다.
h = e.hair("#b9a6d9", dark="#9580bb", light="#e1d6f0")
h.cap(front=28, side=-12, back=-50, segs=18)   # 두건 아래: 열은 성글게 (행은 두건 테 근처가 뚫리지 않게 기본)
h.bangs(n=7, spread=58, tip_el=7.0, jag=0.0, seed=1.0)
h.sides(length=0.07, width=0.056, az=70, flare=0.004)
h.back(length=0.035, n=5, flare=0.012)


def blunt_bangs(locks):
    for lk in locks:
        if lk["region"] != "front":
            continue
        ca = (lk["a0"] + lk["a1"]) / 2
        u = ca / 58.0
        lk["L"] = h.s_of_el(ca, 2.5 + 4.0 * u * u)   # 이마를 따라 아주 낮은 아치
        lk["free"] = 0.030 * k                        # 끝 3cm만 갈라짐
        lk["p"] = 4.0                                 # 뭉툭한 끝
        lk["sweep"] = 0.0
        lk["curl"] = -0.004 * k


sop.hair_locks(h, blunt_bangs)

sop.uniform(e, M, lean=True, arms_kw=dict(sleeve_len=0.95, rank_bars=1, arm_band="L"))
sop.bandana(e, M)
sop.glasses(e, M)
sop.medic_pack(e, M)
sop.harness(e, M)
sop.med_pouch(e, M, ("torso", e.chest_z - 0.004 * k, -16, 0.028 * k), name="chest_med")
sop.med_pouch(e, M, ("leg_R", 0.30, -80, 0.026 * k), size=(0.050, 0.026, 0.060), strap=M["gear"], name="thigh_med")
sop.med_pouch(e, M, ("leg_L", 0.30, 80, 0.026 * k), size=(0.050, 0.026, 0.060), strap=M["gear"], name="thigh_med_L")
sop.belt_kit(e, M, dump=False, canteen=True, pouches=((-42, (0.040, 0.022, 0.046)),))
# 왼팔 흰 완장 위 청록 마름모
e.patch(M["white"], ("arm_L", 0.36, 62, 0.024 * k), size=(0.024, 0.016), name="medic_band_mark")
# 왼 멜빵의 지혈대
e.gear("tourniquet", ("torso", e.shoulder_z - 0.020 * k, 34, 0.030 * k),
       lambda buf, Mx, w: sop.rbox(buf, (0.020 * k, 0.018 * k, 0.050 * k), Mx @ sop.Matrix.Translation((0, -0.010 * k, 0)),
                                   mat=M["belt"], w=w, r=0.45, segs=1))

e.finalize()
e.export("characters/squad_karen.glb")
