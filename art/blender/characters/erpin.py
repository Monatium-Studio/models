"""에르핀: 요정 왕국 에르피엔의 여왕. 엘다인으로 각성하기 전의 원작 기본 모습 (침공전 전반부 장면용).

에필로그 대관식의 각성한 모습은 별도 모델 erpin_royal.glb(에르핀(왕도))이다. 두 판의 식별 요소를 섞지 않는다.
근거: docs/art/fairy-faction.md 에르핀 절.
- 식별 요소: 발목까지 오는 연한 꿀빛 금발 생머리 + 캐릭터 왼쪽(+X) 옆 땋은 머리, 왼쪽 크리스털 머리핀,
  가운데 크리스털을 단 금색 티아라형 왕관('애도하는 희망의 왕관'), 붉은 주황 눈 + 노란 별 동공, 덧니,
  붉은 후드 칼라 케이프와 땅까지 오는 붉은 망토(밑단 흰 털 방울), 금 테두리 흰 원피스(가슴 크리스털, 검은 허리끈,
  금테 앞판), 검은 가터, 레이스 윗단의 흰 니삭스, 금띠 흰 부츠, 작은 흰 날개(분홍빛 깃).
- 재해석: 3D SD 비율에 맞춰 망토를 팔 뒤로 둘렀다. 왕관은 별도 노드 erpin_crown(장면에 따라 숨김: 원작에서
  왕관은 시즌 2 끝에 힘을 잃고 침공전 종전 뒤 다시 수여된다). 홀(지팡이)은 넣지 않는다(socket_hand_R).
- 표정: 키트 5종 + grin(덧니 웃음, 원작 카드) + teary(울먹) + pout(뾰로통) + blink 교정 키.

npm run model -- art/blender/characters/erpin.py
npm run shot -- characters/erpin.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, lerp, frame  # noqa: E402

cb.reset()
e = fairy.Fairy("erpin", ears=None, height=1.16, chest=0.28, bust=0.55, hips=1.02, segs=0.72, hand_q=0.55, cheek=0.12)
k = e.k
M_ = elf.mat
white = M_("er_white", "#fbf8f6")
white_d = M_("er_white_d", "#e6dee0")
gold = M_("er_gold", "#ecc069")
gold_d = M_("er_gold_d", "#c9933f")
red = M_("er_red", "#d4434c")
red_d = M_("er_red_d", "#a8323d")
black = M_("er_black", "#3a2f35")
crystal = M_("er_crystal", "#dfe9fb")
crystal_d = M_("er_crystal_d", "#a9bfe6")
fur = M_("er_fur", "#fffaf6")
skin_band = M_("er_lace", "#ffffff")

# ---- 얼굴: 붉은 주황 눈(위쪽 짙은 자줏빛), 노란 별 동공, 덧니, 반쯤 감은 능청스러운 눈매
ec.face(e, eye_color="#e9643f", iris_dark="#5b2840", iris_light="#ffb067", pupil="#7a2a2a",
        lash="#4a2a26", brow="#c79a5a", brow_th=0.9, blush="#f7a3a3", blush_size=1.1, blush_lines=0,
        star=None, star_pupil="#ffd23f", star_pupil_size=1.05, fang=0.40,
        base={"eye": {"top": 0.026, "ktop": 3.4, "cout": 0.017},
              "brow": {"ang": -4.0, "dz": 0.066, "arch": 0.004},
              "mouth": {"w": 0.022, "curve": 0.0045, "open": 0.0035}},
        expr={
            # 덧니 웃음: 원작 카드의 능청스러운 반쯤 감은 눈 + 크게 벌린 입
            "grin": {"eye": {"top": 0.018, "lift": 0.010, "ktop": 4.2, "tilt_in": -0.004},
                     "brow": {"ang": -10.0, "dz": 0.062},
                     "mouth": {"w": 0.038, "curve": 0.0080, "open": 0.0280, "top_arch": 0.0015}},
            # 울먹: 눈썹이 안쪽으로 올라가고 아래 눈꺼풀이 떨리며 입이 물결
            "teary": {"eye": {"top": 0.030, "lift": 0.012, "tilt_in": 0.010, "ktop": 2.6},
                      "iris": {"pupil": 0.85},
                      "brow": {"ang": 22.0, "dz": 0.070, "arch": -0.002},
                      "mouth": {"w": 0.026, "curve": -0.0050, "open": 0.0060, "wave": 0.0020}},
            # 뾰로통: 눈을 가늘게, 입을 삐죽
            "pout": {"eye": {"top": 0.016, "ktop": 4.6, "tilt_in": -0.008},
                     "brow": {"ang": -14.0, "dz": 0.058},
                     "mouth": {"w": 0.016, "curve": -0.0035, "open": 0.0, "top_arch": 0.0020}},
        })

# ---- 머리 (헤어 v2): 발목까지 오는 긴 생머리, 넓은 앞머리, 허벅지까지 오는 옆 커튼, +X 옆 땋은 머리
HAIR, HAIR_D, HAIR_L = "#f6dc98", "#dcb46c", "#fff6dc"
h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.18)
h.cap(front=30, side=-6, back=-46, part=4, segs=18, rows=5)
h.bangs(n=7, spread=52, tip_el=-2, sweep=-6, part=4, jag=0.25, curl=1.2, seed=7.0)
h.sides(length=0.42, width=0.080, az=58, curl=0.4, thick=1.1)
h.back(length=0.66, n=9, spread=96)
h.braid(side=1, az=88.0, el=-18.0, length=0.40, width=0.060, beads=10, tie=gold_d, tuft=0.045)
h.shine(el=50, spread=78, n=2, size=1.25)

# 크리스털 머리핀 (+X, 관자놀이 위)
hp_p, hp_n = h.path(70.0, h.s_of_el(70.0, 18.0), 0.004 * k)


def hairpin(buf):
    Mx = Matrix.Translation(hp_p) @ frame(hp_n, (0, 0, 1)) @ Matrix.Rotation(math.radians(-8), 4, "Y")
    ec.gem(buf, Mx, 0.030 * k, 0.050 * k, crystal, depth=0.006 * k, frame_mat=gold, frame_w=0.004 * k,
           wts={"head": 1.0})


e.part("hairpin", "head", hairpin)


# ---- 왕관: 금색 티아라 (별도 노드 erpin_crown). 머리 덩어리 위에 비스듬히 얹힌 고리 + 앞판 + 크리스털 3개
def crown(buf):
    w = {"head": 1.0}

    def el_fn(az):
        return 44.0 + 18.0 * (1 - math.cos(math.radians(az))) / 2

    n = 28
    base, nrm, ups = [], [], []
    for i in range(n):
        az = 360.0 * i / n
        s = h.s_of_el(az, el_fn(az))
        p, nn = h.path(az, s, 0.002 * k)
        p2, _ = h.path(az, max(s - 0.01 * k, 0.0), 0.002 * k)
        base.append(p)
        nrm.append(nn)
        ups.append((p2 - p).normalized())
    elf._loop(buf, base, nrm, ups, 0.014 * k, 0.005 * k, mat=gold, w=w)
    # 앞판: 사다리꼴로 솟고 가운데가 뾰족
    m = 13
    pts_b, pts_t, nn_ = [], [], []
    for i in range(m):
        u = -1 + 2 * i / (m - 1)
        az = u * 50.0
        s = h.s_of_el(az, el_fn(az))
        p, nn = h.path(az, s, 0.004 * k)
        p2, _ = h.path(az, max(s - 0.02 * k, 0.0), 0.004 * k)
        up = (p2 - p).normalized()
        up = (up * 0.55 + nn * 0.45 + V((0, 0, 0.3))).normalized()
        hgt = (0.050 + 0.030 * max(0.0, 1 - abs(u) * 3.0) - 0.020 * u * u) * k
        pts_b.append(p)
        pts_t.append(p + up * hgt)
        nn_.append(nn)
    th = 0.0045 * k
    ob_ = [buf.vert(p, w) for p in pts_b]
    ot = [buf.vert(p, w) for p in pts_t]
    ib = [buf.vert(p - nn * th, w) for p, nn in zip(pts_b, nn_)]
    it = [buf.vert(p - nn * th, w) for p, nn in zip(pts_t, nn_)]
    for i in range(m - 1):
        buf.face((ob_[i], ob_[i + 1], ot[i + 1], ot[i]), gold)
        buf.face((ib[i], it[i], it[i + 1], ib[i + 1]), gold_d)
        buf.face((ot[i], ot[i + 1], it[i + 1], it[i]), gold)
        buf.face((ob_[i], ib[i], ib[i + 1], ob_[i + 1]), gold)
    buf.face((ob_[0], ot[0], it[0], ib[0]), gold)
    buf.face((ob_[-1], ib[-1], it[-1], ot[-1]), gold)
    # 크리스털 무리 (가운데 큰 것 + 양옆 작은 것)
    c = (pts_b[m // 2] + pts_t[m // 2]) / 2
    nc = nn_[m // 2]
    upc = (pts_t[m // 2] - pts_b[m // 2]).normalized()
    Mc = Matrix.Translation(c + nc * 0.003 * k) @ frame(nc, upc)
    ec.gem(buf, Mc, 0.026 * k, 0.050 * k, crystal, depth=0.007 * k, wts=w)
    for sg in (1, -1):
        Ms = Mc @ Matrix.Translation((sg * 0.024 * k, 0.002 * k, -0.008 * k)) @ Matrix.Rotation(
            math.radians(-sg * 26), 4, "Y")
        ec.gem(buf, Ms, 0.016 * k, 0.032 * k, crystal_d, depth=0.005 * k, wts=w)
    # 옆 뾰족 장식 (오른쪽 뒤)
    for az in (62.0, -62.0):
        s = h.s_of_el(az, el_fn(az))
        p, nn = h.path(az, s, 0.004 * k)
        up = (h.path(az, max(s - 0.02 * k, 0.0), 0.004 * k)[0] - p).normalized()
        Mx = Matrix.Translation(p) @ frame(nn, up)
        fairy.prism(buf, [(-0.008 * k, 0.0), (0.008 * k, 0.0), (0.0, 0.026 * k)], 0.004 * k, Mx, mat=gold, w=w,
                    chamfer=0.0015 * k)


ec.node_part(e, "crown", crown)

# ---- 흰 원피스: 몸판 + 치마(금 밑단) + 금테 앞판 + 가슴 크리스털 + 검은 허리끈
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(white, hem=wz - 0.01 * k, collar="stand", collar_mat=white, flare=0.0)
skirt = fairy.Shell(e, white, wz + 0.004 * k, e.crotch_z - 0.002 * k, off=0.016, th=0.004, skirt=True, cols=20,
                    rows=6, flare=[(0.0, 0.0), (0.5, 0.012), (1.0, 0.032)], cover=True)
skirt.hem_trim(gold, width=0.010, th=0.0025)
ec.shell_panel(skirt, 0.08, 1.12, -20.0, 20.0, white, border=gold, bw=0.008, lift=0.004, rows=5, cols=4)
pc, nc_ = skirt.surface(0.35, 0.0, 0.009 * k)
ec.gem(skirt.buf, Matrix.Translation(pc) @ frame(nc_, (0, 0, 1)), 0.026 * k, 0.034 * k, crystal, depth=0.005 * k,
       frame_mat=gold, frame_w=0.003 * k, wts=fairy.skirt_w(e, pc))
skirt.done("skirt")
e.belt(black, z=wz + 0.004 * k, h=0.010, th=0.004, off=0.018)
# 가슴: 금테 크리스털 + 금 테두리 V선
e.gear("chest_gem", ("torso", cz + 0.030 * k, 0.0, 0.012 * k),
       lambda b, Mx, w: ec.gem(b, Mx, 0.026 * k, 0.034 * k, crystal, depth=0.005 * k, frame_mat=gold,
                               frame_w=0.004 * k, wts=w))
for sg in (1, -1):
    e.strap(gold, [("torso", e.torso_top - 0.006 * k, sg * 26, 0.012 * k), ("torso", cz + 0.050 * k, sg * 16, 0.012 * k),
                   ("torso", cz - 0.010 * k, sg * 8, 0.012 * k), ("torso", wz + 0.012 * k, sg * 6, 0.013 * k)],
            width=0.007, th=0.0022, name=f"dress_trim_{'L' if sg > 0 else 'R'}")
e.sleeves(white, length=0.95, off=0.012, flare=0.012, cuff=(gold, 0.014, 0.004))
for sd in ("L", "R"):
    e.ring(gold, f"arm_{sd}", 0.80, h=0.010, th=0.0035, off=0.016, name=f"sleeve_band_{sd}")

# ---- 다리: 흰 니삭스(레이스 윗단) + 검은 가터 + 금띠 흰 부츠
TOP = 0.40
for sd, sg in (("L", 1), ("R", -1)):
    fairy.leg_tube(e, white, sd, TOP, 0.84, off=0.006, name=f"stocking_{sd}")
    e.ring(skin_band, f"leg_{sd}", TOP + 0.015, h=0.034, th=0.005, off=0.008, name=f"lace_{sd}")
    e.ring(white_d, f"leg_{sd}", TOP + 0.040, h=0.006, th=0.003, off=0.011, name=f"lace_line_{sd}")
    for ang in (-8.0 * sg, 64.0 * sg):
        e.strap(black, [(f"leg_{sd}", 0.02, ang, 0.012 * k), (f"leg_{sd}", TOP - 0.01, ang, 0.012 * k)], width=0.009,
                th=0.0025, name=f"garter_{sd}_{int(abs(ang))}")
e.boots(white, top=0.80, sole=(white_d, 0.014), cuff=gold, off=0.014, toe=0.004)
for sd in ("L", "R"):
    e.ring(gold, f"leg_{sd}", 0.93, h=0.010, th=0.003, off=0.016, name=f"boot_band_{sd}")

# ---- 붉은 후드 칼라 케이프 (어깨) + 땅까지 오는 망토 (팔 뒤) + 밑단 흰 털 방울
capelet = fairy.Shell(e, red, e.torso_top + 0.012 * k, e.shoulder_z - 0.030 * k, gap=[(0.0, 14.0), (1.0, 46.0)],
                      off=0.024, th=0.004, shoulder=1.0, cols=18, rows=4, flare=[(0.0, 0.0), (1.0, 0.030)])
capelet.edge_trim(gold, width=0.006, th=0.002).hem_trim(gold, width=0.006, th=0.002)
capelet.done("capelet")


def hood(buf):
    """뒤로 접힌 후드: 목 뒤에 두툼한 붉은 고리."""
    w = {"chest": 1.0}
    pts = []
    for i in range(11):
        a = math.radians(lerp(-120.0, 120.0, i / 10) + 180.0)
        r = 0.090 * k
        pts.append(V((math.sin(a) * r * 1.15, -math.cos(a) * r * 0.95 + 0.012 * k,
                      e.torso_top + 0.010 * k + 0.018 * k * math.cos((i / 10 - 0.5) * math.pi))))
    P = elf.catmull(pts, 22)
    st = [{"c": q, "rx": 0.026 * k * (0.6 + 0.4 * math.sin(math.pi * i / (len(P) - 1))),
           "ry": 0.020 * k * (0.6 + 0.4 * math.sin(math.pi * i / (len(P) - 1))), "w": w, "ref": (0, 0, 1)}
          for i, q in enumerate(P)]
    elf.loft(buf, st, segs=8, cap0="round", cap1="round", mat=red_d)
    # 금 걸쇠 (목 앞)
    ec.gem(buf, Matrix.Translation(V((0, -0.064 * k, e.torso_top + 0.004 * k))) @ frame((0, -1, 0), (0, 0, 1)),
           0.020 * k, 0.020 * k, gold, depth=0.004 * k, wts=w)


e.part("hood", "body", hood)


def cape_a(a, u):
    g = 30.0
    return lerp(104.0, 256.0, (a - g) / (360.0 - 2 * g))


cape = fairy.Shell(e, red, e.shoulder_z + 0.010 * k, 0.040 * k, gap=30.0, off=0.030, th=0.005, skirt=True,
                   shoulder=1.0, cols=12, rows=11, flare=[(0.0, 0.0), (0.25, 0.020), (1.0, 0.110)], a_fn=cape_a)
cape.edge_trim(red_d, width=0.006, th=0.002)
hem = [cape.surface(1.0, lerp(104.0, 256.0, i / 20), 0.010 * k)[0] for i in range(21)]
ec.bead_tube(cape.buf, hem, 0.015 * k, 0.028 * k, 10, segs=6, n_per=4, mat=fur, wfn=lambda q: fairy.skirt_w(e, q))
cape.done("cape")

# ---- 날개: 작은 흰 날개, 아래 깃은 분홍빛
# 원작 일러: 어깨 뒤에서 위로 말려 오른 작은 큐피드형 날개, 깃 끝이 분홍빛
fairy.wings(e, span=0.56, height=0.40, sweep=0.0, raise_=6.0, prim=3, cov=2, color="#fffbfb", color2="#fbdde7",
            z=e.chest_z + 0.030 * k, style="erpin")

e.finalize()
e.export("characters/erpin.glb")
