"""3막 M7 「통신공사」 레벨 (m7_relay): 모나티엄 서쪽 외곽의 전파 시설 세 곳을 하나씩 되찾는다.

npm run model -- art/blender/levels/m7_relay.py   → public/models/levels/m7_relay.glb
npm run shot -- levels/m7_relay.glb --views top,34

[원작] 둠스데이 프로토콜 정전 뒤 R41의 전파 교란기가 무선망을 마비시켰다. 뮤트의 제안으로 코어 AI가 다시 돌고,
       엘레나는 교란기가 추적할 때마다 새 주파수를 만들어 통신망을 되살린다.
[오리지널] 리타의 분대가 서부 외곽의 중계탑(A) → 전파국(B) → 언덕 송신탑(C)을 차례로 되찾는다. 장소, 시설 생김새, 표지.
시간: 흐린 늦은 오후에서 해 질 녘으로 (서쪽의 낮은 회갈색 해, 가로등 꺼짐). 먼 도심의 코어 AI 탑은 아직 꺼져 있다
      (다음 컷신에서 켜진다). HUD가 꺼져 있어 시설은 붉은 항공 장애등이 깜빡이는 높은 철탑과 마젠타 교란기로 읽힌다.
키트: art/blender/lib/radio_site_kit.py (rk), 도시 키트 monatium_city_kit (mk, 읽기만).

배치 (Blender m, +Y 북, +X 동 = 도심 쪽. 길이 약 300 m)
  y -36..262   주거 도로 (x=0, 2차로 + 높인 보도). 양쪽에 2~3층 주택·상가(일부 그을음·잔해). 남쪽 끝은 잔해·차단벽으로 막힘
  y   0        출발 (SPAWN_player, 분대 ALLY_*)
  (34, 82)     A 공원 언덕(높이 5 m) 꼭대기 중계탑 28 m (중계탑 서부 1호 · RELAY W-1), 교란기 JAMMER_a, 전력함
  y 112..172   도로가 4 m 내려간다(순찰로 WP_ab_patrol_01..04, y 150 R41 검문소)
  (12..46.5, 184..228)  B 전파국 구역: 서쪽 정문(y 199..205), 남쪽 철망 틈(x 36..39.5), 북쪽 뒷문(x 38..42),
               발전기 마당(남서), 전파국(1층 장비실 + 2층 본관, 장비실 옥상 테라스와 바깥 계단, 옥상 안테나).
               남쪽 골목(y 177..184)과 동쪽 뒷길(x 46.5..51)로 2차 파상이 돌아 들어온다. 이동식 교란기 JAMMER_b(숨김)
  (72, 300)    C 언덕(높이 18 m, 꼭대기 z=14) 송신탑 26 m + 접시 DISH_c, 제어함, 접시 조정반, 교란기 JAMMER_c.
               접근로 1 = 남서 흙길(전파국 뒷문 → 갈지자), 접근로 2 = 북동 자갈 작업로(동쪽 경계 문 x=136 → 갈지자)
  (430, 285)   도심 코어 AI 탑(원경, 꺼짐) MARK_core, MARK_view_end. 언덕 C에서 동쪽으로 보인다
  경계: 집·담·철망 + 보이지 않는 COL_ 벽 (x=-7, x=7 구간, 공원 둘레, 골목·뒷길 담, y=236·362, x=12·136)

마커 (docs/LEVELS.md, docs/COMBAT.md 2장): 이 파일 끝의 CONTRACT 목록이 미션 m7.ts와의 약속이다.
  SPAWN_player/site_a/road/site_b/site_b_in/site_c, ALLY_rona/sabre/jesty/karen (follow, m4a1)
  TRIG_site_a/b/c, MARK_site_a/b/c, MARK_jammer_a/b/c, MARK_power_a/b/c, MARK_console_b, MARK_dish_c, MARK_core, MARK_view_end
  JAMMER_a/b/c (+ _glow 자식, b는 hidden=1), LIGHT_site_a_01..03 · site_b_01..05 · site_c_01..03 (시안, on=0),
  LIGHT_avia_a_01..03 · avia_b_01 · avia_c_01..03 (적색, on=1, blink=1.2)
  ENEMY_a_01..05, ENEMY_ab_01..04, ENEMY_b_01..06, ENEMY_bw1_01..05, ENEMY_bw2_01..05, ENEMY_c_01..05,
  ENEMY_cw1_01..05, ENEMY_cw2_01..06, COVER_a_*, COVER_ab_*, COVER_b_*, COVER_c_*, WP_ab_patrol_01..04
  CAM_handoff_01..03 + LOOK_handoff_01..03 (A → B → C 복구 장면, 끝은 C 옆)
  추가: DISH_c(접시, alignYaw), FX_smoke_*, PROP_r41_raider(검문소 차량)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import radio_site_kit as rk  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("m7_relay")
REPORT = {}


# ================================================================== terrain
def P(y):
    """도로를 따라 내려가는 바닥 (A 쪽 0 → B 쪽 -4)."""
    return -4.0 * rk.S((y - 112.0) / 60.0)


def E(x):
    """경계 동쪽은 도심 쪽으로 6 m 더 내려간다."""
    return -6.0 * rk.S((x - 140.0) / 80.0)


def hill(x, y, cx, cy, rt, R, h):
    r = math.hypot(x - cx, y - cy)
    return h * rk.S((R - r) / (R - rt))


HA = (34.0, 80.0, 6.0, 26.0, 5.0)        # 공원 언덕 (꼭대기 z 5, 평평한 반지름 6)
HC = (72.0, 300.0, 12.0, 56.0, 18.0)     # 송신 언덕 (꼭대기 z 14, 평평한 반지름 12)
BOX_A = (HA[0] - HA[3], HA[0] + HA[3], HA[1] - HA[3], HA[1] + HA[3])     # 8..60, 54..106
BOX_C = (HC[0] - HC[3], HC[0] + HC[3], HC[1] - HC[3], HC[1] + HC[3])     # 16..128, 244..356


def Gf(x, y):
    return P(y) + E(x) + hill(x, y, *HA) + hill(x, y, *HC)


def in_box(b, x, y):
    return b[0] < x < b[1] and b[2] < y < b[3]


G = rk.Ground(Gf)
C.group("ground")
XS = [-900, -500, -260, -140, -70, -36, -20, -8, 8, 16, 34, 60, 100, 128, 136, 140] + \
     list(range(150, 221, 10)) + [260, 330, 420, 520, 650, 900]
YS = [-900, -500, -260, -140, -70, -36, 0, 30, 54, 80, 106] + list(range(112, 173, 4)) + \
     [200, 236, 244, 272, 300, 328, 356, 380, 450, 560, 700, 900]
G.patch(C, "base", XS, YS, key="turf", skip=lambda x, y: in_box(BOX_A, x, y) or in_box(BOX_C, x, y))
G.patch(C, "hill_a", [BOX_A[0] + (BOX_A[1] - BOX_A[0]) * i / 20 for i in range(21)],
        [BOX_A[2] + (BOX_A[3] - BOX_A[2]) * i / 20 for i in range(21)], key="turf")
G.patch(C, "hill_c", [BOX_C[0] + (BOX_C[1] - BOX_C[0]) * i / 28 for i in range(29)],
        [BOX_C[2] + (BOX_C[3] - BOX_C[2]) * i / 28 for i in range(29)], key="turf")


def gz(x, y, dz=0.0):
    return G.h(x, y) + dz


def on(x, y, dz=0.0):
    return (x, y, round(G.h(x, y) + dz, 4))


WALK = 0.15          # 보도 높이


def on_walk(x, y):
    return (x, y, round(G.h(x, y) + WALK, 4))


# ================================================================== markers helpers
def mark(name, loc, **kw):
    C.marker(name, loc, **kw)
    REPORT[name] = tuple(round(v, 2) for v in loc)


def enemy(eid, loc, face, kind, group, behavior, spawn="start", path=None):
    props = {"kind": kind, "group": group, "behavior": behavior,
             "weapon": "r41_sidearm" if kind == "officer" else "r41_carbine", "drop": "r41_carbine", "spawn": spawn}
    if path:
        props["path"] = path
    mark(f"ENEMY_{eid}", loc, face=face, props=props)


def cover(cid, loc, face, height="low", side="any"):
    mark(f"COVER_{cid}", loc, face=face, props={"height": height, "side": side})


def behind(wall_pt, yaw, d=0.75):
    """모래주머니 벽(정면 -Y = yaw) 뒤쪽 d m 지점."""
    a = math.radians(yaw)
    f = Vector((math.sin(a), -math.cos(a)))
    return Vector((wall_pt[0], wall_pt[1])) - f * d, Vector((wall_pt[0], wall_pt[1])) + f * 6


def bags(x, y, z, yaw, n=4, rows=3):
    rk.sandbags(C, x, y, z, yaw=yaw, n=n, rows=rows)
    return behind((x, y), yaw)


# ================================================================== street (x = 0)
C.group("street")
ST = rk.street_y(C, G, 0.0, -36.0, 300.0, YS, lanes=2, crossings=(4.0, 66.0, 202.0))

# 서쪽 집 줄 (정면 +x), 동쪽 집 줄 (정면 -x)
WEST = [(-36, -22, 2, "apartment", None), (-20, -6, 1, "brick", {"name": "모나티엄 25", "sub": "서부점", "awning": "mint"}),
        (-4, 8, 1, "apartment", None), (10, 24, 1, "office", None), (26, 40, 2, "apartment", None),
        (42, 58, 1, "apartment", None), (60, 72, 1, "brick", {"name": "빵집", "sub": "BAKERY", "awning": "coral"}),
        (74, 90, 2, "apartment", None), (92, 106, 1, "office", None), (108, 122, 1, "apartment", None),
        (124, 138, 1, "brick", None), (140, 154, 1, "apartment", None), (156, 170, 1, "office", None),
        (172, 186, 2, "apartment", None), (188, 202, 1, "brick", None), (204, 218, 1, "apartment", None),
        (220, 234, 2, "office", None), (236, 250, 1, "apartment", None), (252, 268, 1, "warm", None)]
EAST = [(-36, -20, 1, "apartment", None), (-18, -4, 1, "brick", {"name": "커틀릿 하우스", "sub": "공기커틀릿 아님", "awning": "coral"}),
        (-2, 12, 2, "apartment", None), (14, 28, 1, "office", None), (30, 48, 1, "apartment", None),
        (112, 126, 1, "office", None), (128, 142, 1, "apartment", None), (144, 158, 1, "brick", None),
        (160, 177, 2, "office", None)]
mk.STYLES.setdefault("warm", ("warm", "warm_d", "glass", "glass_d", "warm_d"))
RUIN = {3, 7, 11, 15}           # 그을음·잔해를 더할 집 (WEST 순번)


def soot(x, y, z, normal, s=1.0, seed=0):
    rng = random.Random(seed)
    pts = [(math.cos(2 * math.pi * i / 9) * s * rng.uniform(0.7, 1.2) * 1.3,
            math.sin(2 * math.pi * i / 9) * s * rng.uniform(0.7, 1.2) + s * 0.5) for i in range(9)]
    C.decal("soot", pts, (x, y, z), normal, lift=0.05)


def row(side, items, x_in, x_out):
    for i, (y0, y1, fl, st, shop) in enumerate(items):
        x0, x1 = sorted((x_in, x_out))
        flat = abs(G.h(0, y0) - G.h(0, y1)) < 0.05
        bz = G.hmin(x0, x1, y0, y1) - 0.12
        front = "+x" if side < 0 else "-x"
        b = mk.building(C, x0, x1, y0, y1, floors=fl, style=st, front=front, sides=front, seed=40 + i * 7 + side,
                        shop=shop if flat else None, door=flat, z=bz, cctv=flat and i % 3 == 0, r=0.8, col=False)
        rk.building_col(C, x0, x1, y0, y1, bz, b["top"], r=0.8)      # 둥근 모서리까지 맞춘 볼록 COL
        if side < 0 and i in RUIN:
            fx = x1 + 0.0
            soot(fx, (y0 + y1) / 2 + 2, bz + 4.2, (1, 0, 0), 1.4, seed=i)
            rk.rubble(C, x1 + 0.8, (y0 + y1) / 2 - 2.5, G.h(x1 + 0.8, (y0 + y1) / 2 - 2.5), r=1.5, seed=i)
        # 경계: 집 정면 0.12 m 앞(문틀 판 두께)까지, 둥근 모서리(r 0.8)는 빼고. 집 몸통은 건물 COL
        fx0, fx1 = sorted((x_in, x_in + (0.12 if side < 0 else -0.12)))
        zl = min(G.hmin(fx0, fx1, y0, min(y1, 262.0)), -4.0) - 2.0
        if y0 < 262.0:
            C.col(fx0, fx1, y0 + 0.8, min(y1 - 0.8, 262.0), zl, zl + 26.0)
        # 집 사이 담 (틈 가리기): 담 자체가 경계 (보이지 않는 벽을 담 앞에 두지 않는다)
        if i + 1 < len(items):
            ny0 = items[i + 1][0]
            if ny0 - y1 > 0.3:
                wx = x_in + (-0.4 if side < 0 else 0.4)
                wz = G.hmin(wx - 0.2, wx + 0.2, y1, ny0) - 0.2
                C.box("concrete_d", wx - 0.15, wx + 0.15, y1, ny0, wz, G.h(wx, y1) + 1.8, kind="detail")
                if y1 < 262.0:
                    C.col(wx - 0.15, wx + 0.15, y1, ny0, wz, zl + 26.0)


row(-1, WEST, -7.2, -19.0)
row(1, EAST[:5], 7.2, 19.0)
row(1, EAST[5:], 7.2, 22.0)

# 가로등(꺼짐), 전봇대 + 전선, 가로수
for k, y in enumerate(range(-30, 262, 26)):
    mk.lamp(C, 5.4, y, z=gz(5.4, y, WALK))
prev = None
for y in range(-32, 262, 30):
    pts = rk.utility_pole(C, -5.5, y, gz(-5.5, y, WALK), h=7.2)
    if prev:
        rk.wires(C, prev, pts, sag=0.7)
    prev = pts
for (x, y) in ((-6.6, 25), (6.6, 4), (-6.6, 59), (6.6, 118), (-6.6, 139), (6.6, 150), (-6.6, 187)):
    mk.tree(C, x, y, h=4.4, seed=int(y), z=gz(x, y), lod=1)
for (x, y, ko, en) in ((-5.6, 64.0, "서부공원길", "WEST PARK RD"), (5.6, 200.0, "전파국길", "RADIO STN RD")):
    mk.street_sign(C, x, y, ko, en, yaw=90 if x > 0 else -90, z=gz(x, y, WALK))

# 길 위: 폐차·주차 차
rk.car(C, -1.1, 64.0, gz(-1.1, 64.0), yaw=24, wreck=True, seed=1)
rk.car(C, 1.7, 21.0, gz(1.7, 21.0), yaw=182, key="car_b", seed=2)
rk.car(C, -1.6, 41.0, gz(-1.6, 41.0), yaw=-12, wreck=True, seed=3)
rk.car(C, 1.6, 128.0, gz(1.6, 128.0), yaw=176, key="car_w", seed=4)
rk.car(C, -1.7, 197.0, gz(-1.7, 197.0), yaw=160, wreck=True, seed=5)
mk.scorch(C, -1.0, 64.0, 2.4, z=gz(-1.0, 64.0) + 0.03, seed=2)
mk.scorch(C, -1.6, 41.0, 2.0, z=gz(-1.6, 41.0) + 0.03, seed=3)

# 남쪽 끝 막힘 (잔해 + 차단벽), 북쪽 끝 막힘
for (x, s) in ((-4.0, 2.0), (-0.5, 2.4), (3.4, 2.1)):
    rk.rubble(C, x, -33.5, gz(x, -33.5), r=s, seed=int(x * 10) + 50)
rk.r41_barrier(C, 0.0, -31.0, gz(0, -31.0), yaw=180)
for (x, s) in ((-3.6, 2.2), (0.4, 2.0), (4.2, 1.8)):
    rk.rubble(C, x, 259.0, gz(x, 259.0), r=s, seed=int(x * 10) + 70)
rk.r41_barrier(C, -1.5, 256.5, gz(-1.5, 256.5), yaw=0)
rk.r41_barrier(C, 2.0, 256.8, gz(2.0, 256.8), yaw=0)

# ================================================================== A: 공원 언덕 + 중계탑
C.group("site_a")
# 공원 울타리 (길 쪽, 입구 두 곳) + 둘레 생울타리
for (y0, y1) in ((52.5, 66.0), (74.0, 100.0), (107.0, 111.5)):
    mk.fence(C, (7.4, y0), (7.4, y1), z=0.0)                 # 충돌은 키트의 난간 COL
for (x0, x1, y0, y1) in ((8.0, 63.5, 52.6, 53.6), (62.8, 63.8, 53.6, 110.6), (8.0, 63.5, 110.6, 111.6)):
    zb = G.hmin(x0, x1, y0, y1) - 0.1
    C.box("hedge", x0, x1, y0, y1, zb, zb + 1.5, kind="main")
mk.planter(C, 8.3, 10.9, 63.0, 64.4, z=gz(9.6, 63.7) - 0.05)
mk.planter(C, 8.3, 10.9, 75.6, 77.0, z=gz(9.6, 76.3) - 0.05)
# 공원 표지
L = rk.Local((8.4, 66.6, gz(8.4, 66.6)), -90)
L.cyl(C, "dark", (0, 0, 0), (0, 0, 2.1), 0.05, segs=6, kind="detail")
L.col(C, -0.07, 0.07, -0.07, 0.07, 0.0, 2.1)                # 표지 기둥
L.plate(C, "navy", mk.hw.rrect(1.8, 0.6, 0.12, 2), (0, -0.06, 1.75), (0, -1, 0), 0.05)
L.text(C, "white", "모나티엄 서부공원", 0.17, (0, -0.115, 1.82), (0, -1, 0), lift=0.004)
L.text(C, "glow_off", "MONATIUM WEST PARK", 0.09, (0, -0.115, 1.63), (0, -1, 0), lift=0.004)
# 공원길
rk.drape(C, "pave", [(7.0, 70.0), (14.0, 70.6), (20.5, 73.4), (25.5, 77.0), (30.4, 79.6)], 2.2, G, fillet=3.0)
rk.drape(C, "pave", [(7.0, 103.5), (14.0, 101.5), (21.0, 95.5), (26.5, 89.0), (31.0, 85.4)], 2.0, G, fillet=3.0)
rk.drape(C, "pave_d", [(20.5, 73.4), (24.0, 66.0), (34.0, 60.5), (46.0, 64.0), (53.0, 74.0)], 1.6, G, fillet=4.0)
# 기단 + 중계탑
MAST_A = Vector((34.0, 82.0, 5.12))
C.box("conc", 30.0, 38.0, 77.0, 85.0, 4.2, 5.12, col=True)
C.box("conc_d", 29.9, 38.1, 76.9, 85.1, 5.05, 5.13, kind="detail")
mast_a = rk.lattice_mast(C, MAST_A, h=28.0, w0=2.4, w1=0.7, legs=3, yaw=-90, lid="site_a", avia="avia_a",
                         n_avia=3, sign=("중계탑 서부 1호", "RELAY W-1"))
cab_a = rk.breaker_cabinet(C, (31.1, 78.6, 5.12), yaw=-90, label=("전력함 A-1", "POWER A-1"))
leg_a = min(mast_a["legs"], key=lambda p: (p - Vector((37.0, 78.0, 5.12))).length)
jam_a = rk.jammer(C, "a", (36.7, 78.7, 5.12), yaw=rk.face_yaw((36.7, 78.7), (20.0, 70.0)), cable_to=leg_a)
rk.cable(C, [Vector((31.1, 78.9, 5.14)), Vector((32.4, 80.6, 5.14)), Vector(mast_a["legs"][0]) + Vector((0, 0, 0.4))])
# R41 진지 (서쪽·남쪽 비탈) + 보급 상자
SB_A = []
for ang in (178, 214, 250, 146):
    a = math.radians(ang)
    px, py = HA[0] + math.cos(a) * 9.5, HA[1] + math.sin(a) * 9.5
    yaw = math.degrees(math.atan2(px - HA[0], -(py - HA[1])))
    SB_A.append((bags(px, py, gz(px, py) - 0.05, yaw), (px, py), yaw))
rk.r41_crate(C, 37.3, 84.0, 5.12, yaw=12, stack=2)
rk.r41_crate(C, 39.4, 75.2, gz(39.4, 75.2), yaw=-20)
# 공원 나무·벤치·가로등
for i, (x, y) in enumerate(((14, 59), (20, 57.5), (47, 59), (55, 67), (57, 80), (53, 93), (45, 101), (15, 91),
                            (12, 83), (41, 67.5), (22, 106), (51, 105), (25.5, 59.5), (48, 86), (18, 98), (58, 100))):
    mk.tree(C, x, y, h=5.0, seed=100 + i, z=gz(x, y) - 0.05, lod=1)
for (x, y, yaw) in ((17.0, 68.8, 180), (23.4, 71.4, 150), (18.0, 103.3, 20)):
    mk.bench(C, x, y, yaw=yaw, z=gz(x, y))
for (x, y) in ((12.0, 69.0), (22.5, 77.0), (17.5, 99.5)):
    mk.lamp(C, x, y, z=gz(x, y))
mk.trash_bin(C, 13.0, 72.2, z=gz(13.0, 72.2))

# ================================================================== A → B 도로: R41 검문소
C.group("road")
rk.r41_barrier(C, -1.5, 150.0, gz(-1.5, 150.0), yaw=0)
rk.r41_barrier(C, 1.7, 151.6, gz(1.7, 151.6), yaw=0)
ab_bag = bags(-4.4, 149.2, gz(-4.4, 149.2, WALK) - 0.03, 0)
rk.r41_crate(C, 4.4, 152.0, gz(4.4, 152.0, WALK), yaw=8)
rk.r41_barrier(C, 4.3, 148.6, gz(4.3, 148.6, WALK), yaw=0, w=1.4)
y_r = 162.0
C.marker("PROP_r41_raider", on(1.4, y_r), look=(1.4, y_r - 4.0, gz(1.4, y_r - 4.0)),
         props={"model": "vehicles/r41/r41_raider.glb"})
REPORT["PROP_r41_raider"] = on(1.4, y_r)

# ================================================================== B: 전파국 구역
C.group("site_b")
ZB = -3.95
mk.paving(C, 12.0, 46.5, 184.0, 228.0, z=ZB, key="conc", grout="conc_d", tile=3.0, t=0.45)
mk.paving(C, 6.1, 12.0, 199.0, 205.0, z=ZB, key="conc", grout=None, t=0.45)           # 정문 앞
rk.chain_fence(C, (12.0, 184.0), (12.0, 228.0), z0=ZB, gaps=[(15.0, 21.0)])
rk.chain_fence(C, (12.0, 184.0), (46.5, 184.0), z0=ZB, gaps=[(24.0, 27.5)])
rk.chain_fence(C, (46.5, 184.0), (46.5, 228.0), z0=ZB)
rk.chain_fence(C, (12.0, 228.0), (46.5, 228.0), z0=ZB, gaps=[(26.0, 30.0)])
rk.fence_gate(C, (12.0, 199.0, ZB), yaw=90, w=3.0, swing=-72)
rk.fence_gate(C, (12.0, 205.0, ZB), yaw=-90, w=3.0, swing=64)
rk.fence_gate(C, (38.0, 228.0, ZB), yaw=0, w=4.0, swing=-84)
# 부서진 철망 조각 (남쪽 틈)
C.poly("mesh_a", [(36.2, 183.2, ZB + 0.02), (39.0, 182.6, ZB + 0.02), (39.4, 183.6, ZB + 0.5), (36.4, 184.0, ZB + 0.9)])
# 정문 기둥 + 표지
for y in (198.8, 205.2):
    C.box("navy", 11.7, 12.3, y - 0.3, y + 0.3, ZB, ZB + 2.3, col=True)
    C.box("gold", 11.65, 12.35, y - 0.35, y + 0.35, ZB + 2.3, ZB + 2.42, kind="detail")
L = rk.Local((11.66, 196.9, ZB), -90)
L.plate(C, "navy", mk.hw.rrect(2.6, 0.9, 0.15, 2), (0, 0.0, 1.7), (0, -1, 0), 0.06)
L.text(C, "white", "모나티엄 전파국 서부분국", 0.16, (0, -0.07, 1.82), (0, -1, 0), lift=0.004)
L.text(C, "glow_off", "MONATIUM RADIO · WEST", 0.1, (0, -0.07, 1.6), (0, -1, 0), lift=0.004)
L.cyl(C, "galv", (0, 0.05, 0), (0, 0.05, 1.3), 0.05, segs=6, kind="detail")
L.col(C, -0.07, 0.07, -0.02, 0.12, 0.0, 1.3)                # 표지 기둥 (판 밑은 지나간다)
L = rk.Local((11.9, 210.0, ZB), -90)
L.plate(C, "white", mk.hw.rrect(1.5, 0.5, 0.06, 1), (0, -0.1, 1.3), (0, -1, 0), 0.03)
L.text(C, "red", "관계자 외 출입 금지", 0.1, (0, -0.135, 1.36), (0, -1, 0), lift=0.004)
L.text(C, "dark", "AUTHORIZED ONLY", 0.07, (0, -0.135, 1.2), (0, -1, 0), lift=0.004)
# 전파국
stn = rk.radio_station(C, (31.0, 215.0, ZB), yaw=-90, lid="site_b", avia="avia_b",
                       name=("모나티엄 전파국", "MONATIUM RADIO"))
# 발전기 마당
C.box("conc_d", 15.0, 28.0, 186.5, 192.5, ZB - 0.2, ZB + 0.04, kind="detail")
gen = rk.generator(C, (18.6, 189.4, ZB + 0.04), yaw=180)
rk.fuel_tank(C, (25.2, 188.6, ZB + 0.04), yaw=0)
rk.cable(C, [Vector((18.6, 188.6, ZB + 0.07)), Vector((18.6, 187.2, ZB + 0.07)), Vector((13.4, 187.2, ZB + 0.07)),
             Vector((13.4, 207.2, ZB + 0.03)), Vector((22.6, 207.2, ZB + 0.03)), Vector((22.75, 208.6, ZB + 0.03)),
             Vector((22.75, 208.6, ZB + 2.5))])
for (x, y) in ((22.7, 209.4), (22.7, 220.6)):
    mk.trash_bin(C, x - 0.6, y, z=ZB)
# 이동식 교란기 자리 (처음에 숨김)
jam_b = rk.jammer(C, "b", (43.6, 188.4, ZB), yaw=rk.face_yaw((43.6, 188.4), (30.0, 197.0)), mount="cart",
                  hidden=True)
# R41 진지 (정문 안쪽 모래주머니, 마당 상자)
SB_B1 = bags(14.7, 197.2, ZB, -90)
SB_B2 = bags(14.7, 206.9, ZB, -90)
rk.r41_crate(C, 21.2, 201.0, ZB, yaw=8, stack=2)
rk.r41_crate(C, 27.5, 195.0, ZB, yaw=-14)
rk.r41_crate(C, 40.0, 200.5, ZB, yaw=30)
rk.r41_barrier(C, 9.0, 211.5, gz(9.0, 211.5), yaw=-90)
rk.r41_barrier(C, 33.5, 189.6, ZB, yaw=0, w=1.6)
# 마당 나무, 투광등 기둥(꺼짐)
for (x, y) in ((14.5, 225.0), (20.0, 225.5), (44.5, 225.0)):
    mk.tree(C, x, y, h=4.2, seed=int(x), z=ZB, lod=1)
mk.lamp(C, 45.2, 192.0, z=ZB, h=4.6)
mk.lamp(C, 13.2, 214.0, z=ZB, h=4.6)
# 남쪽 골목·동쪽 뒷길 담 + 잡동사니
C.box("brick", 21.6, 51.2, 176.6, 177.0, -4.3, -1.6, col=True)
C.box("brick", 51.0, 51.4, 177.0, 236.0, -4.3, -1.6, col=True)
for (x, y, yaw) in ((30.0, 179.0, 0), (48.8, 205.0, 90)):
    L = rk.Local((x, y, -4.0), yaw)
    L.box(C, "teal", -0.9, 0.9, -0.55, 0.55, 0.0, 1.1, col=True)
    L.box(C, "dark", -0.95, 0.95, -0.6, 0.6, 1.1, 1.2, kind="detail")
rk.r41_crate(C, 41.0, 180.0, -4.0, yaw=10)
rk.rubble(C, 48.6, 214.0, -4.0, r=1.3, seed=21)

# ================================================================== C: 송신 언덕
C.group("site_c")
ZC = 14.12
TC = Vector((72.0, 301.5, ZC))
oc = [(64.0, 295.0), (67.0, 292.0), (77.0, 292.0), (80.0, 295.0), (80.0, 305.0), (77.0, 308.0), (67.0, 308.0),
      (64.0, 305.0)]
C.prism("conc", oc, 12.4, ZC, bottom=False)
C.col(64.0, 80.0, 295.0, 305.0, 12.4, ZC)
C.col(67.0, 77.0, 292.0, 308.0, 12.4, ZC)
for (x0, x1, y0, y1) in ((65.5, 67.0, 293.5, 295.0), (77.0, 78.5, 293.5, 295.0), (65.5, 67.0, 305.0, 306.5),
                         (77.0, 78.5, 305.0, 306.5)):
    C.col(x0, x1, y0, y1, 12.4, ZC)                          # 모따기 모서리 (대략)
C.ring_prism("conc_d", [(x + (0.06 if x > 72 else -0.06), y + (0.06 if y > 300 else -0.06)) for x, y in oc],
             [(x + (-0.3 if x > 72 else 0.3), y + (-0.3 if y > 300 else 0.3)) for x, y in oc], ZC - 0.02, ZC + 0.03,
             kind="detail")
CORE = Vector((430.0, 285.0, Gf(430.0, 285.0)))
tow = rk.lattice_mast(C, TC, h=26.0, w0=3.4, w1=1.2, legs=4, yaw=rk.face_yaw((72.0, 301.5), (62.0, 289.0)),
                      lid="site_c", avia="avia_c", n_avia=3, sign=("서부 송신소 2호탑", "WEST TX-2"), bands=7)
zd = 11.5
d_city = (Vector((CORE.x, CORE.y, 0)) - Vector((TC.x, TC.y, 0))).normalized()
legs_d = [tow["leg_at"](k, zd) for k in range(4)]
leg_d = max(legs_d, key=lambda p: (p - TC).dot(d_city))
mount = Vector((TC.x, TC.y, TC.z + zd)) + d_city * 2.9
align = rk.face_yaw(mount, CORE)
rk.dish(C, "c", mount, yaw=align + 52.0, align_yaw=align, diameter=3.0, arm=leg_d)
box_c = rk.control_box(C, (73.6, 297.2, ZC), yaw=0)
dctl = rk.dish_control(C, (77.4, 296.6, ZC), yaw=0)
legs_c = tow["legs"]
leg_j = min(legs_c, key=lambda p: (p - Vector((67.0, 298.0, ZC))).length)
jam_c = rk.jammer(C, "c", (66.9, 297.6, ZC), yaw=rk.face_yaw((66.9, 297.6), (60.0, 288.0)), cable_to=leg_j)
rk.cable(C, [Vector((73.6, 297.8, ZC + 0.03)), Vector((73.0, 299.0, ZC + 0.03)), Vector(legs_c[0]) + Vector((0, 0, 0.4))])
rk.cable(C, [Vector((77.0, 296.9, ZC + 0.03)), Vector((74.6, 297.2, ZC + 0.03))])
# 언덕 꼭대기 진지 (모래주머니 둘레, 남서·북동 길목은 비움)
SB_C = []
for (x, y, yaw) in ((69.2, 292.9, 0), (75.6, 292.9, 0), (64.9, 300.4, -90), (64.9, 304.0, -90), (71.0, 307.2, 180),
                    (79.2, 297.4, 90), (79.2, 302.4, 90)):
    SB_C.append((bags(x, y, ZC, yaw), (x, y), yaw))
rk.r41_crate(C, 76.6, 304.6, ZC, yaw=20, stack=2)
rk.r41_crate(C, 68.0, 305.6, ZC, yaw=-10)
# 접근로
PATH1 = [(40.0, 228.6), (51.0, 239.5), (65.6, 254.4), (49.3, 274.7), (67.0, 276.5), (63.0, 289.3), (65.4, 293.4)]
PATH2 = [(140.0, 322.0), (104.0, 340.0), (80.0, 345.0), (102.0, 318.0), (82.0, 322.0), (78.0, 309.6)]
rk.drape(C, "dirt", PATH1, 2.2, G, fillet=4.0, lift=0.07)
rk.drape(C, "gravel", PATH2, 3.0, G, fillet=5.0, lift=0.07)
rk.drape(C, "dirt", [(6.2, 246.0), (24.0, 242.0), (40.0, 241.0), (51.0, 239.5)], 1.8, G, fillet=4.0, lift=0.07)


def seg_dist(p, a, b):
    p, a, b = Vector(p), Vector(a), Vector(b)
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (a + ab * t - p).length


def near_path(x, y, d):
    for path in (PATH1, PATH2):
        for a, b in zip(path, path[1:]):
            if seg_dist((x, y), a, b) < d:
                return True
    return False


rng = random.Random(77)
n_tree = 0
tries = 0
while n_tree < 26 and tries < 600:
    tries += 1
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(17, 54)
    x, y = HC[0] + math.cos(a) * r, HC[1] + math.sin(a) * r
    if not (15 < x < 132 and 240 < y < 358) or near_path(x, y, 4.5):
        continue
    if abs(math.degrees(a + math.pi) % 360 - 180) < 42:      # 동쪽(도심 쪽) 시야는 비운다
        continue
    mk.tree(C, x, y, h=rng.uniform(4.6, 6.4), seed=200 + n_tree, z=gz(x, y) - 0.1, lod=1)
    n_tree += 1
for i, (x, y) in enumerate(((22.0, 330.0), (30.0, 346.0), (20.0, 300.0), (40.0, 354.0), (118.0, 352.0),
                            (126.0, 344.0), (122.0, 250.0), (108.0, 244.0), (24.0, 276.0), (40.0, 330.0))):
    mk.tree(C, x, y, h=5.6 + (i % 3) * 0.6, seed=300 + i, z=gz(x, y) - 0.1, lod=1)
ROCKS = [(58.0, 268.0, 1.4), (84.0, 284.0, 1.2), (92.0, 296.0, 1.6), (56.0, 300.0, 1.3), (88.0, 330.0, 1.2),
         (74.0, 262.0, 1.5), (60.0, 284.0, 1.0)]
for i, (x, y, s) in enumerate(ROCKS):
    z = gz(x, y)
    mk.rock(C, x, y, s=s, z=z - 0.2 * s, seed=i)               # 충돌은 키트의 바위 COL
# 경계 철망 (보호구역) + 북동 작업로 문
PF = dict(z0=-4.0, h=1.8, pitch=3.6, wire=False, mid=False)
rk.chain_fence(C, (51.4, 236.0), (136.0, 236.0), **PF)
rk.chain_fence(C, (136.0, 236.0), (136.0, 362.0), gaps=[(83.0, 89.0)], **PF)
rk.chain_fence(C, (12.0, 362.0), (136.0, 362.0), **PF)
rk.chain_fence(C, (12.0, 262.0), (12.0, 362.0), **PF)
L = rk.Local((135.4, 317.2, -4.0), 90)
L.plate(C, "white", mk.hw.rrect(1.6, 0.55, 0.06, 1), (0, 0.04, 1.2), (0, 1, 0), 0.03)
L.text(C, "red", "송신소 보호구역", 0.11, (0, 0.08, 1.27), (0, 1, 0), lift=0.004)
L.text(C, "dark", "WEST TX · RESTRICTED", 0.07, (0, 0.08, 1.1), (0, 1, 0), lift=0.004)
L.col(C, -0.82, 0.82, -0.01, 0.1, 0.9, 1.5)                 # 떠 있는 판 (밑은 몸보다 낮아 못 지나간다)

# ================================================================== 경계 COL (보이지 않는 벽)
C.group("bounds")
# 집 줄 앞 벽은 row()에서 집마다 정면 0.12 m 앞 띠 + 집 사이 담. 공원 둘레는 생울타리(1 m 두께) 자체가 벽. 언덕 철망 둘레는 철망 COL(±0.08)과 거의 같은 두께
for (x0, x1, y0, y1) in ((7.08, 7.7, 48.0, 52.6),          # 동쪽 집 줄 끝 ~ 공원 (골목 막음)
                         (7.3, 63.8, 52.6, 53.6),          # 공원 남 (생울타리)
                         (62.8, 63.8, 52.6, 111.6),        # 공원 동 (생울타리)
                         (7.3, 63.8, 110.6, 111.6),        # 공원 북 (생울타리)
                         (-7.7, 7.7, -36.6, -36.0),        # 남쪽 끝
                         (-7.7, 12.4, 262.0, 262.6),       # 북쪽 끝 (길)
                         (11.9, 12.1, 262.0, 362.0),       # 언덕 서
                         (12.0, 136.0, 361.9, 362.1),      # 언덕 북
                         (135.9, 136.1, 236.0, 319.0),     # 언덕 동 (남)
                         (135.9, 136.1, 325.0, 362.0),     # 언덕 동 (북)
                         (51.2, 136.0, 235.9, 236.1)):     # 언덕 남동
    zl = min(G.hmin(x0, x1, y0, y1), -4.0) - 2.0
    C.col(x0, x1, y0, y1, zl, zl + 26.0)
for (x0, x1, y0, y1) in ((136.0, 141.0, 318.6, 319.0), (136.0, 141.0, 325.0, 325.4), (140.6, 141.0, 319.0, 325.0)):
    C.col(x0, x1, y0, y1, -12.0, 14.0)                      # 작업로 문 밖 (막힌 주머니)

# ================================================================== 외곽 · 원경
# 원경 빌딩 상자 (그리기는 아래 skyline 그룹). 먼저 정해 두고 외곽 집이 그 속이나 벽에 붙어 나지 않게 한다
# (집 벽이 빌딩 벽과 몇 mm 차로 한 평면에 겹치면 먼 거리에서 깜빡인다)
SKY = []
rng = random.Random(31)
for i in range(52):
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(26, 170)
    x, y = CORE.x + math.cos(a) * r * 0.8, CORE.y + math.sin(a) * r * 1.2
    if x < 335:
        continue
    w, d = rng.uniform(14, 26), rng.uniform(14, 24)
    h = rng.uniform(20, 58) * (1.15 - r / 300)
    z0 = Gf(x, y) - 1.0
    SKY.append((x - w / 2, x + w / 2, y - d / 2, y + d / 2, z0, z0 + h, ("far", "far_d", "concrete_d")[i % 3],
                "far_d" if i % 3 != 1 else "far"))
for i in range(26):
    x, y = rng.uniform(250, 340), rng.uniform(140, 440)
    w, d, h = rng.uniform(12, 20), rng.uniform(10, 18), rng.uniform(9, 20)
    z0 = Gf(x, y) - 1.0
    SKY.append((x - w / 2, x + w / 2, y - d / 2, y + d / 2, z0, z0 + h, "far", "far_d"))



def sky_clash(x0, x1, y0, y1):
    """외곽 집이 원경 빌딩 속에 완전히 들거나(안 보임), 벽이 빌딩 벽과 5 cm 안쪽 차로 겹치면(깜빡임) True."""
    for b in SKY:
        if not (x0 < b[1] and x1 > b[0] and y0 < b[3] and y1 > b[2]):
            continue
        if x0 >= b[0] and x1 <= b[1] and y0 >= b[2] and y1 <= b[3]:
            return True
        if min(abs(u - v) for u in (x0, x1) for v in (b[0], b[1])) < 0.05 or \
                min(abs(u - v) for u in (y0, y1) for v in (b[2], b[3])) < 0.05:
            return True
    return False


C.group("outskirts")
rng = random.Random(9)


def scatter_houses(x0, x1, y0, y1, step, jitter=2.0, avoid=None):
    for x in range(int(x0), int(x1), step):
        for y in range(int(y0), int(y1), step):
            xx, yy = x + rng.uniform(-jitter, jitter), y + rng.uniform(-jitter, jitter)
            if avoid and avoid(xx, yy):
                continue
            w, d = rng.uniform(7, 11), rng.uniform(6, 9)
            h = rng.uniform(4.6, 8.4)
            axis = "x" if rng.random() < 0.5 else "y"
            wall = ("warm", "concrete", "brick", "warm_d")[rng.randint(0, 3)]
            roof = ("roof", "navy_l", "coral")[rng.randint(0, 2)]
            if sky_clash(xx - w / 2, xx + w / 2, yy - d / 2, yy + d / 2):
                continue                                     # 난수는 다 뽑은 뒤 빼서 다른 집은 그대로
            zh = G.hmin(xx - w / 2, xx + w / 2, yy - d / 2, yy + d / 2, n=1)
            rk.lod_house(C, xx, yy, zh, w=w, d=d, h=h, axis=axis, wall=wall, roof=roof)
            if xx - w / 2 < 63.8 and xx + w / 2 > 7.3 and yy - d / 2 < 111.6 and yy + d / 2 > 52.6:
                C.col(xx - w / 2, xx + w / 2, yy - d / 2, yy + d / 2, zh - 0.5, zh + h)   # 공원 생울타리 안으로 나온 집


scatter_houses(-72, -26, -100, 300, 14)                      # 서쪽 뒷줄
scatter_houses(-24, 130, -110, -44, 15)                      # 남쪽
scatter_houses(24, 130, -40, 50, 15, avoid=lambda x, y: x < 30 and y > -40)
scatter_houses(70, 130, 56, 110, 15)                         # 공원 동쪽
scatter_houses(30, 130, 116, 166, 15)                        # 도로 동쪽 뒤
scatter_houses(60, 130, 182, 230, 15)                        # 뒷길 동쪽
scatter_houses(150, 330, 150, 430, 18, jitter=3.0)           # 경계 밖 동쪽 (내리막)
scatter_houses(-30, -12, 270, 360, 14)                         # 언덕 서쪽
for i in range(70):
    x, y = rng.uniform(-20, 170), rng.uniform(368, 450)
    mk.lod_tree(C, x, y, h=rng.uniform(8, 13), r=rng.uniform(2.6, 4.2), z=Gf(x, y) - 0.3,
                key=("leaf", "leaf_d", "leaf_l")[i % 3], rot=rng.uniform(0, 1), kind="far")
for i in range(40):
    x, y = rng.uniform(140, 200), rng.uniform(240, 360)
    mk.lod_tree(C, x, y, h=rng.uniform(7, 11), r=rng.uniform(2.4, 3.6), z=Gf(x, y) - 0.3,
                key=("leaf", "leaf_d")[i % 2], rot=rng.uniform(0, 1), kind="far")

C.group("skyline")
for (x0, x1, y0, y1, z0, z1, key, win_key) in SKY:
    rk.far_block(C, x0, x1, y0, y1, z0, z1, key=key, win_key=win_key, faces=("-x",))
rk.core_far(C, CORE.x, CORE.y, CORE.z, h=72.0, lit=False, r0=10.0)
for (x, y, h, s) in ((318.0, 196.0, 70.0, 1), (372.0, 392.0, 85.0, 2), (505.0, 238.0, 95.0, 3)):
    mk.smoke_column(C, x, y, z=Gf(x, y), h=h, r=6.0, drift=(0.28, 0.08), seed=s)

# ================================================================== 마커
C.group("markers")
# 출발 + 분대
mark("SPAWN_player", on(-0.9, -2.0), face=(-0.9, 30.0))
for (who, x, y) in (("rona", -2.2, 0.6), ("sabre", 1.2, 0.0), ("jesty", -2.3, -3.6), ("karen", 1.5, -4.2)):
    mark(f"ALLY_{who}", on(x, y), face=(x, 30.0), props={"who": who, "behavior": "follow", "weapon": "m4a1"})

# ---- A
mark("SPAWN_site_a", on_walk(4.3, 70.0), face=(20.0, 72.0))
mark("MARK_site_a", tuple(MAST_A))
mark("MARK_jammer_a", (jam_a["front"].x, jam_a["front"].y, 5.12))
mark("MARK_power_a", (cab_a["front"].x, cab_a["front"].y, 5.12))
rk.trig(C, "site_a", 10.0, 40.0, 64.0, 96.0, -1.0, 10.0)
REPORT["TRIG_site_a"] = "x 10..40, y 64..96, z -1..10"
(b1, f1), _, _ = SB_A[0]
(b2, f2), _, _ = SB_A[1]
(b3, f3), _, _ = SB_A[2]
(b4, f4), _, _ = SB_A[3]
enemy("a_01", on(b1.x, b1.y), tuple(f1), "rifleman_a", "a", "hold")
enemy("a_02", on(b2.x, b2.y), tuple(f2), "rifleman_b", "a", "hold")
enemy("a_03", (37.4, 80.9, 5.12), (20.0, 74.0), "officer", "a", "hold")
enemy("a_04", on(19.0, 86.5), (6.0, 80.0), "rifleman_c", "a", "advance")
enemy("a_05", on(b4.x, b4.y), tuple(f4), "rifleman_a", "a", "advance")
for i, ((bp, fp), _, _) in enumerate(SB_A):
    cover(f"a_{i + 1:02d}", on(bp.x, bp.y), tuple(fp), "low", "r41")
cover("a_05", on(12.2, 63.7), (30.0, 78.0), "low", "ally")
cover("a_06", on(12.2, 76.3), (30.0, 80.0), "low", "ally")
cover("a_07", on(-2.6, 66.0), (30.0, 76.0), "high", "ally")
cover("a_08", (36.0, 85.6, 5.12), (20.0, 80.0), "low", "r41")

# ---- A → B 도로
for i, (x, y) in enumerate(((1.4, 117.0), (1.4, 143.0), (-1.4, 143.0), (-1.4, 117.0))):
    mark(f"WP_ab_patrol_{i + 1:02d}", on(x, y))
mark("SPAWN_road", on(-1.0, 110.0), face=(-1.0, 140.0))
enemy("ab_01", on(1.4, 117.0), (1.4, 143.0), "rifleman_a", "ab", "patrol", path="ab_patrol")
enemy("ab_02", on(-1.4, 143.0), (-1.4, 117.0), "rifleman_b", "ab", "patrol", path="ab_patrol")
enemy("ab_03", on(-1.5, 151.3), (-1.5, 120.0), "rifleman_c", "ab", "hold")
bp, fp = ab_bag
enemy("ab_04", on_walk(bp.x, bp.y), (-4.4, 120.0), "rifleman_a", "ab", "hold")
cover("ab_01", on(-1.5, 151.0), (-1.5, 120.0), "high", "r41")
cover("ab_02", on(1.7, 152.6), (1.7, 120.0), "high", "r41")
cover("ab_03", on_walk(bp.x, bp.y), (-4.4, 120.0), "low", "r41")
cover("ab_04", on(1.6, 126.0), (1.6, 150.0), "high", "ally")

# ---- B
mark("SPAWN_site_b", (8.4, 202.0, ZB), face=(20.0, 202.0))
mark("SPAWN_site_b_in", tuple(stn["spawn_in"]), face=tuple(stn["console_front"]))
mark("MARK_site_b", (12.0, 202.0, ZB))
mark("MARK_power_b", (gen["front"].x, gen["front"].y, ZB + 0.04))
mark("MARK_console_b", tuple(stn["console_front"]))
mark("MARK_jammer_b", (jam_b["front"].x, jam_b["front"].y, ZB))
rk.trig(C, "site_b", 6.0, 32.0, 186.0, 226.0, -6.0, 1.0)
REPORT["TRIG_site_b"] = "x 6..32, y 186..226, z -6..1"
ZR = stn["roof_z"]
ZF = ZB + 0.15
enemy("b_01", (SB_B1[0].x, SB_B1[0].y, ZB), tuple(SB_B1[1]), "rifleman_a", "b", "hold")
enemy("b_02", (20.6, 191.6, ZB), (4.0, 196.0), "rifleman_b", "b", "hold")
enemy("b_03", (22.1, 213.0, ZB), (6.0, 206.0), "rifleman_c", "b", "hold")
enemy("b_04", (22.4, 202.6, ZB), (6.0, 202.0), "rifleman_a", "b", "advance")
enemy("b_05", (24.3, 212.4, ZR), (4.0, 204.0), "rifleman_b", "b", "hold")
enemy("b_06", (26.0, 218.2, ZF), (23.0, 215.0), "officer", "b", "hold")
for i, (x, y, fx, fy, hgt) in enumerate(((SB_B1[0].x, SB_B1[0].y, 0.0, 197.0, "low"),
                                        (SB_B2[0].x, SB_B2[0].y, 0.0, 207.0, "low"),
                                        (22.2, 201.0, 6.0, 201.0, "low"),
                                        (20.6, 191.6, 6.0, 192.0, "high"),
                                        (22.3, 210.2, 6.0, 205.0, "high"),
                                        (33.5, 190.5, 37.5, 176.0, "high"),
                                        (40.0, 201.3, 38.0, 176.0, "low"))):
    cover(f"b_{i + 1:02d}", (x, y, ZB), (fx, fy), hgt, "any")
cover("b_08", on(-2.2, 194.6), (20.0, 202.0), "high", "ally")
cover("b_09", on(8.0, 211.6), (24.0, 211.6), "high", "ally")
cover("b_10", (23.6, 212.6, ZR), (4.0, 204.0), "low", "any")
# 1차 파상: 도로에서 정문으로 (북 3 + 남 2)
for i, (x, y, z) in enumerate((on(1.4, 238.0), on(-1.4, 241.0), on_walk(4.2, 236.5), on(1.3, 169.0),
                               on(-1.5, 171.5))):
    enemy(f"bw1_{i + 1:02d}", (x, y, z), (12.0, 202.0), ("rifleman_a", "rifleman_b", "rifleman_c")[i % 3], "b_wave1",
          "advance", spawn="manual")
# 2차 파상: 골목·뒷길로 측면 2, 돌격 진압병 1, 전진 2
enemy("bw2_01", on(44.0, 180.4), (37.5, 186.0), "rifleman_b", "b_wave2", "flank", spawn="manual")
enemy("bw2_02", on(48.8, 197.0), (37.5, 186.0), "rifleman_c", "b_wave2", "flank", spawn="manual")
enemy("bw2_03", on(0.2, 242.5), (12.0, 202.0), "riot", "b_wave2", "rush", spawn="manual")
enemy("bw2_04", on(-1.5, 167.5), (12.0, 202.0), "rifleman_a", "b_wave2", "advance", spawn="manual")
enemy("bw2_05", on_walk(4.3, 234.0), (12.0, 202.0), "rifleman_b", "b_wave2", "advance", spawn="manual")

# ---- C
mark("SPAWN_site_c", (70.4, 295.8, ZC), face=(72.0, 301.5))
mark("MARK_site_c", tuple(TC))
mark("MARK_power_c", (box_c["front"].x, box_c["front"].y, ZC))
mark("MARK_dish_c", (dctl["front"].x, dctl["front"].y, ZC))
mark("MARK_jammer_c", (jam_c["front"].x, jam_c["front"].y, ZC))
rk.trig(C, "site_c", 56.0, 88.0, 284.0, 316.0, 8.0, 24.0)
REPORT["TRIG_site_c"] = "x 56..88, y 284..316, z 8..24"
(c1, cf1), _, _ = SB_C[0]
(c2, cf2), _, _ = SB_C[2]
(c5, cf5), _, _ = SB_C[5]
enemy("c_01", (c1.x, c1.y, ZC), tuple(cf1), "rifleman_a", "c", "hold")
enemy("c_02", (c2.x, c2.y, ZC), tuple(cf2), "rifleman_b", "c", "hold")
enemy("c_03", (68.2, 299.4, ZC), (60.0, 288.0), "officer", "c", "hold")
enemy("c_04", on(63.6, 279.6), (50.0, 268.0), "rifleman_c", "c", "advance")
enemy("c_05", (c5.x, c5.y, ZC), tuple(cf5), "rifleman_a", "c", "hold")
for i, ((bp, fp), _, _) in enumerate(SB_C):
    cover(f"c_{i + 1:02d}", (bp.x, bp.y, ZC), tuple(fp), "low", "any")
cover("c_08", (76.6, 305.5, ZC), (90.0, 320.0), "high", "any")
cover("c_09", on(59.2, 268.6), (72.0, 300.0), "low", "any")
cover("c_10", on(92.8, 296.4), (72.0, 300.0), "low", "any")
for i, (x, y) in enumerate(((60.0, 252.0), (66.5, 250.0), (54.0, 246.0), (70.0, 256.5), (47.0, 243.0))):
    enemy(f"cw1_{i + 1:02d}", on(x, y), (65.4, 293.4), ("rifleman_a", "rifleman_b", "rifleman_c")[i % 3], "c_wave1",
          "advance", spawn="manual")
for i, (x, y, kind, beh) in enumerate(((104.0, 339.6, "riot", "rush"), (99.0, 341.6, "riot", "rush"),
                                       (112.0, 335.6, "rifleman_a", "advance"), (120.0, 331.6, "rifleman_b", "advance"),
                                       (86.0, 347.0, "rifleman_c", "flank"), (128.0, 327.0, "rifleman_a", "flank"))):
    enemy(f"cw2_{i + 1:02d}", on(x, y), (78.0, 309.6), kind, "c_wave2", beh, spawn="manual")

# ---- 끝: 도심 코어 AI 쪽 시선, 복구 장면 레일
for jid, j in (("a", jam_a), ("b", jam_b), ("c", jam_c)):
    REPORT[f"JAMMER_{jid}"] = tuple(round(v, 2) for v in j["root"].location)
REPORT["DISH_c"] = tuple(round(v, 2) for v in mount)
mark("MARK_core", tuple(CORE))
mark("MARK_view_end", (CORE.x, CORE.y, CORE.z + 44.0))
C.cam("handoff", [
    (0.0, (12.0, 58.0, 17.0), (34.0, 82.0, 20.0), 50),
    (6.0, (6.0, 178.0, 9.0), (34.0, 213.0, 3.5), 50),
    (12.0, (54.0, 282.0, 24.0), (73.0, 302.0, 22.0), 48),
])
for i, (cp, lp) in enumerate((((12.0, 58.0, 17.0), (34.0, 82.0, 20.0)), ((6.0, 178.0, 9.0), (34.0, 213.0, 3.5)),
                              ((54.0, 282.0, 24.0), (73.0, 302.0, 22.0)))):
    REPORT[f"CAM_handoff_{i + 1:02d}"] = cp
    REPORT[f"LOOK_handoff_{i + 1:02d}"] = lp
# 연기 (HUD 없이 시설 위치를 알리는 표식)
for (fid, x, y, z, st) in (("smoke_a1", -1.1, 64.0, gz(-1.1, 64.0) + 0.6, 0.7), ("smoke_a2", 39.4, 75.2, gz(39.4, 75.2) + 0.5, 0.5),
                           ("smoke_b1", 41.0, 180.0, -3.5, 0.6), ("smoke_c1", 58.0, 268.0, gz(58.0, 268.0) + 0.4, 0.6)):
    C.fx(fid, (x, y, z), delay=0.0, dir="0,1,0", strength=st)
    REPORT[f"FX_{fid}"] = (x, y, round(z, 2))

# ================================================================== root
ROOT = {
    "sky": "#9a9096",                # 흐린 늦은 오후 → 해 질 녘 (회갈색에 옅은 자줏빛)
    "fog": "60,600",
    "sun": "-0.86,0.3,0.12",         # three.js: 서쪽에서 낮게
    "ambient": 1.25,
    "sunColor": "#f2c49c",
    "sunIntensity": 1.45,
    "hemiSky": "#b8adb2",
    "hemiGround": "#5b514f",
    "near": 0.05,
    "far": 1200,
    "music": "m7",
    "timeOfDay": "dusk_overcast",
    "scene": "M7_RELAY",
}
PREVIEW = os.environ.get("M7_PREVIEW") == "1"      # 스크린샷용: 충돌·트리거 상자 없이 _tmp에 내보낸다
if PREVIEW:
    C.cols.clear()
    for g, o in list(C.nodes):
        if o.name.startswith(("TRIG_", "COL_")):
            C.nodes.remove((g, o))
            __import__("bpy").data.objects.remove(o, do_unlink=True)
stats = C.finish("_tmp/m7_relay_preview.glb" if PREVIEW else "levels/m7_relay.glb", root_props=ROOT, outline=0.025)

CONTRACT = (["SPAWN_player", "SPAWN_site_a", "SPAWN_road", "SPAWN_site_b", "SPAWN_site_b_in", "SPAWN_site_c"]
            + [f"ALLY_{w}" for w in ("rona", "sabre", "jesty", "karen")]
            + ["TRIG_site_a", "MARK_site_a", "MARK_jammer_a", "MARK_power_a", "JAMMER_a", "JAMMER_a_glow"]
            + [f"LIGHT_site_a_{i:02d}" for i in (1, 2, 3)] + [f"LIGHT_avia_a_{i:02d}" for i in (1, 2, 3)]
            + [f"ENEMY_a_{i:02d}" for i in range(1, 6)]
            + [f"ENEMY_ab_{i:02d}" for i in range(1, 5)] + [f"WP_ab_patrol_{i:02d}" for i in range(1, 5)]
            + ["TRIG_site_b", "MARK_site_b", "MARK_power_b", "MARK_console_b", "MARK_jammer_b", "JAMMER_b",
               "JAMMER_b_glow"] + [f"LIGHT_site_b_{i:02d}" for i in range(1, 6)]
            + [f"ENEMY_b_{i:02d}" for i in range(1, 7)] + [f"ENEMY_bw1_{i:02d}" for i in range(1, 6)]
            + [f"ENEMY_bw2_{i:02d}" for i in range(1, 6)]
            + ["TRIG_site_c", "MARK_site_c", "MARK_power_c", "MARK_dish_c", "MARK_jammer_c", "JAMMER_c", "JAMMER_c_glow"]
            + [f"LIGHT_site_c_{i:02d}" for i in (1, 2, 3)] + [f"LIGHT_avia_c_{i:02d}" for i in (1, 2, 3)]
            + [f"ENEMY_c_{i:02d}" for i in range(1, 6)] + [f"ENEMY_cw1_{i:02d}" for i in range(1, 6)]
            + [f"ENEMY_cw2_{i:02d}" for i in range(1, 7)]
            + ["MARK_view_end", "MARK_core"] + [f"CAM_handoff_{i:02d}" for i in (1, 2, 3)]
            + [f"LOOK_handoff_{i:02d}" for i in (1, 2, 3)])
names = {o.name for o in __import__("bpy").data.objects}
missing = [n for n in CONTRACT if n not in names and not (PREVIEW and n.startswith("TRIG_"))]
print("[m7] contract names:", len(CONTRACT), "missing:", missing)
for k in sorted(REPORT):
    if k.startswith(("SPAWN_", "MARK_", "ALLY_", "JAMMER_")):
        print(f"[m7] {k} {REPORT[k]}")
if missing:
    raise SystemExit(f"missing contract nodes: {missing}")
