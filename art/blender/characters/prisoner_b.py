"""무명 엘프 포로 B (밀빛 금발 낮은 포니테일, 파란 졸린 눈). 공용 빌더와 근거: prisoner_common.py, 복장: art/blender/lib/prisoner.py.

npm run model -- art/blender/characters/prisoner_b.py
npm run shot -- characters/prisoner_b.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prisoner_common  # noqa: E402

prisoner_common.build("prisoner_b", "b")
