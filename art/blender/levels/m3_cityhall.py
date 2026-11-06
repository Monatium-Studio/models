"""1막 M3 「둠스데이」: 시청 앞 마지막 방어선 (D-DAY 17:55 무렵, 해 질 녘).

npm run model -- art/blender/levels/m3_cityhall.py   → public/models/levels/m3_cityhall.glb

[원작] 엘레나가 제어권을 되찾은 뒤 둠스데이 프로토콜을 발동한다. 모나티엄 시청은 지하 23층이다. 주말농장 법칙:
       아무도 죽지 않는다(부상자는 쓰러져 기절했을 뿐이다).
[오리지널] M2의 광장 방어선은 무너졌고(쓰러진 바리케이드, 흩어진 모래주머니, 그을음, 불탄 차, 추락한 드론),
       새 방어선은 시청 포르티코(계단 위 기둥 사이 모래주머니)다. 정문이 열려 있고 안쪽 복도 끝은 지하로 내려간다
       (대피소 표지는 없다). 리타는 카운트다운 동안 버티며 방어선 위와 바로 뒤에 쓰러진 부상 진압반원과 숨은 시민을
       방어선 뒤(시청 서쪽 골목 끝) 승차 지점에 오는 탈출 차량(험비, 스크립트 m3evac.ts)에 태운다. 차는 서쪽 외곽에서
       EBI 본부 뒤 뒷길로 들어와 서고, 시청 뒤를 돌아 북쪽 외곽으로 빠진다(광장에는 들어가지 않는다).
       SCREEN_cityhall에 카운트다운이 뜬다(스크립트가 그린다). 코어 AI 탑은 아직 켜져 있다.
계약 노드: 스크래치패드 act1_level_contract.md "M3 「둠스데이」" (조명은 해 질 녘 17:55로 바뀜). 실행하면 [m3] 줄에
노드 좌표를 찍는다.

좌표 (Blender, m): 원점 = 광장 가운데, +Y = 북쪽(시청). 지면 z = 0, 차도 z = -0.15, 포르티코 바닥 z = 0.9
(계단 y 11.3..14, 바닥 y 14..19, 기둥 y 14.9, 정문 x -1.3..1.3, y 19). 광장 (-24..24, -11..18), 분수 (0, 2).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import monatium_defense_kit as dk  # noqa: E402

cb.reset()
C = mk.City("m3_cityhall")
AV = mk.AVENUE_Y
TOP = dk.TRACK_TOP
PZ = 0.9
WIND = (-0.32, 0.12)
SQ = {k: f"characters/squad_{k}.glb" for k in ("sabre", "rona", "jesty", "karen")}
SQ_W = {"sabre": "m4a1", "rona": "m4a1", "jesty": "m870", "karen": "m249"}
RIOT = "characters/_kit_elfinia_soldier.glb"
CIV = "characters/_kit_base.glb"
NODES = []


def M(name, loc, **kw):
    C.marker(name, loc, **kw)
    NODES.append((name, tuple(round(v, 2) for v in loc), kw.get("props", {})))


# ================================================================== 도심 (해 질 녘: 가로등 켜짐)
A = mk.downtown(C, variant="dusk", training=False, train=False, highway_on=True, skyline=False, screens=True)
C.group("plaza")
# 판석 없는 낮은 땅(-0.32, 자동 오르기 0.28로 못 나온다) 메우기. (-48, -28, 12, 14): 훈련장 판석(y 12까지)과 EBI 본부(y 14부터)
# 사이 2 m 도랑 (2026-11-03: 방어선 오른쪽 날개 서쪽 끝, 빠지면 5초 넘게 갇혔다)
for box in ((24, 42, -11, -9), (24, 26, -9, 22), (26, 42, 9, 11), (40, 42, 11, 22), (-48, -24, -11, -9),
            (-26, -24, -9, 12), (-48, -28, 12, 14)):
    mk.paving(C, *box, grout=None, tile=1.6)
# 광장 벤치 등판: COL 윗면이 7 cm 판이라 좌판에서 뛰어 올라서면 그 위에 서서 내려오지 못하고 섰다 (2026-11-03 봇 걷기,
# 1.7초) → 등판 COL을 0.6 m 위로 능선(66°)으로 깎아 올라서지 못하고 미끄러져 내려오게 한다 (보이는 등판 높이 0.65 그대로)
for sx in (-1, 1):
    for k in range(3):
        bx, by = sx * 17.5 - sx * 2.6, -6 + k * 7.5
        rx = bx + 0.235 * sx
        dk.drop_cols_in(C, (rx - 0.045, rx + 0.045, by - 0.76, by + 0.76, -0.01, 0.66))
        pts = []
        for ly in (-0.75, 0.75):
            for (lx, lz) in ((-0.035, 0.0), (0.035, 0.0), (-0.035, 0.6), (0.035, 0.6), (0.0, 0.68)):
                pts.append((rx + lx, by + ly, lz))
        dk.col_hull(C, pts, hint="b")
# 도심 COL 보수 (배경 판석, 판석 없는 땅, 중앙 화단, 코어 탑, 표지 문형) + 맵 경계 (도심 판석 끝, 진입로는 밖)
dk.downtown_cols(C, A)
dk.downtown_bounds(C, A)
# 쓰러진 가로등: 서 있던 것을 뽑고 눕힌다
FALLEN = [("plaza", (6.5, -9.5), 125), ("avenue", (-6.0, -11.6), 200), ("avenue", (18.0, -11.6), 160),
          ("avenue", (24.0, -30.0), 20)]
for grp, (lx, ly), yaw in FALLEN:
    dk.cut_box(C, grp, ("dark", "gold", "lamp", "lamp_off"), (lx - 0.3, lx + 0.3, ly - 0.3, ly + 0.3, -0.2, 4.6))
    dk.drop_cols_in(C, (lx - 0.3, lx + 0.3, ly - 0.3, ly + 0.3, -0.2, 4.6))    # 뽑은 기둥의 COL
    C.group(grp)
    dk.fallen_lamp(C, lx, ly, yaw)
# 동쪽 옆길 (M2와 같다)
C.group("avenue")
C.box("asphalt", 43.0, 47.0, -11.0, 38.0, -0.02, 0.02, kind="detail")
for x in (42.0, 47.0):
    C.box("pave_d", x, x + 1.0, -11.0, 38.0, -0.02, 0.06, kind="detail")
C.strip("line_y", (45.0, -10.0, 0.02), (45.0, 37.0, 0.02), 0.1, lift=0.006)
C.col(42.0, 48.0, -11.0, 38.0, -0.4, 0.0)
mk.street_sign(C, 47.6, -10.4, "시청 동로", "CITY HALL E. ST", yaw=0)
C.group("track")
for k in range(17):
    dk.pillar(C, -120.0 + 16 * k, visual=False)
dk.catwalks(C, -104.0, -33.0)
dk.track_gate(C, -103.8, face=1, text=("점검 구간 · 통행 금지", "MAINTENANCE · NO ENTRY"))

# ================================================================== 중앙역 (M2와 같은 역, 계단탑)
C.group("station")
SS_X0, SS_Y0, SS_Y1 = -29.4, -15.9, -11.5
ST = dk.central_station(C, -33.0, -5.0, north_open=(SS_X0 + 0.1, SS_X0 + 2.45))
dk.stair_tower(C, SS_X0, SS_Y0, SS_Y1, ST["top"], z0=0.0, top_lane=-1, top_end=-1, style="glass",
               top_open=("-y", SS_X0 + 0.1, SS_X0 + 2.45), bottom_open=("+y", SS_X0 + 0.1, SS_X0 + 2.45))

# ================================================================== 시청: 열린 정문 + 대피소 복도, 앞면 그을음
# 대피소 표지는 달지 않는다 (2026-11-02: 시민·부상자는 지하 대피소가 아니라 탈출 차량으로 도시 밖에 보낸다)
DOOR = dk.cityhall_doorway(C, lit=True, shelter=False)
C.group("cityhall")
rng = random.Random(33)
for (x, z, r) in ((-11.0, 4.2, 1.6), (9.5, 2.0, 1.2), (13.0, 7.5, 1.4), (-6.5, 9.0, 1.0)):
    pts = [(math.cos(a) * r * rng.uniform(0.7, 1.2), math.sin(a) * r * rng.uniform(0.6, 1.1))
           for a in [i * 2 * math.pi / 12 for i in range(12)]]
    C.decal("soot", pts, (x, 18.97, z), (0, -1, 0), lift=0.035)
for x in (-4.5, 4.5):
    C.decal("soot", [(math.cos(a) * 0.35, math.sin(a) * 0.9) for a in [i * 0.785 for i in range(8)]],
            (x, 14.9 - 0.49, 3.2), (0, -1, 0), lift=0.01)

# ================================================================== 새 방어선: 포르티코
C.group("lastline")
for x in (-6.0, -3.0, 3.0, 6.0):
    dk.sandbags(C, x, 14.35, yaw=0, z=PZ, n=3, rows=3)
# 포르티코 양 옆 모래주머니: 포르티코 바닥(x ±8) 위에, 바깥 기둥(x ±7.5, y 14.4..15.4) 뒤에 붙여 쌓는다
# (2026-11-03 사용자: "모래주머니는 언제까지 공중부양하게 둘건데" → 예전 x ±8.6은 바닥 밖이라 땅 위 0.9 m에 떠 있었다.
# 기둥과의 틈은 2 cm: 캡슐이 들어가 낄 틈을 남기지 않는다)
for x in (-7.76, 7.76):
    dk.sandbags(C, x, 16.36, yaw=90, z=PZ, n=3, rows=3)
# 계단 아래 앞줄과 양옆 (화단 + 바리케이드 + 모래주머니)
for sx in (-1, 1):
    mk.planter(C, sx * 10.0 - 1.2, sx * 10.0 + 1.2, 12.9, 14.1, h=0.75, hedge=True)
    dk.riot_barricade(C, sx * 6.2, 10.5, yaw=sx * 12)
    dk.sandbags(C, sx * 11.8, 16.4, yaw=sx * 70, n=4, rows=3)
    dk.jersey_barrier(C, sx * 9.6, 10.2, 0.0, sx * -20, length=2.0)
# 포르티코 위 보급: 탄약, M72, M249, 들것
AMMO_P = dk.ammo_crate(C, -1.9, 17.6, PZ, 0, key="violet", text="진압반 · 탄약")
dk.ammo_crate(C, -2.2, 18.3, PZ, 10)
M72_P = dk.weapon_crate(C, 3.0, 17.7, PZ, 0, text="U.S. ARMY · M72 LAW")
M249_P = dk.weapon_crate(C, 5.6, 17.7, PZ, 0, text="U.S. ARMY · M249")
dk.supply_stack(C, 7.15, 18.2, PZ, 0, n=3, seed=41)     # M249 상자(x ..6.25)와 겹치지 않게
dk.stretcher(C, -5.0, 17.9, z=PZ, yaw=90)
dk.stretcher(C, -6.4, 18.2, z=PZ, yaw=85)
# 비워진 지휘소 자리: 넘어진 탁자 + 흩어진 지도
C.rbox("navy_l", (-6.8, 16.9, PZ + 0.35), (1.6, 0.04, 0.8), rot=(0, 0, 8), kind="detail")
C.ocol((-6.8, 16.9, PZ - 0.05), (1.6, 0.08, 0.8), 8)
for k in range(5):
    C.decal("paper", mk.hw.rrect(0.3, 0.42, 0.01, 1), (-7.6 + k * 0.5, 16.2 + (k % 2) * 0.4, PZ), (0, 0, 1),
            up=(math.cos(k), math.sin(k), 0), lift=0.01 + k * 0.001)

# ================================================================== 무너진 M2 방어선 + 광장 피해
C.group("ruin")
ARC_C, ARC_R = (0.0, 18.0), 26.0
PLAN = ["S", "B", "s", "S", "B", "b", "S", "b", "B", "S", "s", "B", "S"]
for i, k in enumerate(PLAN):
    th = math.radians(-42.0 + 7.0 * i)
    nx, ny = math.sin(th), -math.cos(th)
    px, py = ARC_C[0] + nx * ARC_R, ARC_C[1] + ny * ARC_R
    yaw = math.degrees(mk.yaw_to((px, py), (px + nx, py + ny)))
    if k in ("B", "b"):
        dk.broken_barricade(C, px, py, yaw + rng.uniform(-30, 30), seed=100 + i)
    elif k in ("S", "s"):
        dk.spilled_sandbags(C, px, py, n=7, r=1.3, seed=120 + i, yaw=yaw)
    if i % 3 == 1:
        dk.scorch_mark(C, px + nx * 1.5, py + ny * 1.5, rng.uniform(1.6, 2.6), seed=140 + i)
# 무너진 M2 방어선의 잔해: 불탄 차, 추락 드론, 넘어진 바리케이드, 빈 들것
dk.car(C, -13.2, -0.8, 35, z=0.0, burned=True, seed=7)
dk.fire(C, -13.6, -1.2, 0.7, s=0.6, seed=7)
dk.crashed_drone(C, 7.8, -6.2, yaw=40, s=1.2, seed=8)
dk.car(C, -4.6, -15.6, 97, burned=True, seed=9)
dk.fire(C, -4.8, -15.4, 0.5, s=0.7, seed=9)
dk.broken_barricade(C, 16.6, -3.6, 150, seed=10)
dk.spilled_sandbags(C, 18.2, -4.6, n=6, r=1.1, seed=11)
dk.stretcher(C, -11.0, 1.0, yaw=-30)
dk.stretcher(C, 7.6, -2.8, yaw=20)
# 추락 드론 하나 더 + 그을음 + 잔해
dk.crashed_drone(C, -7.2, 7.6, yaw=-70, s=1.0, seed=12)
for j, (x, y, r) in enumerate(((-2.0, -6.0, 3.0), (11.0, 3.5, 2.2), (-18.0, -7.0, 2.4), (3.5, 9.0, 1.8),
                               (20.0, 6.0, 2.0), (-9.0, -9.5, 2.0))):
    dk.scorch_mark(C, x, y, r, seed=160 + j)
for j, (x, y) in enumerate(((-15.5, 11.0), (14.0, 12.0), (21.0, -9.0))):
    dk.rubble(C, x, y, r=1.1, h=0.6, seed=170 + j)
# 버스 정류장 (깨진 유리)
dk.bus_shelter(C, 13.0, -12.2, yaw=0, broken=True)

# ================================================================== 대피: 방어선 뒤 승차 지점 + 시청 뒷길 (2026-11-03)
# 사용자: "적이 바글바글한 곳에 부상자를 데려다 놓고 탈출 차량이 오는 게 말이 돼?" → 승차 지점을 방어선 뒤, 시청 서쪽
# 골목(시청 기단 x -18 ~ EBI 본부 정면 x -28) 북쪽 끝으로 옮긴다. 험비는 서쪽 외곽에서 EBI 본부 뒤 뒷길(y 33..39)로
# 들어와 시청 서북 모퉁이(EVAC_STOP)에 동쪽을 보고 서서 오른쪽(골목 쪽) 문을 열고, 시청 뒤를 돌아 북쪽(x -10)으로
# 빠진다. 광장(R41이 오는 쪽)에는 들어가지 않는다. 차 길·자리는 m3evac.ts(ROUTE_IN·ROUTE_OUT·STOP)와 같다.
C.group("backroad")
EVAC_STOP = (-22.0, 36.0)
# EBI 본부 뒤 판석 없는 낮은 땅(-0.32: 내려서면 다시 못 오르는 0.32 m 턱) → 판석
mk.paving(C, -48.0, -28.0, 30.0, 36.0, grout=None, tile=1.6)
# 차로: 판석 위 2 cm 아스팔트 띠(장식, 걷기 바닥은 판석 COL) + 가운데 황색선. 맵 끝(x -96, y 60)에서 끝난다: 그 너머는
# 낮은 바닥(-0.32)이라 경계 벽은 낭떠러지 막이로 남고(보이는 길을 막는 투명 벽이 아니다), 차만 내려서 사라진다
for (x0, x1, y0, y1) in ((-96.0, -7.0, 33.0, 39.0), (-13.0, -7.0, 39.0, 60.0)):
    C.box("asphalt", x0, x1, y0, y1, -0.02, 0.02, kind="detail")
C.strip("line_y", (-96.0, 36.0, 0.02), (-17.0, 36.0, 0.02), 0.1, lift=0.006)
C.strip("line_y", (-10.0, 42.0, 0.02), (-10.0, 60.0, 0.02), 0.1, lift=0.006)
# 승차 지점: 골목 쪽 바닥에 노란 테이프 칸 + 글자 (리타가 부축해 오는 곳)
HX, HY = -21.6, 33.2
for (a, b) in (((-1.4, -0.9), (1.4, -0.9)), ((1.4, -0.9), (1.4, 0.7)), ((1.4, 0.7), (-1.4, 0.7)), ((-1.4, 0.7), (-1.4, -0.9))):
    C.strip("hazard", (HX + a[0], HY + a[1], 0.0), (HX + b[0], HY + b[1], 0.0), 0.08, lift=0.014)
C.text("white", "대피 차량 · EVAC", 0.32, (HX, HY - 0.1, 0.0), (0, 0, 1), up=(0, 1, 0), lift=0.016)
# 골목 어귀 가림막: 진압반 방패벽(높이 1.9)을 EBI 정면에서 x -20.8까지 세워 광장에서 승차 지점이 보이지 않게 한다.
# 판 아래(0.46 m까지)는 모래주머니 두 줄로 막는다. 기단(x -18) 쪽 2.7 m는 사람이 지나는 길로 비운다.
# 충돌체는 보이는 판 높이(0.86 h)까지
for k in range(3):
    bx = -26.8 + 2.4 * k
    dk.riot_barricade(C, bx, 19.6, yaw=0, w=2.4, h=1.9, col=False)
    dk.col_obox(C, (bx, 19.6, 0.86 * 1.9 / 2), (2.4, 0.35, 0.86 * 1.9), 0.0)
    dk.sandbags(C, bx, 19.6, yaw=0, n=4, rows=2)

# ================================================================== 큰길 피해 (불타는 차, R41 방벽, 그을음)
C.group("war")
for j, (x, y, yaw) in enumerate(((-26.0, -24.8, 80), (5.0, -25.4, 100), (30.0, -17.0, 75), (-58.0, -17.2, 95),
                                 (52.0, -24.6, 92))):
    dk.burning_wreck(C, x, y, yaw, seed=60 + j, drift=WIND, smoke_h=30.0)
    dk.scorch_mark(C, x + 1.4, y + 0.6, 2.8, z=-0.15, seed=70 + j)
    M(f"FX_smoke_{j + 1:02d}", (x, y, 1.2), props={"dir": "0,1,0", "strength": 0.9})
for j, (x, y, yaw, col) in enumerate(((-44.0, -24.6, 84, "car_b"), (-14.0, -17.1, 263, "car_w"),
                                      (38.0, -28.8, 6, "car_r"), (16.0, -24.4, 92, "car_y"))):
    dk.car(C, x, y, yaw, color=col, seed=80 + j)
for j, (x, y, yaw) in enumerate(((-36.0, -26.0, 10), (-10.0, -27.6, -8), (22.0, -26.8, 4), (44.0, -15.4, 175))):
    dk.r41_barrier(C, x, y, yaw, z=0.0 if (y > -14.2 or y < -27.4) else -0.15)   # 보도 위는 0 (차도 높이면 15 cm 묻혔다)
dk.crashed_drone(C, 26.0, -21.5, yaw=10, z=-0.15, s=1.1, seed=13)
# 남쪽 상가 옥상 화재
dk.fire(C, -30.0, -38.0, 21.0, s=1.6, seed=14)
dk.smoke_plume(C, -30.0, -38.0, z=22.0, h=60.0, r=4.0, drift=WIND, seed=15, dark=0.7)

# ================================================================== 원경 (고층 고리, 바닥판, 짙은 연기)
C.group("far")
dk.far_ring(C, 0.0, 0.0, radius=150.0, n=22, seed=91, rx=1.2, h=(28, 60),
            skip=lambda sx, sy: sx > 60 and abs(sy - AV) < 16)
dk.far_ring(C, 0.0, 0.0, radius=230.0, n=24, seed=92, rx=1.15, h=(40, 90),
            skip=lambda sx, sy: sx > 60 and abs(sy - AV) < 20)
C.box("pave_d", -300, 300, -260, 260, -0.6, -0.32, kind="fine")
C.col(-300, 300, -260, 260, -0.9, -0.32)
dk.horizon_smoke(C, [(-150, 120, 120, 11, 1.0), (-210, -80, 100, 12, 1.0), (130, 150, 130, 12, 1.0),
                     (100, -170, 110, 11, 1.0), (-60, 200, 115, 10, 1.0), (230, 20, 110, 11, 1.0),
                     (-90, -150, 90, 9, 1.0), (60, 110, 80, 8, 1.0)], drift=WIND, seed=44)

# ================================================================== 경보등 (카운트다운과 함께 켬)
C.group("ALERTS")
n = 0
for (x, y) in ((-6.5, -9.5), (-22.5, 14.5), (22.5, 14.5), (-22.8, -10.2), (22.8, -10.2), (-6.5, 13.0), (6.5, 13.0)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, 4.75 if abs(x) < 10 else 4.45), blink=0.6 + 0.07 * n)
    M(f"FX_siren_{n:02d}", (x, y, 4.2), props={"sound": "siren", "group": "alert"})
for (x, y, z) in ((-15.0, 19.6, 12.4), (15.0, 19.6, 12.4), (0.0, 13.6, 9.6)):
    n += 1
    mk.alert_beacon(C, f"alert_{n:02d}", (x, y, z), blink=0.55 + 0.05 * n, siren=False)

# ================================================================== 마커
C.group("markers")
M("SPAWN_player", (0.0, 16.3, PZ), face=(0.0, 0.0))
M("SPAWN_evac", (-1.6, 16.0, PZ), face=(-8.0, 8.0))   # 포르티코 위 (방어선 뒤, 부상자 쪽을 봄)
M("SPAWN_lastline", (0.0, 15.4, PZ), face=(0.0, 0.0))
M("MARK_shelter", (DOOR["door"][0], DOOR["door"][1] - 0.2, PZ), face=(0.0, 0.0))
M("MARK_lastline", (0.0, 15.0, PZ), face=(0.0, 0.0))
for who, (x, y) in (("sabre", (-3.0, 15.2)), ("rona", (3.0, 15.2)), ("jesty", (-6.0, 15.2)), ("karen", (6.0, 15.2))):
    M(f"ALLY_{who}", (x, y, PZ), face=(x, 0.0), props={"who": who, "behavior": "hold", "model": SQ[who],
                                                       "weapon": SQ_W[who]})
for j, (x, y) in enumerate(((-6.6, 15.9), (6.6, 15.9), (-4.6, 15.4), (4.6, 15.4)), start=1):
    M(f"ALLY_riot_{j:02d}", (x, y, PZ), face=(x, 0.0),
      props={"who": "riot", "behavior": "hold", "model": RIOT, "weapon": "monatium_riot_carbine"})
# 분대 자리: 앞쪽(계단 아래·양옆 화단) → 마지막(포르티코 위 모래주머니 뒤)
for sec, center, spots, z in (
        ("portico", (0.0, 11.6), {"sabre": (-6.2, 11.4), "rona": (6.2, 11.4), "jesty": (-10.0, 14.9),
                                  "karen": (10.0, 14.9)}, 0.0),
        ("lastline", (0.0, 15.3), {"sabre": (-3.0, 15.1), "rona": (3.0, 15.1), "jesty": (-6.0, 15.1),
                                   "karen": (6.0, 15.1)}, PZ)):
    dk.hold_marks(C, sec, center, spots, z=z, face=(0.0, -20.0))
    NODES.append((f"MARK_hold_{sec}", (*center, z), {}))
    for who, p in spots.items():
        NODES.append((f"MARK_hold_{sec}_{who}", (*p, z), {}))
# 엄폐점: 기둥(서서), 모래주머니·화단·바리케이드(앉아서)
COV = [((-6.0, 15.0, PZ), "low"), ((-3.0, 15.0, PZ), "low"), ((3.0, 15.0, PZ), "low"), ((6.0, 15.0, PZ), "low"),
       ((-7.5, 15.6, PZ), "high"), ((-1.5, 15.6, PZ), "high"), ((1.5, 15.6, PZ), "high"), ((7.5, 15.6, PZ), "high"),
       ((-10.0, 14.6, 0.0), "low"), ((10.0, 14.6, 0.0), "low"), ((-6.2, 11.2, 0.0), "low"), ((6.2, 11.2, 0.0), "low")]
for j, (p, h) in enumerate(COV, start=1):
    M(f"COVER_portico_{j:02d}", p, face=(p[0] * 0.8, -10.0), props={"height": h})
# 트리거
for tid, box in (("shelter", (-1.3, 1.3, 19.4, 21.6, PZ - 0.5, PZ + 3.0)),
                 ("breach", (-9.0, 9.0, 8.6, 11.6, -0.5, 3.0))):
    dk.trig(C, tid, *box)
    NODES.append((f"TRIG_{tid}", box, {}))
# 집기
M("PICKUP_ammo_portico", (-1.9, 17.6, AMMO_P + 0.04), yaw=90, props={"weapon": "ammo"})
M("PICKUP_m72_portico", (3.0, 17.55, M72_P + 0.04), yaw=90, props={"weapon": "m72", "lay": "side"})
M("PICKUP_m249_portico", (5.6, 17.55, M249_P + 0.04), yaw=90, props={"weapon": "m249", "lay": "side"})
# 부상 진압반원 4: 방어선 위와 바로 뒤에 쓰러져 있다 (2026-11-03: 적 쪽 광장이 아니다). 리타가 부축해 뒤쪽 승차 지점
# (시청 서쪽 골목 끝)으로 데려간다. 소품 곁에 붙여 앉혀 사람과 소품 사이에 끼는 틈(캡슐 폭 남짓)을 남기지 않는다
WOUNDED = [
    (-11.65, 13.5, 0.0, (-16.0, 15.0)),       # 오른쪽 끝 화단 서쪽 면에 기대
    (-7.4, 10.85, 0.0, (-7.4, 2.0)),          # 계단 서쪽 끝 첫 단 앞 바닥 (단에 등을 기댐, 앞은 바리케이드)
    (-4.2, 16.8, PZ, (-4.2, 22.0)),           # 포르티코 모래주머니 뒤 (들것 곁)
    (7.4, 10.85, 0.0, (7.4, 2.0)),            # 계단 동쪽 끝 첫 단 앞 바닥
]
for i, (wx, wy, wz, face) in enumerate(WOUNDED, start=1):
    M(f"NPC_wounded_{i}", (wx, wy, wz), face=face,
      props={"model": RIOT, "name": "부상 진압반원", "pose": "sit_dazed", "look": "none"})
# 시민 8: 시청 정문 앞 3, 골목 어귀 가림막 뒤 2, 동쪽 모래주머니 뒤 3 (모두 방어선 뒤)
SB_C, SB_D, SB_N = (11.8, 16.4), (0.342, 0.940), (-0.940, 0.342)      # 동쪽 모래주머니 (yaw 70) 축·뒤쪽
CIVS = [((-0.5, 18.5, PZ), (-0.5, 25.0)), ((0.5, 18.65, PZ), (0.5, 25.0)), ((1.45, 18.45, PZ), (1.45, 25.0)),
        ((-24.0, 21.0, 0.0), (-24.0, 30.0)), ((-22.8, 21.3, 0.0), (-22.8, 30.0))]
for t in (-0.8, 0.05, 0.9):
    cx, cy = SB_C[0] + SB_D[0] * t + SB_N[0] * 0.51, SB_C[1] + SB_D[1] * t + SB_N[1] * 0.51
    CIVS.append(((cx, cy, 0.0), (cx + SB_N[0] * 5, cy + SB_N[1] * 5)))
for i, (p, away) in enumerate(CIVS, start=1):
    M(f"NPC_civ_{i:02d}", p, face=away, props={"model": CIV, "name": "시민", "pose": "cower", "look": "none"})

# ---------------------------------------------------------------- 적 (전부 spawn=manual)


def E(eid, loc, kind, group, behavior, face=None, path=None):
    dk.enemy(C, eid, loc, kind, group, behavior, face=face, path=path)
    NODES.append((f"ENEMY_{eid}", tuple(round(v, 2) for v in loc), {"kind": kind, "group": group}))


RIF = ("rifleman_a", "rifleman_b", "rifleman_c")


def zg(y):
    return 0.0 if (y > -14.2 or y < -27.4) else -0.15


for j, (x, y) in enumerate(((-18.0, -29.4), (-10.0, -28.8), (-2.0, -29.6), (8.0, -29.0), (15.0, -29.5),
                            (22.0, -28.9), (-12.0, -24.8), (12.0, -24.6)), start=1):
    E(f"m3_w1_{j:02d}", (x, y, zg(y)), RIF[j % 3], "m3_w1", "advance", face=(x * 0.5, 14.0))
for j, (x, y) in enumerate(((-3.0, -18.0), (3.5, -18.4)), start=1):
    E(f"m3_w1_riot_{j:02d}", (x, y, zg(y)), "riot", "m3_w1", "advance", face=(0.0, 14.0))
for j, (x, y, kind) in enumerate(((44.0, 8.0, "rifleman_a"), (46.0, 14.0, "rifleman_b"), (44.5, 20.0, "assault"),
                                  (-45.0, 6.0, "rifleman_c"), (-43.0, 0.5, "rifleman_a"), (-46.0, -4.5, "assault"),
                                  (46.5, 26.0, "rifleman_c"), (-41.0, 10.0, "rifleman_b")), start=1):
    E(f"m3_w2_{j:02d}", (x, y, 0.0), kind, "m3_w2", "flank" if kind != "assault" else "rush", face=(0.0, 12.0))
for j, (x, y, z) in enumerate(((-14.0, -20.0, 13.0), (0.0, -26.0, 14.0), (14.0, -20.0, 12.5), (20.0, 2.0, 13.5)),
                              start=1):
    E(f"m3_drone_{j:02d}", (x, y, z), "drone", "m3_drone", "patrol", face=(0.0, 14.0), path="m3_drone")
for j, p in enumerate(((-20.0, -18.0, 13.0), (20.0, -18.0, 13.5), (18.0, 6.0, 12.5), (-18.0, 6.0, 12.5)), start=1):
    M(f"WP_m3_drone_{j:02d}", p)
for vid, pts in (("m3_apc1", ((-90.0, -24.6), (-50.0, -24.6), (-14.0, -23.6))),
                 ("m3_apc2", ((62.0, -17.0), (40.0, -17.0), (12.0, -17.6)))):
    M(f"VEH_{vid}", (pts[0][0], pts[0][1], -0.15), face=pts[1],
      props={"vehicle": "r41_apc", "faction": "enemy", "state": "ready", "driver": "ai", "path": vid,
             "group": "m3_apc", "spawn": "manual"})
    for j, p in enumerate(pts, start=1):
        M(f"WP_{vid}_{j:02d}", (p[0], p[1], -0.15))
FINAL = [((-20.0, -26.0), "rifleman_a", "advance"), ((-8.0, -27.0), "assault", "rush"), ((0.0, -29.5), "officer", "hold"),
         ((8.0, -27.5), "riot", "advance"), ((18.0, -26.0), "rifleman_b", "advance"), ((26.0, -29.0), "rifleman_c", "hold"),
         ((45.0, 4.0), "assault", "rush"), ((46.0, 11.0), "riot", "advance"), ((44.0, 18.0), "rifleman_a", "flank"),
         ((-44.0, 3.0), "assault", "rush"), ((-46.0, 9.0), "riot", "advance"), ((-42.0, -3.0), "rifleman_b", "flank")]
for j, ((x, y), kind, beh) in enumerate(FINAL, start=1):
    E(f"m3_final_{j:02d}", (x, y, zg(y)), kind, "m3_final", beh, face=(0.0, 14.0))

# ================================================================== 보고 + 내보내기
for nm, p, pr in NODES:
    extra = " ".join(f"{k}={v}" for k, v in pr.items() if k in ("kind", "group", "weapon", "height", "who", "pose"))
    print(f"[m3] {nm:28s} {p} {extra}")
ROOT = {
    "sky": "#a9879c",            # 해 질 녘: 보랏빛 하늘에 연기 (해 쪽은 주황)
    "fog": "70,420",
    "sun": "-0.86,0.22,0.3",     # 서남서 낮은 해 (17:55), 긴 그림자
    "sunColor": "#ff8a4a",
    "sunIntensity": 1.9,
    "ambient": 0.85,
    "hemiSky": "#9c86b4",
    "hemiGround": "#4a3842",
    "near": 0.1,
    "far": 800,
    "music": "m3_combat",
    "timeOfDay": "dusk_1755",
}
C.finish("levels/m3_cityhall.glb", root_props=ROOT, outline=0.025)
