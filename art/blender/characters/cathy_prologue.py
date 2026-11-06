"""캐시 (프롤로그): 지구 침공 당일, 수송선의 정찰 침투조 선임이자 튜토리얼 교관.

원작 인물 캐시(트릭컬 리바이브, 모나티엄 진압반 정찰병)의 얼굴·머리에 엘피니아 군 전투복을 입힌 모델.
- 복장: 사용자 확정에 따라 원작 원피스가 아니라 알레트·타이다·레이지 계열 전투복이다.
  _kit_elfinia_soldier와 같은 함수·같은 색(cameo.elfinia_uniform)을 쓰고, 선임이라 계급장만 막대 3줄이다.
- 식별 요소: 회흑색 머리 + 오른쪽 앞머리의 은회색 브릿지, 귀 뒤로 길게 늘어진 양 갈래 땋은 머리(끝으로 갈수록
  밝은 회색, 검은 리본), 주황빛 붉은 눈, 해골 머리핀(여기서는 헬멧 띠에 꽂은 부적).
- 표정: 키트 5종 + freeze(굳는 표정, 프롤로그 끝) + smirk(능청 웃음) + tease(윙크·메롱) + 각 blink 교정 키.
근거: docs/art/characters-cameo.md, docs/scenario.md 프롤로그

npm run model -- art/blender/characters/cathy_prologue.py
npm run shot -- characters/cathy_prologue.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "characters"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo  # noqa: E402
import cathy_common as cc  # noqa: E402

cb.reset()
e = elf.Elf("cathy_prologue", segs=0.66, hand_q=0.6, cheek=0.11)
k = e.k

cc.face(e)
h = cc.hair(e, helmet=True)
m = cameo.elfinia_uniform(e, "cpr", rank="bars3")
bs = cc.braids(e, h)

# 해골 부적: 헬멧 띠 왼쪽 앞에 꽂았다 (원작 해골 머리핀의 자리 옮김)
bone = elf.mat("cpr_skull", "#f4f0ec")
hole = elf.mat("cpr_skull_d", "#3a3034")
e.gear("skull_charm", ("head", 52, 34, 0.036 * k * 1.12 + 0.006 * k),
       lambda buf, M, w: cameo.skull(buf, M @ elf.Matrix.Rotation(elf.math.radians(-12), 4, "Y"), 0.052 * k, bone,
                                     hole, w=w))

e.finalize()
print("[cathy] braid vcol corners:", cc.shade(e, bs))
e.export("characters/cathy_prologue.glb")
