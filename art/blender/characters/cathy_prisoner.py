"""캐시 (인터루드 포로 생활 ~ 엘리아스 불시착): 주황 죄수복 차림.

사용자 확정(docs/scenario.md 인터루드 2번): 포로 생활부터 탈출 직후까지 엘프들은 미국 교도소식 주황 죄수복을 입는다.
얼굴·머리는 캐시 공용 함수(cathy_common.py: face, hair, braids, skull_pin, shade)를 그대로 쓴다. 회흑색 머리 + 은회색
브릿지, 바보털, 귀 뒤로 무릎 위까지 늘어지는 양 갈래 땋은 머리(끝으로 갈수록 밝은 회색, 검은 리본), 왼쪽 머리 위
해골 머리핀. 체격 값은 cathy.py와 같다. 수용 번호는 0418 (리타 0417과 같은 날 투항한 바로 다음 번호).
표정: 키트 5종 + freeze, smirk, tease (+ blink 교정 키). 포로 생활 컷의 '인형들기' smirk가 그대로 나온다.
복장: 공용 죄수복 모듈(art/blender/lib/prisoner.py).

npm run model -- art/blender/characters/cathy_prisoner.py
npm run shot -- characters/cathy_prisoner.glb
npm run shot -- characters/cathy_prisoner.glb --focus cathy_prisoner_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "characters"))
import cb  # noqa: E402
import elf  # noqa: E402
import cathy_common as cc  # noqa: E402
import prisoner as pr  # noqa: E402

cb.reset()
e = elf.Elf("cathy_prisoner", segs=0.68, hand_q=0.6, cheek=0.11)
P = pr.mats("capr")

cc.face(e)
h = cc.hair(e, helmet=False)
bs = cc.braids(e, h, end_z=0.30)
cc.skull_pin(e, h, az=56, el=46, size=0.060)
pr.outfit(e, P, number="0418")

e.finalize()
print("[cathy] braid vcol corners:", cc.shade(e, bs))
e.export("characters/cathy_prisoner.glb")
