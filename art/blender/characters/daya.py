"""다야: 용족의 수장(다이아몬드 용족). 에필로그 '에르핀의 세 번째 대관식'에서 다섯 번째로 헌사를 하는 지도자
(원작 테마극장 「여왕님의 마음으로 만든 나라」 에피소드 12: 용족 동굴의 다야).

원작 다야(트릭컬 리바이브, '용족의 수장', 순수 성격 용족)의 기본 복장으로 만든 카메오 모델. 다야(퓨어샤인)은 별개의 판이다.
- 유지한 식별 요소: 바닥 근처까지 오는 은백색 긴 생머리와 일자 앞머리, 정수리 위 작은 짙은 회색 티아라, 머리 양옆에서
  솟아 바깥으로 말린 거대한 다이아몬드(다면체) 뿔, 짧은 뾰족 귀와 마름모 크리스털 귀걸이, 회청색 반쯤 감긴 나른한 눈과
  'ω' 입, 아이보리 민소매 홀터 원피스(목의 작은 짙은 회색 깃), 엇갈린 X 무늬의 회색 허리띠, 맨팔·맨발, 회색 박쥐형 막
  날개(관절 끝의 흰 크리스털 조각), 회색 꼬리, 손에 든 다이아몬드, 왕좌 옆에 기대 둔 회색 대검.
- 재해석: 3D SD 비율에 맞춰 원피스 옆트임을 캐릭터 왼쪽(+X) 앞에 두었다. 뿔은 원작의 깎은 면을 살려 육각 단면을
  평면 셰이딩으로 그렸다. 다이아몬드(daya_gem, 왼손)와 대검(daya_sword, 등에 비스듬히)은 별도 노드다.
  대검은 원작에서 왕좌 옆에 기대 둔 장식이라 장면에 따라 숨긴다.
- 표정: 키트 5종 + proud(헌사: 당당히 고개를 든 얼굴, 말하는 입) + wink(원작 카드의 왼눈 윙크, 교정 키 없음)
  + doubt(속은 기분: 가늘게 뜬 의심의 눈) + delight(다이아몬드를 보는 반짝이는 웃음) + blink 교정 키.
근거: docs/art/characters-cameo3.md

npm run model -- art/blender/characters/daya.py
npm run shot -- characters/daya.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
import dragon_common as dc  # noqa: E402
from elf import V, Matrix, Buf, band, loft, lerp, smoothstep, catmull, frame  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("daya", height=1.22, head=0.45, leg=1.03, chest=0.30, bust=0.40, hips=1.02, segs=0.62, hand_q=0.45, cheek=0.11,
            ear_len=0.062, ear_width=0.044, ear_angle=-6.0, ear_sweep=16.0)
k = e.k

# ---- 팔레트 (원작 카드·소개 이미지에서 눈으로 뽑음)
HAIR, HAIR_D, HAIR_L = "#d8d7e1", "#a6a3b6", "#f6f6fa"     # 은회색 (아이보리 원피스와 구분되게)
dress = M_("dy_dress", "#e9e3d7")       # 아이보리 (피부색과 구분되게 베이지 쪽으로)
dress_d = M_("dy_dress_d", "#c8bfae")
collar_m = M_("dy_collar", "#5e5a66")
belt_m = M_("dy_belt", "#8f8c98")
belt_d = M_("dy_belt_d", "#5f5c69")
tiara_m = M_("dy_tiara", "#55515e")
crystal = M_("dy_crystal", "#f1f4fa")
crystal_d = M_("dy_crystal_d", "#c9d1de")
mem = M_("dy_membrane", "#9d99a5")
wbone = M_("dy_wingbone", "#6f6a78")
tail_m = M_("dy_tail", "#aeadb8")
tail_b = M_("dy_tail_belly", "#d4d3db")

# ---- 얼굴: 회청색 눈, 반쯤 감긴 나른한 눈매, 가는 회색 눈썹, 'ω' 입
e.face(eye_color="#9aa6b8", iris_dark="#5d6779", iris_light="#dfe6f0", pupil="#3d4352",
       lash="#4a4450", brow="#9b97a6", brow_th=0.85, blush="#f6a5a7", blush_size=1.18,
       base={"eye": {"top": 0.014, "ktop": 5.2, "tilt_in": -0.002, "cout": 0.017},
             "brow": {"ang": -2.0, "dz": 0.066, "arch": 0.002},
             "mouth": {"w": 0.022, "curve": 0.0018, "wave": 0.0018, "open": 0.0}},
       expr={
           # 헌사: 당당히 뜬 눈, 살짝 올린 눈썹, 말하는 입 ("나, 다야는 그대가 영원히 빛날 것이라 믿는다")
           "proud": {"eye": {"top": 0.024, "ktop": 3.8, "lift": 0.004},
                     "brow": {"ang": 4.0, "dz": 0.070, "arch": 0.004},
                     "mouth": {"w": 0.022, "curve": 0.0035, "open": 0.0110, "wave": 0.0, "top_arch": 0.0010}},
           # 속은 기분: 더 가늘게 뜬 의심의 눈, 안쪽이 올라간 눈썹, 물결 입
           "doubt": {"eye": {"top": 0.008, "ktop": 5.8, "tilt_in": -0.006},
                     "brow": {"ang": 10.0, "dz": 0.064},
                     "mouth": {"w": 0.018, "curve": -0.0020, "wave": 0.0016}},
           # 다이아몬드를 보는 반짝이는 웃음: 크게 뜬 눈, 'ω'로 벌린 입
           "delight": {"eye": {"top": 0.030, "ktop": 3.0, "lift": 0.006},
                       "iris": {"pupil": 0.80},
                       "brow": {"ang": 10.0, "dz": 0.074, "arch": 0.005},
                       "mouth": {"w": 0.030, "curve": 0.0060, "open": 0.0100, "wave": 0.0020}},
       })
c2.face_expr(e, "wink",
             both={"mouth": {"w": 0.022, "curve": 0.0018, "wave": 0.0018}},
             L={"eye": {"close": 1.0}, "brow": {"dz": 0.064, "ang": -4.0}},
             R={"eye": {"top": 0.016, "ktop": 5.0}, "brow": {"dz": 0.068, "ang": 0.0}},
             blink_fix=False)


# ---- 머리 (헤어 v2): 은백색 긴 생머리, 일자 앞머리, 허리 아래까지 오는 옆머리, 종아리까지 오는 뒷머리
def dy_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.4            # 뭉툭한 일자 앞머리
        lk["free"] *= 0.55


h = c2.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.10, lock_fn=c2.lock_edit(dy_locks))
h.cap(front=30, side=-6, back=-46, part=0, segs=15, rows=5)
h.bangs(n=8, spread=58, tip_el=-2, sweep=0, part=0, jag=0.14, curl=0.9, seed=5.0)
h.sides(length=0.40, width=0.076, az=62, curl=0.4, thick=1.05)
h.back(length=0.58, n=7, spread=100)
h.ahoge(az=-20, height=0.045, curl=1.1, width=0.014)
h.shine(el=52, spread=74, n=2, size=1.1)


# ---- 다이아몬드 뿔: 머리 양옆 위에서 솟아 바깥·뒤로 갔다가 아래·앞으로 말린다 (육각 단면, 평면 셰이딩)
def crystal_horn(side):
    s = 1 if side == "L" else -1
    az, el = s * 72.0, 28.0
    base, nrm = h.path(az, h.s_of_el(az, el), -0.006 * k)
    offs = [(s * 0.034, 0.014, 0.030), (s * 0.072, 0.034, 0.026), (s * 0.096, 0.036, -0.008),
            (s * 0.098, 0.016, -0.046), (s * 0.082, -0.012, -0.066)]
    pts = [base - nrm * 0.022 * k, base] + [base + V(o) * k for o in offs]
    P = catmull(pts, 12)

    def R(t):
        return max(0.074 * (1.0 - t) ** 0.45, 0.017) * k

    def fn(buf):
        st = []
        n = len(P)
        for i, q in enumerate(P):
            t = i / (n - 1)
            r = R(t)
            st.append({"c": q, "rx": r, "ry": r * 0.92, "w": {"head": 1.0}, "ref": (0, 0, 1),
                       "rot": math.radians(30.0 + 18.0 * t)})
        loft(buf, st, segs=6, cap0="flat", cap1="flat", mat=crystal)
        # 끝: 깎은 결정 끝 (육각뿔)
        cE, TE = dc.path_at(P, 1.0)
        loft(buf, [{"c": cE, "rx": R(1.0), "ry": R(1.0) * 0.92, "w": {"head": 1.0}, "ref": (0, 0, 1),
                    "rot": math.radians(48.0)},
                   {"c": cE + TE * 0.020 * k, "rx": 0.0008 * k, "ry": 0.0008 * k, "w": {"head": 1.0}, "ref": (0, 0, 1),
                    "rot": math.radians(48.0)}], segs=6, cap0="flat", cap1="flat", mat=crystal_d)
        # 깎은 면 하이라이트: 굵은 쪽 바깥 면에 덧댄 얇은 결정 판 몇 장 (밝은/어두운 면이 엇갈려 다면체로 읽힘)
        for t, mat in ((0.22, crystal_d), (0.42, crystal_d), (0.62, crystal_d)):
            c, T = dc.path_at(P, t)
            r = R(t)
            out = V((s, 0.2, 0.3)).normalized()
            out = (out - T * out.dot(T)).normalized()
            Mx = Matrix.Translation(c + out * r * 0.86) @ frame(out, T)
            c2.prism(buf, c2.diamond_poly(r * 0.9, r * 1.5), 0.0025 * k, Mx, mat=mat, w={"head": 1.0})
    e.part(f"horn_{side}", "head", fn)


for sd in ("L", "R"):
    crystal_horn(sd)


# ---- 티아라: 정수리 위 작은 짙은 회색 관 (띠 + 봉우리 다섯 + 둥근 고리 장식)
def tiara(buf):
    w = {"head": 1.0}
    pts, nrm, ups = [], [], []
    n = 13
    for i in range(n):
        az = lerp(-62.0, 62.0, i / (n - 1))
        el = 54.0 - 6.0 * (abs(az) / 62.0) ** 2
        s_ = h.s_of_el(az, el)
        p, nn = h.path(az, s_, 0.004 * k)
        p2, _ = h.path(az, max(s_ - 0.01 * k, 0.0), 0.004 * k)
        up = (p2 - p)
        up = (up - nn * up.dot(nn)).normalized()
        up = (up + nn * 0.6).normalized()        # 봉우리를 바깥으로 기울여 정면에서 보이게
        pts.append(p)
        nrm.append(nn)
        ups.append(up)
    elf._loop(buf, pts, nrm, ups, 0.012 * k, 0.004 * k, mat=tiara_m, w=w, closed=False)
    for i, hgt in ((2, 0.026), (4, 0.036), (6, 0.054), (8, 0.036), (10, 0.026)):
        p, nn, up = pts[i], nrm[i], ups[i]
        Mx = Matrix.Translation(p + up * 0.004 * k + nn * 0.002 * k) @ frame(nn, up)
        c2.prism(buf, [(-0.008 * k, 0.0), (0.008 * k, 0.0), (0.0, hgt * k)], 0.004 * k, Mx, mat=tiara_m, w=w)
    for i in (3, 5, 7, 9):          # 봉우리 사이 둥근 고리
        p, nn, up = pts[i], nrm[i], ups[i]
        c = p + up * 0.012 * k + nn * 0.002 * k
        side = nn.cross(up).normalized()
        band(buf, c, side, up, 0.006 * k, 0.006 * k, 0.003 * k, 0.0025 * k, segs=8, mat=tiara_m, w=w)


e.part("tiara", "head", tiara)


# ---- 마름모 크리스털 귀걸이 (양쪽)
def earrings(buf):
    w = {"head": 1.0}
    for sd in ("L", "R"):
        eb, et = e._ear_axis(sd)
        hook = eb.lerp(et, 0.30) + V((0, -0.003 * k, -0.012 * k))
        loft(buf, [{"c": hook, "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w},
                   {"c": hook + V((0, 0, -0.010 * k)), "rx": 0.0016 * k, "ry": 0.0016 * k, "w": w}], segs=5,
             cap0="round", cap1="round", mat=tiara_m)
        Mx = Matrix.Translation(hook + V((0, -0.002 * k, -0.030 * k))) @ frame(V((0, -1, 0)), (0, 0, 1))
        c2.prism(buf, c2.diamond_poly(0.016 * k, 0.034 * k), 0.006 * k, Mx @ Matrix.Translation((0, 0.003 * k, 0)),
                 mat=crystal, w=w, chamfer=0.0022 * k)


e.part("earrings", "head", earrings)

# ---- 아이보리 민소매 홀터 원피스: 몸판 + 목의 작은 짙은 회색 깃 + 회색 X 무늬 허리띠 + 옆트임 긴 치마
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(dress, hem=hz - 0.010 * k, collar=None, flare=0.006)


def halter_collar(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.012 * k), (0, 0, 1), (1, 0, 0), 0.050 * k, 0.046 * k, 0.016 * k,
         0.004 * k, segs=14, mat=dress, w=w, taper=-0.04)
    for sg in (1, -1):         # 작은 짙은 회색 깃 두 장 (목 앞에서 아래로 뾰족)
        p, n = e.torso_point(e.torso_top - 0.002 * k, sg * 20, 0.012 * k)
        Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 14), 4, "Y")
        c2.prism(buf, [(-sg * 0.016 * k, 0.008 * k), (sg * 0.012 * k, 0.010 * k), (sg * 0.002 * k, -0.022 * k)],
                 0.004 * k, Mx, mat=collar_m, w=w)


e.part("halter_collar", "body", halter_collar)
# 허리띠: 회색 띠 + 짙은 X 무늬 (엇갈린 줄 한 바퀴)
e.ring(belt_m, "torso", wz - 0.002 * k, h=0.026, th=0.005, off=0.016, name="belt")


def belt_x(buf):
    n = 18
    zc = wz - 0.002 * k
    for i in range(n):
        a0 = 360.0 * i / n
        a1 = 360.0 * (i + 1) / n
        for z0, z1 in ((zc + 0.008 * k, zc - 0.008 * k), (zc - 0.008 * k, zc + 0.008 * k)):
            p0, n0 = e.torso_point(z0, a0, 0.0225 * k)
            p1, n1 = e.torso_point(z1, a1, 0.0225 * k)
            d = (p1 - p0)
            c = (p0 + p1) / 2
            nn = (n0 + n1).normalized()
            Mx = Matrix.Translation(c) @ frame(nn, d.normalized())
            c3.box12(buf, (0.0030 * k, 0.0016 * k, d.length * 1.05), Mx, belt_d, e._torso_wfn(c, 0))


e.part("belt_x", "body", belt_x)

# 긴 치마: 종아리까지, 캐릭터 왼쪽(+X) 앞 옆트임 (허벅지 중간부터 벌어짐)
SLIT = 30.0
skirt = c2.Shell(e, dress, wz + 0.004 * k, 0.150 * k, gap=[(0.0, 1.5), (0.30, 4.0), (0.55, 12.0), (1.0, 20.0)],
                 a_fn=lambda a, u: a + SLIT, off=0.016, th=0.004, skirt=True, rows=9, cols=22,
                 flare=[(0.0, 0.0), (0.35, 0.016), (1.0, 0.052)], cover=True)
skirt.edge_trim(dress_d, width=0.006, th=0.0018, i0=2).hem_trim(dress_d, width=0.008, th=0.002)
skirt.done("dress_skirt")
q0 = e.q
e.q = 0.40   # 치마 속 속바지 (거의 안 보임)
e.pants(dress_d, length=0.10, bag=0.0, blouse=0.0, off=0.006)
e.q = q0

# ---- 용 날개 (회색 막, 짙은 회색 뼈대) + 관절 끝 흰 크리스털 조각
wm = dc.wings(e, span=0.34, height=0.34, mem=mem, bone=wbone, angle=138.0, sweep=18.0, raise_=12.0,
              z=e.chest_z + 0.070 * k)


def wing_crystals(buf):
    L, H = 0.34 * k, 0.34 * k
    for sd, Mw in wm.items():
        # 손목(W)과 바깥 손가락 끝(F1)
        for (x, z), sc in (((0.58, 0.96), 1.0), ((1.00, 0.62), 0.75), ((0.30, 0.52), 0.6)):
            c = Mw @ V((x * L, 0.0, z * H))
            up = (Mw.to_3x3() @ V((0.25, 0.0, 1.0))).normalized()
            out = (Mw.to_3x3() @ V((1.0, 0.0, 0.0))).normalized()
            bone_name = f"wing_{sd}_02" if sc == 1.0 else (f"wing_{sd}_f1" if sc == 0.75 else f"wing_{sd}_01")
            w = {bone_name: 1.0}
            for j, (dx, hh, rr) in enumerate(((0.0, 0.034, 0.010), (0.008, 0.022, 0.007))):
                b0 = c + out * dx * k * sc
                st = [{"c": b0, "rx": rr * k * sc, "ry": rr * k * sc, "w": w, "rot": math.radians(30)},
                      {"c": b0 + up * hh * 0.45 * k * sc, "rx": rr * 1.15 * k * sc, "ry": rr * 1.15 * k * sc, "w": w,
                       "rot": math.radians(30)},
                      {"c": b0 + up * hh * k * sc, "rx": 0.0008 * k, "ry": 0.0008 * k, "w": w, "rot": 0.0}]
                loft(buf, st, segs=5, cap0="flat", cap1="flat", mat=crystal if j == 0 else crystal_d)


e.part("wing_crystals", "body", wing_crystals)

# ---- 꼬리: 엉덩이 뒤에서 아래로 늘어졌다가 캐릭터 오른쪽 옆으로 말려 올라간다
bz = hz + 0.030 * k
bp, bn = e.torso_point(bz, 180.0, -0.012 * k)
ctrl = [bp,
        bp + V((0.0, 0.080 * k, -0.070 * k)),
        V((-0.030 * k, bp.y + 0.160 * k, 0.150 * k)),
        V((-0.110 * k, bp.y + 0.200 * k, 0.050 * k)),
        V((-0.210 * k, bp.y + 0.170 * k, 0.034 * k)),
        V((-0.290 * k, bp.y + 0.100 * k, 0.050 * k)),
        V((-0.320 * k, bp.y + 0.030 * k, 0.090 * k))]
dc.tail(e, ctrl, 0.050, mat=tail_m, belly=tail_b, bones=4, segs=10, n=20)

e.finalize()


# ---- 다이아몬드 (별도 노드 gem): 왼손에 든 큰 다이아몬드 (브릴리언트 컷을 단순화한 팔각 두 뿔)
def gem_geo():
    b = Buf()
    w = {}
    r, ht, hb = 0.030 * k, 0.012 * k, 0.034 * k
    n = 8
    top = [b.vert(V((math.cos(2 * math.pi * i / n) * r * 0.62, math.sin(2 * math.pi * i / n) * r * 0.62, ht)), w)
           for i in range(n)]
    gir = [b.vert(V((math.cos(2 * math.pi * (i + 0.5) / n) * r, math.sin(2 * math.pi * (i + 0.5) / n) * r, 0.0)), w)
           for i in range(n)]
    tc = b.vert(V((0, 0, ht)), w)
    bot = b.vert(V((0, 0, -hb)), w)
    for i in range(n):
        j = (i + 1) % n
        b.face((tc, top[i], top[j]), crystal)
        b.face((top[i], gir[i], top[j]), crystal_d)
        b.face((top[j], gir[i], gir[j]), crystal)
        b.face((gir[i], bot, gir[j]), crystal_d if i % 2 else crystal)
    ob = b.obj("daya_gem_geo", smooth=False)
    return ob


gem = gem_geo()
sock = bpy.data.objects["socket_hand_L"]
Mw = Matrix.Translation(sock.matrix_world.translation + V((0.0, -0.030 * k, 0.020 * k))) @ \
    Matrix.Rotation(math.radians(15), 4, "X")
c3.socket_prop(e, gem, "socket_hand_L", Mw, name="gem", outline=0.0025)


# ---- 회색 대검 (별도 노드 sword): 등에 비스듬히. 무기 규약: 원점 = 파지점, 칼날 +Y, 칼등 +Z
def sword_geo():
    S = k
    b = Buf()
    w = {}
    blade_m = M_("dy_blade", "#a8a6b0")
    blade_d = M_("dy_blade_d", "#7c7987")
    grip = M_("dy_grip", "#4e4a57")
    # 칼날: 넓고 긴 판 + 가운데 홈 + 끝 뾰족
    pts = [(0.034, 0.10), (0.036, 0.62), (0.0, 0.74), (-0.036, 0.62), (-0.034, 0.10)]
    poly = [(x * S, y * S) for x, y in pts]
    bl = c2.poly_object("daya_sword_blade", poly, 0.010 * S,
                        Matrix.Translation((0, 0, -0.005 * S)) @
                        Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))), blade_m, bevel=0.002 * S)
    # 위 행렬: 다각형 (x, z) → 로컬 (x, y=z)로 눕히고 두께(+Z)를 가운데로
    c3.box12(b, (0.008 * S, 0.50 * S, 0.0125 * S), Matrix.Translation(V((0, 0.36 * S, 0.0))), blade_d, w)
    # 코등이 (각진 날개) + 손잡이 + 폼멜
    c3.box12(b, (0.150 * S, 0.026 * S, 0.026 * S), Matrix.Translation(V((0, 0.09 * S, 0.0))), blade_d, w)
    for sg in (1, -1):
        c2.prism(b, [(sg * 0.075 * S, 0.0), (sg * 0.100 * S, 0.020 * S), (sg * 0.075 * S, 0.026 * S)], 0.024 * S,
                 Matrix.Translation(V((0, 0.077 * S, -0.012 * S))) @ Matrix.Rotation(math.radians(90), 4, "X"),
                 mat=blade_d, w=w)
    loft(b, [{"c": V((0, -0.08 * S, 0.0)), "rx": 0.014 * S, "ry": 0.014 * S, "w": w},
             {"c": V((0, 0.08 * S, 0.0)), "rx": 0.014 * S, "ry": 0.014 * S, "w": w}], segs=6, cap0="flat",
         cap1="flat", mat=grip)
    for yy in (-0.05, -0.01, 0.03):
        band(b, V((0, yy * S, 0.0)), (0, 1, 0), (1, 0, 0), 0.0155 * S, 0.0155 * S, 0.008 * S, 0.002 * S,
             segs=6, mat=blade_d, w=w)
    c2.prism(b, c2.diamond_poly(0.040 * S, 0.040 * S), 0.022 * S,
             Matrix.Translation(V((0, -0.100 * S, 0.011 * S))) @ Matrix.Rotation(math.radians(90), 4, "X"),
             mat=blade_d, w=w)
    ob = b.obj("daya_sword_core", angle=35.0)
    cb.apply_modifiers(bl)
    return cb.join([ob, bl], "daya_sword_src")


sw = sword_geo()
sock = bpy.data.objects["socket_back"]
bpy.context.view_layer.update()
d = V((-0.55, 0.10, 0.83)).normalized()           # 칼끝: 캐릭터 오른쪽 위 (등 뒤에 비스듬히)
up = V((0, 1, 0))
up = (up - d * up.dot(d)).normalized()
X = d.cross(up).normalized()
Mw = Matrix((X, d, up)).transposed().to_4x4()
Mw.translation = sock.matrix_world.translation + V((0.040 * k, 0.050 * k, -0.120 * k))
c3.socket_prop(e, sw, "socket_back", Mw, name="sword", outline=0.003,
               props={"blade_tip": "0,%.3f,0" % (0.74 * k)})

e.export("characters/daya.glb")
