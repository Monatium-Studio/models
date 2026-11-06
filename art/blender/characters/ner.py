"""네르(빡침): 세계수 교단의 사제장. 엘리아스 침공전에서 흑뉴아의 만행에 격노한 교주와 공명해 엘다인으로 각성하고
성전을 선포한다. 이 작품에서는 3막 M9 마지막 전투신(에르핀/네르 vs 흑뉴아)의 기습 장면에 쓴다.

원작 네르의 엘다인 이격 '네르(빡침)'(2.5주년 테마극장 「여왕님의 마음으로 만든 나라」)의 외형을 따른다.
각성 전 기본 네르(남색 수녀 베일, 짧은 남색 사제복, 작은 손도끼)와는 다른 판이다. 침공전 결전 장면은 각성 뒤이므로
이 판 하나만 만든다. 근거: docs/art/characters-cameo3.md 1장.
- 식별 요소: 바닥까지 오는 연한 금발(일자에 가까운 앞머리, 가슴까지 오는 옆머리), 캐릭터 오른쪽(-X)으로 늘어진
  바닥까지 오는 굵은 땋은 머리(끝에 은색 꽃 장식과 붉은 보석), 남보라빛 파란 눈의 반쯤 감긴 눈매, 흰 베일(안감 남색)과
  은색 티아라(가운데 위가 뾰족한 딸기형 붉은 보석, 은색 잎), 은색 흉갑(목 아래 조개 부채 장식 + 붉은 보석),
  남색 짧은 어깨 망토(금 테두리), 흰 소매와 은색 날개형 견갑·건틀릿, 바닥까지 오는 남보라 긴 드레스(오른쪽 앞 트임,
  금 테두리), 흰 타이츠와 흰 부츠(금색 나비 장식), 큰 흰 깃털 날개(엘다인), 폴암이 된 '세계수의 도끼'.
- 재해석: 3D SD 비율에 맞춰 드레스 트임을 캐릭터 오른쪽 앞으로 두고, 땋은 머리는 팔 뒤로 늘어지게 했다.
  도끼창은 별도 노드 ner_poleaxe(무기 규약: 원점 = 파지점, 자루는 로컬 Z, 날은 +Y)이고 기본은 왼손 옆에 세워 든다.
  도끼창 받침판의 문양은 원작 도안 대신 새싹(세계수) 실루엣으로 다시 그렸다.
- 표정: 키트 5종 + rage(빡침: 크게 벌린 입, 치켜뜬 눈) + glare(심판: 가늘게 뜬 차가운 눈) + teary(눈물 많은 여린 심성)
  + smug(한 손 도끼창을 짚은 위협 포즈용 한쪽 입꼬리) + blink 교정 키.

npm run model -- art/blender/characters/ner.py
npm run shot -- characters/ner.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame  # noqa: E402

cb.reset()
e = c3.ner_body("ner")
k = e.k
M_ = elf.mat

# ---- 팔레트 (원작 카드·소개 이미지에서 눈으로 뽑음)
navy = M_("ne_navy", "#4b4a86")
navy_d = M_("ne_navy_d", "#383669")
cape_m = M_("ne_cape", "#3f3d74")
white = M_("ne_white", "#fbf9fc")
white_d = M_("ne_white_d", "#e4e0ee")
veil_in = M_("ne_veil_in", "#3a3868")
silver = M_("ne_silver", "#c6cad9")
silver_d = M_("ne_silver_d", "#959bb2")
gold = M_("ne_gold", "#ecc475")
red = M_("ne_red", "#e2455e")
brown = M_("ne_brown", "#6e4c3f")
brown_d = M_("ne_brown_d", "#523830")
wing_hex, wing2_hex = "#ffffff", "#c8daf3"

# ---- 얼굴·머리: 공용 (cameo3.ner_face, ner_hair) — 대관식 판 ner_coronation.py와 같다
c3.ner_face(e)
h = c3.ner_hair(e)

# ---- 흰 베일 (안감 남색): 티아라 뒤 정수리부터 덮고 등·어깨로 늘어진다
EL_T = 46.0
c3.veil(e, h, white, veil_in, el_front=EL_T, az_open=72.0, az_full=104.0, lift=0.008, lift_lo=0.018, th=0.004,
        cols=24, rows=9, z_side=e.shoulder_z + 0.020 * k, z_back=e.shoulder_z - 0.110 * k, pleat=(0.010, 9, 0.45),
        rim=gold, rim_w=0.010)


# [오리지널] 베일 뒤 가운데 세계수 교단 문장 (금색 잎 네 장 십자): 각성 전 네르의 금색 십자 앞판을 베일로 옮긴 3차 디테일
def veil_emblem(buf):
    az, el = 180.0, -8.0
    s = h.s_of_el(az, el)
    p, nn = h.path(az, s, 0.0135 * k)
    Mx = Matrix.Translation(p) @ frame(nn, (0, 0, 1))
    for ang, L in ((0.0, 0.056), (90.0, 0.042), (180.0, 0.066), (270.0, 0.042)):
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(L, 0.026, n=5)], 0.0025 * k,
                 Mx @ Matrix.Rotation(math.radians(ang), 4, "Y"), mat=gold, w={"head": 1.0})
    c3.gem_drop(buf, Mx @ Matrix.Translation((0, -0.002 * k, 0.0)), 0.011 * k, red, depth=0.004 * k,
                w={"head": 1.0})


e.part("veil_emblem", "head", veil_emblem)


# ---- 은색 티아라: 베일 앞 가장자리를 따라 두른 띠 + 가운데 딸기형 붉은 보석과 은색 잎
def tiara(buf):
    w = {"head": 1.0}
    lift = 0.0125 * k
    pts, nrm, ups = [], [], []
    n = 17
    for i in range(n):
        az = lerp(-74.0, 74.0, i / (n - 1))
        el = EL_T - 0.8 - 4.0 * (abs(az) / 72.0) ** 2
        s = h.s_of_el(az, el)
        p, nn = h.path(az, s, lift)
        p2, _ = h.path(az, max(s - 0.01 * k, 0.0), lift)
        up = (p2 - p)
        up = (up - nn * up.dot(nn)).normalized()
        pts.append(p)
        nrm.append(nn)
        ups.append(up)
    elf._loop(buf, pts, nrm, ups, 0.010 * k, 0.0035 * k, mat=silver, w=w, closed=False)
    c = pts[n // 2]
    nc = nrm[n // 2]
    upc = ups[n // 2]
    Mc = Matrix.Translation(c + nc * 0.004 * k + upc * 0.010 * k) @ frame(nc, upc)
    # 은색 잎 무리 (가운데 위로 세 장, 양옆으로 누운 두 장씩)
    for ang, L, W, dz in ((0.0, 0.040, 0.020, 0.008), (40.0, 0.034, 0.017, 0.0), (-40.0, 0.034, 0.017, 0.0),
                          (78.0, 0.030, 0.015, -0.006), (-78.0, 0.030, 0.015, -0.006)):
        Ml = Mc @ Matrix.Translation((0, 0.0015 * k, dz * k)) @ Matrix.Rotation(math.radians(-ang), 4, "Y")
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(L, W)], 0.004 * k, Ml, mat=silver, w=w)
    c3.gem_drop(buf, Mc @ Matrix.Translation((0, -0.004 * k, 0.010 * k)), 0.012 * k, red, depth=0.006 * k,
                frame_mat=silver_d, frame_w=0.0028 * k, w=w)
    # 양옆 작은 은잎 (띠 위)
    for sg in (1, -1):
        for i0, ang in ((n // 2 + sg * 4, 90.0),):
            p, nn, up = pts[i0], nrm[i0], ups[i0]
            side = nn.cross(up).normalized() * sg
            Ml = Matrix.Translation(p + nn * 0.003 * k) @ frame(nn, side)
            c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.022, 0.012, n=4)], 0.003 * k, Ml, mat=silver,
                     w=w)


e.part("tiara", "head", tiara)

# ---- 굵은 땋은 머리 + 끝 은색 꽃 장식: 공용 (cameo3.ner_braid)
sz = e.shoulder_z
br = c3.ner_braid(e, h, silver, red)
h.shine(el=52, spread=76, n=2, size=1.2)

# ---- 상의: 남보라 몸판(세운 깃) + 흰 소매(약간 부풂) + 흰 장갑
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(navy, hem=hz - 0.010 * k, collar="stand", collar_mat=navy_d, flare=0.010)
e.sleeves(white, length=0.70, off=0.012, flare=0.010, puff=0.008)
e.gloves(white, cuff=white_d)
# 은색 건틀릿(팔뚝 보호대): 팔꿈치 쪽이 넓고 뾰족한 날개 장식
for sd in ("L", "R"):
    c2.arm_tube(e, silver, sd, 0.64, 0.95, off=0.020, extra=lambda t: 0.010 * smoothstep(0.80, 0.64, t),
                name=f"vambrace_{sd}")


def pauldron(buf, s):
    """날개형 은색 견갑: 둥근 덮개 + 뒤로 젖힌 깃 두 장."""
    sd = "L" if s > 0 else "R"
    S, d = e.S[sd], e.adir[sd]
    w = {f"shoulder_{sd}": 0.4, f"upperarm_{sd}": 0.6}
    up = V((-d.z * s * 0.0 + s * math.sin(math.radians(40)), 0.0, math.cos(math.radians(40))))
    up = (up - d * up.dot(d)).normalized()
    c = S + d * 0.050 * k + up * (0.040 * k)
    c2.ellipsoid(buf, c, d, V((0, 1, 0)), up, 0.050 * k, 0.046 * k, 0.020 * k, segs=10, rings=5, mat=silver, w=w)
    c2.ellipsoid(buf, c + up * 0.006 * k, d, V((0, 1, 0)), up, 0.034 * k, 0.030 * k, 0.018 * k, segs=10, rings=4,
                 mat=silver_d, w=w)
    for i, (dy, ln, ang) in enumerate(((0.024, 0.050, 24.0),)):
        root = c + V((0, dy * k, 0)) + up * 0.004 * k
        back = (V((0, 1, 0)) * math.cos(math.radians(ang)) + d * math.sin(math.radians(ang))).normalized()
        Ml = Matrix.Translation(root) @ frame(up, back)
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(ln, 0.026, n=5)], 0.005 * k, Ml, mat=silver, w=w,
                 chamfer=0.0015 * k)


for s in (1, -1):
    e.part(f"pauldron_{'L' if s > 0 else 'R'}", "arms", lambda buf, s=s: pauldron(buf, s))

# ---- 남색 짧은 어깨 망토 (금 테두리), 앞이 열려 흉갑이 보인다
capelet = c2.Shell(e, cape_m, e.torso_top + 0.014 * k, sz - 0.046 * k, gap=[(0.0, 26.0), (1.0, 44.0)], off=0.036,
                   th=0.004, shoulder=1.04, cols=20, rows=4, flare=[(0.0, 0.0), (1.0, 0.026)])
capelet.edge_trim(gold, width=0.006, th=0.002).hem_trim(gold, width=0.007, th=0.002)
capelet.done("capelet")

# ---- 은색 흉갑: 앞판 + 목 아래 조개 부채 장식 + 붉은 보석
plate = c2.Shell(e, silver, e.torso_top - 0.010 * k, wz + 0.006 * k, gap=96.0, back_only=True, off=0.022,
                 th=0.006, rows=5, cols=11, flare=[(0.0, 0.002), (0.45, 0.010), (1.0, 0.004)],
                 bust_drape=0.010)   # 성형 흉갑: 천처럼 늘어지지 않고 가슴 볼륨을 단단하게 감싼다
plate.edge_trim(silver_d, width=0.007, th=0.002).hem_trim(silver_d, width=0.008, th=0.002)
pc, pn = plate.surface(0.10, 0.0, 0.006 * k)
Mp = Matrix.Translation(pc) @ frame(pn, (0, 0, 1))
wp = e._torso_wfn(pc, 0)
for i in range(7):
    ang = lerp(-66.0, 66.0, i / 6)
    Ml = Mp @ Matrix.Translation((0, 0, -0.010 * k)) @ Matrix.Rotation(math.radians(-ang), 4, "Y")
    c2.prism(plate.buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.036 - 0.006 * abs(ang) / 66, 0.016, n=5)],
             0.004 * k, Ml, mat=silver if i % 2 == 0 else silver_d, w=wp)
c3.gem_drop(plate.buf, Mp @ Matrix.Translation((0, -0.004 * k, -0.004 * k)), 0.010 * k, red, depth=0.006 * k,
            frame_mat=silver, frame_w=0.003 * k, w=wp)
# 흉갑 아래 붓꽃 문양 (작은 잎 셋)
pc2, pn2 = plate.surface(0.62, 0.0, 0.004 * k)
Mp2 = Matrix.Translation(pc2) @ frame(pn2, (0, 0, 1))
for ang in (0.0, 46.0, -46.0):
    Ml = Mp2 @ Matrix.Rotation(math.radians(-ang), 4, "Y") @ Matrix.Translation((0, 0, -0.010 * k))
    c2.prism(plate.buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.028 if ang == 0 else 0.020, 0.012, n=4)],
             0.003 * k, Ml, mat=silver_d, w=e._torso_wfn(pc2, 0))
plate.done("breastplate")

# ---- 갈색 허리띠 + 오른쪽 작은 주머니
e.belt(brown, z=wz - 0.006 * k, h=0.014, th=0.004, off=0.024, buckle=silver, buckle_size=(0.020, 0.016))
e.pouch(brown, ("torso", wz - 0.030 * k, -62, 0.034 * k), size=(0.038, 0.020, 0.044), flap=brown_d, button=silver)

# ---- 바닥까지 오는 남보라 드레스: 캐릭터 오른쪽 앞 트임, 금 테두리
SLIT = -22.0
dress = c2.Shell(e, navy, wz + 0.004 * k, 0.026 * k, gap=[(0.0, 2.0), (0.22, 6.0), (0.55, 14.0), (1.0, 24.0)],
                 a_fn=lambda a, u: a + SLIT, off=0.018, th=0.004, skirt=True, rows=10, cols=24,
                 flare=[(0.0, 0.0), (0.35, 0.022), (1.0, 0.070)], cover=True)
dress.edge_trim(gold, width=0.007, th=0.002, i0=1).hem_trim(gold, width=0.009, th=0.002)
dress.done("dress")

# ---- 흰 타이츠 + 흰 부츠(금색 에르피엔 나비: 군기와 같은 도안)
for sd in ("L", "R"):
    c2.leg_tube(e, white, sd, 0.0, 0.86, off=0.004, name=f"tights_{sd}", segs=8)
q0 = e.q
e.q = 0.48     # 부츠는 드레스 자락에 거의 가려진다
e.boots(white, top=0.80, sole=(white_d, 0.014), cuff=gold, off=0.012, toe=0.004)
e.q = q0
for sd in ("L", "R"):
    a = e.anchor((f"leg_{sd}", 0.88, 0, 0.020 * k))

    def bfly(buf, a=a):
        Mx = a.matrix(lift=0.001 * k)
        fairy.emblem(buf, Mx, 0.034 * k, gold, depth=0.003 * k, w=a.w, n=20, low=True)    # 에르피엔 나비
    e.part(f"boot_bfly_{sd}", "body", bfly)

# ---- 큰 흰 깃털 날개 (엘다인: 기본 요정 날개보다 크다)
# 원작 일러(네르(빡침)): 옆으로 길게 펼친 큰 깃털 날개, 긴 깃 끝이 하늘빛
fairy.wings(e, span=0.52, height=0.22, sweep=22.0, raise_=2.0, prim=4, cov=2, color=wing_hex, color2=wing2_hex,
            z=wz + 0.080 * k, style="feather")

e.finalize()


# ---- 도끼창 (세계수의 도끼가 폴암으로 변한 것): 별도 노드 ner_poleaxe
def poleaxe():
    """로컬: 원점 = 파지점, 자루 = +Z(위: 은색 꼭지) / -Z(아래: 도끼머리), 날 = +Y. 길이 단위 m (k 배율)."""
    pink = M_("ne_shaft", "#d2577c")
    shaft = M_("ne_shaft_d", "#3d3a5e")
    sage = M_("ne_sage", "#7fae7e")
    plate_m = M_("ne_axe_plate", "#c8cbd8")
    S = k
    b = Buf()
    w = {}

    def tube(z0, z1, r0, r1, mat, segs=8):
        loft(b, [{"c": V((0, 0, z0 * S)), "rx": r0 * S, "ry": r0 * S, "w": w},
                 {"c": V((0, 0, z1 * S)), "rx": r1 * S, "ry": r1 * S, "w": w}], segs=segs, cap0="flat",
             cap1="flat", mat=mat)
    tube(-0.36, 0.10, 0.0115, 0.0115, pink)
    tube(0.10, 0.98, 0.0115, 0.0115, shaft)
    for z in (-0.30, 0.10, 0.62):                           # 은색 고리
        tube(z - 0.010, z + 0.010, 0.0150, 0.0150, silver)
    # 꼭지: 은색 깃 장식 + 붉은 보석 + 뾰족 끝
    tube(0.98, 1.00, 0.0170, 0.0170, silver_d)
    loft(b, [{"c": V((0, 0, 1.000 * S)), "rx": 0.020 * S, "ry": 0.016 * S, "w": w},
             {"c": V((0, 0, 1.040 * S)), "rx": 0.030 * S, "ry": 0.020 * S, "w": w},
             {"c": V((0, 0, 1.090 * S)), "rx": 0.022 * S, "ry": 0.016 * S, "w": w},
             {"c": V((0, 0, 1.130 * S)), "rx": 0.004 * S, "ry": 0.004 * S, "w": w}], segs=8, cap0="flat",
         cap1="flat", mat=silver)
    for sg in (1, -1):
        Ml = Matrix.Translation(V((sg * 0.016 * S, 0, 1.020 * S))) @ frame(V((sg, 0, 0)), V((sg * 0.6, 0, 1)))
        c2.prism(b, [(x * S, z * S) for x, z in c3.leaf_poly(0.060, 0.026, n=5)], 0.005 * S,
                 Ml @ Matrix.Translation((0, 0.0025 * S, 0)), mat=silver, w=w)
    for yy in (-1, 1):
        c3.gem_drop(b, Matrix.Translation(V((0, yy * 0.020 * S, 1.060 * S))) @ frame(V((0, yy, 0)), (0, 0, 1)),
                    0.009 * S, red, depth=0.004 * S, w=w)
    # 도끼머리 블록 + 문양판 (새싹)
    rbox(b, (0.040 * S, 0.050 * S, 0.130 * S), Matrix.Translation(V((0, 0, -0.420 * S))), mat=silver, w=w, r=0.25,
         segs=1)
    for xx in (1, -1):
        Mpl = Matrix.Translation(V((xx * 0.0205 * S, 0, -0.420 * S))) @ frame(V((xx, 0, 0)), (0, 0, 1))
        rbox(b, (0.036 * S, 0.004 * S, 0.096 * S), Mpl, mat=plate_m, w=w, r=0.3, segs=1)
        c2.prism(b, [(x * S, z * S) for x, z in c3.leaf_poly(0.040, 0.020)], 0.002 * S,
                 Mpl @ Matrix.Translation((0, -0.002 * S, -0.024 * S)), mat=sage, w=w)
        for ang in (40.0, -40.0):
            c2.prism(b, [(x * S, z * S) for x, z in c3.leaf_poly(0.020, 0.012, n=4)], 0.002 * S,
                     Mpl @ Matrix.Translation((0, -0.002 * S, 0.010 * S)) @ Matrix.Rotation(math.radians(ang), 4, "Y"),
                     mat=sage, w=w)
    tube(-0.495, -0.485, 0.020, 0.020, silver_d)
    # 아래 창끝
    loft(b, [{"c": V((0, 0, -0.490 * S)), "rx": 0.016 * S, "ry": 0.012 * S, "w": w},
             {"c": V((0, 0, -0.540 * S)), "rx": 0.012 * S, "ry": 0.009 * S, "w": w},
             {"c": V((0, 0, -0.640 * S)), "rx": 0.001 * S, "ry": 0.001 * S, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=silver)
    ob = b.obj("ner_poleaxe_core", angle=35.0)
    parts = [ob]
    # 초승달 날 (+Y): 바깥 호가 크고 안쪽이 오목, 아래에 이 빠진 홈
    poly = []
    for i in range(13):                                     # 바깥 날 (위 → 아래)
        t = i / 12
        a = math.radians(lerp(78.0, -96.0, t))
        poly.append((0.020 + 0.150 * math.cos(a) * (0.55 + 0.45 * math.sin(math.pi * t)), -0.430 + 0.200 * math.sin(a)))
    poly += [(0.050, -0.610), (0.064, -0.580), (0.044, -0.560)]   # 아래 홈 (이 빠진 자리)
    for i in range(6):                                      # 안쪽 오목 (아래 → 위, 블록에 붙음)
        t = i / 5
        poly.append((0.018 + 0.030 * math.sin(math.pi * t), lerp(-0.520, -0.250, t)))
    blade = c2.poly_object("ner_poleaxe_blade", [(y * S, z * S) for y, z in poly], 0.008 * S,
                           Matrix.Translation(V((0.004 * S, 0, 0))) @ Matrix(((0, 1, 0, 0), (1, 0, 0, 0),
                                                                            (0, 0, 1, 0), (0, 0, 0, 1))),
                           silver, bevel=0.0018 * S)
    parts.append(blade)
    # 날 위 붉은 보석 장식 (작은 마름모 셋)
    b2 = Buf()
    for (yy, zz, r) in ((0.085, -0.380, 0.010), (0.112, -0.360, 0.006), (0.095, -0.410, 0.005)):
        for xx in (1, -1):
            c2.prism(b2, c2.diamond_poly(r * S * 1.2, r * S * 2.0), 0.002 * S,
                     Matrix.Translation(V((xx * 0.0045 * S, yy * S, zz * S))) @ frame(V((xx, 0, 0)), (0, 0, 1)),
                     mat=red, w=w)
    # 뒤쪽 깃 날개 (-Y): 깃털 셋
    for i, (zz, ln, ang) in enumerate(((-0.360, 0.110, 30.0), (-0.400, 0.120, 8.0), (-0.440, 0.090, -14.0))):
        Mf = Matrix.Translation(V((0, -0.022 * S, zz * S))) @ Matrix.Rotation(math.radians(90 + ang), 4, "X") @ \
            Matrix.Rotation(math.radians(90), 4, "Z")
        c2.prism(b2, [(x * S, z * S) for x, z in c3.leaf_poly(ln, 0.040, tip=1.2)], 0.006 * S,
                 Mf @ Matrix.Translation((0, 0.003 * S, 0)), mat=silver_d if i == 1 else silver, w=w)
    parts.append(b2.obj("ner_poleaxe_trim", angle=35.0))
    for p in parts:
        cb.apply_modifiers(p)
    ob = cb.join(parts, "ner_poleaxe")
    # 파지점을 자루 위쪽으로: 도끼머리 아래 창끝이 바닥(z=0) 바로 위에 오도록 기하 전체를 올린다
    ob.data.transform(Matrix.Translation((0, 0, GRIP_UP * S)))
    return ob


GRIP_UP = 0.19


axe = poleaxe()
sock = bpy.data.objects["socket_hand_L"]
pos = sock.matrix_world.translation.copy()
Y = V((1.0, -0.55, 0.0)).normalized()          # 날이 바깥 앞을 본다 (정면에서 날 면이 보이게)
Z = V((0.0, 0.0, 1.0))
X = Y.cross(Z).normalized()
Mw = Matrix((X, Y, Z)).transposed().to_4x4()
Mw.translation = pos + V((0.004 * k, -0.010 * k, 0.0))
c3.socket_prop(e, axe, "socket_hand_L", Mw, name="poleaxe", outline=0.003,
               props={"grip": "0,0,0", "tip": "0,0,%.3f" % ((GRIP_UP - 0.64) * k)})

e.export("characters/ner.glb")
