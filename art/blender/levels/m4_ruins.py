"""2막 M4 「폐허」: 정전된 시청 앞 일대 (밤).

npm run model -- art/blender/levels/m4_ruins.py   → public/models/levels/m4_ruins.glb

원작: 둠스데이 프로토콜 뒤, 흑뉴아가 시청 폐허에서 엘레나와 로네를 심문한다.
오리지널: 리타의 분대가 시청 동쪽 계단 끝 잔해 뒤에서 그 장면을 보고 동쪽으로 빠진다. 한 줄로 이어진 길(레일 슈터):
  B1 동쪽 골목 (수색조 둘) → 옆길 남쪽 끝이 무너져 막힘
  B2 사무동 E1 남쪽 반: 정문은 잔해에 묻혔고 쪽문은 안에서 빗장. 리타만 0.5 m 틈으로 엎드려 들어가 쪽문을 연다
  B3 꺾여 내려앉은 바닥판 경사로로 2층 → 남쪽 벽이 통째로 쓰러진 2층 끝에서 큰길을 내려다본다
  B4 쓰러진 벽판 비탈로 북쪽 보도 → 순찰 틈에 큰길 건너기 (동쪽은 무너진 모노레일·잔해 둑, 서쪽은 잔해 둑)
  B5 편의점 「모나티엄 25」 (숨은 시민 셋) → 반쯤 올라간 뒤 셔터
  B6 뒷골목 (드럼통 불 쬐는 차원미아 하나) → 고가 밑으로 북쪽
  B7 고가 밑 남쪽에서 들어와 멈추면 그 자리에서 뮤트 조우 컷신(A2_MUTE)이 이어진다: 모닥불 곁 무너진 상판 더미 위의 뮤트,
     동쪽 잔해 둑의 틈으로 실이 길을 긋는다 (무대 자리: art/blender/lib/m4_mute_stage.py, 출연진: cine_ruins.py)
되돌아가는 길은 보이는 잔해 둑·건물이 막는다 (보이지 않는 벽 없음). 계획: m4plan/plan.md, 마커: docs/script/m4.md 6장.
문서: docs/art/monatium-ruins.md, 미션: src/game/missions/m4.ts

좌표 (Blender, m): 원점 = 광장 가운데, +Y = 북쪽(시청). 지면 z = 0, 차도 z = -0.15.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import monatium_ruins_kit as rk  # noqa: E402
import m4_mute_stage as ms  # noqa: E402
from mathutils import Vector  # noqa: E402

cb.reset()
C = mk.City("m4_ruins")
AV = -21.0          # 큰길 중심선
CARBINE = "r41_carbine"
SQ = {k: f"characters/squad_{k}.glb" for k in ("sabre", "rona", "jesty", "karen")}
Y_SOUTH = -75.0     # 맵 남쪽 끝 (뒷골목 뒷줄 건물 뒤)

# ---------------------------------------------------------------- 바닥 (빈틈 아래 받침)
C.group("ground")
C.box("ash", -60, 130, Y_SOUTH, 50, -0.6, -0.2)
C.col(-60, 130, Y_SOUTH, 50, -0.6, -0.2)
# 받침 가장자리 COL 벽: 남쪽 상가 사이 틈(0.6 m)·시청 뒤·고가 동쪽으로 나가 받침 끝에서 떨어지지 않게 (안개 너머 어둠)
C.group("bounds")
for (x0, x1, y0, y1) in [(-60, -59, Y_SOUTH, 50), (129, 130, Y_SOUTH, 50), (-60, 130, Y_SOUTH, Y_SOUTH + 1),
                         (-60, 130, 49, 50)]:
    C.col(x0, x1, y0, y1, -0.6, 4.0)

# ---------------------------------------------------------------- 시청과 광장
C.group("cityhall")
rk.ruined_city_hall(C, 0, 26)
mk.paving(C, -30, 24, 18, 42, tile=2.0, grout=None)

C.group("plaza")
mk.paving(C, -24, 24, -11.2, 18, tile=1.6, border="pave_r")
mk.fountain(C, 0, 2.0)
rk.fountain_col(C, 0, 2.0)
rk.rubble(C, 2.6, 0.2, r=1.1, h=0.8, seed=4)          # 분수 조형이 깨져 떨어진 조각
rk.rubble(C, -2.2, 4.4, r=0.8, h=0.6, seed=5)
for sx in (-1, 1):
    for k in range(3):
        y = -6 + k * 7.5
        x = sx * 17.5
        mk.planter(C, x - 1.4, x + 1.4, y - 1.4, y + 1.4, h=0.5, hedge=False)
        if (sx, k) == (-1, 1):
            rk.fallen_tree(C, x, y, 200, seed=k)
        else:
            mk.tree(C, x, y, h=5.0, seed=11 + k * 3 + sx, z=0.5)
mk.planter(C, -11.1, -7.9, -2.7, -1.7, h=0.45)
mk.planter(C, 7.9, 11.1, 4.8, 5.8, h=0.45)


def hedge_col(x0, x1, y0, y1, h):
    """mk.planter 생울타리 덩어리 그대로의 COL (화단 COL은 상자 높이까지만이라 화단에 올라서면 울타리 속에 선다)."""
    rk.col_blob(C, ((x0 + x1) / 2, (y0 + y1) / 2, h + 0.1), 1.0, ((x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1, 0.45),
                segs=12, rings=6)


hedge_col(-11.1, -7.9, -2.7, -1.7, 0.45)
hedge_col(7.9, 11.1, 4.8, 5.8, 0.45)
mk.bench(C, -14.9, -6, yaw=90)
mk.bench(C, 14.9, 1.5, yaw=-90)
mk.lamp(C, -6.5, -9.5)
rk.fallen_lamp(C, 6.5, -9.5, 160)
mk.lamp(C, -6.5, 13.0)
rk.fallen_lamp(C, 22.5, 14.5, 230)
mk.lamp(C, -22.5, 14.5)
mk.vending(C, 21.5, 9.2, yaw=-90)
mk.cctv_pole(C, -22.8, -10.2, yaw=30)
for i, (x, y, r) in enumerate([(5.5, -5.5, 2.2), (-12, 9, 1.6), (13, -2, 1.4), (-4, -8, 1.2)]):
    mk.scorch(C, x, y, r, z=0.0, seed=i)
for i, (a, b) in enumerate([((-20, -4), (-8, 2)), ((4, 8), (16, 3)), ((-6, 14), (6, 16.5)), ((10, -10), (20, -6))]):
    rk.crack(C, a, b, seed=i)
# 동쪽 계단 끝: 숨은 자리 앞 잔해 엄폐 (높이 0.75)
for x in (13.2, 15.4, 17.6):
    rk.rubble(C, x, 10.9, r=0.95, h=0.72, seed=int(x * 10), sq=0.7)
# 광장 불 (포획 장면 조명), 바닥에 떨어진 화학 발광봉
rk.fire_barrel(C, 3, -12.5, 4.0)
# 드럼통 4·발광봉 (1.5, -16)은 큰길 차도(-0.15) 위다 (2026-11-03 floatcheck: 보도 높이 0에 놓아 15 cm 떴다). 드럼통은 가운데
# 섬 연석(y -20까지)에 걸치지 않게 북쪽으로 0.2 m
rk.fire_barrel(C, 4, -6.0, -19.6, z=-0.15, rust=True)
for (x, y, a, z) in [(-3.5, -10, 20, 0.0), (1.5, -16, 80, -0.15), (-8, 0, 140, 0.0)]:
    rk.chemlight(C, x, y, a, z=z)

# 광장 서쪽·북서쪽 막기
C.group("west")
rk.ruined_building(C, -46, -26, -10, 16, floors=4, style="apartment", front="+x", seed=21, broken=0.7)
rk.ruined_building(C, -46, -32, 18, 40, floors=3, style="office", front="+x", seed=22)
rk.rubble_wall(C, -26, -24.5, -10, 18, h=2.6, seed=1)
rk.rubble_wall(C, 18, 24, 16, 18, h=2.6, seed=2)      # 시청 동쪽 날개와 북쪽 블록 사이

# ---------------------------------------------------------------- B1 동쪽 골목 (x 24..60)
C.group("alley")
mk.paving(C, 24, 46, -1.2, 14.6, tile=1.6, grout="pave_d")
mk.paving(C, 46, 60, -11.2, 14.6, tile=1.6, grout="pave_d")
rk.ruined_building(C, 24, 46, 15, 32, floors=4, style="office", front="-y", seed=31, broken=0.8)
# 서쪽 이웃(x ..46)과 0.2 m 띄운다: 붙이면 두 건물의 층 띠(바깥으로 8 cm)가 겹쳐 윗면이 같은 평면에서 깜빡인다
rk.ruined_building(C, 46.2, 76, 15, 32, floors=3, style="brick", front="-y", seed=32)
rk.ruined_building(C, 26, 46, -11.0, -1.6, floors=3, style="apartment", front="+y", seed=33, broken=0.7)
# 사무동 E1 북쪽 반 (통짜). 남쪽 반 E1s(들어가는 폐허)는 아래 B2·B3. 남쪽 면(E1s 안쪽 벽 뒤)에는 창을 그리지 않는다.
# 앞 잔해는 예전 E1(60..76 × -10.5..14)의 북쪽 하나만 같은 자리에 둔다 (남쪽 하나는 기는 틈 자리라 뺐다)
rk.ruined_building(C, 60, 76, 2.6, 14, floors=3, style="office", front="-x", sides="+y-x+x", seed=34, rubble_front=False)
rk.rubble(C, 58.53, 12.61, r=1.17, h=0.79, seed=65)
# E1 동쪽 틈 막이: E1s 동쪽 벽 안으로 덩이가 비치지 않게 x 77..78, 쓰러진 벽판 발치(y -10.5)와 띄워 y -9부터
rk.rubble_wall(C, 77, 78, -9, 32, h=3.0, seed=3)
rk.rubble(C, 28, 8.2, r=1.3, h=0.9, seed=41)
rk.rubble(C, 35, 3.0, r=1.3, h=0.85, seed=42)
rk.rubble(C, 41.5, 10.4, r=1.2, h=0.9, seed=43)
rk.rubble(C, 50.5, 2.5, r=1.1, h=0.85, seed=44)
rk.rubble(C, 54.5, -6.0, r=1.2, h=0.9, seed=45)
rk.burnt_car(C, 49.5, -3.5, yaw=80, seed=1)
rk.fallen_lamp(C, 31, 13.5, 200)
mk.lamp(C, 39, 13.8)
rk.fire_barrel(C, 1, 44.0, 6.0)
for (x, y, a) in [(37, 6.5, 40), (46, 8.8, 120), (31, 5.0, 10)]:
    rk.chemlight(C, x, y, a)
for i, (a, b) in enumerate([((26, 4), (40, 7)), ((47, 12), (58, 2)), ((50, -9), (57, 0))]):
    rk.crack(C, a, b, seed=10 + i)
mk.scorch(C, 36, 5.6, 1.4, seed=8)
# 옆길 남쪽 끝이 무너졌다: 큰길로 못 내려간다 (B1 끝). 마지막 덩이는 E1 서쪽 벽 바깥면까지 (안으로 비치지 않게)
rk.rubble_wall(C, 46, 59.0, -9.5, -7, h=2.8, seed=8)
for (c, s, rot) in [((50.2, -7.6, 2.3), (2.6, 1.0, 0.22), (24, -18, 40)), ((55.6, -8.6, 2.2), (2.2, 0.9, 0.2), (-20, 14, 120))]:
    C.rbox("concrete_d", c, s, rot)
    rk.col_rbox(C, c, s, rot)

# ---------------------------------------------------------------- B2·B3 사무동 E1 남쪽 반 (들어가는 폐허)
E1 = (60.0, 76.0, -10.5, 2.6)
E1_T = 0.3
E1_2F = 3.0
RAMP = (69.7, 72.3, 0.8, -5.2)          # 꺾여 내려앉은 2층 바닥판: x0, x1, 발(y, z 0), 머리(y, z 3.0)
E1_COLS = [(64.2, -6.6), (68.0, -6.6), (74.0, -6.6), (64.2, -2.8), (68.0, -2.8), (74.0, -2.8)]
E1_WIN_Y = [(-9.4, -7.9), (-6.6, -5.1), (-3.8, -2.3), (0.0, 1.5)]


def e1_south():
    C.group("office")
    x0, x1, y0, y1 = E1
    t = E1_T
    # 기는 틈: 2층 바닥판 조각이 서쪽 벽 구멍에 걸렸다 (밑 0.52 m: 엎드린 리타만)
    # 틈 길이 1.2 m: 엎드려 기기는 다니는 내비 1 m 안에서만 된다(Player.proneMoveOk). 틈 속은 내비가 없으니 짧아야 지나간다
    crawl = rk.crawl_gap(C, x0, -5.1, -4.1, t=t, inn=0.9, rise=0.2, clear=0.52, plug=1.25, seed=3)
    win2 = [(a, b, E1_2F + 0.75, E1_2F + 1.95) for (a, b) in E1_WIN_Y]
    win3 = [(a, b, E1_2F + 2.7 + 0.75, E1_2F + 2.7 + 1.95) for (a, b) in E1_WIN_Y]
    rk.ruined_shell(
        C, x0, x1, y0, y1, floors=3, h0=E1_2F, fh=2.7, t=t, slab_t=0.25, key="concrete", band="concrete_d",
        holes={"-x": [crawl, (-0.3, 0.9, 0.0, 2.1)] + win3, "+x": win3},
        glass={"-x": win2, "+x": win2},
        grilles={"-x": [(-3.3, -1.9, 0.8, 2.0)]},
        gone={"-y": E1_2F},
        slab_holes={1: [(RAMP[0], RAMP[1], RAMP[3], RAMP[2])], 2: [(64.8, 67.6, -9.0, -3.6)]},
        cols=E1_COLS, top=(7.2, 9.8), ext={"-x": (y1, y1 + 1.0), "+x": (y1, y1 + 1.0)}, bands="-x+x-y", seed=4)
    # 1층 로비 바닥 (벽 밑까지: 기는 틈·쪽문 문턱이 받침 땅으로 꺼지지 않게)
    mk.paving(C, x0, x1, y0, y1, key="stone_d", grout="concrete_d", tile=1.2)
    # 쪽문 (안에서 빗장: 미닫이 철문 DOOR_m4_fire, 열면 남쪽(-y)으로 1.45 m) + 위 레일·빗장 걸쇠(고정)
    dx0, dx1 = x0 + t + 0.02, x0 + t + 0.10

    def door_build(b):
        mk._bm_box(b, dx0, dx1, -0.45, 1.05, 0.0, 2.15)
        mk._bm_box(b, dx1, dx1 + 0.03, 0.62, 0.98, 0.98, 1.08)            # 빗장 막대 (문짝 북쪽 끝, 걸쇠로)
        mk._bm_box(b, dx1, dx1 + 0.05, 0.1, 0.18, 0.85, 1.25)              # 손잡이
        mk._bm_box(b, dx0 - 0.004, dx1 + 0.004, -0.45, 1.05, 1.9, 1.94)     # 띠
    C.special("DOOR_m4_fire", door_build, "navy_l", {"move": "0,0,1.45"})
    C.box("steel", x0 + t, x0 + t + 0.16, -2.0, 1.2, 2.15, 2.25, kind="detail")             # 문 레일
    C.box("steel", x0 + t, x0 + t + 0.14, 1.05, 1.2, 0.92, 1.14, kind="detail")             # 빗장 걸쇠
    for (ya, yb, za, zb) in [(-0.42, -0.3, 0.0, 2.2), (0.9, 1.02, 0.0, 2.2), (-0.42, 1.02, 2.1, 2.2)]:
        C.box("dark", x0 - 0.05, x0, ya, yb, za, zb, kind="detail")                         # 바깥 문틀
    C.rect("hazard", (x0 - 0.05, 0.3, 2.45), (-1, 0, 0), 0.9, 0.18, up=(0, 0, 1), lift=0.01)   # 비상구 띠
    # 정문 (잔해에 묻힘: 옆길 둑 뒤로 문틀만)
    mk.entrance(C, (x0, -8.3, 0.0), Vector((-1, 0, 0)), Vector((0, -1, 0)), w=1.4, h=2.0, canopy=False)
    # 엘리베이터 (멈춤) · 안내판
    for zf in (0.0, E1_2F):
        C.box("steel", 62.8, 64.6, y1 - t - 0.03, y1 - t, zf, zf + 2.1, kind="detail")
        C.box("dark", 63.68, 63.72, y1 - t - 0.035, y1 - t - 0.03, zf, zf + 2.1, kind="detail")
        C.box("dark", 64.8, 64.95, y1 - t - 0.03, y1 - t, zf + 1.0, zf + 1.25, kind="detail")
    # 로비 소품: 안내 데스크, 넘어진 서류함, 소파, 떨어진 천장판·전선
    C.box("warm_d", 62.2, 63.0, -9.4, -7.4, 0.0, 1.0, col=True)
    C.box("navy", 62.16, 62.2, -9.3, -7.5, 0.1, 0.9, kind="detail")
    C.box("white", 62.15, 63.05, -9.45, -7.35, 1.0, 1.05, kind="detail")
    C.col(62.15, 63.05, -9.45, -7.35, 1.0, 1.05)
    C.box("steel", 74.4, 75.7, -9.0, -7.6, 0.0, 0.6, col=True)                              # 누운 서류함
    C.box("navy_l", 65.6, 67.6, 1.5, 2.3, 0.0, 0.42, col=True)                             # 소파
    C.box("navy_l", 65.6, 67.6, 2.0, 2.3, 0.42, 0.75, col=True)
    for (cx, cy, a) in [(66.4, -5.0, 20), (63.2, -1.5, -35), (71.0, -8.4, 70), (61.8, 0.8, 10)]:
        C.rbox("white", (cx, cy, 0.02), (1.2, 0.6, 0.03), (2, -3, a), kind="detail")       # 떨어진 천장판
    for (cx, cy) in [(66.0, -4.0), (70.0, -7.6), (62.5, -6.5)]:
        C.beam("dark", (cx, cy, E1_2F - 0.25), (cx + 0.2, cy - 0.1, 1.85), 0.025, 0.025, kind="detail")
    # 천장에서 떨어진 잔해 더미 (벽·기둥에서 0.7 m 넘게 띄운다: 사이에 끼는 틈이 없게)
    rk.rubble(C, 66.4, -7.9, r=0.7, h=0.55, seed=61)
    rk.rubble(C, 72.6, -8.5, r=0.7, h=0.5, seed=62)
    rk.soot(C, (x0 + t + 0.02, -6.8, 1.6), (1, 0, 0), 1.6, 1.8, seed=63)
    # 2층 바닥판이 꺾여 내려앉은 경사로 (27°): 밑은 잔해로 꽉 찬 쐐기
    rk.wedge_ramp(C, "y", RAMP[2], RAMP[3], RAMP[0], RAMP[1], E1_2F, seed=5)
    # 2층: 북쪽 사무실은 칸막이벽으로 막혔다 (경사로 구멍 둘레는 벽이 감싼 홈)
    z2a, z2b = E1_2F, E1_2F + 2.7 - 0.25
    rk.wall_run(C, "x", -1.1, x0 + t, RAMP[0] - 0.25, z2a, z2b, t=0.25, key="warm")
    rk.wall_run(C, "x", -1.1, RAMP[1] + 0.25, x1 - t, z2a, z2b, t=0.25, key="warm")
    rk.wall_run(C, "y", RAMP[0] - 0.25, -1.1, RAMP[2] + 0.25, z2a, z2b, t=0.25, key="warm")
    rk.wall_run(C, "y", RAMP[1], -1.1, RAMP[2] + 0.25, z2a, z2b, t=0.25, key="warm")
    rk.wall_run(C, "x", RAMP[2], RAMP[0], RAMP[1], z2a, z2b, t=0.25, key="warm")
    for xd in (62.4, 74.2):
        C.box("navy", xd - 0.5, xd + 0.5, -1.13, -1.1, z2a, z2a + 2.0, kind="detail")         # 닫힌 문 (칸막이 남쪽 면)
    # 2층 남쪽 끝: 벽이 쓰러졌다. 남은 기둥과 낮은 벽 밑동(0.5~0.8 m: 앉으면 가린다). 서쪽 x 60.3..63.2는 비탈로 나가는 자리
    for px in (64.2, 68.0, 74.0):
        C.box("concrete", px - 0.25, px + 0.25, y0, y0 + 0.35, z2a, z2b, col=True)
    stub = [(63.2, 63.95, 0.5), (64.45, 66.1, 0.4), (66.1, 67.75, 0.52), (68.25, 70.0, 0.36), (70.0, 71.9, 0.48),
            (71.9, 73.75, 0.42), (74.25, 75.7, 0.55)]
    for (a, b, h) in stub:
        C.box("concrete", a, b, y0, y0 + 0.3, z2a, z2a + h, col=True)
        C.beam("rebar", ((a + b) / 2, y0 + 0.15, z2a + h), ((a + b) / 2 + 0.15, y0 + 0.05, z2a + h + 0.35), 0.03, 0.03,
               kind="detail")
    # 2층 사무실 소품 (넘어진 책상·서류함·종이)
    C.box("wood_d", 61.0, 62.4, -7.6, -6.8, z2a, z2a + 0.75, col=True)
    C.box("wood_d", 65.2, 66.8, -2.6, -1.8, z2a, z2a + 0.75, col=True)
    C.box("steel", 74.6, 75.7, -5.4, -4.0, z2a, z2a + 0.5, col=True)
    for (cx, cy, a) in [(62.0, -5.0, 30), (66.6, -6.4, -20), (70.6, -6.0, 75), (63.2, -8.8, 5), (72.6, -8.2, 50)]:
        C.rbox("white", (cx, cy, z2a + 0.012), (0.3, 0.21, 0.01), (0, 0, a), kind="fine")     # 흩어진 종이
    # 앞면이 미끄러져 내려온 벽판 비탈 (2층 끝 서쪽 → 북쪽 보도 x 78, 9.5°): 판 밑은 잔해로 꽉 찬다
    rk.wedge_ramp(C, "x", 78.0, x0, -13.0, y0, E1_2F, seed=7)
    nrm = Vector((E1_2F / (78.0 - x0), 0, 1)).normalized()                                 # 비탈 윗면 법선
    for k in range(5):
        u = 62.4 + k * 3.1
        zt = E1_2F * (78.0 - u) / (78.0 - x0)
        C.rect("char", (u, -11.75, zt), tuple(nrm), 1.2, 0.9, up=(0, 1, 0), lift=0.02)      # 벽판의 창 구멍 (그림)


e1_south()

# ---------------------------------------------------------------- B4 큰길 (y = -21)
C.group("avenue")
rd = mk.road(C, "x", AV, -30, 116, lanes=4, median=2.0)
# 모노레일: 동쪽 경간이 고가 앞으로 무너졌다 (x 86.5에서 끊겨 잔해 둑 위로 꺾임). 고가 밑 기둥(96, 112)은 없다
rk.monorail_dark(C, -30, 116, AV, pillars=(-24, -8, 8, 24, 32, 64, 80), gaps=((32.6, 48.0), (86.5, 116.0)))
rk.collapsed_span(C, (33.0, AV, 7.0), (47.5, AV, 0.35))
C.cyl("concrete", (48, AV, -0.15), (48, AV, 2.6), 0.55, segs=14)       # 부러진 기둥 밑동
rk.col_cyl(C, (48, AV, -0.15), (48, AV, 2.6), 0.55, segs=14)
rk.rubble(C, 48.6, AV + 1.2, r=1.2, h=1.0, seed=51, z=-0.15)
rk.collapsed_span(C, (86.5, AV, 7.0), (92.0, AV, 1.8), z_floor=1.2)
# 큰길 서쪽은 광장과만 이어진다: x 26..30 잔해 둑. 건너는 구간(B4) 서쪽 끝 x 49..52.5 둑 (무너진 경간 잔해, 되돌아가지 않게)
rk.rubble_wall(C, 26, 30, -31, -11.2, h=3.0, seed=4)
rk.rubble_wall(C, -32, -30, -31, -11.2, h=3.0, seed=5)
rk.rubble_wall(C, 49, 52.5, -31, -11.2, h=3.0, seed=9)
# 고가 앞 잔해 둑 (무너진 모노레일·고가 끝 잔해): 큰길로는 고가 밑에 못 간다 = 건너야 하는 까닭
rk.rubble_wall(C, 88.5, 94, -31, -9, h=3.2, seed=10)
# 북쪽 보도 뒤 띠 (보도 끝 y -11.2부터 건물·벽판 발치까지 받침 땅 대신 포장): 화단 82 뒤 분대 대기 자리
mk.paving(C, 60, 86, -11.2, -10.5, tile=1.6, grout=None)
mk.paving(C, 76, 86, -10.5, -9.0, tile=1.6, grout=None)
# 남쪽 보도 앞 띠 (상가 정면 y -31.4까지): 가게 문 앞이 받침 땅으로 꺼지지 않게
mk.paving(C, 46.0, 93.7, -31.4, -30.8, tile=1.6, grout=None)
# 북쪽 보도 은신선: 화단 58·82 (66·74는 쓰러진 벽판 밑에 깔렸다)
for x in (58, 82):
    mk.planter(C, x - 1.2, x + 1.2, -13.6, -12.2, h=0.55, hedge=True)
    hedge_col(x - 1.2, x + 1.2, -13.6, -12.2, 0.55)
# 큰길 위 불탄 차·드럼통·상자는 차도(-0.15)에 놓는다 (2026-11-03 floatcheck: 보도 높이 0에 놓아 15 cm 떴다). 남쪽 보도 연석
# (y -27.6)에 걸쳐 한쪽 바퀴만 뜨던 두 대는 차도 안으로 0.4~0.6 m
rk.burnt_car(C, 76, -15.6, yaw=175, z=-0.15, seed=2)
rk.burnt_car(C, 83.2, -16.0, yaw=186, z=-0.15, seed=3)          # 화단 82 앞 (건너기 출발 가림)
rk.burnt_car(C, 77.8, -28.5, yaw=165, z=0.0, seed=7)            # 남쪽 보도에 올라선 차: 불가에서 가게 문 사선을 가린다
rk.burnt_car(C, 58, -26.6, yaw=-5, z=-0.15, seed=4)
rk.burnt_car(C, 10, -16.0, yaw=170, z=-0.15, seed=5)
rk.burnt_car(C, -14, -25.5, yaw=5, z=-0.15, seed=6)
# 잔당 노숙 자리 (모노레일 아래)
rk.fire_barrel(C, 2, 70.0, -24.0, z=-0.15, rust=True)
mk.crate(C, 72.6, -25.8, s=0.7, yaw=20, z=-0.15)
mk.crate(C, 67.4, -26.0, s=0.6, yaw=-15, z=-0.15)
C.box("tarp_o", 66.5, 73.5, -28.6, -28.4, -0.15, 1.6, col=True)
C.beam("tarp_o", (66.5, -28.5, 1.6), (66.5, -26.0, 0.9), 0.05, 0.05)
rk.col_beam(C, (66.5, -28.5, 1.6), (66.5, -26.0, 0.9), 0.05, 0.05)
C.prism("tarp_o", [(66.5, -28.5), (73.5, -28.5), (73.5, -26.5), (66.5, -26.5)], 1.55, 1.62)
for (x, y, a) in [(64, -19, 60), (75, -22, 150), (69, -17.5, 10)]:
    rk.chemlight(C, x, y, a, z=-0.15)

# ---------------------------------------------------------------- 남쪽 상가 줄 (어두운 폐허)
C.group("south")
# 고가 발자리(x 94..106)에는 상가를 두지 않는다 (예전 88..104·104..118은 고가 상판 z 6~6.9를 뚫고 서 있었다). 다섯째 칸
# (70..88)은 아래 B5 편의점(1층 가게 + 위층)
SHOPS = [(-30, -12), (-12, 6), (6, 26), (30, 50), (50, 70), (70, 88), (88, 94), (106, 118)]
for i, (x0, x1) in enumerate(SHOPS):
    if (x0, x1) == (70, 88):
        continue
    rk.ruined_building(C, x0 + 0.3, x1 - 0.3, -46, -31.4, floors=2 + (i % 3), style="brick" if i % 2 else "office",
                       front="+y", seed=60 + i, broken=0.6, dark_windows=True)
# 상가 사이 0.6 m 틈 막기 (정면 바로 안쪽): 캡슐이 비집고 상가 뒤 빈 땅으로 나가고, 병사 경로가 틈에서 끼었다
for xg in (-12, 6, 50, 70, 88):
    C.col(xg - 1.0, xg + 1.0, -32.6, -31.5, -0.2, 4.0)

# ---------------------------------------------------------------- B5 편의점 「모나티엄 25」 (x 70.3..87.7)
C.group("store")
ST = (70.3, 87.7, -46.0, -31.4)
rk.shop_interior(C, *ST, h=3.2, door=(83.0, 85.0), broken=[(75.8, 79.6)], piers=[73.0, 81.3], back=(77.5, 79.7, 2.4),
                 name="모나티엄 25", sub="MONATIUM 25 · 24H", awning="coral", seed=65)
rk.ruined_building(C, *ST, floors=3, style="brick", front="+y", seed=65, broken=0.6, dark_windows=True, z0=3.2, h0=0.4,
                   r=0.3, door=False, rubble_front=False)
# 안: 벽 진열대 · 진열대 넷(둘은 넘어짐, 통로 1.3 m 넘게) · 계산대 · 꺼진 냉장고 벽 · 안쪽 창고
rk.gondola(C, 70.6, 71.2, -41.6, -33.0, h=1.9, seed=1)
rk.gondola(C, 72.6, 73.2, -40.4, -34.2, seed=2)
rk.gondola(C, 75.4, 76.0, -40.4, -34.2, fallen="+x", seed=3)
rk.gondola(C, 78.6, 79.2, -40.4, -35.4, seed=4)
rk.gondola(C, 81.4, 82.0, -40.4, -36.0, fallen="+x", seed=5)
rk.counter(C, 85.4, 86.4, -38.0, -33.2)
rk.cooler_bank(C, 70.6, 77.2, -45.7, -42.4, h=2.6, doors=5, face="+y")
# 창고 (x 80..87.4 × -45.7..-42.4): 북쪽 벽 문 x 81..82.2, 서쪽 벽은 통로(x 77.2..80) 쪽
rk.wall_run(C, "x", -42.4, 80.0, 87.4, 0.0, 2.95, t=0.25, holes=[(81.0, 82.2, 0.0, 2.1)], key="warm")
rk.wall_run(C, "y", 80.0, -45.7, -42.15, 0.0, 2.95, t=0.25, key="warm")
C.box("dark", 80.92, 82.28, -42.17, -42.12, 2.1, 2.18, kind="detail")
C.rect("white", (81.6, -42.12, 2.45), (0, 1, 0), 0.9, 0.22, lift=0.01)                     # 「창고」 표찰
for (x0, x1, y0, y1, h) in [(80.25, 81.6, -45.7, -44.5, 0.55), (86.3, 87.4, -43.7, -42.65, 0.7)]:
    C.box("sand", x0, x1, y0, y1, 0.0, h, col=True)                                           # 상자 더미 (벽에 붙임)
    C.box("sand", x0 + 0.05, x1 - 0.1, y0 + 0.05, y1 - 0.05, h, h * 2, col=True)
    C.strip("wood_d", (x0, (y0 + y1) / 2, h * 2 + 0.002), (x1, (y0 + y1) / 2, h * 2 + 0.002), 0.06, lift=0.003)
# 뒤 셔터 (반쯤 올라감: 밑 1.35 m, 웅크리지 않고 지난다). 미션이 열면 0.85 m 올라간다
rk.roll_shutter(C, "m4_store_back", 77.5, 79.7, ST[2], z_open=1.35, z_top=2.4, raise_by=0.85, out=-1)
# 문 앞 깨진 유리·쏟아진 물건
for (cx, cy, a, k) in [(83.6, -32.6, 30, "red"), (84.4, -33.1, -10, "teal"), (76.6, -32.4, 60, "hazard"),
                       (77.8, -33.2, 15, "coral")]:
    C.rbox(k, (cx, cy, 0.04), (0.26, 0.16, 0.08), (0, 0, a), kind="detail")

# ---------------------------------------------------------------- B6 뒷골목 (y -53.2..-46, x 72..112)
C.group("lane")
mk.paving(C, 66, 118, -53.2, -46.0, tile=1.6, grout="pave_d")
# 고가 밑 남쪽 둑 밑까지 포장 (둑 덩이 아랫배와 0.2 m 낮은 받침 땅 사이 홈에 웅크린 몸이 끼었다: wedgecheck)
mk.paving(C, 93.7, 106.3, -57.8, -53.2, tile=2.0, grout=None)
# 고가 밑 통로 바닥 (뒷골목 → 큰길 남쪽 보도)
mk.paving(C, 93.7, 106.3, -46.0, -30.8, tile=2.0, grout="pave_d")
rk.rubble_wall(C, 68, 72.5, -53.4, -45.8, h=3.0, seed=11)          # 서쪽 끝 (편의점 셔터 서쪽 4 m)
rk.rubble_wall(C, 112.5, 117, -53.4, -45.8, h=3.0, seed=12)        # 동쪽 끝 (차원미아 자리 뒤)
rk.rubble_wall(C, 93.5, 106.5, -56.5, -54.0, h=3.0, seed=13)       # 고가 밑 남쪽 (뒷골목 건너편)
# 뒷줄 건물 (맵 남쪽 끝)
rk.ruined_building(C, 66.3, 87.7, -72, -53.2, floors=3, style="apartment", front="+y", seed=91, broken=0.7,
                   rubble_front=False)
rk.ruined_building(C, 88.3, 93.7, -72, -53.2, floors=2, style="office", front="+y", seed=92, broken=0.6,
                   rubble_front=False, door=False)
rk.ruined_building(C, 106.3, 117.7, -72, -53.2, floors=3, style="brick", front="+y", seed=93, broken=0.7,
                   rubble_front=False)
# 뒷줄 건물 사이 0.6 m 틈 막기 (상가 줄과 같은 규칙): 뒷골목에서 맵 남쪽 끝 빈 땅으로 비집고 나가지 않게
C.col(87.0, 89.0, -54.4, -53.25, -0.2, 4.0)
# 쓰레기통·실외기 (벽에 붙임: 틈 0), 상자·잔해 (벽에서 1.5 m 넘게)
rk.dumpster(C, 84.6, -46.48, yaw=0)
rk.dumpster(C, 90.6, -46.48, yaw=0, key="navy_l")
rk.ac_unit(C, 82.0, -46.0, 0.0)
rk.ac_unit(C, 92.6, -46.0, 0.0)
mk.crate(C, 98.6, -49.4, s=0.7, yaw=15)
mk.crate(C, 101.4, -51.5, s=0.65, yaw=-20)
rk.rubble(C, 89.5, -50.0, r=0.9, h=0.75, seed=81)
for (x, y, a) in [(88.0, -50.0, 30), (96.0, -52.0, 120), (104.0, -48.4, 70)]:
    rk.chemlight(C, x, y, a)
rk.clothesline(C, (75.0, -46.05, 3.3), (75.6, -53.15, 3.5), seed=1)
rk.clothesline(C, (87.2, -46.05, 3.1), (86.6, -53.15, 3.4), seed=2)
# 차원미아의 드럼통 불 (FX_fire_6: 불러올 때부터 점광원이 있다, 세기만 바뀐다)
rk.fire_barrel(C, 6, 108.8, -51.9, rust=True)

# ---------------------------------------------------------------- B7 고가 밑 (뮤트 조우): 남쪽 뒷골목에서 들어온다
C.group("underpass")
rk.overpass(C, 94, 106, -40, -2, z=6.0, pillars=((95.2, -33.5), (104.8, -33.5), (95.2, -8.5), (104.8, -8.5)),
            sign=("알프토반 · 에르피엔 26 mi", "ALFTOBAHN 1 · ERPIEN"))
rk.overpass(C, 94, 106, -58, -40, z=6.0, pillars=((95.2, -45.0), (104.8, -45.0), (95.2, -55.4), (104.8, -55.4)))
rk.overpass(C, 94, 106, -2, 16, z=6.0, pillars=((95.2, 6.0), (104.8, 6.0)))
C.rbox("navy", (102.5, -23.5, 0.55), (4.4, 0.16, 1.4), (12, 8, 64))         # 떨어진 표지판
rk.col_rbox(C, (102.5, -23.5, 0.55), (4.4, 0.16, 1.4), (12, 8, 64))
C.rbox("white", (102.42, -23.6, 0.62), (3.6, 0.04, 0.3), (12, 8, 64), kind="fine")
rk.rubble(C, 99, -26.5, r=1.4, h=1.0, seed=71, z=-0.15)
# 모닥불: 고가 밑 남쪽 통로 끝 보도 (리타가 멈추는 자리 앞 5 m). 편의점 시민이 말한 「고가 밑 불 옆」
FX, FY, FZ = ms.FIRE
rk.campfire(C, 5, FX, FY, z=FZ)
# 모닥불 돌 테 COL (0.5 m: 불 속으로 걸어 들어가 장작 밑으로 발이 빠지지 않게, groundcheck). 키트 campfire는 COL이 없다
rk.col_cyl(C, (FX, FY, FZ), (FX, FY, FZ + 0.5), 0.58, segs=10)
# 뮤트가 걸터앉는 무너진 상판 더미 (불 서쪽): 아래 덩어리 + 위 판, 철근. 위 판의 남동쪽 끝이 남쪽 통로(리타)를 본다.
# 서쪽 기둥(95.2, -33.5)과 0.8 m, 통로 서쪽 끝 상가 모서리와 0.8 m 떨어진다 (들어가면 못 나오는 틈 없음)
PCX, PCY = ms.PERCH_CENTER
C.rbox("concrete_d", (PCX - 0.15, PCY + 0.1, 1.07), (2.2, 1.6, 2.14), (2.5, -3.0, ms.PERCH_YAW + 6))
rk.col_rbox(C, (PCX - 0.15, PCY + 0.1, 1.07), (2.2, 1.6, 2.14), (2.5, -3.0, ms.PERCH_YAW + 6))
# 기대 선 깨진 판 조각 둘 (아래 덩어리 서쪽·북쪽)
for (c, sz, rot) in [((PCX - 1.25, PCY + 0.05, 0.85), (1.6, 0.3, 1.7), (0, 24, ms.PERCH_YAW + 80)),
                     ((PCX + 0.35, PCY + 1.05, 0.7), (1.4, 0.28, 1.4), (-20, 0, ms.PERCH_YAW + 4))]:
    C.rbox("concrete", c, sz, rot)
    rk.col_rbox(C, c, sz, rot)
C.rbox("concrete", (PCX, PCY, ms.PERCH_TOP - 0.2), (2.6, 1.8, 0.4), (1.5, -2.0, ms.PERCH_YAW))
rk.col_rbox(C, (PCX, PCY, ms.PERCH_TOP - 0.2), (2.6, 1.8, 0.4), (1.5, -2.0, ms.PERCH_YAW))
C.rbox("asphalt", (PCX, PCY, ms.PERCH_TOP + 0.01), (2.3, 1.5, 0.03), (1.5, -2.0, ms.PERCH_YAW), kind="detail")
for (a, b) in [((PCX - 1.0, PCY - 0.2, 2.3), (PCX - 1.6, PCY - 0.5, 3.1)), ((PCX + 0.6, PCY + 0.7, 2.4), (PCX + 0.9, PCY + 1.4, 3.0)),
               ((PCX - 0.4, PCY + 0.8, 1.6), (PCX - 0.6, PCY + 1.6, 2.2))]:
    C.beam("rebar", a, b, 0.035, 0.035, kind="detail")
rk.rubble(C, PCX - 1.0, PCY + 1.5, r=0.8, h=0.6, seed=72)
# 동쪽 잔해 둑: 큰길 줄에 틈 (y -23.4..-18.8). 뮤트의 실이 이 틈으로 동쪽 골목(수용소 쪽)에 길을 긋는다.
# 리타가 고가 밑 통로에 들어서면 조작이 시점만이 되므로 놀이 중에는 닿지 않는다 (한 줄 길 그대로)
rk.rubble_wall(C, 112, 118, -31, -25.4, h=3.2, seed=6)
rk.rubble_wall(C, 112, 118, -16.8, -11.2, h=3.2, seed=8)
rk.rubble(C, 113.6, ms.GAP_Y[0] - 0.4, r=1.0, h=0.8, seed=73, z=-0.15)
rk.rubble(C, 116.4, ms.GAP_Y[1] + 0.5, r=0.9, h=0.7, seed=74, z=-0.15)
# 틈 너머 동쪽 골목 (x 116..맵 끝): 판석, 양쪽 불 꺼진 건물, 끝은 안개 속
mk.paving(C, 116.0, 129.0, -24.6, -17.6, tile=1.6, grout="pave_d", z=-0.15, t=0.25)
rk.ruined_building(C, 118.3, 128.8, -34.0, -24.6, floors=2, style="brick", front="+y", seed=94, rubble_front=False, door=False)
rk.ruined_building(C, 118.3, 128.8, -17.6, -6.0, floors=3, style="office", front="-y", seed=95, rubble_front=False, door=False)
for (x, y, a) in [(119.5, -22.6, 40), (124.0, -19.4, 110)]:
    rk.chemlight(C, x, y, a, z=-0.15)
rk.rubble_wall(C, 86, 112, -11.0, -9.0, h=3.0, seed=7)       # 북쪽 블록 앞
# 북쪽 블록: 고가 발자리(x 94..106)를 비운다 (예전 78..112 한 덩이는 고가 상판을 뚫고 섰다)
rk.ruined_building(C, 78, 93.7, -9, 14, floors=3, style="apartment", front="-y", seed=81, rubble_front=False)
rk.ruined_building(C, 106.3, 112, -9, 14, floors=3, style="apartment", front="-y", seed=82, rubble_front=False)

# ---------------------------------------------------------------- 원경: 정전된 스카이라인, 연기, 두 달
C.group("skyline")
rk.dark_skyline(C, 40, 0, r=150, n=40, seed=5)
rk.dark_skyline(C, 40, 0, r=200, n=30, seed=9, hmin=20, hmax=60, key="far_n2")
mk.smoke_column(C, -90, 110, h=70, r=7, seed=1, dark=0.6)
mk.smoke_column(C, 170, 60, h=60, r=6, seed=2, dark=0.6)
mk.smoke_column(C, 60, -150, h=55, r=6, seed=3, dark=0.6)
mk.sky_moons(C, (-120, 260, 140), (0.4, -0.85, -0.35), r=26)

# ================================================================== 마커 (표: docs/script/m4.md 6장)
C.group("markers")
# 시작: 동쪽 계단 끝 잔해 뒤
C.marker("SPAWN_player", (16.0, 9.0, 0), face=(2, 6))
C.marker("SPAWN_alley", (22.0, 7.0, 0), face=(40, 7))
# 단계 시작·체크포인트 (늘린 M4)
C.marker("SPAWN_sidedoor", (53.0, 5.0, 0), face=(53, -5))
C.marker("SPAWN_lobby", (63.0, -1.0, 0), face=(70, -1))
C.marker("SPAWN_apron", (61.6, -10.0, E1_2F), face=(78, -11.8))
C.marker("SPAWN_store", (84.0, -33.6, 0), face=(84, -40))
C.marker("SPAWN_lane", (78.6, -47.6, 0), face=(96, -48))
C.marker("SPAWN_underpass", ms.SPAWN, face=(100, -20))
# 예전 이름 (늘린 대본으로 옮기면 지운다): 큰길 빠른 시작 = 벽판 비탈 발치 북쪽 보도
C.marker("SPAWN_avenue", (80.0, -13.0, 0), face=(80, -30))
for who, (x, y), face in [("sabre", (14.6, 9.6), (2, 8)), ("rona", (17.6, 8.4), (2, 6)),
                          ("jesty", (18.8, 9.8), (2, 9)), ("karen", (15.2, 7.8), (2, 5))]:
    C.marker(f"ALLY_{who}", (x, y, 0), face=face, props={"who": who, "behavior": "follow", "model": SQ[who],
                                                          "weapon": "m4a1"})
# 포획 장면
Z_TOP = 0.9
C.npc("black_renewa", (0, 17.6, Z_TOP), "characters/black_renewa.glb", pose="cross_arms", name="흑뉴아", face=(0, 0))
C.npc("br_guard_a", (-2.4, 17.0, Z_TOP), "enemies/r41_hq_guard.glb", pose="hold_rifle_ready", name="R41",
      face=(-2.4, 0), props={"hold_R": "weapons/r41/r41_carbine.glb"})
C.npc("br_guard_b", (2.4, 17.0, Z_TOP), "enemies/r41_hq_guard.glb", pose="hold_rifle_ready", name="R41",
      face=(2.4, 0), props={"hold_R": "weapons/r41/r41_carbine.glb"})
C.npc("elena", (-3.0, -25.0, -0.15), "characters/elena.glb", pose="idle", name="엘레나", face=(-3, 0))
C.npc("rone", (-1.6, -25.8, -0.15), "characters/rone.glb", pose="idle", name="로네", face=(-1.6, 0))
for nid, (x, y), model in [("escort_a", (-4.4, -26.6), "enemies/r41_rifleman_a.glb"),
                           ("escort_b", (-1.8, -27.6), "enemies/r41_rifleman_b.glb"),
                           ("escort_c", (-3.2, -28.6), "enemies/r41_officer.glb")]:
    C.npc(nid, (x, y, -0.15), model, pose="hold_rifle_ready", name="R41", face=(x, 0),
          props={"hold_R": "weapons/r41/r41_carbine.glb" if nid != "escort_c" else "weapons/r41/r41_sidearm.glb"})
# 계단 높이: 단 6개 (y 11.3부터 0.45 m마다 0.15 m), y 14부터 포르티코 바닥 0.9
for i, (x, y, z) in enumerate([(-3, -24, -0.15), (-3, -12, 0), (-5, -2, 0), (-3, 8, 0), (0, 11.5, 0.15),
                               (0, 15, Z_TOP), (0, 18.6, Z_TOP)], start=1):
    C.marker(f"WP_escort_{i:02d}", (x, y, z))
# 문 앞 보초 (포획 뒤 미션이 부른다)
for nid, x in (("door_a", -2.6), ("door_b", 2.6)):
    C.marker(f"ENEMY_{nid}", (x, 16.2, Z_TOP), face=(x, 0),
             props={"kind": "hq_guard", "group": "door", "behavior": "hold", "spawn": "manual", "weapon": CARBINE})
# B1 골목 수색조 (차원미아)
C.marker("ENEMY_lost_a", (38.0, 4.0, 0), face=(47, 9),
         props={"kind": "rifleman_b", "group": "lost", "behavior": "patrol", "path": "patrol_lost", "weapon": CARBINE})
C.marker("ENEMY_lost_b", (39.5, 5.5, 0), face=(47, 9),
         props={"kind": "rifleman_c", "group": "lost", "behavior": "patrol", "path": "patrol_lost", "weapon": CARBINE})
for i, (x, y) in enumerate([(38, 4), (47, 9), (40, 11.5), (30, 6)], start=1):
    C.marker(f"WP_patrol_lost_{i:02d}", (x, y, 0))
# B2 수색 진압반 셋 (뒤 = 시청 쪽에서 온다: spawn manual, 진입점 MARK_entry_sweep_*). 한 방향 순찰 WP_sweep_01..09,
# 끝(09 = 시청 문 앞)에서 선다. 경로점 속성: wait(초) · look("x,y" Blender, 그쪽을 본다)
for nid, (x, y), kind in [("sweep_a", (24.0, 5.0), "riot"), ("sweep_b", (24.0, 7.0), "rifleman_a"),
                          ("sweep_c", (24.0, 9.0), "officer")]:
    C.marker(f"ENEMY_{nid}", (x, y, 0), face=(36, 6),
             props={"kind": kind, "group": "sweep", "behavior": "patrol", "path": "sweep", "spawn": "manual",
                    "weapon": CARBINE, "loop": 0, "chemlight": 1})
for i, (x, y) in enumerate([(22.5, 3.0), (23.5, 12.0)], start=1):
    C.marker(f"MARK_entry_sweep_{i:02d}", (x, y, 0), face=(36, 6))
for i, (x, y, p) in enumerate([(26, 6, {}), (36, 6, {}), (47, 7, {}), (53, 2, {}),
                               (58.6, -3.0, {"wait": 6, "look": "62,-2.6"}), (53.0, -5.0, {"wait": 4, "look": "53,-9"}),
                               (53, 2, {}), (40, 8, {}), (6.0, 9.0, {"look": "0,16"})], start=1):
    C.marker(f"WP_sweep_{i:02d}", (x, y, 0), props=p)
# B4 큰길 잔당: 불가 셋(불 보던 눈: sightMul 0.5), 도는 하나 (WP_patrol_rem: 북쪽 줄을 서쪽으로 걸을 때 등이 건너는 자리 쪽)
for nid, (x, y), kind, face in [("rem_a", (68.5, -23.0), "rifleman_a", (70, -24)),
                                ("rem_b", (71.5, -22.5), "rifleman_c", (70, -24)),
                                ("rem_c", (70.0, -26.2), "assault", (60, -14))]:
    C.marker(f"ENEMY_{nid}", (x, y, -0.15), face=face,
             props={"kind": kind, "group": "remnant", "behavior": "hold", "weapon": CARBINE, "sightMul": 0.5})
C.marker("ENEMY_rem_d", (58.8, -18.2, -0.15), face=(85, -18),
         props={"kind": "rifleman_b", "group": "remnant", "behavior": "patrol", "path": "patrol_rem", "weapon": CARBINE})
for i, (x, y, p) in enumerate([(58.8, -18.2, {"wait": 2, "look": "50,-21"}), (85.2, -18.0, {"wait": 3, "look": "85,-11"}),
                               (86.3, -23.5, {"wait": 2, "look": "84,-31"}), (84.6, -19.6, {})], start=1):
    C.marker(f"WP_patrol_rem_{i:02d}", (x, y, -0.15), props=p)
# B6 뒷골목 차원미아 (혼자 드럼통 불을 쬔다: 앉은 자세, 10~14초마다 3초 서쪽을 돌아본다). 대본이 둔 조우라 전선 규칙에서 뺀다
C.marker("ENEMY_lane_a", (107.4, -50.6, 0), face=(108.8, -51.9),
         props={"kind": "rifleman_c", "group": "lane", "behavior": "hold", "weapon": CARBINE, "pose": "sit",
                "scan": "10,14,3", "scanLook": "96,-48", "sightMul": 0.5})
# 멈춘 R41 차량 (정전으로 정지: 미션이 상태 off로 세운다)
for vid, (x, y), yaw, veh in [("ifv_plaza", (-9.0, -3.0), 30, "r41_apc"), ("raider_plaza", (11.0, -7.0), -20, "r41_raider"),
                              ("raider_alley", (33.0, 9.6), 100, "r41_raider"), ("ifv_avenue", (62.0, -19.0), 80, "r41_apc")]:
    z = -0.15 if y < -11 else 0.0
    C.marker(f"VEH_{vid}", (x, y, z), yaw=yaw, props={"vehicle": veh, "faction": "r41", "state": "off"})
# 추락한 드론 (모두 떨어졌다). drone_4는 고가 앞 잔해 둑 자리라 고가 밑 북쪽 보도로 옮겼다
for pid, (x, y, z), model, look in [("drone_1", (6.0, -4.0, 0.25), "drones/drone_recon.glb", (8, -2, -1.5)),
                                    ("drone_2", (35.2, 6.4, 0.25), "drones/drone_swarm.glb", (33, 8, -1.2)),
                                    ("drone_3", (-14.0, 10.5, 0.2), "drones/drone_recon.glb", (-16, 12, -1.0)),
                                    ("drone_4", (104.0, -13.6, 0.25), "drones/drone_swarm.glb", (106, -11.6, -1.15))]:
    C.prop(pid, (x, y, z), model, look=look)
# B5 숨은 시민 셋 (창고 안쪽 구석, 그 자리에 남는다)
for nid, (x, y), model, pose, face in [("civ_a", (83.8, -44.9), "characters/crowd_elf_b.glb", "cower", (81.6, -42.4)),
                                       ("civ_b", (85.0, -44.4), "characters/crowd_elf_d.glb", "sit_hunch", (82, -42.8)),
                                       ("civ_c", (86.3, -45.05), "characters/crowd_elf_f.glb", "sit_wall", (83, -43.5))]:
    C.npc(nid, (x, y, 0.0), model, pose=pose, name="시민", face=face)
# 분대 모이는·기다리는 자리
MARKS = {
    "crawl": (59.4, -4.6, 0), "bar": (60.5, 1.0, 1.03), "sidedoor": (59.0, 0.3, 0),
    "wait_side": (58.2, -2.0, 0), "wait_side_1": (58.4, -0.8, 0), "wait_side_2": (58.4, -2.0, 0),
    "wait_side_3": (58.4, -3.2, 0), "wait_side_4": (57.0, -5.5, 0),
    "rg_lobby": (65.5, -0.4, 0), "upstairs": (67.0, -8.5, E1_2F),
    "window_1": (65.4, -9.7, E1_2F), "window_2": (67.0, -9.7, E1_2F), "window_3": (70.4, -9.7, E1_2F),
    "window_4": (72.6, -9.7, E1_2F),
    "cross_n": (82.0, -11.7, 0), "cross_n_1": (80.8, -11.6, 0), "cross_n_2": (82.0, -11.7, 0),
    "cross_n_3": (83.2, -11.6, 0), "cross_n_4": (84.4, -11.2, 0),
    "cross_s": (80.6, -30.0, 0), "cross_s_1": (81.6, -30.2, 0), "cross_s_2": (82.6, -29.8, 0),
    "store": (84.0, -32.0, 0), "rg_store": (80.5, -38.5, 0),
    "rg_lane": (80.4, -48.6, 0), "lane": (98.0, -49.5, 0), "collapse": (91.0, -21.0, 3.0),
}
for k, p in MARKS.items():
    C.marker(f"MARK_{k}", p)
# 엄폐 자리 (−Y가 적 쪽)
for cid, p, face, h in [("planter82", (82.0, -11.7, 0), (82, -24), "low"), ("car_n", (83.2, -14.7, -0.15), (83, -24), "low"),
                        ("car_s", (77.8, -30.1, 0), (72, -24), "low"), ("stub_1", (65.4, -9.8, E1_2F), (66, -24), "low"),
                        ("stub_2", (70.4, -9.8, E1_2F), (70, -24), "low"), ("stub_3", (72.6, -9.8, E1_2F), (74, -24), "low"),
                        ("lobby_win", (60.7, -2.6, 0), (50, -2.6), "low"), ("counter", (86.9, -35.6, 0), (80, -35.6), "low"),
                        ("lane_rubble", (88.4, -50.0, 0), (107, -50.6), "low"), ("lane_crate", (97.7, -49.4, 0), (107, -50.6), "low"),
                        ("lane_pillar", (94.2, -45.0, 0), (107, -50.6), "high")]:
    C.marker(f"COVER_{cid}", p, face=face, props={"height": h})
# 트리거와 목표 지점
C.group("triggers")
rk.trig(C, "alley", 19, 23, -1, 14, 0, 3)
rk.trig(C, "alley_end", 50, 54, -1, 14, 0, 3)
rk.trig(C, "sidedoor", 56, 60, -6, 2, -0.5, 3)
rk.trig(C, "lobby", 61.5, 64.5, -6, -3, -0.5, 2.6)
rk.trig(C, "ramp_top", 69.5, 72.5, -6.6, -4.6, 2.6, 5.0)
rk.trig(C, "window", 60.3, 75.7, -10.5, -8.0, 2.6, 5.4)
rk.trig(C, "apron_top", 60.2, 63.2, -12.0, -10.3, 2.4, 4.6)
# 예전 이름: 큰길에 닿음 = 벽판 비탈 발치 북쪽 보도 (지금 대본의 「→ 고가 밑」 목표 바꿈이 여기서 걸린다)
rk.trig(C, "avenue", 77.8, 81.6, -14.6, -9.0, -0.5, 3)
rk.trig(C, "cross_s", 77, 86, -31.4, -28.4, -0.5, 3)
rk.trig(C, "store", 82, 86, -34, -31.6, -0.5, 3)
rk.trig(C, "store_back", 77.3, 80.2, -48.0, -45.8, -0.5, 3)
rk.trig(C, "lane", 86, 92, -53.2, -46.0, -0.5, 3)
rk.trig(C, "underpass", 94, 106, -36, -32, -0.5, 3)
rk.trig(C, "mute", 95, 99, -30, -12, -0.5, 3)
C.group("markers")
C.marker("MARK_alley_end", (52.0, 6.0, 0))
C.marker("MARK_avenue", (79.6, -12.6, 0))
C.marker("MARK_underpass", (100.0, -34.0, 0))
C.marker("MARK_mute", (100.0, -18.0, -0.15))
C.marker("MARK_cityhall", (0, 19.0, Z_TOP))
# 뮤트 (개발용 자리표시 조우 ?nochain=1: 고가 밑 모닥불 곁에 서서 남쪽 통로에서 오는 분대를 본다)
C.npc("mute", (97.4, -28.8, 0.0), "characters/mute.glb", pose="cross_arms", name="뮤트", face=(100, -40))
C.marker("WP_mute_01", (99.0, -33.6, 0.0))

# ---------------------------------------------------------------- 뮤트 조우 컷신 A2_MUTE (src/game/missions/cine/a2Mute.ts)
# 출연진은 levels/cine_ruins.glb(겹침 세트)에 이 자리 그대로 있다. 리타가 실제로 멈춘 자리가 기준점(MARK_mute_rita)에서 벗어난 만큼
# 컷신이 카메라(분대 쪽 끝)·경로점을 옮긴다. 좌표: art/blender/lib/m4_mute_stage.py
C.marker("MARK_mute_rita", ms.RITA, face=(100, -18))
C.marker("MARK_mute_perch", (ms.MUTE[0], ms.MUTE[1], ms.MUTE_SEAT))
C.marker("WP_mute_land", ms.MUTE_LAND)
C.marker("WP_mute_aside", ms.MUTE_ASIDE)
for i, p in enumerate(ms.THREAD, start=1):
    C.marker(f"WP_thread_{i:02d}", p)
for i, p in enumerate(ms.RITA_GO, start=1):
    C.marker(f"WP_rita_go_{i:02d}", p)
RX, RY, _ = ms.RITA
MX, MY, _ = ms.MUTE
# mute_a: 고가 동쪽 위에서 큰길 서쪽(R41 잔당의 불·마젠타 발광봉, 안개 속 시청 쪽) → 크레인 다운, 고가 밑에 웅크린 분대
# (상판 동쪽 끝 밖으로 내려오며, 상판 끝 밑으로 분대가 보이는 쪽을 먼저 본다: 끝면이 화면을 덮지 않게)
# 큰길 가운데 줄 위로 내려온다 (남쪽 상가 정면(y -31.4)이 화면을 덮거나 분대를 가리지 않게)
C.cam("mute_a", [
    (0.0, (111.0, -21.5, 15.5), (40.0, -6.0, 8.0), 40),
    (4.2, (109.6, -19.8, 8.0), (100.6, -33.0, 1.6), 42),
    (7.2, (107.4, -24.0, 3.2), (100.4, -35.8, 1.0), 43),
    (10.0, (102.8, -31.6, 1.3), (RX - 0.1, RY - 0.6, 0.8), 44),
])
# mute_c: 리타 오른쪽 낮은 곳에서 북서쪽 위, 상판 더미 끝에 걸터앉은 뮤트. 그 너머 고가 서쪽 끝 밖 하늘에 달
# (M4의 두 달은 안개(16~130 m) 너머라 놀이 중에는 보이지 않는다: 컷신 동안만 안개를 받지 않게 한다, a2Mute.ts)
C.cam("mute_c", [
    (0.0, (RX + 1.0, RY - 0.15, 0.75), (MX, MY, ms.MUTE_SEAT + 0.68), 30),
    (8.0, (RX + 1.3, RY + 0.2, 0.85), (MX, MY, ms.MUTE_SEAT + 0.63), 26),
])
# mute_d: 리타 오른쪽 어깨 위 → 내려선 뮤트 (투샷). 리타는 뮤트 쪽(북서)으로 돌아 있다
LX, LY, _ = ms.MUTE_LAND
C.cam("mute_d", [
    (0.0, (RX + 1.29, RY - 0.68, 1.38), (LX, LY, 0.95), 33),
    (10.0, (RX + 1.06, RY - 0.48, 1.3), (LX, LY, 0.97), 28),
])
# mute_e: 불 동쪽에서 남서쪽: 손을 뻗은 뮤트, 뮤트를 보는 분대 얼굴 → 실을 따라 큰길 동쪽(잔해 둑의 틈)으로 돌아본다
C.cam("mute_e", [
    (0.0, (102.9, -29.6, 1.7), (RX - 0.4, RY + 0.7, 0.85), 42),
    (10.0, (102.6, -29.2, 1.6), (110.0, -21.4, 0.9), 40),
])
# mute_f: 큰길 고가 동쪽 끝(옆 골목 입구)에서 남쪽 통로를 돌아봄: 리타가 실을 따라 카메라 쪽으로 먼저 걸어오고 분대가 뒤따른다
C.cam("mute_f", [
    (0.0, (106.0, -24.6, 0.75), (RX + 0.4, RY + 1.0, 0.8), 38),
    (8.0, (106.9, -23.4, 0.8), (103.8, -27.8, 0.9), 42),
])

rk.blackout(C)
C.finish("levels/m4_ruins.glb", root_props={
    "sky": "#0d1220", "fog": "16,130", "sun": "-0.35,0.8,0.45", "sunColor": "#9fb2e6", "sunIntensity": 0.8,
    "ambient": 1.05, "hemiSky": "#4a5a86", "hemiGround": "#2a2430", "timeOfDay": "night", "music": "act2_ruins",
})
