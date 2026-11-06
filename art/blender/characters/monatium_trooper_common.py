"""무명 모나티엄 진압반원 (교주 차원, 아군 단역). 전투 시스템의 'riot' 아군이 쓴다(src/game/combat/kinds.ts).

[오리지널] 원작 인물이 아닌 무명 반원이다. 원작 얼굴을 쓰지 않고, 변형마다 머리색·머리 모양·눈색·헬멧 장식만 바꾼다.
장비 언어는 진압반(reference-notes 6장)과 알레트의 진압 장비(elf_trio_common)를 따른다: 자줏빛 회색 진압 헬멧(앞 챙),
진회색 조끼, 어깨·무릎 보호대, 밝은 회색 상하의, 검은 벨트 + 은색 버클, 군화. 화면에 여럿 나오므로 삼각형을 줄였다
(목표 10~12k). 근거: docs/art/characters-cameo3.md.

    VARIANTS["a"|"b"|"c"]  머리·눈·헬멧 장식
    build(name, variant)   모델 하나를 만들어 내보낸다
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
import elf_trio_common as tc  # noqa: E402
from elf import V, Matrix, band, rbox, disc, lerp  # noqa: E402

VARIANTS = {
    # A: 짙은 갈색 단발, 갈색 눈, 올린 바이저
    "a": dict(hair="#5c4238", hair_d="#3f2c26", hair_l="#85655a", eye="#7a5a44", style="bob", helmet="visor",
              brow_th=1.15, eye_size=1.0, mark="diamond"),
    # B: 흑갈색 낮은 묶음 머리, 청회색 눈, 정수리 통풍구 + 옆 번호 띠
    "b": dict(hair="#2f2a30", hair_d="#1e1b20", hair_l="#4e4752", eye="#5f7f99", style="tail", helmet="vents",
              brow_th=1.0, eye_size=0.96, mark="bars2"),
    # C: 밝은 재빛 금발 짧은 머리, 초록 눈, 올린 바이저 + 헬멧 띠
    "c": dict(hair="#c9ab84", hair_d="#a1825e", hair_l="#e6d2b4", eye="#5a8a6c", style="short", helmet="visor_band",
              brow_th=1.05, eye_size=1.04, mark="chevron"),
}

PAL = {
    "gray": "#a39ca1", "gray_d": "#837c82", "vest": "#625a62", "vest_d": "#4b444c", "pad": "#57505a",
    "helmet": "#5f5963", "helmet_d": "#443f48", "visor": "#8fa6b8", "visor_d": "#5f7586", "boot": "#55505a",
    "boot_d": "#403b44", "mark": "#c9c3cb", "band": "#3c6e8f",
}


def build(name, variant):
    V_ = VARIANTS[variant]
    cb.reset()
    e = elf.Elf(name, height=1.20, segs=0.56, hand_q=0.34, cheek=0.12)
    k = e.k
    M_ = elf.mat
    P = {kk: M_(f"{name}_{kk}", v) for kk, v in PAL.items()}

    # ---- 얼굴: 키트 기본 눈 + 변형별 눈색·크기·눈썹 + 전투 표정 하나
    e.face(eye_color=V_["eye"], lash="#3a2a2c", brow=elf.mix_hex(V_["hair_d"], "#2a2024", 0.5),
           brow_th=V_["brow_th"], eye_size=V_["eye_size"], blush="#f6a6a8",
           base={"eye": {"top": 0.026, "ktop": 3.4}, "brow": {"ang": -6.0, "dz": 0.064},
                 "mouth": {"w": 0.018, "curve": 0.0020}},
           expr={"shout": {"eye": {"top": 0.030, "tilt_in": -0.010},
                           "brow": {"ang": -20.0, "dz": 0.058, "th": 0.0074},
                           "mouth": {"w": 0.030, "curve": 0.0, "open": 0.024, "top_arch": 0.005}}})

    # ---- 머리 (헤어 v2, 헬멧 아래: 성글게)
    h = e.hair(V_["hair"], dark=V_["hair_d"], light=V_["hair_l"], volume=0.82)   # 헬멧 밖으로 비치지 않게 얇게
    h.cap(front=28, side=-10, back=-50, segs=13, rows=4)
    h.bangs(n=5, spread=50, tip_el=-1, seed=3.0 + ord(variant))
    if V_["style"] == "bob":
        h.sides(length=0.07, width=0.074, curl=0.6)
        h.back(length=0.05, n=5)
    elif V_["style"] == "short":
        h.sides(length=0.02, width=0.068, curl=0.4)
        h.back(length=0.015, n=5)
    else:  # 낮은 묶음 머리: 짧은 옆머리 + 목덜미에서 묶은 짧은 꼬리
        h.sides(length=0.04, width=0.070, curl=0.4)
        h.back(length=0.01, n=5)
        h.ponytail(height=-30, length=0.13, width=0.070, clumps=1, lift=0.6, curve=0.5,
                   tie=P["vest_d"])

    # ---- 진압 헬멧: 앞 챙 + 변형 장식
    vents = P["vest_d"] if V_["helmet"] == "vents" else None
    band_mat = P["band"] if V_["helmet"] == "visor_band" else None
    e.helmet(P["helmet"], off=0.040, front=12.0, side=0.0, back=-24.0, rim=P["helmet_d"], strap=P["vest_d"],
             vents=vents, band_mat=band_mat, band_el=58.0)

    # 뒤 테두리 바로 위로 머리카락이 헬멧 밖에 비치지 않게 한 번 더 누른다 (키트 squash는 테두리 근처에서 off×1.2까지 허용)
    def tight_rim(az):
        aa = abs(((az + 180) % 360) - 180)
        front, side, back = 12.0, 0.0, -24.0
        r = front + (side - front) * elf.smoothstep(0, 90, aa) + (back - side) * elf.smoothstep(90, 180, aa)
        return r - 10.0 * elf.smoothstep(70.0, 150.0, aa) + 40.0 * (1.0 - elf.smoothstep(60.0, 100.0, aa))
    e._hats.append((0.030 * k, tight_rim))

    def helmet_bits(buf):
        w = {"head": 1.0}
        # 앞 챙 (알레트와 같은 진압 헬멧 실루엣)
        n = 11
        rows_ = []
        for j in range(n):
            az = lerp(-82.0, 82.0, j / (n - 1))
            p0, _ = e.head_point(az, 13.0, 0.044 * k)
            a = math.radians(az)
            out = V((math.sin(a), -math.cos(a), 0.0))
            f = math.cos(a) ** 0.6
            p1 = p0 + out * (0.028 * k * f + 0.006 * k) + V((0, 0, -0.012 * k * f))
            rows_.append([buf.vert(q, w) for q in (p0 + V((0, 0, 0.010 * k)), p1, p1 + V((0, 0, -0.012 * k)),
                                                    p0 + V((0, 0, -0.010 * k)))])
        for j in range(n - 1):
            for a_ in range(3):
                buf.face((rows_[j][a_], rows_[j + 1][a_], rows_[j + 1][a_ + 1], rows_[j][a_ + 1]),
                         P["helmet"] if a_ == 0 else P["helmet_d"])
        if V_["helmet"] in ("visor", "visor_band"):
            # 올린 바이저: 챙 위 이마 앞을 덮는 반투명 느낌의 청회 판 (불투명 색으로, 드로우콜을 늘리지 않음)
            m_ = 9
            g = []
            for j in range(m_):
                az = lerp(-70.0, 70.0, j / (m_ - 1))
                col = []
                for i, el in enumerate((20.0, 34.0, 46.0)):
                    col.append(buf.vert(e.head_point(az, el, 0.050 * k + 0.004 * k * i)[0], w))
                g.append(col)
            for j in range(m_ - 1):
                for i in range(2):
                    buf.face((g[j][i], g[j + 1][i], g[j + 1][i + 1], g[j][i + 1]), P["visor"])
            for s in (1, -1):         # 바이저 돌쩌귀
                p, nn = e.head_point(s * 76.0, 30.0, 0.050 * k)
                disc(buf, p, nn, (0, 0, 1), 0.010 * k, 0.010 * k, 0.004 * k, segs=8, mat=P["visor_d"], w=w)
        if V_["helmet"] == "vents":
            # 옆 번호 띠 (흰 사각 표식 두 개)
            for s in (1, -1):
                p, nn = e.head_point(s * 100.0, 32.0, 0.042 * k)
                c3.box12(buf, (0.030 * k, 0.003 * k, 0.012 * k), Matrix.Translation(p) @ elf.frame(nn, (0, 0, 1)),
                         P["mark"], w)

    e.part("helmet_bits", "head", helmet_bits)

    # ---- 복장: 밝은 회색 상하의 + 진회색 조끼 + 어깨·무릎 보호대
    cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
    e.shirt(P["gray"], collar="stand", collar_mat=P["gray_d"], flare=0.010)
    e.sleeves(P["gray"], length=0.90, off=0.012, cuff=(P["gray_d"], 0.018, 0.004))
    m = tc.base_gear(e, name[:3], pants=P["gray"], pants_d=P["gray_d"], boots=P["boot"], boots_d=P["boot_d"],
                     glove=P["vest_d"], glove_cuff=P["vest"], belt_z=hz - 0.024 * k)
    vs = c2.Shell(e, P["vest"], e.torso_top - 0.004 * k, hz - 0.004 * k, off=0.024, th=0.007, rows=5, cols=16,
                  flare=[(0.0, 0.0), (1.0, 0.006)])
    vs.hem_trim(P["vest_d"], width=0.010, th=0.003)
    vs.done("vest")
    e.part("vest_collar", "body", lambda buf: band(buf, (0, 0.006 * k, e.torso_top + 0.004 * k), (0, 0, 1), (1, 0, 0),
                                                   0.074 * k, 0.068 * k, 0.030 * k, 0.007 * k, segs=12,
                                                   mat=P["vest"], w={"neck": 0.3, "chest": 0.7}, taper=0.06))
    e.pouch(P["vest_d"], ("torso", cz - 0.004 * k, 0, 0.030 * k), size=(0.054, 0.010, 0.056), name="plate")
    e.patch(P["mark"], ("torso", cz - 0.004 * k, 0, 0.042 * k), size=(0.026, 0.020), shape=V_["mark"],
            name="plate_mark")
    for i, a in enumerate((-36, 36)):
        e.pouch(P["vest_d"], ("torso", wz - 0.010 * k, a, 0.032 * k), size=(0.038, 0.020, 0.042), flap=P["vest"],
                name=f"pouch_{i}")
    for sd, s in (("L", 1), ("R", -1)):
        e.pad(P["pad"], (f"arm_{sd}", 0.10, s * 70, 0.020 * k), size=(0.070, 0.020, 0.066), name=f"sh_pad_{sd}")
        e.pad(P["pad"], (f"leg_{sd}", 0.52, 0, 0.018 * k), size=(0.060, 0.020, 0.056), name=f"knee_pad_{sd}")

    e.finalize()
    e.export(f"characters/{name}.glb")
    return e
