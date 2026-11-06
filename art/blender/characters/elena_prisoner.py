"""엘레나 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
얼굴·머리·체격은 시장 엘레나(characters/elena.py)와 같다(elena_common.py). 허리 아래까지 오는 긴 생머리가 등의
스텐실을 대부분 덮는다. 수용 번호는 0109 (수용소의 칩을 빼돌려 게이트를 조립한 장본인).
복장: 공용 죄수복 모듈(art/blender/lib/prisoner.py).
쓰는 곳: interlude_escape(칩 숨기기, 게이트 조립), interlude_arrival(세계수를 바라봄).

npm run model -- art/blender/characters/elena_prisoner.py
npm run shot -- characters/elena_prisoner.glb
npm run shot -- characters/elena_prisoner.glb --focus elena_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "characters"))
import cb  # noqa: E402
import elf  # noqa: E402
import elena_common as ec  # noqa: E402
import prisoner as pr  # noqa: E402

cb.reset()
e = elf.Elf("elena_prisoner", **ec.BODY, **ec.TRI)
P = pr.mats("elpr")

ec.face(e)
ec.hair(e)
pr.outfit(e, P, number="0109")

e.finalize()
e.export("characters/elena_prisoner.glb")
