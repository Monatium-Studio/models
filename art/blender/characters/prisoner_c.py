"""무명 엘프 포로 C (남흑색 단발 + 짧은 양 갈래, 붉은 보라 눈). 공용 빌더와 근거: prisoner_common.py, 복장: art/blender/lib/prisoner.py.

npm run model -- art/blender/characters/prisoner_c.py
npm run shot -- characters/prisoner_c.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prisoner_common  # noqa: E402

prisoner_common.build("prisoner_c", "c")
