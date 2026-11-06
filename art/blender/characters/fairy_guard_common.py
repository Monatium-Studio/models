"""요정 경비대 공용 빌더: 병사 A(fairy_guard), 병사 B(fairy_guard_b), 지휘관(fairy_guard_officer).

원작: 폴랑 휘하 에르피엔 경비대. 스토리에서 이례적으로 전용 모델(폴랑 스킨 재탕)로 나오고, 테마극장 「여왕님의 마음으로
만든 나라」 PV 2:40~2:55에서 머스킷 일제 사격을 한다. 침공전에서는 에르피엔 방어, 에필로그에서는 대관식 의장대·경비.
- 공통 식별 요소: 초록 샤코(검은 띠·챙, 금색 구슬 끈·쐐기·나비), 흰 튜닉(세운 깃, 금색 토글 두 줄), 초록 연미복,
  흰 바지, 검은 롱부츠(윗단 금색 나비 원판), 흰 장갑, 크림빛 작은 날개, **앞머리로 눈을 가린 얼굴**(원작 단역 표현).
- 변형: 병사 A = 갈색 높은 포니테일(나무위키 경비대 GIF), 병사 B = 붉은 갈색 긴 생머리(PV 2:43~2:55의 대열),
  지휘관 = [오리지널] 남색 단발 + 눈이 보이는 얼굴 + 금 견장·장식끈·소맷단 금줄 2·연미복 금테·샤코 방울·허리 장식띠.
- 샤코·부츠 원판의 나비는 에르피엔 군기와 같은 나비다(lib/erpien_flag.py, 사용자 결정 2026-11-02. fairy.emblem).
- 무기는 넣지 않는다: socket_hand_R + weapons/fairy/fairy_guard_musket.glb.
근거: docs/art/fairy-faction.md 4장.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
from elf import V, Matrix  # noqa: E402

VARIANTS = {
    # 갈색 높은 포니테일 (나무위키 「폴랑」 경비대 GIF)
    "a": dict(hair="#7a5a53", hair_d="#58403d", hair_l="#b08f84", style="pony", mouth=0.0, height=1.22, chest=0.45),
    # 붉은 갈색 긴 생머리 (PV 2:43~2:55 대열)
    "b": dict(hair="#a8474f", hair_d="#7a2f3a", hair_l="#d98a86", style="long", mouth=-0.0015, height=1.23,
              chest=0.42),
    # 지휘관 [오리지널]: 남색 단발, 눈이 보인다
    "officer": dict(hair="#3f4a6e", hair_d="#2b3350", hair_l="#7d8bb4", style="bob", mouth=0.0, height=1.25,
                    chest=0.48),
}


def build(name, variant):
    v = VARIANTS[variant]
    officer = variant == "officer"
    cb.reset()
    e = fairy.Fairy(name, ears="round" if v["style"] == "pony" else None, height=v["height"], leg=1.04,
                    chest=v["chest"], hips=1.05, segs=0.70, hand_q=0.5, cheek=0.10)
    k = e.k
    P = dict(fairy.GUARD)
    P.update({"pom": "#f4f1ec", "pom_d": "#2f6a4f"})
    M = fairy.mats(name[:12], P)

    # ---- 얼굴
    if officer:
        fairy.face(e, eye_color="#c9944a", iris_dark="#6b4320", iris_light="#f6dfa4", pupil="#3a2412",
                   lash="#2a2433", brow="#2f3550", brow_th=1.2, blush="#f6aaa8",
                   base={"eye": {"top": 0.022, "ktop": 4.0, "tilt_in": -0.006, "cout": 0.014},
                         "brow": {"ang": -9.0, "dz": 0.060, "arch": 0.0},
                         "mouth": {"w": 0.018, "curve": 0.0004}},
                   expr={"order": {"eye": {"top": 0.028, "tilt_in": -0.012},
                                   "brow": {"ang": -18.0, "dz": 0.054, "th": 0.0072},
                                   "mouth": {"w": 0.028, "open": 0.022, "curve": 0.0010, "top_arch": 0.005}}})
    else:
        # 원작 단역: 앞머리 그늘에 눈이 가려진다. 입·볼터치만 (표정은 입 위주로 동작)
        fairy.face(e, eyes=False, shade=elf.mix_hex(e.skin_hex, v["hair_d"], 0.22), blush="#f7aba9",
                   base={"mouth": {"w": 0.016, "curve": 0.0010 + v["mouth"]}},
                   expr={"order": {"mouth": {"w": 0.026, "open": 0.020, "curve": 0.0010, "top_arch": 0.005}}})

    # ---- 머리 (헤어 v2)
    h = fairy.hair(e, v["hair"], dark=v["hair_d"], light=v["hair_l"])
    if v["style"] == "pony":
        h.cap(front=26, side=-8, back=-44, part=6, segs=14, rows=4)
        h.bangs(n=6, spread=60, tip_el=-25, jag=0.30, seed=1.0, thick=1.1)
        h.sides(length=0.04, width=0.066, az=64, curl=0.3)
        h.back(length=0.0, n=5)
        # 높은 포니테일: 샤코 뒤 왼쪽 테두리 바로 아래에서 묶어 허리까지 (원작 GIF)
        h._tails.append(lambda: h._tail(138.0, -10.0, length=0.42 * k, width=0.118 * k, droop=0.45, clumps=2,
                                         prefix="hair_tail", tie=M["green_d"], out=1.15))
    elif v["style"] == "long":
        h.cap(front=26, side=-8, back=-46, part=-4, segs=14, rows=4)
        h.bangs(n=6, spread=62, tip_el=-26, jag=0.25, seed=2.5, thick=1.1)
        h.sides(length=0.24, width=0.070, az=62, curl=0.2)
        h.back(length=0.36, n=7)
    else:
        h.cap(front=26, side=-8, back=-46, part=-20, segs=14, rows=4)
        h.bangs(n=6, spread=58, tip_el=-8, sweep=-10, part=-22, jag=0.30, seed=3.0)
        h.sides(length=0.05, width=0.070, az=64, curl=0.6)
        h.back(length=0.02, n=7)

    # ---- 샤코 (지휘관: 금 윗테 + 초록·흰 방울)
    fairy.shako(e, M, pompom=(M["pom"], M["pom_d"]) if officer else None, front=21.0)

    # ---- 복장
    if officer:
        fairy.guard_uniform(e, M, rank="officer", coat_trim=M["gold"], cuff_rank=2)
        fairy.epaulette(e, "L", M)
        fairy.epaulette(e, "R", M)
        fairy.aiguillette(e, M["gold"], side="R", loops=2)
        # 허리 장식띠 (초록 띠 + 왼쪽 허리 매듭과 금술 두 가닥)
        wz = e.waist_z
        e.belt(M["green_d"], z=wz + 0.004 * k, h=0.030, th=0.005, off=0.020)

        def sash_knot(buf, Mx, w):
            fairy.ellipsoid(buf, Mx @ V((0, -0.008 * k, 0)), Mx.to_3x3() @ V((0, 0, 1)), Mx.to_3x3() @ V((1, 0, 0)),
                            Mx.to_3x3() @ V((0, -1, 0)), 0.018 * k, 0.020 * k, 0.010 * k, segs=8, rings=5,
                            mat=M["green_d"], w=w)
            for dx in (-0.010, 0.010):
                p0 = Mx @ V((dx * k, -0.010 * k, -0.012 * k))
                p1 = Mx @ V((dx * 1.6 * k, -0.012 * k, -0.075 * k))
                elf.loft(buf, [{"c": p0, "rx": 0.006 * k, "ry": 0.004 * k, "w": w},
                               {"c": p0.lerp(p1, 0.7), "rx": 0.007 * k, "ry": 0.004 * k, "w": w},
                               {"c": p1, "rx": 0.010 * k, "ry": 0.005 * k, "w": w}],
                         segs=6, cap0="flat", cap1="flat", mat=M["gold"])
        e.gear("sash_knot", ("torso", wz, 62, 0.026 * k), sash_knot)
    else:
        fairy.guard_uniform(e, M, rank="soldier")

    # ---- 날개: 크림빛 작은 깃털 날개, 끝이 바깥으로 (원작 GIF). 2026-11-04 처진 솜뭉치에서 들어 올린 깃 날개로
    # 원작 GIF: 허리 높이 뒤에서 바깥으로 나온 크림빛 작고 둥근 날개 (물결 깃 끝 둘)
    fairy.wings(e, span=0.34, height=0.26, sweep=8.0, raise_=4.0, prim=2, cov=1, color="#e9cd9c",
                color2="#fff3dc", z=e.waist_z + 0.02 * e.k, style="guard")

    e.finalize()
    e.export(f"characters/{name}.glb")
    return e
