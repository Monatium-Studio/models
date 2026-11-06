"""1막 M2 「방어선」 1부: 남서광장역 지하 → 터널 → 연락 통로 → 모나티엄 병기창고 → 정비 계단 (levels/m2_subway).

npm run model -- art/blender/levels/m2_subway.py              → public/models/levels/m2_subway.glb
PREVIEW=cut npm run model -- art/blender/levels/m2_subway.py  → public/models/_tmp/m2_subway_cut.glb (천장 없이 위에서 보기)
PREVIEW=col npm run model -- art/blender/levels/m2_subway.py  → public/models/_tmp/m2_subway_col.glb (+ 충돌 박스 붉게)
npm run shot -- levels/m2_subway.glb --views top,34

[원작] 개전 당일 R41이 모나티엄으로 밀려든다. 엘프는 지구제 총기·탄약을 들여와 쓴다. R41 전파 교란기가 무선망을 끊는다.
[오리지널] D-DAY 08:41. 재밍으로 지휘 무전이 끊긴 진압반 특수작전부 1분대가 서부선 남서광장역 승강장에서 터널과
연락 통로를 지나 모나티엄 병기창고(MNT-A)에 닿아, 지구에서 들여온 구 미군 화기(M4A1, M249, M870, M17, M67, M72)를
꺼낸다. R41이 차량 경사로 방폭문을 날리고 내려오고, 분대는 정비 계단으로 모노레일 선로를 향해 오른다. 기갑병기(M1A1 등)는
여기가 아니라 별관 제2차고에 있다(표지만). 지하철·병기창고의 배치와 이름은 전부 [오리지널].

한 좌표: 이 레벨은 루트를 SHARED만큼 옮겨 내보낸다 (선로 구역 m2_monorail과 같은 월드 좌표). 정비 계단실(B3 → 지상
1층 → 선로 계단탑)은 m2_monorail.py가 가지고, 두 레벨이 함께 붙어 걸어서 이어진다. 아래 좌표는 옮기기 전 값이다.

좌표 (Blender, m, +X = 동쪽 = 시청 방면, +Y = 북쪽)
  1 승강장    x -26..18 섬식(폭 7.6 m, 윗면 z 0), 궤도 바닥 z -1. 북쪽 선로에 멈춘 전동차 3칸(닫힘). 서쪽 끝 대합실
              계단은 셔터와 진압반 바리케이드로 막혔다(M1에서 내려온 길).
  2 터널      x 24.4..112 복선 박스 터널(폭 11.6 m, 가운데 기둥 줄, 남벽 대피 보도 z -0.75). 남쪽 선로 x 40..64.6에
              멈춘 2칸(끝 비상문 + 하차 계단으로 관통, 북쪽 문 몇 개 열림). x 104부터 무너짐(천장 구멍 햇빛).
  3 연락 통로 터널 남벽 x 96 문(DOOR_passage) → 남 → 서 → 남 (약 38 m, 폭 2.4 m) → 전실 → 방폭문(DOOR_armory).
  4 병기창고  x 67..97, y -51..-31, 바닥 z -0.75, 높이 5.5 m. 동벽 차량 경사로 방폭문(DOOR_ramp) 뒤로 경사로가
              지상까지(R41 돌입로), 서벽 정비 계단(x 61.5..66, 두 번 꺾어 z 4.05 윗층참까지).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import bpy  # noqa: E402
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import monatium_subway_kit as sk  # noqa: E402
from mathutils import Vector  # noqa: E402

PREVIEW = os.environ.get("PREVIEW", "")
if PREVIEW in ("cut", "col"):
    sk.CEIL["on"] = False

cb.reset()
C = mk.City("m2_subway")
# 선로 구역(m2_monorail)과 한 좌표: 내보낼 때 루트를 이만큼 옮긴다 (Blender x, y, z. m2_monorail.py SUB와 같은 값)
SHARED = (-296.35, -2.6, -8.83)

# ---------------------------------------------------------------- 높이·배치 상수
ZB = -1.0           # 궤도 바닥
ZP = 0.0            # 승강장·전동차 바닥
ZW = -0.75          # 대피 보도·연락 통로·병기창고 바닥
SX0, SX1, SY, ZC_ST = -30.0, 24.0, 9.4, 4.2     # 역 상자
PX0, PX1, PY = -26.0, 18.0, 3.8                 # 승강장
TY_ST = 6.2                                     # 역 안 선로 중심 (±)
TX0, TX1, TW, TY, ZC_T = 24.4, 112.0, 5.8, 2.9, 3.4   # 터널 x, 반폭, 선로 중심(±), 천장
CAVE_X = 104.0
PAS_X = 96.0                                    # 연락 통로 문 중심 x
AX0, AX1, AY0, AY1, AH = 67.0, 97.0, -51.0, -31.0, 5.5   # 병기창고 안쪽
ZC_A = ZW + AH
RAMP_X0, RAMP_FLAT, RAMP_TOP, RAMP_X1, RAMP_Z = 98.0, 101.0, 125.0, 131.0, ZW + 5.2
RAMP_Y0, RAMP_Y1 = -43.3, -36.7


def ramp_z(x):
    if x <= RAMP_FLAT:
        return ZW
    if x >= RAMP_TOP:
        return RAMP_Z
    return ZW + (x - RAMP_FLAT) / (RAMP_TOP - RAMP_FLAT) * (RAMP_Z - ZW)


def enemy(eid, group, kind, loc, behavior, *, face=None, extra=None):
    p = {"kind": kind, "group": group, "behavior": behavior, "spawn": "manual"}
    p.update(extra or {})
    C.marker(f"ENEMY_{eid}", loc, face=face or (loc[0] - 10.0, loc[1]), props=p)


def hold(section, center, who_pos, face):
    C.marker(f"MARK_hold_{section}", center, face=face)
    for who, pos in who_pos.items():
        C.marker(f"MARK_hold_{section}_{who}", pos, face=face)


def cover(cid, loc, height, face):
    C.marker(f"COVER_{cid}", loc, face=face, props={"height": height})


def pickup(pid, loc, weapon, muzzle=(1, 0)):
    """PICKUP_: 표면 위 +0.04 m. 총구가 마커 -Y(= muzzle 방향)."""
    C.marker(f"PICKUP_{pid}", (loc[0], loc[1], loc[2] + 0.04), face=(loc[0] + muzzle[0], loc[1] + muzzle[1]),
             props={"weapon": weapon, "lay": "side"})


# ================================================================ 1. 승강장 (남서광장역, 서부선)
C.group("station")
sk.station_hall(C, SX0, SX1, SY, z_bed=ZB, z_plat=ZP, z_ceil=ZC_ST, ends={"e": [(-TW, TW, ZB, ZC_T)]})
sk.island_platform(C, PX0, PX1, -PY, PY, z_top=ZP, z_bed=ZB, steps=("w", "e"))

# 서쪽 끝: 방수문 (정전 때 자동으로 닫힘) [오리지널]
for s in (-1, 1):
    ya, yb = sorted((s * 3.95, s * 8.7))
    sk.floodgate(C, SX0, ya, yb, ZB, 2.9, 1)
    sk.hazard_frame(C, (SX0 + 0.03, s * 6.3, (ZB + 2.9) / 2), (1, 0, 0), 4.8, 3.9, up=(0, 0, 1))

# 기둥 (가운데 한 줄) + 비상등(호박색)
ls_st_a = sk.LampSet("emerg_02", "a")
for x in (-24.0, -8.0, -1.0, 6.0, 13.0):
    sk.round_pillar(C, x, 0.0, z0=ZP, z1=ZC_ST, logo_n="W12", ls=ls_st_a)

# 대합실 계단 (서쪽, 셔터 내림) + 진압반 바리케이드 [오리지널: M1에서 분대가 내려와 막은 길]
HX0, HX1, HY = -20.4, -12.2, 1.3
sk.stair_flight(C, "x", -1.15, 1.15, -12.6, -1, ZP, ZP + 2.4, 16, tread=0.28, key="concrete_d", top_key="pave_d",
                z_floor=ZP)
C.box("concrete_d", HX0, -16.8, -1.15, 1.15, ZP, ZP + 2.4, col=True)
C.box("pave_d", HX0, -16.8, -1.15, 1.15, ZP + 2.4, ZP + 2.42, kind="detail")
for s in (-1, 1):
    ya, yb = sorted((s * HY, s * (HY + 0.15)))
    C.box("navy", HX0, HX1, ya, yb, ZP, ZP + 1.0, col=True)
    C.col(HX0, HX1, ya, yb, ZP, ZC_ST)
    C.rect("glass_a", ((HX0 + HX1) / 2, s * (HY + 0.075), ZP + 2.6), (0, s, 0), HX1 - HX0, 3.1, lift=0.08)
    C.rect("glass_a", ((HX0 + HX1) / 2, s * (HY + 0.075), ZP + 2.6), (0, -s, 0), HX1 - HX0, 3.1, lift=0.08)
    for k in range(5):
        xx = HX0 + (HX1 - HX0) * k / 4
        C.box("steel", xx - 0.04, xx + 0.04, ya, yb, ZP + 1.0, ZC_ST, kind="detail")
    C.box("steel", HX0, HX1, ya, yb, ZC_ST - 0.12, ZC_ST, kind="detail")
    C.strip("glow", (HX0, s * (HY + 0.15), ZP + 0.9), (HX1, s * (HY + 0.15), ZP + 0.9), 0.04, (0, s, 0), lift=0.004)
# 셔터 (닫힘) + 뒷벽
C.box("steel_d", HX0 - 0.2, HX0, -HY, HY, ZP + 2.4, ZC_ST, col=True)
z = ZP + 2.55
while z < ZC_ST - 0.1:
    C.strip("metal", (HX0 + 0.005, -HY, z), (HX0 + 0.005, HY, z), 0.03, (1, 0, 0), lift=0.004)
    z += 0.16
C.text("hazard", "셔터 내림 · CLOSED", 0.14, (HX0 + 0.01, 0.0, ZP + 3.55), (1, 0, 0), lift=0.008)
# 계단 입구 머리판 (표지·비상등 자리)
C.box("navy", HX1 - 0.12, HX1, -HY - 0.16, HY + 0.16, ZC_ST - 1.15, ZC_ST, col=True)   # 칸막이 난간 끝보다 1 cm 밖
sk.sign(C, (HX1 + 0.02, 0.0, ZC_ST - 0.42), (1, 0, 0), 2.4, 0.5,
        [("↑ 대합실 · 출구 1·2", 0.15, "white", 0.06, 0.0), ("CONCOURSE · EXIT", 0.08, "glow", -0.13, 0.0)],
        depth=0.04)
mk.barricade(C, HX1 + 0.9, 0.0, yaw=90, z=ZP, w=2.5)
mk.sandbag_wall(C, HX1 + 1.6, 0.9, yaw=90, z=ZP, n=3, rows=2)

# 벤치 · 자판기 · 휴지통 · 진압반 보급 상자 (충돌은 도시 키트 소품이 직접 단다: 좌판·등판, 몸체)
for x in (-4.5, 9.5):
    mk.bench(C, x, -0.72, yaw=0, z=ZP)
    mk.bench(C, x, 0.72, yaw=180, z=ZP)
mk.vending(C, -11.4, 2.05, yaw=90, z=ZP)
for (x, y) in ((-10.6, -2.4), (16.4, 2.6)):
    mk.trash_bin(C, x, y, z=ZP)
# 진압반 보급 상자 (남보라 + 청록 띠) 두 개: 분대가 들고 내려온 것
for (x, y, l) in ((-2.6, 2.4, 1.1), (-2.6, 1.6, 0.8)):
    C.box("violet", x - l / 2, x + l / 2, y - 0.3, y + 0.3, ZP, ZP + 0.45, kind="detail")
    C.box("violet_d", x - l / 2 - 0.01, x + l / 2 + 0.01, y - 0.31, y + 0.31, ZP + 0.4, ZP + 0.46, kind="detail")
    C.strip("teal", (x - l / 2, y - 0.305, ZP + 0.22), (x + l / 2, y - 0.305, ZP + 0.22), 0.08, (0, -1, 0), lift=0.004)
    C.col(x - l / 2, x + l / 2, y - 0.3, y + 0.3, ZP, ZP + 0.46)
C.text("white", "진압반 보급 · SUPPRESSION UNIT", 0.07, (-2.6, 2.4 - 0.31, ZP + 0.33), (0, -1, 0), lift=0.006)

# 역 이름판, 노선도, 꺼진 광고판 (남벽은 +Y를, 북벽은 -Y를 본다)
for x in (-17.0, 0.5, 15.0):
    sk.name_board(C, (x, -SY + 0.03, ZP + 1.68), (0, 1, 0), "남서광장", "SOUTHWEST SQUARE",
                  left="상가거리 →", right="← 서부차고")
sk.name_board(C, (19.5, SY - 0.03, ZP + 1.68), (0, -1, 0), "남서광장", "SOUTHWEST SQUARE",
              left="← 서부차고", right="상가거리 →")
sk.line_map(C, (-8.3, -SY + 0.03, ZP + 1.68), (0, 1, 0), ["서부차고", "남서광장", "상가거리", "중앙로", "시청"], "남서광장")
for x in (7.6, -25.5):
    C.plate("navy_l", hw.rrect(2.6, 1.1, 0.1, 2), (x, -SY + 0.03, ZP + 1.68), (0, 1, 0), 0.05, kind="detail")
    C.rect("screen", (x, -SY + 0.08, ZP + 1.68), (0, 1, 0), 2.3, 0.85, lift=0.006)
for (x, y, n_) in ((-27.5, -SY, (0, 1, 0)), (22.5, SY, (0, -1, 0))):
    mk.cctv_cam(C, (x, y + n_[1] * 0.03, ZC_ST - 0.5), Vector(n_), Vector((n_[1], 0, 0)) * -1)

# 매단 표지 (판이 ±X를 본다: 동쪽으로 걷는 사람은 -X 면을 본다)
for x in (-5.5, 10.5):
    sk.hanging_sign(C, (x, 0.0, ZC_ST - 0.95), 3.0, 0.55,
                    front=[("↑ 대합실 · 출구 1·2", 0.17, "white", 0.07), ("CONCOURSE · EXIT", 0.08, "glow", -0.15)],
                    back=[("↑ 시청 방면 · 서부선", 0.17, "white", 0.07), ("FOR CITY HALL · W LINE", 0.08, "glow", -0.15)],
                    axis="x", z_ceil=ZC_ST)

# 멈춘 전동차 (북쪽 선로, 닫힘)
sk.train(C, -24.2, TY_ST, ZP, ZB, 3, walk=False, nums=["W-2011", "W-2012", "W-2013"], plain_side=1)

# 비상등 (적색: 양 벽, 호박색: 기둥·계단)
ls_st_r = sk.LampSet("emerg_01", "r")
for x in (-25.0, -14.0, -3.0, 8.0, 19.0):
    sk.emerg_lamp(C, ls_st_r, (x, -SY, ZP + 3.05), (0, 1, 0))
    sk.emerg_lamp(C, ls_st_r, (x + 4.5, SY, ZP + 3.05), (0, -1, 0))
sk.emerg_lamp(C, ls_st_a, (HX1 + 0.02, 0.0, ZC_ST - 1.0), (1, 0, 0), halo=0.6)
for x in (PX0 + 0.2, PX1 - 0.2):
    sk.ceiling_lamp(C, ls_st_a, (x, 0.0, ZC_ST - 0.2), halo=0.0)
ls_st_r.emit(C)
ls_st_a.emit(C)

# ---------------------------------------------------------------- 승강장 마커
C.marker("SPAWN_player", (3.0, -1.6, ZP), face=(12.0, -1.6))
for who, pos in {"sabre": (5.2, 1.6), "rona": (4.6, -2.6), "jesty": (1.0, 2.3), "karen": (0.6, -1.2)}.items():
    C.marker(f"ALLY_{who}", (pos[0], pos[1], ZP), face=(12.0, pos[1]), props={"who": who, "behavior": "follow"})
hold("platform", (11.5, -1.8, ZP), {"sabre": (16.2, 1.7, ZP), "rona": (16.2, -1.7, ZP), "jesty": (12.0, 2.4, ZP),
                                    "karen": (11.0, -2.7, ZP)}, face=(30.0, 0.0))

# ================================================================ 궤도 (역 + 터널)
C.group("track")
for s in (1, -1):
    pts = [(SX0, s * TY_ST), (14.0, s * TY_ST)] + sk.s_curve(14.0, 32.0, s * TY_ST, s * TY)[1:] + [(CAVE_X + 1.5, s * TY)]
    sk.track(C, pts, ZB, third=s, pitch=1.25)

# ================================================================ 2. 터널
C.group("tunnel")
ls_tu_r = sk.LampSet("emerg_03", "r")
ls_tu_a = sk.LampSet("emerg_04", "a")
sk.tunnel(C, TX0, TX1, -TW, TW, z_bed=ZB, z_ceil=ZC_T, walkway=(-1, 1.0, ZW - ZB, (TX0, CAVE_X)),
          pillars=(0.0, 30.0, 102.0, 6.0, 0.6), openings_s=[(PAS_X - 0.7, PAS_X + 0.7, ZW, ZW + 2.0)],
          ceil_holes=[(105.0, 109.0, 0.5, 4.5)], ls_red=ls_tu_r)
C.box("tunnel", TX1, TX1 + 0.5, -TW - 0.5, TW + 0.5, ZB - 0.3, ZC_T + 0.4, col=True)
sk.cave_in(C, CAVE_X, TX1, -TW, TW, z_bed=ZB, z_ceil=ZC_T, hole=(105.0, 109.0, 0.5, 4.5), tracks=(TY, -TY))
C.fx("spark_1", (106.4, 2.2, ZC_T - 1.2), dir="0,-1,0", strength=0.5)

# 터널 입구 표지 (역 쪽 면)
sk.sign(C, (SX1 - 0.02, 0.0, ZC_T + 0.4), (-1, 0, 0), 3.6, 0.55,
        [("서부선 하행 · 상가거리 방면", 0.16, "white", 0.07, 0.0), ("W LINE · TUNNEL W-12", 0.08, "glow", -0.15, 0.0)],
        depth=0.04)
sk.hazard_frame(C, (SX1 - 0.01, 0.0, (ZB + ZC_T) / 2), (-1, 0, 0), 2 * TW, ZC_T - ZB, band=0.2)

# 멈춘 전동차 2칸 (남쪽 선로, 끝 비상문으로 관통, 북쪽 문 일부 열림)
tx0, tx1 = sk.train(C, 40.0, -TY, ZP, ZB, 2, walk=True, open_side=1, open_map={0: (1,), 1: (0, 2)},
                    nums=["W-2071", "W-2072"], lamps=ls_tu_a)
sk.detrain_steps(C, tx0, -1, -TY, ZP, ZB)
sk.detrain_steps(C, tx1, 1, -TY, ZP, ZB)

# 신호기, 거리표
sk.signal_post(C, 31.0, 4.95, ZB, (-1, 0))
sk.signal_post(C, 99.0, -5.35, ZW, (-1, 0))
for x in (50.0, 75.0, 100.0):
    sk.km_plate(C, (x, TW - 0.01, ZB + 1.6), (0, -1, 0), f"W {12 + (x - 24) / 100:.2f} km")

# 대피 유도 (보도 낮은 호박색 등 + 시안 표지)
x = TX0 + 4.0
while x < CAVE_X - 1:
    if abs(x - PAS_X) > 2.0:
        sk.emerg_lamp(C, ls_tu_a, (x, -TW, ZW + 0.45), (0, 1, 0), w=0.26, h=0.1, halo=0.45)
        C.col(x - 0.19, x + 0.19, -TW, -TW + 0.11, ZW + 0.34, ZW + 0.56)   # 보도 높이 등 받침·렌즈 (벽에서 0.11 m)
    x += 8.0
for x in (58.0, 82.0):
    sk.sign(C, (x, -TW + 0.01, ZW + 1.55), (0, 1, 0), 2.2, 0.42,
            [("← 비상 대피 · 연락 통로", 0.13, "glow", 0.05, 0.0), ("EMERGENCY EXIT · CROSS PASSAGE", 0.065, "white", -0.12, 0.0)],
            depth=0.03, key="navy")

# 연락 통로 문 (터널 남벽, 닫힘 → 동쪽 벽 속으로 밀림)
pz0, pz1 = ZW, ZW + 2.0
sk.hazard_frame(C, (PAS_X, -TW + 0.005, (pz0 + pz1) / 2), (0, 1, 0), 1.4, 2.0)
sk.sign(C, (PAS_X, -TW + 0.01, pz1 + 0.5), (0, 1, 0), 2.0, 0.5,
        [("연락 통로 · 관계자 외 출입 금지", 0.11, "white", 0.08, 0.0), ("CROSS PASSAGE · MNT-A", 0.08, "glow", -0.12, 0.0)],
        depth=0.03)
sk.beacon(C, ls_tu_a, (PAS_X - 1.25, -TW + 0.3, pz1 + 0.15), wall_normal=(0, 1, 0), halo=0.7)


def _passage_door_parts():
    def win(b):
        for y in (-5.94, -6.16):
            mk._bm_box(b, PAS_X - 0.25, PAS_X + 0.25, y - 0.005, y + 0.005, ZW + 1.15, ZW + 1.6)

    def stripes(b):
        for y in (-5.94, -6.16):
            mk._bm_box(b, PAS_X - 0.7, PAS_X + 0.7, y - 0.006, y + 0.006, ZW + 0.12, ZW + 0.3)

    def handle(b):
        for y in (-5.92, -6.18):
            mk._bm_box(b, PAS_X - 0.58, PAS_X - 0.5, y - 0.02, y + 0.02, ZW + 0.75, ZW + 1.15)
    return [("glass_d", win), ("hazard", stripes), ("dark", handle)]


sk.door(C, "passage", (PAS_X - 0.72, PAS_X + 0.72, -6.15, -5.95, ZW, ZW + 2.0), "1.5,0,0", key="steel",
        parts=_passage_door_parts())

# 적 쪽 엄폐물: 탈선한 정비 수레 + R41 보급 상자
C.box("steel_d", 78.4, 81.6, 2.15, 3.65, ZB + 0.32, ZB + 0.62, kind="detail")
for xx in (78.9, 81.1):
    for yy in (2.3, 3.5):
        C.cyl("dark", (xx, yy - 0.06, ZB + 0.2), (xx, yy + 0.06, ZB + 0.2), 0.2, segs=10, kind="detail")
for xx in (79.3, 80.7):
    C.cyl("navy_l", (xx, 2.3, ZB + 1.05), (xx, 3.5, ZB + 1.05), 0.42, segs=14, kind="detail")
    C.cyl("hazard", (xx, 2.28, ZB + 1.05), (xx, 2.3, ZB + 1.05), 0.44, segs=14, kind="detail")
C.col(78.4, 81.6, 2.15, 3.65, ZB, ZB + 1.47)
for (x, y, l, w, h) in ((86.6, -2.2, 1.3, 0.8, 0.95), (90.4, 1.7, 1.2, 0.9, 0.85), (93.2, -0.9, 0.9, 0.7, 0.6)):
    C.box("r41_shell", x - l / 2, x + l / 2, y - w / 2, y + w / 2, ZB, ZB + h, kind="detail")
    C.box("amber", x - l / 2 - 0.01, x + l / 2 + 0.01, y - w / 2 - 0.01, y + w / 2 + 0.01, ZB + h - 0.2, ZB + h - 0.14,
          kind="detail")
    C.box("r41_metal", x - l / 2 + 0.1, x + l / 2 - 0.1, y - w / 2 + 0.1, y + w / 2 - 0.1, ZB + h, ZB + h + 0.05,
          kind="detail")
    C.col(x - l / 2, x + l / 2, y - w / 2, y + w / 2, ZB, ZB + h)
ls_tu_r.emit(C)
ls_tu_a.emit(C)

# ---------------------------------------------------------------- 터널 마커
C.marker("SPAWN_tunnel", (27.0, -1.2, ZB), face=(40.0, -1.2))
C.marker("MARK_tunnel", (TX0, 0.0, ZB))
C.marker("MARK_passage", (PAS_X, -5.3, ZW))
sk.trig(C, "tunnel", TX0, 28.0, -TW, TW, ZB - 0.5, ZB + 3.0)
sk.trig(C, "tunnel_mid", 46.0, 49.0, -TW, TW, ZB - 0.5, ZP + 3.0)
hold("tunnel", (35.0, -0.8, ZB), {"sabre": (35.3, 0.0, ZB), "rona": (37.2, -3.7, ZB), "jesty": (35.8, 2.6, ZB),
                                  "karen": (36.6, -5.3, ZW)}, face=(80.0, 0.0))
for i, (x, y, z, hgt) in enumerate(((35.3, 0.0, ZB, "high"), (41.3, 0.0, ZB, "high"), (47.3, 0.0, ZB, "high"),
                                    (53.3, 0.0, ZB, "high"), (59.3, 0.0, ZB, "high"), (65.3, 0.0, ZB, "high"),
                                    (67.4, -3.6, ZB, "low"), (71.3, 0.0, ZB, "high"), (77.9, 2.9, ZB, "low")), 1):
    cover(f"tunnel_{i:02d}", (x, y, z), hgt, face=(90.0, 0.0))
# 터널 팀 (열차 너머): 소총수 4 + 돌격 1, 정찰 드론 1
enemy("tunnel_01", "tunnel", "rifleman_a", (82.0, 2.9, ZB), "hold")
enemy("tunnel_02", "tunnel", "rifleman_b", (78.9, -0.1, ZB), "advance")
enemy("tunnel_03", "tunnel", "rifleman_c", (87.6, -2.2, ZB), "hold")
enemy("tunnel_04", "tunnel", "rifleman_a", (91.4, 1.7, ZB), "advance")
enemy("tunnel_05", "tunnel", "assault", (85.0, 0.9, ZB), "rush")
enemy("tunnel_drone_01", "tunnel_drone", "drone", (84.0, -1.5, ZB + 2.5), "patrol")

# ================================================================ 3. 연락 통로 (남 → 서 → 남 → 전실)
C.group("passage")
ls_pa = sk.LampSet("emerg_05", "r")
PH = 2.6
# P1: 터널 문에서 남쪽으로
# 통로끼리 이어지는 구멍은 바닥 밑까지 비운다(ZW - 0.5): 문턱 상자를 남기면 옆 칸 바닥 판과 겹쳐 윗면이 깜빡인다.
# 그 자리 바닥은 옆 칸 바닥 판이 덮는다. 전실 구멍 위 상인방은 1 cm 올려 P3 천장 판 속에 묻는다(밑면이 같은 높이였다)
sk.room(C, 94.8, 97.2, -17.2, -6.3, ZW, PH, walls="esw", openings={"w": [(-17.2, -14.8, ZW - 0.5, ZW + PH)]})
# P2: 서쪽으로
sk.room(C, 80.8, 94.8, -17.2, -14.8, ZW, PH, walls="nsw",
        openings={"n": [(94.8, 95.2, ZW - 0.5, ZW + PH + 0.5)], "s": [(80.8, 83.2, ZW - 0.5, ZW + PH)]})
# P3: 남쪽으로
sk.room(C, 80.8, 83.2, -25.0, -17.2, ZW, PH, walls="ew")
# 전실 (방폭문 앞)
sk.room(C, 78.5, 85.5, -30.0, -25.0, ZW, 3.6, walls="new", openings={"n": [(80.8, 83.2, ZW - 0.5, ZW + PH + 0.01)]})
# 바닥 시안 네트워크 선 (길 안내)
for (p0, p1) in (((PAS_X, -6.4, ZW), (PAS_X, -16.0, ZW)), ((PAS_X, -16.0, ZW), (82.0, -16.0, ZW)),
                 ((82.0, -16.0, ZW), (82.0, -29.0, ZW))):
    C.strip("glow", p0, p1, 0.06, lift=0.012)
# 배관, 소화전, 전기실 문, 표지
sk.pipes(C, (96.6, -6.6, ZW + PH - 0.18), (96.6, -15.4, ZW + PH - 0.18), n=2, step=(-0.2, 0, 0))
sk.pipes(C, (96.2, -15.2, ZW + PH - 0.18), (81.4, -15.2, ZW + PH - 0.18), n=3, step=(0, -0.2, 0))
C.box("red", 94.82, 95.05, -10.6, -9.8, ZW + 0.7, ZW + 1.6, kind="detail")
C.rect("glass_a", (95.06, -10.2, ZW + 1.15), (1, 0, 0), 0.6, 0.7, lift=0.004)
C.text("white", "소화전", 0.08, (95.06, -10.2, ZW + 1.5), (1, 0, 0), lift=0.011)   # 유리판(0.004)과 7 mm
C.col(94.8, 95.05, -10.6, -9.8, ZW + 0.7, ZW + 1.6)    # 벽걸이 함 (밑은 비어 있다)
C.plate("navy", hw.rrect(1.1, 1.95, 0.08, 2), (88.0, -14.8 - 0.005, ZW + 0.98), (0, -1, 0), 0.05, kind="detail")
C.rect("steel", (88.0, -14.86, ZW + 0.95), (0, -1, 0), 0.9, 1.8, lift=0.004)
C.text("white", "전기실 · ELECTRICAL", 0.08, (88.0, -14.87, ZW + 1.55), (0, -1, 0), lift=0.006)
sk.sign(C, (97.2 - 0.01, -12.0, ZW + 1.75), (-1, 0, 0), 1.9, 0.4,
        [("병기창고 MNT-A →", 0.13, "white", 0.05, 0.0), ("ARMORY · 진압반 시설", 0.07, "glow", -0.11, 0.0)], depth=0.03)
sk.sign(C, (88.0, -17.2 + 0.01, ZW + 1.75), (0, 1, 0), 1.9, 0.4,
        [("← 병기창고 MNT-A", 0.13, "white", 0.05, 0.0), ("ARMORY · 진압반 시설", 0.07, "glow", -0.11, 0.0)], depth=0.03)
for (x, y) in ((96.0, -9.0), (96.0, -14.0), (91.0, -16.0), (85.0, -16.0), (82.0, -21.0)):
    sk.ceiling_lamp(C, ls_pa, (x, y, ZW + PH), r=0.12, halo=0.6)
# 전실: 방폭문 위 이름판, 사선 띠, 열쇠판, 벤치
sk.hazard_frame(C, (82.0, -30.0 + 0.005, ZW + 1.25), (0, 1, 0), 2.4, 2.5, band=0.22)
sk.sign(C, (82.0, -30.0 + 0.01, ZW + 3.05), (0, 1, 0), 4.6, 0.62,
        [("모나티엄 병기창고", 0.24, "white", 0.08, -0.25), ("MONATIUM ARMORY · MNT-A", 0.085, "glow", -0.19, -0.25)],
        logo=True, depth=0.04)
C.plate("navy", hw.rrect(0.3, 0.42, 0.05, 2), (84.1, -30.0 + 0.01, ZW + 1.3), (0, 1, 0), 0.06, kind="detail")
C.rect("glow", (84.1, -29.93, ZW + 1.4), (0, 1, 0), 0.18, 0.08, lift=0.006)
for k in range(3):
    C.rect("steel", (84.1 - 0.07 + k * 0.07, -29.93, ZW + 1.23), (0, 1, 0), 0.05, 0.05, lift=0.006)
mk.bench(C, 79.4, -25.6, yaw=180, z=ZW, length=1.4)
ls_pa.emit(C)

C.marker("MARK_armory_door", (82.0, -29.3, ZW))
sk.trig(C, "passage", 94.8, 97.2, -12.0, -7.0, ZW - 0.5, ZW + 3.0)
sk.trig(C, "armory_door", 78.5, 85.5, -30.0, -25.5, ZW - 0.5, ZW + 3.0)

# ================================================================ 4. 병기창고 (MNT-A)
C.group("armory")
ls_ar_r = sk.LampSet("emerg_06", "r", blink=1.6)
ls_ar_a = sk.LampSet("emerg_07", "a")
sk.room(C, AX0, AX1, AY0, AY1, ZW, AH, t=1.0, wall_key="concrete", floor_key="floor_ar", ceil_key="tunnel_d",
        band="violet", band_z=1.25, tile=2.0, grout="floor_ar_d",
        openings={"n": [(80.8, 83.2, ZW, ZW + 2.5)], "e": [(-42.5, -37.5, ZW, ZW + 3.6)],
                  "w": [(-34.4, -32.4, ZW, ZW + 2.3)]})
# 천장 보 + 평상 조명판 (LIGHT_main, 미션이 켬)
if sk.CEIL["on"]:
    for x in (70.0, 76.0, 82.0, 88.0, 94.0):
        C.box("steel_d", x - 0.15, x + 0.15, AY0, AY1, ZC_A - 0.45, ZC_A, kind="detail")
    C.cyl("steel", (AX0 + 0.5, -50.2, ZC_A - 0.6), (AX1 - 0.5, -50.2, ZC_A - 0.6), 0.32, segs=10, kind="detail",
          cap=False)
for i, x in enumerate((73.0, 79.0, 85.0, 91.0), 1):
    ls_main = sk.LampSet(f"main_{i:02d}", None, group="main", on=0, key="lamp", hexcol="#fff1c9", halo=False)
    for y in (-35.5, -41.0, -46.5):
        sk.main_panel(C, ls_main, x, y, ZC_A, 0.7, 2.4)
    ls_main.emit(C)

# 기둥 4개
for (x, y) in ((75.0, -38.0), (89.0, -38.0), (75.0, -45.0), (89.0, -45.0)):
    sk.column_sq(C, x, y, ZW, ZC_A)

# 가운데 거치대 줄 (양면) + 작업대 3개 (PICKUP 화기)
sk.weapon_rack(C, 79.0, -36.6, z=ZW, n=7, kind="m4", double=True, length=2.4, label="M4A1 · 5.56")
sk.weapon_rack(C, 85.0, -36.6, z=ZW, n=4, kind="m249", double=True, length=2.4, label="M249 · M870")
t1 = sk.work_table(C, 76.6, 79.0, -41.5, -40.5, ZW)
t2 = sk.work_table(C, 80.8, 83.2, -41.5, -40.5, ZW)
t3 = sk.work_table(C, 85.0, 87.4, -41.5, -40.5, ZW)
for (xa, lbl) in ((77.8, "M4A1"), (82.0, "M249"), (86.2, "M870")):
    C.text("white", lbl, 0.07, (xa, -41.5 - 0.005, ZW + 0.58), (0, -1, 0), lift=0.004)
# 서벽 소총 거치대 (단면)
for y in (-38.6, -41.4, -44.2):
    sk.weapon_rack(C, AX0 + 0.25, y, yaw=90, z=ZW, n=6, kind="m4" if y > -44 else "m870", length=2.4)
# 북벽: 진압반 방패 거치대(서) · 선반(동)
sk.riot_rack(C, 68.2, 73.6, AY1 - 0.3, ZW, side=-1, n=6)
sk.shelf_unit(C, 87.2, 91.8, AY1 - 0.62, AY1 - 0.05, ZW, h=2.3, seed=1)
sk.shelf_unit(C, 92.2, 96.8, AY1 - 0.62, AY1 - 0.05, ZW, h=2.3, seed=2)
# 남벽: 작업대 + 공구판, 선반
wb = sk.work_table(C, 76.0, 82.4, AY0 + 0.1, AY0 + 0.9, ZW)
sk.tool_board(C, 76.2, 82.2, AY0 + 0.0, ZW + 0.62, side=1)
for (x, y) in ((77.0, AY0 + 0.5), (81.5, AY0 + 0.45)):
    C.box("steel_d", x - 0.12, x + 0.12, y - 0.08, y + 0.08, wb, wb + 0.16, kind="detail")
sk.shelf_unit(C, 84.0, 90.0, AY0 + 0.05, AY0 + 0.65, ZW, h=2.3, seed=3)
# 탄약 철망 우리 (남서 모서리) + 안의 탄약 상자·탄약통
CG = (AX0 + 0.2, 73.6, AY0 + 0.2, -45.6)
sk.ammo_cage(C, CG[0], CG[1], CG[2], CG[3], ZW, h=2.4, gate=("n", 2.8, 1.4))
for (x, y, z, st) in ((68.2, -50.0, ZW, 1), (69.4, -50.0, ZW, 1), (68.2, -50.0, ZW + 0.5, 2), (72.5, -50.0, ZW, 1),
                      (72.5, -50.0, ZW + 0.5, 0), (68.4, -47.6, ZW, 1)):
    sk.us_crate(C, x, y, z, l=1.0, w=0.6, h=0.5, stencil=st, text_sides=(1,) if y < -49 else (1,), col=True)
sk.shelf_unit(C, 70.9, 73.3, -47.0, -46.4, ZW, h=1.6, levels=3, seed=4, fill=("od", "od_d"))
sk.ammo_cans(C, 70.2, -48.6, ZW, n=4)
sk.ammo_cans(C, 70.2, -48.2, ZW, n=3)
# 탄약 상자 (PICKUP_ammo)
a1 = sk.us_crate(C, 72.7, -44.8, ZW, l=0.8, w=0.5, h=0.42, stencil=1, key="od", text_sides=(1,))
a2 = sk.us_crate(C, 84.5, -48.3, ZW, l=0.8, w=0.5, h=0.42, stencil=1, key="od", text_sides=(1,))
# 화기 상자 (PICKUP m67, m72)
c67 = sk.us_crate(C, 84.0, -45.0, ZW, l=0.8, w=0.55, h=0.45, stencil=1, text_sides=(1,))
c72 = sk.us_crate(C, 80.0, -45.0, ZW, l=1.3, w=0.55, h=0.45, stencil=2, text_sides=(1,))
# 엄폐 상자 더미 (경사로 돌입 대비, 차량 통로 y -42.5..-37.5는 비움)
stacks = [(91.4, -35.0, 2, 1.2, 0.8), (93.6, -33.0, 1, 1.2, 0.8), (92.4, -45.6, 2, 1.2, 0.8), (87.6, -48.2, 1, 1.4, 0.7),
          (94.4, -47.6, 1, 1.0, 0.7), (95.6, -49.6, 2, 1.0, 0.7)]
for i, (x, y, n_, l, w) in enumerate(stacks):
    z = ZW
    for k in range(n_):
        z = sk.us_crate(C, x, y, z, l=l, w=w, h=0.6, stencil=2 if (i + k) % 3 == 0 else 1,
                        text_sides=(-1,) if y > -40 else (1,))
# 차량 통로 표시 (경사로 문 → 창고 안)
for y in (-42.6, -37.4):
    C.strip("hazard", (89.7, y, ZW), (AX1, y, ZW), 0.12, lift=0.014)
for x in (90.0, 93.5):
    for s in (-1, 1):
        C.strip("hazard", (x, -40.0, ZW), (x + 1.0, -40.0 + s * 1.2, ZW), 0.18, lift=0.014)
C.text("hazard", "차량 통로 · NO PARKING", 0.32, (92.0, -40.0, ZW), (0, 0, 1), up=(-1, 0, 0), lift=0.016)

# 경사로 방폭문 (동벽, 닫힘 → 위로)
DR = (97.3, 97.7, -42.55, -37.45, ZW, ZW + 3.65)


def _ramp_door_parts():
    def ribs(b):
        for xf in (97.29, 97.71):
            for k in range(1, 5):
                z = ZW + 3.65 * k / 5
                mk._bm_box(b, xf - 0.012, xf + 0.012, -42.4, -37.6, z - 0.05, z + 0.05)

    def stripes(b):
        for xf in (97.285, 97.715):
            for k in range(9):
                y = -42.4 + k * 0.56
                if k % 2 == 0:
                    mk._bm_box(b, xf - 0.006, xf + 0.006, y, y + 0.5, ZW + 0.1, ZW + 0.45)
    return [("steel_d", ribs), ("hazard", stripes)]


d_ramp = sk.door(C, "ramp", DR, "0,3.7,0", key="steel", parts=_ramp_door_parts())
sk.door_text(d_ramp, "MNT-A · RAMP 1", 0.32, (97.3, -40.0, ZW + 2.2), (-1, 0, 0))
sk.door_text(d_ramp, "MNT-A · RAMP 1", 0.32, (97.7, -40.0, ZW + 2.2), (1, 0, 0))
sk.hazard_frame(C, (AX1 - 0.005, -40.0, ZW + 1.8), (-1, 0, 0), 5.0, 3.6, band=0.25)
sk.sign(C, (AX1 - 0.01, -40.0, ZW + 4.3), (-1, 0, 0), 4.4, 0.6,
        [("차량 경사로 · 지상 출구", 0.2, "white", 0.08, 0.0), ("VEHICLE RAMP · SURFACE", 0.09, "glow", -0.17, 0.0)],
        depth=0.04)
# 기갑 차고 안내 (기갑병기는 여기 없다: 별관 제2차고)
sk.sign(C, (AX1 - 0.01, -34.2, ZW + 2.2), (-1, 0, 0), 3.0, 0.9,
        [("기갑 차고 → 제2차고 (별관)", 0.17, "white", 0.2, 0.0), ("ARMOR → GARAGE 2", 0.13, "hazard", -0.02, 0.0),
         ("구 기갑병기는 별관 차고에 보관", 0.08, "glow", -0.25, 0.0)], depth=0.04)
# 정비 계단 문 표지 (서벽)
sk.hazard_frame(C, (AX0 + 0.005, -33.4, ZW + 1.15), (1, 0, 0), 2.0, 2.3)
sk.sign(C, (AX0 + 0.01, -33.4, ZW + 2.95), (1, 0, 0), 2.6, 0.5,
        [("정비 계단 · 모노레일 선로 ↑", 0.13, "white", 0.07, 0.0), ("MAINT. STAIRS · MONORAIL", 0.07, "glow", -0.13, 0.0)],
        depth=0.03)
# 창고 이름판 (남벽, 입구에서 보인다)
sk.sign(C, (82.0, AY0 + 0.01, ZW + 3.5), (0, 1, 0), 7.0, 1.2,
        [("모나티엄 병기창고", 0.46, "white", 0.15, -0.5), ("MONATIUM ARMORY · MNT-A", 0.17, "gold", -0.3, -0.5),
         ("노획 화기 보관 · 지구 반입분", 0.12, "glow", -0.48, -0.5)], logo=True, depth=0.06)
# 비상등: 적색 경광등(깜빡임), 호박색 벽등
for (base, n_) in (((82.0, AY1 - 0.3, ZW + 2.95), (0, -1, 0)), ((AX1 - 0.3, -44.0, ZW + 3.9), (-1, 0, 0)),
                   ((72.0, AY0 + 0.3, ZW + 3.3), (0, 1, 0)), ((92.0, AY0 + 0.3, ZW + 3.3), (0, 1, 0)),
                   ((AX0 + 0.3, -46.5, ZW + 3.3), (1, 0, 0)), ((76.0, AY1 - 0.3, ZW + 3.3), (0, -1, 0))):
    sk.beacon(C, ls_ar_r, base, wall_normal=n_)
for (p, n_) in (((AX0, -35.6, ZW + 2.3), (1, 0, 0)), ((AX1, -36.6, ZW + 3.1), (-1, 0, 0)),
                ((AX1, -43.4, ZW + 3.1), (-1, 0, 0)), ((79.4, AY1, ZW + 2.2), (0, -1, 0)),
                ((84.6, AY1, ZW + 2.2), (0, -1, 0)), ((70.5, AY0, ZW + 2.6), (0, 1, 0))):
    # 번짐 원판을 벽에서 2.6 cm: 남보라 띠(2 cm), 경사로 문 노랑·검정 틀(1.7·2.1 cm)과 같은 평면을 피한다
    sk.emerg_lamp(C, ls_ar_a, p, n_, halo_lift=0.026)
# 전실 경광등 (방폭문 위, 전실 쪽)
sk.beacon(C, ls_ar_a, (82.0, -30.0 + 0.3, ZW + 2.75), wall_normal=(0, 1, 0), halo=0.8)
ls_ar_r.emit(C)
ls_ar_a.emit(C)

# 방폭문 (북벽, 닫힘 → 동쪽 벽 속으로)
DA = (80.75, 83.25, -30.75, -30.25, ZW, ZW + 2.5)


def _armory_door_parts():
    def frame(b):
        for yf in (-30.245, -30.755):
            mk._bm_box(b, 80.8, 83.2, yf - 0.02, yf + 0.02, ZW + 0.05, ZW + 0.2)
            mk._bm_box(b, 80.8, 83.2, yf - 0.02, yf + 0.02, ZW + 2.3, ZW + 2.45)
            mk._bm_box(b, 80.8, 80.95, yf - 0.02, yf + 0.02, ZW + 0.05, ZW + 2.45)
            mk._bm_box(b, 83.05, 83.2, yf - 0.02, yf + 0.02, ZW + 0.05, ZW + 2.45)

    def wheel(b):
        for yf, s in ((-30.25, 1), (-30.75, -1)):
            c = Vector((81.6, yf + s * 0.06, ZW + 1.25))
            mk._bm_cyl(b, c - Vector((0, s * 0.06, 0)), c, 0.07, segs=10)
            for a in range(3):
                ang = math.radians(a * 60)
                d = Vector((math.cos(ang), 0, math.sin(ang))) * 0.28
                mk._bm_cyl(b, c - d, c + d, 0.022, segs=6)
                for e in (c - d, c + d):
                    mk._bm_box(b, e.x - 0.03, e.x + 0.03, e.y - 0.02, e.y + 0.02, e.z - 0.03, e.z + 0.03)

    def stripes(b):
        for yf in (-30.24, -30.76):
            for k in range(4):
                x = 81.0 + k * 0.6
                mk._bm_box(b, x, x + 0.3, yf - 0.006, yf + 0.006, ZW + 0.25, ZW + 0.5)
    return [("steel_d", frame), ("gold", wheel), ("hazard", stripes)]


d_arm = sk.door(C, "armory", DA, "2.6,0,0", key="steel", parts=_armory_door_parts())
sk.door_text(d_arm, "MNT-A", 0.26, (82.4, -30.25, ZW + 1.8), (0, 1, 0))
sk.door_text(d_arm, "MNT-A", 0.26, (82.4, -30.75, ZW + 1.8), (0, -1, 0))

# ---------------------------------------------------------------- 병기창고 마커
C.marker("SPAWN_armory", (82.0, -32.6, ZW), face=(82.0, -40.0))
C.marker("SPAWN_breach", (84.0, -39.0, ZW), face=(97.0, -40.0))
C.marker("MARK_racks", (82.0, -39.0, ZW))
C.marker("MARK_ramp", (AX1 - 0.6, -40.0, ZW))
sk.trig(C, "armory", AX0 + 0.5, AX1 - 0.5, AY0 + 0.5, AY1 - 0.8, ZW - 0.5, ZW + 3.0)
hold("armory", (82.0, -34.0, ZW), {"sabre": (80.4, -33.2, ZW), "rona": (83.6, -33.2, ZW), "jesty": (81.0, -38.8, ZW),
                                   "karen": (83.0, -38.8, ZW)}, face=(82.0, -45.0))
hold("breach", (86.0, -40.0, ZW), {"sabre": (88.3, -38.0, ZW), "rona": (88.3, -45.0, ZW), "jesty": (84.6, -41.0, ZW),
                                   "karen": (83.4, -36.6, ZW)}, face=(97.0, -40.0))
pickup("m4a1", (77.8, -41.0, t1), "m4a1")
pickup("m249", (82.0, -41.0, t2), "m249")
pickup("m870", (86.2, -41.0, t3), "m870")
pickup("m17", (79.2, AY0 + 0.5, wb), "m17")
pickup("m67", (84.0, -45.0, c67), "m67")
pickup("m72", (80.0, -45.0, c72), "m72")
pickup("ammo_1", (72.7, -44.8, a1), "ammo")
pickup("ammo_2", (84.5, -48.3, a2), "ammo")
FACE_RAMP = (97.0, -40.0)
for i, (x, y, hgt) in enumerate(((88.3, -38.0, "high"), (88.3, -45.0, "high"), (84.6, -41.0, "low"),
                                 (83.4, -36.6, "high"), (90.6, -35.0, "high"), (91.6, -45.6, "high"),
                                 (86.7, -48.2, "low"), (80.4, -41.0, "low"), (74.4, -38.0, "high"),
                                 (93.6, -47.6, "low")), 1):
    cover(f"armory_{i:02d}", (x, y, ZW), hgt, face=FACE_RAMP)

# ================================================================ 차량 경사로 (R41 돌입로)
C.group("ramp")
ls_rp = sk.LampSet("emerg_08", "a")
sk.vehicle_ramp(C, RAMP_X0, RAMP_FLAT, RAMP_TOP, RAMP_X1, RAMP_Y0, RAMP_Y1, z0=ZW, z_top=RAMP_Z, ls=ls_rp)
sk.sign(C, (RAMP_X1 - 1.3, RAMP_Y1 - 0.01, RAMP_Z + 2.6), (0, -1, 0), 2.4, 0.42,   # 햇빛판(x 131) 앞에서 끝나게
        [("지상 · 남서광장 별관 →", 0.12, "white", 0.05, 0.0), ("SURFACE EXIT", 0.07, "glow", -0.12, 0.0)], depth=0.03)
ls_rp.emit(C)
C.fx("smoke_1", (99.2, -40.0, ZW + 1.6), dir="-1,0,0", strength=0.8)
# 돌입 팀 (경사로 위): 소총수 6 + 진압 방패 2 + 장교 1, 드론 2
for (eid, kind, x, y, beh) in (("breach_01", "rifleman_a", 104.0, -38.5, "advance"),
                               ("breach_02", "rifleman_b", 104.5, -41.5, "advance"),
                               ("breach_03", "riot", 102.4, -40.6, "advance"),
                               ("breach_04", "riot", 102.6, -38.8, "rush"),
                               ("breach_05", "rifleman_c", 108.0, -39.2, "advance"),
                               ("breach_06", "rifleman_a", 108.6, -42.0, "advance"),
                               ("breach_07", "officer", 114.0, -40.0, "hold"),
                               ("breach_08", "rifleman_b", 111.0, -37.8, "rush"),
                               ("breach_09", "rifleman_c", 112.0, -42.2, "advance")):
    enemy(eid, "breach", kind, (x, y, ramp_z(x)), beh)
enemy("breach_drone_01", "breach_drone", "drone", (106.0, -40.0, ramp_z(106.0) + 2.5), "advance")
enemy("breach_drone_02", "breach_drone", "drone", (110.0, -38.6, ramp_z(110.0) + 2.6), "advance")

# ================================================================ 정비 계단 (모노레일 선로로)
# 계단실(x 61.5..66, y -47..-31.5, B3 → 지상 1층)과 창고 서벽 문(DOOR_armory_stair)은 선로 레벨(m2_monorail.py
# '정비 계단실')이 가진다: 두 레벨이 한 좌표에 함께 붙어 있다가 지하는 열차 안에서 뗀다(m2.ts). 여기에는 판정만 남긴다.
C.group("stairs")
SX_W, SX_E, SY_S, SY_N = 61.5, 66.0, -47.0, -31.5
Z_MID = ZW + 2.4
# 내비 겹침: 계단실 1층 바닥(선로 레벨 판석과 같은 높이)에 이 레벨의 COL 바닥을 겹쳐 둔다. 창고 쪽 분대원이 계단실
# 바닥까지 길을 찾고, 거기서 선로 레벨 내비메시로 넘어간다 (m2.ts follow link)
C.col(SX_W, SX_E, -35.5, SY_N, ZW - 0.3, ZW)

C.marker("SPAWN_stairs", (69.0, -33.4, ZW), face=(60.0, -33.4))
C.marker("MARK_stairs", (AX0 + 0.4, -33.4, ZW))
sk.trig(C, "stairs", SX_W, SX_E, SY_S, -41.5, Z_MID - 0.5, Z_MID + 3.0)

# ================================================================ 마무리
C.group("station")
sk.report(C)
ROOT = {
    "sky": "#0b0c12",
    "fog": "8,90",
    "sun": "0.25,1,0.35",
    "ambient": 0.95,
    "near": 0.1,
    "far": 220,
    "music": "m2_subway",
    "sunIntensity": 0.35,
    "sunColor": "#ffb4a0",
    "hemiSky": "#b9a6b2",
    "hemiGround": "#2e2632",
    "timeOfDay": "underground",
}
if PREVIEW == "cut":
    # 뷰어는 COL_/TRIG_ 상자도 흰 면으로 그린다: 위에서 보는 미리보기에서는 뺀다
    C.cols.clear()
    for g, o in list(C.nodes):
        if o.name.startswith(("TRIG_", "COL_")):
            C.nodes.remove((g, o))
            bpy.data.objects.remove(o, do_unlink=True)
if PREVIEW == "col":
    out = "_tmp/m2_subway_col.glb"
elif PREVIEW == "cut":
    out = "_tmp/m2_subway_cut.glb"
else:
    out = "levels/m2_subway.glb"
C.finish(out, root_props=ROOT, outline=0.016, detail_outline=0.008, col_debug=(PREVIEW == "col"), root_offset=SHARED)
