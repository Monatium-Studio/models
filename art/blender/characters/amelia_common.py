"""아멜리아 공용: 교주 차원 아멜리아(amelia.py)와 아멜리아(R41)(amelia_r41.py)가 같이 쓰는 몸·얼굴·머리색.

두 사람은 같은 원형이라 체격, 눈색, 머리색(옅은 분홍빛 베이지 → 끝이 분홍빛 갈색), 가슴까지 오는 넓은 옆머리가
같다. 구분은 머리 모양(단정한 크라운 브레이드 vs 헝클어진 앞머리와 경단), 머리핀(하늘색 초승달 vs 금색 별+초승달),
복장(검은 정장 vs 흰 더블 연구 코트)으로 한다. 근거: docs/art/characters-cameo2.md

체형 (2026-11-02): 성인 비서의 날씬한 체형. 공식 3주년 설정표의 아멜리아(R41) 가슴 '소', 원작 카드·코스튬(흰 드레스,
수영복)에서도 작게 그려진다 → bust 0.30 (두 사람 공통).
올림머리 뒤통수는 두피를 따라 감싸는 넓은 곡면이라 성긴 두개골 메시(segs 0.76)의 면이 툰 3단 그늘에 각지게 비쳤다.
그래서 두개골은 분할 0.9로 만들고(body), 머리카락 셸도 몸보다 촘촘하게 만든다(done_hair).
"""
import math

import elf
import cameo2 as c2
from elf import V, Matrix, Buf, loft, rbox, disc, lerp, smoothstep

HAIR = "#eacbb9"        # 원작 실측 #f0d9cb (정수리). 툰 셰이딩에서 피부와 섞이지 않게 살짝 진하게
HAIR_D = "#c39d8e"
HAIR_L = "#fcefe7"
HAIR_BRAID = "#dcb7a5"  # 땋은 머리·경단 (결이 읽히게 한 단 어둡게)
HAIR_TIP = "#cd8476"    # 옆머리 끝 분홍빛 갈색 (#d39b8a)
HAIR_TIP_D = "#a2625b"
EYE = "#93d487"          # 연두빛 초록 눈


def body(name, **kw):
    """아멜리아 체격: 표준 엘프보다 조금 크고 다리가 길다 (원작 스탠딩 2.8등신, 바지 차림이 길어 보임)."""
    args = dict(height=1.24, head=0.45, leg=1.05, chest=0.30, bust=0.30, hips=1.0, segs=0.76, hand_q=0.6, cheek=0.09)
    args.update(kw)
    # 머리(두개골) 메시는 촘촘한 분할(0.9)로 만든다: 머리카락 셸은 이 메시에 투영되므로, 성기면 올림머리 뒤통수에
    # 다각형 면이 그대로 비친다. 몸·옷은 원래 분할(segs)로 되돌린다.
    q = args.pop("segs")
    e = elf.Elf(name, segs=0.9, **args)
    e.q = q
    return e


def face(e, *, base=None, expr=None, **kw):
    """연두빛 초록 눈, 윗눈꺼풀이 평평하게 홍채 위쪽 3분의 1을 덮는 반쯤 감은 무표정(원작 카드), 옅은 갈색 눈썹."""
    b = {"eye": {"top": 0.0150, "ktop": 5.2, "tilt_out": -0.001},
         "iris": {"cz": 0.0020},
         "brow": {"dz": 0.062, "ang": 2.0, "arch": 0.003, "th": 0.0050, "len": 0.036},
         "mouth": {"w": 0.016, "curve": 0.0002}}
    if base:
        b = elf._merge_expr(b, base)
    args = dict(eye_color=EYE, iris_dark="#3f7e45", iris_light="#e2f7c6", pupil="#1f3a22", lash="#5a3a34",
                brow="#a8806e", blush="#f6a8a4", blush_size=1.05)
    args.update(kw)
    return e.face(base=b, expr=expr, **args)


# 가슴까지 오는 넓은 옆머리 (원작: 귀 앞에서 볼 바깥을 덮으며 곧게 떨어지는 넓적한 커튼, 끝만 살짝 모임).
# 예전 값(width 0.118, n=2)은 가는 끈 두 가닥으로 보였다.
SIDES = dict(length=0.31, width=0.150, az=70, n=1, curl=0.0, thick=1.7, puff=0.8)


def side_lock(h, lk):
    """옆머리 다발: 끝이 둥글게 살짝 모이는 넓적한 끝, 갈라짐은 끝에서만, 끝은 살짝 몸 쪽으로."""
    if lk["region"] == "side":
        lk["p"] = 2.2
        lk["free"] = min(lk["free"], 0.06 * h.k)
        lk["curl"] = -0.004 * h.k


def curtain(h, lk):
    """가운데 가르마 커튼 앞머리 (교주 차원 아멜리아): 앞머리를 양옆으로 매끈하게 쓸고, 가운데 두 다발은 머리선에서
    끝나 이마가 드러나게. 끝은 둥글게(p 2.4) 하고 갈라짐을 짧게 해 들쭉날쭉한 톱니가 생기지 않게."""
    k = h.k
    updo_back(h, lk)
    side_lock(h, lk)
    if lk["region"] != "front":
        return
    ca = (lk["a0"] + lk["a1"]) / 2
    sg = 1 if ca > 0 else -1
    lk["sweep"] = sg * 22.0
    lk["p"] = 2.4
    lk["free"] *= 0.55
    if abs(ca) < 16:
        hl = h.s_of_el(ca, h.hairline(ca))
        lk["L"] = hl + 0.030 * k
        lk["free"] = 0.026 * k


def secretary_hair(e, braid_name):
    """교주 차원 아멜리아의 머리 (amelia.py, amelia_prisoner.py 공용): 가운데 가르마 커튼 앞머리 + 가슴까지 오는
    넓은 옆머리 + 머리를 두르는 크라운 브레이드 + 뒤통수 경단(뒷머리는 올림) + 왼쪽 위 하늘색 초승달 핀."""
    k = e.k
    h = c2.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, lock_fn=c2.lock_edit(curtain), hug_fn=updo_hug, vol_fn=updo_vol)
    h.cap(front=30, side=-8, back=-58, part=0)
    h.bangs(n=6, spread=52, tip_el=5, jag=0.06, seed=1.0)
    h.sides(**SIDES)
    h.back(length=-0.03, n=5)
    h.shine(el=52, spread=64, size=1.0)
    # 크라운 브레이드: 오른쪽 옆 → 이마 위 → 왼쪽 옆 → 뒤통수 경단
    ctrl = [h.path(az, h.s_of_el(az, el), 0.004 * k)[0] for az, el in
            ((-118, 22), (-88, 34), (-50, 52), (0, 63), (50, 52), (88, 34), (118, 24), (150, 26))]
    braid_m = elf.mat(braid_name, HAIR_BRAID)
    c2.braid(h, ctrl, 0.050 * k, 0.042 * k, beads=20, tilt=32, flat=0.62, mat=braid_m)
    braided_bun(h, 170, 24, 0.106, braid_m, beads=12)
    moon_pin(e, h, 58, 50, size=0.052)
    return h


def done_hair(e, q=0.9):
    """머리카락 셸·속층을 몸보다 높은 분할로 지금 만든다 (finalize 전에 부른다). 키트 Hair.done이 e.q를 읽으므로
    잠깐 올렸다가 되돌린다. 몸 분할(segs)과 삼각형 예산은 그대로 둔다."""
    q0 = e.q
    e.q = q
    for h in getattr(e, "_hairs", []):
        h.done()
    e.q = q0


def tip_gradient(e, span, *, x_min=0.09):
    """옆머리·꼬리 끝을 분홍빛 갈색으로 물들인다 (finalize 뒤, 정점색). 머리카락의 가장 낮은 점에서 span(m, e.k 곱함)
    위까지 그라데이션. x_min: 가운데(뒤통수)는 건드리지 않도록 |x| 문턱."""
    k = e.k
    hob = e.result.get("hair")
    zmin = min(v.co.z for v in hob.data.vertices if abs(v.co.x) > x_min * k)
    for node, base, tip in (("hair", HAIR, HAIR_TIP), ("hair_in", HAIR_D, HAIR_TIP_D)):
        ob = e.result.get(node)
        if ob is None:
            continue
        c2.vc_gradient(ob, base, [(zmin + 0.02 * k, tip), (zmin + span * k, base)])


def tablet(e, bone_side="L", *, logo=None, gold=False, name="tablet"):
    """비서 태블릿: 손에 든 짙은 판 + 화면 테 + 초승달 로고. 별도 노드로 손 본에 붙인다."""
    k = e.k
    W = e.W[bone_side]
    d = e.adir[bone_side]
    pn = e.palm_n[bone_side]
    s = 1 if bone_side == "L" else -1
    buf = Buf()
    body_m = elf.mat(f"{e.name}_tab", "#3b3438")
    edge_m = elf.mat(f"{e.name}_tab_e", "#59505a")
    logo_m = logo or elf.mat(f"{e.name}_tab_l", "#7fd6e6")
    c = W + d * 0.040 * k + pn * 0.018 * k + V((0, -0.010 * k, 0))
    up = -d
    nrm = V((s, 0, 0)) * 0.0 + V((0, -1, 0))
    nrm = (nrm - up * nrm.dot(up)).normalized()
    M = Matrix.Translation(c) @ elf.frame(nrm, up)
    rbox(buf, (0.078 * k, 0.010 * k, 0.104 * k), M, mat=body_m, w={}, r=0.18, segs=1)
    rbox(buf, (0.068 * k, 0.004 * k, 0.092 * k), M @ Matrix.Translation((0, -0.004 * k, 0)), mat=edge_m, w={},
         r=0.15, segs=1)
    c2.crescent(buf, M @ Matrix.Translation((0, -0.0065 * k, 0.010 * k)) @ Matrix.Rotation(math.radians(-30), 4, "Y"),
                0.016 * k, width=0.55, th=0.25, a0=60, a1=300, mat=logo_m, n=12, segs=6)
    ob = buf.obj(f"{e.name}_{name}_tmp", angle=40.0)
    return c2.prop(e, name, ob, f"hand_{bone_side}", outline=0.0025)


def moon_pin(e, h, az, el, *, size=0.030, mat=None, star=False, star_mat=None, name="hairpin", tilt=-20.0):
    """초승달 머리핀 (교주 차원: 하늘색) / 별 + 초승달 (R41: 금색). 머리 덩어리 바깥 면에 붙인다."""
    k = e.k
    m = mat or elf.mat(f"{e.name}_pin", "#7fd8ea")

    def fn(buf):
        s_ = h.s_of_el(az, el)
        p, n = h.path(az, s_, 0.004 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
        if star:
            c2.prism(buf, c2.star_poly(size * 0.62 * k, size * 0.27 * k, n=5, rot=90 + 8), 0.008 * k,
                     M @ Matrix.Translation((size * 0.18 * k, 0.002 * k, -size * 0.10 * k)), mat=star_mat or m,
                     w={"head": 1.0}, chamfer=0.003 * k)
            c2.crescent(buf, M @ Matrix.Translation((-size * 0.10 * k, -0.006 * k, size * 0.16 * k)),
                        size * 0.36 * k, width=0.62, th=0.34, a0=50, a1=320, mat=m, w={"head": 1.0}, n=12, segs=6)
            disc(buf, M @ V((-size * 0.10 * k, -0.010 * k, size * 0.16 * k)), n, (0, 0, 1), size * 0.10 * k,
                 size * 0.10 * k, 0.003 * k, segs=10, mat=m, w={"head": 1.0})
        else:
            c2.crescent(buf, M @ Matrix.Translation((0, -0.002 * k, 0)), size * 0.5 * k, width=0.60, th=0.36,
                        a0=55, a1=305, mat=m, w={"head": 1.0}, n=14, segs=8)
    e.part(name, "head", fn)


def updo_back(h, lk):
    """올림머리: 뒷머리 다발 끝을 갈라지지 않게 모아 목덜미에서 안으로 말아 넣는다."""
    if lk["region"] in ("back", "fill") and abs(((lk["a0"] + lk["a1"]) / 2 + 180) % 360 - 180) > 100:
        lk["free"] = 0.012 * h.k
        lk["p"] = 3.0
        lk["curl"] = -0.014 * h.k


def updo_hug(az):
    """올림머리: 옆머리(귀 앞) 바깥의 뒤통수는 두피를 따라 감싼다. 반환값은 감쌀 가장 낮은 높이(도) 또는 None.
    귀 뒤에서는 -36°(귀 아래까지, 맨살 두피가 비치지 않게), 뒤통수 가운데로 갈수록 목덜미(-62°)까지."""
    a = abs(((az + 180) % 360) - 180)
    if a <= 98:
        return None
    return lerp(-36.0, -62.0, smoothstep(104, 160, a))


def updo_vol(az, el):
    """올림머리: 뒤통수 아래쪽 볼륨을 줄여 당겨 묶은 느낌을 낸다."""
    a = abs(((az + 180) % 360) - 180)
    return 1.0 - 0.38 * smoothstep(100, 150, a) * smoothstep(20, -30, el)


def braided_bun(h, az, el, size, mat, *, beads=12):
    """땋은 머리를 감아 올린 경단: 매끈한 경단 + 밑둘레를 두르는 땋은 고리 + 윗면을 가로지르는 땋은 띠."""
    k = h.k
    h.bun(az=az, el=el, size=size)
    s0 = h.s_of_el(az, el)
    base, n = h.path(az, s0)
    c = base + n * size * 0.32 * k
    t1 = n.cross(V((0, 0, 1)))
    t1 = t1.normalized() if t1.length > 1e-6 else V((1, 0, 0))
    t2 = n.cross(t1).normalized()
    r = size * 0.50 * k
    ring = [c - n * size * 0.12 * k + (t1 * math.cos(a) + t2 * math.sin(a)) * r
            for a in [2 * math.pi * i / 12 for i in range(13)]]
    c2.braid(h, ring, 0.034 * k, 0.034 * k, beads=beads, tilt=30, flat=0.6, mat=mat,
             face_fn=lambda q: (q - c))
    arc = [c + (t1 * math.cos(a) + n * math.sin(a) * 0.95) * size * 0.50 * k
           for a in [math.radians(x) for x in (200, 240, 270, 300, 340)]]
    c2.braid(h, arc, 0.030 * k, 0.026 * k, beads=7, tilt=30, flat=0.6, mat=mat, face_fn=lambda q: (q - c))
