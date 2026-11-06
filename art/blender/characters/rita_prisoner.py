"""리타 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
얼굴·머리는 1막~4막 리타(characters/rita.py)와 같은 함수다(monatium_sop.rita_face, rita_hair). 목덜미 꽁지는
진압반 청록 끈 대신 수용소 고무줄로 묶었다. 복장은 공용 죄수복 모듈(art/blender/lib/prisoner.py)이고 수용 번호는 0417.
쓰는 곳: interlude_camp(철망 앞), interlude_escape(망보기, 탈주), interlude_arrival(주저앉음).

npm run model -- art/blender/characters/rita_prisoner.py
npm run shot -- characters/rita_prisoner.glb
npm run shot -- characters/rita_prisoner.glb --focus rita_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import monatium_sop as sop  # noqa: E402
import prisoner as pr  # noqa: E402

cb.reset()
e = elf.Elf("rita_prisoner", **sop.RITA_BODY, segs=0.86, hand_q=0.8)
P = pr.mats("ritapr")

sop.rita_face(e)
sop.rita_hair(e, tail_tie=elf.mat("ritapr_tie", "#3e363b"))
pr.outfit(e, P, number="0417")

e.finalize()
e.export("characters/rita_prisoner.glb")
