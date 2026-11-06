"""교주의 리볼버 「코코」 (2017년 신형 콜트 코브라, .38 스페셜 +P 2인치 단총신 더블액션 6연발).

[오리지널] 2026-11-04 사용자 지시 「교주에게 콜트 코브라(코코)를 모델링해서 쥐어줘. 선 채로 한손으로 사격하게끔. 원래 시즌3 시점에서
있으면 안되는 물건이지만 아무리 그래도 맨몸으로 전장을 돌아다니는것도 이상하거든.」 → 교주가 오른손에 쥔다 (목장은 왼손 그대로).
원작 시즌3 시점에 있을 물건이 아니다(사용자가 알고 허락한 시대착오). 교주 차원 병기가 아니라 지구의 권총이라 엘프 로고를 넣지 않는다.
2026-11-04 사용자 「트릭컬에서 콜트 코브라는 신형 콜트 코브라야. 이건 구형이잖아.」 → 1950~81년 구형(호두나무 손잡이, 드러난 이젝터
로드, 경사 가늠쇠)을 2017년 신형으로 다시 만들었다. [원작] 코코는 「2017년 개량형 콜트 코브라와 비슷하게 생겼고」, 낡고 희미한 각인
(「코ㄷ 코ㅁㄹ」)을 보고 마요가 「코코」라고 이름 붙였다 (나무위키 교주(트릭컬 리바이브)).

형태 (2017 코브라 제원: 전장 7.2", 높이 4.9", 폭 1.4", 2인치 총열, 무광 스테인리스, 호그 오버몰드 손잡이, 빨간 파이버 가늠쇠,
프레임 홈 가늠자). 옆모습은 실물 옆 사진의 외곽선을 실측 비율로 옮겼다 (1 px = 0.278 mm, 사진은 저장소에 넣지 않았다).
  총열 + 이젝터 덮개(슈라우드): 총열과 밑 덮개가 한 덩어리, 총구까지 덮개가 이어진다. 왼쪽에 이젝터 로드가 보이는 긴 홈
  가늠쇠: 낮은 검은 날 위에 빨간 파이버 막대 (뒤에서 빨간 점)
  프레임: 두꺼운 탑스트랩 위에 가늠자 홈(트렌치), 공이치기 뒤 프레임 등이 손잡이 위로 내려온다, 왼쪽 옆판 나사
  실린더 걸쇠: 실린더 뒤 왼쪽의 알약 모양 손잡이 (뒤로 당긴다)
  실린더: 6연발, 앞쪽으로 치우친 긴 홈(플루트) 여섯
  방아쇠울: 크고 둥근 고리 (앞과 밑이 둥글고 앞이 두껍다, 장갑 낀 손가락), 방아쇠는 가늘게 휘어 끝이 앞으로 말린다
  공이치기: 위로 휘어 올라간 갈고리형 박차 + 빗살
  손잡이: 검은 고무 호그 오버몰드 (앞면 손가락 홈 셋, 뒤는 등판을 덮고 밑으로 갈수록 뒤로 부푼다, 오돌토돌한 결)
  각인: 총열 왼쪽 「COBRA」와 「.38 SPL +P」를 낡아 희미하게 (원작: 낡고 희미한 각인). 말 문장(로고)·상호는 넣지 않았다.

움직이는 파츠 (three.js 부모 공간 기준 축은 런타임 src/game/missions/act3kit/kyojuGun.ts가 쓴다)
  crane    실린더 팔 (실린더 앞 아래, 총열과 나란한 축으로 돌아 실린더가 왼쪽으로 나온다)
  cylinder crane의 자식, 제 축으로 60°씩 돈다 (한 발마다). 이젝터 로드·꼭지 포함 (닫히면 덮개 홈 속)
  hammer   공이치기 (뒤로 젖혀졌다 떨어진다)
  trigger  방아쇠

npm run model -- art/blender/weapons/kyoju/colt_cobra.py
npm run shot -- weapons/kyoju/colt_cobra.glb --views side,34,34r,front
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("colt_cobra")

LINE_DARK = hw.LINE_DARK
# 무광 스테인리스 (2017 코브라의 마감): 공이치기·방아쇠·걸쇠는 같은 스테인리스를 조금 밝게(광택)
STEEL = cb.mat("cc_steel", "#a2a6ae", line=hw.LINE, roughness=0.6)        # 무광 스테인리스 (프레임·총열·실린더)
POLISH = cb.mat("cc_polish", "#c3c6cc", line=hw.LINE, roughness=0.35)     # 광택 스테인리스 (공이치기·방아쇠·걸쇠)
ETCH = cb.mat("cc_etch", "#868a93", line=hw.LINE, roughness=0.6)          # 낡아 희미한 각인
RUBBER = cb.mat("cc_rubber", "#25262a", line=LINE_DARK, roughness=0.85)   # 호그 오버몰드 고무 손잡이
RUBBER_D = cb.mat("cc_rubber_d", "#35363c", line=LINE_DARK, roughness=0.9)  # 고무의 오돌토돌한 결
RED = cb.mat("cc_red", "#e8303a", line=hw.LINE, roughness=0.3)            # 파이버 옵틱 가늠쇠
GOLD = "gold"     # 약실 속 탄피
DARK = "dark"     # 총구, 약실, 홈, 가늠쇠 날

# ------------------------------------------------------------------ 실측 좌표 (옆 사진 px → m)
# 사진의 왼쪽 옆모습(총구 왼쪽)을 그대로 쓴다: x px가 커질수록 뒤(-Y), y px가 커질수록 아래(-Z).
# 실린더 앞면(x 288)을 Y 0.019, 총열 축(y 73)을 Z 0.064에 둔다 (옛 모델과 같은 기준: 마지막에 파지점으로 옮긴다)
S = 0.000278


def P(xo, yo):
    return ((288 - xo) * S + 0.019, (73 - yo) * S + 0.064)


def PL(pts):
    return [P(x, y) for x, y in pts]


BZ = 0.064                  # 총열 축 높이
CY1 = P(288, 0)[0]          # 실린더 앞
CY0 = P(437, 0)[0]          # 실린더 뒤
CZ = P(0, 120)[1]           # 실린더 축
CR = 68 * S                 # 실린더 반지름 (0.0189)
BC = BZ - CZ                # 약실 원 반지름 (위 약실 = 총열 축)
TOP = P(0, 33)[1]           # 탑스트랩 윗면
MUZ = P(102, 0)[0]          # 총구
BR = 0.0100                 # 총열 반지름 (윗면 y 37)
W = 0.0220                  # 프레임 두께
SW = 0.0090                 # 총열·덮개 반폭
SB = P(0, 133)[1]           # 덮개 밑면
ROD_R = 0.0013              # 이젝터 로드
SLOT_R = 0.0031             # 덮개 홈 (로드가 지나는 길)

# ================================================================== 프레임
# 앞 기둥 (총열 뿌리), 탑스트랩, 실린더 밑 띠, 뒤 덩어리 (공이치기 둘레 → 손잡이 위 등판), 실린더 뒤 방패(원판)
g.s(hw.side("frame_front", PL([(226, 33), (292, 33), (292, 106), (232, 106), (228, 80)]), 2 * SW, bevel=0.0018,
            seg=2, mat=STEEL))
g.s(hw.boxr("topstrap", -0.0074, 0.0074, CY0 - 0.004, P(288, 0)[0] + 0.0015, P(0, 52)[1], TOP, bevel=0.0024,
            mat=STEEL))
g.s(hw.side("frame_bottom", PL([(286, 190), (440, 190), (440, 226), (305, 226), (290, 221), (286, 214)]), W,
            bevel=0.0018, seg=2, mat=STEEL))
rear = [(432, 33), (452, 34), (461, 41), (471, 58), (482, 79), (495, 96), (512, 108), (534, 117), (552, 123),
        (557, 140), (556, 165), (549, 186), (533, 202), (510, 213), (488, 221), (470, 226), (432, 226)]
g.s(hw.side("frame_rear", PL(rear), W, bevel=0.0026, seg=2, mat=STEEL))
g.s(hw.ycyl("recoil_shield", CR - 0.0012, CY0 - 0.0040, CY0 - 0.0004, z=CZ, verts=32, bevel=0.0012, mat=STEEL))
# 공이치기 길 (프레임 등 위의 홈: 젖혀진 공이치기가 들어간다)
g.f(hw.decal("hammer_slot", hw.rrect(0.0062, 0.016, 0.0010, 1), (0, *P(478, 62)), mat=DARK,
             right=(1, 0, 0), up=(0, -0.55, -0.83)))
# 가늠자 홈 (탑스트랩 위 트렌치: 실린더 위에서 뒤끝까지)
yA, yB = P(300, 0)[0], P(452, 0)[0]
g.f(hw.decal("rear_trench", hw.rrect(0.0030, yA - yB, 0.0010, 1), (0, (yA + yB) / 2, TOP), mat=DARK, **hw.TOP))
# 왼쪽 옆판 나사 셋 + 실린더 밑 나사 (오른쪽은 하나)
for sx, fr, pts in ((-1, hw.LEFT, ((338, 205), (520, 150), (470, 200))), (1, hw.RIGHT, ((338, 205),))):
    for k, (xo, yo) in enumerate(pts):
        y, z = P(xo, yo)
        g.f(hw.decal(f"screw{sx}{k}", hw.circle(0.0018, 12), (sx * W / 2, y, z), mat=POLISH, **fr))
        g.f(hw.decal(f"screw_slot{sx}{k}", hw.rrect(0.0030, 0.0005, 0.0002, 1), (sx * W / 2, y, z), lift=0.0010,
                     mat=DARK, **fr))

# ================================================================== 실린더 걸쇠 (왼쪽, 알약 모양: 뒤로 당긴다)
LATCH_Z = P(0, 114)[1]
ly0, ly1 = P(505, 0)[0], P(452, 0)[0]
g.s(hw.ycyl("latch", 0.0040, ly0, ly1, x=-W / 2 - 0.0008, z=LATCH_Z, verts=20, bevel=0.0028, seg=3, mat=POLISH))
for i in range(5):
    y = ly1 - 0.0016 - i * 0.0022
    g.f(hw.decal(f"latch_ser{i}", hw.rrect(0.0006, 0.0050, 0.0002, 1), (-W / 2 - 0.0008 - 0.0040, y, LATCH_Z),
                 mat=DARK, right=(0, -1, 0), up=(0, 0, 1), lift=0.0002))

# ================================================================== 총열 + 이젝터 덮개 (한 덩어리, 총구까지)
# 단면: 둥근 윗면(총열) + 곧은 옆면 + 밑 덮개. 왼쪽 아래에 로드가 지나는 홈 (실린더가 왼쪽으로 열릴 때 로드가 빠져나간다)
SLOT_T, SLOT_B = P(0, 108)[1], P(0, 129)[1]
sec = []
for i in range(13):                                     # 윗면 반원 (오른쪽 → 왼쪽)
    a = math.pi * i / 12
    sec.append((SW * math.cos(a), BZ + 0.0010 + SW * math.sin(a)))
sec += [(-SW, SLOT_T), (-0.0012, SLOT_T)]                # 왼쪽 벽 → 홈 천장
for i in range(1, 10):                                  # 홈 안쪽 (로드 둘레를 시계 방향으로)
    a = math.radians(105 - 210 * i / 10)
    sec.append((SLOT_R * math.cos(a), CZ + SLOT_R * math.sin(a)))
sec += [(-0.0012, SLOT_B), (-SW + 0.0004, SLOT_B), (-SW + 0.0004, SB + 0.0018), (-SW + 0.0022, SB),
        (SW - 0.0022, SB), (SW, SB + 0.0022)]
yS0 = P(232, 0)[0]
g.s(hw.section("barrel_shroud", sec, yS0, MUZ, bevel=0.0020, seg=2, mat=STEEL, angle=35))
# 홈 앞끝 (총구 쪽 5 mm는 막혀 있다)
g.s(hw.boxr("slot_cap", -SW + 0.0004, -0.0008, P(120, 0)[0], MUZ, SLOT_B - 0.0002, SLOT_T + 0.0002, bevel=0.0010,
            mat=STEEL))
# 총열 뿌리 띠 (프레임에 물리는 자리)
g.s(hw.ycyl("barrel_band", BR + 0.0002, yS0 - 0.0010, P(212, 0)[0], z=BZ + 0.0002, verts=28, bevel=0.0008,
            mat=STEEL))
g.f(hw.decal("bore", hw.circle(0.0046, 18), (0, MUZ, BZ), mat=DARK, **hw.FRONT))
g.f(hw.ring_decal("crown", (0, MUZ, BZ), 0.0064, 0.0050, mat=ETCH, lift=0.0004, **hw.FRONT))
# 홈 그늘: 홈 안쪽 벽에 어두운 얇은 안감 (왼쪽에서 보면 로드 뒤가 어둡다, 사진의 검은 창)
liner = [((SLOT_R - 0.00005) * math.cos(math.radians(a)), CZ + (SLOT_R - 0.00005) * math.sin(math.radians(a)))
         for a in range(105, -106, -15)]
liner += [((SLOT_R - 0.0004) * math.cos(math.radians(a)), CZ + (SLOT_R - 0.0004) * math.sin(math.radians(a)))
          for a in range(-105, 106, 15)]
g.f(hw.section("slot_liner", liner, yS0, P(120, 0)[0], mat=DARK))

# ================================================================== 가늠쇠 (낮은 검은 날 + 빨간 파이버 막대)
FS_TOP = P(0, 30)[1]
fy0, fy1 = P(150, 0)[0], P(105, 0)[0]
blade = [(fy0, BZ + 0.0060), (fy0, FS_TOP), (fy1 - 0.0024, FS_TOP), (fy1, FS_TOP - 0.0020), (fy1, BZ + 0.0060)]
g.s(hw.side("front_sight", blade, 0.0034, bevel=0.0005, seg=1, mat=DARK))
g.s(hw.ycyl("fiber", 0.0010, fy0 - 0.0003, fy1 - 0.0028, z=FS_TOP - 0.0004, verts=10, mat=RED))
g.f(hw.decal("fiber_dot", hw.circle(0.0011, 10), (0, fy0 - 0.0003, FS_TOP - 0.0004), mat=RED, **hw.BACK, lift=0.0002))
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(hw.decal(f"sight_pin{sx}", hw.circle(0.0008, 8), (sx * 0.0017, (fy0 + fy1) / 2, BZ + 0.0083), mat=STEEL,
                 **fr, lift=0.0002))

# ================================================================== 각인 (총열 왼쪽, 낡아 희미하게)
y_txt = P(152, 0)[0]
g.f(hw.text("mk_name", "COBRA", 0.0040, (-SW, y_txt, P(0, 75)[1]), mat=ETCH, **hw.LEFT, lift=0.0003))
g.f(hw.text("mk_cal", ".38 SPL +P", 0.0021, (-SW, y_txt, P(0, 87)[1]), mat=ETCH, **hw.LEFT, lift=0.0003))

# ================================================================== 손잡이 (호그 오버몰드 고무: 손가락 홈, 등판을 덮는다)
# 앞면 손가락 홈: 방아쇠울 뒤 위 혹 → 가운데손가락 홈 → 둘째 혹 → 약지 홈 → 셋째 혹 → 새끼손가락 자리 (실물 사진).
# 홈은 사진보다 조금 깊게: 먹선(1.8 mm)이 오목한 곳을 메워 옆모습에서 혹이 묻히기 때문
GRIP_PTS = [(486, 222), (483, 250), (483, 282), (487, 291),
            (497, 296), (512, 300), (526, 306), (536, 314), (541, 320),
            (540, 328), (536, 339), (536, 351), (542, 362),
            (555, 371), (568, 378), (578, 386), (581, 393),
            (574, 400), (561, 407), (553, 415), (554, 425),
            (562, 434), (574, 442), (585, 448), (600, 455), (622, 461), (650, 464),
            (681, 459), (708, 448), (726, 430), (734, 407), (734, 380), (727, 350), (715, 315), (701, 285),
            (686, 255), (668, 225), (652, 195), (640, 165), (635, 145),
            (630, 137), (600, 133), (575, 128), (555, 124), (552, 160), (544, 188), (528, 204), (505, 215)]
GW = 0.0340        # 손잡이 폭 (실물 전체 폭 1.4")
GN = 2.6           # 단면 초타원 지수 (2 = 타원, 클수록 각진 통통한 고무)
GAX = (math.sin(math.radians(25)), math.cos(math.radians(25)))   # 손잡이 축 (사진 px, 아래로): 앞면은 25° 눕는다
GNX = (GAX[1], -GAX[0])                                            # 축에 수직 (앞 → 뒤)


def g_slice(t):
    """축 위치 t(px, GAX 투영)에서 축에 수직인 선이 외곽선과 만나는 가장 앞·가장 뒤 점 (사진 px)"""
    hits = []
    n = len(GRIP_PTS)
    for i in range(n):
        p0, p1 = GRIP_PTS[i], GRIP_PTS[(i + 1) % n]
        t0 = p0[0] * GAX[0] + p0[1] * GAX[1]
        t1 = p1[0] * GAX[0] + p1[1] * GAX[1]
        if (t0 - t) * (t1 - t) > 0 or t0 == t1:
            continue
        f = (t - t0) / (t1 - t0)
        hits.append((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f))
    if len(hits) < 2:
        return None
    key = lambda q: q[0] * GNX[0] + q[1] * GNX[1]
    return min(hits, key=key), max(hits, key=key)


def se(c, n=GN):
    return math.copysign(abs(c) ** (2 / n), c)


def grip_mesh(name):
    """호그 오버몰드 손잡이: 옆모습 외곽선을 축에 수직으로 잘라 초타원 단면을 이어 붙인다 (둥근 고무 덩어리)"""
    ts = [q[0] * GAX[0] + q[1] * GAX[1] for q in GRIP_PTS]
    tA, tB = min(ts) + 0.4, max(ts) - 0.4
    NS, NR = 50, 20
    rings = []
    for i in range(NS + 1):
        u = i / NS
        t = tA + (tB - tA) * (0.5 * u + 0.5 * (0.5 - 0.5 * math.cos(math.pi * u)))   # 고르게 (손가락 홈을 놓치지 않게) + 끝 조금 촘촘히
        sl = g_slice(t)
        if sl is None:
            continue
        (fy, fz), (by, bz) = P(*sl[0]), P(*sl[1])
        cy, cz = (fy + by) / 2, (fz + bz) / 2
        dy, dz = (by - fy) / 2, (bz - fz) / 2
        half = math.hypot(dy, dz)
        bw = min(GW / 2, half * 1.15 + 0.0015)     # 끝(밑·위)으로 갈수록 폭도 줄여 둥글게
        rings.append([(bw * se(math.sin(2 * math.pi * j / NR)), cy + dy * se(math.cos(2 * math.pi * j / NR)),
                       cz + dz * se(math.cos(2 * math.pi * j / NR))) for j in range(NR)])
    verts, faces = [], []
    for r in rings:
        verts.extend(r)
    for i in range(len(rings) - 1):
        for j in range(NR):
            a, b = i * NR + j, i * NR + (j + 1) % NR
            faces.append((a, b, b + NR, a + NR))
    for end, rev in ((0, True), (len(rings) - 1, False)):
        c = [sum(v[k] for v in rings[end]) / NR for k in range(3)]
        verts.append(tuple(c))
        ci = len(verts) - 1
        for j in range(NR):
            a, b = end * NR + j, end * NR + (j + 1) % NR
            faces.append((ci, b, a) if rev else (ci, a, b))
    o = cb.from_pydata(name, verts, faces, material=RUBBER)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    cb.smooth(o, angle=60)
    return o


g.s(grip_mesh("grip"))
# 고무 결 (옆면에 작은 점을 엇갈려, 표면 위에 법선 방향으로): 가장자리는 비운다
k = 0
for row, yo in enumerate(range(150, 452, 12)):
    for xo in range(486 + (row % 2) * 6, 728, 13):
        t = xo * GAX[0] + yo * GAX[1]
        sl = g_slice(t)
        if sl is None:
            continue
        (fy, fz), (by, bz) = P(*sl[0]), P(*sl[1])
        y, z = P(xo, yo)
        cy, cz = (fy + by) / 2, (fz + bz) / 2
        dy, dz = (by - fy) / 2, (bz - fz) / 2
        half = math.hypot(dy, dz)
        if half < 0.004:
            continue
        sv = ((y - cy) * dy + (z - cz) * dz) / (half * half)       # -1 앞 … 1 뒤
        if abs(sv) > 0.72:
            continue
        bw = min(GW / 2, half * 1.15 + 0.0015)
        xs = bw * (1 - abs(sv) ** GN) ** (1 / GN)
        # 초타원 법선: (d 방향 성분, x 성분)
        gn_d = math.copysign(abs(sv) ** (GN - 1), sv) / half
        gn_x = (xs / bw) ** (GN - 1) / bw
        for sx, side_name in ((-1, "L"), (1, "R")):
            nrm = (sx * gn_x, gn_d * dy / half, gn_d * dz / half)
            ln = math.sqrt(sum(c * c for c in nrm))
            nrm = tuple(c / ln for c in nrm)
            # 손잡이 축 방향 (모델 공간)
            ax = (0.0, (288 - (xo + GAX[0])) * S - (288 - xo) * S, (73 - (yo + GAX[1])) * S - (73 - yo) * S)
            dot = sum(a * b for a, b in zip(ax, nrm))
            up = tuple(a - dot * b for a, b in zip(ax, nrm))
            ul = math.sqrt(sum(c * c for c in up))
            up = tuple(c / ul for c in up)
            right = (up[1] * nrm[2] - up[2] * nrm[1], up[2] * nrm[0] - up[0] * nrm[2], up[0] * nrm[1] - up[1] * nrm[0])
            g.f(hw.decal(f"pebble{side_name}_{k}", hw.circle(0.0007, 6), (sx * xs, y, z), right=right, up=up,
                         mat=RUBBER_D, lift=0.0003))
        k += 1
print(f"[colt_cobra] grip pebbles per side = {k}")

# ================================================================== 방아쇠울 (큰 둥근 고리: 앞은 살짝 불룩, 앞 아래 모서리가 크게 둥글고 앞이 두껍다, 밑은 가운데가 처진다)
def catmull(pts, n=5):
    """열린 캣멀롬 곡선 (점 사이를 n 등분)"""
    out = []
    ext = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(len(p1))))
    out.append(tuple(pts[-1]))
    return out


def strip_var(path):
    """(y, z, 두께) 곡선 → 두께가 변하는 닫힌 외곽선"""
    left, right = [], []
    n = len(path)
    for i, (y, z, w) in enumerate(path):
        a, b = path[max(0, i - 1)], path[min(n - 1, i + 1)]
        ty, tz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ty, tz)
        ny, nz = -tz / ln, ty / ln
        left.append((y + ny * w / 2, z + nz * w / 2))
        right.append((y - ny * w / 2, z - nz * w / 2))
    return left + right[::-1]


# 중심선 (사진 px, 두께 px): 위 이음은 프레임에 붙는 살, 앞 10 px, 앞 아래 모서리 9, 밑 7.5, 뒤 8
guard_c = [(311, 222, 16), (311, 236, 12), (310.5, 250, 11), (311.5, 264, 11), (314.5, 278, 10.5), (320, 290, 10),
           (329, 300, 9.5), (341, 307, 9), (356, 312, 8.5), (376, 315.5, 8), (400, 318, 7.5), (424, 319, 7.5),
           (444, 317.5, 7.5), (457, 313.5, 7.5), (466, 306, 8), (471, 296, 8), (473.5, 283, 8), (474.5, 266, 8),
           (474.5, 248, 8), (475, 233, 9), (477, 222, 10)]
guard = [(*P(x, y), w * S) for x, y, w in catmull(guard_c, 2)]
g.s(hw.side("trigger_guard", strip_var(guard), 0.0078, bevel=0.0008, seg=2, mat=STEEL))

# ================================================================== 방아쇠 (가늘게 휘어 끝이 앞으로 말린다)
TRIG = (0, *P(422, 218))
trig = [(414, 214), (429, 214), (427, 240), (423, 258), (416, 276), (407, 291), (398, 302), (391, 307), (388, 303),
        (395, 292), (402, 278), (408, 262), (411, 245), (412, 228)]
g.p("trigger", hw.side("trigger_blade", PL(trig), 0.0060, bevel=0.0010, seg=2, mat=POLISH))
g.pivot("trigger", TRIG, rotAxis="x", rotDeg=-16)

# ================================================================== 공이치기 (갈고리형 박차 + 빗살)
HAM = (0, *P(482, 112))
# 머리(공이 쪽) 뒤로 V자 골이 패고, 박차는 뒤로 거의 눕게(약 20°) 뻗어 끝이 둥글다 (실물 사진)
ham = [(462, 46), (468, 47), (480, 48), (488, 52), (496, 58), (502, 62), (512, 59), (522, 55.5), (532, 52), (540, 49),
       (544, 48), (547, 49.5), (547, 53), (539, 56.5), (530, 59), (521, 62.5), (513, 67), (507, 73), (502, 81),
       (499, 90), (497, 100), (488, 116), (472, 112), (463, 95), (460, 70)]
g.p("hammer", hw.side("hammer_body", PL(ham), 0.0076, bevel=0.0012, seg=2, mat=POLISH))
SPUR = math.atan2(0.34, 1.0)       # 박차 윗면 기울기 (뒤로 갈수록 올라간다)
for i in range(6):
    xo = 512 + i * 5.5
    y, z = P(xo, 62 - (xo - 502) * 0.34)
    g.pf("hammer", hw.decal(f"spur_ser{i}", hw.rrect(0.0060, 0.0006, 0.0002, 1), (0, y, z), mat=DARK,
                            right=(-1, 0, 0), up=(0, -math.cos(SPUR), math.sin(SPUR)), lift=0.0002))
g.pivot("hammer", HAM, rotAxis="x", rotDeg=34)

# ================================================================== 크레인 · 실린더 (왼쪽으로 열린다)
CRANE = (-0.0062, 0.0, CZ - 0.0237)     # 크레인 축 (총열과 나란함, 왼쪽 아래)
crane = [(234, 106), (287, 106), (287, 214), (258, 214), (249, 196), (240, 168), (235, 140)]
g.p("crane", hw.side("crane_arm", PL(crane), 0.0156, bevel=0.0014, seg=2, mat=STEEL))
g.pf("crane", hw.decal("crane_seam", hw.rrect(P(250, 0)[0] - P(287, 0)[0], 0.0005, 0.0002, 1),
                       (-0.0078, (P(250, 0)[0] + P(287, 0)[0]) / 2, P(0, 180)[1]), mat=DARK, **hw.LEFT))
g.pivot("crane", CRANE, swingDeg=82)


def fluted_cylinder(name):
    """홈(플루트) 여섯 개를 판 실린더 (불리언 없이 반지름을 깎은 격자: 홈 끝은 숟가락처럼 둥글게).
    2017 코브라는 홈이 앞쪽으로 치우쳐 길고, 뒤쪽 1 cm는 홈 없이 둥글다. 양 끝은 모따기 + 평면 뚜껑"""
    NA = 64
    HW = math.radians(13.5)          # 홈 반폭 (각)
    DEP = 0.0031                     # 홈 깊이
    F0, F1, RMP = P(392, 0)[0], P(304, 0)[0], 0.0046   # 홈 곧은 구간과 끝 둥글기 길이
    CH = 0.0018                      # 모따기
    ys = [CY0 + CH, F0 - RMP] + [F0 - RMP + RMP * i / 5 for i in range(1, 6)] + [(F0 + F1) / 2] + \
        [F1 + RMP * i / 5 for i in range(0, 5)] + [F1 + RMP, CY1 - CH]

    def depth(a, y):
        d = min(abs(((a - math.radians(60 * k) + math.pi) % (2 * math.pi)) - math.pi) for k in range(6))
        if d >= HW:
            return 0.0
        f = math.cos(d / HW * math.pi / 2) ** 2
        if y < F0:
            t = (y - (F0 - RMP)) / RMP
        elif y > F1:
            t = ((F1 + RMP) - y) / RMP
        else:
            t = 1.0
        t = max(0.0, min(1.0, t))
        return DEP * f * math.sqrt(t * (2 - t))

    verts, faces = [], []
    rings = []
    verts.append((0, CY0, CZ))
    back_c = 0

    def ring(y, rr_fn):
        idx = []
        for i in range(NA):
            a = 2 * math.pi * i / NA
            r = rr_fn(a)
            idx.append(len(verts))
            verts.append((r * math.cos(a), y, CZ + r * math.sin(a)))
        return idx
    rings.append(ring(CY0, lambda a: CR - CH))
    for y in ys:
        rings.append(ring(y, lambda a, y=y: CR - depth(a, y)))
    rings.append(ring(CY1, lambda a: CR - CH))
    verts.append((0, CY1, CZ))
    front_c = len(verts) - 1
    for i in range(NA):
        j = (i + 1) % NA
        faces.append((back_c, rings[0][j], rings[0][i]))
        faces.append((front_c, rings[-1][i], rings[-1][j]))
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(NA):
            j = (i + 1) % NA
            faces.append((r0[i], r0[j], r1[j], r1[i]))
    o = cb.from_pydata(name, verts, faces, material=STEEL)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    cb.smooth(o, angle=50)
    return o


cyl = fluted_cylinder("cyl_body")
ROD_HEAD0 = P(150, 0)[0]
ROD_END = P(121, 0)[0]
parts_cyl = [cyl,
             hw.ycyl("ejector_rod", ROD_R, CY1 - 0.001, ROD_HEAD0, z=CZ, verts=12, mat=ETCH),
             hw.ycyl("ejector_head", SLOT_R - 0.0004, ROD_HEAD0, ROD_END, z=CZ, verts=14, bevel=0.0006, mat=STEEL)]
g.p("cylinder", *parts_cyl)
# 앞면 약실 여섯 (위 약실이 총열 축) · 로드 꼭지 빗살 · 뒤쪽 멈춤 홈
cf = []
for k in range(6):
    a = math.radians(90 + 60 * k)
    c = (BC * math.cos(a), CY1, CZ + BC * math.sin(a))
    cf.append(hw.decal(f"chamber{k}", hw.circle(0.0047, 14), c, mat=DARK, **hw.FRONT))
    cf.append(hw.decal(f"case{k}", hw.circle(0.0036, 12), c, mat=GOLD, lift=0.0009, **hw.FRONT))
    # 멈춤 홈 (실린더 뒤쪽 둘레, 홈 사이)
    b = math.radians(30 + 60 * k)
    rr = CR - 0.0001
    cf.append(hw.decal(f"stop{k}", hw.rrect(0.0042, 0.0018, 0.0006, 1), (rr * math.cos(b), CY0 + 0.0058, CZ + rr * math.sin(b)),
                       mat=DARK, right=(0, 1, 0), up=(-math.sin(b), 0, math.cos(b)), lift=0.0003))
for k in range(8):
    a = 2 * math.pi * k / 8
    rr = SLOT_R - 0.0004
    cf.append(hw.decal(f"knurl{k}", hw.rrect(ROD_END - ROD_HEAD0 - 0.0012, 0.0005, 0.0002, 1),
                       (rr * math.cos(a), (ROD_HEAD0 + ROD_END) / 2, CZ + rr * math.sin(a)), mat=DARK,
                       right=(0, 1, 0), up=(-math.sin(a), 0, math.cos(a)), lift=0.0002))
g.pf("cylinder", *cf)
g.pivot("cylinder", (0, 0, CZ), spinAxis="z", step=60)
g.sub("cylinder", "crane")

# ================================================================== 앵커
g.anchor("muzzle", (0, MUZ + 0.001, BZ))
g.anchor("sight_eye", (0, -0.200, TOP + 0.0010))
g.anchor("chambers", (0, CY1, CZ), parent="cylinder")   # 실린더 앞면 가운데 (재장전: 탄피가 여기서 나온다)
g.anchor("eject", (-0.030, CY1, CZ))                     # 실린더가 열렸을 때 앞면 자리 (대략)

# ================================================================== 원점 = 파지점 (손잡이 가운데, 가운데손가락 홈 높이)
GRIP = P(628, 330)
DY, DZ = -GRIP[0], -GRIP[1]
for o in bpy.data.objects:
    if o.parent is None:
        o.location.y += DY
        o.location.z += DZ
for k, (x, y, z) in list(g.pivots.items()):
    g.pivots[k] = (x, y + DY, z + DZ)
g.anchors = [(n, (p[0], p[1] + DY, p[2] + DZ), par) for n, p, par in g.anchors]
print(f"[colt_cobra] grip point (before shift) = ({GRIP[0]:.4f}, {GRIP[1]:.4f}), bore height {BZ + DZ:.4f}, "
      f"muzzle ahead {MUZ + DY:.4f}")

g.finish("weapons/kyoju/colt_cobra.glb", outline=0.0018, fp="0.11,-0.12,-0.25", fprot="0,6,0")
