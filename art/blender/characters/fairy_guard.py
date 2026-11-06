"""요정 경비대 병사 A (갈색 높은 포니테일, 나무위키 경비대 GIF 기준). 공용 빌더와 근거: fairy_guard_common.py, docs/art/fairy-faction.md 4장.

npm run model -- art/blender/characters/fairy_guard.py
npm run shot -- characters/fairy_guard.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fairy_guard_common  # noqa: E402

fairy_guard_common.build("fairy_guard", "a")
