"""시온 (시온 더 다크불릿): 영원살이 자매의 둘째, 표면상 '어둠의 유령'. 정령산 감시초소를 맡았고, 3막에서
엘레나의 설명을 듣고 웜홀 저격으로 흑뉴아의 반물질 중성자탄을 아공간으로 보낸다.

원작 시온(트릭컬 리바이브, '검은 마탄의 사수')의 복장을 바탕으로 한 카메오 모델.
- 유지한 식별 요소: 짙은 남색 단발과 일자 앞머리, 오른쪽 높이 묶은 긴 사이드 포니테일(파란 리본, 끝이 파랗게
  물듦), 오른쪽 옆머리에 얼굴을 바깥으로 돌려 매단 검은 드래곤 해골 가면(모자처럼 쓰지 않는다. 뿔 두 개, 눈구멍,
  이빨 난 주둥이가 앞 아래로. 이마 끈 뒤끝을 사이드 포니테일의 파란 리본이 같이 묶는다), 오른눈 분홍빛 붉은 컬러 렌즈 + 왼눈 하늘색
  (오드아이처럼 보이는 렌즈), 중2병 미소, 짙은 회색 고스 코트 드레스(별 무늬 밑단, 큰 소맷단), 흰 깃과 파란
  리본 + 은색 별 브로치, 파란 타이츠, 청회색 신, 오른 허벅지 끈, 검은 대물 저격총 '더 엑시트'.
- 재해석: 3막 통신 복구 장면에 맞춰 왼쪽 귀에 무전 이어피스를 더했다. 저격총 '더 엑시트'(D.EXIT, 엘레나가 지구에서
  훔쳐 온 수십 년 묵은 미군제 대물 저격총)는 원작 옆모습을 따라 다시 짰고 별도 노드 sion_rifle이다(무기 규약: 원점 =
  오른손 파지점, 총구 +Y). 기본은 socket_back에 납작하게 비스듬히 메고 있고, 쏠 때는 socket_hand_R의 자식으로 옮기고
  로컬 변환을 0으로. 제퇴기 상자·가늠쇠 단·드러난 총열은 자식 노드 sion_rifle_barrel(같은 원점)로 나눠 쏠 때 리시버 안으로
  주퇴했다가 복좌하고, 접힌 양각대 다리는 자식 노드 sion_rifle_bipod(엎드려쏴에서는 코드가 같은 마운트에서 펼친다).
- 체형: 유령·엘다인이라 엘프의 긴 귀가 없다. 키트에 둥근 귀가 없어서 귀를 아주 짧게(ear_len 0.022) 줄이고
  옆머리로 덮었다.
- 표정: 키트 5종 + chuuni(이를 드러낸 중2병 미소), aim(조준: 두 눈을 가늘게 좁힘), panic(허당 당황),
  pout(삐침) + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/sion.py
npm run shot -- characters/sion.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("sion", height=1.20, head=0.45, leg=1.02, chest=0.30, bust=0.75, segs=0.76, hand_q=0.6, cheek=0.10,
            ear_len=0.022, ear_width=0.046, ear_angle=0.0, ear_sweep=14.0)
k = e.k

# ---- 팔레트 (원작 실측: 머리 #3a3a58, 코트 #4c4b55, 리본 #2f5fb8, 타이츠 #3f6fc4, 신 #5d7f86, 렌즈 #ff4f7a)
dress = M_("si_dress", "#4d4c57")
dress_d = M_("si_dress_d", "#393842")
star_m = M_("si_star", "#8d8c9c")
white = M_("si_white", "#f1eff2")
blue = M_("si_blue", "#2f62bf")
tights = M_("si_tights", "#3e6cc4")
shoe = M_("si_shoe", "#5b7d86")
sole = M_("si_sole", "#33474d")
strap_m = M_("si_strap", "#26242c")
silver = M_("si_silver", "#d4d6e2")
skull = M_("si_skull", "#4b4e58")
skull_d = M_("si_skull_d", "#202027")
horn = M_("si_horn", "#2c3756")      # 가면 뿔은 원작처럼 푸른 기가 도는 검정
radio = M_("si_radio", "#2b2a31")

# ---- 얼굴: 기본은 여유로운 중2병 미소. 오른눈(-X)은 붉은 컬러 렌즈, 왼눈은 하늘색
e.face(eye_color="#8fc4ec", iris_dark="#3c6fa8", iris_light="#dff2ff", pupil="#1d2e48",
       lash="#24223a", brow="#33324a", blush="#f7a2a6", blush_size=1.1,
       base={"eye": {"top": 0.024, "ktop": 3.6, "tilt_out": 0.002},
             "brow": {"dz": 0.062, "ang": -6.0, "arch": 0.002},
             "mouth": {"w": 0.024, "curve": 0.0050, "open": 0.0020, "top_arch": -0.0006}},
       expr={
           # 당황 (허당): 동그래진 눈, 작은 동공, 물결 입
           "panic": {"eye": {"top": 0.036, "ktop": 2.3, "bot": 0.058},
                     "iris": {"pupil": 0.55, "rx": 0.025, "ry": 0.033},
                     "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                     "mouth": {"w": 0.026, "curve": -0.0030, "open": 0.0100, "wave": 0.0022}},
           # 삐침: 눈을 가늘게, 입을 삐죽
           "pout": {"eye": {"top": 0.016, "tilt_in": -0.004, "ktop": 4.0},
                    "brow": {"ang": 10.0, "dz": 0.060},
                    "mouth": {"w": 0.014, "curve": -0.0030, "open": 0.0020, "top_arch": 0.0020}},
       })
# 중2병 미소: 두 눈 크기는 같게 (한쪽만 크게 뜨면 짝눈으로 보인다 · 2026-11-02 사용자 지적). 입과 눈썹으로만 비튼다
c2.face_expr(e, "chuuni",
             both={"mouth": {"w": 0.032, "curve": 0.0075, "open": 0.0080, "top_arch": -0.0015},
                   "eye": {"top": 0.022, "ktop": 3.4}, "iris": {"pupil": 0.70}},
             R={"brow": {"dz": 0.068, "ang": -6.0}},
             L={"brow": {"dz": 0.062, "ang": -12.0}},
             corner=(0.0035, 0.0085), mouth_dx=-0.0020 * k)
# 조준: 두 눈을 다 뜬 채 가늘게 좁힌다 (한쪽 눈을 감으면 애꾸눈처럼 보인다 · 2026-11-02 사용자 지적)
c2.face_expr(e, "aim",
             both={"mouth": {"w": 0.016, "curve": 0.0005}},
             L={"eye": {"top": 0.022, "tilt_in": -0.008}, "iris": {"pupil": 0.75},
                "brow": {"dz": 0.056, "ang": -12.0}},
             R={"eye": {"top": 0.022, "tilt_in": -0.008}, "iris": {"pupil": 0.75},
                "brow": {"dz": 0.058, "ang": -14.0}})
# 오른눈 컬러 렌즈: 얼굴 정점색에서 오른쪽(-X) 홍채 색만 바꾼다 (셰이프 키와 무관)
c2.recolor_face(e, lambda c: c.x < 0, {"#8fc4ec": "#ff5c86", "#3c6fa8": "#b01e48", "#dff2ff": "#ffd2de",
                                       "#1d2e48": "#4a0a1e"})

# ---- 머리: 짙은 남색 단발, 일자 앞머리, 턱까지 오는 옆머리, 오른쪽 높은 사이드 포니테일
HAIR = "#3b3a5a"
HAIR_TIP = "#4a7fd0"


def sion_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.6
        lk["free"] *= 0.55


h = c2.hair(e, HAIR, dark="#25243c", light="#7473a0", lock_fn=c2.lock_edit(sion_locks), volume=1.06)
h.cap(front=30, side=-6, back=-48, part=0)
h.bangs(n=7, spread=60, tip_el=2, jag=0.10, curl=0.7, seed=7.0)
h.sides(length=0.06, width=0.088, curl=0.2)
h.back(length=0.03, n=7, spread=94)
h.shine(el=50, spread=68, size=1.0)
o = h.vol
root, rn = h.path(-122.0, h.s_of_el(-122.0, 24.0), -o * 0.2)
sz, cz, wz, hz = e.shoulder_z, e.chest_z, e.waist_z, e.hipj_z
out = V((rn.x, rn.y, 0)).normalized()
ctrl = [root,
        root + out * 0.050 * k + V((0, 0, 0.020 * k)),
        root + out * 0.105 * k + V((0, 0.020 * k, -0.050 * k)),
        V((-0.230 * k, 0.140 * k, sz - 0.020 * k)),
        V((-0.250 * k, 0.150 * k, cz - 0.060 * k)),
        V((-0.270 * k, 0.140 * k, hz)),
        V((-0.300 * k, 0.120 * k, e.knee_z + 0.020 * k)),
        V((-0.270 * k, 0.090 * k, 0.110 * k))]
tl = c2.Tail(h, "hair_tail_R", ctrl, 0.090 * k, 0.055 * k, bones=3, parent="head", t_hold=0.55, root_w=0.85,
             clumps=((0.30, 0.55, 0.90), (-0.28, 0.55, 0.84)))
tl.tie(blue, t=0.03, size=1.0, h_=0.022, th=0.008)
c0, T0 = tl.at(0.03)


def ribbon(buf):
    w = tl.w_at(0.03)
    side = V((0, 0, 1)).cross(out).normalized()
    M = Matrix.Translation(c0 + out * 0.010 * k + V((0, 0, 0.018 * k))) @ elf.frame(out, V((0, 0, 1)))
    c2.bow_geo(buf, M, 0.090 * k, blue, w=w, tails=0.9, segs=8)
    _ = side


e.part("ribbon", "head", ribbon)

# ---- 검은 드래곤 해골 가면: 모자처럼 쓰지 않고, 얼굴을 바깥(오른쪽)으로 돌려 오른쪽 옆머리에 매단다 (원작 카드·소개 그림·
# 엎드려 겨눈 옆모습). 정수리는 비고, 가면 이마(뿔 두 개)가 정수리 오른쪽 가장자리, 눈구멍이 관자놀이 위, 이빨 난 주둥이가
# 아래 앞(오른눈 바깥 위)을 향한다. 이마를 가로지르는 끈이 뒤쪽 둥근 징에서 끝나고, 바로 뒤의 파란 리본이 가면 끈과
# 사이드 포니테일을 같이 묶는다. 가면은 머리 덩어리 바깥 면을 따라 휜 판이라 머리카락을 파고들지 않는다
MK_AZ, MK_EL = -72.0, 36.0      # 가면 중심 (오른쪽 옆머리, 관자놀이 위)
MK_AU, MK_AV = 35.0, 35.0       # 가로·세로 반폭 (머리 중심에서 본 각도)
MK_TILT = 20.0                  # 가면 위쪽(뿔)이 뒤로 기울고 주둥이가 앞 아래를 본다
MK_LIFT, MK_BULGE, MK_TH = 0.006, 0.022, 0.007


def _mk_frame():
    a, b = math.radians(MK_AZ), math.radians(MK_EL)
    D = V((math.cos(b) * math.sin(a), -math.cos(b) * math.cos(a), math.sin(b)))
    tu = V((-math.sin(b) * math.sin(a), math.sin(b) * math.cos(a), math.cos(b)))
    tf = V((math.cos(a), math.sin(a), 0.0))
    t = math.radians(MK_TILT)
    Um = tf * math.cos(t) + tu * math.sin(t)       # 가면 가로 (+ = 얼굴 앞쪽)
    Vm = tu * math.cos(t) - tf * math.sin(t)       # 가면 위 (뿔 쪽)
    return D, Um, Vm


MK_D, MK_U, MK_V = _mk_frame()


def mk_w(v):
    """가면 윤곽: 줄 v(-1 = 이빨 끝, +1 = 이마 위)의 가로 반폭 (u 비율)."""
    return lerp(lerp(0.46, 0.92, smoothstep(-1.0, 0.1, v)), 0.80, smoothstep(0.55, 1.0, v))


def mk_pt(u, v, lift=0.0):
    """가면 면의 점·법선. u, v는 -1~1 (u는 윤곽 비율이 아닌 절대값)."""
    d = (MK_D + MK_U * math.tan(math.radians(u * MK_AU)) + MK_V * math.tan(math.radians(v * MK_AV))).normalized()
    el = math.degrees(math.asin(max(-1.0, min(1.0, d.z))))
    az = math.degrees(math.atan2(d.x, -d.y))
    p, n = h._surf_n(az, el)
    bul = MK_BULGE * max(0.0, 1.0 - u * u) * max(0.0, 1.0 - ((v - 0.05) / 1.15) ** 2)
    return p + n * (h._volume(az, el) + (MK_LIFT + bul + lift) * k), n


def dragon_mask(buf):
    w = {"head": 1.0}
    NU, NV = 12, 11
    O, I = [], []
    for j in range(NV):
        v = lerp(-1.0, 1.0, j / (NV - 1))
        ro, ri = [], []
        for i in range(NU):
            u = lerp(-1.0, 1.0, i / (NU - 1)) * mk_w(v)
            p, n = mk_pt(u, v)
            ro.append(buf.vert(p, w))
            ri.append(buf.vert(p - n * MK_TH * k, w))
        O.append(ro)
        I.append(ri)
    for j in range(NV - 1):
        for i in range(NU - 1):
            buf.face((O[j][i], O[j][i + 1], O[j + 1][i + 1], O[j + 1][i]), skull)
            buf.face((I[j][i], I[j + 1][i], I[j + 1][i + 1], I[j][i + 1]), skull_d)
    # 테두리 (바깥에서 반시계로 돈다): 바깥 면과 안쪽 면을 잇는 두께
    loop = [(0, i) for i in range(NU)] + [(j, NU - 1) for j in range(1, NV)] + \
           [(NV - 1, i) for i in range(NU - 2, -1, -1)] + [(j, 0) for j in range(NV - 2, 0, -1)]
    for a_, b_ in zip(loop, loop[1:] + loop[:1]):
        buf.face((O[b_[0]][b_[1]], O[a_[0]][a_[1]], I[a_[0]][a_[1]], I[b_[0]][b_[1]]), skull)

    def fr(u, v, lift=0.0):
        p, n = mk_pt(u, v, lift)
        up = (MK_V - n * MK_V.dot(n)).normalized()
        return p, n, up

    # 눈구멍 두 개 (아몬드꼴, 바깥 끝이 살짝 처진다) + 눈썹뼈
    for sg in (1, -1):
        p, n, up = fr(sg * 0.44, 0.30, 0.0005)
        tilt = Matrix.Rotation(math.radians(-sg * 10), 3, n)
        disc(buf, p, n, tilt @ up, 0.040 * k, 0.025 * k, 0.0015 * k, segs=16, mat=skull_d, w=w, p=1.7)
        p2, n2, up2 = fr(sg * 0.44, 0.56, 0.001)
        sd = up2.cross(n2).normalized()
        c2.ellipsoid(buf, p2, sd, up2, n2, 0.034 * k, 0.008 * k, 0.008 * k, segs=8, rings=5, mat=skull, w=w)
    # 이마를 가로지르는 끈 (두 줄 선) → 뒤쪽 끝(u = -1)의 둥근 징. 리본이 그 뒤에서 묶는다
    pts, nrm, ups = [], [], []
    for i in range(13):
        u = lerp(-1.0, 1.0, i / 12) * mk_w(0.74) * 1.02
        p, n = mk_pt(u, 0.74, 0.0005)
        p2, _ = mk_pt(u, 0.76, 0.0005)
        up = (p2 - p)
        up = (up - n * up.dot(n)).normalized()
        pts.append(p)
        nrm.append(n)
        ups.append(up)
    elf._loop(buf, pts, nrm, ups, 0.013 * k, 0.003 * k, mat=strap_m, w=w, closed=False)
    p, n, up = fr(-mk_w(0.74) * 0.96, 0.74, 0.003)
    disc(buf, p, n, up, 0.015 * k, 0.015 * k, 0.003 * k, segs=12, mat=star_m, w=w)
    disc(buf, p + n * 0.003 * k, n, up, 0.008 * k, 0.008 * k, 0.0015 * k, segs=10, mat=skull_d, w=w)
    # 주둥이: 눈구멍 사이 아래에서 앞 아래로 불룩 (콧등 → 콧구멍 → 윗니)
    st = []
    for i in range(7):
        t = i / 6
        v = lerp(0.02, -0.80, t)
        p, n = mk_pt(0.0, v)
        st.append({"c": p + n * lerp(-0.006, 0.006, smoothstep(0.0, 0.7, t)) * k,
                   "rx": lerp(0.020, 0.050, smoothstep(0.0, 0.7, t)) * k, "ry": lerp(0.008, 0.018, t) * k,
                   "w": w, "ref": tuple((MK_V.cross(n)).normalized()), "p": 2.0})
    loft(buf, st, segs=12, cap0="round", cap1="round", mat=skull, cap_len0=0.012 * k, cap_len1=0.012 * k)
    for sg in (1, -1):      # 콧구멍
        p, n, up = fr(sg * 0.17, -0.58, 0.020)
        disc(buf, p, n, up, 0.008 * k, 0.005 * k, 0.0015 * k, segs=8, mat=skull_d, w=w)
    # 윗니: 아래 가장자리를 따라 아래로 난 들쭉날쭉한 이빨
    for i in range(7):
        u = lerp(-0.92, 0.92, i / 6) * mk_w(-1.0)
        p, n, up = fr(u, -0.98, -MK_TH * 0.5)
        ln = (0.016 if i % 2 == 0 else 0.011) * k
        c2.prism(buf, [(-0.0062 * k, 0.004 * k), (0.0062 * k, 0.004 * k), (0.0, -ln)], MK_TH * k,
                 Matrix.Translation(p + n * MK_TH * k * 0.5) @ elf.frame(n, up), mat=skull, w=w)
    # 뿔 두 개: 이마 위 양쪽 모서리에서 위로 솟아 뒤로 휜다
    for sg in (1, -1):
        b0, n0, up0 = fr(sg * 0.50, 0.84, -0.004)
        back = -MK_U
        pts = [b0, b0 + up0 * 0.042 * k + n0 * 0.012 * k,
               b0 + up0 * 0.084 * k + n0 * 0.012 * k + back * 0.016 * k,
               b0 + up0 * 0.108 * k + back * 0.044 * k + n0 * 0.004 * k]
        Pp = elf.catmull(pts, 9)
        st = [{"c": q, "rx": lerp(0.028, 0.003, i / 8) * k, "ry": lerp(0.020, 0.003, i / 8) * k, "w": w,
               "ref": tuple(MK_U)} for i, q in enumerate(Pp)]
        loft(buf, st, segs=8, cap0="flat", cap1="round", mat=horn)


e.part("dragon_mask", "head", dragon_mask)

# 무전 이어피스 (왼쪽 귀 자리, 3막 통신 복구)
eb, et = e._ear_axis("L")
e.part("earpiece", "head", lambda buf: (rbox(buf, (0.020 * k, 0.018 * k, 0.026 * k),
                                             Matrix.Translation(eb + V((0.016 * k, -0.004 * k, -0.004 * k))),
                                             mat=radio, w={"head": 1.0}, r=0.45, segs=1),
                                        loft(buf, [{"c": eb + V((0.014 * k, -0.012 * k, -0.012 * k)),
                                                    "rx": 0.0018 * k, "ry": 0.0018 * k, "w": {"head": 1.0}},
                                                   {"c": eb + V((-0.004 * k, -0.050 * k, -0.040 * k)),
                                                    "rx": 0.0018 * k, "ry": 0.0018 * k, "w": {"head": 1.0}}],
                                             segs=6, cap0="round", cap1="round", mat=radio)))

# ---- 옷: 짙은 회색 고스 코트 드레스, 흰 깃 + 파란 리본 + 은색 별 브로치
e.shirt(dress, hem=hz + 0.010 * k, collar=None, flare=0.010, placket=dress_d)
e.sleeves(dress, length=0.95, off=0.012, flare=0.030, puff=0.006, cuff=(dress_d, 0.030, 0.005))


def collar_bow(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.012 * k), (0, 0, 1), (1, 0, 0), 0.055 * k, 0.051 * k, 0.026 * k,
         0.005 * k, segs=16, mat=white, w=w, taper=-0.03)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.002 * k, sg * 30, 0.016 * k)
        M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 20), 4, "Y")
        c2.prism(buf, [(-sg * 0.026 * k, 0.014 * k), (sg * 0.016 * k, 0.014 * k), (sg * 0.010 * k, -0.030 * k),
                       (-sg * 0.016 * k, -0.018 * k)], 0.004 * k, M, mat=white, w=w)
    p, n = e.torso_point(e.torso_top - 0.018 * k, 0, 0.022 * k)
    M = Matrix.Translation(p) @ elf.frame(n, (0, 0, 1))
    c2.bow_geo(buf, M, 0.070 * k, blue, w=w, tails=0.8, segs=8)
    c2.prism(buf, c2.star_poly(0.014 * k, 0.006 * k, n=4, rot=90), 0.004 * k,
             M @ Matrix.Translation((0, -0.012 * k, 0.002 * k)), mat=silver, w=w, chamfer=0.0015 * k)


e.part("collar_bow", "body", collar_bow)
e.belt(strap_m, z=wz - 0.004 * k, h=0.018, buckle=silver, buckle_size=(0.024, 0.020))
q0 = e.q
e.q = 0.45    # 치마 속 속바지
e.pants(dress_d, length=0.06, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
sk = c2.Shell(e, dress, wz - 0.004 * k, 0.215 * k, off=0.016, th=0.004, skirt=True, cols=28, rows=7,
              flare=[(0.0, 0.0), (0.4, 0.024), (1.0, 0.070)], ruffle=(0.010, 7, 0.25),
              drop=[(0.0, 0.0), (1.0, 0.040)])
sk.hem_trim(dress_d, width=0.012, th=0.002)
sk.done("skirt", angle=40.0)


def skirt_stars(buf):
    for i in range(10):
        a = 18 + 36 * i
        u = 0.80 if i % 2 == 0 else 0.62
        Mx = sk.frame_at(u, a, 0.003 * k)
        w = c2.skirt_w(e, Mx.to_translation())
        s_ = 0.016 if i % 2 == 0 else 0.012
        c2.prism(buf, c2.star_poly(s_ * k, s_ * 0.36 * k, n=4, rot=90), 0.002 * k, Mx, mat=star_m, w=w)


e.part("skirt_stars", "body", skirt_stars)
for sd in ("L", "R"):
    a = e.anchor((f"arm_{sd}", 0.88, 90 if sd == "L" else -90, 0.046 * k))
    e.part(f"cuff_star_{sd}", "arms", lambda buf, a=a: c2.prism(buf, c2.star_poly(0.011 * k, 0.004 * k, n=4, rot=90),
                                                                 0.002 * k, a.matrix(), mat=star_m, w=a.w))

# ---- 파란 타이츠 + 청회색 신 + 오른 허벅지 끈
for sd in ("L", "R"):
    c2.leg_tube(e, tights, sd, 0.10, 0.99, off=0.003, name=f"tights_{sd}")
e.ring(strap_m, "leg_R", 0.22, h=0.016, th=0.004, off=0.008, name="thigh_strap")
e.gear("thigh_buckle", ("leg_R", 0.22, -60, 0.013 * k),
       lambda buf, Mx, w: rbox(buf, (0.020 * k, 0.005 * k, 0.020 * k), Mx, mat=silver, w=w, r=0.3, segs=1))
e.boots(shoe, top=0.93, sole=(sole, 0.014), toe=0.004, off=0.010)
# 총 멜빵: 왼쪽 어깨 앞 → 가슴 → 오른쪽 허리 → 등
e.strap(strap_m, [("torso", sz + 0.012 * k, 52, 0.016 * k), ("torso", cz + 0.010 * k, 18, 0.020 * k),
                  ("torso", wz + 0.020 * k, -40, 0.022 * k), ("torso", wz + 0.010 * k, -120, 0.022 * k),
                  ("torso", cz, 160, 0.020 * k)], width=0.016, th=0.004, name="sling")

e.finalize()

# ---- 머리끝 파랗게 (사이드 포니테일)
for node, base, tip in (("hair", HAIR, HAIR_TIP),):
    ob = e.result.get(node)
    tz = min(v.co.z for v in ob.data.vertices)
    c2.vc_gradient(ob, base, [(tz + 0.02 * k, tip), (tz + 0.36 * k, base)], pred=lambda co: co.x < -0.12 * k)

# ---- 대물 저격총 '더 엑시트' D.EXIT (별도 노드): 원점 = 오른손 파지점, 총구 +Y, 위 +Z (m, 엘프 체격 그대로)
# [원작] 옆모습(엎드려 겨눔)과 카드를 따라 총구 → 개머리 순서로 다시 짰다 (docs/art/characters-cameo2.md '더 엑시트'):
#   총구 쪽 1/4을 차지하는 굵은 네모 제퇴기 상자(밝은 끝 마개, 옆면 세로 홈 셋, 앞뒤 가장자리의 가로 홈) → 그 뒤 밝은 단과 그 위
#   세모꼴 가늠쇠 날개 → 잠깐 드러난 총열(가운데 가로 홈) → 납작한 윗면의 긴 상자 리시버(앞쪽 아래 사선 홈 셋, 뒤쪽 볼트 판과 둥근
#   손잡이) → 리시버 위 뒤쪽 두 고리 위의 큰 조준경(큰 대물렌즈, 가운데 다이얼, 접안부) → 손 앞의 큰 상자 탄창 → 권총 손잡이 없이
#   방아쇠가 개머리 바로 앞(엘프의 짧은 팔에 맞춘 개조) → 크고 각진 개머리(뺨받침, 안쪽 밝은 판, 개머리판).
#   양각대는 리시버 앞쪽 밑(아래 레일 끝) 마운트에 붙어 총구 쪽으로 접혀 있고 다리 끝은 원뿔이다.
#   색은 짙은 건메탈 한 톤 + 밝은 회색 면. 붉은 줄은 원작에 없어 뺐다. 길이는 시온 키(1.26 m)보다 긴 1.51 m.
# 노드: sion_rifle (고정: 리시버·조준경·탄창·방아쇠·개머리·양각대 마운트) ─ sion_rifle_barrel (반동식 쇼트 리코일로 주퇴복좌하는
#   제퇴기 상자·가늠쇠 단·드러난 총열, 같은 원점) ─ sion_rifle_bipod (접힌 양각대 다리 둘, 같은 원점: 엎드려쏴에서는 숨기고
#   m8/stage.ts가 같은 모양의 다리를 같은 마운트에서 펼친다). 아래 치수는 m8/stage.ts의 MUZZLE·BRAKE·SCOPE_EYE·SUPPORT·BOLT·BIPOD와 맞춘다
gun = Buf()
bar = Buf()
bip = Buf()
gk = M_("si_gun", "#50515a")       # 건메탈 (원작 실측 #50515a)
gl = M_("si_gun_l", "#666873")     # 밝은 면 (끝 마개·가늠쇠 단·드러난 총열·볼트 판·뺨받침)
gd = M_("si_gun_d", "#393a42")     # 홈·고무 개머리판
lens = M_("si_lens", "#2b3242")


def box(sz_, at, m, r=0.1, buf=None):
    rbox(buf if buf is not None else gun, sz_, Matrix.Translation(at), mat=m, w={}, r=r, segs=1)


def span(y0, y1, z0, z1, w, m, r=0.1, buf=None, x=0.0):
    """y0..y1, z0..z1 상자 (폭 w, 가운데 x)"""
    box((w, abs(y1 - y0), abs(z1 - z0)), (x, (y0 + y1) / 2, (z0 + z1) / 2), m, r=r, buf=buf)


def side_prism(buf, pts, x0, x1, m):
    """옆에서 본 볼록 다각형 (y, z)을 x0..x1로 민 기둥 (가늠쇠 날개·사선 홈)"""
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = list(reversed(pts))
    a = [buf.vert(V((x0, y, z)), {}) for (y, z) in pts]
    b = [buf.vert(V((x1, y, z)), {}) for (y, z) in pts]
    buf.face(tuple(reversed(a)), m)
    buf.face(tuple(b), m)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        buf.face((a[i], a[j], b[j], b[i]), m)


def rod(buf, y0, y1, r0, r1, m, x=0.0, z=0.0, segs=12, cap0="flat", cap1="flat"):
    """y축 둥근 관 (조준경·양각대 다리)"""
    loft(buf, [{"c": V((x, y0, z)), "rx": r0, "ry": r0, "w": {}}, {"c": V((x, y1, z)), "rx": r1, "ry": r1, "w": {}}],
         segs=segs, cap0=cap0, cap1=cap1, mat=m)


def xrod(buf, x0, x1, y, z, r, m, segs=10):
    """x축 둥근 관 (다이얼·핀)"""
    loft(buf, [{"c": V((x0, y, z)), "rx": r, "ry": r, "w": {}, "ref": V((0, 1, 0))},
               {"c": V((x1, y, z)), "rx": r, "ry": r, "w": {}, "ref": V((0, 1, 0))}], segs=segs, cap0="flat", cap1="flat",
         mat=m, ref=(0, 1, 0))


SIDES = (1, -1)
# -- 움직이는 쪽 (sion_rifle_barrel): 제퇴기 상자 · 끝 마개 · 가늠쇠 단 · 드러난 총열
MZ_Y, BORE_Z = 1.128, 0.111
span(0.738, 1.052, 0.052, 0.171, 0.074, gk, buf=bar)                      # 제퇴기 상자 (총구 쪽 1/4)
span(1.050, MZ_Y, 0.045, 0.176, 0.080, gl, r=0.12, buf=bar)               # 끝 마개
disc(bar, (0, MZ_Y + 0.0006, BORE_Z), (0, 1, 0), (0, 0, 1), 0.013, 0.013, 0.001, segs=12, mat=gd)   # 총구 구멍
for sg in SIDES:
    x = sg * 0.0372
    for yc in (0.979, 0.959, 0.939):                                          # 세로 홈 셋
        span(yc - 0.0035, yc + 0.0035, 0.083, 0.141, 0.003, gd, r=0.3, buf=bar, x=x)
    span(1.010, 1.052, 0.105, 0.117, 0.003, gd, r=0.3, buf=bar, x=x)       # 앞 가장자리 가로 홈
    span(0.738, 0.768, 0.105, 0.117, 0.003, gd, r=0.3, buf=bar, x=x)       # 뒤 가장자리 가로 홈
span(0.640, 0.740, 0.052, 0.175, 0.078, gl, buf=bar)                      # 가늠쇠 단 (밝은 면)
side_prism(bar, [(0.643, 0.172), (0.697, 0.172), (0.669, 0.199), (0.643, 0.199)], -0.010, 0.010, gk)   # 세모꼴 가늠쇠 날개
span(0.540, 0.646, 0.074, 0.149, 0.050, gl, r=0.08, buf=bar)              # 드러난 총열 (뒤 5 cm는 리시버 속)
for sg in SIDES:
    span(0.596, 0.640, 0.106, 0.116, 0.003, gd, r=0.3, buf=bar, x=sg * 0.0252)   # 총열 가운데 가로 홈
# -- 고정 쪽 (sion_rifle)
span(0.049, 0.592, 0.045, 0.167, 0.072, gk, r=0.08)                       # 리시버 (납작한 윗면)
span(0.289, 0.637, 0.028, 0.049, 0.036, gk, r=0.15)                       # 아래 레일 (리시버 앞 → 가늠쇠 단 밑)
for sg in SIDES:
    x0 = sg * 0.036
    x1 = sg * 0.0385
    for yb in (0.463, 0.432, 0.401):                                          # 사선 홈 셋 (위가 총구 쪽)
        side_prism(gun, [(yb, 0.052), (yb + 0.008, 0.052), (yb + 0.021, 0.088), (yb + 0.013, 0.088)], min(x0, x1), max(x0, x1), gd)
    span(0.139, 0.296, 0.063, 0.122, 0.004, gl, r=0.2, x=sg * 0.037)       # 볼트 판 (앞쪽이 높다)
    span(0.073, 0.141, 0.063, 0.108, 0.004, gl, r=0.2, x=sg * 0.037)
xrod(gun, -0.038, -0.050, 0.268, 0.093, 0.008, gd)                         # 볼트 판 둥근 손잡이 (왼쪽)
span(0.108, 0.292, -0.122, 0.047, 0.052, gk, r=0.08)                      # 상자 탄창 (손 앞, 아래로 길게)
span(0.103, 0.297, -0.136, -0.118, 0.058, gl, r=0.2)                      # 탄창 바닥판
span(0.226, 0.229, -0.112, 0.040, 0.0535, gd, r=0.3)                      # 탄창 앞 줄
span(0.030, 0.096, -0.020, -0.010, 0.014, gk, r=0.3)                      # 방아쇠울 (개머리 바로 앞)
span(0.086, 0.096, -0.020, 0.047, 0.014, gk, r=0.3)
span(0.052, 0.060, -0.004, 0.046, 0.008, gl, r=0.3)                       # 방아쇠
# 개머리 목: 리시버 뒤끝에서 개머리 아래로 비스듬히 이어진다 (오른손이 아랫부분을 감싼다. 권총 손잡이 없음)
side_prism(gun, [(0.062, 0.045), (0.062, 0.167), (-0.070, 0.167), (-0.070, -0.085), (0.000, -0.035)], -0.026, 0.026, gk)
span(-0.360, -0.062, -0.088, 0.162, 0.068, gk, r=0.08)                    # 개머리 (크고 각진 상자)
span(-0.292, -0.090, 0.150, 0.186, 0.056, gl, r=0.2)                      # 뺨받침
span(-0.388, -0.356, -0.096, 0.172, 0.074, gd, r=0.15)                    # 개머리판
for sg in SIDES:
    span(-0.318, -0.104, -0.058, 0.128, 0.003, gl, r=0.35, x=sg * 0.0345)  # 안쪽 밝은 판 (모서리가 둥글다)
    span(-0.300, -0.122, 0.034, 0.040, 0.002, gk, r=0.4, x=sg * 0.0362)    # 판을 가르는 가는 줄
    for (yy, zz) in ((-0.128, 0.108), (-0.294, 0.108), (-0.128, -0.040), (-0.294, -0.040)):
        xrod(gun, sg * 0.0355, sg * 0.0385, yy, zz, 0.0045, gd, segs=8)       # 나사
SCOPE_Z = 0.226
rod(gun, 0.418, 0.362, 0.040, 0.040, gk, z=SCOPE_Z, segs=16)              # 조준경 대물렌즈 통 (크다)
rod(gun, 0.362, 0.320, 0.040, 0.023, gk, z=SCOPE_Z, segs=16)
disc(gun, (0, 0.4185, SCOPE_Z), (0, 1, 0), (0, 0, 1), 0.033, 0.033, 0.002, segs=16, mat=lens)
rod(gun, 0.322, 0.112, 0.023, 0.023, gk, z=SCOPE_Z, segs=14)              # 몸통
rod(gun, 0.114, 0.060, 0.023, 0.028, gk, z=SCOPE_Z, segs=14)              # 접안부
rod(gun, 0.062, 0.042, 0.029, 0.029, gl, z=SCOPE_Z, segs=14)
disc(gun, (0, 0.0415, SCOPE_Z), (0, -1, 0), (0, 0, 1), 0.022, 0.022, 0.002, segs=14, mat=lens)
for yc in (0.237, 0.139):                                                    # 고리 둘 (리시버 윗면에 얹힘)
    rod(gun, yc + 0.010, yc - 0.010, 0.028, 0.028, gl, z=SCOPE_Z, segs=14)
    span(yc - 0.012, yc + 0.012, 0.160, SCOPE_Z - 0.018, 0.030, gl, r=0.15)
loft(gun, [{"c": V((0, 0.190, SCOPE_Z)), "rx": 0.017, "ry": 0.017, "w": {}},
           {"c": V((0, 0.190, SCOPE_Z + 0.047)), "rx": 0.017, "ry": 0.017, "w": {}}], segs=12, cap0="flat", cap1="flat",
     mat=gk, ref=(1, 0, 0))                                                   # 가운데 다이얼 (위)
xrod(gun, -0.020, -0.040, 0.190, SCOPE_Z, 0.015, gk)                       # 옆 다이얼 (왼쪽)
xrod(gun, 0.020, 0.036, 0.190, SCOPE_Z, 0.012, gk)
# 양각대 마운트 (고정 쪽: 아래 레일 앞쪽 밑, 리시버에 붙어 총열이 주퇴해도 움직이지 않는다). 피벗 축 (y 0.522, z 0)
BIPOD_Y, BIPOD_Z, LEG_X = 0.522, 0.0, 0.0195
span(0.500, 0.546, 0.010, 0.030, 0.050, gk, r=0.2)                        # 마운트 (아래 레일 밑)
for sg in SIDES:
    span(0.508, 0.536, -0.012, 0.022, 0.004, gk, r=0.3, x=sg * 0.0415)     # 피벗 귀 (다리 바깥)
xrod(gun, -0.045, 0.045, BIPOD_Y, BIPOD_Z, 0.008, gl)                       # 피벗 핀
# 접힌 다리 둘 (sion_rifle_bipod): 굵은 관 · 가는 대 · 고리 · 원뿔 발 (총구 쪽을 가리킨다). m8/stage.ts LEG와 같은 치수
for sg in SIDES:
    x = sg * LEG_X
    rod(bip, BIPOD_Y - 0.012, 0.619, 0.0175, 0.0175, gk, x=x, z=BIPOD_Z, cap0="round")
    rod(bip, 0.609, 0.613, 0.0182, 0.0182, gd, x=x, z=BIPOD_Z)               # 굵은 관 끝 줄
    rod(bip, 0.619, 0.700, 0.0110, 0.0110, gk, x=x, z=BIPOD_Z, segs=10)
    rod(bip, 0.700, 0.724, 0.0160, 0.0160, gl, x=x, z=BIPOD_Z)
    rod(bip, 0.724, 0.738, 0.0190, 0.0190, gk, x=x, z=BIPOD_Z, segs=8)
    rod(bip, 0.738, 0.792, 0.0190, 0.0015, gk, x=x, z=BIPOD_Z, segs=8)
vc = elf.vc_material("sion_toon_vc", e.line)


def gun_node(buf, name):
    ob = buf.obj(name + "_geo", angle=35.0)
    cb.apply_modifiers(ob)
    elf.bake_vcol(ob)
    elf.remap_to_vc(ob, vc)
    elf.collapse_slots(ob)
    ob.name = name
    ob["outline"] = 0.003
    return ob


rifle = gun_node(gun, "sion_rifle")
rifle["prop"] = "rifle"
rifle["muzzle"] = "0,%.3f,%.3f" % (MZ_Y, BORE_Z)
barrel = gun_node(bar, "sion_rifle_barrel")
barrel["recoil"] = "0.040"    # 주퇴 거리 (m, 총 지역 -Y). 코드(m8/stage.ts BARREL_STROKE)가 같은 값을 쓴다
legs = gun_node(bip, "sion_rifle_bipod")
for ch in (barrel, legs):
    ch.parent = rifle
    ch.matrix_parent_inverse = Matrix.Identity(4)
    ch.matrix_basis = Matrix.Identity(4)
sock = bpy.data.objects["socket_back"]
rifle.parent = sock
# 등 왼쪽에 납작하게 비스듬히 멤 (총 왼쪽 옆면이 등에 붙는다): 총구가 왼쪽(+X) 위, 개머리가 가운데 아래. 1.51 m라 머리 왼쪽 밖으로
# 총구가 머리 위까지 오른다. 오른쪽 사이드 포니테일이 발목 높이까지 내려와(x -0.17..-0.35) 개머리는 x -0.15 안쪽에서 끝나고
# (총 가운데를 왼쪽으로), 조준경은 대각선 아래 왼쪽(왼팔 바깥)을 본다
rifle.matrix_parent_inverse = Matrix.Identity(4)
rifle.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
mw = sock.matrix_world.copy()
CARRY_DEG = 26.0                                  # 세로에서 기운 각
d = V((math.sin(math.radians(CARRY_DEG)), 0.0, math.cos(math.radians(CARRY_DEG))))   # 총구 방향 (월드)
gx = V((0.0, 1.0, 0.0))                           # 총 오른쪽 = 바깥 (총 위쪽이 대각선 아래 왼쪽을 본다: 개머리 윗모서리가 오른쪽 사이드 포니테일로 가지 않게)
gz = gx.cross(d).normalized()                     # 총 위
Mw = Matrix((gx, d, gz)).transposed().to_4x4()
# 총 가운데(파지점에서 앞 0.37, 위 0.03)가 등 소켓 조금 왼쪽·아래에 오게
center = V((0.26, mw.translation.y + 0.045, 0.82))
Mw.translation = center - d * 0.37 - gz * 0.03
rifle.matrix_basis = mw.inverted() @ Mw

e.export("characters/sion.glb")
