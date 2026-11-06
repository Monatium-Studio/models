"""요정 경비대 병사 B (붉은 갈색 긴 생머리, PV 2:43~2:55 대열 기준). 공용 빌더와 근거: fairy_guard_common.py, docs/art/fairy-faction.md 4장.

npm run model -- art/blender/characters/fairy_guard_b.py
npm run shot -- characters/fairy_guard_b.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fairy_guard_common  # noqa: E402

fairy_guard_common.build("fairy_guard_b", "b")
