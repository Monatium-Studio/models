"""교주: 세계수 교단의 교주이자 원작의 주인공(플레이어 대리인). 엘리아스 침공전에서 흑뉴아의 만행에 격노해 성전을 선포하고,
공명으로 엘다인이 된 네르와 함께 성전군을 이끈다. 이 작품에서는 3막 「성전 소식·요정 성전군 합류」 컷신과 M9 전열에 선다.

원작 근거 (나무위키 「교주(트릭컬 리바이브)」 2.1절, 「엘리아스 침공전」 2.5.2절, docs/art/characters-cameo3.md 11장)
- 엘리아스의 유일한 인간. 사도들보다 키와 팔다리가 길고 크며 손가락이 다섯 개인 평범한 지구인 체격. 성별·얼굴은 정해지지 않았다
  (플레이어 대리인). 인게임에서는 얼굴을 보여 주지 않고(케이크 머리 아바타, 손만 나오는 삽화), PV의 전신은 검은 그림자에
  푸른 안광뿐이다.
- 네르가 만든 교단 복장, 현실의 주교들이 입는 하얀 사제복. 소매는 흰색에 푸른 띠(손 삽화). 갈색 운동화.
- 네르 티아라·도끼창의 위가 뾰족한 딸기형 붉은 보석은 교주(케이크 머리 위 딸기)를 은유한다.

사용자 지시 (2026-11-02)
- 미트라를 쓴 가톨릭 교주의 모습을 어느 정도 차용한다(원작 교주의 복장이 실제로 주교의 흰 사제복이다).
- 교주는 인간이다. 얼굴은 없이, 일반적인 성인 남성의 체형으로(키 약 1.78 m, 7.6등신). 엘프 귀 없음, 표정 모프 없음.

3D [오리지널] 해석
- 얼굴: 흰 두건(안감 남색) 속 얼굴 자리를 그림자(UNLIT 짙은 남보라)로 비웠다. 눈·입은 없다.
- 미트라: 흰 앞뒤 판(뾰족한 아치), 금 테두리, 가운데 세로 띠(티툴루스), 밑동 금 띠(키르쿨루스), 앞판 교단 문장, 뒤로 늘어진 두 수대(라펫).
- 흰 수단(바닥까지, 앞 단추) + 남색 허리띠(파시아) + 남색 영대(스톨, 금 테두리, 끝에 문장·술) + 흰 코프(금 오프리 띠, 남색 안감,
  등에 큰 문장) + 가슴 여밈 금 걸쇠(모르스, 가운데 문장 메달). 흰 소매에 남색 소맷단(원작 손 삽화).
- 교단 문장: 가슴 십자가 대신 금 잎 네 장 십자 + 가운데 딸기형 붉은 보석. 네르 베일 뒤 문장과 같은 [오리지널] 교단 문장이다.
  실존 교황의 초상·문장, 바티칸 문장은 쓰지 않는다.
- 목장(크로지어): 별도 노드 kyoju_crozier. 상아색 자루 + 금 고리 + 금 마디 + 바깥으로 말린 금 고둥(잎 장식 셋),
  고둥 안에 세계수 새싹과 딸기형 보석. 왼손(socket_hand_L)에 쥔다. 로컬: 원점 = 파지점, 자루 = +Z.
  기본 배치는 교주 자세 kyoju_stand(왼팔을 앞으로 굽혀 목장을 세워 듦)에서 자루가 수직이 되도록 맞췄다.

npm run model -- art/blender/characters/kyoju.py
npm run shot -- characters/kyoju.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import human  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, loft, band, disc, lerp, smoothstep, keys, frame, mixw  # noqa: E402

cb.reset()
M_ = elf.mat

# ---- 팔레트 (교단: 흰색·남색·금, 네르 복장과 같은 남색)
white = M_("kj_white", "#f7f4ee")
white_d = M_("kj_white_d", "#e6e0d4")
cream = M_("kj_cream", "#f3eee2")
navy = M_("kj_navy", "#46447f")
navy_d = M_("kj_navy_d", "#383669")
lining = M_("kj_lining", "#3f3d74")
gold = M_("kj_gold", "#e8c170")
gold_d = M_("kj_gold_d", "#c79c4e")
red = M_("kj_red", "#e2455e")
sage = M_("kj_sage", "#8fbf7a")
ivory = M_("kj_ivory", "#f1ead9")
shoe = M_("kj_shoe", "#8a5b3d")
shoe_d = M_("kj_shoe_d", "#6b4530")
sole = M_("kj_sole", "#efe6d4")
shadow = M_("UNLIT_kj_shadow", "#17141f", unlit=True)

e = human.Human("kyoju", height=1.78, head=0.235, head_mat=shadow, skin="#f6dccb", segs=0.9, hand_q=0.9, head_q=0.55)
s = e.s
k = e.k

# ---- 교주 자세: 런타임 src/game/missions/act3kit/leaderPoses.ts와 같은 계산 (arm(), fingers()를 옮겼다)
REST_ARM = {"L": ((-0.64, -0.769, 0.0), (0.769, -0.64, 0.0), (0.0, 0.0, 1.0)),
            "R": ((-0.64, 0.769, 0.0), (-0.769, -0.64, 0.0), (0.0, 0.0, 1.0))}


def arm_pose(side, d, bend=(0, 0, 1), elbow=0.0, hand=0.0):
    """cinePoses.arm()과 같다: 위팔 방향(인물 공간 +X 왼쪽, +Y 위, +Z 앞) → three.js XYZ 오일러(도)."""
    y = V(d).normalized()
    z = V(bend)
    z = z - y * z.dot(y)
    if z.length_squared < 1e-6:
        z = V((0, 0, 1)) - y * y.z
    z.normalize()
    x = y.cross(z)
    T = Matrix((x, y, z)).transposed()
    R = Matrix(REST_ARM[side]).transposed()
    q = R.transposed() @ T
    m13 = max(-1.0, min(1.0, q[0][2]))
    ey = math.asin(m13)
    if abs(m13) < 0.9999999:
        ex = math.atan2(-q[1][2], q[2][2])
        ez = math.atan2(-q[0][1], q[0][0])
    else:
        ex = math.atan2(q[2][1], q[1][1])
        ez = 0.0
    r = lambda a: round(math.degrees(a), 1)  # noqa: E731
    return {f"upperarm_{side}": (r(ex), r(ey), r(ez)), f"forearm_{side}": (elbow, 0, 0), f"hand_{side}": (hand, 0, 0)}


def fingers(side, curl, index=None, thumb=None):
    ix = curl if index is None else index
    th = curl if thumb is None else thumb
    p = {f"f1_01_{side}": (70 * ix, 0, 0), f"f1_02_{side}": (80 * ix, 0, 0),
         f"thumb_01_{side}": (25 * th, 0, 0), f"thumb_02_{side}": (40 * th, 0, 0)}
    for f in ("f2", "f3"):
        p[f"{f}_01_{side}"] = (70 * curl, 0, 0)
        p[f"{f}_02_{side}"] = (80 * curl, 0, 0)
    return p


def merge(*ps):
    out = {}
    for p in ps:
        out.update(p)
    return out


# 왼손 목장 (leaderPoses.ts CROZIER_L): 목장은 이 자세에서 자루가 수직이 되도록 아래에서 맞춘다
STAND_L = merge(arm_pose("L", (0.14, -0.97, 0.12), (0, 0.35, 1), 72, 0), fingers("L", 0.85, thumb=0.6))
RELAXED_R = merge({"upperarm_R": (4, 0, 34), "forearm_R": (14, 0, 0), "hand_R": (6, 0, 0)}, fingers("R", 0.3))
BLESS_R = {"f1_01_R": (0, 0, 0), "f1_02_R": (0, 0, 0), "f2_01_R": (0, 0, 0), "f2_02_R": (0, 0, 0),
           "f3_01_R": (72, 0, 0), "f3_02_R": (82, 0, 0), "thumb_01_R": (24, 0, 0), "thumb_02_R": (40, 0, 0)}
POINT_R = fingers("R", 0.9, index=0, thumb=0.6)
POSES = {
    "kyoju_stand": merge(STAND_L, RELAXED_R, {"head": (-3, 0, 0)}),
    "kyoju_point": merge(STAND_L, arm_pose("R", (-0.25, 0.28, 1), (0, 1, 0), 6, -6), POINT_R,
                         {"chest": (-2, -8, 0), "head": (-6, -6, 0)}),
    "kyoju_bless": merge(STAND_L, arm_pose("R", (-0.12, -0.25, 1), (0, 1, 0.2), 78, -6), BLESS_R, {"head": (-4, 0, 0)}),
    "kyoju_raise": merge(arm_pose("L", (0.1, 0.06, 1), (0, 1, 0), 6, 0), fingers("L", 0.85, thumb=0.6),
                         arm_pose("R", (-0.38, -0.3, 1), (0, 1, 0), 12, -10), fingers("R", 0.1),
                         {"spine": (-2, 0, 0), "chest": (-4, 4, 0), "head": (-8, 4, 0)}),
}
POSE_STAND = POSES["kyoju_stand"]


def emblem(buf, M, size, *, w, depth=0.003, back=None):
    """교단 문장 [오리지널]: 금 잎 네 장 십자(아래 잎이 가장 길다) + 가운데 딸기형 붉은 보석. M 로컬: X-Z 평면, -Y 바깥.
    size = 위아래 전체 길이(m). back을 주면 금 테 + 그 재질의 둥근 받침판(메달) 위에 얹는다."""
    sc = size / 0.13
    Mx = M
    if back is not None:
        n_out = (M.to_3x3() @ V((0, -1, 0))).normalized()
        up = (M.to_3x3() @ V((0, 0, 1))).normalized()
        c0 = M @ V((0, 0, 0))
        disc(buf, c0, n_out, up, 0.064 * sc, 0.064 * sc, 0.003 * sc, segs=24, mat=gold_d, w=w)
        disc(buf, c0 + n_out * 0.003 * sc, n_out, up, 0.054 * sc, 0.054 * sc, 0.002 * sc, segs=24, mat=back, w=w)
        Mx = M @ Matrix.Translation((0, -0.005 * sc, 0))
    for ang, L in ((0.0, 0.050), (90.0, 0.040), (180.0, 0.064), (270.0, 0.040)):
        c2.prism(buf, [(x * sc, z * sc) for x, z in c3.leaf_poly(L, 0.026, n=5)], depth,
                 Mx @ Matrix.Rotation(math.radians(ang), 4, "Y"), mat=gold, w=w)
    c3.gem_drop(buf, Mx @ Matrix.Translation((0, -depth * 0.6, 0.0)), 0.011 * sc, red, depth=depth * 1.4,
                frame_mat=gold_d, frame_w=0.003 * sc, w=w)


def vstrip(buf, pts, nrm, ups, wid, th, mat, ws):
    """폭이 바뀌는 이어진 띠 (영대, 수대). ws: 점마다 웨이트."""
    rings = []
    for c, nn, u, wd, w in zip(pts, nrm, ups, wid, ws):
        hw = wd / 2
        quad = [c + u * hw, c + u * hw + nn * th, c - u * hw + nn * th, c - u * hw]
        rings.append([buf.vert(q, w) for q in quad])
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for a in range(4):
            b = (a + 1) % 4
            buf.face((r0[a], r0[b], r1[b], r1[a]), mat)
    buf.face(tuple(reversed(rings[0])), mat)
    buf.face(tuple(rings[-1]), mat)


# =========================================================================== 수단 (흰 사제복, 바닥까지)
HIP_Z = e.hipj_z


def cass_sec(z):
    if z >= HIP_Z:
        rx, ry, cy = e.torso_at(z)
        return rx + 0.016 * s, ry + 0.016 * s, cy
    rx0, ry0, cy0 = e.torso_at(HIP_Z)
    t = smoothstep(HIP_Z, 0.03 * s, z) ** 0.85
    return lerp(rx0 + 0.016 * s, 0.262 * s, t), lerp(ry0 + 0.016 * s, 0.218 * s, t), lerp(cy0, 0.012 * s, t)


CASS_Z = [z * s for z in (1.496, 1.476, 1.448, 1.410, 1.350, 1.270, 1.180, 1.075, 0.990, 0.925, 0.840, 0.720,
                          0.580, 0.440, 0.300, 0.160, 0.030)]
cass = human.Drape(e, white, CASS_Z, cass_sec, th=0.004 * s, cols=22, mat_in=white_d,
                   wfn=lambda q: human.skirt_w(e, q, legs=0.55))
cass.strip_row(navy, 0.022 * s, 0.003 * s)                 # 밑단 남색 띠
cass.done("cassock")
e.cover["torso"].append((e.crotch_z - 0.2, e.torso_top + 0.1))
for sd in ("L", "R"):
    e.cover[f"leg_{sd}"].append((-0.2, 1.2))


def cass_pt(z, a, lift=0.0):
    return cass.surface(z, a, lift)


# 앞 단추 (금, 목 아래부터 무릎 위까지)
def buttons(buf):
    for i in range(11):
        z = lerp(1.44 * s, 0.66 * s, i / 10)
        p, n = cass_pt(z, 0.0, 0.0008)
        disc(buf, p, n, (0, 0, 1), 0.0058 * s, 0.0058 * s, 0.0022 * s, segs=6, mat=gold, w=human.skirt_w(e, p))


e.part("buttons", "body", buttons)


# 남색 허리띠(파시아) + 왼쪽 앞으로 늘어진 두 자락 (금 술)
def fascia(buf):
    z = e.waist_z
    rx, ry, cy = cass_sec(z)
    band(buf, (0, cy, z), (0, 0, 1), (1, 0, 0), rx + 0.002 * s, ry + 0.002 * s, 0.062 * s, 0.005 * s, segs=28, p=2.3,
         mat=navy, w=e._torso_wfn(V((0, 0, z)), 0))
    for i, (a, ln) in enumerate(((34.0, 0.30), (44.0, 0.25))):
        pts, nrm, ups = [], [], []
        for j in range(6):
            zz = z - 0.02 * s - ln * s * j / 5
            p, n = cass_pt(zz, a, 0.008 * s + 0.003 * s * i)
            pts.append(p)
            nrm.append(n)
            ups.append(n.cross(V((0, 0, 1))).normalized())
        elf._loop(buf, pts, nrm, ups, 0.060 * s, 0.004 * s, mat=navy_d if i else navy, closed=False,
                  w=lambda t, zz0=z: human.skirt_w(e, V((0.08, 0, zz0 - 0.25 * t))))
        # 금 술: 끝에 짧은 막대 여럿
        pe, ne = pts[-1], nrm[-1]
        side = ups[-1]
        for f in range(5):
            o = side * ((f - 2) * 0.011 * s)
            loft(buf, [{"c": pe + o + ne * 0.002 * s, "rx": 0.0028 * s, "ry": 0.0028 * s, "w": {"hips": 1.0}},
                       {"c": pe + o + ne * 0.002 * s - V((0, 0, 0.040 * s)), "rx": 0.0020 * s, "ry": 0.0020 * s,
                        "w": {"hips": 1.0}}], segs=4, cap0="flat", cap1="flat", mat=gold)


e.part("fascia", "body", fascia)

# =========================================================================== 소매·손·신
e.sleeves(white, length=0.955, off=0.010, flare=0.022, cuff=(navy, 0.022, 0.0035))
e.hide_feet = True
q0 = e.q
e.q = 0.6                                                    # 신은 수단 자락 아래로 발끝만 보인다
for sd in ("L", "R"):
    e.add(e.foot(sd, shoe, sole=(sole, 0.020 * s), name=f"kyoju_shoe_{sd}"), group="body", tag=f"shoe_{sd}")
e.q = q0




# =========================================================================== 영대 (스톨): 목 뒤에서 앞으로 늘어진 남색 띠 두 가닥
STOLE_BOT = 0.43 * s


def stole(buf):
    for sg in (1, -1):
        pts, nrm, ups, wid = [], [], [], []
        zs = [1.488, 1.46, 1.42, 1.36, 1.29, 1.21, 1.13, 1.06, 0.99, 0.93, 0.86, 0.76, 0.66, 0.56, 0.48, 0.43]
        for i, z0 in enumerate(zs):
            z = z0 * s
            a = sg * lerp(36.0, 15.0, smoothstep(1.49 * s, 1.30 * s, z))
            p, n = cass_pt(z, a, 0.009 * s)
            if z < 1.06 * s:                              # 허리띠 위로 지나간다
                p = p + n * 0.006 * s
            pts.append(p)
            nrm.append(n)
            ups.append(n.cross(V((0, 0, 1))).normalized() * -sg)
            wid.append(lerp(0.064, 0.100, smoothstep(0.62 * s, 0.45 * s, z)) * s)
        ws = [human.skirt_w(e, p, legs=0.45) for p in pts]
        vstrip(buf, pts, nrm, ups, wid, 0.004 * s, navy, ws)
        for ee in (1, -1):                                   # 금 테두리 (양쪽 가장자리)
            q = [p + u * (ee * (wd / 2 - 0.004 * s)) + nn * 0.0035 * s for p, u, nn, wd in zip(pts, ups, nrm, wid)]
            vstrip(buf, q, nrm, ups, [0.006 * s] * len(q), 0.0015 * s, gold, ws)
        # 끝: 문장 + 금 술
        pe, ne, ue = pts[-1], nrm[-1], ups[-1]
        up = ne.cross(ue).normalized()
        if up.z < 0:
            up = -up
        Mx = Matrix.Translation(pts[-3] + nrm[-3] * 0.004 * s) @ frame(nrm[-3], (0, 0, 1))
        emblem(buf, Mx, 0.070 * s, w=ws[-3], depth=0.0025 * s)
        for f in range(5):
            o = ue * ((f - 2) * 0.019 * s)
            q = pe + o + ne * 0.002 * s - V((0, 0, 0.002 * s))
            loft(buf, [{"c": q, "rx": 0.0030 * s, "ry": 0.0030 * s, "w": ws[-1]},
                       {"c": q - V((0, 0, 0.032 * s)), "rx": 0.0022 * s, "ry": 0.0022 * s, "w": ws[-1]}],
                 segs=4, cap0="flat", cap1="flat", mat=gold)
        elf._loop(buf, [pe + ue * (0.050 * s) + ne * 0.002 * s, pe - ue * (0.050 * s) + ne * 0.002 * s], [ne, ne],
                  [V((0, 0, 1)), V((0, 0, 1))], 0.010 * s, 0.004 * s, mat=gold, closed=False, w=ws[-1])


e.part("stole", "body", stole)

# =========================================================================== 코프 (흰 망토, 남색 안감, 금 오프리)
COPE_TOP = 1.540 * s
SH_Z = 1.430 * s


def cope_sec(z):
    t = smoothstep(COPE_TOP, SH_Z, z) ** 0.5
    rx = lerp(0.099, 0.288, t) * s                           # 위는 두건 목에 붙는 깃 (속 안감이 앞으로 비치지 않게)
    ry = lerp(0.094, 0.184, t) * s
    cy = lerp(0.014, 0.022, t) * s
    b = smoothstep(SH_Z, 0.20 * s, z) ** 0.75
    return rx + (0.470 * s - rx) * b, ry + (0.400 * s - ry) * b, cy + 0.034 * s * b


COPE_ZS = [z * s for z in (1.540, 1.530, 1.514, 1.492, 1.462, 1.430, 1.390, 1.330, 1.250, 1.150, 1.030, 0.880, 0.720,
                           0.550, 0.380, 0.200)]
GAP = [(1.540, 40.0), (1.500, 48.0), (1.430, 56.0), (1.300, 58.0), (1.000, 58.0), (0.600, 60.0), (0.200, 62.0)]


def cope_gap(z):
    return keys(sorted((zz * s, g) for zz, g in GAP), z)


def cope_w(q):
    w = e._torso_wfn(V((q.x, q.y, max(q.z, e.chest_z))), 0)
    lo = smoothstep(1.10 * s, 0.40 * s, q.z)
    return mixw(w, {"chest": 0.55, "spine": 0.30, "hips": 0.15}, lo)


cope = human.Drape(e, cream, COPE_ZS, cope_sec, gap=cope_gap, th=0.005 * s, cols=24, p=2.2, mat_in=lining, wfn=cope_w)
OR_W = 0.068 * s
for side in (0, 1):
    cope.strip_edge(gold, OR_W, 0.0025 * s, side=side)
cope.strip_row(gold, 0.030 * s, 0.0022 * s)                   # 밑단
cope.strip_row(gold, 0.016 * s, 0.0022 * s, row=0, up=False)  # 윗단 (목둘레)


def cope_extras(buf):
    # 오프리 띠 위의 금 마름모 (양쪽 넷씩)
    for side in (0, 1):
        jj, jn = (0, 1) if side == 0 else (cope.cols - 1, cope.cols - 2)
        for i in (4, 7, 10, 13):
            p, n = cope.P[i][jj], cope.N[i][jj]
            d = (cope.P[i][jn] - p).normalized()
            Mx = Matrix.Translation(p + d * OR_W * 0.5 + n * 0.003 * s) @ frame(n, (0, 0, 1))
            c2.prism(buf, c2.diamond_poly(0.030 * s, 0.044 * s), 0.002 * s, Mx, mat=gold_d, w=cope.Wt[i][jj])
            c3.gem_drop(buf, Mx @ Matrix.Translation((0, -0.002 * s, 0)), 0.007 * s, red, depth=0.0025 * s,
                        w=cope.Wt[i][jj])
    # 등의 큰 문장 (금 테두리 원 안)
    z = 1.17 * s
    p, n = cope.surface(z, 180.0, 0.004 * s)
    Mx = Matrix.Translation(p) @ frame(n, (0, 0, 1))
    w = cope_w(p)
    ring = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        q, nn = cope.surface(z + 0.115 * s * math.sin(a), 180.0 + math.degrees(0.115 * s * math.cos(a) / 0.30), 0.004 * s)
        ring.append((q, nn))
    pts = [q for q, _ in ring]
    nrm = [nn for _, nn in ring]
    ups = [(pts[(i + 1) % 24] - pts[i - 1]).cross(nrm[i]).normalized() for i in range(24)]
    elf._loop(buf, pts, nrm, ups, 0.012 * s, 0.002 * s, mat=gold, closed=True, w=w)
    emblem(buf, Mx, 0.17 * s, w=w, depth=0.003 * s)


e.part("cope_extras", "body", cope_extras)
cope.done("cope")

# 가슴 여밈 금 걸쇠(모르스) + 가운데 문장 메달: 코프 두 오프리 띠를 잇는다
MORSE_Z = 1.395 * s


def morse(buf):
    g = cope_gap(MORSE_Z)
    pts, nrm, ups = [], [], []
    n_ = 13
    for i in range(n_):
        a = lerp(-g + 4.0, g - 4.0, i / (n_ - 1))
        rx, ry, cy = cope_sec(MORSE_Z)
        q, nn = human.elf_ring_pt(rx, ry, cy, MORSE_Z, a, 2.2)
        q2, _ = cass_pt(MORSE_Z, a, 0.030 * s)
        # 가운데는 가슴 앞 (영대 위), 양끝은 코프 가장자리
        t = abs(i / (n_ - 1) - 0.5) * 2
        p = q2.lerp(q, smoothstep(0.55, 1.0, t)) + nn * 0.004 * s
        pts.append(p)
        nrm.append(nn)
        ups.append(V((0, 0, 1)))
    w = e._torso_wfn(V((0, 0, MORSE_Z)), 0)
    elf._loop(buf, pts, nrm, ups, 0.034 * s, 0.006 * s, mat=gold, closed=False, w=w)
    c = pts[n_ // 2]
    Mx = Matrix.Translation(c + nrm[n_ // 2] * 0.006 * s) @ frame(nrm[n_ // 2], (0, 0, 1))
    emblem(buf, Mx, 0.105 * s, w=w, depth=0.004 * s, back=navy)


e.part("morse", "body", morse)

# =========================================================================== 두건 (흰 겉, 남색 안감): 얼굴 자리는 그림자로 비운다
HC = e.head_c


def head_surf(az, el, off):
    def f(a, b):
        x = math.cos(b) * math.sin(a)
        y = -math.cos(b) * math.cos(a)
        z = math.sin(b)
        return e._head_fn(x, y, z)
    a, b = math.radians(az), math.radians(el)
    p = f(a, b)
    d = 1e-3
    pa = f(a + d, b) - f(a - d, b)
    pb = f(a, min(b + d, math.pi / 2)) - f(a, max(b - d, -math.pi / 2))
    n = pa.cross(pb)
    if n.length < 1e-9 or abs(el) > 88:
        n = p - HC
    if n.dot(p - HC) < 0:
        n = -n
    n.normalize()
    return p + n * off, n


EL_ROWS = [86, 72, 58, 46, 38, 28, 18, 8, -2, -12, -22, -32, -41, -50]
OPEN_C, OPEN_R, OPEN_G = -4.0, 42.0, 56.0


def hood_gap(el):
    t = (el - OPEN_C) / OPEN_R
    return OPEN_G * math.sqrt(max(0.0, 1 - t * t)) ** 0.8 if abs(t) < 1 else 0.0


def hood(buf):
    cols = 21
    rows = []
    for el in EL_ROWS:
        g = hood_gap(el)
        off = (0.016 + 0.006 * smoothstep(20, 80, el)) * s
        ring = []
        for j in range(cols):
            az = g + (360.0 - 2 * g) * j / (cols - 1)
            p, n = head_surf(az, el, off)
            ring.append((p, n, {"head": 1.0}))
        rows.append(ring)
    # 목 아래로 (턱 밑을 감싸고 목을 따라 코프 깃 안으로)
    # 수단 깃(맨 위 반경 약 0.078) 바로 바깥을 지나 수단 안으로 들어간다: 두건 끝과 깃 사이 틈이 보이지 않게
    neck = [(e.chin - 0.008 * s, 0.073, 0.080, 0.000), (e.chin - 0.024 * s, 0.079, 0.083, 0.008),
            (1.502 * s, 0.083, 0.084, 0.014), (1.470 * s, 0.080, 0.081, 0.014)]
    for i, (z, rx, ry, cy) in enumerate(neck):
        ring = []
        t = i / (len(neck) - 1)
        w = mixw({"head": 1.0}, {"neck": 1.0}, smoothstep(0.0, 0.5, t))
        w = mixw(w, {"chest": 1.0}, smoothstep(0.5, 1.0, t))
        for j in range(cols):
            az = 360.0 * j / (cols - 1)
            q, n = human.elf_ring_pt(rx * s, ry * s, cy * s, z, az, 2.0)
            ring.append((q, n, w))
        rows.append(ring)
    th = 0.004 * s
    o = [[buf.vert(p, w) for p, n, w in r] for r in rows]
    ii = [[buf.vert(p - n * th, w) for p, n, w in r] for r in rows]
    R = len(rows)
    for i in range(R - 1):
        for j in range(cols - 1):
            buf.face((o[i][j], o[i + 1][j], o[i + 1][j + 1], o[i][j + 1]), white)
            buf.face((ii[i][j], ii[i][j + 1], ii[i + 1][j + 1], ii[i + 1][j]), lining)
    for i in range(R - 1):                                   # 열린 가장자리 두께
        for j0, jn in ((0, 0), (cols - 1, cols - 1)):
            if j0 == 0:
                buf.face((o[i][0], ii[i][0], ii[i + 1][0], o[i + 1][0]), lining)
            else:
                buf.face((o[i][jn], o[i + 1][jn], ii[i + 1][jn], ii[i][jn]), lining)
    for j in range(cols - 1):                                # 아래 끝단
        buf.face((o[R - 1][j], o[R - 1][j + 1], ii[R - 1][j + 1], ii[R - 1][j]), lining)
    top = buf.vert(HC + V((0, 0, e.hh / 2 + 0.024 * s)), {"head": 1.0})
    for j in range(cols - 1):
        buf.face((top, o[0][j], o[0][j + 1]), white)
    # 얼굴 테두리 금 선 (열린 가장자리를 따라)
    for side in (0, cols - 1):
        pts, nrm, ups = [], [], []
        for i, el in enumerate(EL_ROWS):
            if hood_gap(el) <= 0.0 and not (i > 0 and hood_gap(EL_ROWS[i - 1]) > 0) and \
                    not (i + 1 < len(EL_ROWS) and hood_gap(EL_ROWS[i + 1]) > 0):
                continue
            p, n, _ = rows[i][side]
            jn = 1 if side == 0 else cols - 2
            d = (rows[i][jn][0] - p).normalized()
            pts.append(p + d * 0.006 * s + n * 0.0006)
            nrm.append(n)
            ups.append(d)
        if len(pts) > 1:
            elf._loop(buf, pts, nrm, ups, 0.010 * s, 0.0016 * s, mat=gold, closed=False, w={"head": 1.0})


elf._weld(e.part("hood", "head", hood), 1e-5)        # 닫힌 행의 앞 이음매 정점을 붙인다

# =========================================================================== 미트라
MZ = HC.z + math.sin(math.radians(36.0)) * e.hh / 2          # 밑동 높이 (얼굴 자리 위)
MH = 0.330 * s                                               # 밑동 위 판 높이
MB = 0.058 * s                                               # 금 띠(키르쿨루스) 높이


def mitre_base():
    """밑동 타원: 두건 표면의 그 높이 단면 + 여유."""
    best = [0.0, 0.0, 0.0, 0.0]
    for az in range(0, 360, 10):
        el = math.degrees(math.asin(max(-1, min(1, (MZ - HC.z) / (e.hh / 2)))))
        p, _n = head_surf(az, el, (0.016 + 0.006 * smoothstep(20, 80, el)) * s)
        best[0] = max(best[0], p.x)
        best[1] = min(best[1], p.y)
        best[2] = max(best[2], p.y)
    rx = best[0] + 0.007 * s
    ry = (best[2] - best[1]) / 2 + 0.007 * s
    cy = (best[2] + best[1]) / 2
    return rx, ry, cy


MRX, MRY, MCY = mitre_base()
AS = 82.0                                                    # 판 하나가 덮는 반각


def panel_U(v):
    """높이 비율 v에서 판의 남은 반폭 비율 (뾰족한 아치)."""
    v0 = 0.36
    if v <= v0:
        return 1.0
    t = (v - v0) / (1 - v0)
    return max(0.0, math.cos(math.pi / 2 * t ** 1.25)) ** 0.85


def panel_pt(front, u, v):
    a = u * AS + (0.0 if front else 180.0)
    q, n = human.elf_ring_pt(MRX, MRY, MCY, MZ, a, 2.0)
    xs = 1.0 + 0.16 * math.sin(math.pi * min(v / 0.75, 1.0)) * (1 - 0.3 * v)
    flat = 1.0 - 0.84 * v ** 0.75
    p = V((q.x * xs, MCY + (q.y - MCY) * flat, MZ + v * (MH + MB)))
    nn = V((q.x * 0.35, (q.y - MCY), 0.0)).normalized()
    return p, nn


def mitre(buf):
    w = {"head": 1.0}
    NR, NC = 10, 10
    th = 0.006 * s
    for front in (True, False):
        grid = []
        for i in range(NR + 1):
            v = i / NR
            U = panel_U(v)
            grid.append([panel_pt(front, U * (2 * j / NC - 1), v) for j in range(NC + 1)])
        o = [[buf.vert(p, w) for p, n in r] for r in grid]
        ii = [[buf.vert(p - n * th, w) for p, n in r] for r in grid]
        for i in range(NR):
            for j in range(NC):
                if front:
                    buf.face((o[i][j], o[i][j + 1], o[i + 1][j + 1], o[i + 1][j]), white)
                    buf.face((ii[i][j], ii[i + 1][j], ii[i + 1][j + 1], ii[i][j + 1]), lining)
                else:
                    buf.face((o[i][j], o[i + 1][j], o[i + 1][j + 1], o[i][j + 1]), white)
                    buf.face((ii[i][j], ii[i][j + 1], ii[i + 1][j + 1], ii[i + 1][j]), lining)
        for i in range(NR):                                   # 판 가장자리 두께
            for j in (0, NC):
                a, b = (o[i][j], o[i + 1][j]), (ii[i][j], ii[i + 1][j])
                if (j == 0) == front:
                    buf.face((a[0], b[0], b[1], a[1]), white_d)
                else:
                    buf.face((a[0], a[1], b[1], b[0]), white_d)
        # 금 테두리 (아치 윤곽: 왼쪽 위로 → 꼭대기 → 오른쪽 아래로)
        pts, nrm, ups = [], [], []
        i0 = max(1, int(round(NR * MB / (MH + MB))))
        for i in range(i0, NR + 1):
            p, n = grid[i][0]
            q, _ = grid[i][1]
            pts.append(p + n * 0.0015)
            nrm.append(n)
            ups.append((q - p).normalized() if (q - p).length > 1e-6 else V((0, 0, -1)))
        for i in range(NR - 1, i0 - 1, -1):
            p, n = grid[i][NC]
            q, _ = grid[i][NC - 1]
            pts.append(p + n * 0.0015)
            nrm.append(n)
            ups.append((q - p).normalized())
        # 테두리 띠는 판 안쪽으로 폭을 둔다
        pts2 = [p + u * 0.007 * s for p, u in zip(pts, ups)]
        elf._loop(buf, pts2, nrm, ups, 0.014 * s, 0.002 * s, mat=gold, closed=False, w=w)
        # 가운데 세로 띠 (티툴루스)
        mid = NC // 2
        pts, nrm, ups = [], [], []
        for i in range(i0, NR):
            p, n = grid[i][mid]
            q1, _ = grid[i][mid + 1]
            q0, _ = grid[i][mid - 1]
            pts.append(p + n * 0.0016)
            nrm.append(n)
            ups.append((q1 - q0).normalized())
        elf._loop(buf, pts, nrm, ups, 0.030 * s, 0.002 * s, mat=gold, closed=False, w=w)
        # 문장: 앞판에만
        if front:
            p, n = panel_pt(front, 0.0, 0.44)
            Mx = Matrix.Translation(p + n * 0.0035 * s) @ frame(n, (0, 0, 1))
            emblem(buf, Mx, 0.140 * s, w=w, depth=0.0035 * s)
    # 밑동 금 띠 (닫힌 고리) + 앞의 보석
    band(buf, (0, MCY, MZ + MB / 2), (0, 0, 1), (1, 0, 0), MRX * 1.005, MRY * 1.005, MB, 0.006 * s, segs=24, mat=gold,
         w=w)
    for a, r in ((0.0, 0.011), (42.0, 0.007), (-42.0, 0.007)):
        q, n = human.elf_ring_pt(MRX * 1.005 + 0.006 * s, MRY * 1.005 + 0.006 * s, MCY, MZ + MB / 2, a, 2.0)
        c3.gem_drop(buf, Matrix.Translation(q + n * 0.001) @ frame(n, (0, 0, 1)), r * s, red, depth=0.004 * s,
                    frame_mat=gold_d, frame_w=0.0025 * s, w=w)


e.part("mitre", "head", mitre)


# 수대 (라펫): 미트라 뒤 밑동에서 두건·코프 등으로 늘어진 두 띠 (금 테두리, 끝에 금 술과 작은 문장)
def lappets(buf):
    for sg in (1, -1):
        x0 = sg * 0.040 * s
        pts, nrm, ups, ws = [], [], [], []
        zs = [MZ + 0.012 * s - i * 0.031 * s for i in range(11)]
        for i, z in enumerate(zs):
            # 그 높이의 뒤쪽 바깥면: 두건(머리) → 목 → 코프 깃
            y = 0.0
            if z > e.chin:
                el = math.degrees(math.asin(max(-1, min(1, (z - HC.z) / (e.hh / 2)))))
                az = 180.0 - math.degrees(math.atan2(x0, 0.1))
                p, _n = head_surf(az, el, (0.016 + 0.006 * smoothstep(20, 80, el) + 0.006) * s)
                y = p.y
            else:
                y = 0.092 * s + 0.014 * s
            if z < COPE_TOP + 0.01 * s:
                rx, ry, cy = cope_sec(min(z, COPE_TOP))
                y = max(y, cy + ry * math.sqrt(max(0.0, 1 - (x0 / rx) ** 2)) + 0.010 * s)
            p = V((x0, y + 0.004 * s, z))
            pts.append(p)
            nrm.append(V((0, 1, 0)))
            ups.append(V((1, 0, 0)))
            t = i / (len(zs) - 1)
            ws.append(mixw({"head": 1.0}, {"chest": 1.0}, smoothstep(0.35, 0.8, t)))
        # 법선을 경로에 맞춘다
        for i in range(len(pts)):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, len(pts) - 1)]
            tan = (b - a).normalized()
            nrm[i] = V((1, 0, 0)).cross(tan).normalized()
            if nrm[i].y < 0:
                nrm[i] = -nrm[i]
        vstrip(buf, pts, nrm, ups, [0.046 * s] * len(pts), 0.003 * s, white, ws)
        for ee in (1, -1):
            q = [p + V((ee * 0.019 * s, 0, 0)) + nn * 0.0025 * s for p, nn in zip(pts, nrm)]
            vstrip(buf, q, nrm, ups, [0.006 * s] * len(q), 0.0012 * s, gold, ws)
        pe, ne = pts[-1], nrm[-1]
        for f in range(5):
            q = pe + V(((f - 2) * 0.0095 * s, 0, 0)) + ne * 0.002 * s
            loft(buf, [{"c": q, "rx": 0.0028 * s, "ry": 0.0028 * s, "w": ws[-1]},
                       {"c": q - V((0, 0, 0.028 * s)), "rx": 0.0020 * s, "ry": 0.0020 * s, "w": ws[-1]}],
                 segs=4, cap0="flat", cap1="flat", mat=gold)


e.part("lappets", "head", lappets)

e.finalize()


# =========================================================================== 목장 (크로지어): 별도 노드 kyoju_crozier
def crozier():
    """로컬: 원점 = 파지점, 자루 = +Z(위: 고둥) / -Z(아래: 물미). 고둥은 로컬 +Y 쪽으로 말린다. 단위 m."""
    b = Buf()
    w = {}

    def tube(z0, z1, r0, r1, mat, segs=10):
        loft(b, [{"c": V((0, 0, z0 * s)), "rx": r0 * s, "ry": r0 * s, "w": w},
                 {"c": V((0, 0, z1 * s)), "rx": r1 * s, "ry": r1 * s, "w": w}], segs=segs, cap0="flat", cap1="flat",
             mat=mat)
    tube(-0.985, 0.700, 0.0135, 0.0135, ivory)
    loft(b, [{"c": V((0, 0, -0.985 * s)), "rx": 0.016 * s, "ry": 0.016 * s, "w": w},
             {"c": V((0, 0, -1.010 * s)), "rx": 0.012 * s, "ry": 0.012 * s, "w": w},
             {"c": V((0, 0, -1.030 * s)), "rx": 0.003 * s, "ry": 0.003 * s, "w": w}], segs=8, cap0="flat", cap1="flat",
         mat=gold)                                             # 물미
    for z in (-0.62, -0.20, 0.16):                             # 금 고리
        tube(z - 0.010, z + 0.010, 0.0175, 0.0175, gold)
    # 마디 (매듭): 둥근 금 마디 + 위아래 테
    loft(b, [{"c": V((0, 0, z * s)), "rx": r * s, "ry": r * s, "w": w} for z, r in
             ((0.560, 0.015), (0.575, 0.024), (0.600, 0.036), (0.630, 0.040), (0.660, 0.036), (0.685, 0.024),
              (0.700, 0.017))], segs=12, cap0="flat", cap1="flat", mat=gold)
    for ang in range(0, 360, 90):                              # 마디 둘레 작은 보석 넷
        a = math.radians(ang)
        n = V((math.cos(a), math.sin(a), 0))
        c3.gem_drop(b, Matrix.Translation(V((0, 0, 0.630 * s)) + n * 0.039 * s) @ frame(n, (0, 0, 1)), 0.008 * s, red,
                    depth=0.003 * s, w=w)
    # 고둥: 자루 꼭대기에서 위로 솟아 바깥(+Y)으로 말리며 안으로 감긴다 (1.2바퀴)
    C = V((0, 0.090 * s, 0.840 * s))
    R0 = 0.090 * s
    pts = [V((0, 0, 0.700 * s)), V((0, 0, 0.760 * s))]
    n = 26
    for i in range(n + 1):
        t = i / n
        th = math.radians(180.0 - 420.0 * t)
        r = R0 * (1 - 0.62 * t)
        pts.append(C + V((0, r * math.cos(th), r * math.sin(th))))
    st = []
    for i, p in enumerate(pts):
        t = i / (len(pts) - 1)
        rr = lerp(0.0150, 0.0085, t) * s
        st.append({"c": p, "rx": rr, "ry": rr, "w": w, "ref": (1, 0, 0)})
    loft(b, st, segs=10, cap0="flat", cap1="round", mat=gold)
    # 고둥 바깥 잎 장식 셋 (크로켓)
    for t in (0.18, 0.40, 0.62):
        th = math.radians(180.0 - 420.0 * t)
        r = R0 * (1 - 0.62 * t)
        p = C + V((0, r * math.cos(th), r * math.sin(th)))
        out = V((0, math.cos(th), math.sin(th)))
        Ml = Matrix.Translation(p + out * 0.010 * s) @ frame(V((1, 0, 0)), out)
        c2.prism(b, [(x * s, z * s) for x, z in c3.leaf_poly(0.040, 0.022, n=4)], 0.004 * s,
                 Ml @ Matrix.Translation((0, 0.002 * s, 0)), mat=gold, w=w)
    # 고둥 안: 세계수 새싹(잎 둘) + 딸기형 보석 (양면)
    for xx in (1, -1):
        Mg = Matrix.Translation(C + V((xx * 0.004 * s, 0.006 * s, -0.004 * s))) @ frame(V((xx, 0, 0)), (0, 0, 1))
        c3.gem_drop(b, Mg, 0.020 * s, red, depth=0.005 * s, frame_mat=gold_d, frame_w=0.003 * s, w=w)
    stem0 = C + V((0, 0.004 * s, -0.030 * s))
    for ang in (38.0, -38.0):
        Ml = Matrix.Translation(stem0) @ frame(V((1, 0, 0)), (0, math.sin(math.radians(ang)), math.cos(math.radians(ang))))
        c2.prism(b, [(x * s, z * s) for x, z in c3.leaf_poly(0.034, 0.018, n=4)], 0.003 * s,
                 Ml @ Matrix.Translation((0, 0.0015 * s, 0)), mat=sage, w=w)
    ob = b.obj("kyoju_crozier_mesh", angle=35.0)
    return ob


cz = crozier()
arm = e.arm_obj


def posed_socket(pose):
    """자세를 걸어 socket_hand_L의 월드 행렬을 읽는다 (three.js XYZ 오일러 = Blender 'ZYX'). 끝나면 레스트로 되돌린다."""
    for pb in arm.pose.bones:
        pb.rotation_mode = "ZYX"
        pb.rotation_euler = (0, 0, 0)
    for bn, r in pose.items():
        arm.pose.bones[bn].rotation_euler = tuple(math.radians(x) for x in r)
    bpy.context.view_layer.update()
    m = bpy.data.objects["socket_hand_L"].matrix_world.copy()
    for pb in arm.pose.bones:
        pb.rotation_euler = (0, 0, 0)
        pb.rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()
    return m


Ms = posed_socket(POSE_STAND)
grip = Ms.translation.copy()
# 자세에서 자루가 수직(+Z), 고둥은 교주의 왼쪽 바깥(+X)으로 말리게
Zw = V((0, 0, 1))
Yw = V((1.0, 0.0, 0.0))
Xw = Yw.cross(Zw).normalized()
Mw = Matrix((Xw, Yw, Zw)).transposed().to_4x4()
Mw.translation = grip
print(f"[kyoju] stand grip = ({grip.x:.3f}, {grip.y:.3f}, {grip.z:.3f})  socket Z = {tuple(round(x, 3) for x in Ms.to_3x3().col[2])}")
# 레스트 포즈에서의 배치 = 소켓 레스트 행렬 @ (자세 소켓⁻¹ @ 원하는 월드 배치)
local = Ms.inverted() @ Mw
sock = bpy.data.objects["socket_hand_L"]
c3.socket_prop(e, cz, "socket_hand_L", sock.matrix_world @ local, name="crozier", outline=0.003,
               props={"grip": "0,0,0", "tip": "0,0,%.3f" % (-1.03 * s)})

# 런타임 (src/game/npc/Npc.ts): 충돌 캡슐은 미트라 아랫부분까지(2.0 m, 반지름 0.27: 코프 자락), 목장 든 왼팔은 걸어도 흔들지
# 않고 손목으로 목장을 곧게 세운다(steadyArm), 바닥까지 오는 수단 밑으로 신이 튀어나오지 않게 보폭을 줄인다(strideScale)
e.export("characters/kyoju.glb", props={"human": 1, "npcHeight": round(2.0 * s, 3), "npcRadius": round(0.27 * s, 3),
                                        "steadyArm": "L", "strideScale": 0.6})

# ---- 미리보기 (KYOJU_PREVIEW=1): 자세 액션 + 옆에 엘프(네르) 한 명을 세운 비교 glb → public/models/_tmp/ (커밋하지 않음)
#   KYOJU_PREVIEW=1 npm run model -- art/blender/characters/kyoju.py
#   npm run shot -- _tmp/kyoju_preview.glb --anim kyoju_stand
if os.environ.get("KYOJU_PREVIEW"):
    arm.animation_data_create()
    for name, pose in POSES.items():
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        arm.animation_data.action = act
        for pb in arm.pose.bones:
            pb.rotation_mode = "ZYX"
        for f in (1, 2):
            for pb in arm.pose.bones:
                pb.rotation_euler = tuple(math.radians(x) for x in pose.get(pb.name, (0, 0, 0)))
                pb.keyframe_insert("rotation_euler", frame=f)
        tr = arm.animation_data.nla_tracks.new()
        tr.name = name
        tr.strips.new(name, 1, act)
        tr.mute = True
    arm.animation_data.action = None
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(cb.MODELS_DIR, "characters", "ner.glb"))
    for o in set(bpy.context.scene.objects) - before:
        if o.parent is None:
            o.location.x -= 0.85
    cb.export("_tmp/kyoju_preview.glb")
