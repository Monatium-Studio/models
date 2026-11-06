"""왕디: 디아나(왕년). 털 부락 전사 시절의 디아나가 책에서 실체화한 사슴 수인 엘다인. 엘리아스 침공전에서 교주와 함께
뒤늦게 모나티엄에 합류해 흑뉴아를 막아서고, 그 사이 엘레나가 둠스데이 프로토콜을 가동한다(원작). 1막 M3 둠스데이
시네마틱에서 흑뉴아를 가로막는 장면용 카메오.

원작 디아나(왕년)(트릭컬 리바이브, '왕년의 최강자')의 기본 복장을 따른다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 크림빛 큰 사슴뿔 한 쌍(뿌리에 감은 붕대와 늘어진 끈), 옆으로 뻗은 사슴 귀, 발목까지 오는 풍성한 장밋빛
  갈색 머리(끝이 살구빛으로 밝아짐), 헝클어진 앞머리와 바보털, 오른쪽(-X) 앞으로 늘어진 땋은 머리와 금색 매듭,
  반쯤 감은 나른한 붉은 눈, 송곳니 목걸이, 가슴을 감은 붕대, 복근이 드러난 배, 짙은 회색 털 어깨 망토(금색 사각 장식,
  둥근 금색 문장), 바닥까지 오는 짙은 갈색 망토, 금색 룬 버클 허리띠, 마름모 격자 무늬 앞자락, 붕대 감은 손목·발목,
  맨발, 커다란 도끼.
- 재해석: 도끼는 별도 노드 wangdi_axe(오른손 본, 강체). 날의 엮음 무늬는 돋을새김 띠로 다시 그렸다. 복근은 아웃라인
  없는 옅은 음영 판(별도 노드 wangdi_abs)으로만 표시했다. 땋은 머리 방향은 원작 소개 이미지·피규어 일러스트 기준이다
  (카드 일러스트는 좌우가 뒤집혀 있다). 꼬리는 원작 스탠딩에서 보이지 않아 만들지 않았다.
- 표정: 키트 5종 + roar(전투 함성) + bored(귀찮음) + smirk(한쪽 입꼬리) + blink 교정 키.

npm run model -- art/blender/characters/wangdi.py
npm run shot -- characters/wangdi.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame, keys  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("wangdi", height=1.25, head=0.45, leg=1.04, chest=0.55, bust=0.75, shoulders=1.08, hips=1.04, limb=1.06,
            segs=0.64, hand_q=0.55, cheek=0.10, ear_len=0.092, ear_width=0.056, ear_angle=-6.0, ear_sweep=8.0)
k = e.k

# ---- 팔레트 (원작 카드 실측: 머리 #b77a6e → 끝 #e8b088, 뿔 #ece0cc, 털 망토 #4f4a4c, 망토 #6b5852, 붕대 #cdbfb0)
fur = M_("wd_fur", "#4f4a4e")
fur_d = M_("wd_fur_d", "#3a3639")
cape_m = M_("wd_cape", "#6b5752")
cape_d = M_("wd_cape_d", "#4f403d")
bandage = M_("wd_bandage", "#d6c8ba")
bandage_d = M_("wd_bandage_d", "#a8988a")
check = M_("wd_check", "#7d716c")
check_d = M_("wd_check_d", "#585050")
gold = M_("wd_gold", "#e0b04c")
gold_d = M_("wd_gold_d", "#b07f2a")
leather = M_("wd_leather", "#4a3a34")
antler = M_("wd_antler", "#eee3d0")
antler_d = M_("wd_antler_d", "#c9b296")
bone = M_("wd_bone", "#efdcb8")
steel = M_("wd_steel", "#b9bcc4")
steel_d = M_("wd_steel_d", "#5d606b")
wood = M_("wd_wood", "#6e5446")
abs_m = M_("wd_abs", "#f1cfc6")

# ---- 얼굴: 붉은 눈, 무겁게 내려온 나른한 눈꺼풀, 짙은 속눈썹, 기본은 살짝 웃는 입
e.face(eye_color="#d6343c", iris_dark="#6e1820", iris_light="#ff9c78", pupil="#3a0a10",
       lash="#4a2228", brow="#8e5a52", brow_th=1.05, blush="#f4a2a0", blush_size=1.08, blush_lines=2,
       base={"eye": {"top": 0.016, "ktop": 5.0, "tilt_out": -0.003, "cout": 0.013, "bot": 0.050},
             "iris": {"cz": 0.0010, "ry": 0.0380},
             "brow": {"dz": 0.062, "ang": 4.0, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0035}},
       expr={
           # 전투 함성: 눈을 크게 뜨고 눈썹을 세게 내리며 입을 크게 벌린다 (흑뉴아를 막아서는 장면)
           "roar": {"eye": {"top": 0.030, "ktop": 3.0, "tilt_in": -0.014},
                    "iris": {"pupil": 0.70},
                    "brow": {"ang": -22.0, "dz": 0.054, "th": 0.0076},
                    "mouth": {"w": 0.040, "open": 0.040, "curve": -0.0010, "top_arch": 0.008}},
           # 귀찮음: 거의 감긴 눈, 처진 눈썹, 일자 입
           "bored": {"eye": {"top": 0.008, "ktop": 6.0, "lift": 0.004},
                     "brow": {"ang": 8.0, "dz": 0.060},
                     "mouth": {"w": 0.016, "curve": -0.0008}},
       })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.014, "lift": 0.008}, "mouth": {"w": 0.026, "curve": 0.0030}},
             L={"brow": {"dz": 0.066, "ang": 2.0, "arch": 0.004}}, R={"brow": {"dz": 0.058, "ang": -10.0}},
             corner=(-0.0010, 0.0090), mouth_dx=-0.0025 * k)

# ---- 머리 (헤어 v2): 풍성한 긴 머리, 헝클어진 앞머리, 바보털, 오른쪽(-X) 땋은 머리
HAIR, HAIR_D, HAIR_L = "#b9786c", "#8a4f4c", "#cd8d7e"
HAIR_TIP, HAIR_TIP_D = "#eab48a", "#c58a68"


def wd_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.2
        lk["free"] *= 0.75
    elif lk["region"] in ("side", "back"):
        lk["p"] = 1.8
        lk["curl"] = lk.get("curl", 0.0) + 0.022 * k     # 끝이 바깥으로 뻗친다 (풍성한 갈기)
        lk["free"] *= 0.65


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.24, lock_fn=fairy.lock_edit(wd_locks))
h.cap(front=28, side=-6, back=-46, part=-8, segs=14, rows=5)
h.bangs(n=7, spread=60, tip_el=-8, sweep=6, part=-8, jag=0.45, curl=1.2, seed=11.0)
h.sides(length=0.36, width=0.090, az=62, curl=0.5, thick=1.30, puff=1.3)
h.back(length=0.62, n=9, spread=112, thick=1.15)
h.braid(side=-1, az=84.0, el=-12.0, length=0.30, width=0.044, beads=9, tie=gold, tuft=0.034)
h.ahoge(az=-6, height=0.070, curl=1.2, width=0.018)
h.shine(el=44, spread=0, n=1, size=0.9)
o = h.off
# 눈 사이로 내려오는 앞머리 한 가닥 (원작의 헝클어진 앞머리)
h.strand([h.sp(-4, 26, o * 1.0), h.sp(-2, 12, o * 1.30), h.sp(2, -2, o * 1.25) + V((0, -0.004 * k, 0)),
          h.sp(4, -14, o * 1.0) + V((0, -0.006 * k, 0))],
         0.030 * k, 0.010 * k, n=10, segs=8, taper=[(0, 0.8), (0.3, 1.0), (0.7, 0.8), (1, 0.0)])


# ---- 사슴뿔 한 쌍: 뿌리에 붕대 + 늘어진 끈. 위·바깥으로 휘는 줄기에 가지 셋
def antler_geo(buf, s):
    w = {"head": 1.0}
    root = h.sp(s * 40.0, 50.0, o * 0.3)
    out = V((s * 1.0, 0.05, 0.0)).normalized()
    up = V((0, 0, 1))
    beam = [root - (root - e.head_c).normalized() * 0.010 * k, root + out * 0.040 * k + up * 0.040 * k,
            root + out * 0.085 * k + up * 0.090 * k + V((0, 0.012 * k, 0)),
            root + out * 0.112 * k + up * 0.170 * k + V((0, 0.020 * k, 0)),
            root + out * 0.098 * k + up * 0.255 * k + V((0, 0.024 * k, 0))]
    P = elf.catmull([V(p) for p in beam], 16)
    st = []
    for i, q in enumerate(P):
        t = i / (len(P) - 1)
        r = lerp(0.023, 0.006, t ** 0.9) * k
        st.append({"c": q, "rx": r, "ry": r * 0.92, "w": w})
    loft(buf, st, segs=7, cap0="flat", cap1="round", mat=antler)

    def at(t):
        i = min(int(t * (len(P) - 1)), len(P) - 2)
        return P[i], (P[i + 1] - P[i]).normalized()
    # 가지: 줄기에서 바깥·위로 (앞쪽 하나, 안쪽 둘)
    for t, d, ln in ((0.30, (s * 0.9, -0.35, 0.55), 0.080), (0.55, (-s * 0.35, -0.10, 1.0), 0.090),
                     (0.76, (s * 0.85, 0.10, 0.75), 0.068)):
        c, T = at(t)
        d = V(d).normalized()
        r0 = lerp(0.023, 0.006, t ** 0.9) * k * 0.80
        tip = c + d * ln * k + V((0, 0, 0.020 * k))
        mid = c.lerp(tip, 0.5) + V((0, 0, 0.010 * k))
        Q = elf.catmull([c, mid, tip], 7)
        loft(buf, [{"c": q, "rx": lerp(r0, 0.0035 * k, i / (len(Q) - 1)), "ry": lerp(r0, 0.0035 * k, i / (len(Q) - 1)),
                    "w": w} for i, q in enumerate(Q)], segs=5, cap0="flat", cap1="round", mat=antler)
    # 뿌리 붕대 두 겹 + 늘어진 끈
    for t in (0.08, 0.15):
        c, T = at(t)
        r = lerp(0.023, 0.006, t ** 0.9) * k
        band(buf, c, T, V((0, -1, 0)), r * 1.25, r * 1.25, 0.012 * k, 0.003 * k, segs=10, mat=bandage, w=w)
    c, T = at(0.11)
    for j, (dx, ln) in enumerate(((0.004, 0.070), (-0.004, 0.050))):
        a = c + out * (0.016 * k) + V((0, -0.004 * k, 0))
        pts = [a, a + V((s * 0.010 * k + dx * k, -0.004 * k, -ln * 0.5 * k)), a + V((s * 0.012 * k + dx * k, 0, -ln * k))]
        Q = elf.catmull(pts, 6)
        loft(buf, [{"c": q, "rx": 0.0045 * k, "ry": 0.0012 * k, "w": w, "ref": (1, 0, 0)} for q in Q], segs=4,
             cap0="flat", cap1="flat", mat=bandage_d, p=1.0)


for s in (1, -1):
    e.part(f"antler_{'L' if s > 0 else 'R'}", "head", lambda buf, s=s: antler_geo(buf, s))


# ---- 귀걸이: 양쪽 귀 아래 금색 룬 모양
def earring(buf, side):
    w = {"head": 1.0}
    eb, et = e._ear_axis(side)
    hook = eb.lerp(et, 0.30) + V((0, -0.003 * k, -0.010 * k))
    loft(buf, [{"c": hook, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w},
               {"c": hook + V((0, 0, -0.014 * k)), "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w}], segs=5,
         cap0="round", cap1="round", mat=gold)
    Mx = Matrix.Translation(hook + V((0, 0, -0.028 * k))) @ frame(V((0, -1, 0)), (0, 0, 1))
    fairy.prism(buf, [(-0.007 * k, -0.012 * k), (0.0, -0.002 * k), (0.007 * k, -0.012 * k), (0.008 * k, 0.004 * k),
                      (0.0, 0.012 * k), (-0.008 * k, 0.004 * k)], 0.003 * k, Mx, mat=gold, w=w, chamfer=0.0008 * k)


for sd in ("L", "R"):
    e.part(f"earring_{sd}", "head", lambda buf, sd=sd: earring(buf, sd))

# ---- 몸통: 가슴 붕대 + 복근 음영 + 송곳니 목걸이
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
wrap = c2.Shell(e, bandage, e.torso_top - 0.048 * k, cz - 0.016 * k, off=0.008, th=0.004, cols=20, rows=4, cover=True,
                bust_drape=0.004)   # 가슴 붕대: 천처럼 늘어지지 않고 밴드처럼 볼륨에 붙는다
wrap.done("chest_wrap")
for i, (z, tl) in enumerate(((cz + 0.030 * k, 0.10), (cz - 0.002 * k, -0.08))):
    def wrap_line(buf, z=z, tl=tl):
        pts, nrm, ups = [], [], []
        for j in range(17):
            a = 360.0 * j / 16
            zz = z + tl * 0.10 * k * math.sin(math.radians(a))
            p, n = e.torso_point(zz, a, 0.004 * k)    # 붕대 층(bust_drape 0.004)과 같은 볼륨 모양에서
            p = p + n * 0.0085 * k                      # 붕대 바깥 면 위로
            pts.append(p)
            nrm.append(n)
            ups.append(V((0, 0, 1)))
        elf._loop(buf, pts, nrm, ups, 0.004 * k, 0.0015 * k, mat=bandage_d,
                  w=lambda t: e._torso_wfn(pts[min(int(t * 16), 16)], 0), closed=False)
    e.part(f"wrap_line_{i}", "body", wrap_line)


def abs_marks():
    b = Buf()
    strokes = []
    zc = (wz + cz) / 2 - 0.006 * k
    # 가운데 세로선 + 좌우 가로선 두 줄 (옅은 음영)
    strokes.append([(0.0, zc + 0.034 * k, 0.0025), (0.0, zc - 0.040 * k, 0.0025)])
    for dz in (0.012, -0.014):
        for sg in (1, -1):
            strokes.append([(sg * 6.0, zc + dz * k, 0.0022), (sg * 26.0, zc + dz * k - 0.003 * k, 0.0016)])
    for (a0, z0, w0), (a1, z1, w1) in [(st[0], st[1]) for st in strokes]:
        pts, nrm, ups, wds = [], [], [], []
        for j in range(6):
            t = j / 5
            a, z = lerp(a0, a1, t), lerp(z0, z1, t)
            p, n = e.torso_point(z, a, 0.0012 * k)
            pts.append(p)
            nrm.append(n)
            wds.append(lerp(w0, w1, t) * k * (0.4 + 0.6 * math.sin(math.pi * (0.1 + 0.8 * t))))
        for j in range(6):
            tan = pts[min(j + 1, 5)] - pts[max(j - 1, 0)]
            ups.append(nrm[j].cross(tan).normalized())
        fairy.taper_strip(b, pts, nrm, ups, wds, 0.0004 * k, mat=abs_m, w=lambda t, p=pts: e._torso_wfn(p[2], 0))
    ob = b.obj("wangdi_abs_geo", smooth=False)
    e.add(ob, group="body", tag="abs", node="abs", props={"noOutline": 1})


abs_marks()


def necklace(buf):
    zc = e.torso_top - 0.004 * k
    pts, nrm, ups = [], [], []
    for j in range(13):
        a = lerp(-70.0, 70.0, j / 12)
        p, n = e.torso_point(zc - 0.010 * k * math.cos(math.radians(a)) ** 2, a, 0.010 * k)
        pts.append(p)
        nrm.append(n)
        ups.append(V((0, 0, 1)))
    elf._loop(buf, pts, nrm, ups, 0.004 * k, 0.003 * k, mat=leather,
              w=lambda t: e._torso_wfn(pts[min(int(t * 12), 12)], 0), closed=False)
    for i, a in enumerate((-36, -18, 0, 18, 36)):
        p, n = e.torso_point(zc - 0.010 * k * math.cos(math.radians(a)) ** 2 - 0.004 * k, a, 0.013 * k)
        w = e._torso_wfn(p, 0)
        ln = (0.024 if a == 0 else 0.017) * k
        loft(buf, [{"c": p, "rx": 0.0050 * k, "ry": 0.0032 * k, "w": w, "ref": tuple(n)},
                   {"c": p + V((0, 0, -ln * 0.5)) + n * 0.002 * k, "rx": 0.0044 * k, "ry": 0.0028 * k, "w": w,
                    "ref": tuple(n)},
                   {"c": p + V((0, 0, -ln)) + n * 0.003 * k, "rx": 0.0004 * k, "ry": 0.0004 * k, "w": w,
                    "ref": tuple(n)}], segs=5, cap0="flat", cap1="flat", mat=bone)
        if i in (1, 3):
            c2.ellipsoid(buf, p + n * 0.003 * k + V((0, 0, 0.002 * k)), V((0, 0, 1)), V((1, 0, 0)), n, 0.0035 * k,
                         0.0035 * k, 0.0035 * k, segs=6, rings=4, mat=gold, w=w)


e.part("necklace", "body", necklace)

# ---- 하의: 붕대 감은 짧은 속바지 + 허리띠(금색 룬 버클) + 마름모 격자 앞자락
q0 = e.q
e.q = 0.42
e.pants(bandage, length=0.12, bag=0.0, off=0.004)
e.q = q0
e.belt(leather, z=wz - 0.004 * k, h=0.020, th=0.005, off=0.014)


def rune_buckle(buf, Mx, w):
    # 룬(ᛟ 모양): 위 마름모 고리 + 아래로 벌어진 두 다리
    th = 0.0045 * k
    fairy.prism(buf, c2.diamond_poly(0.030 * k, 0.026 * k, 0.0, 0.006 * k), th, Mx, mat=gold, w=w,
                chamfer=0.0012 * k)
    fairy.prism(buf, c2.diamond_poly(0.016 * k, 0.012 * k, 0.0, 0.006 * k), th * 1.3, Mx, mat=leather, w=w)
    for sg in (1, -1):
        fairy.prism(buf, [(sg * 0.002 * k, -0.004 * k), (sg * 0.008 * k, -0.002 * k), (sg * 0.016 * k, -0.018 * k),
                          (sg * 0.010 * k, -0.020 * k)] if sg > 0 else
                    [(sg * 0.002 * k, -0.004 * k), (sg * 0.010 * k, -0.020 * k), (sg * 0.016 * k, -0.018 * k),
                     (sg * 0.008 * k, -0.002 * k)], th, Mx, mat=gold, w=w, chamfer=0.0010 * k)


e.gear("rune_buckle", ("torso", wz - 0.002 * k, 0.0, 0.019 * k), rune_buckle)

apron = c2.Shell(e, check, wz - 0.010 * k, 0.140 * k, gap=150.0, back_only=True, off=0.022, th=0.004, skirt=True,
                 cols=7, rows=6, flare=[(0.0, 0.0), (0.4, 0.010), (1.0, 0.020)])
apron.hem_trim(check_d, width=0.010, th=0.0025)
for i in range(7):
    for j in range(-2, 3):
        u = 0.07 + 0.135 * i
        a = 13.0 * j + (6.5 if i % 2 else 0.0)
        if abs(a) > 20.0:
            continue
        Mx = apron.frame_at(u, a, 0.0015 * k)
        fairy.prism(apron.buf, c2.diamond_poly(0.028 * k, 0.040 * k), 0.0016 * k, Mx, mat=check_d,
                    w=c2.skirt_w(e, Mx.translation))
apron.done("apron")

# ---- 다리·팔: 붕대 (정강이~발목, 손목), 맨발
for sd in ("L", "R"):
    c2.leg_tube(e, bandage, sd, 0.74, 0.97, off=0.006, name=f"legwrap_{sd}")
    for t in (0.86,):
        e.ring(bandage_d, f"leg_{sd}", t, h=0.004, th=0.002, off=0.011, name=f"legwrap_line_{sd}{t}")
    c2.arm_tube(e, bandage, sd, 0.80, 0.97, off=0.005, name=f"wristwrap_{sd}")
    e.ring(bandage_d, f"arm_{sd}", 0.88, h=0.004, th=0.002, off=0.010, name=f"wristwrap_line_{sd}")

# ---- 짙은 회색 털 어깨 망토: 어깨를 두르는 털 깃 + 위팔을 덮는 털 소매 (금색 사각 장식, 오른 소매 둥근 금색 문장)
collar = c2.Shell(e, fur, e.torso_top + 0.012 * k, e.shoulder_z - 0.012 * k, gap=[(0.0, 30.0), (1.0, 40.0)],
                  off=0.026, th=0.006, shoulder=1.12, cols=18, rows=3, flare=[(0.0, 0.0), (1.0, 0.020)])
hem = [collar.surface(1.0, lerp(34.0, 326.0, i / 16), 0.006 * k)[0] for i in range(17)]
ec.bead_tube(collar.buf, hem, 0.011 * k, 0.018 * k, 9, segs=6, n_per=3, mat=fur_d, wfn=lambda q: e._torso_wfn(q, 0))
collar.done("fur_collar")
for sd in ("L", "R"):
    c2.arm_tube(e, fur, sd, 0.0, 0.44, off=0.020, extra=lambda t: 0.012 * math.sin(math.pi * min(t / 0.44, 1.0)) ** 0.7,
                name=f"fur_sleeve_{sd}")
    e.ring(fur_d, f"arm_{sd}", 0.43, h=0.014, th=0.005, off=0.024, name=f"fur_sleeve_hem_{sd}")
    for t, ang in ((0.18, 70.0), (0.18, -70.0)):
        a_ = ang if sd == "L" else -ang
        e.gear(f"sleeve_stud_{sd}{t}{ang}", (f"arm_{sd}", t, a_, 0.036 * k),
               lambda b, Mx, w: ec.gem(b, Mx, 0.018 * k, 0.018 * k, gold, depth=0.003 * k, frame_mat=gold_d,
                                       frame_w=0.002 * k, wts=w))


def emblem(b, Mx, w):
    disc(b, Mx.translation, Mx.to_3x3() @ V((0, -1, 0)), Mx.to_3x3() @ V((0, 0, 1)), 0.026 * k, 0.026 * k, 0.003 * k,
         segs=14, mat=fur_d, w=w)
    loft(b, [{"c": Mx @ V((0.020 * k * math.cos(2 * math.pi * i / 14), -0.0035 * k,
                           0.020 * k * math.sin(2 * math.pi * i / 14))), "rx": 0.0022 * k, "ry": 0.0022 * k, "w": w}
             for i in range(15)], segs=5, cap0="flat", cap1="flat", mat=gold)
    fairy.prism(b, [(-0.003 * k, -0.014 * k), (0.003 * k, -0.014 * k), (0.003 * k, 0.014 * k), (-0.003 * k, 0.014 * k)],
                0.004 * k, Mx, mat=gold, w=w)


e.gear("sleeve_emblem", ("arm_R", 0.24, -90.0, 0.038 * k), emblem)

# ---- 바닥까지 오는 짙은 갈색 망토 (어깨 뒤, 팔 뒤)


def cape_a(a, u):
    return lerp(100.0, 260.0, (a - 30.0) / 300.0)


cape = c2.Shell(e, cape_m, e.shoulder_z + 0.006 * k, 0.020 * k, gap=30.0, off=0.040, th=0.005, skirt=True,
                shoulder=1.05, cols=12, rows=10, flare=[(0.0, 0.0), (0.25, 0.024), (1.0, 0.100)], a_fn=cape_a,
                ruffle=(0.010, 9, 0.6))
cape.edge_trim(cape_d, width=0.008, th=0.002)
cape.hem_trim(cape_d, width=0.012, th=0.002)
cape.done("cape")

# ---- 도끼 (별도 노드 wangdi_axe, 오른손 본 강체): 긴 자루 + 큰 외날 (엮음 무늬 돋을새김, 밝은 날 끝)
grip = e._grip_point("R")
AX = V((-0.06, 0.02, 1.0)).normalized()
OUT = V((-1.0, 0.0, 0.0))
OUT = (OUT - AX * OUT.dot(AX)).normalized()          # 날이 바깥(-X)을 향한다
FW = AX.cross(OUT).normalized()                       # 날 면의 법선


def ap(u, x=0.0, y=0.0):
    return grip + AX * (u * k) + OUT * (x * k) + FW * (y * k)


axe = Buf()
loft(axe, [{"c": ap(u), "rx": 0.0135 * k, "ry": 0.0135 * k, "w": {}} for u in (-0.30, 0.0, 0.72)], segs=8,
     cap0="round", cap1="flat", mat=wood)
for u in (-0.05, 0.0, 0.05, 0.10):     # 손잡이 붕대 감기
    band(axe, ap(u), AX, OUT, 0.0150 * k, 0.0150 * k, 0.016 * k, 0.0025 * k, segs=8, mat=bandage)
UC = 0.52                               # 날 가운데 높이 (손잡이에서)
BS = 1.40                               # 날 크기 배율 (원작은 머리보다 큰 날)
Mb = Matrix((OUT, FW, AX)).transposed().to_4x4()   # 오른손 좌표계 (면이 바깥을 본다)


def blade_prism(poly, depth, mat, lift=0.0):
    """날 면 양쪽에 같은 판 (X: 바깥, Z: 자루 방향, 두께는 FW 양쪽). 날 좌표는 UC 기준으로 BS배."""
    for sg in (1, -1):
        M2 = Mb @ (Matrix.Rotation(math.pi, 4, "Z") if sg < 0 else Matrix.Identity(4))
        M2.translation = grip - FW * (sg * lift * k)      # 로컬 -Y(바깥) 쪽으로 띄운다
        pts = [((x * BS if sg > 0 else -x * BS) * k, (UC + (z - UC) * BS) * k) for x, z in poly]
        fairy.prism(axe, pts, depth * k, M2, mat=mat, chamfer=depth * 0.3 * k)


# 날 몸통: 자루 쪽 목은 좁고, 바깥으로 넓어져 둥근 날 끝
body = [(0.00, UC - 0.050), (0.08, UC - 0.070), (0.17, UC - 0.125), (0.21, UC - 0.120), (0.225, UC - 0.06),
        (0.230, UC), (0.225, UC + 0.06), (0.21, UC + 0.120), (0.17, UC + 0.125), (0.08, UC + 0.070), (0.00, UC + 0.050)]
blade_prism(body, 0.007, steel_d)
# 날 끝 밝은 띠
edge = [(0.195, UC - 0.118), (0.21, UC - 0.120), (0.225, UC - 0.06), (0.230, UC), (0.225, UC + 0.06), (0.21, UC + 0.120),
        (0.195, UC + 0.118), (0.208, UC + 0.06), (0.212, UC), (0.208, UC - 0.06)]
blade_prism(edge, 0.0035, steel, lift=0.004)
# 엮음 무늬: 두 방향 대각선 금빛 띠
for i in range(3):
    c = 0.05 + 0.050 * i
    for sg in (1, -1):
        poly = [(c - 0.030, UC - sg * 0.055), (c - 0.018, UC - sg * 0.055), (c + 0.030, UC + sg * 0.055),
                (c + 0.018, UC + sg * 0.055)]
        if sg < 0:
            poly = list(reversed(poly))
        blade_prism(poly, 0.002, gold_d, lift=0.0068 if sg > 0 else 0.0074)
# 날을 자루에 묶은 금속 띠
for u in (UC - 0.060, UC + 0.060):
    band(axe, ap(u), AX, OUT, 0.0165 * k, 0.0165 * k, 0.020 * k, 0.003 * k, segs=8, mat=steel_d)
aob = axe.obj("wangdi_axe_geo", angle=35.0)
c2.prop(e, "axe", aob, "hand_R", outline=0.003)

e.finalize()

# 머리끝 살구빛 그라데이션 (정점색)
hob = e.result.get("hair")
zmin = min(v.co.z for v in hob.data.vertices)
for node, base, tip in (("hair", HAIR, HAIR_TIP), ("hair_in", HAIR_D, HAIR_TIP_D)):
    ob = e.result.get(node)
    if ob is not None:
        c2.vc_gradient(ob, base, [(zmin + 0.03 * k, tip), (zmin + 0.34 * k, base)])

e.export("characters/wangdi.glb")
