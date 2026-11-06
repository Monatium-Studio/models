"""1막 위성 브리핑용 모나티엄 전경 (act1_overview): 고도 300 m~8 km에서 내려다보는 도시와 외곽.

npm run model -- art/blender/levels/act1_overview.py   → public/models/levels/act1_overview.glb
npm run shot -- levels/act1_overview.glb --views top,34

로딩 영상 1(상황 브리핑)과 2(시청 후퇴 작전)가 이 glb를 따로 만든 three.js 장면에 불러 거의 수직으로 내려다보고,
단색 위성 사진으로 후처리한다(그림자는 실시간 그림자 맵). 겹침 정보(괄호, 부대 표시, 경로 화살표)는 MARK_/WP_ 노드를 읽어
코드가 그린다.

좌표: Blender m, +X 동, +Y 북, 원점 = downtown()의 광장 중심 (시청 (0,26), 중앙로·모노레일 y=-20.8,
코어 AI 탑 (32,36), EBI 진압반 본부 (-38,22), x=66부터 동쪽으로 알프토반 진입로).

[원작] 시청 앞 광장, 도시 중앙부를 순환하는 모노레일(공장·발전소 구역까지 연장, 중앙역), 모나티엄-에르피엔 고속도로,
       정령산·에르피엔 접경, 침공전의 차원문.
[오리지널] 도시 전체의 가로망과 구역, 강, 순환선 노선, 서부환승역, 지하철(남서광장역), 병기창고, 차원문 세 곳의 위치,
       진압반 검문소, 분대 위치, 전쟁 피해(WAR_d0).

구성 (루트 아래 그룹)
  zone_plaza … zone_skyline 밖   downtown() 공용 배치 (원경 고층은 끄고 넓은 도시로 바꿈)
  zone_ground   가로(아스팔트 띠)와 블록 바닥판. 같은 높이에서 서로 겹치지 않게 쌓는다(먼 거리 깊이 깜빡임 방지)
  zone_city_*   절차 생성 건물 (도심 고층 고리 / 중층 / 저층 주거 / 공단 / 물류)
  zone_trees    가로수·공원·숲 가장자리 (육각 쌍뿔)
  zone_river    강(물 + 둑) 과 다리
  zone_transit  모노레일 순환선·서쪽 연장선·동쪽 연결선, 중앙역, 서부환승역(2층), 엘레나디지털단지역, 지하철 출입구
  zone_highway  알프토반 고가 연장 + 외곽 성토 구간
  zone_outskirts 지형(정점색 밭 조각보, 언덕), 숲, 산울타리, 농가, 시골길
  zone_gates    GATE_a / GATE_b / GATE_c (R41 차원문, 루트 스케일 0→1 = 열림)
  zone_units    분대 위치·검문소 바리케이드와 진압반 차량
  zone_armory   모나티엄 병기창고 (M2: 지하 통로 → 병기창고 → 궤도 정비 계단 → 모노레일 → 시청)
  WAR_d0        hidden=1 전쟁 피해 (연기 기둥, 불씨, 그을음, 탄 지붕, R41 차량 행렬, 버려진 차)
  GLOW_cityhall … GLOW_d4  hidden=1 야간 조명 (1막 종료 「정전」: 루트 blackout 순서로 끈다)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()

# ================================================================== palette (위성 시점 전용: 단색으로 바꿨을 때 밝기 차이가 나게)
mk.PAL.update({
    "ov_road": "#4a474f",    # 간선 차도 (도심 키트 asphalt보다 어둡게)
    "ov_road2": "#625f68",   # 이면도로·골목 (간선보다 밝게: 위에서 가로 위계가 보이게)
    "ov_walk": "#c6c0b4",    # 보도·블록 바닥
    "ov_lot": "#8a878e",     # 주차장·공장 마당
    "ov_yard": "#93b97a",    # 주거 마당
    "ov_grass": "#7caf66",   # 공원
    "ov_water": "#2d4658",   # 강·연못
    "ov_bank": "#88a874",    # 둑 비탈
    "ov_track": "#b4664f",   # 육상 트랙
    "ov_pitch": "#6ea85a",   # 운동장
    "ov_b1": "#dedad5",      # 밝은 콘크리트
    "ov_b2": "#d7c6ae",      # 베이지
    "ov_b3": "#aaa6ad",      # 회색
    "ov_b4": "#77737c",      # 짙은 회색 지붕
    "ov_b5": "#b4735d",      # 기와·테라코타
    "ov_b6": "#8c6a5a",      # 갈색 벽돌
    "ov_b7": "#7b91a7",      # 청회색 금속
    "ov_b8": "#f1eee8",      # 흰 지붕
    "ov_b9": "#8fa394",      # 녹회색 (동판)
    "ov_glass2": "#3f6c93",  # 짙은 유리
    "ov_metal": "#c8ccd1",   # 공장 금속 지붕
    "ov_metal_d": "#8d949c",
    "ov_forest": "#4b7a49",
    "ov_car_w": "#e9e7e3",
    "ov_car_d": "#3c3940",
    "ov_car_b": "#56739a",
    "ov_car_s": "#a9adb2",
    # 도시 안 밭 (외곽 지형 정점색과 같은 값)
    "ov_f1": "#cdc28c", "ov_f2": "#a3c27a", "ov_f3": "#8db06b", "ov_f4": "#b8b58a", "ov_f5": "#a99674",
    "ov_f6": "#7aa35f",
})
FIELD_KEYS = ["ov_f1", "ov_f2", "ov_f3", "ov_f4", "ov_f5", "ov_f6"]
MID_KEYS = ["ov_b1", "ov_b1", "ov_b2", "ov_b2", "ov_b3", "ov_b3", "ov_b4", "ov_b5", "ov_b6", "ov_b7", "ov_b8", "ov_b9"]
TOWER_KEYS = ["ov_b1", "ov_b3", "ov_b8", "glass_t", "ov_glass2", "ov_b7"]
HOUSE_WALL = ["ov_b2", "ov_b8", "ov_b1", "ov_b2"]
HOUSE_ROOF = ["ov_b5", "ov_b5", "ov_b4", "ov_b6", "ov_b7", "ov_b3", "ov_b9", "ov_b4"]
CAR_KEYS = ["ov_car_w", "ov_car_w", "ov_car_d", "ov_car_s", "ov_car_s", "ov_car_b", "red"]
LEAF = ["leaf", "leaf_d", "leaf_d", "ov_forest"]

C = mk.City("act1_overview")
A = mk.downtown(C, variant="day", training=True, train=True, highway_on=True, skyline=False, screens=False)

AV = mk.AVENUE_Y            # 중앙로 중심 y = -20.8
Z_ROAD = -0.15              # 차도 윗면 (도심 키트와 같음)
HALF = 1100.0               # 도시 정사각형 반폭 (지형 구멍과 같음)
DT = (-96.0, 96.0, -60.0, 60.0)    # downtown() 영역 (건드리지 않음)
TRACK_TOP = 7.5 + 0.65      # 모노레일 보 윗면

STATS = {"trees": 0, "cars": 0, "bld": 0}


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def in_dt(x, y, m=0.0):
    return DT[0] - m < x < DT[1] + m and DT[2] - m < y < DT[3] + m

# ================================================================== 가로망
# 남북 가로 (x, 폭), 동서 가로 (y, 폭). 폭 20 = 간선, 10 = 이면도로. 도심 경계 가로 x=±106, y=±70은 가장자리가
# downtown() 바닥(±96, ±60)과 맞닿는다. 중앙로(y=AV)는 서쪽 14 m(도심 차로와 같음), 동쪽은 고가 아래 측도 24 m.
# 시가지 밖(밭) 칸 사이의 이면도로는 지운다. THROUGH_*는 시가지 밖으로도 이어지는 간선(외곽 시골길과 만남).
XS = [(-1090, 20), (-1010, 10), (-930, 10), (-850, 20), (-770, 10), (-700, 10), (-630, 10), (-545, 20), (-470, 20),
      (-400, 10), (-330, 10), (-250, 10), (-180, 10), (-106, 20), (-40, 10), (40, 10), (106, 20), (170, 10),
      (235, 10), (300, 10), (365, 10), (430, 20), (500, 10), (570, 10), (640, 20), (720, 10), (800, 10),
      (880, 10), (960, 20), (1025, 10), (1090, 20)]
YS = [(-1090, 20), (-1010, 10), (-930, 10), (-850, 20), (-770, 10), (-700, 10), (-630, 10), (-560, 20), (-490, 10),
      (-400, 10), (-320, 20), (-250, 10), (-180, 20), (-125, 10), (-70, 20), (AV, 14), (70, 20), (140, 10),
      (210, 20), (280, 10), (355, 10), (430, 20), (500, 10), (570, 10), (640, 20), (710, 10), (780, 10),
      (850, 20), (920, 10), (1000, 10), (1090, 20)]
THROUGH_X = {-850, -545, 106, 430, 960}
THROUGH_Y = {-850, -320, AV, 210, 430, 850}
NX, NY = len(XS), len(YS)
J_AV = [k for k, (y, _) in enumerate(YS) if y == AV][0]


def xw(i):
    return XS[i][1]


def yw(j, x):
    if j == J_AV:
        return 14.0 if x < 0 else 24.0
    return YS[j][1]


def ix_of(x):
    return [k for k, (v, _) in enumerate(XS) if abs(v - x) < 0.5][0]


def iy_of(y):
    return [k for k, (v, _) in enumerate(YS) if abs(v - y) < 0.5][0]


# 큰 블록 (가로 일부를 지우고 칸을 합침): (이름, x선 a, x선 b, y선 a, y선 b, 종류)
SUPER = [
    ("park_gate_a", -850, -630, -630, -400, "park_big"),       # 차원문 A 아래 남서 공원 (대각 대로가 가로지름)
    ("park_gate_c", -180, 40, 500, 640, "park_big"),           # 차원문 C 아래 북부 공원
    ("stadium", 720, 960, -320, -70, "stadium"),               # 차원문 B 아래 모나티엄 경기장
    ("industry_1", -1010, -850, 355, 500, "industry_big"),
    ("industry_2", -930, -770, 140, 280, "industry_big"),
    ("logistics_1", 720, 880, -630, -490, "logistics_big"),
    ("school_1", 235, 365, 280, 355, "school"),
    ("school_2", -400, -250, 640, 710, "school"),
    ("school_3", 500, 640, -490, -400, "school"),
    ("school_4", -630, -470, 500, 570, "school"),
    ("mall_1", 570, 720, 140, 210, "bigbox"),
    ("apt_1", 170, 300, 500, 640, "apt_big"),
    ("apt_2", -1010, -850, -400, -250, "apt_big"),
    ("apt_3", 500, 640, 640, 780, "apt_big"),
    ("apt_4", -250, -106, -770, -630, "apt_big"),
    ("apt_5", 640, 800, 280, 430, "apt_big"),
    ("armory", -470, -400, -180, -70, "armory"),                 # 모나티엄 병기창고 (M2 경유지)
]
CELL_SB = {}
SB_RECT = {}
for (nm, xa, xb, ya, yb, kind) in SUPER:
    i0, i1, j0, j1 = ix_of(xa), ix_of(xb), iy_of(ya), iy_of(yb)
    for i in range(i0, i1):
        for j in range(j0, j1):
            CELL_SB[(i, j)] = nm
    SB_RECT[nm] = (i0, i1, j0, j1, kind)


def cell_rect(i, j):
    x0 = XS[i][0] + xw(i) / 2
    x1 = XS[i + 1][0] - xw(i + 1) / 2
    xm = (x0 + x1) / 2
    y0 = YS[j][0] + yw(j, xm) / 2
    y1 = YS[j + 1][0] - yw(j + 1, xm) / 2
    return x0, x1, y0, y1


def sb_rect(nm):
    i0, i1, j0, j1, _ = SB_RECT[nm]
    x0 = XS[i0][0] + xw(i0) / 2
    x1 = XS[i1][0] - xw(i1) / 2
    xm = (x0 + x1) / 2
    return x0, x1, YS[j0][0] + yw(j0, xm) / 2, YS[j1][0] - yw(j1, xm) / 2


def cell_in_dt(i, j):
    x0, x1, y0, y1 = cell_rect(i, j)
    return in_dt((x0 + x1) / 2, (y0 + y1) / 2)


# 시가지 경계: 방향마다 반지름이 다른 울퉁불퉁한 윤곽 + 고속도로·대각 대로를 따라 뻗은 손가락. 공단·물류는 늘 시가지.
def industry_zone(x, y):
    return x < -630 and 70 < y < 640


def logistics_zone(x, y):
    return 640 < x < 1030 and -860 < y < -400


def urban_at(x, y):
    if industry_zone(x, y) or logistics_zone(x, y) or in_dt(x, y, 40):
        return True
    th = math.atan2(y, x)
    R = 905 + 120 * math.sin(3 * th + 0.7) + 75 * math.sin(5 * th + 2.1) + 50 * math.sin(8 * th + 0.3)
    if x > 0 and abs(y - AV) < 150:
        R += 260
    if x < 0 and abs(y - AV) < 120:
        R += 160
    dd = abs((x + 545) * 200.0 - (y + 320) * 215.0) / math.hypot(200.0, 215.0)
    if dd < 140 and x < -545:
        R += 220
    return math.hypot(x, y) < R


URBAN = {}
for i in range(NX - 1):
    for j in range(NY - 1):
        x0, x1, y0, y1 = cell_rect(i, j)
        URBAN[(i, j)] = bool(CELL_SB.get((i, j))) or urban_at((x0 + x1) / 2, (y0 + y1) / 2)


def urban(i, j):
    return URBAN.get((i, j), False)

# ================================================================== 강 (서부를 남북으로 흐름. 물은 둑 위 +2.2 m: 아래 바닥판과 깊이가 겹치지 않게)
Z_WATER = 2.2


def river_x(y):
    x = -300.0 + 45.0 * math.sin(y / 260.0) + 25.0 * math.sin(y / 130.0 + 1.0)
    if y > 1000:
        x -= 0.00006 * (y - 1000) ** 2
    if y < -1000:
        x -= 0.00004 * (y + 1000) ** 2
    x += smooth(900, 1600, abs(y)) * 140.0 * math.sin(y / 650.0)
    return x


def river_hw(y):
    return 34.0 + 10.0 * smooth(1100, 1500, abs(y))


RIVER_Y = sorted(set([y for y in range(-1400, 1401, 20)] + [y for y in range(-12000, 12001, 160)]))
RIVER = [(river_x(y), float(y)) for y in RIVER_Y]

# ================================================================== 대각 대로 (차원문 A → 분대 교차로)
DIAG0 = Vector((-1090.0, -320.0 - (1090 - 545) * 200.0 / 215.0))
DIAG1 = Vector((-545.0, -320.0))
DIAG_HW = 9.0
_dd = (DIAG1 - DIAG0).normalized()
DIAG_N = Vector((-_dd.y, _dd.x))

# ================================================================== 모노레일 노선
RING = mk.fillet_path([(-470, AV), (-470, 430), (430, 430), (430, -180), (-470, -180), (-470, AV)],
                      [90.0, 90.0, 90.0, 28.0], seg=8)
BRANCH = mk.fillet_path([(-470, AV), (-700, AV), (-700, 280), (-985, 280)], 60.0, seg=6)
EAST_LINK = mk.fillet_path([(136, AV), (170, AV + 34), (170, 140), (430, 140)], 30.0, seg=5)
WEST_LINE = [(-120.0, AV, 7.5), (-470.0, AV, 7.5)]
JUNCTION = (-470.0, AV)
HWY_X = (430.0, AV)


def ring_z(x, y):
    """순환선 보 높이: 서부환승역에서 2층(15.5), 고속도로 위에서 17, 그 밖은 7.5."""
    d1 = math.hypot(x - JUNCTION[0], y - JUNCTION[1])
    d2 = math.hypot(x - HWY_X[0], y - HWY_X[1])
    return 7.5 + 8.0 * (1 - smooth(70, 170, d1)) + 9.5 * (1 - smooth(70, 170, d2))


# ================================================================== 장애물 (건물·나무를 놓지 않을 띠): 공간 해시
class Obstacles:
    def __init__(self, cell=60.0):
        self.cell = cell
        self.h = {}

    def add(self, a, b, r):
        x0, x1 = min(a[0], b[0]) - r, max(a[0], b[0]) + r
        y0, y1 = min(a[1], b[1]) - r, max(a[1], b[1]) + r
        for gx in range(int(math.floor(x0 / self.cell)), int(math.floor(x1 / self.cell)) + 1):
            for gy in range(int(math.floor(y0 / self.cell)), int(math.floor(y1 / self.cell)) + 1):
                self.h.setdefault((gx, gy), []).append((a[0], a[1], b[0], b[1], r))

    def hit(self, x0, x1, y0, y1, pad=0.0):
        seen = set()
        for gx in range(int(math.floor((x0 - pad) / self.cell)), int(math.floor((x1 + pad) / self.cell)) + 1):
            for gy in range(int(math.floor((y0 - pad) / self.cell)), int(math.floor((y1 + pad) / self.cell)) + 1):
                for s in self.h.get((gx, gy), ()):
                    if id(s) in seen:
                        continue
                    seen.add(id(s))
                    if seg_rect_dist(s[0], s[1], s[2], s[3], x0, x1, y0, y1) < s[4] + pad:
                        return True
        return False


def _pt_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - dx * t, py - ay - dy * t)


def _pt_rect(px, py, x0, x1, y0, y1):
    dx = max(x0 - px, 0.0, px - x1)
    dy = max(y0 - py, 0.0, py - y1)
    return math.hypot(dx, dy)


def _seg_cross(ax, ay, bx, by, cx, cy, dx, dy):
    def o(px, py, qx, qy, rx, ry):
        return (qx - px) * (ry - py) - (qy - py) * (rx - px)
    d1, d2 = o(ax, ay, bx, by, cx, cy), o(ax, ay, bx, by, dx, dy)
    d3, d4 = o(cx, cy, dx, dy, ax, ay), o(cx, cy, dx, dy, bx, by)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def seg_rect_dist(ax, ay, bx, by, x0, x1, y0, y1):
    if _pt_rect(ax, ay, x0, x1, y0, y1) == 0 or _pt_rect(bx, by, x0, x1, y0, y1) == 0:
        return 0.0
    edges = ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0))
    for e in edges:
        if _seg_cross(ax, ay, bx, by, *e):
            return 0.0
    d = min(_pt_rect(ax, ay, x0, x1, y0, y1), _pt_rect(bx, by, x0, x1, y0, y1))
    for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        d = min(d, _pt_seg(px, py, ax, ay, bx, by))
    return d


OBS = Obstacles()
for k in range(len(RIVER) - 1):
    if abs(RIVER[k][1]) < 1300:
        OBS.add(RIVER[k], RIVER[k + 1], river_hw(RIVER[k][1]) + 16.0)
OBS.add(DIAG0, DIAG1, DIAG_HW + 3.0)
for path in (RING, BRANCH, EAST_LINK):
    for k in range(len(path) - 1):
        OBS.add(path[k], path[k + 1], 6.0)

# 역·출입구·검문소 자리 (블록 건물이 덮지 않게 미리 비움)
for (cx_, cy_, r_) in ((-526.0, -301.0, 7.0), (-438.0, -31.5, 5.0), (-411.0, -30.0, 5.0), (-532.0, -165.0, 6.0), (-618.0, -405.0, 6.0),
                       (-450.0, -29.8, 6.0), (-490.0, -11.8, 6.0), (-457.8, -10.8, 6.0), (-950.0, 270.8, 6.0),
                       (-36.0, 421.5, 6.0), (438.5, 236.0, 6.0), (424.0, -70.0, 10.0), (-106.0, 424.0, 10.0),
                       (-545.0, -320.0, 20.0)):
    OBS.add((cx_, cy_), (cx_ + 0.01, cy_), r_)

# ================================================================== 초점 (저고도 줌에서 보일 곳: 지붕 디테일·차량·가로수를 더 둔다)
SQUAD = (-545.0, -320.0)
KIOSK_SW = (-526.0, -301.0)
FOCUS = [(SQUAD, 260.0), ((-470.0, AV), 240.0), ((430.0, -70.0), 140.0), ((-106.0, 430.0), 140.0)]


def near_focus(x, y):
    return any(math.hypot(x - p[0], y - p[1]) < r for p, r in FOCUS)


BUILDINGS = []          # (x0, x1, y0, y1, top) 전쟁 피해(탄 지붕)·야간 불빛 고를 때 쓴다
GABLES = set()          # 박공집 (x0, x1, y0, y1): 지붕 대신 현관 불빛


def bld(key, x0, x1, y0, y1, h, *, z0=0.0, detail=None, rng=None, parapet=True, rec=True, force=False):
    """건물 상자 하나 (바닥면 없음). 장애물 띠에 걸리면 놓지 않는다(force면 무시). detail이면 파라펫·옥상 기계."""
    if x1 - x0 < 2 or y1 - y0 < 2 or h < 1:
        return False
    if not force and OBS.hit(x0, x1, y0, y1, 1.0):
        return False
    top = z0 + h
    mk.lod_box(C, key, x0, x1, y0, y1, z0, top)
    STATS["bld"] += 1
    if rec:
        BUILDINGS.append((x0, x1, y0, y1, top))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if detail is None:
        detail = near_focus(cx, cy)
    r = rng or random.Random(int(cx * 7 + cy * 13))
    if detail and h > 5 and x1 - x0 > 8 and y1 - y0 > 8:
        if parapet:
            o = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            i_ = [(x0 + 0.5, y0 + 0.5), (x1 - 0.5, y0 + 0.5), (x1 - 0.5, y1 - 0.5), (x0 + 0.5, y1 - 0.5)]
            C.ring_prism("ov_b3" if key != "ov_b3" else "ov_b1", o, i_, top, top + 0.9)
        for _ in range(r.randint(1, 3)):
            w, d = r.uniform(2.0, 5.0), r.uniform(2.0, 4.0)
            ux, uy = r.uniform(x0 + 1.5, x1 - 1.5 - w), r.uniform(y0 + 1.5, y1 - 1.5 - d)
            mk.lod_box(C, r.choice(("steel", "ov_b4", "ov_b8")), ux, ux + w, uy, uy + d, top, top + r.uniform(1.2, 2.6))
    elif h > 14 and r.random() < 0.45:
        w, d = min(x1 - x0, 12) * r.uniform(0.25, 0.5), min(y1 - y0, 12) * r.uniform(0.25, 0.5)
        ux, uy = r.uniform(x0 + 1, x1 - 1 - w), r.uniform(y0 + 1, y1 - 1 - d)
        mk.lod_box(C, r.choice(("ov_b4", "ov_b8", "ov_b3")), ux, ux + w, uy, uy + d, top, top + r.uniform(2.0, 4.0))
    return True


TREE_CAP = 3000


def tree(x, y, rng, *, h=None, r=None, z=0.0, key=None, check=True):
    if STATS["trees"] >= TREE_CAP:
        return
    if check and OBS.hit(x - 1, x + 1, y - 1, y + 1, 1.0):
        return
    hh = h if h is not None else rng.uniform(7.0, 12.0)
    rr = r if r is not None else hh * rng.uniform(0.3, 0.42)
    mk.lod_tree(C, x, y, h=hh, r=rr, z=z, key=key or rng.choice(LEAF), rot=rng.uniform(0, 1.25), sides=5)
    STATS["trees"] += 1


CAR_CAP = 520


def car(x, y, along_x, rng, *, z=0.0, key=None, length=3.6, width=1.7, height=1.3):
    if STATS["cars"] >= CAR_CAP:
        return
    hl, hw_ = (length / 2, width / 2) if along_x else (width / 2, length / 2)
    mk.lod_box(C, key or rng.choice(CAR_KEYS), x - hl, x + hl, y - hw_, y + hw_, z, z + height)
    STATS["cars"] += 1

# ================================================================== 볼록 다각형 자르기 (대각 대로가 지나는 블록 바닥판)
def clip_half(poly, n, c):
    """n·p >= c 쪽만 남긴다 (Sutherland-Hodgman, 볼록 다각형)."""
    out = []
    m = len(poly)
    for k in range(m):
        p, q = poly[k], poly[(k + 1) % m]
        dp = n[0] * p[0] + n[1] * p[1] - c
        dq = n[0] * q[0] + n[1] * q[1] - c
        if dp >= 0:
            out.append(p)
        if (dp >= 0) != (dq >= 0):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def diag_hits(x0, x1, y0, y1):
    return seg_rect_dist(DIAG0.x, DIAG0.y, DIAG1.x, DIAG1.y, x0, x1, y0, y1) < DIAG_HW


def slab(key, x0, x1, y0, y1, z=0.0):
    """블록 바닥판 (윗면 z=0, 차도보다 0.15 m 높음). 연석 옆면은 위에서 보이지 않아 윗면만 둔다(glb 크기).
    대각 대로가 지나면 대로를 피해 두 조각으로 자른다. z: 다른 판 밑에 깔리는 바탕판이면 조금 낮춘다."""
    rect = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    parts = [rect]
    if diag_hits(x0, x1, y0, y1):
        n = (DIAG_N.x, DIAG_N.y)
        c0 = DIAG_N.x * DIAG0.x + DIAG_N.y * DIAG0.y
        parts = [clip_half(rect, n, c0 + DIAG_HW), clip_half(rect, (-n[0], -n[1]), -(c0 - DIAG_HW))]
    b = C.bm(key)
    for part in parts:
        if len(part) >= 3:
            b.faces.new([b.verts.new((x, y, z)) for x, y in part])


def ring_pts(x0, x1, y0, y1, cx, cy, rx, ry, n=32):
    """사각형 둘레(모서리 포함)와 타원의 같은 각도 점 쌍."""
    angs = sorted(set([2 * math.pi * k / n for k in range(n)] +
                      [math.atan2(yy - cy, xx - cx) % (2 * math.pi) for xx, yy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]))
    outer, inner = [], []
    for a in angs:
        dx, dy = math.cos(a), math.sin(a)
        ts = []
        if abs(dx) > 1e-9:
            ts += [(x0 - cx) / dx, (x1 - cx) / dx]
        if abs(dy) > 1e-9:
            ts += [(y0 - cy) / dy, (y1 - cy) / dy]
        t = min(t for t in ts if t > 0)
        outer.append((cx + dx * t, cy + dy * t))
        inner.append((cx + dx * rx, cy + dy * ry))
    return outer, inner


def slab_hole(key, x0, x1, y0, y1, cx, cy, rx, ry, *, z_in=Z_ROAD, n=32):
    """타원 구멍이 난 바닥판 (구멍에는 연못·트랙·경기장이 따로 들어간다)."""
    outer, inner = ring_pts(x0, x1, y0, y1, cx, cy, rx, ry, n)
    b = C.bm(key)
    m = len(outer)
    to = [b.verts.new((x, y, 0.0)) for x, y in outer]
    ti = [b.verts.new((x, y, 0.0)) for x, y in inner]
    bo = [b.verts.new((x, y, Z_ROAD)) for x, y in outer]
    bi = [b.verts.new((x, y, z_in)) for x, y in inner]
    for k in range(m):
        k2 = (k + 1) % m
        b.faces.new((to[k], to[k2], ti[k2], ti[k]))
        b.faces.new((bo[k], bo[k2], to[k2], to[k]))
        b.faces.new((bi[k2], bi[k], ti[k], ti[k2]))


def ellipse_ring(key, cx, cy, rx0, ry0, rx1, ry1, z, n=40, z_out=None, wall=None):
    """타원 고리 윗면 (z, 바깥 z_out이면 경사). wall=(z_bottom)이면 바깥·안 벽도."""
    b = C.bm(key)
    zo = z if z_out is None else z_out
    o = [b.verts.new((cx + math.cos(2 * math.pi * k / n) * rx0, cy + math.sin(2 * math.pi * k / n) * ry0, zo))
         for k in range(n)]
    i_ = [b.verts.new((cx + math.cos(2 * math.pi * k / n) * rx1, cy + math.sin(2 * math.pi * k / n) * ry1, z))
          for k in range(n)]
    for k in range(n):
        k2 = (k + 1) % n
        b.faces.new((o[k], o[k2], i_[k2], i_[k]))
    if wall is not None:
        ob = [b.verts.new((v.co.x, v.co.y, wall)) for v in o]
        ib = [b.verts.new((v.co.x, v.co.y, wall)) for v in i_]
        for k in range(n):
            k2 = (k + 1) % n
            b.faces.new((ob[k], ob[k2], o[k2], o[k]))
            b.faces.new((i_[k], i_[k2], ib[k2], ib[k]))


def ellipse_disc(key, cx, cy, rx, ry, z, n=40):
    b = C.bm(key)
    vs = [b.verts.new((cx + math.cos(2 * math.pi * k / n) * rx, cy + math.sin(2 * math.pi * k / n) * ry, z))
          for k in range(n)]
    b.faces.new(vs)


# ================================================================== 블록 종류별 생성기
def split(a0, a1, n, rng, gap=(0.0, 3.0)):
    """[a0, a1]을 n칸으로 (폭을 조금씩 흔들고 사이 간격)."""
    ws = [rng.uniform(0.7, 1.3) for _ in range(n)]
    tot = sum(ws)
    out = []
    s = a0
    for k, w in enumerate(ws):
        e = s + (a1 - a0) * w / tot
        g = rng.uniform(*gap) / 2 if k < n - 1 else 0.0
        out.append((s + (rng.uniform(*gap) / 2 if k > 0 else 0.0), e - g))
        s = e
    return out


def core_block(x0, x1, y0, y1, rng, r):
    """도심 고층 고리: 필지 2~4개, 탑(포디엄 + 몸통 + 왕관) 또는 꽉 찬 중층."""
    inset = 3.0
    x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - inset
    w, d = x1 - x0, y1 - y0
    nx = 2 if w > 48 else 1
    ny = 2 if d > 48 else 1
    if nx * ny == 1:
        if w >= d:
            nx = 2
        else:
            ny = 2
    hmax = 98.0 - 46.0 * smooth(140, 340, r)
    for (ax0, ax1) in split(x0, x1, nx, rng, (2, 8)):
        for (ay0, ay1) in split(y0, y1, ny, rng, (2, 8)):
            lw, ld = ax1 - ax0, ay1 - ay0
            if rng.random() < 0.7 and lw > 16 and ld > 16:
                key = rng.choice(TOWER_KEYS)
                hp = rng.uniform(5, 11)
                bld(rng.choice(("ov_b1", "ov_b3", "ov_b8", "ov_b2")), ax0, ax1, ay0, ay1, hp, rng=rng)
                fx, fy = lw * rng.uniform(0.1, 0.24), ld * rng.uniform(0.1, 0.24)
                sx0, sx1 = ax0 + fx * rng.uniform(0.4, 1.6), ax1 - fx * rng.uniform(0.4, 1.6)
                sy0, sy1 = ay0 + fy * rng.uniform(0.4, 1.6), ay1 - fy * rng.uniform(0.4, 1.6)
                h = rng.uniform(0.55, 1.0) * hmax
                bld(key, sx0, sx1, sy0, sy1, h - hp, z0=hp, rng=rng, parapet=False)
                if rng.random() < 0.6:
                    c = rng.uniform(1.5, 4.0)
                    bld(rng.choice(("ov_b3", "ov_b4", "ov_b8", key)), sx0 + c, sx1 - c, sy0 + c, sy1 - c,
                        rng.uniform(3, 9), z0=h, rng=rng)
            else:
                h = rng.uniform(16, 34)
                bld(rng.choice(MID_KEYS), ax0, ax1, ay0, ay1, h, rng=rng)


def midrise_lots(x0, x1, y0, y1, rng, hr=(12, 30), inset=2.5, keys=None):
    """필지로 나눈 중층 블록 (상가·사무·주거가 섞인 가로변)."""
    x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - inset
    w, d = x1 - x0, y1 - y0
    if w >= d:
        rows = split(y0, y1, 2 if d > 34 else 1, rng, (0, 6))
        for (ay0, ay1) in rows:
            for (ax0, ax1) in split(x0, x1, max(1, int(w / rng.uniform(16, 28))), rng, (0, 4)):
                if rng.random() < 0.08:
                    continue
                bld(rng.choice(keys or MID_KEYS), ax0, ax1, ay0, ay1, rng.uniform(*hr), rng=rng)
    else:
        cols = split(x0, x1, 2 if w > 34 else 1, rng, (0, 6))
        for (ax0, ax1) in cols:
            for (ay0, ay1) in split(y0, y1, max(1, int(d / rng.uniform(16, 28))), rng, (0, 4)):
                if rng.random() < 0.08:
                    continue
                bld(rng.choice(keys or MID_KEYS), ax0, ax1, ay0, ay1, rng.uniform(*hr), rng=rng)


def perimeter_block(x0, x1, y0, y1, rng, hr=(14, 26)):
    """중정형 블록: 둘레 네 변을 따라 건물, 가운데 안뜰(나무 몇 그루)."""
    inset = 2.5
    x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - inset
    dpt = rng.uniform(11, 15)
    if x1 - x0 < 2 * dpt + 8 or y1 - y0 < 2 * dpt + 8:
        midrise_lots(x0 - inset, x1 + inset, y0 - inset, y1 + inset, rng, hr)
        return
    key = rng.choice(MID_KEYS)
    h = rng.uniform(*hr)
    sides = [(x0, x1, y0, y0 + dpt), (x0, x1, y1 - dpt, y1), (x0, x0 + dpt, y0 + dpt, y1 - dpt),
             (x1 - dpt, x1, y0 + dpt, y1 - dpt)]
    for (a0, a1, b0, b1) in sides:
        along_x = (a1 - a0) > (b1 - b0)
        segs = split(a0, a1, rng.randint(1, 3), rng, (0, 0)) if along_x else split(b0, b1, rng.randint(1, 2), rng, (0, 0))
        for (s0, s1) in segs:
            if rng.random() < 0.1:
                continue
            k = key if rng.random() < 0.7 else rng.choice(MID_KEYS)
            hh = h * rng.uniform(0.8, 1.2)
            if along_x:
                bld(k, s0, s1, b0, b1, hh, rng=rng)
            else:
                bld(k, a0, a1, s0, s1, hh, rng=rng)
    for _ in range(rng.randint(2, 6)):
        tree(rng.uniform(x0 + dpt + 3, x1 - dpt - 3), rng.uniform(y0 + dpt + 3, y1 - dpt - 3), rng)


def apt_complex(x0, x1, y0, y1, rng, hr=(36, 58)):
    """아파트 단지: 동서로 긴 판상 동이 남향으로 줄지어 선다(줄 간격 = 그림자 길이). 사이에 나무."""
    m = 7.0
    x0, x1, y0, y1 = x0 + m, x1 - m, y0 + m, y1 - m
    h = rng.uniform(*hr)
    L = rng.uniform(38, 56)
    D = rng.uniform(11, 13)
    pitch = max(D + 22, h * rng.uniform(0.6, 0.8))
    key = rng.choice(("ov_b8", "ov_b1", "ov_b1", "ov_b2"))
    y = y0
    while y + D <= y1:
        x = x0 + rng.uniform(0, 6)
        while x + L * 0.6 <= x1:
            ln = min(L, x1 - x)
            bld(key, x, x + ln, y, y + D, h * rng.uniform(0.85, 1.1), rng=rng)
            for _ in range(2):
                tree(rng.uniform(x, x + ln), y + D + rng.uniform(4, pitch - D - 4), rng)
            x += ln + rng.uniform(10, 18)
        y += pitch


def _house(hx0, hx1, hy0, hy1, along_x, rng, eave=None):
    if OBS.hit(hx0, hx1, hy0, hy1, 0.5):
        return
    eave = eave or rng.uniform(5.0, 7.5)
    if rng.random() < 0.7:
        mk.lod_gable(C, rng.choice(HOUSE_WALL), rng.choice(HOUSE_ROOF), hx0, hx1, hy0, hy1, 0.0,
                     eave, eave + rng.uniform(2.0, 3.0), axis="x" if along_x else "y")
        STATS["bld"] += 1
        BUILDINGS.append((hx0, hx1, hy0, hy1, eave + 2))
        GABLES.add((hx0, hx1, hy0, hy1))
    else:
        bld(rng.choice(HOUSE_ROOF + HOUSE_WALL), hx0, hx1, hy0, hy1, eave, rng=rng)


def houses_block(x0, x1, y0, y1, rng, sparse=False):
    """단독 주택가: 두 줄 필지(폭 12~16 m, 앞마당 2.5~4.5 m), 박공지붕 위주, 뒷마당 나무. 가끔 줄집(연립)."""
    w, d = x1 - x0, y1 - y0
    along_x = w >= d
    a0, a1 = (x0, x1) if along_x else (y0, y1)
    b0, b1 = (y0, y1) if along_x else (x0, x1)
    rows = [(b0, (b0 + b1) / 2, -1), ((b0 + b1) / 2, b1, 1)] if (b1 - b0) > 30 else [(b0, b1, -1)]
    row_house = (not sparse) and rng.random() < 0.22
    for (r0, r1, face) in rows:
        a = a0 + rng.uniform(1, 3)
        fd = rng.uniform(9, 12.5)
        front = rng.uniform(2.5, 4.5)
        c0, c1 = (r0 + front, r0 + front + fd) if face < 0 else (r1 - front - fd, r1 - front)
        if row_house:
            # 줄집: 3~6칸을 한 지붕으로
            while a < a1 - 12:
                ln = min(rng.uniform(30, 52), a1 - a - 2)
                ka = (a, a + ln)
                hx0, hx1, hy0, hy1 = (ka[0], ka[1], c0, c1) if along_x else (c0, c1, ka[0], ka[1])
                _house(hx0, hx1, hy0, hy1, along_x, rng, eave=rng.uniform(6, 8.5))
                a += ln + rng.uniform(4, 8)
            continue
        while a < a1 - 8:
            lot = rng.uniform(12, 16)
            if sparse and rng.random() < 0.45:
                a += lot
                continue
            fw = min(lot - rng.uniform(2.0, 3.5), a1 - a - 1.5)
            if fw > 6:
                ka = (a, a + fw)
                hx0, hx1, hy0, hy1 = (ka[0], ka[1], c0, c1) if along_x else (c0, c1, ka[0], ka[1])
                _house(hx0, hx1, hy0, hy1, along_x, rng)
                if rng.random() < 0.18:
                    # 차고·창고 (작은 평지붕)
                    kb = (c1 + 1.5, c1 + 6) if face < 0 else (c0 - 6, c0 - 1.5)
                    gx0, gx1, gy0, gy1 = (a + 1, a + 6, kb[0], kb[1]) if along_x else (kb[0], kb[1], a + 1, a + 6)
                    bld(rng.choice(("ov_b3", "ov_b8", "ov_b4")), gx0, gx1, gy0, gy1, 3.0, rng=rng, rec=False)
                if rng.random() < 0.32:
                    tb = (r0 + r1) / 2 + rng.uniform(-2, 2)
                    ta = a + rng.uniform(2, fw)
                    tree(ta if along_x else tb, tb if along_x else ta, rng, h=rng.uniform(6, 10))
            a += lot


def rural_block(x0, x1, y0, y1, rng):
    """시가지 밖 칸: 밭(줄무늬로 둘·셋으로 나눔) + 산울타리·농가·나무 몇 그루, 가끔 숲."""
    t = rng.random()
    if t < 0.13:
        slab("ov_grass", x0, x1, y0, y1)
        if not OBS.hit(x0 + 6, x1 - 6, y0 + 6, y1 - 6, 0):
            mk.lod_box(C, "ov_forest", x0 + 6, x1 - 6, y0 + 6, y1 - 6, 0.0, rng.uniform(11, 15))
        for _ in range(6):
            tree(rng.uniform(x0 + 3, x1 - 3), rng.choice((y0 + 4, y1 - 4)), rng, h=rng.uniform(10, 14))
        return
    w, d = x1 - x0, y1 - y0
    n = rng.choice((1, 2, 2, 3))
    k0 = rng.choice(FIELD_KEYS)
    for k in range(n):
        key = k0 if k % 2 == 0 else rng.choice(FIELD_KEYS)
        if w >= d:
            slab(key, x0 + w * k / n, x0 + w * (k + 1) / n, y0, y1)
        else:
            slab(key, x0, x1, y0 + d * k / n, y0 + d * (k + 1) / n)
    if rng.random() < 0.35:
        horiz = rng.random() < 0.5
        if horiz:
            yy = rng.choice((y0 + 2, y1 - 2))
            mk.lod_box(C, "ov_forest", x0 + 2, x1 - 2, yy - 2, yy + 2, 0.0, rng.uniform(5, 8))
        else:
            xx = rng.choice((x0 + 2, x1 - 2))
            mk.lod_box(C, "ov_forest", xx - 2, xx + 2, y0 + 2, y1 - 2, 0.0, rng.uniform(5, 8))
    if rng.random() < 0.2:
        hx, hy = rng.uniform(x0 + 6, x1 - 30), rng.uniform(y0 + 6, y1 - 24)
        if not OBS.hit(hx, hx + 26, hy, hy + 20, 0):
            mk.lod_gable(C, "ov_b8", rng.choice(HOUSE_ROOF), hx, hx + 12, hy, hy + 9, 0, 5, 7.6)
            mk.lod_gable(C, "ov_b6", "ov_b4", hx + 2, hx + 24, hy + 12, hy + 20, 0, 6, 9, axis="x")
            for _ in range(3):
                tree(hx + rng.uniform(-6, 26), hy + rng.uniform(-6, 22), rng)


def lot_cars(x0, x1, y0, y1, rng, fill=0.4, cap=60):
    """주차장 차량 줄 (x 방향 통로, 차는 y 방향으로 선다)."""
    n = 0
    y = y0 + 2.5
    while y + 5 < y1 and n < cap:
        for row in (0, 1):
            yy = y + row * 5.4 + 2.5
            x = x0 + 2.0
            while x + 2 < x1 and n < cap:
                if rng.random() < fill:
                    car(x + 1.0, yy, False, rng)
                    n += 1
                x += 2.7
        y += 16.0


def bigbox_block(x0, x1, y0, y1, rng):
    """대형 상가 + 주차장."""
    slab("ov_lot", x0, x1, y0, y1)
    w, d = x1 - x0, y1 - y0
    if w >= d:
        bx0, bx1 = x0 + 6, x1 - 6
        by0, by1 = y1 - min(d * 0.55, 60), y1 - 6
        bld(rng.choice(("ov_b8", "ov_b1", "ov_metal")), bx0, bx1, by0, by1, rng.uniform(8, 12), rng=rng)
        lot_cars(x0 + 4, x1 - 4, y0 + 3, by0 - 6, rng, fill=0.22, cap=30)
    else:
        bx0, bx1 = x1 - min(w * 0.55, 60), x1 - 6
        bld(rng.choice(("ov_b8", "ov_b1", "ov_metal")), bx0, bx1, y0 + 6, y1 - 6, rng.uniform(8, 12), rng=rng)
        lot_cars(x0 + 4, bx0 - 6, y0 + 4, y1 - 4, rng, fill=0.22, cap=30)


def parking_block(x0, x1, y0, y1, rng):
    slab("ov_lot", x0, x1, y0, y1)
    lot_cars(x0 + 3, x1 - 3, y0 + 3, y1 - 3, rng, fill=0.3, cap=40)
    for k in range(int((x1 - x0) / 14)):
        tree(x0 + 7 + k * 14, y0 + 1.5, rng, h=7)


def park_block(x0, x1, y0, y1, rng, *, dense=1.0, pond=None, slab_done=False):
    """공원: 잔디 바닥 + 나무 무리(몇 덩어리) + 둘레 가로수. pond=(cx, cy, rx, ry)면 연못."""
    if not slab_done:
        if pond:
            slab_hole("ov_grass", x0, x1, y0, y1, *pond, z_in=-1.2)
            ellipse_disc("ov_water", pond[0], pond[1], pond[2] + 0.5, pond[3] + 0.5, -0.45)
        else:
            slab("ov_grass", x0, x1, y0, y1)
    area = (x1 - x0) * (y1 - y0)
    n_cl = max(1, int(area / 2600 * dense))
    for _ in range(n_cl):
        cx, cy = rng.uniform(x0 + 8, x1 - 8), rng.uniform(y0 + 8, y1 - 8)
        rad = rng.uniform(8, 20)
        for _ in range(rng.randint(4, 10)):
            a, d = rng.uniform(0, 6.3), rad * math.sqrt(rng.random())
            px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
            if pond and ((px - pond[0]) / (pond[2] + 6)) ** 2 + ((py - pond[1]) / (pond[3] + 6)) ** 2 < 1:
                continue
            if x0 + 2 < px < x1 - 2 and y0 + 2 < py < y1 - 2:
                tree(px, py, rng, h=rng.uniform(8, 14))
    step = 12.0
    for (ax, ay, bx_, by_) in ((x0 + 3, y0 + 3, x1 - 3, y0 + 3), (x0 + 3, y1 - 3, x1 - 3, y1 - 3)):
        k = 0
        while ax + k * step < bx_:
            tree(ax + k * step, ay, rng, h=rng.uniform(7, 10))
            k += 1


def school_block(x0, x1, y0, y1, rng):
    """학교: ㄱ자 교사 + 트랙 운동장."""
    w, d = x1 - x0, y1 - y0
    if w >= d:
        fx0, fx1 = x0 + 8, x0 + w * 0.6
        fcx, fcy = (fx0 + fx1) / 2, (y0 + y1) / 2
        rx, ry = (fx1 - fx0) / 2 - 2, min(d / 2 - 8, (fx1 - fx0) / 2 * 0.62)
        bx0 = x0 + w * 0.64
        bld("ov_b8", bx0, x1 - 6, y1 - 22, y1 - 7, rng.uniform(12, 15), rng=rng)
        bld("ov_b8", bx0, bx0 + 14, y0 + 8, y1 - 22, rng.uniform(12, 15), rng=rng)
    else:
        fy0, fy1 = y0 + 8, y0 + d * 0.6
        fcx, fcy = (x0 + x1) / 2, (fy0 + fy1) / 2
        ry, rx = (fy1 - fy0) / 2 - 2, min(w / 2 - 8, (fy1 - fy0) / 2 * 0.62)
        by0 = y0 + d * 0.64
        bld("ov_b8", x0 + 7, x1 - 7, by0, by0 + 14, rng.uniform(12, 15), rng=rng)
        bld("ov_b8", x1 - 22, x1 - 7, by0 + 14, y1 - 6, rng.uniform(12, 15), rng=rng)
    slab_hole("ov_walk", x0, x1, y0, y1, fcx, fcy, rx, ry)
    ellipse_ring("ov_track", fcx, fcy, rx, ry, rx - 7, ry - 7, 0.0, n=32, wall=Z_ROAD)
    ellipse_disc("ov_pitch", fcx, fcy, rx - 7, ry - 7, 0.0, n=32)
    for k in range(10):
        a = 2 * math.pi * k / 10
        tree(fcx + math.cos(a) * (rx + 4), fcy + math.sin(a) * (ry + 4), rng, h=8)


def industrial_block(x0, x1, y0, y1, rng, big=False):
    """공단: 금속 지붕 공장동(톱니 지붕 일부), 저장 탱크, 마당 트럭."""
    slab("ov_lot", x0, x1, y0, y1)
    m = 5.0
    x0, x1, y0, y1 = x0 + m, x1 - m, y0 + m, y1 - m
    w, d = x1 - x0, y1 - y0
    n = 1 if not big else 2
    lots = split(y0, y1, n + (1 if d > 90 else 0), rng, (8, 16)) if d >= w else split(x0, x1, n + (1 if w > 90 else 0), rng, (8, 16))
    for (s0, s1) in lots:
        if d >= w:
            ax0, ax1, ay0, ay1 = x0, x1 - rng.uniform(0, w * 0.35), s0, s1
        else:
            ax0, ax1, ay0, ay1 = s0, s1, y0, y1 - rng.uniform(0, d * 0.35)
        h = rng.uniform(9, 15)
        key = rng.choice(("ov_metal", "ov_metal", "ov_metal_d", "ov_b8", "ov_b7"))
        if rng.random() < 0.35 and ax1 - ax0 > 30:
            # 톱니 지붕: 벽 상자 + 북쪽을 향한 톱니
            if bld(key, ax0, ax1, ay0, ay1, h, rng=rng):
                n_t = max(2, int((ay1 - ay0) / 9))
                for k in range(n_t):
                    t0 = ay0 + (ay1 - ay0) * k / n_t
                    t1 = ay0 + (ay1 - ay0) * (k + 1) / n_t
                    mk.lod_gable(C, key, "ov_metal_d" if key != "ov_metal_d" else "ov_metal", ax0, ax1, t0, t1, h, h,
                                 h + 3.0, axis="x")
        else:
            bld(key, ax0, ax1, ay0, ay1, h, rng=rng)
    for k in range(rng.randint(0, 3)):
        tx, ty = rng.uniform(x0 + 8, x1 - 8), rng.uniform(y0 + 8, y1 - 8)
        rr = rng.uniform(5, 10)
        if not OBS.hit(tx - rr, tx + rr, ty - rr, ty + rr, 0):
            # 겹쳐 선 탱크끼리 밑면이 같은 평면이 되지 않게 밑동을 3 cm씩 다르게 묻는다 (난수는 그대로)
            C.cyl(rng.choice(("ov_b8", "ov_metal", "white")), (tx, ty, -0.03 * (k + 1)), (tx, ty, rng.uniform(9, 16)), rr,
                  segs=12, smooth=True)
    for k in range(rng.randint(2, 8)):
        tx, ty = rng.uniform(x0 + 4, x1 - 4), rng.uniform(y0 + 4, y1 - 4)
        th = 3.4 + 0.05 * (k % 4)          # 겹쳐 선 트레일러 지붕이 같은 높이가 되지 않게 (난수는 그대로)
        if rng.random() < 0.5:
            mk.lod_box(C, rng.choice(("ov_car_w", "ov_b7", "red")), tx - 6, tx + 6, ty - 1.3, ty + 1.3, 0, th)
        else:
            mk.lod_box(C, rng.choice(("ov_car_w", "ov_b7", "red")), tx - 1.3, tx + 1.3, ty - 6, ty + 6, 0, th)
    if rng.random() < 0.3:
        cx_, cy_ = rng.uniform(x0 + 4, x1 - 4), rng.uniform(y0 + 4, y1 - 4)
        C.cyl("brick", (cx_, cy_, -0.15), (cx_, cy_, rng.uniform(30, 45)), 1.8, r2=1.2, segs=10)   # 탱크 밑면과 겹치지 않게 묻음


def logistics_block(x0, x1, y0, y1, rng):
    """물류 창고: 크고 납작한 흰 지붕 + 트럭 마당."""
    slab("ov_lot", x0, x1, y0, y1)
    m = 6.0
    w, d = x1 - x0, y1 - y0
    if w >= d:
        bld(rng.choice(("ov_b8", "ov_metal")), x0 + m, x1 - m, y0 + d * 0.35, y1 - m, rng.uniform(10, 14), rng=rng)
        for k in range(int((w - 2 * m) / 4.5)):
            if rng.random() < 0.5:
                tx = x0 + m + 2 + k * 4.5
                mk.lod_box(C, rng.choice(("ov_car_w", "ov_b7", "ov_b3")), tx - 1.3, tx + 1.3, y0 + d * 0.35 - 14,
                           y0 + d * 0.35 - 1.5, 0, 3.6)
    else:
        bld(rng.choice(("ov_b8", "ov_metal")), x0 + w * 0.35, x1 - m, y0 + m, y1 - m, rng.uniform(10, 14), rng=rng)


def field_block(x0, x1, y0, y1, rng):
    """도시 가장자리 빈 땅: 풀밭 + 몇 그루, 가끔 농가."""
    slab(rng.choice(("ov_yard", "ov_grass", "ov_yard")), x0, x1, y0, y1)
    for _ in range(rng.randint(0, 6)):
        tree(rng.uniform(x0 + 3, x1 - 3), rng.uniform(y0 + 3, y1 - 3), rng)
    if rng.random() < 0.4:
        hx, hy = rng.uniform(x0 + 8, x1 - 22), rng.uniform(y0 + 8, y1 - 20)
        mk.lod_gable(C, "ov_b8", rng.choice(HOUSE_ROOF), hx, hx + 12, hy, hy + 9, 0, 5, 7.6)
        mk.lod_gable(C, "ov_b6", "ov_b4", hx + 2, hx + 18, hy + 12, hy + 20, 0, 6, 9, axis="x")


def plaza_block(x0, x1, y0, y1, rng):
    """광장 (남서광장): 판석 + 둘레 나무 + 가운데 둥근 화단."""
    slab("ov_walk", x0, x1, y0, y1)
    cx, cy = (x0 + x1) / 2 + 4, (y0 + y1) / 2 + 4
    C.cyl("white", (cx, cy, 0), (cx, cy, 0.6), 7.0, segs=24)
    C.cyl("hedge", (cx, cy, 0.6), (cx, cy, 1.0), 6.4, segs=24)
    for k in range(int((x1 - x0) / 9)):
        tree(x0 + 4 + k * 9, y1 - 4, rng, h=8)
        tree(x0 + 4 + k * 9, y0 + 4, rng, h=8)
    for k in range(1, int((y1 - y0) / 9)):
        tree(x1 - 4, y0 + 4 + k * 9, rng, h=8)
    for k in range(6):
        a = 2 * math.pi * k / 6
        tree(cx + math.cos(a) * 12, cy + math.sin(a) * 12, rng, h=9)


# ================================================================== 구역 판정
SPECIAL_CELLS = {}      # (i, j) → 종류 (지정 블록)
SPECIAL_CELLS[(ix_of(-545), iy_of(-320))] = "plaza_sw"      # 남서광장 (분대 교차로 북동 모서리)
SPECIAL_CELLS[(ix_of(-470), iy_of(-70))] = "station_hall"   # 서부환승역 역사 (교차로 남동)
SPECIAL_CELLS[(ix_of(-545), iy_of(-70))] = "bus_terminal"   # 서부환승역 버스 터미널 (교차로 남서)
SW_CENTER = (-505.0, -270.0)    # 남서 부도심 (남서광장 둘레 상가)


def zone_of(cx, cy, rng=None):
    if industry_zone(cx, cy):
        return "industry"
    if logistics_zone(cx, cy):
        return "logistics"
    n = mk.noise2(cx * 0.35, cy * 0.35, 4)
    r = math.hypot(cx, (cy - 30) * 1.1)
    if r < 290 + 25 * n:
        return "core"
    if math.hypot(cx - SW_CENTER[0], cy - SW_CENTER[1]) < 230 or math.hypot(cx + 470, cy - AV) < 170:
        return "subcenter"
    if r < 610 + 55 * n:
        return "mid"
    th = math.atan2(cy, cx)
    R = 905 + 120 * math.sin(3 * th + 0.7) + 75 * math.sin(5 * th + 2.1)
    if math.hypot(cx, cy) > R - 110:
        return "fringe"
    return "outer"


def riverside(x0, x1, y0, y1):
    for yy in (y0, (y0 + y1) / 2, y1):
        xr, hw_ = river_x(yy), river_hw(yy)
        if x1 > xr - hw_ - 30 and x0 < xr + hw_ + 30:
            return True
    return False


def alley_split(x0, x1, y0, y1, rng, w=6.0):
    """긴 블록 가운데를 골목으로 나눈다: 골목 차도 + 두 조각 반환."""
    if x1 - x0 >= y1 - y0:
        xm = x0 + (x1 - x0) * rng.uniform(0.42, 0.58)
        road_rect(xm - w / 2, xm + w / 2, y0, y1, "ov_road2")
        return [(x0, xm - w / 2, y0, y1), (xm + w / 2, x1, y0, y1)]
    ym = y0 + (y1 - y0) * rng.uniform(0.42, 0.58)
    road_rect(x0, x1, ym - w / 2, ym + w / 2, "ov_road2")
    return [(x0, x1, y0, ym - w / 2), (x0, x1, ym + w / 2, y1)]


def fill_block(x0, x1, y0, y1, kind, rng, r):
    if kind in ("core", "mid", "subcenter") and max(x1 - x0, y1 - y0) > 58 and rng.random() < 0.45 \
            and not diag_hits(x0, x1, y0, y1):
        for (a0, a1, b0, b1) in alley_split(x0, x1, y0, y1, rng):
            fill_one(a0, a1, b0, b1, kind, rng, r)
        return
    fill_one(x0, x1, y0, y1, kind, rng, r)


def fill_one(x0, x1, y0, y1, kind, rng, r):
    if kind == "core":
        slab("ov_walk", x0, x1, y0, y1)
        core_block(x0, x1, y0, y1, rng, r)
    elif kind == "subcenter":
        slab("ov_walk", x0, x1, y0, y1)
        if rng.random() < 0.3:
            perimeter_block(x0, x1, y0, y1, rng, (12, 24))
        else:
            midrise_lots(x0, x1, y0, y1, rng, (8, 26), inset=2.0)
    elif kind == "mid":
        t = rng.random()
        if t < 0.32:
            slab("ov_walk", x0, x1, y0, y1)
            perimeter_block(x0, x1, y0, y1, rng)
        elif t < 0.52:
            slab("ov_yard", x0, x1, y0, y1)
            apt_complex(x0, x1, y0, y1, rng)
        elif t < 0.91:
            slab("ov_walk", x0, x1, y0, y1)
            midrise_lots(x0, x1, y0, y1, rng, (10, 30), inset=2.0)
        elif t < 0.95:
            parking_block(x0, x1, y0, y1, rng)
        else:
            park_block(x0, x1, y0, y1, rng)
    elif kind == "outer":
        t = rng.random()
        if t < 0.5:
            slab("ov_yard", x0, x1, y0, y1)
            houses_block(x0, x1, y0, y1, rng)
        elif t < 0.62:
            slab("ov_yard", x0, x1, y0, y1)
            apt_complex(x0, x1, y0, y1, rng, (26, 46))
        elif t < 0.82:
            slab("ov_walk", x0, x1, y0, y1)
            midrise_lots(x0, x1, y0, y1, rng, (6, 15), inset=2.0)
        elif t < 0.89:
            bigbox_block(x0, x1, y0, y1, rng)
        elif t < 0.95:
            park_block(x0, x1, y0, y1, rng)
        else:
            parking_block(x0, x1, y0, y1, rng)
    elif kind == "fringe":
        t = rng.random()
        if t < 0.55:
            slab("ov_yard", x0, x1, y0, y1)
            houses_block(x0, x1, y0, y1, rng, sparse=True)
        elif t < 0.75:
            logistics_block(x0, x1, y0, y1, rng)
        elif t < 0.88:
            slab("ov_yard", x0, x1, y0, y1)
            midrise_lots(x0, x1, y0, y1, rng, (5, 10), inset=4.0)
        else:
            park_block(x0, x1, y0, y1, rng, dense=1.8)
    elif kind == "industry":
        industrial_block(x0, x1, y0, y1, rng)
    elif kind == "logistics":
        logistics_block(x0, x1, y0, y1, rng)

# ================================================================== 가로와 블록 바닥
C.group("ground")
# 도심 바닥 빈틈 메우기 (downtown()은 원경 고층과 큰 바닥판을 끄면 가장자리에 틈이 남는다)
mk.lod_box(C, "ov_road", 66, 96, -30.6, -11.0, Z_ROAD - 0.6, Z_ROAD)
mk.lod_box(C, "ov_walk", -96, 96, -44.0, -30.6, -0.6, -0.05)


def sb_same(c1, c2):
    a, b = CELL_SB.get(c1), CELL_SB.get(c2)
    return a is not None and a == b


def road_rect(x0, x1, y0, y1, key="ov_road"):
    """차도 한 장 (윗면만: 옆은 보도 바닥판 연석이 가린다)."""
    if x1 - x0 > 0.01 and y1 - y0 > 0.01:
        b = C.bm(key)
        # 이면도로는 간선 밑 1 cm: 두 차도판이 교차로에서 겹쳐도 같은 평면이 아니게
        z = Z_ROAD - (0.01 if key == "ov_road2" else 0.0)
        b.faces.new([b.verts.new((x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])


def ns_seg_exists(i, j):
    x = XS[i][0]
    ya = YS[j][0] + yw(j, x) / 2
    yb = YS[j + 1][0] - yw(j + 1, x) / 2
    if in_dt(x, (ya + yb) / 2, -0.5):
        return False
    if 0 < i < NX - 1 and sb_same((i - 1, j), (i, j)):
        return False
    return XS[i][0] in THROUGH_X or (i > 0 and urban(i - 1, j)) or (i < NX - 1 and urban(i, j))


def ew_seg_exists(i, j):
    y = YS[j][0]
    xa = XS[i][0] + xw(i) / 2
    xb = XS[i + 1][0] - xw(i + 1) / 2
    if in_dt((xa + xb) / 2, y, -0.5):
        return False
    if 0 < j < NY - 1 and sb_same((i, j - 1), (i, j)):
        return False
    return YS[j][0] in THROUGH_Y or (j > 0 and urban(i, j - 1)) or (j < NY - 1 and urban(i, j))


def rkey(w):
    return "ov_road" if w >= 14 else "ov_road2"


# 남북 가로 조각 (교차로 사이)
for i in range(NX):
    x, w = XS[i]
    for j in range(NY - 1):
        if ns_seg_exists(i, j):
            road_rect(x - w / 2, x + w / 2, YS[j][0] + yw(j, x) / 2, YS[j + 1][0] - yw(j + 1, x) / 2, rkey(w))
# 동서 가로 조각
for j in range(NY):
    y = YS[j][0]
    for i in range(NX - 1):
        if ew_seg_exists(i, j):
            xa = XS[i][0] + xw(i) / 2
            xb = XS[i + 1][0] - xw(i + 1) / 2
            w = yw(j, (xa + xb) / 2)
            road_rect(xa, xb, y - w / 2, y + w / 2, rkey(w))
# 교차로 (넓은 쪽 가로 색)
CROSS = set()
for i in range(NX):
    for j in range(NY):
        x, y = XS[i][0], YS[j][0]
        if in_dt(x, y, -0.5):
            continue
        ns = (j > 0 and ns_seg_exists(i, j - 1)) or (j < NY - 1 and ns_seg_exists(i, j))
        ew = (i > 0 and ew_seg_exists(i - 1, j)) or (i < NX - 1 and ew_seg_exists(i, j))
        if not (ns or ew):
            continue
        w = yw(j, x)
        CROSS.add((i, j))
        road_rect(x - xw(i) / 2, x + xw(i) / 2, y - w / 2, y + w / 2, rkey(max(w, xw(i))))
# 대각 대로 (차원문 A → 분대 교차로)
_b = C.bm("ov_road")
_q = [DIAG0 - DIAG_N * DIAG_HW, DIAG1 - DIAG_N * DIAG_HW, DIAG1 + DIAG_N * DIAG_HW, DIAG0 + DIAG_N * DIAG_HW]
_v = [_b.verts.new((p.x, p.y, Z_ROAD)) for p in _q]
_b.faces.new(_v)
# 대각 대로 가운데 화단 섬 (높이 0.5: 위에서 줄무늬로 보임)
_m = [DIAG0.lerp(DIAG1, 0.04) - DIAG_N * 1.2, DIAG1.lerp(DIAG0, 0.06) - DIAG_N * 1.2,
      DIAG1.lerp(DIAG0, 0.06) + DIAG_N * 1.2, DIAG0.lerp(DIAG1, 0.04) + DIAG_N * 1.2]
mk._bm_prism(C.bm("hedge"), [(p.x, p.y) for p in _m], Z_ROAD, 0.5, top=True, bottom=False)

# ================================================================== 블록
BLOCK_GROUPS = {"core": "city_core", "mid": "city_mid", "subcenter": "city_mid", "outer": "city_outer",
                "fringe": "city_outer", "industry": "city_industry", "logistics": "city_industry"}
done_sb = set()
PARK_RECTS = {}
for i in range(NX - 1):
    for j in range(NY - 1):
        if cell_in_dt(i, j):
            continue
        rng = random.Random(i * 1009 + j * 37 + 5)
        sb = CELL_SB.get((i, j))
        if sb:
            if sb in done_sb:
                continue
            done_sb.add(sb)
            x0, x1, y0, y1 = sb_rect(sb)
            kind = SB_RECT[sb][4]
            C.group("city_special")
            if kind in ("park_big", "stadium", "armory"):
                PARK_RECTS[sb] = (x0, x1, y0, y1)
                continue            # 아래에서 따로 (차원문 공원·경기장)
            if kind == "industry_big":
                C.group("city_industry")
                industrial_block(x0, x1, y0, y1, rng, big=True)
            elif kind == "logistics_big":
                C.group("city_industry")
                logistics_block(x0, x1, y0, y1, rng)
            elif kind == "school":
                school_block(x0, x1, y0, y1, rng)
            elif kind == "bigbox":
                bigbox_block(x0, x1, y0, y1, rng)
            elif kind == "apt_big":
                slab("ov_yard", x0, x1, y0, y1)
                apt_complex(x0, x1, y0, y1, rng, (42, 66))
            continue
        x0, x1, y0, y1 = cell_rect(i, j)
        # 시가지 밖에서 가로가 지워진 쪽은 바닥판을 가로 중심선까지 넓힌다 (밭이 이어지게)
        if not urban(i, j):
            if not ns_seg_exists(i, j):
                x0 = XS[i][0] if i > 0 else -HALF
            if not ns_seg_exists(i + 1, j):
                x1 = XS[i + 1][0] if i + 1 < NX - 1 else HALF
            if not ew_seg_exists(i, j):
                y0 = YS[j][0] if j > 0 else -HALF
            if not ew_seg_exists(i, j + 1):
                y1 = YS[j + 1][0] if j + 1 < NY - 1 else HALF
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sp = SPECIAL_CELLS.get((i, j))
        if sp:
            C.group("city_special")
            if sp == "plaza_sw":
                plaza_block(x0, x1, y0, y1, rng)
            elif sp == "station_hall":
                slab("ov_walk", x0, x1, y0, y1)
            elif sp == "bus_terminal":
                slab("ov_lot", x0, x1, y0, y1)
            PARK_RECTS[sp] = (x0, x1, y0, y1)
            continue
        if riverside(x0, x1, y0, y1):
            C.group("river")
            park_block(x0, x1, y0, y1, rng, dense=1.0 if urban(i, j) else 0.6)
            continue
        if not urban(i, j):
            C.group("rural")
            rural_block(x0, x1, y0, y1, rng)
            continue
        kind = zone_of(cx, cy, rng)
        C.group(BLOCK_GROUPS[kind])
        fill_block(x0, x1, y0, y1, kind, rng, math.hypot(cx, (cy - 30) * 1.1))
# 시가지 밖에서 가로가 지워져 생긴 교차점 빈칸 (네 칸 모두 밭이면 가운데 사각을 밭으로 메움)
C.group("rural")
for i in range(NX):
    for j in range(NY):
        if (i, j) in CROSS:
            continue
        x, y = XS[i][0], YS[j][0]
        if in_dt(x, y, -0.5) or any(CELL_SB.get(c) for c in ((i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j))):
            continue
        hx, hy = xw(i) / 2, yw(j, x) / 2
        if not any(urban(a, b_) for (a, b_) in ((i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j))):
            # 바탕판: 둘레 칸(±HALF까지 넓힌 밭)과 겹치는 곳이 있어 2 cm 아래에 깐다(같은 평면이면 위성 시점에서 깜빡임)
            slab(FIELD_KEYS[(i + j) % len(FIELD_KEYS)], max(-HALF, x - hx), min(HALF, x + hx),
                 max(-HALF, y - hy), min(HALF, y + hy), z=-0.02)

# ---------------------------------------------------------------- 서부환승역·남서광장 블록 세부
C.group("city_special")
rng = random.Random(77)
sx0, sx1, sy0, sy1 = PARK_RECTS["station_hall"]
bld("ov_b8", sx0 + 4, sx0 + 36, sy0 + 3, sy1 - 10, 9.0, rng=rng, force=True)                 # 역사 (흰 지붕)
bld("glass_t", sx0 + 4, sx0 + 36, sy1 - 10, sy1 - 8, 7.5, rng=rng, force=True)            # 역사 정면 유리 회랑
bx0, bx1, by0, by1 = PARK_RECTS["bus_terminal"]
bld("ov_b8", bx0 + 4, bx1 - 4, by1 - 12, by1 - 4, 5.0, rng=rng, detail=False, force=True)   # 버스 승강장 지붕
for k in range(int((bx1 - bx0 - 10) / 4.2)):
    if rng.random() < 0.6:
        tx = bx0 + 6 + k * 4.2
        mk.lod_box(C, rng.choice(("ov_car_w", "ov_car_b", "teal")), tx - 1.25, tx + 1.25, by1 - 26, by1 - 14, 0, 3.2)
for k in range(5):
    tree(bx0 + 6 + k * (bx1 - bx0 - 12) / 4, by0 + 3, rng, h=8)

# ================================================================== 공원 (차원문 A·C) 과 경기장 (차원문 B)
C.group("city_special")
x0, x1, y0, y1 = PARK_RECTS["park_gate_a"]
park_block(x0, x1, y0, y1, random.Random(101), dense=1.6)
x0, x1, y0, y1 = PARK_RECTS["park_gate_c"]
park_block(x0, x1, y0, y1, random.Random(102), dense=1.6, pond=(0.0, 600.0, 26.0, 18.0))
# 경기장: 판석 마당(타원 구멍) + 경사 관중석 고리 + 트랙 + 잔디, 둘레 주차
x0, x1, y0, y1 = PARK_RECTS["stadium"]
SCX, SCY = 835.0, -195.0
slab_hole("ov_walk", x0, x1, y0, y1, SCX, SCY, 98.0, 78.0)
ellipse_ring("ov_b8", SCX, SCY, 98.0, 78.0, 98.0, 78.0, 26.0, n=48, wall=0.0)          # 바깥 벽 (높이 26)
ellipse_ring("ov_b3", SCX, SCY, 98.0, 78.0, 66.0, 47.0, 6.0, n=48, z_out=26.0)          # 관중석 경사
ellipse_ring("ov_b4", SCX, SCY, 66.0, 47.0, 66.0, 47.0, 6.0, n=48, wall=0.0)            # 안쪽 벽
ellipse_ring("ov_track", SCX, SCY, 66.0, 47.0, 58.0, 39.0, 0.0, n=48)
ellipse_disc("ov_pitch", SCX, SCY, 58.0, 39.0, 0.0, n=48)
ellipse_ring("ov_b8", SCX, SCY, 99.0, 79.0, 92.0, 72.0, 30.0, n=48, z_out=27.0)        # 지붕 띠
rng = random.Random(55)
lot_cars(x0 + 4, x1 - 4, y0 + 3, y0 + 30, rng, fill=0.25, cap=50)
for k in range(int((x1 - x0) / 13)):
    tree(x0 + 6 + k * 13, y1 - 4, rng, h=9)

# ================================================================== 모나티엄 병기창고 (M2: 지하 통로 → 병기창고 → 모노레일 → 시청)
# [오리지널] 분대가 옛 지구제 무기를 꺼내는 진압반 병기창고. 두꺼운 담장(북쪽 정문), 네 모서리 망루, 짙은 올리브
# 지붕의 큰 창고(지붕에 흰 형판 숫자 "03"과 환기 해치 줄), 흙 덮은 탄약고, 상자 더미, 군용 트럭.
C.group("armory")
ax0, ax1, ay0, ay1 = PARK_RECTS["armory"]
ARM = ((ax0 + ax1) / 2, (ay0 + ay1) / 2)
rng = random.Random(303)
slab("ov_lot", ax0, ax1, ay0, ay1)
WI, WT, WH = 1.0, 1.4, 3.8          # 담장 안쪽 들임, 두께, 높이
gx0, gx1 = ARM[0] - 7.0, ARM[0] + 7.0
for (x0_, x1_, y0_, y1_) in ((ax0 + WI, ax1 - WI, ay0 + WI, ay0 + WI + WT),                     # 남
                             (ax0 + WI, ax0 + WI + WT, ay0 + WI, ay1 - WI),                     # 서
                             (ax1 - WI - WT, ax1 - WI, ay0 + WI, ay1 - WI),                     # 동
                             (ax0 + WI, gx0, ay1 - WI - WT, ay1 - WI),                          # 북 (정문 서쪽)
                             (gx1, ax1 - WI, ay1 - WI - WT, ay1 - WI)):                         # 북 (정문 동쪽)
    mk.lod_box(C, "concrete_d", x0_, x1_, y0_, y1_, 0.0, WH)
mk.lod_box(C, "hazard", gx0, gx1, ay1 - WI - 0.4, ay1 - WI, 0.0, 0.5)                          # 정문 차단봉
for (tx, ty) in ((ax0 + WI, ay0 + WI), (ax1 - WI, ay0 + WI), (ax0 + WI, ay1 - WI), (ax1 - WI, ay1 - WI)):
    mk.lod_box(C, "ov_b4", tx - 1.8, tx + 1.8, ty - 1.8, ty + 1.8, 0.0, 8.5)                    # 망루
    mk.lod_box(C, "navy", tx - 2.3, tx + 2.3, ty - 2.3, ty + 2.3, 8.5, 9.1)
mk.lod_box(C, "ov_b4", gx1 + 1.0, gx1 + 4.5, ay1 - 7.5, ay1 - 3.0, 0.0, 3.0)                   # 정문 초소
# 본 창고 (낮고 큰 상자, 올리브 지붕) + 형판 숫자 + 해치
D0, D1, E0, E1 = ax0 + 6.0, ax1 - 6.0, ay0 + 22.0, ay1 - 24.0
DH = 10.0
bld("olive", D0, D1, E0, E1, DH, rng=rng, detail=False, force=True)
mk.lod_box(C, "concrete_d", D0 - 0.3, D1 + 0.3, E0 - 0.3, E1 + 0.3, DH - 1.2, DH + 0.4)        # 처마 띠
mk.lod_box(C, "olive", D0 + 0.4, D1 - 0.4, E0 + 0.4, E1 - 0.4, DH + 0.4, DH + 0.45)


def stencil_digit(ch, cx, cy, z, w=9.0, h=16.0, t=2.0, key="white"):
    """7획 형판 숫자 (위에서 북쪽이 위로 읽힘)."""
    seg = {"a": (cx - w / 2, cx + w / 2, cy + h / 2 - t, cy + h / 2), "d": (cx - w / 2, cx + w / 2, cy - h / 2, cy - h / 2 + t),
           "g": (cx - w / 2, cx + w / 2, cy - t / 2, cy + t / 2), "f": (cx - w / 2, cx - w / 2 + t, cy + 0.6, cy + h / 2 - t - 0.6),
           "b": (cx + w / 2 - t, cx + w / 2, cy + 0.6, cy + h / 2 - t - 0.6),
           "e": (cx - w / 2, cx - w / 2 + t, cy - h / 2 + t + 0.6, cy - 0.6),
           "c": (cx + w / 2 - t, cx + w / 2, cy - h / 2 + t + 0.6, cy - 0.6)}
    on = {"0": "abcdef", "3": "abcdg"}[ch]
    for k in on:
        x0_, x1_, y0_, y1_ = seg[k]
        mk.lod_box(C, key, x0_, x1_, y0_, y1_, z, z + 0.5)


stencil_digit("0", ARM[0] - 6.5, (E0 + E1) / 2 + 2.0, DH + 0.45)
stencil_digit("3", ARM[0] + 6.5, (E0 + E1) / 2 + 2.0, DH + 0.45)
for k in range(5):                                                                              # 환기 해치 줄
    hx = D0 + 4.0 + k * (D1 - D0 - 8.0) / 4
    mk.lod_box(C, "dark", hx - 1.6, hx + 1.6, E0 + 3.0, E0 + 6.2, DH + 0.45, DH + 1.4)
mk.lod_box(C, "hazard", ARM[0] - 9.0, ARM[0] + 9.0, E1 - 0.2, E1 + 0.6, 0.0, 4.5)               # 북쪽 하역 문 테
mk.lod_box(C, "concrete", ARM[0] - 11.0, ARM[0] + 11.0, E1, E1 + 7.0, 0.0, 1.1)                 # 하역 단
# 흙 덮은 탄약고 (남동 마당) + 상자 더미 (남서 마당)
mk.lod_gable(C, "concrete_d", "ov_grass", ARM[0] + 2.0, ax1 - 6.0, ay0 + 6.0, ay0 + 17.0, 0.0, 2.2, 5.5, axis="x")
for k in range(3):
    for m in range(2):
        cx_, cy_ = ax0 + 7.0 + k * 5.2, ay0 + 7.5 + m * 5.0
        mk.lod_box(C, rng.choice(("olive", "wood", "olive")), cx_, cx_ + 4.0, cy_, cy_ + 3.6, 0.0, rng.uniform(1.4, 3.2))
# 북쪽 마당: 군용 트럭·지프 (엘프 체격)
for k, (vx, vy, ln) in enumerate(((ax0 + 9.0, ay1 - 14.0, 7.0), (ax0 + 13.0, ay1 - 14.0, 7.0),
                                  (ax1 - 12.0, ay1 - 15.0, 7.0), (ax1 - 16.0, ay1 - 15.0, 4.5))):
    mk.lod_box(C, "olive", vx - 1.2, vx + 1.2, vy - ln / 2, vy + ln / 2, 0.0, 2.4)
    mk.lod_box(C, "navy", vx - 1.1, vx + 1.1, vy + ln / 2 - 2.0, vy + ln / 2 - 0.2, 2.4, 2.9)
for k in range(4):
    tree(ax0 - 3.0, ay0 + 12 + k * 22, rng, h=8)

# ================================================================== 가로수 (간선도로 양쪽, 일부 구간)
C.group("trees")
rng = random.Random(9)


def on_ew_street(x, y, pad=2.0):
    return any(abs(y - yy) < yw(j, x) / 2 + pad for j, (yy, _) in enumerate(YS))


def on_ns_street(x, y, pad=2.0):
    return any(abs(x - xx) < w / 2 + pad for (xx, w) in XS)


for i, (x, w) in enumerate(XS):
    if w < 20:
        continue
    for side in (-1, 1):
        y = -HALF + 20
        while y < HALF - 20:
            px = x + side * (w / 2 + 2.2)
            zr = zone_of(px, y, rng)
            if not in_dt(px, y, 6) and zr in ("mid", "outer", "core", "subcenter") and urban_at(px, y) \
                    and rng.random() < 0.75 and not on_ew_street(px, y):
                tree(px, y, rng, h=rng.uniform(7, 10), r=rng.uniform(2.4, 3.2))
            y += 15.0 if near_focus(px, y) else 22.0
for j, (y, w) in enumerate(YS):
    if w < 20 and j != J_AV:
        continue
    for side in (-1, 1):
        x = -HALF + 20
        while x < HALF - 20:
            py = y + side * (yw(j, x) / 2 + 2.2)
            zr = zone_of(x, py, rng)
            if not in_dt(x, py, 6) and zr in ("mid", "outer", "core", "subcenter") and urban_at(x, py) \
                    and rng.random() < 0.75 and not on_ns_street(x, py):
                tree(x, py, rng, h=rng.uniform(7, 10), r=rng.uniform(2.4, 3.2))
            x += 15.0 if near_focus(x, py) else 22.0
# 대각 대로 가로수
L = (DIAG1 - DIAG0).length
k = 6.0
while k < L - 10:
    p = DIAG0 + _dd * k
    for s in (-1, 1):
        q = p + DIAG_N * s * (DIAG_HW + 2.5)
        tree(q.x, q.y, rng, h=9, r=3.0, check=False)
    k += 15.0

# ================================================================== 강과 다리
C.group("river")
bw = C.bm("ov_water")
bb = C.bm("ov_bank")
prev = None
for (x, y) in RIVER:
    hw_ = river_hw(y)
    k_ = (x - hw_, x + hw_)
    row = (bw.verts.new((k_[0], y, Z_WATER)), bw.verts.new((k_[1], y, Z_WATER)),
           bb.verts.new((k_[0], y, Z_WATER + 0.2)), bb.verts.new((k_[0] - 14.0, y, -0.65)),
           bb.verts.new((k_[1], y, Z_WATER + 0.2)), bb.verts.new((k_[1] + 14.0, y, -0.65)))
    if prev:
        bw.faces.new((prev[0], prev[1], row[1], row[0]))
        bb.faces.new((prev[3], prev[2], row[2], row[3]))
        bb.faces.new((prev[4], prev[5], row[5], row[4]))
    prev = row
# 다리: 강을 건너는 동서 가로마다 상판 + 양쪽 경사로 + 난간
BRIDGES = []
for j, (y, w) in enumerate(YS):
    xr = river_x(y)
    hw_ = river_hw(y)
    w = yw(j, xr)
    ii = max(k for k in range(NX - 1) if XS[k][0] < xr)
    if not (ew_seg_exists(ii, j) or (ii > 0 and ew_seg_exists(ii - 1, j)) or ew_seg_exists(min(ii + 1, NX - 2), j)):
        continue
    a0, a1 = xr - hw_ - 16, xr + hw_ + 16
    zt = Z_WATER + 1.3
    mk.lod_box(C, "ov_b3", a0, a1, y - w / 2 - 0.6, y + w / 2 + 0.6, zt - 1.1, zt - 0.2)
    mk.lod_box(C, "ov_road", a0, a1, y - w / 2, y + w / 2, zt - 0.2, zt)
    for s in (-1, 1):
        mk.lod_box(C, "ov_b1", a0, a1, y + s * (w / 2 + 0.6) - 0.35, y + s * (w / 2 + 0.6) + 0.35, zt - 0.2, zt + 0.9)
    for (e0, e1) in ((a0, a0 - 26), (a1, a1 + 26)):
        b = C.bm("ov_road")
        v = [b.verts.new((e0, y - w / 2, zt)), b.verts.new((e0, y + w / 2, zt)),
             b.verts.new((e1, y + w / 2, Z_ROAD + 0.02)), b.verts.new((e1, y - w / 2, Z_ROAD + 0.02))]
        f = b.faces.new(v)
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
        for s in (-1, 1):
            yy = y + s * w / 2
            vv = [b.verts.new((e0, yy, zt)), b.verts.new((e1, yy, Z_ROAD)), b.verts.new((e0, yy, Z_ROAD))]
            b.faces.new(vv)
    for k in range(1, 3):
        px = a0 + (a1 - a0) * k / 3
        mk.lod_box(C, "ov_b3", px - 1.2, px + 1.2, y - w / 2, y + w / 2, Z_WATER - 0.5, zt - 1.1)
    BRIDGES.append((xr, y))

# ================================================================== 모노레일
C.group("transit")


def avoid_pillar(x, y):
    if math.hypot(x - JUNCTION[0], y - JUNCTION[1]) < 16:
        return True
    if 120 < x < 1010 and abs(y - AV) < 8.5:          # 고속도로 상판 아래
        return True
    for (bx, by) in BRIDGES:
        if abs(y - by) < 12 and abs(x - bx) < 60:
            return True
    return False


# 중앙로 서쪽 연장 (도심 궤도와 같은 16 m 기둥 간격, x=-120 기둥은 도심 것)
mk.monorail_path(C, WEST_LINE, pitch=16.0, pillar_from=16.0, segs=8, avoid=avoid_pillar, step=400.0)
# 순환선 (서부환승역 2층, 고속도로 위로 넘음)
mk.monorail_path(C, [(x, y, 7.5) for x, y, _ in RING], zf=ring_z, pitch=26.0, avoid=avoid_pillar, step=30.0,
                 segs=6, glow=False)
# 서쪽 연장선 (공단: 엘레나디지털단지역)
mk.monorail_path(C, [(x, y, 7.5) for x, y, _ in BRANCH], pitch=26.0, pillar_from=24.0, avoid=avoid_pillar,
                 step=60.0, segs=6, glow=False)
# 동쪽 연결선 (도심 궤도 끝 x=136에서 순환선 동쪽 변으로)
mk.monorail_path(C, [(x, y, 7.5) for x, y, _ in EAST_LINK], pitch=26.0, pillar_from=20.0, avoid=avoid_pillar,
                 step=60.0, segs=6, glow=False)

# 중앙역: 시청 앞 중앙로, 도심 궤도 기둥(x=-24, -8)에 받침 보, 계단탑은 양쪽 보도
CENTRAL = mk.station_platform(C, -31.0, -5.0, AV, axis="x", z=7.5, posts=[-24.0, -8.0], roof_key="white",
                              stairs=[(-28.0, 1, 6.7, 9.6), (-28.0, -1, 6.7, 9.7)])
# 서부환승역: 1층 = 중앙로선(동서), 2층 = 순환선(남북)
TR_LO = mk.station_platform(C, -505.0, -435.0, AV, axis="x", z=7.5, roof_key="ov_b8",
                            stairs=[(-450.0, -1, 7.0, 11.0), (-490.0, 1, 7.0, 11.0)])
TR_HI = mk.station_platform(C, -58.0, 16.0, -470.0, axis="y", z=15.5, roof_key="ov_b1",
                            posts=[-54.0, -46.0, -38.0, -6.0, 2.0, 10.0], stairs=[(10.0, 1, 10.5, 14.0)])
for u in (-54.0, -46.0, -38.0, -6.0, 2.0, 10.0):
    C.cyl("concrete", (-470.0, u, 0.0), (-470.0, u, TR_HI["top"] - 1.25), 0.7, segs=10, cap=False)
# 엘레나디지털단지역 (서쪽 연장선 종점)
mk.station_platform(C, -985.0, -935.0, 280.0, axis="x", z=7.5, roof_key="ov_b1", stairs=[(-950.0, -1, 7.5, 11.0)])
# 순환선 북쪽·동쪽 작은 역 (지붕만 보이는 정류장)
mk.station_platform(C, -40.0, 0.0, 430.0, axis="x", z=7.5, roof_key="ov_b8", stairs=[(-36.0, -1, 7.0, 10.0)])
mk.station_platform(C, 200.0, 240.0, 430.0, axis="y", z=7.5, roof_key="ov_b8", stairs=[(236.0, 1, 7.0, 10.0)])

# 지하철 출입구 (남서광장역: M1 후퇴 지점), 서부환승역 연결 출입구, 노선 중간 출입구
SW_ENT = mk.subway_entrance(C, KIOSK_SW[0], KIOSK_SW[1], yaw=-45.0)
TR_ENT = mk.subway_entrance(C, -438.0, -31.5, yaw=90.0)
# 병기창고 → 궤도 정비 계단 (서부환승역 동쪽, 중앙로 남쪽 보도에서 궤도 보 옆 점검 통로로)
MAINT = (-411.0, -30.2)
mk.lod_box(C, "ov_b4", MAINT[0] - 3.0, MAINT[0] + 3.0, MAINT[1] - 1.8, MAINT[1] + 1.8, 0.0, TRACK_TOP + 1.3)
mk.lod_box(C, "steel", MAINT[0] - 0.8, MAINT[0] + 0.8, AV - 0.55, MAINT[1] - 1.8, TRACK_TOP - 0.45, TRACK_TOP)
mk.lod_box(C, "hazard", MAINT[0] - 3.2, MAINT[0] + 3.2, MAINT[1] - 2.0, MAINT[1] + 2.0, TRACK_TOP + 1.3,
           TRACK_TOP + 1.55)
MID_ENT = mk.subway_entrance(C, -532.0, -165.0, yaw=90.0)
FAR_ENT = mk.subway_entrance(C, -618.0, -405.0, yaw=-45.0)

# ================================================================== 고속도로 (알프토반) 연장
C.group("highway")
HW_Y = AV
Z_DECK = 9.0
mk.lod_box(C, "ov_road", 266.0, 1000.0, HW_Y - 5.5, HW_Y + 5.5, Z_DECK - 0.9, Z_DECK)
for s in (-1, 1):
    mk.lod_box(C, "ov_b1", 266.0, 1000.0, HW_Y + s * 5.5 - 0.25, HW_Y + s * 5.5 + 0.25, Z_DECK, Z_DECK + 0.9)
x = 281.0
while x < 1000:
    C.cyl("concrete", (x, HW_Y, Z_ROAD), (x, HW_Y, Z_DECK - 1.6), 1.1, segs=8, cap=False)
    mk.lod_box(C, "concrete", x - 0.8, x + 0.8, HW_Y - 5.0, HW_Y + 5.0, Z_DECK - 1.6, Z_DECK - 0.9)
    x += 36.0
# 내려오는 경사로 (도시 가장자리)
b = C.bm("ov_road")
Z_EMB = 1.2
for (xa, xb, za, zb) in ((1000.0, 1100.0, Z_DECK, Z_EMB),):
    v = [b.verts.new((xa, HW_Y - 5.5, za)), b.verts.new((xb, HW_Y - 5.5, zb)), b.verts.new((xb, HW_Y + 5.5, zb)),
         b.verts.new((xa, HW_Y + 5.5, za))]
    b.faces.new(v)
    for s in (-1, 1):
        yy = HW_Y + s * 5.5
        vv = [b.verts.new((xa, yy, za)), b.verts.new((xb, yy, zb)), b.verts.new((xb, yy, Z_ROAD)),
              b.verts.new((xa, yy, Z_ROAD))]
        b.faces.new(vv)
# 외곽 성토 구간: 상하행 두 판 (가운데 4 m 띠는 지형이 보임)
HWY_PATH = mk.fillet_path([(1100.0, HW_Y), (1700.0, -40.0), (2400.0, -130.0), (3200.0, -330.0), (4200.0, -650.0),
                           (5400.0, -1000.0), (6600.0, -1300.0), (9000.0, -1900.0), (13000.0, -2900.0)], 400.0, seg=6)
HWY_PTS = mk.path_points(HWY_PATH, 120.0)


def emb_strip(pts, off0, off1, z_top, key, toe0, toe1):
    """성토 도로 띠: 윗면 off0..off1 (중심선 왼쪽 법선 기준 거리), 비탈 끝 toe0, toe1."""
    b = C.bm(key)
    prev = None
    for k, (x, y, _, s_) in enumerate(pts):
        a = pts[min(k + 1, len(pts) - 1)]
        c = pts[max(k - 1, 0)]
        d = Vector((a[0] - c[0], a[1] - c[1], 0)).normalized()
        n = Vector((-d.y, d.x, 0))
        p = Vector((x, y, 0))
        q = [p + n * o for o in (off0, off1, toe0, toe1)]
        row = (b.verts.new((q[0].x, q[0].y, z_top)), b.verts.new((q[1].x, q[1].y, z_top)),
               b.verts.new((q[2].x, q[2].y, -0.8)), b.verts.new((q[3].x, q[3].y, -0.8)))
        if prev:
            for (u, v_) in ((0, 1), (2, 0), (1, 3)):
                f = b.faces.new((prev[u], prev[v_], row[v_], row[u]))
                f.normal_update()
                if f.normal.z < 0:
                    f.normal_flip()
        prev = row


emb_strip(HWY_PTS, -15.0, -2.0, Z_EMB, "ov_road", -19.5, -0.2)
emb_strip(HWY_PTS, 2.0, 15.0, Z_EMB, "ov_road", 0.2, 19.5)


def hwy_at(dist_x):
    """고속도로 위 점 (도시 원점에서 동쪽 거리 근사)."""
    best = min(HWY_PTS, key=lambda p: abs(p[0] - dist_x))
    return best


# ================================================================== 외곽 지형 (정점색 밭 조각보, 언덕) — 한 메시
C.group("outskirts")


def dist_poly(x, y, pts, step=1):
    d = 1e18
    for k in range(0, len(pts) - 1, step):
        a, b_ = pts[k], pts[k + 1]
        d = min(d, _pt_seg(x, y, a[0], a[1], b_[0], b_[1]))
    return d


RIVER_COARSE = [(river_x(y), float(y)) for y in range(-14000, 14001, 200)]
HWY_COARSE = [(p[0], p[1]) for p in HWY_PTS] + [(266.0, HW_Y), (1100.0, HW_Y)]
HWY_COARSE.sort()


def hills(x, y):
    n = (math.sin(x * 0.0011 + 1.3) * math.cos(y * 0.0009 - 0.4) * 22
         + math.sin(x * 0.0023 - y * 0.0017 + 2.0) * 12
         + math.cos(x * 0.0047 + y * 0.0039) * 6 + 18)
    # 정령산 쪽 (북서) 산줄기
    rx, ry = x + 2500.0, y - 4200.0
    along = (rx * 0.94 + ry * 0.34)
    across = (-rx * 0.34 + ry * 0.94)
    ridge = math.exp(-(across / 1500.0) ** 2) * (330 + 120 * math.sin(along / 900.0)) * smooth(-9000, -4000, along) \
        * (1 - smooth(5000, 9000, along))
    # 남동쪽 낮은 구릉
    se = math.exp(-(((x - 3800) / 1600) ** 2 + ((y + 3600) / 1300) ** 2)) * 120
    return max(0.0, n) + ridge + se


def h_terrain(x, y):
    dc = max(abs(x), abs(y)) - HALF
    if dc <= 0:
        return Z_ROAD
    base = hills(x, y) * smooth(0, 1400, dc)
    fr = smooth(140, 520, dist_poly(x, y, RIVER_COARSE))
    fh = smooth(60, 360, dist_poly(x, y, HWY_COARSE))
    return Z_ROAD + base * fr * fh


FIELD_COLS = ["#cdc28c", "#a3c27a", "#8db06b", "#b8b58a", "#a99674", "#7aa35f", "#c1b27c", "#96b878", "#6f985a",
              "#d8cf9e", "#9a8a6a"]
HILL_COLS = ["#6f985a", "#5f8a50", "#7aa35f", "#557f4b"]
FOREST_COL = "#4b7a49"
ROCK_COL = "#a2a194"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def build_terrain():
    """외곽 지형 한 메시: 183 m 칸(도시 정사각형 = 12칸 구멍), 정점색 밭 조각보. 밭은 농지 구획(6×6칸)마다
    1~3칸 크기 필지로 묶고 일부는 줄무늬 밭. 언덕 위는 숲·초지 색, 높은 곳은 바위."""
    CELL = HALF / 6.0
    N = 30
    bm = bmesh.new()
    FC = []
    V = {}
    for gi in range(-N, N + 1):
        for gj in range(-N, N + 1):
            x, y = gi * CELL, gj * CELL
            V[(gi, gj)] = bm.verts.new((x, y, h_terrain(x, y)))
    rng = random.Random(31)
    region = {}

    def parcel_col(gi, gj):
        rk = (gi // 6, gj // 6)
        if rk not in region:
            region[rk] = (rng.choice((1, 2, 2, 3)), rng.choice((1, 1, 2, 3)), rng.randint(0, 2), rng.randint(0, 2),
                          rng.random() < 0.3, rng.random())
        sx, sy, ox, oy, stripe, seed = region[rk]
        pk = ((gi + ox) // sx, (gj + oy) // sy)
        h = (pk[0] * 73856093 ^ pk[1] * 19349663 ^ int(seed * 1e6)) & 0xffffff
        c = FIELD_COLS[h % len(FIELD_COLS)]
        if stripe and (gj % 2 == 0):
            c = FIELD_COLS[(h // 7) % len(FIELD_COLS)]
        return c

    hole = 6
    for gi in range(-N, N):
        for gj in range(-N, N):
            if -hole <= gi < hole and -hole <= gj < hole:
                continue
            cx, cy = (gi + 0.5) * CELL, (gj + 0.5) * CELL
            hc = h_terrain(cx, cy)
            if hc > 270:
                c = ROCK_COL
            elif hc > 60:
                c = HILL_COLS[(gi * 7 + gj * 3) % len(HILL_COLS)] if rng.random() < 0.75 else FOREST_COL
            else:
                c = parcel_col(gi, gj)
            f = bm.faces.new((V[(gi, gj)], V[(gi + 1, gj)], V[(gi + 1, gj + 1)], V[(gi, gj + 1)]))
            f.smooth = True
            FC.append(hexrgb(c))
    # 먼 바깥 치마 (안개 속으로)
    ring = []
    for gi in range(-N, N):
        ring.append((gi, -N))
    for gj in range(-N, N):
        ring.append((N, gj))
    for gi in range(N, -N, -1):
        ring.append((gi, N))
    for gj in range(N, -N, -1):
        ring.append((-N, gj))
    outer = []
    for (gi, gj) in ring:
        a = math.atan2(gj, gi)
        outer.append(bm.verts.new((math.cos(a) * 18000.0, math.sin(a) * 18000.0, 20.0)))
    far = hexrgb("#8fa98a")
    for k in range(len(ring)):
        k2 = (k + 1) % len(ring)
        f = bm.faces.new((V[ring[k]], V[ring[k2]], outer[k2], outer[k]))
        f.smooth = True
        FC.append(far)
    me = bpy.data.meshes.new("outskirts_terrain")
    bm.to_mesh(me)
    bm.free()
    ca = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    for poly, c in zip(me.polygons, FC):
        for li in poly.loop_indices:
            ca.data[li].color_srgb = (*c, 1.0)
    me.color_attributes.active_color = ca
    o = bpy.data.objects.new("outskirts_terrain", me)
    cb.link(o)
    m = bpy.data.materials.new("ov_terrain")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    node = nt.nodes.new("ShaderNodeVertexColor")
    node.layer_name = "Col"
    nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    m["lineColor"] = "#3a4a34"
    me.materials.append(m)
    o["collider"] = 0
    me.calc_loop_triangles()
    print(f"[ov] terrain tris {len(me.loop_triangles)}")
    return o


TERRAIN = C.add_node(build_terrain())


def in_city(x, y, m=0.0):
    return max(abs(x), abs(y)) < HALF + m


# 숲 (언덕 위 + 평지 군데군데): 둘레가 울퉁불퉁한 수관 판 (높이 14 m, 가장자리 그림자)
rng = random.Random(61)
FORESTS = []
tries = 0
while len(FORESTS) < 70 and tries < 2000:
    tries += 1
    x, y = rng.uniform(-6200, 6200), rng.uniform(-6200, 6200)
    if in_city(x, y, 250):
        continue
    if dist_poly(x, y, RIVER_COARSE) < 220 or dist_poly(x, y, HWY_COARSE) < 160:
        continue
    hh = h_terrain(x, y)
    if hh < 30 and rng.random() < 0.6:
        continue
    rad = rng.uniform(140, 420) * (1.3 if hh > 60 else 1.0)
    if any(math.hypot(x - fx, y - fy) < (rad + fr) * 0.8 for fx, fy, fr in FORESTS):
        continue
    FORESTS.append((x, y, rad))
for (fx, fy, rad) in FORESTS:
    n = 18
    seed = rng.random() * 10
    outl = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = rad * (0.78 + 0.22 * math.sin(a * 3 + seed) + 0.12 * math.sin(a * 7 + seed * 2.3))
        outl.append((fx + math.cos(a) * rr, fy + math.sin(a) * rr))
    b = C.bm("ov_forest")
    top = 13.0
    vc = b.verts.new((fx, fy, h_terrain(fx, fy) + top + 2))
    mid = [b.verts.new(((fx + px) / 2, (fy + py) / 2, h_terrain((fx + px) / 2, (fy + py) / 2) + top + 1)) for px, py in outl]
    ot = [b.verts.new((px, py, h_terrain(px, py) + top)) for px, py in outl]
    ob = [b.verts.new((px, py, h_terrain(px, py) - 3)) for px, py in outl]
    for k in range(n):
        k2 = (k + 1) % n
        b.faces.new((vc, mid[k], mid[k2]))
        b.faces.new((mid[k], ot[k], ot[k2], mid[k2]))
        b.faces.new((ob[k], ob[k2], ot[k2], ot[k]))
    # 가장자리에 나무 몇 그루 (윤곽을 부드럽게)
    for k in range(0, n, 3):
        px, py = outl[k]
        tree(px + rng.uniform(-10, 10), py + rng.uniform(-10, 10), rng, h=rng.uniform(12, 16), r=rng.uniform(5, 8),
             z=h_terrain(px, py), check=False)

# 시골길 (도시 간선의 연장 + 먼 격자): 지형을 따라가는 1 m 둑길
ROADS_X = sorted(THROUGH_X) + [-2200.0, 2200.0, -3600.0, 3600.0]
ROADS_Y = sorted(y for y in THROUGH_Y if y != AV) + [-2200.0, 2200.0, 3600.0, -3600.0, AV - 0.0]


def country_road(p0, p1, w=7.0, step=275.0):
    a, b_ = Vector(p0), Vector(p1)
    L = (b_ - a).length
    n = max(1, int(L / step))
    d = (b_ - a).normalized()
    nrm = Vector((-d.y, d.x, 0)) * (w / 2)
    bm_ = C.bm("ov_road")
    prev = None
    for k in range(n + 1):
        p = a.lerp(b_, k / n)
        if in_city(p.x, p.y, -1) or dist_poly(p.x, p.y, RIVER_COARSE) < 70:
            prev = None
            continue
        z = h_terrain(p.x, p.y) + 1.0
        row = (bm_.verts.new((p.x - nrm.x, p.y - nrm.y, z)), bm_.verts.new((p.x + nrm.x, p.y + nrm.y, z)),
               bm_.verts.new((p.x - nrm.x * 1.8, p.y - nrm.y * 1.8, z - 2.5)),
               bm_.verts.new((p.x + nrm.x * 1.8, p.y + nrm.y * 1.8, z - 2.5)))
        if prev:
            f = bm_.faces.new((prev[0], prev[1], row[1], row[0]))
            f.normal_update()
            if f.normal.z < 0:
                f.normal_flip()
            bm_.faces.new((prev[2], prev[0], row[0], row[2]))
            bm_.faces.new((prev[1], prev[3], row[3], row[1]))
        prev = row


for x in ROADS_X:
    country_road((x, -6500.0), (x, -HALF))
    country_road((x, HALF), (x, 6500.0))
    if abs(x) > HALF:
        country_road((x, -HALF), (x, HALF))
for y in ROADS_Y:
    country_road((-6500.0, y), (-HALF, y))
    if y != AV:                                   # 동쪽 y=AV는 고속도로
        country_road((HALF, y), (6500.0, y))
    if abs(y) > HALF:
        country_road((-HALF, y), (HALF, y))

# 농가 (시골길 교차점 근처) + 산울타리
rng = random.Random(71)
FARMS = []
for x in ROADS_X:
    for y in ROADS_Y:
        if in_city(x, y, 150) or rng.random() < 0.35 or (y == AV and x > 0):
            continue
        for _ in range(rng.randint(1, 2)):
            hx, hy = x + rng.choice((-1, 1)) * rng.uniform(25, 120), y + rng.choice((-1, 1)) * rng.uniform(25, 120)
            z = h_terrain(hx, hy)
            FARMS.append((hx - 3.0, hy + 5.0, z + 0.6))
            mk.lod_gable(C, "ov_b8", rng.choice(HOUSE_ROOF), hx, hx + 14, hy, hy + 10, z - 1, z + 5, z + 8)
            mk.lod_gable(C, "ov_b6", "ov_b4", hx + 20, hx + 44, hy - 6, hy + 8, z - 1, z + 7, z + 11, axis="x")
            C.cyl("ov_b8", (hx + 50, hy, z - 1), (hx + 50, hy, z + 14), 3.2, segs=8, cap=True)
            for _ in range(4):
                tree(hx + rng.uniform(-15, 50), hy + rng.uniform(-18, 25), rng, z=z - 1, check=False)
HEDGES = 0
TC = HALF / 6.0
for gi in range(-29, 29):
    for gj in range(-29, 29):
        x, y = gi * TC, gj * TC
        if in_city(x, y, 300) or rng.random() > 0.07:
            continue
        if dist_poly(x, y, RIVER_COARSE) < 200 or h_terrain(x, y) > 60:
            continue
        horiz = rng.random() < 0.5
        x2, y2 = (x + TC, y) if horiz else (x, y + TC)
        z0, z1 = h_terrain(x, y), h_terrain(x2, y2)
        if abs(z1 - z0) > 12:
            continue
        zz = min(z0, z1) - 1.5
        if horiz:
            mk.lod_box(C, "ov_forest", x, x2, y - 3, y + 3, zz, max(z0, z1) + 7)
        else:
            mk.lod_box(C, "ov_forest", x - 3, x + 3, y, y2, zz, max(z0, z1) + 7)
        HEDGES += 1

# ================================================================== 차원문 (R41)
C.group("gates")
GATES = {
    # id: (지면 중심, 중심 높이, 반지름, 기울기, yaw): 앞(-Z 로컬, 나오는 쪽)이 도심을 향하고 아래로 숙인다
    "a": ((-760.0, -520.0), 64.0, 56.0, 45.0, -55.6),
    "b": ((820.0, -180.0), 56.0, 46.0, 45.0, 77.6),
    "c": ((-60.0, 560.0), 56.0, 46.0, 45.0, -173.9),
}
for gid, ((gx, gy), gz, rad, tilt, yaw) in GATES.items():
    g = mk.gate_r41(C, gid, (gx, gy, gz), radius=rad, tilt=tilt, yaw=yaw, segments=16, spin=18.0)
    g["main"] = 1 if gid == "a" else 0
    g["ground"] = f"{gx:.1f},{gy:.1f},0"

# ================================================================== 분대 위치와 검문소 (평소 장면에 보임)
C.group("units")


def riot_van(x, y, yaw_deg):
    a = math.radians(yaw_deg)
    c, s = math.cos(a), math.sin(a)
    C.rbox("violet", (x, y, 1.35), (2.5, 6.2, 2.5), (0, 0, yaw_deg))
    C.rbox("navy", (x, y, 2.75), (2.2, 3.6, 0.3), (0, 0, yaw_deg))
    C.rbox("glow", (x - s * 1.0, y + c * 1.0, 3.0), (1.6, 0.35, 0.2), (0, 0, yaw_deg))


def barricade_line(p0, p1, yaw_deg, n, kit=0):
    """바리케이드 줄. 처음 kit개만 키트 바리케이드(약 670 삼각형), 나머지는 같은 크기의 값싼 판."""
    for k in range(n):
        t = k / max(1, n - 1)
        x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        if k < kit:
            mk.barricade(C, x, y, yaw=yaw_deg)
        else:
            C.rbox("violet", (x, y, 0.55), (1.6, 0.12, 0.6), (0, 0, yaw_deg))
            C.rbox("teal", (x, y, 0.36), (1.5, 0.14, 0.1), (0, 0, yaw_deg))


# 분대 교차로 (-545,-320): 대각 대로(남서)와 서쪽·남쪽에서 오는 적을 막는 바리케이드 줄 + 모래주머니 + 진압반 차량
sx, sy = SQUAD
barricade_line((sx - 22, sy + 2), (sx + 2, sy - 22), -45.0, 12, kit=4)
mk.sandbag_wall(C, sx - 13, sy - 13, yaw=-45, n=4)
for (dx, dy, yw_) in ((-24, 6, -90), (6, -24, 0), (-4, -18, -45)):      # 값싼 모래주머니 줄 (위에서 같은 크기)
    C.rbox("sand", (sx + dx, sy + dy, 0.4), (2.6, 0.8, 0.8), (0, 0, yw_))
barricade_line((sx - 12, sy + 14), (sx - 12, sy + 6), -90.0, 4)
barricade_line((sx + 6, sy - 12), (sx + 14, sy - 12), 0.0, 4)
riot_van(sx + 8, sy + 9, -45.0)
riot_van(sx + 16, sy + 4, 0.0)
# 검문소 2 (동쪽, 순환선 아래 x=430 × y=-70): 동쪽(차원문 B)을 막음
barricade_line((441.0, -82.0), (441.0, -58.0), 90.0, 10)
riot_van(424.0, -64.0, 0.0)
riot_van(424.0, -77.0, 0.0)
C.rbox("sand", (444.0, -91.0, 0.4), (2.6, 0.8, 0.8), (0, 0, 90))
# 검문소 3 (북쪽, x=-106 × y=430): 북쪽(차원문 C)을 막음
barricade_line((-118.0, 441.0), (-94.0, 441.0), 180.0, 10)
riot_van(-100.0, 424.0, 90.0)
riot_van(-113.0, 424.0, 90.0)

# 초점 근처 길가 차량 (저고도 줌에서 '사는 도시'로 보이게)
rng = random.Random(13)
for (p, rr) in FOCUS[:2]:
    for i, (x, w) in enumerate(XS):
        if abs(x - p[0]) > rr:
            continue
        y = p[1] - rr
        while y < p[1] + rr:
            if not in_dt(x, y, 4) and rng.random() < 0.13 and math.hypot(x - SQUAD[0], y - SQUAD[1]) > 30:
                car(x + rng.choice((-1, 1)) * (w / 2 - 1.6), y, False, rng, z=Z_ROAD)
            y += 7.0
    for j, (y, _) in enumerate(YS):
        if abs(y - p[1]) > rr:
            continue
        w = yw(j, p[0])
        x = p[0] - rr
        while x < p[0] + rr:
            if not in_dt(x, y, 4) and rng.random() < 0.13 and math.hypot(x - SQUAD[0], y - SQUAD[1]) > 30:
                car(x, y + rng.choice((-1, 1)) * (w / 2 - 1.6), True, rng, z=Z_ROAD)
            x += 7.0

# 초점 근처 차선 (점선 중앙선·간선 황색 중앙선) 과 분대 교차로 횡단보도: 저고도 줌용 얇은 판
C.group("units")
ZL = Z_ROAD + 0.03


def mark_quad(key, x0, x1, y0, y1):
    b = C.bm(key)
    b.faces.new([b.verts.new((x, y, ZL)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])


for (p, rr) in FOCUS[:2]:
    for i, (x, w) in enumerate(XS):
        if abs(x - p[0]) > rr:
            continue
        for j in range(NY - 1):
            ya, yb = YS[j][0] + yw(j, x) / 2, YS[j + 1][0] - yw(j + 1, x) / 2
            if not ns_seg_exists(i, j) or max(abs(ya - p[1]), abs(yb - p[1])) > rr:
                continue
            if w >= 20:
                for o in (-0.25, 0.25):
                    mark_quad("line_y", x + o - 0.08, x + o + 0.08, ya + 1, yb - 1)
            else:
                yy = ya + 2
                while yy + 3 < yb - 1:
                    mark_quad("line", x - 0.08, x + 0.08, yy, yy + 3)
                    yy += 8
    for j, (y, _) in enumerate(YS):
        if abs(y - p[1]) > rr:
            continue
        for i in range(NX - 1):
            xa, xb = XS[i][0] + xw(i) / 2, XS[i + 1][0] - xw(i + 1) / 2
            w = yw(j, (xa + xb) / 2)
            if not ew_seg_exists(i, j) or max(abs(xa - p[0]), abs(xb - p[0])) > rr:
                continue
            if w >= 14:
                for o in (-0.25, 0.25):
                    mark_quad("line_y", xa + 1, xb - 1, y + o - 0.08, y + o + 0.08)
            else:
                xx = xa + 2
                while xx + 3 < xb - 1:
                    mark_quad("line", xx, xx + 3, y - 0.08, y + 0.08)
                    xx += 8
for (cx_, cy_) in (SQUAD, (-470.0, AV)):
    ii, jj = ix_of(cx_), iy_of(cy_)
    hx, hy = xw(ii) / 2, yw(jj, cx_) / 2
    for side in (-1, 1):
        y0_ = cy_ + side * (hy + 0.8)
        k = -hx + 0.6
        while k < hx - 0.6:
            mark_quad("line", cx_ + k, cx_ + k + 0.5, min(y0_, y0_ + side * 3.0), max(y0_, y0_ + side * 3.0))
            k += 1.1
        x0_ = cx_ + side * (hx + 0.8)
        k = -hy + 0.6
        while k < hy - 0.6:
            mark_quad("line", min(x0_, x0_ + side * 3.0), max(x0_, x0_ + side * 3.0), cy_ + k, cy_ + k + 0.5)
            k += 1.1

# ================================================================== 경로 (WP_) 정의
G = 1.0         # 지상 경로 높이
D = 60.0        # 드론 경로 높이
ROUTES = {
    "in_a_troops": [(-760, -520, G), (-706, -470, G), (-652, -420, G), (-599, -370, G), (-545, -320, G),
                    (-470, -320, G), (-390, -320, G), (river_x(-320), -320, G + 2.5), (-180, -320, G),
                    (-106, -300, G), (-106, -150, G), (-106, -70, G), (-106, AV, G), (-48, AV + 1, G),
                    (-20, -9, G), (0, 8, G)],
    "in_a_vehicles": [(-760, -520, G), (-700, -470, G), (-700, -400, G), (-700, -320, G), (-700, -180, G),
                      (-700, -70, G), (-690, AV, G), (-545, AV, G), (-470, AV, G), (-400, AV, G),
                      (river_x(AV), AV, G + 2.5), (-180, AV, G), (-106, AV, G), (-60, AV, G), (-10, AV, G)],
    "in_a_drones": [(-760, -520, D), (-640, -420, D), (-520, -300, D), (-400, -200, D), (-260, -110, D),
                    (-120, -30, D), (-30, 14, D), (0, 26, D)],
    "in_b_troops": [(820, -180, G), (800, -100, G), (800, -70, G), (640, -70, G), (500, -70, G), (430, -70, G),
                    (300, -70, G), (170, -70, G), (106, -70, G), (106, AV, G), (70, AV, G), (30, AV, G),
                    (10, -9, G), (0, 8, G)],
    "in_b_vehicles": [(820, -180, G), (880, -120, G), (880, -70, G), (880, AV, G), (720, AV, G), (570, AV, G),
                      (430, AV, G), (300, AV, G), (170, AV, G), (106, AV, G), (60, AV, G), (10, AV, G)],
    "in_b_drones": [(820, -180, D), (680, -150, D), (540, -100, D), (430, -70, D), (280, -30, D), (130, 8, D),
                    (40, 24, D), (0, 26, D)],
    "in_c_troops": [(-60, 560, G), (-60, 510, G), (-106, 500, G), (-106, 430, G), (-106, 355, G), (-106, 210, G),
                    (-106, 70, G), (-72, 56, G), (-72, 20, G), (-72, -6, G), (-24, -6, G), (0, 8, G)],
    "in_c_drones": [(-60, 560, D), (-84, 480, D), (-106, 430, D), (-90, 300, D), (-60, 170, D), (-25, 70, D),
                    (0, 26, D)],
}
RETREAT = {
    # 남서광장역 → 지하 통로(가로 아래 z=-8: x=-545 아래로 북쪽, y=-180 아래로 동쪽) → 병기창고 지하 경사로로 올라옴
    "route_subway": [(SW_ENT["entrance"].x, SW_ENT["entrance"].y, 0.0),
                     (SW_ENT["bottom"].x, SW_ENT["bottom"].y, -4.5),
                     (-545.0, -295.0, -8.0), (-545.0, -250.0, -8.0), (-545.0, -180.0, -8.0),
                     (-500.0, -180.0, -8.0), (-445.0, -180.0, -8.0), (-440.0, -160.0, -8.0),
                     (-440.0, -142.0, -3.5), (round(ARM[0], 2), round(ARM[1], 2), 0.0)],
    # 병기창고 → 북쪽 정문 → y=-70 가로 건너 → 서부환승역 동쪽 궤도 정비 계단 → 중앙로선 궤도 위
    "route_armory": [(round(ARM[0], 2), round(ARM[1], 2), 0.0), (round(ARM[0], 2), ay1 - 12.0, 0.0),
                     (round(ARM[0], 2), ay1 - 1.0, 0.0), (-421.0, -70.0, 0.0), (MAINT[0], -58.0, 0.0),
                     (MAINT[0], MAINT[1] - 2.6, 0.0), (MAINT[0], MAINT[1], TRACK_TOP),
                     (MAINT[0], AV - 1.2, TRACK_TOP), (MAINT[0], AV, TRACK_TOP)],
    "route_monorail": [(MAINT[0], AV, TRACK_TOP), (-400.0, AV, TRACK_TOP), (-330.0, AV, TRACK_TOP),
                       (river_x(AV), AV, TRACK_TOP), (-250.0, AV, TRACK_TOP), (-180.0, AV, TRACK_TOP),
                       (-106.0, AV, TRACK_TOP), (-60.0, AV, TRACK_TOP), (-18.0, AV, TRACK_TOP)],
    "route_cityhall": [(-18.0, AV + 2.6, CENTRAL["top"]), (-28.0, AV + 4.0, CENTRAL["top"]),
                       (-28.0, -14.6, CENTRAL["top"]), (-28.0, -12.6, 0.0), (-22.0, -9.0, 0.0), (-7.0, -2.0, 0.0),
                       (-5.0, 8.0, 0.0), (0.0, 14.0, 0.0)],
}

# ================================================================== 전쟁 피해 (WAR_d0, hidden=1): 브리핑 2에서 코드가 켬
C.group("WAR_d0", hidden=1, war=1, state="overrun")
rng = random.Random(404)
WIND = (-0.34, 0.12)       # 연기가 기우는 쪽 (동남동 바람 → 서북서)
SMOKES = []


def smoke(x, y, h, r, *, dark=0.4, z=0.0):
    mk.smoke_column(C, x, y, z=z, h=h, r=r, drift=WIND, seed=int(abs(x) * 3 + abs(y) * 7), dark=dark, segs=6)
    SMOKES.append((x, y))
    scorch(x, y, r * rng.uniform(1.6, 2.6), z=z)


def scorch(x, y, r, z=0.0):
    pts = []
    for k in range(14):
        a = 2 * math.pi * k / 14
        rr = r * rng.uniform(0.6, 1.15)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    mk.lod_poly_prism(C, "soot", pts, z - 0.3, z + 0.55)


# 차원문 아래: 착지 지점마다 연기 3~4 기둥
for gid, ((gx, gy), gz, rad, tilt, yaw) in GATES.items():
    for k in range(4 if gid == "a" else 3):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(25, rad * 1.2)
        smoke(gx + math.cos(a) * d, gy + math.sin(a) * d, rng.uniform(45, 80), rng.uniform(6, 10), dark=0.5)


def along(route, step, cb_):
    pts = [Vector((p[0], p[1], 0)) for p in route]
    acc = 0.0
    for k in range(len(pts) - 1):
        a, b_ = pts[k], pts[k + 1]
        L = (b_ - a).length
        t = (step - acc)
        while t < L:
            p = a.lerp(b_, t / L)
            d = (b_ - a).normalized()
            cb_(p, d)
            t += step
        acc = (acc + L) % step


def route_smoke(p, d):
    if math.hypot(p.x, p.y - 10) < 60:
        return
    n = Vector((-d.y, d.x, 0)) * rng.choice((-1, 1)) * rng.uniform(16, 34)
    q = p + n
    smoke(q.x, q.y, rng.uniform(30, 70), rng.uniform(4.5, 8), dark=rng.uniform(0.2, 0.7))


for key in ("in_a_troops", "in_a_vehicles", "in_b_troops", "in_b_vehicles", "in_c_troops"):
    along(ROUTES[key][1:], rng.uniform(150, 200), route_smoke)
# 광장 둘레와 검문소
for (x, y, h) in ((-62.0, -27.0, 70), (58.0, -36.0, 55), (-22.0, 50.0, 60), (70.0, 30.0, 45),
                  (452.0, -60.0, 50), (420.0, -95.0, 35), (-96.0, 452.0, 50), (-130.0, 418.0, 40),
                  (sx - 30, sy - 26, 55), (sx - 48, sy + 10, 40), (sx + 10, sy - 50, 45)):
    smoke(x, y, h, rng.uniform(5, 8), dark=0.5)
# 고속도로 위 불탄 차
for xx in (520.0, 610.0):
    mk.lod_box(C, "soot", xx - 2, xx + 2, AV - 3, AV - 1.3, Z_DECK, Z_DECK + 1.4)
    smoke(xx, AV - 2, 50, 4.5, dark=0.8, z=Z_DECK)
# 탄 지붕: 유입 경로 60 m 안 건물 일부
route_segs = []
for key in ("in_a_troops", "in_a_vehicles", "in_b_troops", "in_b_vehicles", "in_c_troops"):
    r_ = ROUTES[key]
    for k in range(len(r_) - 1):
        route_segs.append((r_[k][0], r_[k][1], r_[k + 1][0], r_[k + 1][1]))
burned = 0
for (x0, x1, y0, y1, top) in BUILDINGS:
    if burned > 70:
        break
    if any(seg_rect_dist(*s, x0, x1, y0, y1) < 55 for s in route_segs) and rng.random() < 0.3:
        i_ = min(1.0, (x1 - x0) * 0.1, (y1 - y0) * 0.1)
        mk.lod_box(C, "soot", x0 + i_, x1 - i_, y0 + i_, y1 - i_, top, top + 0.6)
        burned += 1
# R41 차량 행렬 (차량 경로 위)


def r41_vehicle(p, d):
    yaw = math.degrees(math.atan2(d.y, d.x)) - 90.0
    C.rbox("r41_shell", (p.x, p.y, 1.45), (3.0, 7.2, 2.6), (0, 0, yaw))
    C.rbox("r41_metal", (p.x - d.x * 0.6, p.y - d.y * 0.6, 3.1), (1.8, 2.6, 0.8), (0, 0, yaw))
    C.rbox("magenta", (p.x + d.x * 3.4, p.y + d.y * 3.4, 1.9), (2.2, 0.15, 0.25), (0, 0, yaw))


for key in ("in_a_vehicles", "in_b_vehicles"):
    r_ = ROUTES[key]
    cnt = [0]

    def put(p, d, cnt=cnt):
        if cnt[0] < 9 and math.hypot(p.x, p.y) > 140:
            r41_vehicle(p, d)
            cnt[0] += 1
    along(r_[2:], 16.0, put)
# 버려진 시민 차 (비뚤게)
for key in ("in_a_troops", "in_b_troops", "in_c_troops"):
    def put2(p, d):
        if math.hypot(p.x, p.y) > 120 and rng.random() < 0.7:
            n = Vector((-d.y, d.x, 0)) * rng.uniform(-5, 5)
            C.rbox(rng.choice(CAR_KEYS), (p.x + n.x, p.y + n.y, 0.65), (1.7, 3.6, 1.3),
                   (0, 0, math.degrees(math.atan2(d.y, d.x)) + rng.uniform(-70, 70)))
    along(ROUTES[key][1:], 45.0, put2)

# ================================================================== 야간 조명 (GLOW_*, hidden=1): 1막 종료 「정전」 위성 컷
# 해 질 녘 위성 화면에서 코드가 모두 켰다가 시청 → 코어 → 모노레일 → 도심(d1) → 중층(d2) → 외곽(d3) → 교외·고속도로(d4)
# 순서로 끈다(루트 blackout). 노드마다 UNLIT 발광 판만 있다: 가로등 줄(주황), 창·옥상 불빛(따뜻한 흰색),
# 모노레일·코어 AI(시안). 위에서 보는 수평 판이라 1~6 km 위에서 빛 점·빛 줄로 읽힌다.
GLOW_ORDER = ["cityhall", "core", "monorail", "d1", "d2", "d3", "d4"]
GQ = {g: [] for g in GLOW_ORDER}         # 그룹별 (key, 다각형 점) 목록 → 마지막에 그룹마다 한꺼번에 쌓음


def glow_zone(x, y):
    if not in_city(x, y, -1.0):
        return "d4"
    r = math.hypot(x, (y - 30) * 1.1)
    if r < 380:
        return "d1"
    if r < 680:
        return "d2"
    return "d3"


def gq(g, key, x, y, z, s):
    GQ[g].append((key, [(x - s / 2, y - s / 2, z), (x + s / 2, y - s / 2, z), (x + s / 2, y + s / 2, z),
                        (x - s / 2, y + s / 2, z)]))


def gstrip(g, key, p0, p1, w, z):
    d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
    if d.length < 0.5:
        return
    n = Vector((-d.y, d.x, 0.0)).normalized() * (w / 2)
    z0 = z if not isinstance(z, tuple) else z[0]
    z1 = z if not isinstance(z, tuple) else z[1]
    GQ[g].append((key, [(p0[0] - n.x, p0[1] - n.y, z0), (p1[0] - n.x, p1[1] - n.y, z1),
                        (p1[0] + n.x, p1[1] + n.y, z1), (p0[0] + n.x, p0[1] + n.y, z0)]))


rng = random.Random(808)
ZG = Z_ROAD + 0.35
# 가로등 줄: 가로 조각마다 가운데 빛 줄 (간선은 굵게)
for i in range(NX):
    x, w = XS[i]
    for j in range(NY - 1):
        if ns_seg_exists(i, j):
            ya, yb = YS[j][0] - yw(j, x) / 2, YS[j + 1][0] + yw(j + 1, x) / 2
            if not any(urban(a, j) for a in (i - 1, i) if 0 <= a < NX - 1):
                continue
            gstrip(glow_zone(x, (ya + yb) / 2), "fire", (x, ya), (x, yb), 2.4 if w >= 20 else 1.3, ZG)
for j in range(NY):
    y = YS[j][0]
    for i in range(NX - 1):
        if ew_seg_exists(i, j):
            xa, xb = XS[i][0] - xw(i) / 2, XS[i + 1][0] + xw(i + 1) / 2
            if not any(urban(i, b_) for b_ in (j - 1, j) if 0 <= b_ < NY - 1):
                continue
            w = yw(j, (xa + xb) / 2)
            gstrip(glow_zone((xa + xb) / 2, y), "fire", (xa, y), (xb, y), 2.4 if w >= 14 else 1.3, ZG)
gstrip("d2", "fire", DIAG0, DIAG1, 2.4, 0.6)
gstrip("d1", "fire", (-96.0, AV), (66.0, AV), 2.6, ZG)                     # 도심 중앙로
for (ax_, ay_, bx_, by_) in ((-96, -11, 96, -11), (-96, -30.6, 96, -30.6), (-24, 18, 24, 18), (-24, -11, -24, 18),
                             (24, -11, 24, 18), (-96, 60, 96, 60), (-96, -60, 96, -60)):
    gstrip("d1", "fire", (ax_, ay_), (bx_, by_), 1.2, 0.45)                # 도심 보도·광장 둘레
# 건물 불빛: 평지붕은 지붕 위 빛 조각, 박공집은 현관 불빛
for (x0, x1, y0, y1, top) in BUILDINGS:
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    g = glow_zone(cx, cy)
    if (x0, x1, y0, y1) in GABLES:
        if rng.random() < 0.55:
            gq(g, "win_lit", cx + rng.uniform(-2, 2), y0 - 1.6, 0.5, 2.2)
        continue
    if rng.random() > (0.75 if g == "d1" else 0.55):
        continue
    area = (x1 - x0) * (y1 - y0)
    for k in range(max(1, min(4, int(area / 300)))):
        s_ = rng.uniform(2.5, 5.0)
        if x1 - x0 < s_ + 2 or y1 - y0 < s_ + 2:
            continue
        # 한 지붕의 빛 조각끼리 겹칠 수 있어 하나씩 3 cm 위로 쌓는다
        gq(g, rng.choice(("win_lit", "win_lit", "lamp")), rng.uniform(x0 + 1 + s_ / 2, x1 - 1 - s_ / 2),
           rng.uniform(y0 + 1 + s_ / 2, y1 - 1 - s_ / 2), top + 1.2 + 0.03 * k, s_)
# 도심 건물 (downtown() 상가 줄·북쪽·동쪽·EBI 본부) 지붕 불빛
DT_ROOFS = [(-60, -48, 40, 52, 3 + 6 * 2.7), (-46, -32, 40, 52, 3 + 7 * 2.7), (-30, -18, 40, 52, 3 + 5 * 2.7),
            (44, 58, 40, 52, 3 + 8 * 2.7), (60, 72, 40, 52, 3 + 6 * 2.7), (-64, -51, -8, 6, 3 + 5 * 2.7),
            (-64, -51, 10, 24, 3 + 6 * 2.7), (48, 61, -8, 6, 3 + 7 * 2.7), (48, 61, 8, 22, 3 + 5 * 2.7),
            (26, 42, -9, 9, 3 + 6 * 2.7), (26, 40, 11, 22, 3 + 5 * 2.7), (-48, -28, 14, 30, 3 + 5 * 2.7)]
for (nm_, b_) in A.get("shops", []):
    fc = b_["front_center"]
    half = b_["front_len"] / 2 + 1.0
    DT_ROOFS.append((fc.x - half, fc.x + half, -44.0, -31.0, b_["top"]))
for (x0, x1, y0, y1, top) in DT_ROOFS:
    for k in range(2):
        gq("d1", "win_lit", rng.uniform(x0 + 3, x1 - 3), rng.uniform(y0 + 3, y1 - 3), top + 1.2 + 0.03 * k,
           rng.uniform(2.5, 4))
# 시청: 탑 꼭대기 둘레, 날개 지붕, 포르티코, 광장 가로등과 분수
for k in range(10):
    a = 2 * math.pi * k / 10
    gq("cityhall", "lamp", 0 + math.cos(a) * 4.3, 25.0 + math.sin(a) * 4.3, 27.6, 1.8)
for xx in (-14.0, -10.0, 10.0, 14.0):
    for yy in (21.5, 26.0, 30.5):
        gq("cityhall", "win_lit", xx, yy, 12.6, 2.6)
gq("cityhall", "lamp", 0.0, 17.0, 9.6, 6.0)
for (lx, ly) in ((-6.5, -9.5), (6.5, -9.5), (-6.5, 13.0), (6.5, 13.0), (-22.5, 14.5), (22.5, 14.5)):
    gq("cityhall", "lamp", lx, ly, 4.4, 2.4)
gq("cityhall", "lamp", 0.0, 2.0, 3.6, 3.0)
ellipse_glow = []
# 코어 AI: 꼭대기 시안 후광 + 허리 고리 + 바닥 네트워크 고리
for (zz, r0, r1, n_) in ((35.6, 3.0, 7.5, 24), (21.0, 3.6, 6.0, 20), (0.5, 11.0, 13.5, 32)):
    for k in range(n_):
        a0_, a1_ = 2 * math.pi * k / n_, 2 * math.pi * (k + 1) / n_
        GQ["core"].append(("glow", [(32 + math.cos(a0_) * r0, 36 + math.sin(a0_) * r0, zz),
                                    (32 + math.cos(a0_) * r1, 36 + math.sin(a0_) * r1, zz),
                                    (32 + math.cos(a1_) * r1, 36 + math.sin(a1_) * r1, zz),
                                    (32 + math.cos(a1_) * r0, 36 + math.sin(a1_) * r0, zz)]))
gq("core", "cyan_hot", 32.0, 36.0, 36.0, 3.0)
# 모노레일: 궤도 위 시안 줄 (도심 구간 포함) + 역 지붕 불빛
for path, zf_ in ((WEST_LINE + [(136.0, AV, 7.5)], None), (RING, ring_z), (BRANCH, None), (EAST_LINK, None)):
    pts = mk.path_points([(p[0], p[1], 7.5) for p in path], 40.0)
    for k in range(len(pts) - 1):
        za = (zf_(pts[k][0], pts[k][1]) if zf_ else 7.5) + 0.75
        zb = (zf_(pts[k + 1][0], pts[k + 1][1]) if zf_ else 7.5) + 0.75
        gstrip("monorail", "glow", pts[k][:2], pts[k + 1][:2], 2.0, (za, zb))
for (x0, x1, y0, y1, zz) in ((-31, -5, AV - 5, AV + 5, CENTRAL["roof"] + 0.7), (-505, -435, AV - 5, AV + 5, TR_LO["roof"] + 0.7),
                             (-475, -465, -58, 16, TR_HI["roof"] + 0.7)):
    for k in range(int((x1 - x0) / 6)):
        gq("monorail", "lamp", x0 + 3 + k * 6, (y0 + y1) / 2, zz, 2.2) if x1 - x0 > y1 - y0 else None
    for k in range(int((y1 - y0) / 6)):
        gq("monorail", "lamp", (x0 + x1) / 2, y0 + 3 + k * 6, zz, 2.2) if y1 - y0 > x1 - x0 else None
# d4: 고속도로 (도심 진입로부터 외곽 성토 구간까지) 양쪽 가로등 줄, 농가 불빛
gstrip("d4", "lamp", (66.0, AV - 4.5), (1000.0, AV - 4.5), 1.2, Z_DECK + 1.0)
gstrip("d4", "lamp", (66.0, AV + 4.5), (1000.0, AV + 4.5), 1.2, Z_DECK + 1.0)
for k in range(len(HWY_PTS) - 1):
    a_, b_ = HWY_PTS[k], HWY_PTS[k + 1]
    if a_[0] > 9000:
        break
    for off in (-8.5, 8.5):
        d = Vector((b_[0] - a_[0], b_[1] - a_[1], 0)).normalized()
        n = Vector((-d.y, d.x, 0)) * off
        gstrip("d4", "lamp", (a_[0] + n.x, a_[1] + n.y), (b_[0] + n.x, b_[1] + n.y), 1.4, Z_EMB + 1.0)
for (fx, fy, fz) in FARMS:
    gq("d4", "win_lit", fx, fy, fz, 3.0)
    gq("d4", "lamp", fx + 22, fy + 2, fz, 2.4)
GLOW_TRIS = 0
for k, g in enumerate(GLOW_ORDER):
    C.group(f"GLOW_{g}", hidden=1, glow=1, order=k)
    for key, pts in GQ[g]:
        b = C.bm(key)
        f = b.faces.new([b.verts.new(p) for p in pts])
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
        GLOW_TRIS += 2
print(f"[ov] glow quads " + ", ".join(f"{g}={len(GQ[g])}" for g in GLOW_ORDER))

# ================================================================== 마커
C.group("city")
M = {
    "MARK_cityhall": (0.0, 26.0, 0.0),
    "MARK_plaza": (0.0, 2.0, 0.0),
    "MARK_core": (32.0, 36.0, 0.0),
    "MARK_hq": (-38.0, 22.0, 0.0),
    "MARK_station_central": (-18.0, AV, TRACK_TOP),
    "MARK_station_transfer": (-470.0, AV, TRACK_TOP),
    "MARK_subway_entrance": (round(SW_ENT["entrance"].x, 2), round(SW_ENT["entrance"].y, 2), 0.0),
    "MARK_squad": (-552.0, -327.0, 0.0),
    "MARK_gate_a": (-760.0, -520.0, 0.0),
    "MARK_gate_b": (820.0, -180.0, 0.0),
    "MARK_gate_c": (-60.0, 560.0, 0.0),
    "MARK_unit_2": (430.0, -70.0, 0.0),
    "MARK_unit_3": (-106.0, 430.0, 0.0),
    "MARK_region": (250.0, -40.0, 0.0),
    "MARK_armory": (round(ARM[0], 2), round(ARM[1], 2), 0.0),
}
hp = hwy_at(1800.0)
M["MARK_highway_erpien"] = (round(hp[0], 1), round(hp[1], 1), Z_EMB)
MARK_PROPS = {
    "MARK_gate_a": {"gate": "GATE_a", "gateZ": GATES["a"][1], "radius": GATES["a"][2], "label": "차원문 A"},
    "MARK_gate_b": {"gate": "GATE_b", "gateZ": GATES["b"][1], "radius": GATES["b"][2], "label": "차원문 B"},
    "MARK_gate_c": {"gate": "GATE_c", "gateZ": GATES["c"][1], "radius": GATES["c"][2], "label": "차원문 C"},
    "MARK_cityhall": {"label": "모나티엄 시청"},
    "MARK_core": {"label": "코어 AI"},
    "MARK_hq": {"label": "EBI 진압반 본부"},
    "MARK_station_central": {"label": "모노레일 중앙역"},
    "MARK_station_transfer": {"label": "서부환승역", "upperZ": round(TR_HI["top"], 2)},
    "MARK_subway_entrance": {"label": "남서광장역"},
    "MARK_squad": {"label": "진압반 특수작전부 분대", "friendly": 1},
    "MARK_unit_2": {"label": "진압반 2검문소", "friendly": 1},
    "MARK_unit_3": {"label": "진압반 3검문소", "friendly": 1},
    "MARK_highway_erpien": {"label": "알프토반 → 에르피엔"},
    "MARK_region": {"label": "모나티엄 일대"},
    "MARK_armory": {"label": "모나티엄 병기창고", "friendly": 1, "size": f"{ax1 - ax0:.0f},{ay1 - ay0:.0f}"},
}
for nm, p in M.items():
    C.marker(nm, p, props=MARK_PROPS.get(nm))
for key, pts in list(ROUTES.items()) + list(RETREAT.items()):
    for k, p in enumerate(pts, start=1):
        props = {"route": key}
        if key.endswith("drones"):
            props["air"] = 1
        if key.startswith("in_"):
            props["side"] = "enemy"
        else:
            props["side"] = "friendly"
        C.marker(f"WP_{key}_{k:02d}", (round(float(p[0]), 2), round(float(p[1]), 2), round(float(p[2]), 2)),
                 props=props)

# 충돌체는 쓰지 않는다 (위성 시점 전용 장면): 키트 모듈이 만든 COL_ 상자를 버린다
C.cols.clear()
# 글자·로고 메시(간판, 표지, 바리케이드 문구, 엘프 로고)는 300 m 위에서 읽히지 않으므로 버린다 (도심 삼각형의 약 20%)
for (_, _, _, o) in C.objs:
    data = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)
C.objs.clear()

print(f"[ov] buildings {STATS['bld']} trees {STATS['trees']} cars {STATS['cars']} forests {len(FORESTS)} "
      f"hedges {HEDGES} smokes {len(SMOKES)} bridges {len(BRIDGES)}")
ROOT = {
    "sky": "#b9c7cf",
    "fog": "4000,16000",
    "sun": "0.80,0.50,0.33",        # 동남동, 고도 30° (아침)
    "ambient": 1.3,
    "near": 2,
    "far": 30000,
    "physics": 0,
    "collider": 0,
    "noOutline": 1,                 # 높은 곳에서 보므로 먹선 헐을 붙이지 않는다
    "sunIntensity": 2.6,
    "sunColor": "#fff2dc",
    "hemiSky": "#e6eef4",
    "hemiGround": "#7e7a70",
    "timeOfDay": "morning",
    "scene": "ACT1_OVERVIEW",
    "warNode": "WAR_d0",
    "blackout": ",".join(GLOW_ORDER),         # 「정전」 컷에서 끄는 순서 (GLOW_<이름> 노드, 모두 hidden=1)
    "gates": "GATE_a,GATE_b,GATE_c",
    "routes": ",".join(list(ROUTES) + list(RETREAT)),
}
C.finish("levels/act1_overview.glb", root_props=ROOT, outline=0.0)
