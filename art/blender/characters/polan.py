"""폴랑: 요정 왕국 에르피엔의 경비대장. 침공전에서 에르피엔 함락 직전까지 경비대를 이끌고 방어를 맡았고,
에필로그 대관식에서는 에르핀의 마차 곁을 지킨다(원작 대관식 컷).

원작 폴랑(트릭컬 리바이브)의 외형을 따른다 (근거: docs/art/fairy-faction.md 3장).
- 식별 요소: 흰 긴 생머리 + 왼눈(+X)을 덮는 앞머리 다발, 별(✦) 반짝임이 든 청록 눈과 눈 밑 점, 날카로운 눈매,
  초록 샤코(검은 띠·챙, 금색 구슬 끈·쐐기·나비, 왼쪽 앞의 큰 금색 깃털 장식), 흰 튜닉(세운 깃, 금색 토글 두 줄),
  초록 연미복(금 테두리), 오른 어깨의 초록 망토와 뺨까지 솟은 세운 깃, 금색 견장·장식끈, 흰 바지와 검은 롱부츠
  (윗단 금색 나비 원판), 작은 흰 날개.
- 재해석: 3D SD 비율에 맞춰 망토를 오른쪽 등 뒤로 걸쳐 팔이 앞으로 나오게 했다. 망토 자락의 문양은 원작 백합 문양
  대신 요정 왕국 나비 문장(에르피엔 군기의 나비, lib/erpien_flag.py)을 쓴다. 머스킷은 모델에 넣지 않는다(socket_hand_R, weapons/fairy/).
- 표정: 키트 5종 + shout(지휘 외침, PV "모두 전열을 정비해!") + doting(에르핀 앞에서 풀리는 얼굴) + blink 교정 키.

npm run model -- art/blender/characters/polan.py
npm run shot -- characters/polan.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
from elf import V, Matrix, Buf  # noqa: E402

cb.reset()
e = fairy.Fairy("polan", ears=None, height=1.24, leg=1.05, chest=0.55, bust=0.65, hips=1.08, segs=0.74, hand_q=0.5,
                 cheek=0.10)
k = e.k
P = dict(fairy.GUARD)
P.update({"plume": "#f2cf8a", "plume_d": "#dcab5e"})
M = fairy.mats("po", P)

# ---- 얼굴: 청록 눈 + 별 반짝임, 날카로운 눈매, 굵은 짙은 눈썹, 오른눈(-X) 바깥 아래 점
fairy.face(e, eye_color="#57b4a3", iris_dark="#1d5c5a", iris_light="#c8f1e2", pupil="#1a3d3e",
           lash="#33262d", brow="#4d4049", brow_th=1.25, blush="#f7a9a8", blush_size=1.05,
           star="sparkle", star_size=1.0, mole=(-0.036, -0.030),
           base={"eye": {"top": 0.024, "ktop": 3.8, "tilt_in": -0.006, "cout": 0.018, "bot": 0.052},
                 "brow": {"ang": -10.0, "dz": 0.060, "arch": 0.002},
                 "mouth": {"w": 0.019, "curve": 0.0012}},
           expr={
               # 지휘 외침: 눈썹을 세게 내리고 입을 크게 벌린다 (PV 2:41 "모두 전열을 정비해!")
               "shout": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.012},
                         "brow": {"ang": -20.0, "dz": 0.054, "th": 0.0074},
                         "mouth": {"w": 0.032, "open": 0.028, "curve": 0.0006, "top_arch": 0.006}},
               # 에르핀 앞: 눈꼬리가 풀리고 볼이 올라가며 입이 동그랗게 웃는다
               "doting": {"eye": {"lift": 0.020, "top": 0.026, "tilt_in": 0.004, "kbot": 2.4},
                          "brow": {"ang": 8.0, "dz": 0.068, "arch": 0.006},
                          "mouth": {"w": 0.024, "curve": 0.0060, "open": 0.0060, "top_arch": -0.0005}},
           })

# ---- 머리 (헤어 v2): 흰 긴 생머리, 옆머리는 가슴 앞으로, 뒷머리는 허리까지. 왼눈(+X)을 덮는 큰 다발.
h = fairy.hair(e, "#eeecf3", dark="#c2bdd3", light="#ffffff", volume=1.05)
h.cap(front=26, side=-10, back=-48, part=-16, segs=14, rows=4)
h.bangs(n=6, spread=60, tip_el=-9, sweep=8, part=-18, jag=0.40, seed=4.0)
h.sides(length=0.36, width=0.072, az=62, curl=0.2, thick=1.05)
h.back(length=0.44, n=7)
o = h.off
# 왼눈을 덮는 다발: 가르마 반대쪽 앞머리 위에서 눈을 지나 볼까지
r0 = h.sp(20, 12, o * 1.05)
h.strand([r0, h.sp(25, 0, o * 1.30), h.sp(28, -14, o * 1.35) + V((0, -0.004, 0)) * k,
          h.sp(30, -28, o * 1.05) + V((0, -0.008, 0)) * k],
         0.085 * k, 0.014 * k, n=12, segs=10, taper=[(0, 0.85), (0.2, 1.0), (0.65, 0.85), (1, 0.0)])
# 앞머리 큰 다발 둘 (샤코 챙 아래로 뾰족하게 내려온다: 원작의 굵은 앞머리 다발)
for az, el0, el1, wd in ((-8.0, 16.0, -14.0, 0.072), (-34.0, 14.0, -6.0, 0.056)):
    h.strand([h.sp(az, el0, o * 1.05), h.sp(az - 2, (el0 + el1) / 2, o * 1.28),
              h.sp(az - 4, el1, o * 1.10) + V((0, -0.004, 0)) * k],
             wd * k, 0.013 * k, n=10, segs=8, taper=[(0, 0.9), (0.3, 1.0), (0.7, 0.75), (1, 0.0)])
h.shine(el=46, spread=70, n=2, size=1.1)

# ---- 샤코 (깃털 장식 = 경비대장 표식)
fairy.shako(e, M, plume=(M["plume"], M["plume_d"]), front=21.0)

# ---- 경비대 복장 (대장: 연미복 금 테두리, 소맷단 금줄 2)
fairy.guard_uniform(e, M, rank="captain", coat_trim=M["gold"], cuff_rank=1)
fairy.epaulette(e, "R", M)    # 오른 어깨 (망토 깃 옆, PV·소개 이미지). 왼 어깨는 머리카락에 덮인다
fairy.aiguillette(e, M["gold"], side="R", loops=2)

# ---- 오른 어깨 망토: 어깨 뒤에서 오른쪽 등을 덮고 무릎까지 (팔은 망토 앞으로 나온다)
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z


def cape_a(a, u):
    g = 30.0
    f = (a - g) / (360.0 - 2 * g)
    return elf.lerp(-100.0, -206.0, f)


cape = fairy.Shell(e, M["green"], e.torso_top + 0.006 * k, 0.17 * k, gap=30.0, off=0.040, th=0.005, skirt=True,
                   shoulder=1.0, cols=9, rows=10, flare=[(0.0, 0.0), (0.3, 0.012), (1.0, 0.060)], a_fn=cape_a)
cape.edge_trim(M["gold"], width=0.010, th=0.003).hem_trim(M["gold"], width=0.012, th=0.003)
# 망토 자락 문장 (오른쪽 뒤 아래)
Mx = cape.frame_at(0.86, -150.0, 0.004 * k)
fairy.emblem(cape.buf, Mx, 0.060 * k, M["gold"], depth=0.0025 * k, w=fairy.skirt_w(e, Mx.translation), line=M["gold_d"],
             n=36)
cape.done("cape")


# 뺨까지 솟은 세운 깃 (망토 깃, 오른쪽): 목 뒤를 돌아 오른쪽 앞에서 끝난다
def collar(buf):
    rows, cols = 5, 11
    z0, z1 = e.torso_top - 0.012 * k, e.chin + 0.040 * k
    R = []
    for i in range(rows):
        u = i / (rows - 1)
        z = elf.lerp(z0, z1, u)
        r = (0.070 + 0.085 * u ** 1.3) * k
        row = []
        for j in range(cols):
            a = math.radians(elf.lerp(-22.0, -196.0, j / (cols - 1)))
            x, y = math.sin(a) * r * 1.05, -math.cos(a) * r * 0.95 + 0.010 * k
            row.append(V((x, y, z)))
        R.append(row)
    w = {"chest": 1.0}
    th = 0.005 * k
    o_ = [[buf.vert(p, w) for p in row] for row in R]
    n_ = [[buf.vert(p - V((p.x, p.y - 0.010 * k, 0)).normalized() * th, w) for p in row] for row in R]
    for i in range(rows - 1):
        for j in range(cols - 1):
            buf.face((o_[i][j], o_[i][j + 1], o_[i + 1][j + 1], o_[i + 1][j]), M["green"])
            buf.face((n_[i][j], n_[i + 1][j], n_[i + 1][j + 1], n_[i][j + 1]), M["green_d"])
    for j in range(cols - 1):
        buf.face((o_[-1][j], n_[-1][j], n_[-1][j + 1], o_[-1][j + 1]), M["gold"])
    for i in range(rows - 1):
        for jj, sg in ((0, 1), (cols - 1, -1)):
            f = (o_[i][jj], o_[i + 1][jj], n_[i + 1][jj], n_[i][jj])
            buf.face(f if sg > 0 else tuple(reversed(f)), M["gold"])
    # 윗단 금테
    pts = [R[-1][j] for j in range(cols)]
    nrm = [V((p.x, p.y - 0.010 * k, 0)).normalized() for p in pts]
    elf._loop(buf, [p - V((0, 0, 0.004 * k)) for p in pts], nrm, [V((0, 0, 1))] * cols, 0.008 * k, 0.003 * k,
              mat=M["gold"], w=w, closed=False)


e.part("cape_collar", "body", collar)

# ---- 날개: 흰 깃털 2단 (아래 크림빛)
# 날개: 흰 바탕 + 크림 안쪽, 둥근 깃 셋이 위로 말린 큐피드형 (원작 카드)
fairy.wings(e, span=0.60, height=0.40, sweep=8.0, raise_=14.0, prim=3, cov=2, color=P["wing"], color2=P["wing_d"],
            style="cupid")

e.finalize()
e.export("characters/polan.glb")
