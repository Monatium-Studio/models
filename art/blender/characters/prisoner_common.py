"""무명 엘프 포로 공용 빌더: prisoner_a, prisoner_b, prisoner_c (인터루드 수용소·탈주·불시착의 군중).

[오리지널] 지구 포로수용소에 갇힌 이름 없는 엘프들. 모두 같은 주황 죄수복(art/blender/lib/prisoner.py)을 입고,
얼굴·머리·키만 다르다. 다수가 한 화면에 나오므로 분할을 낮췄다(segs 0.72, hand_q 0.6, 먹선·가슴 스텐실 일부 생략).
- A: 갈색 부스스한 단발, 초록 눈, 바보털 (1146번)
- B: 밀빛 금발 낮은 포니테일, 파란 졸린 눈, 조금 큰 키 (0823번)
- C: 남흑색 단발 + 짧은 양 갈래, 붉은 보라 눈, 일자 눈썹 (1390번)
표정: 키트 표준(blink, serious, surprised, pained, smile + talk, talk_o, look_*) + blink 교정 키.

npm run model -- art/blender/characters/prisoner_a.py   (b, c 같음)
npm run shot -- characters/prisoner_a.glb
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import prisoner as pr  # noqa: E402

VARIANTS = {
    "a": dict(number="1146", height=1.18, cheek=0.11,
              hair=("#7a5040", "#563628", "#b37d60"), eye="#4f8a6c",
              face_base=None),
    "b": dict(number="0823", height=1.22, cheek=0.09,
              hair=("#dcb877", "#ad8a4d", "#f5e3ad"), eye="#4f78b8",
              face_base={"eye": {"top": 0.023, "ktop": 3.7, "tilt_out": -0.003}, "brow": {"ang": 6.0, "dz": 0.066}}),
    "c": dict(number="1390", height=1.19, cheek=0.10,
              hair=("#3c3a52", "#27263a", "#74739a"), eye="#a2506c",
              face_base={"brow": {"ang": -7.0, "arch": 0.0, "th": 0.0068}, "mouth": {"w": 0.019, "curve": 0.0010}}),
}


def _hair(e, variant, hc):
    h = e.hair(hc[0], dark=hc[1], light=hc[2])
    if variant == "a":
        h.cap(front=28, side=-10, back=-50, part=10, segs=18, rows=5)
        h.bangs(n=7, spread=58, tip_el=2, jag=0.45, seed=2.0)
        h.sides(length=0.045, width=0.070, curl=0.5)
        h.back(length=0.035, n=7)
        h.ahoge(az=12, height=0.06, curl=1.2, width=0.016)
        h.shine(el=52, spread=70, n=2, size=1.1)
    elif variant == "b":
        h.cap(front=27, side=-12, back=-50, part=16, segs=18, rows=5)
        h.bangs(n=6, spread=56, tip_el=3, sweep=-10, jag=0.3, seed=5.0)
        h.sides(length=0.07, width=0.060, right=dict(length=0.02, width=0.055))
        h.back(length=0.0, n=5)
        h.ponytail(height=12, length=0.22, width=0.095, clumps=2, lift=0.7, curve=0.6,
                   tie=elf.mat(f"{e.name}_tie", "#3e363b"))
        h.shine(el=52, spread=70, n=2, size=1.1)
    else:
        h.cap(front=30, side=-8, back=-48, part=0, segs=18, rows=5)
        h.bangs(n=8, spread=58, tip_el=-1, jag=0.2, seed=7.0)
        h.sides(length=0.075, width=0.064, curl=0.3)
        h.back(length=0.02, n=7)
        h.twintails(height=16, az=128, length=0.15, width=0.070, clumps=1, lift=0.7, curve=0.4,
                    tie=elf.mat(f"{e.name}_tie", "#3e363b"))
        h.shine(el=52, spread=70, n=2, size=1.1)
    return h


def build(name, variant):
    v = VARIANTS[variant]
    cb.reset()
    e = elf.Elf(name, height=v["height"], cheek=v["cheek"], segs=0.72, hand_q=0.6)
    hc = v["hair"]
    lash = elf.mix_hex(elf.shade(hc[0], -0.6), "#2a1a20", 0.5)
    e.face(eye_color=v["eye"], lash=lash, brow=elf.shade(hc[0], -0.45), base=v["face_base"])
    _hair(e, variant, hc)
    P = pr.mats(f"{name}_p")
    pr.outfit(e, P, number=v["number"], lean=True, seed={"a": 0.0, "b": 1.3, "c": 2.6}[variant])
    e.finalize()
    e.export(f"characters/{name}.glb")
    return e
