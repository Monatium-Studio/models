"""헤어 v2 검증 시트: 긴 생머리 / 단발 / 포니테일 / 트윈테일 4종 (오리지널 무명 인물, 바디슈트).

한 번 실행하면 4개를 내보낸다: characters/_kit_hair_test_{long,bob,pony,twin}.glb
원작 SD 스탠딩과 나란히 비교하는 용도다 (docs/art/reference-notes.md 8장).

npm run model -- art/blender/characters/_kit_hair_test.py
npm run shot -- characters/_kit_hair_test_long.glb --focus hairtest_long_hair --views front,34,side,back
npm run shot -- characters/_kit_hair_test_long.glb --focus hairtest_long_face --views front,34
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402

STYLES = {
    # 이름: (머리색, 눈색, 바디슈트색, 헤어 함수)
    "long": ("#c98a76", "#5f86b8", "#8a93a8",
             lambda h: (h.cap(), h.bangs(n=7, tip_el=2), h.sides(length=0.32, width=0.07),
                        h.back(length=0.46, n=7), h.shine())),
    "bob": ("#6b4636", "#5f8a86", "#7f8aa3",
            lambda h: (h.cap(), h.bangs(n=6, tip_el=6, jag=0.35), h.sides(length=0.03, width=0.075, curl=0.6),
                       h.back(length=0.02, n=7), h.shine())),
    "pony": ("#e2c98f", "#4f9a92", "#7d8c99",
             lambda h: (h.cap(part=18), h.bangs(n=5, tip_el=4, sweep=-10), h.sides(length=0.07, width=0.06, right=dict(length=0.0, width=0.05)),
                        h.back(length=0.0, n=5), h.ponytail(length=0.32), h.ahoge(), h.shine())),
    "twin": ("#3e3a44", "#b0605a", "#8b8296",
             lambda h: (h.cap(), h.bangs(n=7, tip_el=0, jag=0.2), h.sides(length=0.05, width=0.065),
                        h.back(length=0.03, n=7), h.twintails(length=0.30), h.shine())),
}

for style, (hair_c, eye_c, suit_c, fn) in STYLES.items():
    cb.reset()
    e = elf.Elf(f"hairtest_{style}")
    suit = elf.mat(f"ht_{style}_suit", suit_c)
    e.face(eye_color=eye_c, lash=elf.mix_hex(elf.shade(hair_c, -0.6), "#2a1a20", 0.5), brow=elf.shade(hair_c, -0.45))
    fn(e.hair(hair_c))
    e.shirt(suit, off=0.003, flare=0.0, collar="stand")
    e.sleeves(suit, length=0.9, off=0.003, flare=0.0)
    e.pants(suit, off=0.003, bag=0.0, blouse=0.0, length=0.86)
    e.finalize()
    e.export(f"characters/_kit_hair_test_{style}.glb")
