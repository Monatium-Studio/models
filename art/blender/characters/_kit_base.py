"""키트 검증용 기본 엘프: 맨몸에 가까운 단색 바디슈트 (오리지널 무명 인물).

새 인물을 만들 때 출발점으로 복사해서 쓴다. 맨손·맨발, 기본 표정 세트, 짧은 단발.

npm run model -- art/blender/characters/_kit_base.py
npm run shot -- characters/_kit_base.glb
npm run shot -- characters/_kit_base.glb --focus kitbase_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402

cb.reset()
e = elf.Elf("kitbase")

suit = elf.mat("kb_suit", "#7f8aa3")      # 단색 바디슈트 (회청색)
trim = elf.mat("kb_trim", "#5f6880")      # 목·소맷단·발목 테두리

e.face(eye_color="#4f78b0")
h = e.hair("#8a5a44")
h.cap()
h.bangs(n=7)
h.sides(length=0.06)
h.back(length=0.05)
h.shine()

# 몸에 붙는 바디슈트: 옷 셸을 아주 얇게 (off 3mm), 장식 없음
e.shirt(suit, off=0.003, flare=0.0, collar="stand", collar_mat=trim)
e.sleeves(suit, length=0.90, off=0.003, flare=0.0, cuff=(trim, 0.012, 0.003))
e.pants(suit, off=0.003, bag=0.0, blouse=0.0, length=0.86, cuff=(trim, 0.012, 0.003))

e.finalize()
e.export("characters/_kit_base.glb")
