"""무명 모나티엄 진압반원 변형 B ([오리지널] 아군 단역). 공용 빌더와 변형 표: monatium_trooper_common.py.

npm run model -- art/blender/characters/monatium_trooper_b.py
npm run shot -- characters/monatium_trooper_b.glb
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monatium_trooper_common  # noqa: E402

monatium_trooper_common.build("monatium_trooper_b", "b")
