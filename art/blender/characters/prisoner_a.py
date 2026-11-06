"""무명 엘프 포로 A (갈색 부스스한 단발, 초록 눈). 공용 빌더와 근거: prisoner_common.py, 복장: art/blender/lib/prisoner.py.

npm run model -- art/blender/characters/prisoner_a.py
npm run shot -- characters/prisoner_a.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prisoner_common  # noqa: E402

prisoner_common.build("prisoner_a", "a")
