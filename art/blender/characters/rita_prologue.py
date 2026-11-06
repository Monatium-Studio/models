"""리타 (프롤로그, 지구 침공 당일): 엘피니아 군 전투복 차림의 정찰 침투조원.

사용자 확정: 알레트·타이다·레이지의 전투복과 같은 계열이며 _kit_elfinia_soldier의 복장을 따른다.
얼굴·머리는 1막~4막 리타(characters/rita.py)와 같다. 헬멧 아래로 구리빛 앞머리, 왼쪽 긴 가닥, 목덜미 꽁지가 나온다.
아직 특수작전부 이전이라 청록 스카프와 HUD 헤드셋은 없다(엘피니아 통신기만).
1인칭 팔은 art/blender/viewmodels/rita_prologue_fp_arms.py (같은 elfinia_arms 함수).

npm run model -- art/blender/characters/rita_prologue.py
npm run shot -- characters/rita_prologue.glb
npm run shot -- characters/rita_prologue.glb --mode fpbody --pitch -60 --arms viewmodels/rita_prologue_fp_arms.glb --weapon weapons/us/m4a1.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402

cb.reset()
e = elf.Elf("rita_prologue", **sop.RITA_BODY, **sop.RITA_TRI)
EM = sop.elfinia_mats("ritap")

sop.rita_face(e)
sop.rita_hair(e, helmet=True, tail_tie=EM["web_d"])
sop.elfinia_uniform(e, EM, helmet=True, headset_on=True)

e.finalize()
e.export("characters/rita_prologue.glb")
