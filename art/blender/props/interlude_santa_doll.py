"""인터루드 포로 생활 장면의 산타 인형 (props/interlude_santa_doll.glb).

[원작] 지구 포로 시절 엘프들은 산타가 나눠 줄 크리스마스 장난감을 1년 내내 조립·포장했다(엘레나 테마극장,
      나무위키 「엘레나(트릭컬 리바이브)/작중 행적」 2.2.3, 「엘프(트릭컬 리바이브)」 포로 생활).
[오리지널] 디자인: 빨간 원뿔 몸통 + 흰 털 단 + 검은 띠와 금 버클 + 흰 수염 + 고깔모자. 높이 약 0.22 m.
      대본 IL_CAMP_02에서 캐시가 "산타 인형은 왜 한여름에도 만들어?" 하며 들어 보인다(gesture 인형들기).
      세트 안의 인형들은 같은 함수(interlude_kit.santa_doll)로 더 낮은 분할로 깔았다.

원점 = 인형 바닥 가운데, 정면 -Y. grip: 손으로 쥘 때의 점(몸통 가운데).

npm run model -- art/blender/props/interlude_santa_doll.py
npm run shot -- props/interlude_santa_doll.glb --views front,34,side,back
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import interlude_kit as ik  # noqa: E402

L = ik.begin("interlude_santa_doll")
F = ik.Frame((0, 0, 0))
ik.santa_doll(L, F, 0, 0, 0, s=1.0, V=14, kind="main")
# 눈 (검은 단추 두 개) + 볼
import home_weapons as hw  # noqa: E402
for sx in (1, -1):
    L.decal("can_k", hw.circle(0.0065, 8), (sx * 0.016, -0.0405, 0.163), (0, -1, 0.15), lift=0.001)
    L.decal("toy_red", hw.circle(0.006, 8), (sx * 0.026, -0.036, 0.148), (sx * 0.3, -1, 0), lift=0.001)
L.marker("grip", (0, 0, 0.07))
ik.finish(L, "props/interlude_santa_doll.glb", root_props={"outline": 0.0025}, prop=True, detail_outline=0.0015)
