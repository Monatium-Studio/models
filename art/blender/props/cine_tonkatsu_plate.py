"""수용소 해방 장면의 돈까스 접시 (props/cine_tonkatsu_plate.glb). 로네가 왼손에 들고 먹으며 달려 나온다.

[원작] 로네의 돈까스 사랑(표정 dreamy = 돈까스 상상). [오리지널] 수용소 배식으로 받은 돈까스를 두고 갈 수 없다는 장면
(2026-11-01 사용자 확정, docs/script/act2c.md).
디자인: 흰 둥근 접시(지름 0.2 m, 엘프 체격 기준) + 테 + 금색 가는 줄, 썰어 놓은 돈까스 6조각(겉은 황금빛 튀김옷,
단면은 흰 고기), 갈색 소스 줄, 채 썬 양배추 더미, 레몬 한 조각, 파슬리 한 점.

원점 = 왼손이 쥐는 접시 테(손가락은 접시 밑, 엄지는 테 위). 접시는 Blender +Y 쪽으로 뻗고 위가 +Z
→ 손 소켓에서 회전 0이면 손 앞에 평평하게 놓인다 (hold.ts: 소품 앞 -Z three = Blender +Y).

npm run model -- art/blender/props/cine_tonkatsu_plate.py
npm run shot -- props/cine_tonkatsu_plate.glb --views top,34,side
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
mk.PAL.update({
    "plate_w": "#f4f1ea",
    "plate_line": "#d9b45e",
    "katsu": "#d79a3e",        # 튀김옷
    "katsu_d": "#b0722c",      # 튀김옷 그늘·가장자리
    "katsu_in": "#f3e6d2",     # 단면 (흰 고기)
    "sauce": "#5a2f1e",
    "cabbage": "#c7e39a",
    "cabbage_d": "#9fca73",
    "lemon": "#f2d84f",
    "parsley": "#4f9a45",
})
C = mk.City("cine_tonkatsu_plate", prop=True)
R = 0.1
CY = R + 0.004          # 접시 가운데 (원점 = 손 쪽 테)
Z0 = 0.0
# 접시: 바닥 굽 + 넓은 판 + 테 (도넛)
C.cyl("plate_w", (0, CY, Z0 - 0.006), (0, CY, Z0), R * 0.55, segs=24, kind="detail")
C.cyl("plate_w", (0, CY, Z0), (0, CY, Z0 + 0.008), R, segs=32, kind="main")
mk._bm_torus(C.bm("plate_w", "main"), (0, CY, Z0 + 0.009), R - 0.006, 0.006, seg=36, rseg=6)
mk._bm_torus(C.bm("plate_line", "fine"), (0, CY, Z0 + 0.0092), R - 0.017, 0.0016, seg=36, rseg=4)

# 양배추: 뒤쪽(먼 쪽) 더미 + 채 몇 가닥
C.blob("cabbage", (0.028, CY + 0.042, Z0 + 0.022), 0.034, scale=(1.2, 0.9, 0.62), segs=10, rings=6)
for i in range(7):
    a = i / 7 * math.tau
    x, y = 0.028 + math.cos(a) * 0.016, CY + 0.042 + math.sin(a) * 0.012
    C.rbox("cabbage_d", (x, y, Z0 + 0.036 + (i % 2) * 0.004), (0.028, 0.004, 0.003), rot=(0, 0, math.degrees(a) + 60),
           kind="detail")

# 돈까스: 6조각을 비스듬히 기대어 늘어놓는다 (단면이 위·앞을 본다)
SL = 6
for i in range(SL):
    x = -0.058 + i * 0.019
    y = CY - 0.008 + (i % 2) * 0.003
    tilt = 18
    rot = (0, tilt, 8)
    # 튀김옷 (조각)
    C.rbox("katsu", (x, y, Z0 + 0.022), (0.016, 0.078, 0.024), rot=rot, kind="main")
    # 단면 (오른쪽 면에 붙인 흰 판)
    C.rbox("katsu_in", (x + 0.0075, y, Z0 + 0.022), (0.002, 0.066, 0.016), rot=rot, kind="fine")
    # 소스 줄
    C.rbox("sauce", (x - 0.001, y + 0.006, Z0 + 0.0345), (0.012, 0.05, 0.002), rot=(0, tilt, 8), kind="fine")
# 튀김옷 가장자리 그늘 (아래 띠)
C.box("katsu_d", -0.068, 0.05, CY - 0.05, CY + 0.034, Z0 + 0.008, Z0 + 0.012, kind="detail")

# 레몬 한 조각 (쐐기) + 파슬리
C.prism("lemon", [(0.07, CY - 0.03), (0.088, CY - 0.012), (0.062, CY - 0.008)], Z0 + 0.008, Z0 + 0.02, kind="detail",
        top=True)
C.blob("parsley", (0.05, CY - 0.05, Z0 + 0.016), 0.008, segs=8, rings=4, kind="detail")

C.marker("grip", (0, 0.0, Z0 - 0.002))
C.finish("props/cine_tonkatsu_plate.glb", root_props={"outline": 0.0016}, detail_outline=0.0009)
