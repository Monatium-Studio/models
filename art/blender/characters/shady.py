"""셰이디(역전): 유령늪의 수장('유령늪의 새로운 질서'). 에필로그 에르핀의 세 번째 대관식에서 네 번째로 헌사를 하는
지도자다(원작 테마극장 「여왕님의 마음으로 만든 나라」 에피소드 12: "유령늪의 셰이디 씨").

원작 이격 '셰이디(역전)'(영문 Twisted)의 카드·소개 이미지를 따른다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 검은빛 남색 긴 머리(허리까지)와 정수리·옆머리의 청록 하이라이트, 캐릭터 왼쪽 뒤의 큰 검은 리본(청록 테)과
  그 아래로 늘어진 흰 베일, 반쯤 감긴 회청색 눈과 'ω' 입(메롱), 왼쪽 귀의 청록 물방울 귀걸이, 어깨를 드러낸 검은
  고딕 드레스(검은 초커 + 청록 보석 브로치, 회색 자보 프릴, 검은 코르셋), 따로 낀 검은 부푼 소매, 회색 속치마 위의
  검은 프릴 치마(청록 안단, 뒤로 길게 늘어진 청록 자락), 회색 리본, 짙은 회색 타이츠, 청록 큰 낫(해골 장식 + 사슬),
  분홍 봉제 인형.
- 유령: 원작 유령은 사람 귀(둥근 귀)라 fairy.Fairy(ears="round")의 둥근 귀를 쓰고 날개는 만들지 않는다.
- 재해석: 원작 눈의 가로 줄무늬(멍한 눈 표현)는 옮기지 않고 회청색 홍채 + 밝은 아래 반달로 단순화했다. 낫은 별도 노드
  shady_scythe(socket_hand_R, 로컬: 원점 = 파지점, 자루 = +Z, 날 = +Y), 인형은 별도 노드 shady_doll(socket_hand_L).
- 표정: 키트 5종 + tease(헌사의 "흐흥~" 놀리는 웃음) + tongue(메롱, 소개 이미지) + vexed(빡침을 참는 미간 주름)
  + fond(대견해하는 부드러운 미소) + blink 교정 키.

npm run model -- art/blender/characters/shady.py
npm run shot -- characters/shady.glb
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
# 체형: 원작 카드·소개 이미지의 성인 체형(코르셋 위 완만한 가슴 볼륨)을 키트 bust로 단정하게 옮긴다 (양식화, ELF_KIT 2장)
e = fairy.Fairy("shady", ears="round", ear_size=0.9, height=1.22, head=0.45, leg=1.03, chest=0.45, bust=0.5,
                hips=1.05, segs=0.62, hand_q=0.45, cheek=0.12)
k = e.k
M_ = elf.mat

# ---- 팔레트 (원작 카드·소개 이미지에서 눈으로 뽑음)
HAIR, HAIR_D, HAIR_L = "#2b2a38", "#1a1924", "#5fd3d0"
black = M_("sh_black", "#24222c")
black_l = M_("sh_black_l", "#36343f")
gray = M_("sh_gray", "#8e8c9b")
gray_d = M_("sh_gray_d", "#6a6877")
cyan = M_("sh_cyan", "#56cfcb")
cyan_d = M_("sh_cyan_d", "#2f8f8f")
veil_m = M_("sh_veil", "#d3d6e0")
veil_d = M_("sh_veil_d", "#a9adbd")
tights = M_("sh_tights", "#4a4756")
silver = M_("sh_silver", "#c3c6d2")
hair_cy = M_("sh_hair_cyan", "#4cc6c4")

# ---- 얼굴: 반쯤 감긴 회청색 눈, 'ω' 입 (원작 카드의 능청스러운 얼굴)
e.face(eye_color="#8d9bb6", iris_dark="#4c5770", iris_light="#d9e3f2", pupil="#2c3346",
       lash="#26222e", brow="#2e2c3a", brow_th=0.9, blush="#f4a0a6", blush_size=1.15,
       base={"eye": {"top": 0.016, "ktop": 4.8, "tilt_in": 0.002, "cout": 0.017},
             "brow": {"ang": 6.0, "dz": 0.066, "arch": 0.003},
             "mouth": {"w": 0.022, "curve": 0.0024, "wave": 0.0018, "open": 0.0}},
       expr={
           # 메롱: 혀를 내민 능청 (소개 이미지)
           "tongue": {"eye": {"top": 0.020, "lift": 0.006},
                      "brow": {"ang": 4.0, "dz": 0.068},
                      "mouth": {"w": 0.026, "curve": 0.0050, "open": 0.0170, "top_arch": 0.0012, "wave": 0.0}},
           # 빡침을 참는 얼굴: 미간을 모으고 입을 다문다 (원작 이격의 새 표정)
           "vexed": {"eye": {"top": 0.014, "ktop": 5.2, "tilt_in": -0.012},
                     "brow": {"ang": -18.0, "dz": 0.056, "th": 0.0070},
                     "mouth": {"w": 0.018, "curve": -0.0030, "wave": 0.0012}},
           # 대견해하는 미소: 눈이 휘고 입꼬리가 부드럽게 오른다 ("시간도 참 빠르게 지나간다")
           "fond": {"eye": {"top": 0.018, "lift": 0.014, "kbot": 2.4, "tilt_in": 0.006},
                    "brow": {"ang": 12.0, "dz": 0.068, "arch": 0.004},
                    "mouth": {"w": 0.024, "curve": 0.0060, "open": 0.0040, "wave": 0.0}},
       })
c2.face_expr(e, "tease",
             both={"eye": {"top": 0.015, "lift": 0.010, "ktop": 5.0},
                   "mouth": {"w": 0.028, "curve": 0.0050, "open": 0.0060, "wave": 0.0}},
             L={"brow": {"dz": 0.072, "ang": 8.0, "arch": 0.004}}, R={"brow": {"dz": 0.062, "ang": -4.0}},
             corner=(0.0080, 0.0005), mouth_dx=0.0020 * k)

# ---- 머리 (헤어 v2): 검은빛 남색 긴 머리, 흐트러진 앞머리, 정수리 청록 광택, 허리까지 오는 뒷머리


def soft_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.1
        lk["free"] *= 0.7


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.12, lock_fn=fairy.lock_edit(soft_locks))
h.cap(front=30, side=-6, back=-46, part=-12, segs=15, rows=5)
h.bangs(n=7, spread=58, tip_el=-6, sweep=-8, part=-12, jag=0.18, curl=1.2, seed=9.0)
h.sides(length=0.30, width=0.082, az=62, curl=0.6, thick=1.1, n=2)
h.back(length=0.46, n=7, spread=100)
h.shine(el=52, spread=70, n=2, size=1.25)      # 광택 = 청록 (light 색)
o = h.off
# 청록 하이라이트 다발: 캐릭터 오른쪽(-X) 앞머리 위에서 볼 옆으로 내려오는 한 다발 (원작 카드의 청록 브릿지)
h.strand([h.sp(-38, 30, o * 1.05), h.sp(-50, 10, o * 1.32), h.sp(-58, -12, o * 1.30),
          h.sp(-62, -34, o * 1.05)],
         0.050 * k, 0.012 * k, n=12, segs=8, taper=[(0, 0.8), (0.25, 1.0), (0.7, 0.8), (1, 0.0)], mat=hair_cy)

# ---- 큰 검은 리본 (캐릭터 왼쪽 뒤, 청록 매듭) + 그 아래로 늘어진 흰 베일
BOW_AZ, BOW_EL = 118.0, 36.0
bp, bn = h.path(BOW_AZ, h.s_of_el(BOW_AZ, BOW_EL), 0.012 * k)
bout = V((bn.x, bn.y, 0.0)).normalized()


def big_bow(buf):
    w = {"head": 1.0}
    # 리본 면은 뒤·바깥을 보고, 날개는 위아래로 크게 벌어진다 (원작: 머리 옆에서 솟은 큰 리본)
    face_dir = (bout * 0.85 + V((0, 0.40, 0.25))).normalized()
    M = Matrix.Translation(bp + bout * 0.020 * k + V((0, 0, 0.010 * k))) @ frame(face_dir, V((0, 0, 1))) @ \
        Matrix.Rotation(math.radians(-24.0), 4, "Y")
    c2.bow_geo(buf, M, 0.340 * k, black, w=w, tails=0.55, knot_mat=cyan, segs=8)
    # 리본 날개 안쪽 청록 띠 (날개 가운데를 지나는 줄)
    for sg in (1, -1):
        Mt = M @ Matrix.Translation((sg * 0.075 * k, -0.030 * k, 0.012 * k))
        c2.ellipsoid(buf, Mt.to_translation(), (M.to_3x3() @ V((sg, 0, 0.25))).normalized(),
                     (M.to_3x3() @ V((0, 0, 1))).normalized(), (M.to_3x3() @ V((0, -1, 0))).normalized(),
                     0.045 * k, 0.010 * k, 0.010 * k, segs=6, rings=4, mat=cyan, w=w)


e.part("big_bow", "head", big_bow)


def veil(buf):
    """리본 아래 뒷머리 위로 늘어진 흰 베일: 물결 진 천 두 장 (위는 머리, 아래로 갈수록 가슴 뒤 웨이트)."""
    rows, cols = 8, 9
    for layer, (az0, az1, ln, mat) in enumerate(((118.0, 168.0, 0.34, veil_d), (126.0, 160.0, 0.26, veil_m))):
        P = []
        for i in range(rows):
            u = i / (rows - 1)
            row = []
            for j in range(cols):
                v_ = j / (cols - 1)
                az = lerp(az0, az1, v_)
                # 뒷머리 바깥 면을 따라 늘어진다: 머리 덩어리 바깥 + 아래로 갈수록 등 뒤로 벌어짐, 세로 물결
                hem = 0.035 * k * abs(math.sin(v_ * math.pi * 3.0))      # 물결 밑단 (가리비)
                q, nn = h.path(az, h.s_of_el(az, BOW_EL - 10.0) + (ln * k - hem) * u, (0.030 + 0.010 * layer) * k)
                rad = V((nn.x, nn.y, 0.0)).normalized()
                q = q + rad * (0.014 * k * math.sin(v_ * math.pi * 6.0) * smoothstep(0.0, 0.5, u) + 0.016 * k * u)
                row.append(q)
            P.append(row)
        ids = []
        for i in range(rows):
            u = i / (rows - 1)
            wgt = {"head": 1.0} if u < 0.10 else elf.mixw({"head": 1.0}, {"chest": 1.0}, smoothstep(0.10, 0.5, u))
            ids.append([buf.vert(q, wgt) for q in P[i]])
        for i in range(rows - 1):
            for j in range(cols - 1):
                buf.face((ids[i][j], ids[i + 1][j], ids[i + 1][j + 1], ids[i][j + 1]), mat)
                buf.face((ids[i][j], ids[i][j + 1], ids[i + 1][j + 1], ids[i + 1][j]), mat)


e.part("veil", "head", veil)

# 왼쪽(+X) 귀 청록 물방울 귀걸이
ear_p, ear_n = e.head_point(92.0, -14.0, 0.006 * k)


def earring(buf):
    w = {"head": 1.0}
    loft(buf, [{"c": ear_p, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w},
               {"c": ear_p + V((0, 0, -0.014 * k)), "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w}], segs=5,
         cap0="round", cap1="round", mat=silver)
    Mx = Matrix.Translation(ear_p + V((0.002 * k, -0.002 * k, -0.026 * k))) @ frame(V((1, -0.3, 0)), (0, 0, -1))
    c2.prism(buf, c3.drop_poly(0.007 * k, n=10, point=1.6), 0.005 * k, Mx, mat=cyan, w=w, chamfer=0.0015 * k)


e.part("earring", "head", earring)

# ---- 상의: 어깨를 드러낸 검은 코르셋 + 초커(청록 보석 브로치) + 회색 자보 프릴
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
bod = c2.Shell(e, black, sz - 0.030 * k, hz - 0.006 * k, off=0.010, th=0.004, rows=6, cols=20, cover=True,
               flare=[(0.0, 0.004), (0.5, 0.0), (1.0, 0.004)])
bod.top_trim(black_l, width=0.010, th=0.003).hem_trim(black_l, width=0.008, th=0.002)
# 코르셋 앞판 (짙은 판 + 아래로 뾰족)
pc, pn = bod.surface(0.55, 0.0, 0.003 * k)
c2.prism(bod.buf, [(-0.034 * k, 0.040 * k), (0.034 * k, 0.040 * k), (0.026 * k, -0.020 * k), (0.0, -0.046 * k),
                   (-0.026 * k, -0.020 * k)], 0.003 * k, Matrix.Translation(pc) @ frame(pn, (0, 0, 1)), mat=black_l,
         w=e._torso_wfn(pc, 0))
bod.done("bodice")
e.part("choker", "head", lambda buf: band(buf, (0, 0.004 * k, e.torso_top + 0.026 * k), (0, 0, 1), (1, 0, 0),
                                          0.050 * k, 0.046 * k, 0.012 * k, 0.004 * k, segs=14, mat=black,
                                          w={"neck": 1.0}))


def jabot(buf):
    """초커 아래 브로치 + 가슴 가운데 회색 자보 프릴 세 단 (위가 좁고 아래가 넓은 물결 판)."""
    for i, (z, wd, mat) in enumerate(((sz - 0.020 * k, 0.050, gray), (sz - 0.048 * k, 0.064, gray_d),
                                      (sz - 0.078 * k, 0.074, gray))):
        p, n = e.torso_point(z, 0, 0.022 * k + 0.002 * k * i)
        Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1))
        pts = []
        for t in range(13):
            u = -1 + 2 * t / 12
            zz = -0.026 * k - 0.006 * k * abs(math.sin(u * math.pi * 2))
            pts.append((u * wd * k * 0.5, zz))
        pts = [(wd * k * 0.22, 0.004 * k)] + list(reversed(pts)) + [(-wd * k * 0.22, 0.004 * k)]
        pts = list(reversed(pts))
        c2.prism(buf, pts, 0.004 * k, Mx, mat=mat, w=e._torso_wfn(p, 0))
    p, n = e.torso_point(e.torso_top - 0.006 * k, 0, 0.020 * k)
    Mb = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    w = {"neck": 0.4, "chest": 0.6}
    c2.prism(buf, c2.star_poly(0.016 * k, 0.012 * k, n=8, rot=90), 0.004 * k, Mb, mat=gray_d, w=w)
    c3.gem_drop(buf, Mb @ Matrix.Translation((0, -0.004 * k, 0.0)), 0.008 * k, cyan, depth=0.004 * k, w=w)


e.part("jabot", "body", jabot)

# ---- 따로 낀 검은 부푼 소매 (위팔 중간 ~ 손목 위), 끝 청록 안단
for sd in ("L", "R"):
    c2.arm_tube(e, black, sd, 0.18, 0.84, off=0.014,
                extra=lambda t: 0.020 * math.sin(math.pi * min(1.0, (t - 0.18) / 0.66)) + 0.018 * smoothstep(0.66, 0.84, t),
                name=f"sleeve_{sd}", segs=12)
    e.ring(cyan, f"arm_{sd}", 0.835, h=0.010, th=0.003, off=0.048, name=f"sleeve_cuff_{sd}")
    e.ring(black_l, f"arm_{sd}", 0.19, h=0.012, th=0.004, off=0.018, name=f"sleeve_top_{sd}")

# ---- 하의: 회색 속치마 + 검은 프릴 치마(청록 밑단) + 뒤로 늘어진 청록 자락 + 회색 리본, 짙은 회색 타이츠
q0 = e.q
e.q = 0.45
e.pants(black, length=0.08, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
train = c2.Shell(e, cyan_d, wz - 0.004 * k, 0.150 * k, gap=70.0, back_only=False, off=0.020, th=0.004, skirt=True,
                 rows=7, cols=16, flare=[(0.0, 0.0), (0.4, 0.036), (1.0, 0.100)], ruffle=(0.010, 6, 0.4),
                 drop=[(0.0, 0.0), (1.0, 0.080)])
train.hem_trim(cyan, width=0.012, th=0.003)
train.done("train")
petti = c2.Shell(e, gray, wz - 0.002 * k, 0.290 * k, off=0.024, th=0.004, skirt=True, rows=6, cols=22,
                 flare=[(0.0, 0.0), (0.4, 0.022), (1.0, 0.052)], ruffle=(0.006, 9, 0.3))
petti.hem_trim(gray_d, width=0.008, th=0.002)
petti.done("petticoat")
over = c2.Shell(e, black, wz + 0.002 * k, 0.250 * k, gap=[(0.0, 10.0), (0.5, 26.0), (1.0, 46.0)], back_only=False,
                off=0.032, th=0.004, skirt=True, rows=8, cols=22, flare=[(0.0, 0.0), (0.4, 0.034), (1.0, 0.080)],
                ruffle=(0.014, 8, 0.30))
over.edge_trim(cyan, width=0.008, th=0.002, i0=1).hem_trim(cyan, width=0.010, th=0.002)
over.done("overskirt")
e.ring(black_l, "torso", wz, h=0.014, th=0.004, off=0.036, name="waist_band")
for sg in (1, -1):
    a = e.anchor(("torso", hz - 0.010 * k, sg * 68, 0.060 * k))
    e.part(f"skirt_bow_{sg}", "body",
           lambda buf, a=a: c2.bow_geo(buf, a.matrix(), 0.052 * k, gray, w=a.w, tails=0.9, knot_mat=cyan, segs=6))
for sd in ("L", "R"):
    c2.leg_tube(e, tights, sd, 0.05, 0.92, off=0.004, name=f"tights_{sd}", segs=10)
q0 = e.q
e.q = 0.48
e.boots(black, top=0.90, sole=(black_l, 0.012), cuff=cyan, off=0.010, toe=0.004)
e.q = q0

e.finalize()


# ---- 큰 낫 (별도 노드 scythe): 회색 감은 자루 + 위 해골 장식 + 늘어진 사슬 + 청록 날
def scythe():
    """로컬: 원점 = 오른손 파지점, 자루 = +Z(위: 날·해골), 날은 +Y(앞)로 휘어 아래로 내려온다."""
    S = k
    b = Buf()
    w = {}
    blade_c = M_("sh_blade", "#7fe4df")
    blade_e = M_("sh_blade_e", "#e9fbfa")
    shaft = M_("sh_shaft", "#9a98a6")
    shaft_d = M_("sh_shaft_d", "#5a5866")
    bone = M_("sh_bone", "#f1eee9")
    hole = M_("sh_hole", "#2a2630")

    def tube(z0, z1, r, mat, segs=8):
        loft(b, [{"c": V((0, 0, z0 * S)), "rx": r * S, "ry": r * S, "w": w},
                 {"c": V((0, 0, z1 * S)), "rx": r * S, "ry": r * S, "w": w}], segs=segs, cap0="flat", cap1="flat",
             mat=mat)
    tube(-0.50, 0.70, 0.011, shaft)
    for z in (-0.40, -0.20, 0.10, 0.36, 0.58):            # 감은 띠
        tube(z - 0.012, z + 0.012, 0.0135, shaft_d)
    tube(-0.56, -0.50, 0.016, shaft_d)                       # 물미
    loft(b, [{"c": V((0, 0, -0.56 * S)), "rx": 0.012 * S, "ry": 0.012 * S, "w": w},
             {"c": V((0, 0, -0.64 * S)), "rx": 0.001 * S, "ry": 0.001 * S, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=shaft_d)
    # 위 해골 장식 (두개골 + 눈구멍 + 턱)
    top = V((0, 0, 0.76 * S))
    c2.ellipsoid(b, top, V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.040 * S, 0.038 * S, 0.036 * S, segs=10,
                 rings=6, mat=bone, w=w)
    rbox(b, (0.044 * S, 0.034 * S, 0.026 * S), Matrix.Translation(top + V((0, -0.006 * S, -0.034 * S))), mat=bone,
         w=w, r=0.4, segs=1)
    for sx in (1, -1):
        disc(b, top + V((sx * 0.015 * S, -0.033 * S, 0.000)), (sx * 0.25, -1, 0), (0, 0, 1), 0.010 * S, 0.011 * S,
             0.003 * S, segs=8, mat=hole, w=w)
    tube(0.70, 0.73, 0.016, shaft_d)
    ob = b.obj("shady_scythe_core", angle=35.0)
    # 날: 자루 위에서 앞(+Y)으로 뻗었다가 아래로 휘는 초승달 (청록, 바깥 날은 밝게)
    poly = []
    n = 14
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(lerp(100.0, -10.0, t))
        r = 0.34 * (0.92 + 0.08 * math.sin(math.pi * t))
        poly.append((0.02 + r * math.cos(a) + 0.06, 0.62 + 0.20 * math.sin(a) - 0.20 * t))
    for i in range(n):
        t = 1 - i / (n - 1)
        a = math.radians(lerp(96.0, 0.0, t))
        r = 0.26 * (0.90 + 0.10 * math.sin(math.pi * t))
        poly.append((0.02 + r * math.cos(a) + 0.07, 0.64 + 0.12 * math.sin(a) - 0.25 * t + 0.02))
    poly = [(y, z) for y, z in poly]
    Mside = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    blade = c2.poly_object("shady_scythe_blade", [(y * S, z * S) for y, z in poly], 0.008 * S,
                           Matrix.Translation(V((0.004 * S, 0, 0))) @ Mside, blade_c, bevel=0.0016 * S)
    # 날 등 쪽 짙은 받침 (자루와 날을 잇는 쇠)
    b2 = Buf()
    rbox(b2, (0.030 * S, 0.070 * S, 0.050 * S), Matrix.Translation(V((0, 0.040 * S, 0.660 * S))), mat=shaft_d, w=w,
         r=0.3, segs=1)
    # 해골 아래 늘어진 사슬 (자루 옆)
    c3.chain(b2, [V((0.016 * S, 0, 0.72 * S)), V((0.040 * S, -0.010 * S, 0.60 * S)),
                  V((0.030 * S, -0.020 * S, 0.48 * S))], 0.030 * S, 0.0035 * S, silver, segs=5, ring=3)
    ob2 = b2.obj("shady_scythe_trim", angle=35.0)
    _ = blade_e
    return cb.join([ob, blade, ob2], "shady_scythe")


sc = scythe()
sock = bpy.data.objects["socket_hand_R"]
pos = sock.matrix_world.translation.copy()
Yd = V((-0.55, -1.0, 0.0)).normalized()        # 날이 앞·바깥(캐릭터 오른쪽)을 본다
Zd = V((0.0, 0.0, 1.0))
Xd = Yd.cross(Zd).normalized()
Mw = Matrix((Xd, Yd, Zd)).transposed().to_4x4()
Mw.translation = pos + V((-0.004 * k, -0.010 * k, 0.040 * k))
c3.socket_prop(e, sc, "socket_hand_R", Mw, name="scythe", outline=0.003,
               props={"grip": "0,0,0", "tip": "0,0,%.3f" % (-0.64 * k)})


# ---- 분홍 봉제 인형 (별도 노드 doll): 둥근 몸 + 처진 귀 + 흰 해골 두건 + 꿰맨 자국
def doll():
    S = k
    b = Buf()
    w = {}
    pink = M_("sh_doll", "#e7a7a6")
    pink_d = M_("sh_doll_d", "#c97f82")
    bone = M_("sh_doll_skull", "#f3efe9")
    eye = M_("sh_doll_eye", "#3a2a30")
    c2.ellipsoid(b, V((0, 0, 0.040 * S)), V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.040 * S, 0.034 * S,
                 0.030 * S, segs=10, rings=6, mat=pink, w=w)
    c2.ellipsoid(b, V((0, -0.004 * S, 0.096 * S)), V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.034 * S,
                 0.038 * S, 0.032 * S, segs=10, rings=6, mat=pink, w=w)
    for sx in (1, -1):                                      # 처진 귀
        c2.ellipsoid(b, V((sx * 0.038 * S, 0.004 * S, 0.084 * S)), V((sx * 0.4, 0, -1)).normalized(),
                     V((0, 1, 0)), V((1, 0, 0)), 0.030 * S, 0.010 * S, 0.014 * S, segs=8, rings=5, mat=pink_d, w=w)
        c2.ellipsoid(b, V((sx * 0.030 * S, -0.004 * S, 0.012 * S)), V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)),
                     0.014 * S, 0.012 * S, 0.012 * S, segs=6, rings=4, mat=pink_d, w=w)
        disc(b, V((sx * 0.012 * S, -0.033 * S, 0.096 * S)), (sx * 0.2, -1, 0), (0, 0, 1), 0.0050 * S, 0.0050 * S,
             0.0015 * S, segs=6, mat=eye, w=w)
    # 흰 해골 두건 (머리 위를 덮는 반구 + 눈구멍 대신 작은 홈)
    c2.ellipsoid(b, V((0, 0.002 * S, 0.118 * S)), V((0, 0, 1)), V((1, 0, 0)), V((0, -1, 0)), 0.022 * S, 0.034 * S,
                 0.030 * S, segs=10, rings=5, mat=bone, w=w)
    rbox(b, (0.004 * S, 0.004 * S, 0.030 * S), Matrix.Translation(V((0.010 * S, -0.030 * S, 0.050 * S))), mat=pink_d,
         w=w, r=0.2, segs=1)
    return b.obj("shady_doll", angle=40.0)


dl = doll()
sockl = bpy.data.objects["socket_hand_L"]
posl = sockl.matrix_world.translation.copy()
Mw2 = Matrix.Translation(posl + V((0.006 * k, -0.024 * k, -0.040 * k)))
c3.socket_prop(e, dl, "socket_hand_L", Mw2, name="doll", outline=0.0025)

e.export("characters/shady.glb")
