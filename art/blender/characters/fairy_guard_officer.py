"""요정 경비대 지휘관 [오리지널] (남색 단발, 눈이 보이는 얼굴, 금 견장·장식끈·방울 샤코). 공용 빌더와 근거: fairy_guard_common.py, docs/art/fairy-faction.md 4장.

npm run model -- art/blender/characters/fairy_guard_officer.py
npm run shot -- characters/fairy_guard_officer.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fairy_guard_common  # noqa: E402

fairy_guard_common.build("fairy_guard_officer", "officer")
