"""인터루드 대탈주 장면의 빼돌린 칩 (props/interlude_chip.glb).

[원작] 엘레나는 노역 중 특별한 칩을 빼돌려 차원 게이트를 조립했다(나무위키 「엘프(트릭컬 리바이브)」 탈출,
      「엘레나(트릭컬 리바이브)」).
[오리지널] 디자인: 손바닥만 한 초록 기판에 큰 검은 칩 하나, 금색 핀 줄, 작은 시안 LED, 모서리에 감은 빨간 리본
      (선물 포장 리본으로 묶어 빼돌렸다는 농담). 실존 제조사 표기는 없다. 가로 0.09 m.

원점 = 기판 가운데, 위 +Z. grip: 엄지와 검지로 집는 점.

npm run model -- art/blender/props/interlude_chip.py
npm run shot -- props/interlude_chip.glb --views top,34,side,front
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import interlude_kit as ik  # noqa: E402

L = ik.begin("interlude_chip")
W, D = 0.09, 0.06
L.box("pcb", -W / 2, W / 2, -D / 2, D / 2, 0, 0.004)
# 큰 칩 + 금색 핀
L.box("chip", -0.019, 0.019, -0.016, 0.016, 0.004, 0.009)
for i in range(7):
    x = -0.015 + i * 0.005
    for sy in (-1, 1):
        L.box("copper", x - 0.0012, x + 0.0012, sy * 0.016 - 0.0025 * (sy < 0), sy * 0.016 + 0.0025 * (sy > 0),
              0.004, 0.0055, kind="detail")
L.decal("solder", hw.circle(0.0025, 8), (-0.013, -0.01, 0.009), (0, 0, 1), lift=0.0003)   # 1번 핀 표시
L.text("solder", "E-7", 0.006, (0.004, 0.003, 0.009), (0, 0, 1), lift=0.0003)
# 작은 부품들, 금색 접점 줄
for i, (x, y) in enumerate(((-0.034, 0.018), (-0.03, -0.018), (0.033, 0.017), (0.03, -0.012))):
    L.box("can_k" if i % 2 else "toy_gold", x - 0.003, x + 0.003, y - 0.002, y + 0.002, 0.004, 0.0065,
          kind="detail")
for i in range(8):
    x = -0.038 + i * 0.0105
    L.box("toy_gold", x - 0.003, x + 0.003, -D / 2, -D / 2 + 0.006, 0.0040, 0.0043, kind="fine")
# LED
L.obj("gate", cb.sphere("led", radius=0.0028, loc=(0.036, 0.0, 0.0055), segments=8, rings=5))
# 리본 (모서리에 감은 선물 포장 리본)
L.box("toy_red", 0.024, 0.031, -D / 2 - 0.001, D / 2 + 0.001, -0.001, 0.0052, kind="detail")
L.obj("toy_red", cb.sphere("bow", radius=0.006, loc=(0.0275, D / 2 + 0.004, 0.004), scale=(1.4, 0.7, 0.8),
                           segments=8, rings=4), kind="detail")
L.marker("grip", (-0.03, 0.0, 0.002))
ik.finish(L, "props/interlude_chip.glb", root_props={"outline": 0.0007}, prop=True, detail_outline=0.0004)
