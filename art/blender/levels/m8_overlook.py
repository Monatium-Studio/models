"""3막 M8 「관측수」: 알프토반(모나티엄-에르피엔 고속도로) 고가 위 전방 관측 지점.

npm run model -- art/blender/levels/m8_overlook.py   → public/models/levels/m8_overlook.glb
npm run shot -- levels/m8_overlook.glb --views top,34 --focus zone_tower

[원작] 흑뉴아가 반물질 중성자탄을 쏘고, 로네의 보고로 발사가 확인되며, 엘레나가 복구한 통신망으로 연락받은 시온이
       초장거리 저격으로 탄의 출발점과 도착점을 웜홀처럼 이어 아공간으로 보낸다. 시온은 정령산에 있다.
       모나티엄-에르피엔 고속도로(엘레나가 1막에서 흑뉴아를 끌어들이려 한 길), 알프토반(아우토반 패러디), 미국 단위계(mi).
[오리지널] 리타가 고가 위 관제·정비탑(관측 지점)까지 침투해 시온의 관측수가 된다. 고가가 끊긴 자리, 관제탑, 정비 마당,
       에르피엔 바깥 망루(레이저 기준점), 다리 위 강풍 바람자루, R41 발사장의 위치와 모양, 에르피엔의 원경 디자인.
시간: 새벽 전 푸른 시각(blue hour). 머리 위는 짙은 파랑, 동쪽(에르피엔) 지평선만 따뜻하게 밝다. 하늘 돔(SKY_dawn)은
       카메라를 따라다닌다(루트 skyNode). 가로등은 대부분 꺼졌고 두 개만 켜져 있다. 평야의 불과 연기가 주황 포인트.

좌표 (Blender m, +X 동, +Y 북, -Y가 마커 정면, 마커는 바닥면 위)
  고가 상판 윗면 z = 9.0. 동행(본선, 플레이) 중심 y = 0 (y -6.6..6.6), 서행(쌍둥이 고가, 배경) 중심 y = 15.6.
  x -80..-12   남쪽 진입로(램프, y -11.6..-6.6): 지면에서 상판 높이로 오른다. x = -26.5에 진압반 바리케이드 + 충돌 벽
  x -12..30    합류부 (램프 차로가 본선 남쪽에 붙는다, 대각 방호벽)          SPAWN_player (-2, -9.0)
  x 18..48     버려진 차 1무리
  x 72         표지 문형 1 "알프토반 1 / 에르피엔 12 mi"  + R41 검문 (모래주머니, R41 레이더 PROP)  ENEMY_d1_*
  x 100..104   TRIG_deck_mid, SPAWN_deck
  x 110..175   버스, R41 장갑차 PROP, 불탄 차 사이                                       ENEMY_d2_*
  x 182        표지 문형 2 (판 하나가 떨어져 매달림)
  x 190..240   차 몇 대 (웨이브 2가 서쪽 상판에서 온다)
  x 245.5..248.5  남쪽 방호벽 틈 → 강재 통로(y -11..-6.6) → 관제탑 기단 층(z 9, x 239.5..253, y -17..-11)  SPAWN_op
  x 239.7..241.3  관측 계단 (기단 층 → 중간 층참 z 12.5 → 꼭대기 층참 z 16, 서쪽 바깥)
  x 242.5..253, y -32.6..-21  관측 갑판 z 16 (상판보다 7 m 위, 동쪽 열린 난간)  MARK_gear (252.0, -26.0)  SPAWN_op_top
  x 253.2..256.8, y -17..-11  정비 마당 → 기단 층 꺾은 계단 (5구간, 웨이브 1·3의 길)
  x 232..270, y -44..-8.5   정비 마당 (자갈, z 0.05, 울타리·충돌 벽)
  x ≈ 262      본선 파단 (동쪽은 무너진 경간). 상판 끝 충돌 벽 x 259.5. 동쪽 토막은 x 283.5부터 다시 이어진다
  x 410        동쪽 토막 남쪽 방호벽 위 바람자루 (MARK_lase_wind, 관측 갑판에서 약 160 m)
원경
  에르피엔 바깥 망루 (1100, 70) 언덕 위        MARK_lase_ref1 (첨탑 끝, 약 850 m)
  가상 낙하점 (1950, -60) 평야               MARK_impact (약 1.7 km)
  R41 발사장 (2600, 2200) 북동                MARK_launch (발사 레일 끝, 약 3.2 km)
  에르피엔 (3400, 120) 언덕 위 왕도. 한가운데 세계수(높이 680 m), 밑동을 두른 왕궁, 시가 고리, 이중 성벽(바깥 약 490 m)
                                              MARK_erpien (세계수 줄기, 왕궁 위, 약 3.15 km)
  정령산 남쪽 (y -1500 이남 산줄기), 감시 초소 (900, -1980) 능선   MARK_sion (망루 바닥, 해발 약 250 m, 약 2.06 km)
  모나티엄 서쪽 (x < -420), 고가가 도시로 들어간다

마커 계약 (미션 m8.ts와 맞춘 이름)
  SPAWN_player · SPAWN_deck · SPAWN_op · SPAWN_op_top
  ALLY_rona · ALLY_sabre · ALLY_jesty · ALLY_karen        (who, behavior=follow, weapon=m4a1)
  ENEMY_d1_01..05 deck1 · ENEMY_d2_01..06 deck2 (d2_03 riot rush) · ENEMY_t_01..04 tower
  ENEMY_w1_01..05 op_wave1 manual · ENEMY_w2_01..06 op_wave2 manual (w2_04 riot rush) · ENEMY_w3_01..04 op_wave3 manual
     공통 속성 kind, group, behavior, spawn=start|manual, weapon=r41_carbine, drop=r41_carbine
     (riot에는 weapon·drop이 없다: 전투 시스템 기본값 r41_suppressor + 방패)
  COVER_d01..d16 (상판, -Y = 동쪽 적) · COVER_op01..op06 (관제탑, -Y = 올라오는 쪽)
  TRIG_deck_mid · TRIG_op · TRIG_op_top
  MARK_op · MARK_gear · GEAR_tripod(hidden=1, 자식 GEAR_tripod_head = 패닝 축) · MARK_lase_ref1 · MARK_lase_wind
  MARK_launch · MARK_impact · WP_bomb_01..08 (발사장 → 최고 약 900 m → 낙하점) · MARK_sion · MARK_erpien
  CAM_handoff_01..03 + LOOK_handoff_01..03 (끝 원경: 평야와 에르피엔)
  덤: WP_route_plain_01.. (마당 → 꺾은 계단 → 기단 층), WP_route_op_01.. (기단 층 → 관측 갑판),
      WP_route_deck_01.. (서쪽 상판 → 통로 → 기단 층). 대체 전투(act3kit)의 직선 이동은 계단을 못 오르니 escort/walk에 쓴다.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bmesh  # noqa: E402
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import overlook_kit as ok  # noqa: E402
import erpien_kit as ek  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()
# 원경 세계수·에르피엔 나무는 4~5 km 밖이라 공기 원근을 색에 미리 넣는다 (안개는 하늘 돔 때문에 옅게 쓴다)
mk.PAL.update({"canopy": "#7b9c94", "canopy_l": "#8fae9f", "bark": "#857b83"})
ek.haze("#9aa7bd", 0.36)        # 세계수·에르피엔 (3 km 넘게 떨어진 새벽 원경)
ERP_C = (3400.0, 120.0)         # 에르피엔 = 세계수 (왕국 한가운데)
ERP_H = 680.0                   # 세계수 높이 (바깥 성벽 반지름 약 490 m)
C = mk.City("m8_overlook")
Z = ok.DECK_Z
HALF = ok.HALF
YT = 15.6                       # 쌍둥이(서행) 고가 중심
YZ = 0.05                       # 정비 마당 바닥
OP = Vector((250.0, -26.0, 16.0))   # 관측 갑판 (원경 거리 기준)
COL = ok.ColAcc()               # 경사·회전 충돌 (계단, 램프, 난간 막대)


class no_climb:
    """with 블록 안에서 만든 COL(축 정렬·돌린 상자·볼록)에 climb=0: 넘기·오르기로 올라서지 않는다 (상자 더미·버려진 차량을
    디딤판 삼아 흉벽·방호벽 너머로 뛰어 길을 벗어나지 않게, scripts/wedgecheck.mjs drop). 맨 점프로 못 오르는 높이만:
    점프 발끝 최고 0.6 m(달리며 뛰어 0.63)라 0.56 m 상자는 맨 점프로 올라섰다. 디딤판이 될 맨 아래 단은 0.7 m 넘게"""

    def __enter__(self):
        self.n = (len(C.cols), len(C.ocols), len(C.ccols))

    def __exit__(self, *exc):
        for lst, k in zip((C.cols, C.ocols, C.ccols), self.n):
            for e in lst[k:]:
                C.col_props[e[0]] = {"climb": 0}


def hp(x0):
    """차선 점선 위상 (12 m 주기를 전역으로 맞춘다)."""
    return (-x0) % 12.0


# ================================================================== 원경 높이 (평야 + 언덕 + 정령산)
PEAKS = [(-2600, -3500, 470, 800), (-1700, -2600, 420, 650), (-700, -2950, 560, 720), (300, -3500, 520, 650),
         (900, -2050, 250, 320),          # 감시 초소 능선 (앞으로 튀어나온 산등성이)
         (1500, -3950, 380, 650),         # 초소 뒤는 낮은 안장: 초소가 하늘을 배경으로 보이게
         (2500, -2850, 600, 780), (3500, -3150, 520, 720), (4600, -2700, 470, 700), (5600, -3300, 540, 800)]


def mountains(x, y):
    s = 0.0
    for (px, py, H, R) in PEAKS:
        dd = ((x - px) ** 2 + (y - py) ** 2) / (R * R)
        if dd < 9:
            s += H * math.exp(-dd)
    s += 90 * ok.smooth(-1800, -3200, y)
    return s * ok.smooth(-1150, -1750, y)


def h(x, y):
    d = math.hypot(x - 250.0, y * 1.3)
    base = ok.smooth(450, 1600, d) * (5.0 + 4.0 * math.sin(x / 530 + 1.1) * math.cos(y / 610 - 0.4)
                                      + 2.5 * math.sin(x / 233 + y / 311))
    base += 26 * math.exp(-((x - 3400) ** 2 + (y - 120) ** 2) / 640 ** 2)     # 에르피엔 언덕
    base += 15 * math.exp(-((x - 1100) ** 2 + (y - 70) ** 2) / 170 ** 2)      # 망루 언덕
    return base + mountains(x, y)


def hz(x, y):
    """지면 높이 (놀이 구역 근처는 정확히 0)."""
    return h(x, y)


# ================================================================== 1. 고가 상판 (플레이)
C.group("deck")
# --- 남쪽 진입로 (램프): 지면 x=-80 → 상판 높이 x=-12
RX0, RX1 = -80.0, -12.0
RY0, RY1 = -11.6, -HALF


def zr(x):
    return Z * ok.smooth(RX0, RX1, x)


NS = 17
rxs = [RX0 + (RX1 - RX0) * i / NS for i in range(NS + 1)]
for xa, xb in zip(rxs, rxs[1:]):
    za, zb = zr(xa), zr(xb)
    b = C.bm("asphalt")
    b.faces.new([b.verts.new(p) for p in ((xa, RY0, za), (xb, RY0, zb), (xb, RY1, zb), (xa, RY1, za))])
    # 옆 가림벽: 윗변은 방호벽 밑면(노면 -5 cm)까지. 북쪽(RY1)은 본선 판 옆면과 한 평면이 되지 않게 1 cm 안쪽
    for yy in (RY0, RY1 - 0.01):
        bw = C.bm("girder")
        bw.faces.new([bw.verts.new(p) for p in ((xa, yy, -0.5), (xb, yy, -0.5), (xb, yy, zb - 0.05),
                                                (xa, yy, za - 0.05))])
    COL.slab([(xa, RY0, za), (xb, RY0, zb), (xb, RY1, zb), (xa, RY1, za)], t=0.4)
    for yy, inward in ((RY0, 1), (RY1, -1)):
        ok.barrier_col(C, (xa, yy, za), (xb, yy, zb), (0, inward))    # 경사를 따라 기운 상자
    for yl in (RY0 + 1.2, RY1 - 0.9):
        C.strip("line", (xa, yl, za), (xb, yl, zb), 0.15, lift=0.02)
bw = C.bm("girder")
bw.faces.new([bw.verts.new(p) for p in ((RX1, RY0, -0.5), (RX1, RY1, -0.5), (RX1, RY1, Z - 0.9), (RX1, RY0, Z - 0.9))])
ok.sweep(C, "barrier", [(x, RY0, zr(x)) for x in rxs], (0, 1))
ok.sweep(C, "barrier", [(x, RY1, zr(x)) for x in rxs], (0, -1))

# --- 본선 서쪽 (바리케이드 뒤는 배경) + 합류부
ok.deck(C, -130.0, RX1, 0.0, phase=hp(-130.0))
A_, B_, C_ = (RX1, RY0), (30.0, -HALF), (RX1, -HALF)
C.prism("deck_c", [A_, B_, C_], Z - 0.9, Z - 0.05, top=True, bottom=True)
ok.sweep(C, "barrier", [(A_[0], A_[1], Z), (B_[0], B_[1], Z)], (-(B_[1] - A_[1]), B_[0] - A_[0]))
COL.prism([A_, B_, C_], Z - 0.9, Z)
_d = Vector((B_[0] - A_[0], B_[1] - A_[1], 0)).normalized()
_n = Vector((-_d.y, _d.x, 0)) * (ok.BAR_W / 2)
COL.obox((A_[0] + _n.x, A_[1] + _n.y), (B_[0] + _n.x, B_[1] + _n.y), ok.BAR_W, Z - 0.25, Z + ok.BAR_H)
C.strip("line", (A_[0] + 2, A_[1] + 1.2, Z), (B_[0] - 4, B_[1] + 0.9, Z), 0.15, lift=0.02)
C.cyl("girder", (6.0, -8.6, -0.5), (6.0, -8.6, Z - 0.9), 0.8, segs=12, cap=False)

# --- 본선 동쪽: 합류부 끝 ~ 파단 (남쪽 방호벽 틈 = 관제탑 통로)
X_BRK = 262.0
ok.deck(C, RX1, X_BRK - 3.5, 0.0, gaps_s=[(RX1, 30.0), (245.5, 248.5)], phase=hp(RX1), asphalt=False)
# 합류부 + 본선 동쪽 아스팔트는 한 장 (이음매 없음)
_ng = [A_, B_, (30.0, -HALF + 0.3), (X_BRK - 3.5, -HALF + 0.3), (X_BRK - 3.5, HALF - 0.3), (RX1, HALF - 0.3)]
C.poly("asphalt", [(x, y, Z) for x, y in _ng], normal=(0, 0, 1), kind="fine")
# 바닥·방호벽 토막·추락 막이 충돌은 들쭉날쭉한 파단면을 따른다 (예전: x 259.5의 곧은 벽이 파단면 1~3 m 앞을 막았다)
ok.broken_end(C, X_BRK, 0.0, Z, direction=1, seed=4, col=True)
# 파단 앞 임시 통제: 콘크리트 블록 + 통행 금지 표지
for (yy, rot) in ((-4.6, 4), (-1.0, -3), (2.8, 6), (5.4, 0)):
    C.rbox("barrier", (256.6, yy, Z + 0.4), (0.6, 2.2, 0.8), (0, 0, rot))
    C.ocol((256.6, yy, Z), (0.6, 2.2, 0.8), rot)
for yy in (-2.8, 1.0):
    C.col(256.13, 256.27, yy - 0.76, yy + 0.76, Z + 0.93, Z + 1.47)          # 표지 판 (밑은 웅크려 지나간다)
    for s in (-1, 1):
        C.col(256.17, 256.23, yy + s * 0.6 - 0.03, yy + s * 0.6 + 0.03, Z, Z + 0.95)
    c = Vector((256.2, yy, Z + 1.2))
    C.box("metal", 256.15, 256.25, yy - 0.7, yy + 0.7, Z, Z + 0.06, kind="detail")
    C.plate("hazard", hw.rrect(1.5, 0.5, 0.06, 2), tuple(c), (-1, 0, 0), 0.04, kind="detail")
    C.text("dark", "통행 금지 · ROAD CLOSED", 0.13, tuple(c + Vector((-0.05, 0, 0))), (-1, 0, 0))
    for s in (-1, 1):
        C.beam("metal", (256.2, yy + s * 0.6, Z), (256.2, yy + s * 0.6, Z + 1.0), 0.05, 0.05, kind="detail")

# --- 쌍둥이(서행) 고가: 배경 (같은 자리에서 끊김, 경간은 땅에 납작하게)
C.group("twin")
ok.deck(C, -130.0, 262.5, YT, lines="north", col=False, phase=hp(-130.0))
ok.broken_end(C, 266.0, YT, Z, direction=1, seed=9)
ok.broken_end(C, 281.0, YT, Z, direction=-1, seed=12)
ok.deck(C, 284.5, 450.0, YT, lines="north", col=False, phase=hp(284.5))
ok.fallen_slab(C, (268.0, 1.4), (279.0, 0.35), YT + 0.8, seed=5, roll=3.0)
ok.rubble(C, 268, YT - 2, 0.0, 6, 10, seed=21)
ok.rubble(C, 279, YT + 3, 0.0, 5, 8, seed=22)
ok.sign_gantry(C, 110.0, YT, Z, [("모나티엄 시청 6 mi", "MONATIUM CITY HALL"), ("엘레나대로", "ELENA AVE")],
               facing=1, col=False)
for x in (26.0, 62.0, 118.0, 154.0, 226.0):
    ok.light_pole(C, x, YT + HALF - 0.28, Z + ok.BAR_H, arms=(-1,), reach=3.0, lit=False)
for (x, y, yaw, kind, key) in ((40, 18.8, 186, "sedan", "car_gray"), (95, 13.2, 175, "van", "car_cream"),
                               (150, 17.6, 190, "hatch", "car_red"), (205, 12.6, 170, "sedan", "car_white"),
                               (243, 18.4, 200, "pickup", "car_blue")):
    ok.car(C, x, y, Z, yaw, kind=kind, key=key, col=False)

# --- 동쪽 토막 (무너진 경간 너머)
C.group("deck_east")
X_E = 283.5
ok.broken_end(C, X_E, 0.0, Z, direction=-1, seed=7)
ok.deck(C, X_E + 3.5, 450.0, 0.0, col=False, phase=hp(X_E + 3.5))
ok.fallen_slab(C, (263.2, 6.9), (281.0, 0.5), 0.3, seed=2, roll=-4.0)
ok.rubble(C, 281.5, -1.0, 0.0, 7, 14, seed=23)
ok.rubble(C, 264.0, 3.0, 0.0, 5, 9, seed=24)
ok.car(C, 272.0, -8.5, 0.0, 120, kind="sedan", key="car_blue", burnt=True, tilt=12, col=False)
ok.sign_gantry(C, 330.0, 0.0, Z, [("에르피엔 11 mi", "ERPIEN"), ("정령산 출구 1/2 mi", "SPIRIT MT · EXIT 14")], col=False)
WIND = ok.windsock(C, 410.0, -HALF + 0.28, Z + ok.BAR_H, h=4.6, toward=(0.85, 0.5))
for x in (296.0, 368.0, 440.0):
    ok.light_pole(C, x, HALF - 0.28, Z + ok.BAR_H, arms=(-1,), reach=3.0, lit=False)

# --- 교각
C.group("piers")
PIER_X = [-105.0 + 30 * k for k in range(13)] + [285.0 + 30 * k for k in range(6)]
for x in PIER_X:
    ok.pier(C, x, 0.0, ground=hz(x, 0))
    ok.pier(C, x, YT, ground=hz(x, YT))

# --- 표지 문형 · 가로등 (본선)
C.group("deck")
ok.sign_gantry(C, 72.0, 0.0, Z, [("알프토반 1", "ALFTOBAHN 1"), ("에르피엔 12 mi", "ERPIEN")])
ok.sign_gantry(C, 182.0, 0.0, Z, [("정령산 출구 1 mi", "SPIRIT MT · EXIT 14"), ("에르피엔 직진", "ERPIEN THRU")],
               damaged=0)
for x, lit in ((8.0, True), (44.0, False), (100.0, False), (136.0, True), (208.0, False), (236.0, False)):
    ok.light_pole(C, x, HALF - 0.28, Z + ok.BAR_H, arms=(-1,), reach=3.0, lit=lit)
for x in (-60.0, -96.0):
    ok.light_pole(C, x, HALF - 0.28, Z + ok.BAR_H, arms=(-1,), reach=3.0, lit=False)

# ================================================================== 2. 상판 위 차량·엄폐
C.group("vehicles")
VEH = [
    # 무리 A (합류부 너머)
    (22.0, 3.4, 8, "sedan", "car_red"), (34.0, -2.2, -12, "hatch", "car_blue"), (44.0, 1.0, 20, "van", "car_white"),
    # 무리 B (문형 1)
    (88.0, 4.3, -10, "sedan", "car_gray"),
    # 무리 C
    (113.0, -2.8, 4, "sedan", "car_cream"), (160.0, 4.2, 5, "pickup", "car_teal"), (170.0, -2.6, -8, "hatch",
                                                                                     "car_yellow"),
    # 무리 D
    (196.0, -3.2, 30, "sedan", "car_white"), (208.0, 3.8, -6, "van", "car_blue"), (226.0, -1.4, 15, "sedan", "car_red"),
    (234.0, 3.6, 4, "pickup", "car_gray"),
]
for (x, y, yaw, kind, key) in VEH:
    ok.car(C, x, y, Z, yaw, kind=kind, key=key)
ok.car(C, 135.0, -3.8, Z, -20, kind="sedan", key="car_white", burnt=True)
ok.smoke(C, 135.0, -3.8, Z + 0.6, h=16, r=0.9, drift=(0.3, 0.12), seed=3, dark=0.8, kind="main", segs=6, rings=4)
ok.truck(C, 78.0, -1.6, Z, 0, key="car_white", box_key="white", jack=28, text="모나티엄 25 물류")
ok.bus(C, 122.0, 2.5, Z, 12)
# R41 차량 (노드 PROP_: 렌더는 소품 glb, 충돌은 단순 상자)
RAIDER = (68.0, 3.6)
IFV = (148.0, -1.2)


def prop_cols(loc, face, boxes):
    """PROP_ 차량(collider=0)의 충돌: 소품 glb의 COL_ 조각(로컬 Blender x, y, z 상자)을 마커 방향대로 돌려 COL_로.
    한 덩어리 상자는 차체 모서리·바퀴 밖에 0.5~0.7 m 빈 벽이 남았다."""
    yaw = math.degrees(mk.yaw_to(loc, face))
    for b in boxes:
        C.lcol(loc[0], loc[1], loc[2], yaw, *b)


def prop_wheels(loc, face, x0, x1, ycs, zc, r, cap=None):
    """PROP_ 차량의 바깥 바퀴 (소품 COL_ 조각 밖으로 나온 것): 로컬 X축 원통의 볼록 껍질.
    cap: 맨 점프(발끝 0.63 m)로 올라서지 못하게, 바퀴 윗부분을 cap 높이까지만 원 그대로 두고 그 위는 꼭대기(폭 0.4 m)로 가파르게
    모은다 (팔각형 윗면 비탈 22.5°에 내려앉아 그 위로 올라섰다). 설 수 있는 비탈(46°)이 꼭대기 아래에 없다"""
    M = Matrix.Translation(loc) @ Matrix.Rotation(mk.yaw_to(loc, face), 4, "Z")
    for yc in ycs:
        if cap is None:
            yz = [(yc + r * math.cos(a), zc + r * math.sin(a)) for a in (2 * math.pi * k / 8 for k in range(8))]
        else:
            yz = [(yc + r * math.cos(a), zc + r * math.sin(a)) for a in (2 * math.pi * k / 16 for k in range(16))
                  if zc + r * math.sin(a) <= cap] + [(yc - 0.2, zc + r), (yc + 0.2, zc + r)]
        C.ccol([tuple(M @ Vector((x, y, z))) for x in (x0, x1) for (y, z) in yz])


C.prop("r41_raider_01", (RAIDER[0], RAIDER[1], Z), "vehicles/r41/r41_raider.glb", face=(RAIDER[0] - 10, RAIDER[1] - 2),
       props={"collider": 0, "state": "abandoned"})
with no_climb():      # 레이더: 롤케이지(1.52 m) 위에서 북쪽 방호벽 너머로 뛰어내렸고, 케이지와 동력부 사이 0.46 m 틈에 박혔다
    prop_cols((RAIDER[0], RAIDER[1], Z), (RAIDER[0] - 10, RAIDER[1] - 2),
              [(-0.62, 0.62, -1.66, 0.16, 0.36, 0.92),          # 앞 몸통 (밑은 바퀴뿐)
               (-0.62, 0.62, 0.56, 1.86, 0.36, 1.17),           # 뒤 동력부
               (-0.36, 0.36, 0.12, 0.62, 0.42, 0.91),           # 허리
               (-0.56, 0.56, -0.90, 0.10, 0.92, 1.52)])         # 롤케이지
    # 앞 범퍼 뿔(0.55 m)·뒤 등(0.65 m)은 맨 점프로 올라서는 디딤판이었다: 뿔 위에서 뛰어 북쪽 방호벽 위로 올라 고가 밖으로
    # 떨어지고, 앞 몸통 위로 올라 케이지와 동력부 사이 0.46 m 틈에 박혔다 (wedgecheck m8_decks). 상자 대신 몸통 윗면 모서리까지
    # 오르는 가파른 쐐기(67°·69°, 설 수 있는 경사 46°보다 가파르다): 위에 서지 못하고 미끄러져 내린다
    _rm = Matrix.Translation((RAIDER[0], RAIDER[1], Z)) @ Matrix.Rotation(mk.yaw_to(RAIDER, (RAIDER[0] - 10, RAIDER[1] - 2)), 4, "Z")
    for (hx, yz) in ((0.35, ((-1.92, 0.30), (-1.66, 0.30), (-1.66, 0.92))),     # 앞 범퍼 뿔 → 앞 몸통 윗면
                     (0.15, ((2.14, 0.45), (1.86, 0.45), (1.86, 1.17)))):       # 뒤 등 → 동력부 윗면
        C.ccol([tuple(_rm @ Vector((sx * hx, y, z))) for sx in (-1, 1) for (y, z) in yz])
    for s_ in (-1, 1):
        prop_wheels((RAIDER[0], RAIDER[1], Z), (RAIDER[0] - 10, RAIDER[1] - 2), *sorted((s_ * 0.6, s_ * 0.95)),
                    (-1.10, 0.98), 0.36, 0.36, cap=0.55)
C.prop("r41_ifv_01", (IFV[0], IFV[1], Z), "vehicles/r41/r41_ifv.glb", face=(IFV[0] - 10, IFV[1] + 1.5),
       props={"collider": 0, "state": "abandoned"})
prop_cols((IFV[0], IFV[1], Z), (IFV[0] - 10, IFV[1] + 1.5),
          [(-1.08, 1.08, -2.86, 0.98, 0.46, 1.58),          # 차체 (밑은 바퀴뿐)
           (-1.02, 1.02, 1.24, 2.80, 0.51, 1.57),           # 뒤 동력부
           (-0.66, 0.66, 0.95, 1.28, 0.62, 1.34),           # 허리
           (-0.70, 0.70, -1.14, 0.26, 1.58, 2.04),          # 포탑 (차체 윗면 1.58에 얹힌다: 4 cm 틈이 떠 보였다)
           (-0.3, 0.3, -3.02, -2.86, 0.55, 0.75),           # 앞 끝
           (-0.15, 0.15, 2.80, 3.08, 0.42, 0.62)])          # 뒤 등
for s_ in (-1, 1):
    prop_wheels((IFV[0], IFV[1], Z), (IFV[0] - 10, IFV[1] + 1.5), *sorted((s_ * 0.8, s_ * 1.17)),
                (-1.70, -0.45, 1.62), 0.43, 0.43)
# R41 검문 모래주머니 (문형 1 아래, 정면 서쪽)
for (x, y) in ((75.6, -4.4), (95.0, 1.6)):
    mk.sandbag_wall(C, x, y, yaw=-90, z=Z, n=4, rows=3)          # 충돌은 키트의 COL
# 진압반 바리케이드 (출발선 서쪽 끝: 아군 진지) + 충돌 벽. 판(두께 0.14) 뒷면을 충돌 벽 앞면(x -26.5)에 붙인다:
# 예전 x -26.0이면 판과 벽 사이가 0.43 m라 캡슐(0.48 m)이 진입로 방호벽 위에서 그 틈으로 내려서다 판 모서리와 벽 사이에
# 발이 뜬 채 박혔다 (scripts/wedgecheck.mjs m8_decks). 진입로 남쪽 끝 바리케이드는 북쪽 끝(-7.8: 북쪽 방호벽 밑동에 0.16 m
# 들어감)처럼 남쪽 방호벽 밑동(y -11.04)에 0.16 m 들인다: 예전 y -10.0이면 판 끝과 방호벽 사이 0.24 m 틈에 같은 식으로 박혔다
XB = -26.5 + 0.07
for yy in (-10.4, -7.8, -3.6, 0.0, 3.6):
    zz = zr(XB) if yy < -HALF else Z
    mk.barricade(C, XB, yy, yaw=-90, z=zz)
C.col(-26.9, -26.5, RY0, HALF, 6.5, Z + 4.0, name="COL_west_wall")
# 진입로 남쪽 방호벽 위 안전 철망 (출발선 서쪽 벽부터 합류부까지, 방호벽 윗면 가운데 위로 2.0 m): 정찰 오토바이(사이드카 꼬리
# 0.45 m → 사이드카 0.69 → 안장 0.96 m, 자동 오르기로 이어 오른다) 위에서 뛰면 방호벽(0.8 m)을 넘어 고가 밖 땅으로 떨어졌다
# (scripts/wedgecheck.mjs m8_decks drop). 북쪽 방호벽 너머는 본선 상판이라 그대로 둔다
_gx = [-26.9] + [x for x in rxs if -26.9 < x < RX1] + [RX1]
for xa, xb in zip(_gx, _gx[1:]):
    ok.guard_run(C, COL, (xa, RY0 + 0.12, zr(xa)), (xb, RY0 + 0.12, zr(xb)), base=ok.BAR_H, col_from=ok.BAR_H,
                 mesh_from=ok.BAR_H, posts=2.0)
C.prop("monatium_scout_01", (-17.0, -9.1, zr(-17.0)), "vehicles/monatium/monatium_scout.glb", face=(0, -9.1),
       props={"collider": 0})
with no_climb():      # 정찰 오토바이: 넘기·오르기로는 못 오르게 (사이드카 꼬리 0.45 m는 맨 점프로 오른다: 아래 진입로 철망)
    # 예전 상자는 90° 돌아가 있어(x 1.5 × y 2.1) 앞뒤 바퀴가 밖으로 나왔다. 오토바이 + 연결대 + 사이드카 껍질
    prop_cols((-17.0, -9.1, zr(-17.0)), (0, -9.1), [(0.20, 0.60, -0.80, 0.70, 0.22, 0.96), (-0.07, 0.22, -0.40, 0.45, 0.20, 0.36),
                                                    (0.60, 0.72, -0.20, -0.04, 0.12, 0.30),     # 발판·배기
                                                    (0.60, 0.75, -0.46, -0.34, 0.84, 0.96),     # 핸들 끝
                                                    (-0.62, -0.02, 0.55, 0.73, 0.15, 0.45)])    # 사이드카 꼬리
    prop_wheels((-17.0, -9.1, zr(-17.0)), (0, -9.1), -0.76, -0.56, (0.24,), 0.26, 0.27)        # 사이드카 바퀴 + 흙받이
    prop_wheels((-17.0, -9.1, zr(-17.0)), (0, -9.1), 0.30, 0.51, (-0.74, 0.62), 0.27, 0.28)    # 오토바이 앞뒤 바퀴
    _sc = Matrix.Translation((-17.0, -9.1, zr(-17.0))) @ Matrix.Rotation(mk.yaw_to((-17.0, -9.1), (0, -9.1)), 4, "Z")
    C.ccol([tuple(_sc @ Vector((-0.32 + sx * 0.30, y, z))) for sx in (1, -1)
            for (y, z) in ((-0.72, 0.45), (-0.52, 0.26), (0.42, 0.24), (0.62, 0.34), (0.61, 0.60), (0.42, 0.69),
                           (-0.22, 0.69), (-0.56, 0.60))])                  # 사이드카 (소품 COL_tub과 같은 껍질)

# ================================================================== 3. 정비 마당 + 관제탑 (관측 지점)
C.group("yard")
YX0, YX1, YY0, YY1 = 232.0, 270.0, -44.0, -8.5
C.box("gravel", YX0, YX1, YY0, YY1, -0.35, YZ)   # 밑면을 관제탑·기둥 밑면(-0.3)과 다른 높이에
C.col(YX0, YX1, YY0, YY1, -0.3, YZ)
# 울타리 (기둥 + 위·아래 가로대 + 반투명 철망) + 충돌 벽
mk.ALPHA["fence_a"] = ("#9a96a2", 0.32)
FENCE = [((YX0, YY1), (YX1, YY1)), ((YX1, YY1), (YX1, YY0)), ((YX1, YY0), (256.0, YY0)), ((248.0, YY0), (YX0, YY0)),
         ((YX0, YY0), (YX0, YY1))]
for (a, b_) in FENCE:
    A, B = Vector((a[0], a[1], YZ)), Vector((b_[0], b_[1], YZ))
    L = (B - A).length
    n = max(1, int(L / 3.0))
    for k in range(n + 1):
        p = A.lerp(B, k / n)
        C.box("metal", p.x - 0.05, p.x + 0.05, p.y - 0.05, p.y + 0.05, YZ, YZ + 2.5, kind="detail")
    for zz in (0.15, 2.4):
        C.beam("metal", tuple(A + Vector((0, 0, zz))), tuple(B + Vector((0, 0, zz))), 0.05, 0.05, kind="detail")
    dd = (B - A).normalized()
    nn = Vector((-dd.y, dd.x, 0))
    C.poly("fence_a", [tuple(A + Vector((0, 0, 0.15))), tuple(B + Vector((0, 0, 0.15))),
                       tuple(B + Vector((0, 0, 2.4))), tuple(A + Vector((0, 0, 2.4)))], normal=tuple(nn), kind="fine")
    x0_, x1_ = sorted((A.x, B.x))
    y0_, y1_ = sorted((A.y, B.y))
    C.col(x0_ - 0.05, x1_ + 0.05, y0_ - 0.05, y1_ + 0.05, YZ, YZ + 3.2)
# 남쪽 문 (닫힘)
C.box("hazard", 248.0, 256.0, YY0 - 0.06, YY0 + 0.06, YZ + 1.0, YZ + 1.15, kind="detail")
C.box("metal", 248.0, 256.0, YY0 - 0.05, YY0 + 0.05, YZ + 2.3, YZ + 2.4, kind="detail")
C.poly("fence_a", [(248.0, YY0, YZ + 0.1), (256.0, YY0, YZ + 0.1), (256.0, YY0, YZ + 2.3), (248.0, YY0, YZ + 2.3)],
       normal=(0, -1, 0), kind="fine")
C.col(248.0, 256.0, YY0 - 0.06, YY0 + 0.06, YZ, YZ + 3.2)
# 정비소 (롤 문 + 간판)
C.box("concrete", 259.0, 268.5, -41.5, -34.5, YZ, YZ + 4.2, col=True)
C.box("roof", 258.7, 268.8, -41.8, -34.2, YZ + 4.2, YZ + 4.45)
C.rect("navy", (263.0, -34.49, YZ + 1.4), (0, 1, 0), 4.2, 2.8, lift=0.01)
for k in range(7):
    C.strip("metal", (261.0, -34.47, YZ + 0.3 + k * 0.4), (265.0, -34.47, YZ + 0.3 + k * 0.4), 0.04, (0, 1, 0),
            lift=0.01)
C.text("white", "알프토반 정비소", 0.42, (263.0, -34.48, YZ + 3.45), (0, 1, 0))
C.text("glow", "ALFTOBAHN MAINT. 7", 0.22, (263.0, -34.48, YZ + 3.0), (0, 1, 0))
ok.truck(C, 236.5, -37.0, YZ, 90, key="hazard", box_key="white", text="알프토반 정비")
for (x, y) in ((262.5, -27.0), (264.2, -27.4), (263.3, -29.2)):
    C.cyl("wood", (x, y - 0.3, YZ + 0.7), (x, y + 0.3, YZ + 0.7), 0.7, segs=10)
    C.cyl("wood_d", (x, y - 0.31, YZ + 0.7), (x, y + 0.31, YZ + 0.7), 0.28, segs=8, kind="detail")
    # 누운 케이블 드럼 (원통): 보이는 원통(create_cone)처럼 꼭짓점 하나가 바닥에 닿게 (예전 각은 바닥이 변이라 3.4 cm 떴다)
    C.ccol([(x + 0.7 * math.cos(a), yy, YZ + 0.7 + 0.7 * math.sin(a)) for yy in (y - 0.31, y + 0.31)
            for a in (math.pi / 2 + 2 * math.pi * k / 10 for k in range(10))])
for k in range(8):
    x, y = 258.0 + (k % 4) * 0.7, -32.0 - (k // 4) * 0.7
    C.cyl("sock_o", (x, y, YZ), (x, y, YZ + 0.5), 0.17, r2=0.03, segs=6, kind="detail")
    C.cyl("white", (x, y, YZ + 0.22), (x, y, YZ + 0.3), 0.105, r2=0.09, segs=6, kind="fine", cap=False)
    C.ccol([(x + r * math.cos(a), y + r * math.sin(a), zz) for (r, zz) in ((0.17, YZ), (0.03, YZ + 0.5))
            for a in (2 * math.pi * k / 6 for k in range(6))])      # 고깔 (0.5 m: 자동 오르기보다 높다)
for (x, y) in ((234.5, -12.5), (235.3, -13.4), (266.5, -12.0)):
    mk.crate(C, x, y, s=0.75, z=YZ, key="olive")                 # 충돌은 키트의 COL
C.box("violet", 263.5, 265.5, -16.5, -15.2, YZ, YZ + 1.3, col=True)          # 발전기
C.box("teal", 263.48, 265.52, -16.52, -15.18, YZ + 0.9, YZ + 1.0, kind="detail")

C.group("tower")
# --- 관제탑 몸통 (관제실 창 띠, 갑판을 받친다)
SX0, SX1, SY0, SY1 = 245.0, 251.0, -30.0, -23.6
C.box("tower_c", SX0, SX1, SY0, SY1, -0.3, 15.6, col=True)
C.box("tower_band", SX0 - 0.03, SX1 + 0.03, SY0 - 0.03, SY1 + 0.03, 14.95, 15.6, kind="detail")
C.box("tower_band", SX0 - 0.03, SX1 + 0.03, SY0 - 0.03, SY1 + 0.03, 8.4, 8.7, kind="detail")
for (c, nrm, w) in (((248.0, SY1, 13.6), (0, 1, 0), 5.0), ((248.0, SY0, 13.6), (0, -1, 0), 5.0),
                    ((SX1, -26.8, 13.6), (1, 0, 0), 5.4), ((SX0, -26.8, 13.6), (-1, 0, 0), 5.4)):
    C.rect("glass_d", c, nrm, w, 2.2, lift=0.02)
    for k in range(5):
        R = Vector(nrm).cross(Vector((0, 0, 1)))
        p = Vector(c) + R * (-w / 2 + w * (k + 0.5) / 5)
        C.rect("tower_c", tuple(p), nrm, 0.12, 2.2, lift=0.03)
C.rect("dark", (248.0, SY1, YZ + 1.0), (0, 1, 0), 1.1, 2.0, lift=0.02)
C.text("white", "알프토반 관제탑 7", 0.62, (248.0, SY1, 11.0), (0, 1, 0))
C.text("glow", "ALFTOBAHN CONTROL 7", 0.3, (248.0, SY1, 10.25), (0, 1, 0))
C.logo((SX1, -26.8, 11.0), 1.2, (1, 0, 0), disc="navy", key="gold")
# --- 관측 갑판 (z 16)
OX0, OX1, OY0, OY1 = 242.5, 253.0, -32.6, -21.0
OZ = 16.0
C.box("deck_c", OX0, OX1, OY0, OY1, OZ - 0.4, OZ, col=True)
for (p0, p1) in (((OX0, OY0 + 0.15), (OX1, OY0 + 0.15)), ((OX1 - 0.15, OY0), (OX1 - 0.15, OY1)),
                 ((OX0 + 0.15, OY0), (OX0 + 0.15, OY1))):
    C.strip("hazard", (p0[0], p0[1], OZ), (p1[0], p1[1], OZ), 0.15, lift=0.012)
for (x, y) in ((OX0 + 0.5, OY0 + 0.5), (OX1 - 0.5, OY0 + 0.5), (OX0 + 0.5, OY1 - 0.5), (OX1 - 0.5, OY1 - 0.5)):
    C.box("metal", x - 0.18, x + 0.18, y - 0.18, y + 0.18, -0.3, OZ - 0.4)
    C.col(x - 0.18, x + 0.18, y - 0.18, y + 0.18, YZ, OZ - 0.4)
for (a, b_) in (((OX0 + 0.5, OY0 + 0.5), (SX0, SY0)), ((OX1 - 0.5, OY0 + 0.5), (SX1, SY0)),
                ((OX0 + 0.5, OY1 - 0.5), (SX0, SY1)), ((OX1 - 0.5, OY1 - 0.5), (SX1, SY1))):
    for z0, z1 in ((1.0, 7.0), (8.0, 14.6)):
        C.beam("metal", (a[0], a[1], z0), (b_[0], b_[1], z1), 0.14, 0.14, kind="detail")
# 북쪽 콘크리트 흉벽 (상판·기단 쪽 엄폐, 0.75 m: 웅크리면 숨고 서면 너머로 쏜다)
C.box("tower_c", OX0, OX1, OY1 - 0.3, OY1, OZ, OZ + 0.75, col=True)
C.box("tower_band", OX0 - 0.02, OX1 + 0.02, OY1 - 0.32, OY1 + 0.02, OZ + 0.62, OZ + 0.76, kind="detail")  # 윗면 1 cm 위
# 동·남·서 강재 난간 (동쪽은 평야를 향해 열려 있다)
ok.rail_run(C, (OX1 - 0.05, OY0 + 0.05, OZ), (OX1 - 0.05, OY1 - 0.3, OZ), col=COL)
ok.rail_run(C, (OX0, OY0 + 0.05, OZ), (OX1 - 0.05, OY0 + 0.05, OZ), col=COL)
ok.rail_run(C, (OX0 + 0.05, -30.6, OZ), (OX0 + 0.05, OY1 - 0.3, OZ), col=COL)
# 장비 창고 (남동 모서리: 북서쪽 상판 시야를 가리지 않게) + 안테나 + 항공 장애등
C.box("tower_c", 250.3, OX1 - 0.1, OY0 + 0.1, -30.3, OZ, OZ + 2.3, col=True)
C.box("roof", 250.15, OX1 + 0.05, OY0 - 0.05, -30.15, OZ + 2.3, OZ + 2.5)
C.rect("dark", (251.2, -30.3, OZ + 0.95), (0, 1, 0), 0.95, 1.85, lift=0.02)
C.rect("glass_d", (250.3, -31.4, OZ + 1.5), (-1, 0, 0), 1.0, 0.6, lift=0.02)
C.text("white", "관측 지점 · OP 7", 0.16, (251.6, -30.29, OZ + 2.05), (0, 1, 0))
C.cyl("metal", (252.3, -32.0, OZ + 2.5), (252.3, -32.0, OZ + 8.5), 0.08, segs=6, kind="detail")
for zz in (OZ + 4.0, OZ + 6.0, OZ + 7.6):
    C.beam("metal", (251.8, -32.0, zz), (252.8, -32.0, zz), 0.04, 0.04, kind="detail")
C.blob("beacon_r", (252.3, -32.0, OZ + 8.65), 0.14, segs=6, rings=4, kind="fine")
mk.cctv_pole(C, OX1 - 0.45, OY1 - 0.7, yaw=0, h=3.0, z=OZ)
# 엄폐: 서쪽 모래주머니(계단 쪽), 북서 상자 더미
with no_climb():      # 서쪽 난간 0.7 m 앞: 위에 올라서면 난간 너머로 뛰었다
    mk.sandbag_wall(C, 243.5, -27.0, yaw=-90, z=OZ, n=4, rows=3)     # 충돌은 키트의 COL (모래주머니·상자)
# 상자 더미는 흉벽(y -21.3)과 서쪽 난간(x 242.6)에서 0.7 m 떨어뜨린다 (예전: 흉벽 0.35·0.4 m, 난간 0.35 m).
# 캡슐(지름 0.44 + 둘레 틈 0.04)보다 좁은 틈은 상자 위(0.56 m)에서 흉벽(0.75 m) 쪽으로 가면 아래 반구가 상자 모서리와 흉벽
# 모서리 사이에 걸려 발이 뜬 채 박혔다 (접지가 아니라 점프도 안 되고, 미는 쪽마다 모서리를 타고 올라 수평 이동이 버려졌다.
# 2026-11-04 사용자: 「관제탑 위에 박스와 벽 사이에 끼는 문제는 왜 해결 안했는데?」, scripts/wedgecheck.mjs).
# 0.7 m면 상자에서 내려선 몸이 갑판 바닥까지 내려가 틈을 따라 걸어 나온다. 위 상자는 아래 두 상자 윗면(0.56 m)에 얹는다
# 상자 더미는 올라서지 못하게: climb=0 + 아래 상자 0.72 m (s 0.9). 예전 0.56 m 상자는 달리며 뛰면 맨 점프(발끝 0.63 m)로
# 올라서고, 거기서 한 번 더 뛰어 흉벽 너머 계단 밑으로 떨어졌다 (wedgecheck m8_tower drop)
with no_climb():
    mk.crate(C, 243.75, -22.45, s=0.9, z=OZ, key="olive")
    mk.crate(C, 244.75, -22.5, s=0.9, z=OZ, key="olive")
    mk.crate(C, 244.25, -22.45, s=0.55, z=OZ + 0.9 * 0.8, key="olive")

# --- 기단 층 (상판 높이 z 9) + 통로
BX0, BX1, BY0, BY1 = 239.5, 253.0, -17.0, -11.0
C.box("grate", BX0, BX1, BY0, BY1, Z - 0.08, Z, kind="detail")
C.box("tower_band", BX0, BX1, BY0, BY1, Z - 0.3, Z - 0.08, kind="detail")
C.col(BX0, BX1, BY0, BY1, Z - 0.3, Z)
for (x, y) in ((239.8, -16.7), (252.7, -16.7), (239.8, -11.3), (252.7, -11.3), (246.25, -16.7), (246.25, -11.3)):
    C.box("metal", x - 0.14, x + 0.14, y - 0.14, y + 0.14, -0.3, Z - 0.3)
    C.col(x - 0.14, x + 0.14, y - 0.14, y + 0.14, YZ, Z - 0.3)
for (a, b_) in (((239.8, -16.7), (246.25, -11.3)), ((246.25, -16.7), (252.7, -11.3)),
                ((239.8, -11.3), (246.25, -16.7)), ((246.25, -11.3), (252.7, -16.7))):
    C.beam("metal", (a[0], a[1], 1.0), (b_[0], b_[1], Z - 0.6), 0.1, 0.1, kind="detail")
ok.rail_run(C, (BX0, BY1, Z), (245.5, BY1, Z), col=COL)
ok.rail_run(C, (248.5, BY1, Z), (BX1, BY1, Z), col=COL)
ok.rail_run(C, (BX0, BY0, Z), (BX0, BY1, Z), col=COL)
ok.rail_run(C, (BX1, -15.4, Z), (BX1, BY1, Z), col=COL)
ok.rail_run(C, (241.3, BY0, Z), (BX1, BY0, Z), col=COL)
# 배전반·상자: 북쪽 난간 앞이라 올라서지 못하게 (위에서 뛰면 난간 너머 마당으로 떨어졌다)
with no_climb():
    C.box("navy", 251.0, 252.6, -12.2, -11.4, Z, Z + 1.45, col=True)               # 배전반
    # 상자는 0.72 m (s 0.9): 0.56 m면 맨 점프로 올라서 난간을 넘었다. 북쪽 난간에서 0.7 m (틈 규칙)
    mk.crate(C, 242.7, -12.2, s=0.9, z=Z, key="olive")                # 충돌은 키트의 COL
    mk.crate(C, 243.7, -12.2, s=0.9, z=Z, key="olive")
C.box("glow", 251.3, 251.6, -12.22, -12.18, Z + 1.1, Z + 1.2, kind="fine")
# 통로 (상판 남쪽 방호벽 틈 → 기단 층)
C.box("grate", 245.5, 248.5, BY1, -HALF, Z - 0.08, Z, kind="detail")
C.box("tower_band", 245.5, 248.5, BY1, -HALF, Z - 0.3, Z - 0.08, kind="detail")
C.col(245.5, 248.5, BY1, -HALF, Z - 0.3, Z)
ok.rail_run(C, (245.5, BY1, Z), (245.5, -HALF, Z), col=COL)
ok.rail_run(C, (248.5, BY1, Z), (248.5, -HALF, Z), col=COL)

# --- 관측 계단 (기단 층 → 관측 갑판, 서쪽 바깥 곧은 계단 + 중간 층참)
AX0, AX1 = 239.7, 241.3
ok.stair_flight(C, COL, AX0, AX1, BY0, -23.0, Z, 12.5, steps=20)
ok.landing(C, AX0, AX1, -24.6, -23.0, 12.5, posts_to=YZ)
ok.rail_run(C, (AX0, -24.6, 12.5), (AX0, -23.0, 12.5), col=COL)
ok.rail_run(C, (AX1, -24.6, 12.5), (AX1, -23.0, 12.5), col=COL)
ok.stair_flight(C, COL, AX0, AX1, -24.6, -30.6, 12.5, OZ, steps=20)
ok.landing(C, AX0, OX0, OY0, -30.6, OZ, posts_to=YZ)
ok.rail_run(C, (AX0, OY0, OZ), (AX0, -30.6, OZ), col=COL)
ok.rail_run(C, (AX0, OY0 + 0.05, OZ), (OX0, OY0 + 0.05, OZ), col=COL)
ok.rail_run(C, (AX1, -30.6, OZ), (OX0, -30.6, OZ), col=COL)
for y in (-20.0, -27.6):
    C.box("metal", AX0 + 0.05, AX0 + 0.2, y - 0.08, y + 0.08, -0.3, (10.6 if y > -24 else 14.1), kind="detail")
    C.box("metal", AX1 - 0.2, AX1 - 0.05, y - 0.08, y + 0.08, -0.3, (10.6 if y > -24 else 14.1), kind="detail")
    for (xa, xb) in ((AX0 + 0.05, AX0 + 0.2), (AX1 - 0.2, AX1 - 0.05)):
        C.col(xa, xb, y - 0.08, y + 0.08, YZ, (10.6 if y > -24 else 14.1) - 0.05)   # 계단 받침 기둥

# --- 안전 철망 (ok.guard_run, 2.0 m): 관측탑 둘레를 정해진 길로 (레일 슈터). 0.85 m 난간만으로는 층참에서 뛰어 내려가는 계단
# 난간 윗대에 올라서 바깥으로 걸어 나가거나, 계단을 달려 내려가며 비스듬히 뛰어 난간을 넘어 계단 밑·마당으로 떨어졌다
# (scripts/wedgecheck.mjs m8_tower drop). 관측 계단 두 구간·중간 층참·꼭대기 층참·갑판 서쪽(계단과 갑판 사이 빈 곳).
# 평평한 갑판·기단 층의 다른 난간·흉벽은 디딤판(상자·모래주머니·배전반)을 climb=0으로 막아 0.85 m 그대로 둔다
# (갑판 북쪽·동쪽은 관측과 사격 시야)
for xs in (AX0, AX1):
    ok.guard_run(C, COL, (xs, BY0, Z), (xs, -23.0, 12.5))                  # 아래 구간
    ok.guard_run(C, COL, (xs, -24.6, 12.5), (xs, -23.0, 12.5))             # 중간 층참
    ok.guard_run(C, COL, (xs, -24.6, 12.5), (xs, -30.6, OZ))               # 위 구간
ok.guard_run(C, COL, (AX0, OY0, OZ), (AX0, -30.6, OZ))                      # 꼭대기 층참 서쪽
ok.guard_run(C, COL, (AX0, OY0 + 0.05, OZ), (OX0, OY0 + 0.05, OZ))          # 꼭대기 층참 남쪽
ok.guard_run(C, COL, (AX1, -30.6, OZ), (OX0, -30.6, OZ))                    # 꼭대기 층참 북쪽 (위 구간 동쪽과 갑판 사이)
ok.guard_run(C, COL, (OX0 + 0.05, -30.6, OZ), (OX0 + 0.05, OY1 - 0.3, OZ))  # 갑판 서쪽

# --- 마당 → 기단 층 꺾은 계단 (5구간)
L1 = (253.2, 254.9)
L2 = (255.1, 256.8)
NY0, NY1 = -12.6, -11.0          # 북쪽 층참 띠
SY0_, SY1_ = -17.0, -15.4        # 남쪽 층참 띠
ZL = [YZ + (Z - YZ) * k / 5 for k in range(6)]
for k in range(5):
    lane = L1 if k % 2 == 0 else L2
    if k % 2 == 0:
        ok.stair_flight(C, COL, lane[0], lane[1], NY0, SY1_, ZL[k], ZL[k + 1], steps=10)
    else:
        ok.stair_flight(C, COL, lane[0], lane[1], SY1_, NY0, ZL[k], ZL[k + 1], steps=10)
for k in (1, 3, 5):
    x0_ = BX1 if k == 5 else L1[0]
    ok.landing(C, x0_, L2[1], SY0_, SY1_, ZL[k], posts_to=YZ if k < 5 else None)
    ok.rail_run(C, (x0_, SY0_ + 0.05, ZL[k]), (L2[1], SY0_ + 0.05, ZL[k]), col=COL)
    ok.rail_run(C, (L2[1] - 0.05, SY0_, ZL[k]), (L2[1] - 0.05, SY1_, ZL[k]), col=COL)
    if k < 5:
        ok.rail_run(C, (L1[0] + 0.05, SY0_, ZL[k]), (L1[0] + 0.05, SY1_, ZL[k]), col=COL)
    else:
        ok.rail_run(C, (L2[0] - 0.1, SY1_, ZL[k]), (L2[1], SY1_, ZL[k]), col=COL)
for k in (2, 4):
    ok.landing(C, L1[0], L2[1], NY0, NY1, ZL[k], posts_to=YZ)
    ok.rail_run(C, (L1[0], NY1 - 0.05, ZL[k]), (L2[1], NY1 - 0.05, ZL[k]), col=COL)
    ok.rail_run(C, (L1[0] + 0.05, NY0, ZL[k]), (L1[0] + 0.05, NY1, ZL[k]), col=COL)
    ok.rail_run(C, (L2[1] - 0.05, NY0, ZL[k]), (L2[1] - 0.05, NY1, ZL[k]), col=COL)
for (x, y) in ((L1[0], SY0_), (L2[1], SY0_), (L1[0], NY1), (L2[1], NY1)):
    C.box("tower_band", x - 0.1, x + 0.1, y - 0.1, y + 0.1, -0.3, Z + 1.0, kind="detail")  # 난간 면과 1.5 cm 넘게 어긋나게
    C.col(x - 0.1, x + 0.1, y - 0.1, y + 0.1, YZ, Z + 1.0)
C.text("white", "정비 계단 · SERVICE STAIR", 0.2, (256.85, -14.0, 1.2), (1, 0, 0), kind="fine")
# 정비 계단 안전 철망 (관측 계단과 같은 2.0 m): 구간 양옆(두 줄 사이 포함)과 층참 바깥 난간. 계단을 달려 내려가며 뛰면
# 바깥 난간을 넘어 마당으로, 안쪽 난간을 넘어 한 구간 아래로 3 m 넘게 떨어졌다 (wedgecheck m8_tower drop)
for k in range(5):
    lane = L1 if k % 2 == 0 else L2
    ya, yb = (NY0, SY1_) if k % 2 == 0 else (SY1_, NY0)
    for xs in lane:
        ok.guard_run(C, COL, (xs, ya, ZL[k]), (xs, yb, ZL[k + 1]))
for k in (1, 3, 5):
    x0_ = BX1 if k == 5 else L1[0]
    ok.guard_run(C, COL, (x0_, SY0_ + 0.05, ZL[k]), (L2[1], SY0_ + 0.05, ZL[k]))
    ok.guard_run(C, COL, (L2[1] - 0.05, SY0_, ZL[k]), (L2[1] - 0.05, SY1_, ZL[k]))
    if k < 5:
        ok.guard_run(C, COL, (L1[0] + 0.05, SY0_, ZL[k]), (L1[0] + 0.05, SY1_, ZL[k]))
    else:
        ok.guard_run(C, COL, (L2[0] - 0.1, SY1_, ZL[k]), (L2[1], SY1_, ZL[k]))
for k in (2, 4):
    ok.guard_run(C, COL, (L1[0], NY1 - 0.05, ZL[k]), (L2[1], NY1 - 0.05, ZL[k]))
    ok.guard_run(C, COL, (L1[0] + 0.05, NY0, ZL[k]), (L1[0] + 0.05, NY1, ZL[k]))
    ok.guard_run(C, COL, (L2[1] - 0.05, NY0, ZL[k]), (L2[1] - 0.05, NY1, ZL[k]))

# --- 관측 장비 (미션이 켠다)
GEAR = Vector((252.0, -26.0, OZ))
ok.tripod_gear(C, "GEAR_tripod", tuple(GEAR), 90.0)

# ================================================================== 4. 원경: 평야 바닥 (높이장)
C.group("plain", noOutline=1)
XS = ok.grid_lines(-2600, 6200, 250.0, step0=40.0, k=0.075, step_max=420.0)
YS = ok.grid_lines(-5200, 4800, -20.0, step0=40.0, k=0.075, step_max=420.0)
FIELDS = ["field_wheat", "field_green", "field_lush", "field_soil", "field_fallow", "meadow", "field_green",
          "field_wheat", "field_flower", "grass_d"]


def hsh(a, b, s=0):
    v = math.sin(a * 12.9898 + b * 78.233 + s * 37.719) * 43758.5453
    return v - math.floor(v)


def zone_special(cx, cy):
    if math.hypot(cx - 3400, cy - 120) < 520:
        return "meadow"
    if math.hypot(cx - 2900, cy - 3900) < 780:
        return "forest_far"
    if abs(cy - 7) < 32 and -260 < cx < 1350:
        return "meadow"
    if 225 < cx < 280 and -60 < cy < 0:
        return "grass_d"
    return None


def mat_fn(cx, cy, hc, slope):
    if hc > 440:
        return "mount_snow"
    if hc > 165 or slope > 0.5:
        return "mount_rock"
    if cy < -1000 and hc > 16:
        return "forest_far"
    z = zone_special(cx, cy)
    if z:
        return z
    return FIELDS[int(hsh(round(cx), round(cy)) * len(FIELDS))]


def strips(cx, cy):
    if zone_special(cx, cy) or h(cx, cy) > 14 or cy < -1150:
        return None
    r = hsh(round(cx), round(cy), 3)
    if r > 0.38:
        return None
    n = 2 + int(r * 10) % 2
    keys = [FIELDS[int(hsh(cx + k, cy - k, 5) * len(FIELDS))] for k in range(n)]
    return ("x" if hsh(cx, cy, 7) < 0.5 else "y"), keys


ok.heightfield(C, XS, YS, hz, mat_fn, strips=strips, kind="far")
print(f"[m8] ground grid {len(XS) - 1} x {len(YS) - 1}")

# 생울타리·나무줄 (2.5 km 안의 평야)
C.group("hedges", noOutline=1)
nh = nt = 0
for i in range(1, len(XS) - 1):
    for j in range(len(YS) - 1):
        x, y0, y1 = XS[i], YS[j], YS[j + 1]
        cy = (y0 + y1) / 2
        if math.hypot(x - 250, cy) > 1900 or zone_special(x, cy) or h(x, cy) > 12 or cy < -1150:
            continue
        if 180 < x < 330 and -70 < cy < 40:
            continue
        if hsh(x, cy, 11) < 0.13:
            ok.hedge(C, (x, y0), (x, y1), hz, height=1.8 + hsh(x, cy, 2) * 0.8)
            nh += 1
            if hsh(x, cy, 13) < 0.4 and math.hypot(x - 250, cy) < 1400:
                yy = y0 + 6
                while yy < y1 - 6:
                    mk.lod_tree(C, x + (hsh(x, yy, 1) - 0.5) * 3, yy, h=9 + hsh(yy, x, 2) * 6, r=3.5 + hsh(x, yy, 3) * 1.5,
                                z=hz(x, yy) - 0.4, key="leaf_d" if hsh(x, yy, 4) < 0.5 else "leaf", kind="far",
                                rot=hsh(x, yy, 6) * 3)
                    nt += 1
                    yy += 26 + hsh(x, yy, 5) * 16
for j in range(1, len(YS) - 1):
    for i in range(len(XS) - 1):
        y, x0, x1 = YS[j], XS[i], XS[i + 1]
        cx = (x0 + x1) / 2
        if math.hypot(cx - 250, y) > 1900 or zone_special(cx, y) or h(cx, y) > 12 or y < -1150:
            continue
        if 180 < cx < 330 and -70 < y < 40:
            continue
        if hsh(cx, y, 17) < 0.12:
            ok.hedge(C, (x0, y), (x1, y), hz, height=1.8 + hsh(cx, y, 2) * 0.8)
            nh += 1
print(f"[m8] hedges {nh}, hedge trees {nt}")
# 숲 덤불 (평야의 작은 숲)
for (fx, fy, r, n, sd) in ((620, -420, 70, 18, 1), (980, 640, 90, 22, 2), (-150, 520, 80, 18, 3), (1450, -650, 110, 24, 4),
                           (2150, 520, 120, 26, 5), (380, 900, 70, 16, 6), (-420, -380, 90, 18, 7),
                           (1750, 1500, 150, 30, 8)):
    rng = random.Random(sd)
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = r * math.sqrt(rng.random())
        x, y = fx + math.cos(a) * d, fy + math.sin(a) * d
        mk.lod_tree(C, x, y, h=rng.uniform(11, 17), r=rng.uniform(4, 6.5), z=hz(x, y) - 0.5,
                    key=rng.choice(("leaf_d", "leaf", "forest_far")), kind="far", rot=rng.uniform(0, 3))
# 정령산 숲 (산 아랫자락에 흩어진 큰 나무 실루엣)
rng = random.Random(41)
for k in range(170):
    x, y = rng.uniform(-2400, 5800), rng.uniform(-3600, -1300)
    z = hz(x, y)
    if not (14 < z < 200):
        continue
    mk.lod_tree(C, x, y, h=rng.uniform(22, 34), r=rng.uniform(8, 12), z=z - 2, key="forest_far", kind="far",
                rot=rng.uniform(0, 3), sides=5)
# 농가
for (x, y, ax, sd) in ((140, -190, "x", 1), (430, 150, "y", 2), (720, -260, "x", 3), (900, 390, "x", 4),
                       (-260, -240, "y", 5), (1300, -330, "y", 6), (1650, 260, "x", 7), (2250, -420, "x", 8),
                       (520, 700, "y", 9), (1900, 900, "x", 10), (-80, 760, "x", 11), (2500, 1100, "y", 12)):
    ok.farmstead(C, x, y, hz(x, y), yaw_axis=ax, seed=sd)

# 길 (지면에서 0.6 m 띄운 띠)
C.group("roads", noOutline=1)
ok.raised_path(C, [(520, -1150), (520, -300), (540, 400), (600, 1400), (760, 2600)], 6.0, hz)    # 남북 시골길 (고가 밑)
ok.raised_path(C, [(540, 60), (800, 40), (1000, 65), (1060, 70)], 4.5, hz)                       # 망루 가는 길
ok.raised_path(C, [(252, -44), (252, -260), (520, -262)], 5.0, hz, lift=0.3)                     # 정비 마당 진입로
ok.raised_path(C, [(-80, -9.1), (-260, -9.1), (-430, -12)], 7.0, hz, lift=0.25)                  # 램프 아래 도시 쪽
ok.raised_path(C, [(1500, 0), (2200, 20), (2900, 80)], 15.0, hz, lift=1.4, key="asphalt")        # 알프토반 성토 구간
ok.raised_path(C, [(600, 1400), (1400, 1650), (2300, 2050), (2550, 2180)], 6.0, hz)              # 발사장 쪽 길
ok.raised_path(C, [(1060, 70), (1700, -180), (2400, -150), (2870, 30)], 4.5, hz)                 # 망루 → 에르피엔

# ================================================================== 5. 원경 고가 (동쪽 → 에르피엔, 서쪽 → 모나티엄)
C.group("highway_far", noOutline=1)
ok.deck_far(C, 450.0, 1300.0, 0.0, pier0=465.0, ground=hz, lamps=36.0)
ok.deck_far(C, 450.0, 1300.0, YT, pier0=465.0, ground=hz)
ok.deck_far(C, -700.0, -130.0, 0.0, pier0=-135.0, ground=hz, lamps=36.0)
ok.deck_far(C, -700.0, -130.0, YT, pier0=-135.0, ground=hz)
for yc in (0.0, YT):
    b = C.bm("asphalt", "far")
    b.faces.new([b.verts.new(p) for p in ((1300, yc - HALF, Z), (1500, yc - HALF, 1.4), (1500, yc + HALF, 1.4),
                                          (1300, yc + HALF, Z))])
    for yy in (yc - HALF, yc + HALF):
        b.faces.new([b.verts.new(p) for p in ((1300, yy, Z), (1300, yy, -1), (1500, yy, -1), (1500, yy, 1.4))])
# R41 도로 봉쇄 (동쪽 토막 너머 상판 위)
for (x, y, yaw) in ((708, -2.5, 20), (716, 3.0, -15), (731, -0.5, 80)):
    C.rbox("r41_shell", (x, y, Z + 1.3), (6.5, 3.0, 2.6), (0, 0, yaw), kind="far")
    C.rbox("r41_metal", (x, y, Z + 2.9), (2.4, 1.8, 0.7), (0, 0, yaw + 10), kind="far")
C.cyl("r41_metal", (722, -5.5, Z + 0.8), (722, -5.5, Z + 7.5), 0.15, segs=4, kind="far")
C.blob("magenta", (722, -5.5, Z + 7.8), 0.45, segs=6, rings=4, kind="fine")

# ================================================================== 6. 원경 랜드마크
C.group("landmarks", noOutline=1)
REF_TIP, REF_PLAT = ok.fairy_watchtower(C, 1100.0, 70.0, hz)
# 에르피엔: [원작] 왕국 한가운데 세계수, 밑동을 두른 왕궁, 둘레의 시가와 이중 성벽 (erpien_kit). 관측 갑판에서 약 3.15 km 동쪽
ERP = ek.erpien(C, ERP_C[0], ERP_C[1], hz(*ERP_C), ERP_H, hfun=hz, face=(OP.x - ERP_C[0], OP.y - ERP_C[1]), kind="far",
                detail=0, seed=11, lit="win_lit", density=0.8)
LAUNCH = ok.launch_site(C, 2600.0, 2200.0, hz)
SION_Z = hz(900, -1980)
SION = ok.watch_post(C, 900.0, -1980.0, SION_Z)
# R41 진지 (평야)
ok.r41_camp(C, 640, 560, hz, seed=1, yaw_deg=200)
ok.r41_camp(C, 1650, 950, hz, seed=2, yaw_deg=210)
ok.r41_camp(C, 2760, -170, hz, seed=3, yaw_deg=0, n=8)
ok.r41_camp(C, 2740, 430, hz, seed=4, yaw_deg=0, n=7)
ok.r41_camp(C, 1880, -380, hz, seed=5, yaw_deg=30, n=4, beacon=False)

# 연기 기둥 (전투 흔적 + 발사장)
C.group("smoke", noOutline=1)
# 에르피엔 왕궁(방위 약 +2.7°)을 가리지 않게 양옆으로 비켜 세운다
for (x, y, hh, r, sd, fire) in ((480, -320, 110, 7, 1, True), (1250, 380, 140, 8, 2, True), (1900, 650, 150, 9, 3, True),
                                (2700, -330, 190, 10, 4, True), (2900, 640, 180, 10, 5, True),
                                (3250, 480, 220, 12, 6, True), (3650, -340, 200, 11, 7, True),
                                (2640, 2230, 130, 12, 8, False), (-900, -200, 150, 9, 9, True),
                                (-1250, 330, 130, 8, 10, True)):
    ok.smoke(C, x, y, hz(x, y), h=hh, r=r, drift=(0.32, 0.12), seed=sd, fire=fire)
# 구름 (새벽: 아래가 옅은 보라)
for (x, y, z, s, sd) in ((1500, 2600, 760, 190, 1), (3900, 1300, 880, 230, 2), (-800, 1900, 650, 170, 3),
                         (2600, -2300, 900, 260, 4), (4700, -700, 820, 210, 5), (700, 3300, 950, 240, 6),
                         (-1600, -1400, 780, 200, 7)):
    ok.cloud(C, x, y, z, size=s, seed=sd, key="cloud_k" if sd % 2 else "cloud_w")

# ================================================================== 7. 모나티엄 (서쪽 원경)
C.group("monatium", noOutline=1)
rng = random.Random(21)
for k in range(110):
    x, y = rng.uniform(-1750, -420), rng.uniform(-780, 780)
    if abs(y - 7) < 34:
        continue
    near_core = math.hypot(x + 1100, y - 100) < 380
    w, d = rng.uniform(26, 64), rng.uniform(26, 64)
    hh = rng.uniform(10, 34) * (2.1 if near_core else 1.0) * (0.6 if x > -700 else 1.0)
    key = rng.choice(["concrete", "warm", "far", "far_d", "concrete_d", "far"])
    z0 = hz(x, y)
    mk.lod_box(C, key, x - w / 2, x + w / 2, y - d / 2, y + d / 2, z0 - 1, z0 + hh, kind="far")
    if rng.random() < 0.45:
        for q in range(rng.randint(1, 4)):
            zz = z0 + rng.uniform(3, hh - 3)
            yy = y + rng.uniform(-d / 2 + 3, d / 2 - 3)
            C.rect("win_lit", (x + w / 2, yy, zz + 0.8), (1, 0, 0), 2.8, 1.6, lift=0.15)
for (x, y, hh) in ((-1150, 120, 96), (-1020, -60, 82), (-1260, -120, 74), (-980, 260, 108), (-1320, 300, 66),
                   (-890, 70, 60)):
    C.cyl("glass_t", (x, y, -1), (x, y, hh), 16, segs=8, kind="far", cap=False)
    C.cyl("mullion", (x, y, hh), (x, y, hh + 3), 17, segs=8, kind="far")
    C.cyl("glow", (x, y, hh * 0.7), (x, y, hh * 0.7 + 1.2), 16.3, segs=8, kind="fine", cap=False)
# 코어 AI 탑 (M7에서 통신망이 되살아남: 시안 띠가 켜져 있다)
C.cyl("concrete", (-1060, 210, -1), (-1060, 210, 128), 13, r2=9, segs=10, kind="far")
for k in range(6):
    zz = 30 + k * 16
    C.cyl("glow", (-1060, 210, zz), (-1060, 210, zz + 2.2), 13.3 - k * 0.65, segs=10, kind="fine", cap=False)
b = C.bm("gold", "far")
mk._bm_torus(b, (-1060, 210, 136), 16, 1.2, seg=16, rseg=4)
C.blob("glow", (-1060, 210, 132), 3.0, segs=8, rings=4, kind="fine")
for k in range(16):
    x = rng.uniform(-420, -160)
    y = rng.choice((-1, 1)) * rng.uniform(45, 260)
    w, d = rng.uniform(20, 46), rng.uniform(18, 40)
    mk.lod_box(C, rng.choice(["concrete_d", "roof", "concrete"]), x - w / 2, x + w / 2, y - d / 2, y + d / 2, -1,
               rng.uniform(6, 11), kind="far")

# ================================================================== 8. 새벽 하늘 돔 (카메라를 따라다닌다)
C.group("sky")


def mix(a, b, t):
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    t = max(0.0, min(1.0, t))
    return "#" + "".join(f"{round(pa[k] + (pb[k] - pa[k]) * t):02x}" for k in range(3))


def ramp(stops, x):
    if x <= stops[0][0]:
        return stops[0][1]
    for (x0, c0), (x1, c1) in zip(stops, stops[1:]):
        if x <= x1:
            return mix(c0, c1, (x - x0) / (x1 - x0))
    return stops[-1][1]


SKY_V = [(-12, "#2e3f63"), (-1, "#56709f"), (0.6, "#6a85b4"), (3, "#6680b0"), (8, "#5671a5"), (15, "#41598f"),
         (26, "#2d437a"), (42, "#1f3165"), (65, "#16234f"), (90, "#101a40")]
GLOW_V = [(-12, "#c58c78"), (-1, "#f59a68"), (0.6, "#ffb07a"), (3, "#fcc18e"), (6, "#efc8a4"), (10, "#c1b6c2"),
          (16, "#8492b8"), (30, "#4b5f93")]
GLOW_AZ = -8.0      # 해가 뜰 자리: 동쪽에서 조금 남쪽 (에르피엔 뒤)


def sky_color(az, el):
    base = ramp(SKY_V, el)
    da = (az - GLOW_AZ + 180) % 360 - 180
    wa = math.exp(-(da / 50.0) ** 2)
    we = math.exp(-(max(el, 0.0) / 10.0) ** 2) if el > 0 else 1.0
    c = mix(base, ramp(GLOW_V, el), wa * we * 0.95)
    # 동쪽 하늘 전체가 조금 밝다 (넓은 번짐)
    w2 = math.exp(-(da / 95.0) ** 2) * math.exp(-(max(el, 0) / 24.0) ** 2) * 0.35
    return mix(c, "#8a9bc4", w2)


def sky_extras(bys):
    """두 달(엘리아스의 낮달, 서남서로 지는 중)과 별 몇 개. 로컬 좌표 = 카메라 기준."""
    def disc(key, az, el, r, dist, n=24):
        b = bys.setdefault(key, bmesh.new())
        a, e = math.radians(az), math.radians(el)
        D = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        R_ = D.cross(Vector((0, 0, 1))).normalized()
        U = R_.cross(D).normalized()
        c = D * dist
        vs = [b.verts.new(c + R_ * (math.cos(2 * math.pi * k / n) * r) + U * (math.sin(2 * math.pi * k / n) * r))
              for k in range(n)]
        f = b.faces.new(vs)
        f.normal_update()
        if f.normal.dot(D) > 0:
            f.normal_flip()
    disc("moon", 203.0, 17.0, 150.0, 6300.0)
    disc("moon_d", 201.6, 17.6, 40.0, 6290.0, n=12)
    disc("moon_d", 204.3, 16.3, 26.0, 6290.0, n=12)
    disc("moon", 214.0, 24.0, 82.0, 6300.0)
    disc("moon_d", 214.4, 23.6, 58.0, 6290.0, n=16)
    rng_ = random.Random(77)
    for k in range(70):
        az = rng_.uniform(70, 330)
        el = rng_.uniform(22, 85)
        disc("sky_a", az, el, rng_.uniform(5, 11), 6200.0, n=4)


ok.sky_dome(C, "SKY_dawn", tuple(OP + Vector((0, 0, 1.0))), sky_color, radius=6600.0, segs=36, extras=sky_extras)

# ================================================================== 9. 충돌 · 트리거
C.group("collision")
COL.flush(C, "stairs_ramps")
ok.flush_vehicle_cols(C, "vehicles")
C.group("triggers")
ok.trig(C, "deck_mid", 100.0, 104.0, -HALF, HALF, Z, Z + 3.0)
ok.trig(C, "op", BX0, BX1, BY0, -HALF, Z, Z + 3.0)
ok.trig(C, "op_top", AX0, OX1, OY0, OY1, OZ, OZ + 3.0)

# ================================================================== 10. 마커
C.group("markers")
EAST = 90.0     # 마커 yaw: -Y가 +X(동쪽)를 본다
C.marker("SPAWN_player", (-2.0, -9.0, Z), yaw=EAST)
C.marker("SPAWN_deck", (101.0, -1.5, Z), yaw=EAST)
C.marker("SPAWN_op", (244.5, -14.0, Z), face=(240.5, -20.0))
C.marker("SPAWN_op_top", (251.0, -24.4, OZ), yaw=EAST)
for (who, x, y) in (("rona", -4.2, -7.4), ("sabre", -4.8, -9.2), ("jesty", -7.0, -7.6), ("karen", -7.6, -9.3)):
    C.marker(f"ALLY_{who}", (x, y, Z), yaw=EAST, props={"who": who, "behavior": "follow", "weapon": "m4a1"})


def enemy(eid, loc, face, kind, group, behavior, spawn="start"):
    props = {"kind": kind, "group": group, "behavior": behavior, "spawn": spawn}
    if kind != "riot":
        # riot은 weapon·drop을 두지 않는다: 전투 시스템 기본값(r41_suppressor + 방패)을 쓴다
        props.update({"weapon": "r41_carbine", "drop": "r41_carbine"})
    C.marker(f"ENEMY_{eid}", loc, face=face, props=props)


W = -1000.0     # 서쪽을 본다 (플레이어가 오는 쪽)
# 상판 1 (문형 1, R41 검문)
enemy("d1_01", (76.6, -4.2, Z), (W, -4.2), "rifleman_a", "deck1", "hold")
enemy("d1_02", (84.6, 0.8, Z), (W, 0.8), "rifleman_b", "deck1", "hold")
enemy("d1_03", (71.4, 5.0, Z), (W, 5.0), "rifleman_c", "deck1", "hold")
enemy("d1_04", (91.2, 4.6, Z), (W, 4.6), "officer", "deck1", "hold")
enemy("d1_05", (96.4, 1.6, Z), (W, 1.6), "assault", "deck1", "advance")
# 상판 2 (버스·장갑차·불탄 차 사이)
enemy("d2_01", (128.0, 4.6, Z), (W, 4.6), "rifleman_b", "deck2", "hold")
enemy("d2_02", (138.6, -4.9, Z), (W, -4.9), "rifleman_a", "deck2", "hold")
enemy("d2_03", (152.6, 1.9, Z), (W, 1.9), "riot", "deck2", "rush")
enemy("d2_04", (152.8, -4.6, Z), (W, -4.6), "rifleman_c", "deck2", "advance")
enemy("d2_05", (163.6, 2.4, Z), (W, 2.4), "assault", "deck2", "flank")
enemy("d2_06", (174.4, -0.6, Z), (W, -0.6), "officer", "deck2", "hold")
# 관제탑 (기단 층 + 계단 층참 + 갑판)
enemy("t_01", (242.2, -13.2, Z), (247.0, -7.0), "rifleman_a", "tower", "hold")
enemy("t_02", (251.4, -15.9, Z), (247.0, -7.0), "rifleman_b", "tower", "hold")
enemy("t_03", (240.5, -23.8, 12.5), (240.5, -17.0), "rifleman_c", "tower", "hold")
enemy("t_04", (245.0, -31.4, OZ), (241.0, -31.4), "assault", "tower", "hold")
# 웨이브 1: 마당 → 꺾은 계단
enemy("w1_01", (254.0, -10.4, YZ), (254.0, -14.0), "rifleman_a", "op_wave1", "advance", "manual")
enemy("w1_02", (256.0, -10.0, YZ), (254.0, -14.0), "rifleman_b", "op_wave1", "advance", "manual")
enemy("w1_03", (254.4, -16.3, ZL[1]), (256.0, -13.0), "assault", "op_wave1", "advance", "manual")
enemy("w1_04", (255.4, -11.8, ZL[2]), (254.0, -14.0), "rifleman_c", "op_wave1", "advance", "manual")
enemy("w1_05", (255.6, -16.3, ZL[3]), (256.0, -13.0), "rifleman_a", "op_wave1", "advance", "manual")
# 웨이브 2: 서쪽 상판에서 + 계단으로 (riot 하나 돌격)
enemy("w2_01", (196.6, 0.4, Z), (247.0, -6.0), "rifleman_a", "op_wave2", "advance", "manual")
enemy("w2_02", (204.0, -5.2, Z), (247.0, -6.0), "assault", "op_wave2", "flank", "manual")
enemy("w2_03", (214.0, 1.2, Z), (247.0, -6.0), "rifleman_b", "op_wave2", "advance", "manual")
enemy("w2_04", (220.0, -3.8, Z), (247.0, -6.0), "riot", "op_wave2", "rush", "manual")
enemy("w2_05", (254.0, -9.8, YZ), (254.0, -14.0), "rifleman_c", "op_wave2", "advance", "manual")
enemy("w2_06", (255.9, -16.3, ZL[1]), (256.0, -13.0), "officer", "op_wave2", "flank", "manual")
# 웨이브 3: 남은 병력 (계단)
enemy("w3_01", (253.8, -9.6, YZ), (254.0, -14.0), "rifleman_b", "op_wave3", "advance", "manual")
enemy("w3_02", (256.2, -9.9, YZ), (254.0, -14.0), "assault", "op_wave3", "advance", "manual")
enemy("w3_03", (255.9, -16.2, ZL[1]), (256.0, -13.0), "rifleman_a", "op_wave3", "advance", "manual")
enemy("w3_04", (254.2, -11.8, ZL[2]), (254.0, -14.0), "rifleman_c", "op_wave3", "advance", "manual")

# 엄폐 (-Y = 적 쪽)
COVERS = [("d01", 20.0, 3.4, "low"), ("d02", 31.6, -2.0, "low"), ("d03", 41.6, 0.4, "high"), ("d04", 74.6, 0.6, "high"),
          ("d05", 65.4, 3.0, "high"), ("d06", 85.6, 4.4, "low"), ("d07", 116.4, 1.6, "high"), ("d08", 110.6, -2.8, "low"),
          ("d09", 132.8, -3.2, "low"), ("d10", 144.4, -1.6, "high"), ("d11", 157.4, 4.2, "low"),
          ("d12", 167.6, -2.4, "low"), ("d13", 193.6, -2.4, "low"), ("d14", 205.2, 3.8, "high"),
          ("d15", 223.6, -1.6, "low"), ("d16", 231.4, 3.6, "low")]
for (cid, x, y, ht) in COVERS:
    C.marker(f"COVER_{cid}", (x, y, Z), yaw=EAST, props={"height": ht})
C.marker("COVER_op01", (247.8, -21.8, OZ), face=(247.8, 0.0), props={"height": "low"})
C.marker("COVER_op02", (244.2, -27.0, OZ), face=(230.0, -27.0), props={"height": "low"})
C.marker("COVER_op03", (249.9, -31.2, OZ), face=(240.0, -31.6), props={"height": "high"})
C.marker("COVER_op04", (245.25, -22.95, OZ), face=(240.5, -18.0), props={"height": "high"})   # 상자 더미와 같이 옮김
C.marker("COVER_op05", (250.6, -12.9, Z), face=(230.0, -4.0), props={"height": "high"})
C.marker("COVER_op06", (243.0, -12.9, Z), face=(243.0, 0.0), props={"height": "low"})

# 목표·레이저 지점
C.marker("MARK_op", (246.0, -14.0, Z))
C.marker("MARK_gear", tuple(GEAR), yaw=EAST)
C.marker("MARK_lase_ref1", tuple(REF_TIP))
C.marker("MARK_lase_wind", tuple(WIND))
C.marker("MARK_launch", tuple(LAUNCH))
IMPACT = Vector((1950.0, -60.0, hz(1950, -60)))
C.marker("MARK_impact", tuple(IMPACT))
C.marker("MARK_sion", tuple(SION), face=(OP.x, OP.y))
C.marker("MARK_erpien", tuple(ERP["center"] + Vector((0, 0, ERP_H * 0.28))))     # 세계수 줄기 (왕궁 위)
# 탄도 (발사 레일 끝 → 최고 약 900 m → 낙하점)
LP = Vector(LAUNCH)
APEX = 880.0
for i, t in enumerate((0.03, 0.15, 0.29, 0.43, 0.57, 0.71, 0.85, 0.96), start=1):
    x = LP.x + (IMPACT.x - LP.x) * t
    y = LP.y + (IMPACT.y - LP.y) * t
    z = LP.z * (1 - t) + IMPACT.z * t + 4 * APEX * t * (1 - t)
    C.marker(f"WP_bomb_{i:02d}", (x, y, z))
# 끝 원경 (관측 갑판 뒤에서 평야와 에르피엔으로)
C.cam("handoff", [
    (0.0, (236.0, -44.0, 24.0), (1400.0, 40.0, 30.0), 50),
    (6.0, (244.0, -40.0, 28.0), (2400.0, 90.0, 60.0), 44),
    (12.0, (256.0, -34.0, 33.0), (3400.0, 120.0, 230.0), 36),
])
# 덤: 적 이동 경로 (계단을 오르는 길)
RT_PLAIN = [(254.05, -10.0, YZ), (254.05, -12.6, YZ), (254.05, -15.4, ZL[1]), (255.0, -16.2, ZL[1]),
            (255.95, -15.4, ZL[1]), (255.95, -12.6, ZL[2]), (255.0, -11.8, ZL[2]), (254.05, -12.6, ZL[2]),
            (254.05, -15.4, ZL[3]), (255.0, -16.2, ZL[3]), (255.95, -15.4, ZL[3]), (255.95, -12.6, ZL[4]),
            (255.0, -11.8, ZL[4]), (254.05, -12.6, ZL[4]), (254.05, -15.4, Z), (253.6, -16.2, Z), (250.5, -15.0, Z)]
RT_OP = [(241.8, -14.5, Z), (240.5, -16.6, Z), (240.5, -20.0, 10.75), (240.5, -23.0, 12.5), (240.5, -24.6, 12.5),
         (240.5, -27.6, 14.25), (240.5, -30.6, OZ), (241.2, -31.6, OZ), (244.6, -30.4, OZ)]
RT_DECK = [(190.0, 0.5, Z), (215.0, -1.0, Z), (238.0, -4.2, Z), (247.0, -5.8, Z), (247.0, -8.8, Z), (247.0, -12.4, Z)]
for nm, pts in (("route_plain", RT_PLAIN), ("route_op", RT_OP), ("route_deck", RT_DECK)):
    for i, p in enumerate(pts, start=1):
        C.marker(f"WP_{nm}_{i:02d}", p)

# 거리 점검 (계약 범위)
for nm, p in (("lase_ref1", REF_TIP), ("lase_wind", WIND), ("launch", LAUNCH), ("impact", IMPACT), ("sion", SION),
              ("erpien", ERP["center"])):
    d = (Vector((p[0], p[1], 0)) - Vector((OP.x, OP.y, 0))).length
    print(f"[m8] {nm}: ({p[0]:.1f}, {p[1]:.1f}, {p[2]:.1f})  {d:.0f} m from OP")
# 시온 초소 시선 (관측 갑판 눈높이 → 망루): 지형이 가리는지
eye = OP + Vector((0, 0, 0.9))
blocked = False
for k in range(1, 200):
    t = k / 200
    p = eye.lerp(Vector(SION) + Vector((0, 0, 2)), t)
    if hz(p.x, p.y) > p.z:
        blocked = True
        print(f"[m8] WARNING sion line of sight blocked at {p.x:.0f},{p.y:.0f} terrain {hz(p.x, p.y):.0f} > {p.z:.0f}")
        break
print(f"[m8] sion post ground z {SION_Z:.1f}, line of sight {'BLOCKED' if blocked else 'clear'}")

ROOT = {
    "sky": "#55709f",          # 안개색 = 지우는 색 (돔이 하늘을 덮는다)
    "fog": "1500,22000",
    "sun": "1,0.2,0.16",       # 낮은 동남동 (three.js: x 동, y 위, z 남)
    "sunColor": "#b8c3ea",
    "sunIntensity": 0.9,
    "ambient": 1.45,
    "hemiSky": "#9cb0e0",
    "hemiGround": "#4e4f66",
    "near": 0.05,
    "far": 7000,
    "skyNode": "SKY_dawn",
    "music": "m8",
    "timeOfDay": "predawn",
    "physics": 1,
}
C.finish("levels/m8_overlook.glb", root_props=ROOT, outline=0.025)
