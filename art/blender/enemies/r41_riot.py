"""R41 진압반 (r41_riot). 타이다(R41) 휘하의 근접 압박형 단역 (오리지널 무명 엘프).

근거: docs/art/r41-style.md 7.2, PV 3:00~3:03 (소총병 헬멧·전투복)
  - 라벤더 회색 베레모(진압반 = 타이다(R41) 근무모 색) + 앰버 육각 휘장, 앰버 렌즈 고글
    (타이다(R41)의 주황 고글을 '반 표식'으로만 이어받음, 인물 복제 아님)
  - 두꺼운 제국 흑(shell) 판 조끼, 가슴에 앰버 엘프 로고, 양팔 앰버 띠 한 줄 = 진압반
  - 진압반 어깨 표식: 짙은 패치 + 앰버 '육각' 휘장 + 엘프 로고 (소총병의 원형 휘장과 구분)
  - 어깨·팔꿈치·무릎 보호대, 장갑, 오른 허벅지 P-2 권총집
무장: S-3 '말벌집'(socket_hand_R), 방패 r41_riot_shield.glb(socket_hand_L), 보조 P-2(socket_hip_R)

npm run model -- art/blender/enemies/r41_riot.py
npm run shot -- enemies/r41_riot.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41_troops as T  # noqa: E402

cb.reset()
t = T.Trooper("r41_riot", variant=dict(eye="#b06a4a", hair="#4b3a4e", style="bob"),
              body=dict(shoulders=1.04, limb=1.03))
M, k, e = t.M, t.k, t.e

t.hair(tip_el=8)
t.uniform(gloves=M["dark"], thigh_pouch=False, cuff_light=False, pockets=False)
t.plate_vest(M["shell"])
t.pads(M["shell"], knees=True, elbows=True, shoulders=True)
t.arm_band(M["amber"], t=0.40)
t.shoulder_insignia(shape="hex", t=0.22, ang=70, bars=1)
# 가슴 엘프 로고 (판 위, 앰버) + 판 볼트 4개 + 아래 막대 부호
t.chest_logo(("torso", e.chest_z + 0.020 * k, 0, 0.041 * k), size=0.056, plate=M["dark"], plate_size=0.040)


def plate_detail(buf, Mx, w):
    for dx, dz in ((-0.052, 0.040), (0.052, 0.040), (-0.050, -0.052), (0.050, -0.052)):
        T.ngon_disc(buf, Mx @ T.Matrix.Translation((dx * k, 0.006 * k, dz * k)), 0.0042 * k, 0.002 * k, M["metal"], w,
                    n=6)
    for i, dx in enumerate((-0.016, -0.008, 0.004, 0.012)):
        T.flat_quad(buf, Mx @ T.Matrix.Translation((dx * k, -0.0005 * k, -0.050 * k)), 0.004 * k, 0.012 * k,
                    M["frame_d"], w)


e.gear("plate_detail", ("torso", e.chest_z + 0.0 * k, 0, 0.041 * k), plate_detail)
t.holster(("leg_R", 0.26, -82, 0.022 * k))
t.beret(M["beret_riot"], badge="hex")
t.goggles("down", lens=M["visor_amber"], frame=M["shell"])
t.headset()
t.export("enemies/r41_riot.glb", props={"unit": "riot"},
         preview={"socket_hand_R": "weapons/r41/r41_suppressor.glb", "socket_hand_L": "enemies/r41_riot_shield.glb",
                  "pose": "shield"})
