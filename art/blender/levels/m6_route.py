"""2막 M6 「돌파」 후반: 구 기갑병기 보관고(차고) → 공장 지대 도로 → 교차로 → 시청 앞 (새벽).

npm run model -- art/blender/levels/m6_route.py   → public/models/levels/m6_route.glb

원작: 흑뉴아는 이미 에르피엔으로 떠났다. 오리지널: 수용소 북문을 나온 분대와 엘레나 일행이 병기창고와 별개인 차고에서
노획 M1A1(`MNT-T01`)을 꺼내 시청까지 탈출로를 뚫는다. R41 승무원은 정전으로 멈춘 차량 몇 대를 손으로 다시 깨운다
(수동 크랭크·점프 시동, 사격 통제 장치는 죽음). 제스티가 몰고 리타가 포수석, 엘레나 일행은 뒤 갑판에 탄다.
문서: docs/art/m6-route.md, 미션: src/game/missions/m6.ts

좌표 (Blender, m): 길은 북쪽(+Y)으로 간다. 도로 x −8..8. 차고 x −44..−12, y −32..−4. 시청 (0, 404).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import battlefield_kit as bk  # noqa: E402  (부서지는 소품: 철조망·모래주머니·벽돌 담·나무 울타리)
import monatium_city_kit as mk  # noqa: E402
import monatium_depot_kit as dk  # noqa: E402
import monatium_ruins_kit as rk  # noqa: E402
import r41_camp_kit as ck  # noqa: E402

cb.reset()
C = mk.City("m6_route")
CARBINE = "r41_carbine"
SQ = {k: f"characters/squad_{k}.glb" for k in ("sabre", "rona", "jesty", "karen")}

# ---------------------------------------------------------------- 바닥·도로
C.group("ground")
C.box("ash", -70, 70, -90, 450, -0.8, -0.05)
C.col(-70, 70, -90, 450, -0.8, -0.05)
dk.industrial_road(C, -8, 8, -72, 345)                # 시청 앞 판석(y 345~)에서 끝난다: 겹치면 윗면이 같은 평면에서 깜빡인다
C.box("asphalt", -13, -8, -26, -10, -0.4, 0.0)       # 차고 앞 진입로
C.col(-13, -8, -26, -10, -0.4, 0.0)
C.box("asphalt", -60, 60, 177, 193, -0.4, -0.01)     # 교차로 가로 길
C.col(-60, 60, 177, 193, -0.4, -0.01)
# 길가 공터 윗면 -0.02 (도로 0, 둘레 땅 -0.05). 공터 위 소품은 LOT_Z에 둔다 (2026-11-03 floatcheck: 공터에 COL이 없어 소품 COL이
# 둘레 땅 COL 위 5 cm에 떴고, 보이는 공터보다 2 cm 떠 있었다)
LOT_Z = -0.02
for (x0, x1) in [(-18, -7.99), (7.99, 18)]:           # 길가 공터 (엄폐물 자리). 끝면은 도로 상자 속 1 cm (진입로 옆면과 겹치지 않게)
    C.box("pave_d", x0, x1, -72, 345, -0.3, LOT_Z, kind="detail")
    C.col(x0, x1, -72, 345, -0.3, LOT_Z)

# ---------------------------------------------------------------- 남쪽: 수용소 북문 끝자락
C.group("camp_stub")
ck.fence_run(C, (-22, -68), (-3.5, -68))
ck.fence_run(C, (3.5, -68), (22, -68))
ck.gate_posts(C, 0, -68, 7.4, h=4.0, sign=None)
# 북문 표지 (m5_camp 북문과 같은 높은 기둥(4.0 m)·같은 가로판, 양면)
ck.gate_label(C, 0, -68, 7.4, [("북문", 0.8, "white"), ("NORTH GATE", 0.17, "r41_band")], h=4.0)
# 북문은 M6 전반 끝에서 제스티의 폭약에 날아갔다 (m6.ts northGateBlow, missions/breach.ts): 문짝은 둘로 찢어져 길 양옆에 눕고
# 문 자리에는 그을음과 뜯긴 레일 조각이 남는다. 자리·크기·꺾임은 m5_camp(북문 x 20, y 40)에서 터질 때와 같다 (여기 북문은 x 0, y -68)
_LEAF_H, _LEAF_T = 2.75, 0.3


def _torn_leaf(cx, cy, w, yaw, bend):
    """누운 문짝 조각 (가운데 세로선에서 두 칸으로 꺾여 양 끝이 들린다). 폭약 쪽 면이 위"""
    c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    for sx, ang in ((-1, bend / 2), (1, -bend)):
        a = math.radians(ang)
        lx, lz = sx * w / 4 * math.cos(a), w / 4 * abs(math.sin(a))
        ctr = (cx + lx * c, cy + lx * s_, _LEAF_T / 2 + lz)
        C.rbox("r41_grey", ctr, (w / 2, _LEAF_H, _LEAF_T), (0, ang, yaw))
        # COL: 이 조각의 보이는 윗면 네 모서리와 그 아래 땅(-0.05)의 볼록 껍질 (들린 끝까지 윗면 그대로, 밑 틈은 채움).
        # 예전에는 문짝 전체에 납작한 0.24 m 상자 하나라 들린 끝(0.6~0.85 m)에서 발이 문짝 속으로 0.45 m 들어갔다 (2026-11-04 groundcheck)
        rx, ry = math.radians(ang), math.radians(yaw)
        top = []
        for u in (-w / 4, w / 4):
            for v in (-_LEAF_H / 2, _LEAF_H / 2):
                # rbox와 같은 회전 (Z yaw · Y ang): 로컬 (u, v, 두께/2)
                px, pz = u * math.cos(rx) + (_LEAF_T / 2) * math.sin(rx), -u * math.sin(rx) + (_LEAF_T / 2) * math.cos(rx)
                top.append((ctr[0] + px * math.cos(ry) - v * math.sin(ry), ctr[1] + px * math.sin(ry) + v * math.cos(ry), ctr[2] + pz))
        C.ccol(top + [(x, y, -0.05) for (x, y, _) in top])


_torn_leaf(-5.0, -61.5, 4.06, -22, 16)     # 서쪽 조각 (문 폭 -0.5 ~ 0.08)
_torn_leaf(4.8, -63.0, 2.94, 35, 12)       # 동쪽 조각 (0.08 ~ 0.5)
# 뜯긴 위 레일·바닥 레일 조각
C.rbox("r41_grey", (-2.6, -68.05, 2.7), (0.6, 0.06, 0.05), (25, 0, 30))
C.rbox("r41_grey", (0.6, -68.05, 2.72), (0.6, 0.06, 0.05), (-15, 0, -40))
C.rbox("r41_grey", (2.9, -68.0, 0.06), (0.6, 0.05, 0.06), (0, 20, 15))
# 그을음: 문 자리 안쪽(남) 넓게, 바깥(북) 길게
for (sx, sy, rx, ry) in ((0.0, -69.0, 4.2, 1.4), (0.0, -66.4, 3.4, 1.8)):
    C.decal("soot", [(rx * math.cos(k * math.pi / 8) * (0.8 + 0.2 * ((k * 7) % 3) / 2),
                      ry * math.sin(k * math.pi / 8) * (0.8 + 0.2 * ((k * 5) % 3) / 2)) for k in range(16)],
            (sx, sy, 0.0), (0, 0, 1), up=(0, 1, 0), lift=0.012)
C.box("concrete_d", -60, -22, -70, -66, -0.05, 6, col=True)      # 둘레 땅(-0.05)부터
C.box("concrete_d", 22, 60, -70, -66, -0.05, 6, col=True)

# ---------------------------------------------------------------- 차고
C.group("garage")
dk.garage(C, -44, -12, -32, -4, door_c=-18.0)
# 문 표지 (2026-11-05 사용자: 어느 문인지 표기). 목표 「차고 남쪽 쪽문」, 케이트 「큰 문은 잠겼어. 남쪽 쪽문으로.」
# 모나티엄 시설이라 남색 판·청록 테·흰 글자. 남쪽 벽 사람 문(x -20) 오른쪽 눈높이, 동쪽 벽 큰 문 남쪽 끝 아래(MNT 글자 밑)
_DEPOT = dict(bg="navy", rim="teal")
ck.label(C, (-17.5, -32.4, 1.55), (0, -1, 0), [("← 차고 쪽문", 0.5, "white"), ("남쪽 출입구 · DEPOT SIDE DOOR", 0.19, "white")], **_DEPOT)
ck.label(C, (-11.6, -27.6, 1.4), (1, 0, 0), [("큰 문 · 차량 전용", 0.32, "white"), ("출입은 ← 남쪽 쪽문", 0.24, "white")], **_DEPOT)
dk.tarp_over(C, "TARP_m1a1", -27.0, -18.0, L=9.8, W=4.3, H=2.75, yaw=0)
dk.tarp_over(C, "TARP_humvee", -37.5, -26.5, L=5.2, W=2.6, H=2.0, yaw=0, col=True)   # 밑에 차량 없음, 걷지 않음
# 관리번호 판
C.cyl("steel", (-21.0, -21.4, 0), (-21.0, -21.4, 1.2), 0.03, segs=6)
C.col(-21.05, -20.95, -21.45, -21.35, 0, 1.0)            # 기둥만 (판은 머리 높이 1.0~1.5 m: COL을 주면 판 밑에서 앉은 채 못 일어선다)
# 판은 기둥(반지름 0.03) 앞면에 붙인다: 기둥이 판 앞면과 4 mm 차이로 겹치지 않게
C.plate("plywood", [(-0.45, -0.25), (0.45, -0.25), (0.45, 0.25), (-0.45, 0.25)], (-20.97, -21.4, 1.25), (1, 0, 0), 0.03)
C.text("navy", "MNT-T01", 0.16, (-20.94, -21.4, 1.33), (1, 0, 0), lift=0.005)
C.text("teal", "M1A1 · 구 기갑병기", 0.07, (-20.94, -21.4, 1.15), (1, 0, 0), lift=0.005)

# ---------------------------------------------------------------- 1구간: 공장 지대 길 (y −10..140)
C.group("seg1")
for i, (x0, x1, y0, y1) in enumerate([(-40, -20, -60, -40), (-40, -18, 6, 40), (-40, -18, 50, 82), (-40, -18, 92, 136),
                                      (18, 40, -60, -20), (18, 40, -10, 30), (18, 40, 40, 78), (20, 40, 88, 140)]):
    dk.warehouse(C, x0, x1, y0, y1, h=6.5 + (i % 3), seed=i, front="+x" if x0 < 0 else "-x", ruin=0.5)
for (x, y, a) in [(-10.5, 30, 90), (10.5, 52, 90), (-11, 96, 90), (11.5, 104, 80), (-12, 124, 100), (12.5, 128, 90),
                  (-14, 70, 0), (14, 76, 0)]:
    dk.jersey(C, x, y, yaw=a, z=LOT_Z)
for i, (x, y, r) in enumerate([(-13, 60, 1.2), (13, 88, 1.3), (-15, 112, 1.2), (15, 98, 1.1), (-14, 140, 1.3)]):
    rk.rubble(C, x, y, r=r, h=0.9, seed=100 + i, z=LOT_Z)
rk.burnt_car(C, -12.5, 44, yaw=95, z=LOT_Z, seed=11)
rk.burnt_car(C, 12.8, 20, yaw=80, z=LOT_Z, seed=12)
rk.burnt_car(C, 4.0, 160, yaw=20, seed=13)
rk.fire_barrel(C, 1, -15.5, 102, z=LOT_Z)
rk.fire_barrel(C, 2, 16.2, 120, z=LOT_Z)
for (x, y) in [(-16, 0), (16, -40), (-16, 80), (16, 60)]:
    mk.lamp(C, x, y, z=LOT_Z)
mk.street_sign(C, -9.5, 10, "시청 4.2 mi ↑", "CITY HALL", yaw=0, z=LOT_Z)

# ---------------------------------------------------------------- 2구간: 모노레일 아래 교차로 (y 140..240)
C.group("seg2")
rk.monorail_dark(C, -60, 60, 185, pillars=(-30, -12, 12, 30))
C.cyl("concrete", (-21, 185, -0.15), (-21, 185, 1.4), 0.55, segs=14)
rk.col_cyl(C, (-21, 185, -0.15), (-21, 185, 1.4), 0.55, segs=14)
for i, (x0, x1, y0, y1) in enumerate([(-55, -18, 140, 175), (18, 55, 140, 175), (-55, -18, 196, 238), (18, 55, 196, 238)]):
    dk.warehouse(C, x0, x1, y0, y1, h=7.5, seed=20 + i, front="+x" if x0 < 0 else "-x", ruin=0.7)
dk.hull_down(C, -13, 196, yaw=-60)
for (x, y, a) in [(-10.5, 170, 90), (11, 176, 100), (-11, 204, 80), (10.5, 222, 90), (12, 200, 0)]:
    dk.jersey(C, x, y, yaw=a, z=LOT_Z)
rk.burnt_car(C, -24, 186, yaw=0, z=-0.01, seed=21)           # 교차로 가로 길 (윗면 -0.01)
rk.burnt_car(C, 28, 182, yaw=180, z=-0.01, seed=22)
rk.fire_barrel(C, 3, 14.8, 190, z=-0.01)
rk.rubble_wall(C, -62, -58, 177, 193, h=3.0, seed=23)
rk.rubble_wall(C, 58, 62, 177, 193, h=3.0, seed=24)

# ---------------------------------------------------------------- 3구간: 도심 가장자리 폐허 (y 240..340)
C.group("seg3")
for i, (x0, x1, y0, y1) in enumerate([(-42, -16, 242, 268), (-42, -16, 276, 306), (-42, -16, 314, 340),
                                      (16, 42, 242, 270), (16, 42, 278, 300), (16, 42, 308, 340)]):
    rk.ruined_building(C, x0, x1, y0, y1, floors=3 + (i % 2), style=("office", "apartment", "brick")[i % 3],
                       front="+x" if x0 < 0 else "-x", seed=30 + i, broken=0.7)
for i, (x, y, a) in enumerate([(-11, 258, 85), (12, 266, 95), (-12, 288, 100), (13, 312, 80), (-4, 326, 30)]):
    rk.burnt_car(C, x, y, yaw=a, z=LOT_Z if abs(x) > 8 else 0.0, seed=40 + i)
for i, (x, y) in enumerate([(-14, 300), (14, 286), (-13, 330), (15, 330)]):
    rk.rubble(C, x, y, r=1.3, h=0.95, seed=50 + i, z=LOT_Z)
rk.fire_barrel(C, 4, -14.6, 272, z=LOT_Z)
rk.fire_barrel(C, 5, 14.6, 320, z=LOT_Z, rust=True)
for (x, y) in [(-16, 250), (16, 296)]:
    rk.fallen_lamp(C, x, y, 120, z=LOT_Z)

# ---------------------------------------------------------------- 시청 앞 (y 340..430)
C.group("cityhall")
rk.ruined_city_hall(C, 0, 404, east_cover=False)
mk.paving(C, -30, 30, 345, 389.3, tile=1.6, border="pave_r")
mk.paving(C, -30, 30, 396, 430, tile=2.0, grout=None)
mk.fountain(C, 0, 370)
rk.fountain_col(C, 0, 370)
rk.rubble(C, 2.4, 368.2, r=1.1, h=0.8, seed=60)
rk.fallen_column(C, (-12, 386), (-17, 381), r=0.42)
rk.fallen_column(C, (13, 387), (18, 383), r=0.42)
for (x, y) in [(-20, 356), (21, 362), (-6, 380)]:
    rk.rubble(C, x, y, r=1.2, h=0.85, seed=int(x * 3 + y))
rk.fire_barrel(C, 6, -9.0, 352)
# 코어 AI(x 27..41)와 바닥 선(동쪽 x 54까지)은 판석 위에 선다: 판석(x ..30) 밖은 둘레 땅(-0.05)이라 기단·문·선이 5~7 cm
# 떠 있었다 (2026-11-03 floatcheck). 동쪽 건물(y ..400)과 겹치지 않게 y 400부터
mk.paving(C, 30, 56, 400, 430, tile=2.0, grout=None)
mk.core_ai(C, 34, 414, lit=False)
# 남쪽 3구간 건물(y ..340)과 0.2 m 띄운다: 붙이면 층 띠(바깥으로 8 cm)가 겹쳐 윗면이 같은 평면에서 깜빡인다
for (x0, x1, y0, y1) in [(-60, -31, 340.2, 440), (31, 60, 340.2, 400)]:
    rk.ruined_building(C, x0, x1, y0, y1, floors=4, style="office", front="+x" if x0 < 0 else "-x", seed=int(x0), broken=0.5)

# ---------------------------------------------------------------- 부서지는 소품 (BRK_, src/game/level/destructibles.ts)
# 전차(MNT-T01)가 길 가운데로 밀고 지나가며 부수는 것(검문 철조망, 모래주머니 초소, 나무 바리케이드, 벽돌 담)과 도심 입구에서
# 포수(리타)가 주포로 무너뜨리는 엄폐물(R41 소총수 앞 벽돌 담·모래주머니). 길 양쪽 공터(x ±8..18)는 늘 트여 있어 보병 길과
# 진행은 부서지는 것에 기대지 않는다. 습격차 순찰로(y 84~132, 176~214)에는 두지 않는다. 문서: docs/art/m6-route.md
class _Flat:
    @staticmethod
    def h(x, y):
        return LOT_Z if 7.99 < abs(x) < 18 else 0.0       # 길가 공터는 2 cm 낮다


FLAT = _Flat()
C.group("breakables")
# 1구간 입구: R41 검문선 (차고에서 나오면 바로)
bk.wire_coil(C, FLAT, (-7.6, 14.0), (7.6, 14.0), seed=61, breakable=True, brk_name="gate", section=5.0)
for (a, b) in [((-1.55, 40.6), (1.55, 40.6)), ((-1.55, 40.85), (-1.55, 42.4)), ((1.55, 40.85), (1.55, 42.4))]:
    bk.bag_row(C, a, b, 0.0, rows=3, seed=int(a[0] * 7 + a[1]), breakable=True)
bk.picket(C, FLAT, (-6.6, 48.0), (6.6, 48.0), h=1.0, pitch=0.3, key="wood", seed=62, breakable=True, brk_name="road", section=4.4)
bk.stone_wall(C, FLAT, [(-5.2, 57.5), (5.2, 57.5)], h=1.25, t=0.45, seed=63, seg=2.6, key="brick", cap="concrete_d",
              breakable=True, brk_name="road")
# 3구간 (도심 입구): R41 소총수 앞 엄폐물 (포수가 주포로 무너뜨린다)
bk.stone_wall(C, FLAT, [(-14.6, 283.0), (-10.2, 283.0)], h=1.15, t=0.45, seed=64, seg=2.2, key="brick", cap="concrete_d",
              breakable=True, brk_name="rc1")
bk.stone_wall(C, FLAT, [(-16.0, 301.0), (-11.6, 301.0)], h=1.15, t=0.45, seed=65, seg=2.2, key="brick", cap="concrete_d",
              breakable=True, brk_name="rc3")
bk.bag_row(C, (11.0, 287.4), (15.4, 287.4), LOT_Z, rows=4, seed=66, breakable=True, brk_name="rc2")
bk.bag_row(C, (12.4, 313.4), (16.4, 313.4), LOT_Z, rows=4, seed=67, breakable=True, brk_name="rc4")
# 3구간 끝: 길을 막은 철조망과 모래주머니 (싸움이 끝나면 전차가 밀고 시청으로)
bk.wire_coil(C, FLAT, (-7.6, 294.0), (7.6, 294.0), seed=68, breakable=True, brk_name="city", section=5.0)
bk.bag_row(C, (-1.6, 296.2), (1.6, 296.2), 0.0, rows=3, seed=69, breakable=True, brk_name="city")

# ---------------------------------------------------------------- 맵 닫기·원경
C.group("bounds")
for (x0, x1, y0, y1, h) in [(-64, -60, -90, 340, 9), (60, 64, -90, 340, 9), (-64, 64, 440, 446, 12), (-64, 64, -90, -86, 9)]:
    C.box("concrete_d", x0, x1, y0, y1, -0.05, h, col=True)      # 둘레 땅(-0.05)부터 (5 cm 떠 있었다)
C.group("skyline")
rk.dark_skyline(C, 0, 180, r=260, n=44, seed=31, solid_in=(-64, 64, -90, 446))   # 고리 남북 끝 블록이 맵 땅 위에 선다
mk.smoke_column(C, -120, 300, h=80, r=8, seed=4, dark=0.6)
mk.smoke_column(C, 140, 120, h=60, r=6, seed=5, dark=0.6)

# ================================================================== 마커
C.group("markers")
C.marker("SPAWN_player", (0.0, -62.0, 0), face=(0, 0))
C.marker("SPAWN_garage", (-20.0, -28.0, 0), face=(-20, 0))
C.marker("SPAWN_cityhall", (0.0, 352.0, 0), face=(0, 400))
for who, (x, y) in [("sabre", (-1.6, -64.0)), ("rona", (1.6, -64.5)), ("jesty", (-2.6, -66.0)), ("karen", (2.6, -66.0))]:
    C.marker(f"ALLY_{who}", (x, y, 0), face=(x, 0), props={"who": who, "behavior": "follow", "model": SQ[who]})
for nid, (x, y), model, name in [("elena", (-1.0, -67.4), "characters/elena.glb", "엘레나"),
                                 ("amelia", (1.0, -67.8), "characters/amelia.glb", "아멜리아"),
                                 ("rone", (0.0, -68.6), "characters/rone.glb", "로네"),
                                 ("mute", (3.6, -67.0), "characters/mute.glb", "뮤트")]:
    C.npc(nid, (x, y, 0), model, pose="idle", name=name, face=(x, 0))
C.marker("MARK_garage_door", (-20.0, -33.4, 0))
C.marker("MARK_tank", (-27.0, -18.0, 0))
C.marker("MARK_garage_out", (-6.0, -18.0, 0))
C.marker("VEH_m1a1", (-27.0, -18.0, 0.0), yaw=90, props={"vehicle": "m1a1", "faction": "us", "state": "ready"})
TANK = [(-27, -18), (-12, -18), (-1, -8), (0, 30), (0, 70), (0, 110), (1, 150), (0, 185), (-1, 220), (0, 262), (0, 300),
        (0, 330), (0, 346), (0, 352)]
for i, (x, y) in enumerate(TANK, start=1):
    C.marker(f"WP_tank_{i:02d}", (x, y, 0))
for i, y in enumerate((70, 160, 262), start=1):
    C.marker(f"MARK_hold_{i}", (0.0, float(y), 0))
C.marker("MARK_end", (0.0, 350.0, 0))
C.marker("MARK_cityhall_door", (0.0, 397.0, 0.9))


def veh(vid, xy, vehicle, face, state="off", path=None):
    p = {"vehicle": vehicle, "faction": "r41", "state": state}
    if path:
        p["driver"] = "ai"
        p["path"] = path
    C.marker(f"VEH_{vid}", (xy[0], xy[1], 0.0), face=face, props=p)


veh("raider_1", (13.0, 118.0), "r41_raider", (13, 80), path="raider1")
veh("raider_2", (-15.0, 132.0), "r41_raider", (-15, 100), path="raider2")
veh("ifv_1", (-13.0, 196.0), "r41_apc", (2, 172))
veh("raider_3", (12.0, 214.0), "r41_raider", (12, 180), path="raider3")
veh("ifv_2", (10.0, 300.0), "r41_apc", (4, 260))
veh("ifv_3", (-11.0, 318.0), "r41_apc", (-2, 280))
for name, pts in [("raider1", [(13, 118), (9, 92), (-8, 84), (-9, 112)]), ("raider2", [(-15, 132), (-10, 100), (8, 96), (10, 124)]),
                  ("raider3", [(12, 214), (8, 186), (-6, 176), (-8, 205)])]:
    for i, (x, y) in enumerate(pts, start=1):
        C.marker(f"WP_{name}_{i:02d}", (x, y, 0))


def enemy(eid, xy, kind, group, face, behavior="hold"):
    C.marker(f"ENEMY_{eid}", (xy[0], xy[1], 0), face=face,
             props={"kind": kind, "group": group, "behavior": behavior, "weapon": CARBINE})


enemy("crank_a", (15.4, 117.0), "rifleman_c", "route_a", (13, 118))
enemy("crank_b", (10.8, 116.4), "rifleman_a", "route_a", (13, 118))
for i, (x, y, kind) in enumerate([(-11.5, 98, "rifleman_a"), (12.2, 106, "rifleman_b"), (-12.5, 126, "assault"), (11.8, 131, "rifleman_c")], start=1):
    enemy(f"ra_{i}", (x, y), kind, "route_a", (0, y - 30))
for i, (x, y, kind) in enumerate([(-11.6, 172, "rifleman_a"), (12.4, 178, "rifleman_b"), (-12, 206, "assault"), (11.8, 198, "rifleman_c"),
                                  (-6, 214, "rifleman_a")], start=1):
    enemy(f"rb_{i}", (x, y), kind, "route_b", (0, y - 30))
for i, (x, y, kind) in enumerate([(-12.5, 286, "rifleman_a"), (13.2, 290, "assault"), (-13.8, 304, "rifleman_b"), (14.4, 316, "rifleman_c"),
                                  (-5, 334, "rifleman_a")], start=1):
    enemy(f"rc_{i}", (x, y), kind, "route_c", (0, y - 30))
# 추락한 드론
for pid, (x, y, z), model, look in [("drone_1", (-15.0, 18.0, 0.2), "drones/drone_recon.glb", (-13, 20, -1.4)),
                                    ("drone_2", (14.0, 150.0, 0.2), "drones/drone_swarm.glb", (12, 152, -1.2)),
                                    ("drone_3", (-15.0, 250.0, 0.2), "drones/drone_recon.glb", (-17, 252, -1.0)),
                                    ("drone_4", (18.0, 372.0, 0.2), "drones/drone_swarm.glb", (16, 374, -1.4))]:
    C.prop(pid, (x, y, z), model, look=look)
C.group("triggers")
rk.trig(C, "garage", -42, -14, -30, -6, 0, 4)
rk.trig(C, "garage_door", -22, -18, -36, -31, 0, 3)
rk.trig(C, "seg1", -12, 12, 60, 76, 0, 6)
rk.trig(C, "seg2", -12, 12, 150, 166, 0, 6)
rk.trig(C, "seg3", -12, 12, 252, 268, 0, 6)
rk.trig(C, "cityhall", -24, 24, 340, 362, 0, 6)

rk.blackout(C)
C.finish("levels/m6_route.glb", root_props={
    "sky": "#2b3556", "fog": "40,300", "sun": "0.9,0.25,-0.2", "sunColor": "#ffb27a", "sunIntensity": 1.2,
    "ambient": 1.05, "hemiSky": "#6a78a8", "hemiGround": "#3a3038", "timeOfDay": "dawn", "music": "act2_tank",
})
