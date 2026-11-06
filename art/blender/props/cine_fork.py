"""로네의 포크 (props/cine_fork.glb). 돈까스 한 조각을 꽂은 채 입으로 가져간다.

원점 = 오른손이 쥐는 자루 가운데, 갈래는 Blender +Y, 위 +Z (소품 앞 = +Y, hold.ts 규약).
은색 자루 0.12 m + 4갈래 머리, 끝에 돈까스 한 조각 (황금빛 튀김옷 + 흰 단면 + 소스).

npm run model -- art/blender/props/cine_fork.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402

cb.reset()
mk.PAL.update({
    "silver": "#d6d8de",
    "katsu": "#d79a3e",
    "katsu_in": "#f3e6d2",
    "sauce": "#5a2f1e",
})
C = mk.City("cine_fork", prop=True)
# 자루 (손 쪽이 넓다)
C.rbox("silver", (0, 0.0, 0), (0.014, 0.075, 0.005), kind="main")
C.rbox("silver", (0, 0.055, 0.002), (0.008, 0.045, 0.004), rot=(8, 0, 0), kind="main")
# 머리 + 갈래
C.rbox("silver", (0, 0.082, 0.006), (0.016, 0.012, 0.004), kind="main")
for i in range(4):
    x = -0.006 + i * 0.004
    C.rbox("silver", (x, 0.1, 0.007), (0.0022, 0.026, 0.0025), kind="detail")
# 꽂은 돈까스 한 조각
C.rbox("katsu", (0, 0.104, 0.012), (0.024, 0.016, 0.02), rot=(0, 12, 0), kind="main")
C.rbox("katsu_in", (0.0125, 0.104, 0.012), (0.002, 0.012, 0.014), rot=(0, 12, 0), kind="fine")
C.rbox("sauce", (0, 0.104, 0.0225), (0.018, 0.01, 0.002), rot=(0, 12, 0), kind="fine")
C.finish("props/cine_fork.glb", root_props={"outline": 0.0012}, detail_outline=0.0006)
