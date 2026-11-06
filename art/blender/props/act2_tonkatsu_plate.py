"""돈까스 접시 (2막 M5: 로네가 수용소 경비 식당에서 들고 뛰쳐나오는 접시) + 포크.

npm run model -- art/blender/props/act2_tonkatsu_plate.py
  → public/models/props/act2_tonkatsu_plate.glb, public/models/props/act2_fork.glb
원작 근거: 모나티엄 돈까스반(공기커틀릿·수소커틀릿 단속), 로네의 돈까스 상상 표정(dreamy). 연출은 오리지널(2026-11-01 사용자 확정).
규약: 접시 원점 = 바닥 가운데, 쥐는 점 `grip` = 테두리 아래(왼손이 받친다). 포크 원점 = 손잡이 쥐는 점. 엘프 손 크기에 맞춘 지름 0.2 m.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

mk.PAL.update({
    "plate": "#f4f1ea",
    "plate_rim": "#d9d4ca",
    "cutlet": "#d39a4a",
    "cutlet_d": "#a8692c",
    "cutlet_in": "#f2e2c4",
    "cabbage": "#cfe3a4",
    "cabbage_d": "#a9c67a",
    "lemon": "#f3d75a",
    "sauce": "#5a2e1c",
})

# ---------------------------------------------------------------- 접시
cb.reset()
C = mk.City("act2_tonkatsu_plate", prop=True)
R = 0.1
C.cyl("plate", (0, 0, 0), (0, 0, 0.006), R * 0.62, segs=20)
C.cyl("plate", (0, 0, 0.006), (0, 0, 0.016), R, r2=R * 1.02, segs=24, cap=False)
C.cyl("plate_rim", (0, 0, 0.012), (0, 0, 0.0165), R * 1.02, segs=24)
C.cyl("plate", (0, 0, 0.006), (0, 0, 0.009), R * 0.78, segs=24)
# 양배추 채 (볼록한 더미)
C.blob("cabbage", (0.035, 0.03, 0.022), 0.034, (1.0, 0.9, 0.55), segs=9, rings=4)
C.blob("cabbage_d", (0.05, 0.012, 0.026), 0.02, (1.0, 1.0, 0.6), segs=7, rings=3)
# 돈까스 여섯 조각 (비스듬히 썬 단면이 보이게)
for i in range(6):
    t = (i - 2.5) * 0.019
    cx, cy = -0.022 + t * 0.35, -0.01 + t
    C.rbox("cutlet", (cx, cy, 0.024), (0.07, 0.017, 0.016), (0, 6 if i % 2 else -4, 28))
    C.rbox("cutlet_in", (cx + 0.004, cy - 0.0075, 0.0245), (0.058, 0.002, 0.009), (0, 0, 28), kind="fine")
    C.rbox("cutlet_d", (cx, cy, 0.0325), (0.066, 0.015, 0.002), (0, 6 if i % 2 else -4, 28), kind="detail")
# 소스 한 줄, 레몬 조각
C.rbox("sauce", (-0.022, -0.01, 0.0335), (0.012, 0.1, 0.0015), (0, 0, 28), kind="fine")
C.blob("lemon", (0.055, -0.045, 0.02), 0.016, (1.0, 0.55, 0.6), segs=8, rings=4)
C.marker("grip", (0, -R * 0.98, 0.004))
C.finish("props/act2_tonkatsu_plate.glb", root_props={"outline": 0.0025})

# ---------------------------------------------------------------- 포크
cb.reset()
F = mk.City("act2_fork", prop=True)
F.beam("steel", (0, -0.03, 0), (0, 0.06, 0), 0.008, 0.003)
for k in range(3):
    x = (k - 1) * 0.0035
    F.beam("steel", (x, 0.06, 0), (x, 0.085, 0.002), 0.0016, 0.0016)
F.finish("props/act2_fork.glb", root_props={"outline": 0.0015})

