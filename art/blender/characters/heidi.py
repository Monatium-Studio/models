"""하이디: 모나티엄 방송국(선전반) 소속 엘프 기자. 선전반 이전에는 종군기자로 지구 침공 현장을 찍었다(원작 설정).
이 작품에서는 1막 로딩 영상 3 「종군기자 하이디」의 카메라 시점 주인공이다(역할은 사용자 확정, 원작 경력과 맞는다).

원작 하이디(트릭컬 리바이브, '특종 그 자체 기자')의 기본 복장을 따른다. 근거: docs/art/characters-cameo3.md 2장.
- 식별 요소: 잿빛 연두 회색 머리(옆으로 넘긴 앞머리, 귀 뒤로 낮게 늘어져 바깥으로 말리는 양 갈래 컬), 별(✦) 반짝임이
  든 초록 눈과 자신만만한 웃음, 디어스토커 모자(베이지 조각 + 갈색 솔기, 뒤·왼쪽은 적갈색 체크, 꼭지의 초록 새싹,
  앞 왼쪽의 렌즈 모양 흰 배지), 흰 셔츠와 주황빛 빨간 애스콧 타이 + 렌즈 브로치, 베이지 니트 조끼(세로 골지),
  크림색 반바지와 갈색 벨트, 오른 허벅지 갈색 홀스터 띠, 체크무늬 숄더백, 오른손목 시계, 헐렁한 흰 양말,
  짙은 갈색 앞코와 리본 끈의 황갈색 부츠, 검은 2안 필름 카메라(별도 노드 heidi_camera).
- [오리지널] 종군기자 표식: 왼팔 'PRESS' 완장(흰 바탕에 검은 블록 글자), 조끼 왼쪽 가슴의 모나티엄 방송국 기자증.
  원작 외형은 바꾸지 않고 장면(전장 취재)에 맞는 3차 디테일만 더했다.
- 표정: 키트 5종 + grin(특종 웃음, 원작 카드) + smug(자뻑) + shock(포화 속 경악) + wink(셀카 윙크, 교정 키 없음)
  + blink 교정 키.

npm run model -- art/blender/characters/heidi.py
npm run shot -- characters/heidi.glb
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
e = elf.Elf("heidi", height=1.18, head=0.45, leg=0.96, limb=1.06, chest=0.24, bust=0.25, hips=1.10, segs=0.60, hand_q=0.36,
            cheek=0.12)
k = e.k
M_ = elf.mat

# ---- 팔레트 (원작 카드·소개·피규어 GIF에서 눈으로 뽑음)
HAIR, HAIR_D, HAIR_L = "#aaac9e", "#7b7f72", "#d6d8cc"
hat = M_("hd_hat", "#e3cfa3")
hat_d = M_("hd_hat_d", "#a57b52")
plaid = M_("hd_plaid", "#a9533f")
plaid_d = M_("hd_plaid_d", "#6e3a2e")
plaid_l = M_("hd_plaid_l", "#e8a25a")
white = M_("hd_white", "#fbf9f6")
white_d = M_("hd_white_d", "#e6e0d8")
ascot = M_("hd_ascot", "#ea4a22")
vest = M_("hd_vest", "#d8bd8f")
vest_d = M_("hd_vest_d", "#bf9f6f")
shorts = M_("hd_shorts", "#f0e2c6")
brown = M_("hd_brown", "#8a5c3e")
brown_d = M_("hd_brown_d", "#4f3328")
boot_m = M_("hd_boot", "#cfa77c")
silver = M_("hd_silver", "#cfd2da")
black = M_("hd_black", "#2c2a30")
gold = M_("hd_gold", "#e7bd5e")
green = M_("hd_green", "#43b25a")
lens = M_("hd_lens", "#3f5f63")
press_m = M_("hd_press", "#2f4f8f")

# ---- 얼굴: 초록 눈 + 별(✦) 반짝임, 자신만만한 웃음이 기본, 회색 눈썹
fairy.face(e, eye_color="#3fbf8a", iris_dark="#1d6a4f", iris_light="#b8f0cf", pupil="#17473a",
           lash="#4a3b38", brow="#7d7c70", brow_th=0.95, blush="#f7a3a6", blush_size=1.2,
           star="sparkle", star_color="#fff6c4", star_size=1.1,
           base={"eye": {"top": 0.027, "ktop": 3.2},
                 "brow": {"ang": 4.0, "dz": 0.068, "arch": 0.004},
                 "mouth": {"w": 0.024, "curve": 0.0050, "open": 0.0030}},
           expr={
               # 특종 웃음: 이를 드러낸 큰 웃음 (원작 카드)
               "grin": {"eye": {"top": 0.026, "lift": 0.010, "ktop": 3.4},
                        "brow": {"ang": 8.0, "dz": 0.070, "arch": 0.005},
                        "mouth": {"w": 0.040, "curve": 0.0100, "open": 0.0200, "top_arch": -0.0020}},
               # 포화 속 경악: 동그란 눈, 작은 동공, 벌린 입
               "shock": {"eye": {"top": 0.036, "ktop": 2.2, "bot": 0.058},
                         "iris": {"pupil": 0.50, "rx": 0.025, "ry": 0.033},
                         "brow": {"ang": 18.0, "dz": 0.078, "arch": 0.004},
                         "mouth": {"w": 0.024, "curve": -0.0040, "open": 0.0200, "wave": 0.0015}},
           })
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.018, "lift": 0.010, "ktop": 4.0}, "mouth": {"w": 0.030, "curve": 0.0060}},
             L={"brow": {"dz": 0.072, "ang": 6.0, "arch": 0.004}}, R={"brow": {"dz": 0.064, "ang": -6.0}},
             corner=(0.0090, 0.0010), mouth_dx=0.0020 * k)
c2.face_expr(e, "wink",
             both={"mouth": {"w": 0.036, "curve": 0.0090, "open": 0.0120, "top_arch": -0.0015}},
             L={"eye": {"close": 1.0}, "brow": {"dz": 0.064, "ang": -4.0}},
             R={"eye": {"top": 0.028, "lift": 0.006}, "brow": {"dz": 0.072, "ang": 8.0}},
             corner=(0.0040, 0.0060), blink_fix=False)

# ---- 디어스토커 모자 (원작: 베이지 조각 + 갈색 솔기, 뒤·왼쪽 적갈색 체크, 꼭지 초록 새싹, 앞 왼쪽 렌즈 배지)
OFF = 0.034 * k


def rim_el(az):
    a = abs(((az + 180) % 360) - 180)
    return lerp(22.0, -2.0, smoothstep(0, 150, a))


def is_plaid(az):
    """캐릭터 왼쪽 뒤 조각들 (원작 카드에서 오른쪽(캐릭터 왼쪽)과 뒤가 체크)."""
    a = az % 360.0
    return 85.0 <= a <= 225.0


HAT = {}


def hat_geo(buf):
    w = {"head": 1.0}
    hc = e.head_c
    n, rows = 20, 5
    R = []
    for r in range(rows):
        t = r / (rows - 1)
        row = []
        for j in range(n):
            az = 360.0 * j / n
            el = lerp(rim_el(az), 84.0, t ** 0.9)
            puff = OFF * (1.0 + 0.30 * math.sin(math.pi * min(1.0, t * 1.3)))
            row.append(e.head_point(az, el, puff)[0])
        R.append(row)
    top = e.head_point(0.0, 90.0, OFF * 1.05)[0]
    ids = [[buf.vert(q, w) for q in row] for row in R]
    ti = buf.vert(top, w)
    for r in range(rows - 1):
        for j in range(n):
            j2 = (j + 1) % n
            m = plaid if is_plaid(360.0 * (j + 0.5) / n) else hat
            buf.face((ids[r][j], ids[r][j2], ids[r + 1][j2], ids[r + 1][j]), m)
    for j in range(n):
        m = plaid if is_plaid(360.0 * (j + 0.5) / n) else hat
        buf.face((ids[-1][j], ids[-1][(j + 1) % n], ti), m)
    # 안쪽 면 (테두리 두께)
    inner = [buf.vert(q - (q - hc).normalized() * 0.006 * k, w) for q in R[0]]
    for j in range(n):
        j2 = (j + 1) % n
        buf.face((ids[0][j2], ids[0][j], inner[j], inner[j2]), hat_d)
    # 조각 솔기 (갈색 파이핑, 8조각)
    for s in range(8):
        az = s * 45.0 + 22.5
        pts, nrm, ups = [], [], []
        for r in range(rows):
            t = r / (rows - 1)
            el = lerp(rim_el(az), 84.0, t ** 0.9)
            puff = OFF * (1.0 + 0.30 * math.sin(math.pi * min(1.0, t * 1.3)))
            p, nn = e.head_point(az, el, puff + 0.0015 * k)
            pts.append(p)
            nrm.append(nn)
            ups.append(V((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0)))
        elf._loop(buf, pts, nrm, ups, 0.0045 * k, 0.0025 * k, mat=hat_d, w=w, closed=False)
    # 체크 무늬: 체크 조각 위의 가로 줄 2 + 세로 줄 (짙은 적갈색, 주황)
    for el_t, mat_ in ((0.28, plaid_d), (0.58, plaid_l)):
        pts, nrm, ups = [], [], []
        for i in range(13):
            az = lerp(87.0, 223.0, i / 12)
            el = lerp(rim_el(az), 84.0, el_t ** 0.9)
            puff = OFF * (1.0 + 0.30 * math.sin(math.pi * min(1.0, el_t * 1.3)))
            p, nn = e.head_point(az, el, puff + 0.0012 * k)
            pts.append(p)
            nrm.append(nn)
            ups.append(V((0, 0, 1)))
        elf._loop(buf, pts, nrm, ups, 0.0070 * k, 0.0012 * k, mat=mat_, w=w, closed=False)
    for az in (118.0, 186.0):
        for mat_, da in ((plaid_l, 0.0),):
            pts, nrm, ups = [], [], []
            for r in range(5):
                t = 0.05 + 0.80 * r / 4
                el = lerp(rim_el(az + da), 84.0, t ** 0.9)
                puff = OFF * (1.0 + 0.30 * math.sin(math.pi * min(1.0, t * 1.3)))
                p, nn = e.head_point(az + da, el, puff + 0.0012 * k)
                pts.append(p)
                nrm.append(nn)
                ups.append(V((math.cos(math.radians(az + da)), math.sin(math.radians(az + da)), 0.0)))
            elf._loop(buf, pts, nrm, ups, 0.0045 * k, 0.0010 * k, mat=mat_, w=w, closed=False)
    # 앞 챙 (아래로 휜 반달) + 뒤 챙(짧게)
    for front, a0, a1, reach0, drop in ((True, -70.0, 70.0, 0.050, 0.020), (False, 120.0, 240.0, 0.030, 0.016)):
        m_ = 11
        top_i, out_i, bot_i, bin_i = [], [], [], []
        for j in range(m_):
            az = lerp(a0, a1, j / (m_ - 1))
            p0, n0 = e.head_point(az, rim_el(az) + 1.0, OFF + 0.001 * k)
            a = math.radians(az)
            out = V((math.sin(a), -math.cos(a), 0.0))
            f = math.sin(math.pi * j / (m_ - 1)) ** 0.7
            reach = reach0 * k * f
            p1 = p0 + out * reach + V((0, 0, -drop * k * f))
            top_i.append(buf.vert(p0, w))
            out_i.append(buf.vert(p1, w))
            bot_i.append(buf.vert(p1 + V((0, 0, -0.004 * k)), w))
            bin_i.append(buf.vert(p0 + V((0, 0, -0.004 * k)), w))
        mt = plaid if not front else hat
        for j in range(m_ - 1):
            buf.face((top_i[j], top_i[j + 1], out_i[j + 1], out_i[j]), mt)
            buf.face((out_i[j], out_i[j + 1], bot_i[j + 1], bot_i[j]), hat_d)
            buf.face((bot_i[j], bot_i[j + 1], bin_i[j + 1], bin_i[j]), hat_d)
    # 꼭지 단추 + 초록 새싹 (잎 두 장)
    c2.ellipsoid(buf, top + V((0, 0, 0.004 * k)), V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)), 0.008 * k, 0.010 * k,
                 0.010 * k, segs=8, rings=4, mat=hat_d, w=w)
    loft(buf, [{"c": top + V((0, 0, 0.008 * k)), "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
               {"c": top + V((0.004 * k, 0, 0.022 * k)), "rx": 0.0030 * k, "ry": 0.0030 * k, "w": w}], segs=6,
         cap0="flat", cap1="round", mat=hat_d)
    for sg, ang in ((1, 35.0), (-1, -50.0)):
        Ml = Matrix.Translation(top + V((0.003 * k, 0, 0.018 * k))) @ frame(V((0, -1, 0)), V((0, 0, 1))) @ \
            Matrix.Rotation(math.radians(-ang), 4, "Y")
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.030 if sg > 0 else 0.022, 0.016, n=5)],
                 0.003 * k, Ml @ Matrix.Translation((0, 0.0015 * k, 0)), mat=green, w=w)
    # 렌즈 배지 (앞 왼쪽): 흰 물방울 판 + 짙은 렌즈
    p, nn = e.head_point(30.0, 36.0, OFF * 1.30)
    Mb = Matrix.Translation(p) @ frame(nn, (0, 0, 1)) @ Matrix.Rotation(math.radians(-12), 4, "Y")
    c2.prism(buf, c3.drop_poly(0.022 * k, n=12, point=1.35), 0.005 * k, Mb, mat=white, w=w, chamfer=0.0015 * k)
    disc(buf, Mb @ V((0, -0.005 * k, 0.003 * k)), nn, (0, 0, 1), 0.0105 * k, 0.0105 * k, 0.003 * k, segs=12,
         mat=silver, w=w)
    disc(buf, Mb @ V((0, -0.008 * k, 0.003 * k)), nn, (0, 0, 1), 0.0075 * k, 0.0075 * k, 0.002 * k, segs=12,
         mat=black, w=w)
    HAT["ok"] = True


e.part("hat", "head", hat_geo)
e._hats = getattr(e, "_hats", []) + [(OFF, rim_el)]

# ---- 머리 (헤어 v2): 잿빛 연두 회색의 풍성한 곱슬 장발 (허리 아래까지), 옆으로 넘긴 앞머리
# 셸은 cameo3.CurlyHair(떨어지는 구간에 엇갈린 짧은 물결 + 끝이 말린 다발), 그 위에 나선 링렛 다발을 둘렀다.
def curly_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.1
        lk["free"] *= 0.7
    elif lk["region"] in ("side", "back"):
        lk["curl"] = 0.030 * k       # 끝이 바깥으로 둥글게 말린다
        lk["p"] = 2.6
        lk["puff"] *= 1.9


h = c3.curly_hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.28, lock_fn=c2.lock_edit(curly_locks),
                  wave=(0.026, 0.100, -0.01, 0.05), q_shell=1.04)
h.cap(front=26, side=-8, back=-44, part=-26, segs=15, rows=5)
h.bangs(n=6, spread=58, tip_el=-2, sweep=-14, part=-26, jag=0.14, curl=1.4, seed=6.0)
h.sides(length=0.30, width=0.092, az=62, n=2, curl=1.2, puff=2.2, thick=1.15)
h.back(length=0.44, n=9, spread=104, thick=1.2)


def s_at_z(az, z):
    lo, hi = 0.0, 2.0 * k
    for _ in range(36):
        mid = (lo + hi) / 2
        if h.path(az, mid)[0].z > z:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# 나선 링렛 다발: 앞 어깨 앞(옆머리 끝) 2 + 옆 2 + 뒤 2. 셸 바깥 면에서 시작해 아래로 감기며 머리끝 아래까지 내려온다
RINGLETS = [(58.0, e.shoulder_z - 0.050 * k, 0.17), (-58.0, e.shoulder_z - 0.050 * k, 0.17),
            (100.0, e.chest_z - 0.020 * k, 0.19), (-100.0, e.chest_z - 0.020 * k, 0.19),
            (150.0, e.waist_z - 0.040 * k, 0.17), (-150.0, e.waist_z - 0.040 * k, 0.17)]
for i, (az, z, ln) in enumerate(RINGLETS):
    top, nrm = h.path(az, s_at_z(az, z), 0.004 * k)
    c3.ringlet(h, f"hair_curl_{i + 1:02d}", top, nrm, length=ln, radius=0.021, turns=2.0, width=0.048,
               thick=0.038, bones=2, parent="chest", n=18, segs=7, twist=1 if az > 0 else -1)

# ---- 셔츠 + 니트 조끼 + 애스콧 타이 + 렌즈 브로치
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(white, hem=wz - 0.012 * k, collar=None, flare=0.006)
e.sleeves(white, length=0.93, off=0.012, flare=0.010, puff=0.010, cuff=(white_d, 0.020, 0.004))


def collar(buf):
    w = {"neck": 0.4, "chest": 0.6}
    band(buf, (0, 0.004 * k, e.torso_top + 0.008 * k), (0, 0, 1), (1, 0, 0), 0.054 * k, 0.050 * k, 0.020 * k,
         0.005 * k, segs=14, mat=white, w=w, taper=-0.03)
    for sg in (1, -1):
        p, n = e.torso_point(e.torso_top - 0.002 * k, sg * 26, 0.016 * k)
        M = Matrix.Translation(p) @ frame(n, (0, 0, 1)) @ Matrix.Rotation(math.radians(sg * 18), 4, "Y")
        c2.prism(buf, [(-sg * 0.022 * k, 0.010 * k), (sg * 0.014 * k, 0.012 * k), (sg * 0.002 * k, -0.026 * k)],
                 0.004 * k, M, mat=white, w=w)


e.part("collar", "body", collar)
vest_sh = c2.Shell(e, vest, e.torso_top - 0.006 * k, wz - 0.016 * k,
                   gap=[(0.0, 40.0), (0.36, 16.0), (0.50, 0.0), (1.0, 0.0)], off=0.022, th=0.005, rows=6, cols=18,
                   flare=[(0.0, 0.0), (0.6, 0.006), (1.0, 0.010)])
vest_sh.edge_trim(vest_d, width=0.010, th=0.002, i1=4)
vest_sh.hem_trim(vest_d, width=0.016, th=0.003)
# 세로 골지 (짙은 줄)
for a in (-48, 48, 130, 180, 230):
    pts, nrm, ups, ws = [], [], [], []
    for i in range(4):
        u = lerp(0.56 if abs(a) < 90 else 0.08, 0.90, i / 3)
        p, n = vest_sh.surface(u, a, 0.0006 * k)
        pts.append(p)
        nrm.append(n)
        ups.append(V((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0)))
        ws.append(e._torso_wfn(p, 0))
    vest_sh._strip(pts, nrm, ups, 0.004, 0.0012, vest_d, ws)
vest_sh.done("vest")
# 조끼 아래 뾰족한 셔츠 자락 (원작: 조끼 밑단 아래 흰 삼각 자락)
for a in (-14.0, 14.0):
    p, n = e.torso_point(wz - 0.020 * k, a, 0.024 * k)
    e.part(f"shirt_tail_{int(a)}", "body",
           lambda buf, p=p, n=n: c2.prism(buf, [(-0.016 * k, 0.0), (0.016 * k, 0.0), (0.0, -0.022 * k)], 0.003 * k,
                                          Matrix.Translation(p) @ frame(n, (0, 0, 1)), mat=white,
                                          w=e._torso_wfn(p, 0)))


def ascot_tie(buf):
    w = {"neck": 0.3, "chest": 0.7}
    p, n = e.torso_point(e.torso_top - 0.014 * k, 0, 0.024 * k)
    M = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    c2.bow_geo(buf, M, 0.052 * k, ascot, w=w, tails=1.15, segs=5)
    # 렌즈 브로치: 흰 원판 + 짙은 렌즈 + 은테
    disc(buf, M @ V((0, -0.010 * k, 0.000)), n, (0, 0, 1), 0.0095 * k, 0.0095 * k, 0.003 * k, segs=12, mat=white,
         w=w)
    disc(buf, M @ V((0, -0.013 * k, 0.000)), n, (0, 0, 1), 0.0055 * k, 0.0055 * k, 0.0025 * k, segs=10, mat=black,
         w=w)


e.part("ascot", "body", ascot_tie)


# [오리지널] 모나티엄 방송국 기자증: 조끼 왼쪽 가슴 클립 카드 (흰 카드 + 초록 띠 + 사진 칸)
def press_card(buf, Mx, w):
    c3.box12(buf, (0.030 * k, 0.003 * k, 0.040 * k), Mx, white, w)
    c3.box12(buf, (0.030 * k, 0.0034 * k, 0.008 * k), Mx @ Matrix.Translation((0, -0.0004 * k, 0.014 * k)), green, w)
    c3.box12(buf, (0.010 * k, 0.0036 * k, 0.012 * k), Mx @ Matrix.Translation((-0.007 * k, -0.0006 * k, -0.002 * k)),
             silver, w)
    c3.box12(buf, (0.008 * k, 0.004 * k, 0.006 * k), Mx @ Matrix.Translation((0, 0.0, 0.022 * k)), silver, w)


e.gear("press_card", ("torso", cz + 0.004 * k, 42, 0.031 * k), press_card)

# ---- 크림색 반바지 + 갈색 벨트 + 오른 허벅지 홀스터 띠
q0 = e.q
e.q = 0.48     # 반바지·부츠는 성글게 (곱슬 장발에 삼각형을 돌린다)
e.pants(shorts, waist=wz - 0.004 * k, length=0.24, bag=0.020, blouse=0.0, off=0.014, cuff=(shorts, 0.010, 0.003))
e.q = q0
e.belt(brown, z=wz - 0.040 * k, h=0.016, th=0.004, off=0.024, buckle=gold, buckle_size=(0.020, 0.016))
e.ring(brown, "leg_R", 0.33, h=0.020, th=0.005, off=0.006, name="thigh_strap")
e.pouch(brown, ("leg_R", 0.31, -70, 0.016 * k), size=(0.036, 0.020, 0.046), flap=brown_d, button=silver)
a_r = e.anchor(("leg_R", 0.33, -12, 0.011 * k))
e.part("thigh_rivet", "body", lambda buf: disc(buf, a_r.pos, a_r.n, (0, 0, 1), 0.0075 * k, 0.0075 * k, 0.003 * k,
                                               segs=10, mat=silver, w=a_r.w))

# ---- 체크무늬 숄더백 (왼 어깨 → 오른쪽 엉덩이) + 플래시 손잡이
e.strap(brown_d, [("torso", sz - 0.010 * k, 46, 0.026 * k), ("torso", sz + 0.004 * k, 90, 0.026 * k),
                  ("torso", cz, 150, 0.032 * k), ("torso", wz - 0.010 * k, -150, 0.034 * k),
                  ("torso", hz + 0.010 * k, -112, 0.036 * k)], width=0.014, th=0.004, name="bag_strap")
e.strap(brown_d, [("torso", sz - 0.010 * k, 46, 0.026 * k), ("torso", cz + 0.010 * k, 20, 0.034 * k),
                  ("torso", wz - 0.006 * k, -40, 0.036 * k), ("torso", hz + 0.004 * k, -96, 0.040 * k)],
        width=0.014, th=0.004, name="bag_strap_f")


def satchel(buf, Mx, w):
    rbox(buf, (0.080 * k, 0.040 * k, 0.066 * k), Mx @ Matrix.Translation((0, -0.012 * k, 0)), mat=plaid, w=w, r=0.3,
         segs=1)
    rbox(buf, (0.084 * k, 0.044 * k, 0.030 * k), Mx @ Matrix.Translation((0, -0.014 * k, 0.022 * k)), mat=plaid_d,
         w=w, r=0.3, segs=1)
    for x in (-0.022, 0.022):     # 체크 세로줄
        c3.box12(buf, (0.006 * k, 0.042 * k, 0.064 * k), Mx @ Matrix.Translation((x * k, -0.012 * k, 0)), plaid_l, w)
    c3.box12(buf, (0.082 * k, 0.042 * k, 0.006 * k), Mx @ Matrix.Translation((0, -0.012 * k, -0.012 * k)), plaid_d, w)
    # 플래시 손잡이 (은색 관 두 개가 가방 뒤로 비스듬히 솟음)
    for i, (dx, ln) in enumerate(((-0.012, 0.11), (0.012, 0.09))):
        a0 = Mx @ V((dx * k, 0.004 * k, 0.020 * k))
        a1 = Mx @ V((dx * k - 0.020 * k, 0.020 * k, (0.020 + ln) * k))
        loft(buf, [{"c": a0, "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
                   {"c": a1, "rx": 0.009 * k, "ry": 0.009 * k, "w": w}], segs=8, cap0="flat", cap1="flat",
             mat=silver)
        loft(buf, [{"c": a1, "rx": 0.012 * k, "ry": 0.012 * k, "w": w},
                   {"c": a1 + (a1 - a0).normalized() * 0.012 * k, "rx": 0.012 * k, "ry": 0.012 * k, "w": w}],
             segs=8, cap0="flat", cap1="flat", mat=black)


e.gear("satchel", ("torso", hz - 0.010 * k, -112, 0.050 * k), satchel)

# ---- 헐렁한 흰 양말 + 부츠(짙은 갈색 앞코, 리본 끈)
for sd in ("L", "R"):
    c2.leg_tube(e, white, sd, 0.62, 0.86, off=0.010, extra=lambda t: 0.010 * math.sin(math.pi * (t - 0.62) / 0.24),
                name=f"sock_{sd}", segs=12)
e.q = 0.48
e.boots(boot_m, top=0.84, sole=(brown_d, 0.016), cuff=brown, off=0.014, toe=0.006)
e.q = q0
for sd in ("L", "R"):
    a = e.anchor((f"leg_{sd}", 0.95, 0, 0.026 * k))

    def boot_bits(buf, a=a, sd=sd):
        Mx = a.matrix()
        c2.bow_geo(buf, Mx @ Matrix.Translation((0, -0.004 * k, 0.004 * k)), 0.034 * k, brown_d, w=a.w, tails=0.0,
                   segs=5)
        # 짙은 갈색 앞코
        ch = e.leg_chain(sd)
        c, tan = ch.at(1.0)
        rx, ry = e.leg_r(1.0)
        c2.ellipsoid(buf, c + V((0, -0.052 * k, -0.030 * k)), V((0, -1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.032 * k,
                     rx + 0.012 * k, 0.024 * k, segs=7, rings=4, mat=brown_d, w=ch.weights(1.0))
    e.part(f"boot_bits_{sd}", "body", boot_bits)

# ---- 오른손목 시계 + [오리지널] 왼팔 PRESS 완장
e.ring(brown, "arm_R", 0.90, h=0.012, th=0.004, off=0.018, name="watch_band")
a_w = e.anchor(("arm_R", 0.90, -90, 0.022 * k))
e.part("watch_face", "arms", lambda buf: (disc(buf, a_w.pos, a_w.n, (0, 0, 1), 0.010 * k, 0.010 * k, 0.004 * k,
                                               segs=12, mat=gold, w=a_w.w),
                                          disc(buf, a_w.pos + a_w.n * 0.004 * k, a_w.n, (0, 0, 1), 0.0072 * k,
                                               0.0072 * k, 0.0015 * k, segs=12, mat=white, w=a_w.w)))
e.ring(press_m, "arm_L", 0.30, h=0.034, th=0.004, off=0.024, name="press_band")

# 블록 글자 'PRESS' (완장 바깥 면, 3×5 칸 글자: cameo3.block_word)
def press_letters(buf):
    ch = e.arm_chain("L")
    c, tan = ch.at(0.30)
    rx, ry = e.arm_r(0.30)
    out = V((0.30, -1.0, 0.45))
    out = (out - tan * out.dot(tan)).normalized()       # 위팔 앞·바깥 면 (정면에서 읽히게)
    side = out.cross(tan).normalized()
    base = c + out * (max(rx, ry) + 0.0275 * k)
    M = Matrix.Translation(base) @ frame(out, side) @ Matrix.Rotation(math.radians(-90), 4, "Y")
    c3.block_word(buf, "PRESS", M, 0.0040 * k, 0.0016 * k, white, w=ch.weights(0.30))


_pb = Buf()
press_letters(_pb)
e.add(_pb.obj("heidi_press_letters", smooth=False), group="arms", tag="press", node="press",
      props={"noOutline": 1})

e.finalize()


# ---- 2안 필름 카메라 (별도 노드 heidi_camera): 왼손에 든다
def camera():
    """로컬: 원점 = 파지점(몸체 아래 손잡이 자리), +Y = 렌즈 방향, +Z = 위."""
    S = k * 1.25
    b = Buf()
    w = {}
    rbox(b, (0.060 * S, 0.046 * S, 0.084 * S), Matrix.Translation(V((0, 0, 0.050 * S))), mat=black, w=w, r=0.18,
         segs=1)
    rbox(b, (0.064 * S, 0.010 * S, 0.088 * S), Matrix.Translation(V((0, 0.024 * S, 0.050 * S))), mat=silver, w=w,
         r=0.2, segs=1)
    for zz, r in ((0.072, 0.017), (0.030, 0.019)):
        loft(b, [{"c": V((0, 0.028 * S, zz * S)), "rx": r * S, "ry": r * S, "w": w},
                 {"c": V((0, 0.050 * S, zz * S)), "rx": r * S, "ry": r * S, "w": w},
                 {"c": V((0, 0.052 * S, zz * S)), "rx": r * 0.86 * S, "ry": r * 0.86 * S, "w": w}], segs=12,
             cap0="flat", cap1="flat", mat=silver)
        disc(b, V((0, 0.0525 * S, zz * S)), (0, 1, 0), (0, 0, 1), r * 0.70 * S, r * 0.70 * S, 0.002 * S, segs=12,
             mat=lens, w=w)
    rbox(b, (0.030 * S, 0.026 * S, 0.016 * S), Matrix.Translation(V((-0.008 * S, 0.004 * S, 0.098 * S))), mat=silver,
         w=w, r=0.2, segs=1)
    rbox(b, (0.014 * S, 0.012 * S, 0.012 * S), Matrix.Translation(V((0.020 * S, -0.004 * S, 0.096 * S))), mat=black,
         w=w, r=0.2, segs=1)
    loft(b, [{"c": V((0.031 * S, 0.0, 0.050 * S)), "rx": 0.008 * S, "ry": 0.008 * S, "w": w},
             {"c": V((0.040 * S, 0.0, 0.050 * S)), "rx": 0.008 * S, "ry": 0.008 * S, "w": w}], segs=8, cap0="flat",
         cap1="flat", mat=silver)
    loft(b, [{"c": V((0.040 * S, 0.0, 0.050 * S)), "rx": 0.003 * S, "ry": 0.003 * S, "w": w},
             {"c": V((0.042 * S, 0.0, 0.034 * S)), "rx": 0.003 * S, "ry": 0.003 * S, "w": w}], segs=6, cap0="flat",
         cap1="round", mat=silver)
    ob = b.obj("heidi_camera_geo", angle=35.0)
    return ob


cam = camera()
sock = bpy.data.objects["socket_hand_L"]
pos = sock.matrix_world.translation.copy()
Yd = V((0.15, -1.0, 0.0)).normalized()
Zd = V((0.0, 0.0, 1.0))
Xd = Yd.cross(Zd).normalized()
Mw = Matrix((Xd, Yd, Zd)).transposed().to_4x4()
Mw.translation = pos + V((0.010 * k, -0.030 * k, -0.040 * k))
c3.socket_prop(e, cam, "socket_hand_L", Mw, name="camera", outline=0.0025,
               props={"lens": "0,%.3f,%.3f" % (0.052 * k, 0.072 * k)})

e.export("characters/heidi.glb")
