"""R41 현장 지휘관 (r41_officer). 4막 최종 목표 'R41 침공군 지휘부 궤멸'의 표적 (오리지널 무명 엘프).

설정: 흑뉴아가 에르피엔으로 떠난 뒤 모나티엄에 남은 현장 지휘관단의 지휘관. [원작] R41은 현장 지휘관에게 지휘권을
위임한 자율 임무 체계다. 전원 실전 경험이 있는 군인 출신.

근거와 해석 (docs/art/r41-style.md 7.3, docs/art/enemies-r41.md 2.4)
  - 아멜리아·포셔(R41)의 흰 코트를 군용으로 바꾼 본 화이트 롱코트: 제국 흑 깃·소맷단·밑단·앞여밈 테, 금속 단추
  - 제국 흑 베레모 + 앰버 머리띠 테 + 이중 테 휘장(본 화이트·앰버) = 현장 지휘관 (병종·계급은 베레모 색과 휘장 테)
  - 견장 판에 앰버 줄 4개(현장 지휘관), 오른 어깨 앰버 장식 끈, 가슴 계급장, 대각 멜빵과 앰버 버클
  - 제국 흑 망토(앰버 안감·밑단): 어깨 뒤에서 무릎까지, 지휘부 표적이 멀리서도 읽히는 실루엣
  - 왼 손목 오각 화면 태블릿(glow_dim), 오른 허리 P-2 권총집, 긴 군화
무장: P-2 '등에'(socket_hand_R 또는 socket_hip_R)

npm run model -- art/blender/enemies/r41_officer.py
npm run shot -- enemies/r41_officer.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41_troops as T  # noqa: E402

cb.reset()
t = T.Trooper("r41_officer", variant=dict(eye="#b04a6a", hair="#3a3550", style="long", goggles=None),
              body=dict(height=1.24, shoulders=1.02), segs=0.8, hand_q=0.7,
              # 기본 표정부터 자신만만하게: 눈을 조금 내리깔고 눈썹을 살짝 내림
              face=dict(base={"eye": {"top": 0.027, "tilt_in": -0.003}, "brow": {"ang": -6.0, "th": 0.0066}}))
M, k, e = t.M, t.k, t.e

t.hair(side_len=0.07, back_len=0.17, part=-14, sweep=10)
# 코트 상의 + 소매 (본 화이트, 제국 흑 깃·여밈·소맷단)
e.shirt(M["ceramic"], collar="stand", collar_mat=M["shell"], placket=M["shell"], buttons=M["metal"], flare=0.010)
e.sleeves(M["ceramic"], length=0.95, cuff=(M["shell"], 0.030, 0.005), flare=0.010)
e.pants(M["dark"], bag=0.008, blouse=0.004)
e.boots(M["shell"], top=0.50, sole=(M["sole"], 0.016), cuff=M["shell"])
e.gloves(M["shell"], cuff=M["amber"], cuff_h=0.010)
zb = T.lerp(e.hipj_z, e.waist_z, 0.72)
t.coat_skirt(M["ceramic"], z_top=zb + 0.006 * k, gap=15, off=0.027, flare=0.040, back_slit=3.0, hem=M["shell"],
             edge=M["shell"])
# 지휘관 망토: 제국 흑 겉감 + 앰버 안감, 어깨 뒤에서 무릎 아래까지 (최종 목표의 실루엣)
t.cape(M["shell"], lining=M["amber_d"], hem=M["amber"])
e.belt(M["shell"], z=zb, h=0.030, off=0.034, buckle=M["amber"], buckle_size=(0.042, 0.034))
# 대각 멜빵 (오른 어깨 → 왼 허리)
e.strap(M["shell"], [("torso", e.shoulder_z + 0.012 * k, -60, 0.016 * k), ("torso", e.chest_z + 0.02 * k, -18, 0.018 * k),
                     ("torso", e.waist_z, 30, 0.020 * k), ("torso", zb + 0.01 * k, 62, 0.026 * k)],
        width=0.020, th=0.004, name="sam_browne")
t.epaulet_boards(M["shell"], stripes=4)
t.aiguillette(M["amber"], side="R")
# 가슴 계급장 (짙은 판 + 앰버 막대 셋) + 왼팔 원형 휘장(테 있음)
e.patch(M["shell"], ("torso", e.chest_z + 0.045 * k, 28, 0.013 * k), size=(0.030, 0.024), name="rank_bg")
e.patch(M["amber"], ("torso", e.chest_z + 0.045 * k, 28, 0.0145 * k), size=(0.022, 0.016), shape="bars3", name="rank_fg")
t.shoulder_insignia(sides=("L",), t=0.20, ang=66, ring=M["ceramic"], bars=0, patch=M["shell"])
t.wrist_tablet(side="L")
t.holster(("torso", zb - 0.02 * k, -78, 0.040 * k))
t.beret(M["beret_black"], band=M["shell"], rib=M["metal"], piping=M["amber"], badge="round",
        badge_ring=[M["ceramic"], M["amber"]])
t.headset()
t.export("enemies/r41_officer.glb", props={"unit": "officer", "rank": "field_commander"},
         preview={"socket_hand_R": "weapons/r41/r41_sidearm.glb", "pose": "pistol"})
