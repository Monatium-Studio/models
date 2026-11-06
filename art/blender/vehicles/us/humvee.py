"""노획 험비 (M1114 계열 장갑형 고기동차량) + 지붕 링 마운트 M2.

npm run model -- art/blender/vehicles/us/humvee.py
npm run shot -- vehicles/us/humvee.glb --views front,34,side,top

규약: docs/art/VEHICLES.md. 정면 -Y, 왼쪽 +X, 원점 = 차체 중심 아래 지면.
실측 기준: 전장 5.0 m, 전폭 2.3 m, 지붕 1.94 m(링·방호판 포함 2.75 m), 축거 3.30 m, 윤거 1.82 m, 타이어 37인치.
거치 무기: turret(사수 링, 요 360°) > mount_m2(피치만, weapons/us/m2.glb를 붙임).
엘프식 흔적: 운전석 분홍 방석 2단, 페달 나무 연장 블록, 운전석 문 아래 밧줄 발판, 사수 발판(상자 2단 + 방석),
왼쪽 거울의 창고 태그, 청록 관리번호와 한글 스텐실, 뒤 경고판에 한글 덧칠.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402
import vehicles_us as vu  # noqa: E402
from vehicles_us import boxr, side, text, xcyl, ycyl, zcyl  # noqa: E402

cb.reset()
b = vu.VBuild("humvee")

# ================================================================== 치수
WB, TRK = 3.30, 1.82
TR, TW = 0.47, 0.32
AXF, AXR = -WB / 2, WB / 2
WX = TRK / 2
FX = 1.15                 # 펜더 반폭
DX0, DX1 = 1.02, 1.10     # 문 안/바깥 면
ZF = 0.66                 # 차체 바닥(프레임 위)
ZR = 1.94                 # 지붕 윗면
Y_WS0, Y_WS1 = -0.50, -0.17   # 앞유리 아래/위 y
RC = (0.0, 0.52, ZR)      # 사수 링 중심
PZ = 2.30                 # M2 고각 핀 높이
PY = 0.12                 # M2 피벗 y (링 중심보다 0.40 앞)
LS = dict(right=(0, 1, 0), up=(0, 0, 1))     # 왼쪽(+X) 면 글자
RS = dict(right=(0, -1, 0), up=(0, 0, 1))    # 오른쪽(-X) 면 글자
FR = dict(right=(1, 0, 0), up=(0, 0, 1))     # 앞면(-Y) 글자
BK = dict(right=(-1, 0, 0), up=(0, 0, 1))    # 뒷면(+Y) 글자


def hz(y):
    """후드 윗선 (앞 끝 y=-2.31 → 카울 y=-0.50)."""
    return 1.065 + (y + 2.31) / 1.81 * 0.235


def arch(yc, rear_first=True):
    """바퀴 아치 (사다리꼴 + 둥근 모서리). 차체 옆모습 외곽선 일부."""
    pts = [(yc + 0.60, 0.70), (yc + 0.575, 0.90), (yc + 0.50, 1.00), (yc + 0.42, 1.025), (yc - 0.42, 1.025),
           (yc - 0.50, 1.00), (yc - 0.575, 0.90), (yc - 0.60, 0.70)]
    return pts if rear_first else list(reversed(pts))


# ================================================================== 차체: 앞 (펜더, 후드, 그릴, 범퍼)
for sx in (-1, 1):
    fpts = [(-0.50, 0.70)] + arch(AXF) + [(-2.36, 0.70), (-2.36, 0.99), (-2.315, 1.055), (-0.50, hz(-0.50))]
    b.s(side(f"fender{sx}", fpts, FX - 0.62, x=sx * (FX + 0.62) / 2, bevel=0.014, seg=1, mat="tan"))
    # 펜더 안쪽 휠하우스 라이너 (아치 안이 비어 보이지 않게)
    b.s(boxr(f"wheelhouse_f{sx}", min(sx * 0.60, sx * 0.64), max(sx * 0.60, sx * 0.64), AXF - 0.60, AXF + 0.60, 0.62,
             1.02, mat="tan_dk"))
hood = [(-0.50, ZF), (-2.30, ZF), (-2.30, 0.975), (-2.345, 0.99), (-2.345, 1.02), (-2.31, 1.065), (-0.50, hz(-0.50))]
b.s(side("hood_core", hood, 1.24, bevel=0.010, seg=1, mat="tan"))
# 후드 가운데 융기 (엔진 덮개)
hump = [(-2.02, hz(-2.02) - 0.01), (-1.92, hz(-1.92) + 0.042), (-0.66, hz(-0.66) + 0.042), (-0.60, hz(-0.60) - 0.01)]
b.s(side("hood_hump", hump, 0.98, bevel=0.012, seg=1, mat="tan"))
# 흡기구 (오른쪽 카울, 루버)
b.s(boxr("intake", -1.02, -0.70, -0.98, -0.64, hz(-0.98) - 0.01, hz(-0.64) + 0.045, bevel=0.012, mat="tan"))
for i in range(6):
    y = -0.94 + i * 0.05
    b.f(boxr(f"louver{i}", -0.99, -0.73, y, y + 0.022, hz(-0.64) + 0.045, hz(-0.64) + 0.050, mat="black"))
# 후드와 펜더 사이 패널선, 후드 걸쇠(고무 T 래치)
for sx in (-1, 1):
    b.f(vu.beam(f"hood_seam{sx}", (sx * 0.62, -2.31, hz(-2.31) + 0.0025), (sx * 0.62, -0.52, hz(-0.52) + 0.0025),
                0.010, 0.004, mat="tan_dk"))
    for y in (-0.80, -2.05):
        b.t(boxr(f"latch{sx}{y}", min(sx * FX, sx * (FX + 0.018)), max(sx * FX, sx * (FX + 0.018)), y - 0.035,
                 y + 0.035, hz(y) - 0.07, hz(y) - 0.012, bevel=0.006, mat="black"))
# 카울 (앞유리 받침)
b.s(boxr("cowl", -1.10, 1.10, -0.57, -0.45, 1.27, 1.335, bevel=0.012, mat="tan"))

# 그릴: 어두운 바탕 + 세로 살 + 전조등 하우징
b.s(boxr("grille_back", -0.61, 0.61, -2.306, -2.296, 0.68, 0.96, mat="black"))
for i in range(9):
    x = -0.36 + i * 0.09
    b.t(boxr(f"grille_bar{i}", x - 0.016, x + 0.016, -2.33, -2.30, 0.69, 0.955, bevel=0.005, mat="tan"))
for sx in (-1, 1):
    b.s(ycyl(f"hl_house{sx}", 0.108, -2.335, -2.30, x=sx * 0.50, z=0.85, verts=18, mat="black"))
    b.f(boxr(f"turn{sx}", sx * 0.50 - 0.05, sx * 0.50 + 0.05, -2.338, -2.330, 0.70, 0.735, mat="amber"))
# 범퍼 + 견인 고리 + 인양 고리
b.s(boxr("bumper", -1.12, 1.12, -2.50, -2.37, 0.50, 0.68, bevel=0.018, mat="tan"))
b.s(boxr("bumper_brace", -0.70, 0.70, -2.38, -2.30, 0.52, 0.64, bevel=0.01, mat="tan_dk"))
for sx in (-1, 1):
    sh = us.torus(f"shackle{sx}", 0.045, 0.012, loc=(sx * 0.66, -2.53, 0.55), rot=(0, 90, 0), seg=8, rseg=5,
                  arc=220, mat="black")
    b.t(sh)
    b.t(boxr(f"shackle_tab{sx}", sx * 0.66 - 0.03, sx * 0.66 + 0.03, -2.53, -2.49, 0.52, 0.62, bevel=0.006,
             mat="tan_dk"))
    b.t(us.torus(f"lift_eye{sx}", 0.035, 0.010, loc=(sx * 0.42, -2.43, 0.70), rot=(90, 0, 90), seg=6, rseg=5,
                 arc=180, mat="tan_dk"))
# 범퍼 표식 (청록 덧칠: 왼쪽 MNT, 오른쪽 V-07)
b.f(text("bump_l", "MNT", 0.075, (0.82, -2.502, 0.59), mat="paint", **FR))
b.f(text("bump_r", "V-07", 0.075, (-0.82, -2.502, 0.59), mat="paint", **FR))
for sx in (-1, 1):   # 범퍼 볼트
    for x in (0.28, 0.95):
        b.f(vu.radial_disc(f"bb{sx}{x}", (sx * x, -2.502, 0.645), (0, -1, 0), 0.014, 0.006, verts=6, mat="steel"))
# 앞 하부 보호판
b.s(boxr("skid", -0.62, 0.62, -2.36, -1.95, 0.50, 0.56, bevel=0.01, mat="tan_dk"))

# ================================================================== 차체: 실내 바닥, 로커, 필러, 지붕, 앞유리
b.s(boxr("floor", -1.00, 1.00, -0.52, 1.50, ZF, 0.74, mat="tan_dk"))
for sx in (-1, 1):
    b.s(boxr(f"rocker{sx}", min(sx * 0.96, sx * 1.085), max(sx * 0.96, sx * 1.085), -0.50, 1.03, 0.56, 0.70,
             bevel=0.012, mat="tan"))
    b.s(boxr(f"bpillar{sx}", min(sx * 0.99, sx * 1.075), max(sx * 0.99, sx * 1.075), 0.495, 0.565, 0.68, ZR - 0.04,
             bevel=0.01, mat="tan"))
    b.s(vu.beam(f"apillar{sx}", (sx * 1.03, Y_WS0 - 0.02, 1.30), (sx * 1.03, Y_WS1 - 0.01, ZR - 0.03), 0.10, 0.08,
                mat="tan", bevel=0.012))
    # 뒷바퀴 휠하우스 (실내)
    b.s(boxr(f"wheelhouse_r{sx}", min(sx * 0.62, sx * 1.02), max(sx * 0.62, sx * 1.02), 1.04, 1.50, 0.70, 1.06,
             bevel=0.02, mat="tan_dk"))
roof = boxr("roof", -1.065, 1.065, Y_WS1 - 0.04, 1.53, ZR - 0.08, ZR, bevel=0.018, mat="tan")
us.cut(roof, zcyl("ring_hole", 0.565, ZR - 0.2, ZR + 0.1, x=RC[0], y=RC[1], verts=32))
b.s(roof)
for y in (0.24, 0.80, 1.24):   # 지붕 장갑판 이음선
    if abs(y - RC[1]) > 0.6:
        b.f(boxr(f"roof_seam{y}", -1.0, 1.0, y - 0.006, y + 0.006, ZR, ZR + 0.003, mat="tan_dk"))
b.s(vu.beam("ws_post", (0, Y_WS0 - 0.02, 1.32), (0, Y_WS1 - 0.01, ZR - 0.04), 0.07, 0.06, mat="tan", bevel=0.01))
ws_len = math.hypot(Y_WS1 - Y_WS0, ZR - 0.05 - 1.335)
ws_ang = math.degrees(math.atan2(Y_WS1 - Y_WS0, ZR - 0.05 - 1.335))
for sx in (-1, 1):
    g = cb.box(f"ws{sx}", size=(0.92, 0.014, ws_len), loc=(sx * 0.505, (Y_WS0 + Y_WS1) / 2, (1.335 + ZR - 0.05) / 2),
               rot=(-ws_ang, 0, 0))
    vu.setmat(g, "glass")
    b.s(g)
    wn = (0, -math.cos(math.radians(ws_ang)), math.sin(math.radians(ws_ang)))   # 앞유리 바깥 법선
    for k, (off, w) in enumerate(((0.10, 0.06), (0.20, 0.03))):   # 반사 줄 (바깥에서만 보임)
        c = (sx * 0.505 + off, (Y_WS0 + Y_WS1) / 2 - 0.008, (1.335 + ZR - 0.05) / 2)
        b.f(vu.glint(f"ws_hl{sx}{k}", c, wn, w, ws_len * 0.75))
    # 와이퍼
    b.t(vu.beam(f"wiper{sx}", (sx * 0.16, Y_WS0 - 0.005, 1.36), (sx * 0.86, Y_WS0 + 0.03, 1.40), 0.018, 0.012,
                mat="black"))

# ================================================================== 차체: 뒤 (화물칸, 경사 덮개 받침, 뒷면)
for sx in (-1, 1):
    rpts = [(1.47, 1.025), (AXR + 0.42, 1.025), (AXR + 0.50, 1.00), (AXR + 0.575, 0.90),
            (AXR + 0.60, 0.70), (2.42, 0.70), (2.42, 1.38), (2.37, 1.44), (1.47, 1.865)]
    b.s(side(f"rear_side{sx}", rpts, DX1 - 0.62, x=sx * (DX1 + 0.62) / 2, bevel=0.014, seg=1, mat="tan"))
    b.s(boxr(f"wheelhouse_rr{sx}", min(sx * 0.60, sx * 0.64), max(sx * 0.60, sx * 0.64), AXR - 0.60, AXR + 0.60,
             0.62, 1.03, mat="tan_dk"))
b.s(side("rear_core", [(1.47, ZF), (2.42, ZF), (2.42, 1.38), (2.37, 1.44), (1.47, 1.865)], 1.24, bevel=0.012,
         seg=1, mat="tan"))
# 뒷범퍼 (짧은 범퍼렛 둘) + 견인 고리 + 후미등 하우징
for sx in (-1, 1):
    b.s(boxr(f"bumperette{sx}", min(sx * 0.70, sx * 1.05), max(sx * 0.70, sx * 1.05), 2.40, 2.52, 0.54, 0.70,
             bevel=0.015, mat="tan"))
    b.s(boxr(f"tl_house{sx}", min(sx * 0.80, sx * 1.02), max(sx * 0.80, sx * 1.02), 2.41, 2.445, 0.93, 1.13,
             bevel=0.01, mat="black"))
    b.t(us.torus(f"rear_shackle{sx}", 0.04, 0.011, loc=(sx * 0.88, 2.55, 0.58), rot=(0, 90, 0), seg=8, rseg=5,
                 arc=220, mat="black"))
b.t(boxr("pintle_hook_base", -0.10, 0.10, 2.42, 2.50, 0.56, 0.70, bevel=0.01, mat="black"))
b.t(us.torus("pintle_hook", 0.05, 0.016, loc=(0, 2.54, 0.60), rot=(0, 90, 0), seg=9, rseg=5, arc=270, mat="black"))
# 뒤 경고판: 원래 영문 + 엘프가 덧칠한 한글
b.s(boxr("sign", -0.36, 0.36, 2.42, 2.432, 1.03, 1.31, bevel=0.006, mat="paper"))
b.f(text("sign_en", "STAY BACK 100 M", 0.070, (0, 2.433, 1.235), mat="black", **BK))
b.f(text("sign_kr", "100야드 뒤로!", 0.060, (0, 2.433, 1.105), mat="paint", font="kr", **BK))
b.f(boxr("sign_strike", -0.30, 0.30, 2.4334, 2.4338, 1.226, 1.236, mat="paint"))   # 영문 위 덧칠 줄
for (x, z) in ((-0.33, 1.06), (0.33, 1.06), (-0.33, 1.28), (0.33, 1.28)):
    b.f(vu.radial_disc(f"sign_bolt{x}{z}", (x, 2.434, z), (0, 1, 0), 0.010, 0.004, verts=6, mat="steel"))
# 뒷면 청록 관리번호
b.f(text("rear_no", "MNT-V07", 0.085, (0.58, 2.421, 1.25), mat="paint", **BK))

# ================================================================== 하부 (프레임, 서스펜션, 배기)
for sx in (-1, 1):
    b.s(boxr(f"frame{sx}", min(sx * 0.40, sx * 0.48), max(sx * 0.40, sx * 0.48), -2.36, 2.40, 0.50, 0.66,
             bevel=0.01, mat="tan_dk"))
    for ya in (AXF, AXR):
        b.s(xcyl(f"hub_house{sx}{ya}", 0.13, sx * 0.62, sx * 0.74, y=ya, z=TR + 0.02, verts=16, mat="tan_dk"))
        b.s(xcyl(f"halfshaft{sx}{ya}", 0.035, sx * 0.20, sx * 0.64, y=ya, z=TR + 0.08, verts=10, mat="black"))
        for (z0, z1, dy) in ((0.62, 0.58, 0.16), (0.40, 0.42, 0.20)):   # 위·아래 A암
            b.s(vu.beam(f"arm{sx}{ya}{z0}a", (sx * 0.42, ya - dy, z0), (sx * 0.66, ya, z1), 0.05, 0.04,
                        mat="tan_dk"))
            b.s(vu.beam(f"arm{sx}{ya}{z0}b", (sx * 0.42, ya + dy, z0), (sx * 0.66, ya, z1), 0.05, 0.04,
                        mat="tan_dk"))
        b.s(vu.beam(f"coil{sx}{ya}", (sx * 0.55, ya, 0.52), (sx * 0.52, ya, 0.88), 0.11, 0.11, mat="black"))
for ya in (AXF, AXR):
    b.s(boxr(f"diff{ya}", -0.22, 0.22, ya - 0.18, ya + 0.14, 0.40, 0.62, bevel=0.03, mat="tan_dk"))
b.s(ycyl("driveshaft", 0.045, AXF + 0.2, AXR - 0.2, x=0.10, z=0.50, verts=10, mat="black"))
b.s(vu.tube("exhaust", vu.rounded_path([(-0.30, -1.0, 0.56), (-0.55, -0.2, 0.55), (-0.85, 0.75, 0.56),
                                        (-1.03, 0.95, 0.60)], 0.12, 2), 0.04, mat="black", verts=8))
b.empty("exhaust_1", (-1.06, 0.97, 0.60), dir="-1,0,0")

# ================================================================== 실내 (창으로 보이는 정도)
b.s(boxr("firewall", -1.00, 1.00, -0.56, -0.494, 0.74, 1.05, mat="tan_dk"))   # 차체 뒤끝 면(y -0.50)보다 6 mm 앞 (같은 평면 깜빡임)
b.s(boxr("dash", -1.00, 1.00, -0.52, -0.30, 1.00, 1.25, bevel=0.02, mat="tan_dk"))
b.s(boxr("dash_top", -0.98, 0.98, -0.50, -0.26, 1.22, 1.29, bevel=0.02, mat="black"))
b.s(boxr("console", -0.22, 0.22, -0.30, 1.40, 0.74, 1.02, bevel=0.02, mat="tan_dk"))
b.s(boxr("radio", -0.20, 0.20, -0.30, -0.02, 1.02, 1.26, bevel=0.012, mat="black"))
for i in range(3):
    b.f(boxr(f"radio_knob{i}", -0.14 + i * 0.10, -0.10 + i * 0.10, -0.022, -0.014, 1.15, 1.19, mat="steel"))
for sx in (-1, 1):
    for ys in (0.10, 1.00):
        b.s(boxr(f"seat{sx}{ys}", sx * 0.50 - 0.24, sx * 0.50 + 0.24, ys - 0.22, ys + 0.22, 0.74, 0.90, bevel=0.03,
                 mat="black"))
        bk = boxr(f"seatback{sx}{ys}", sx * 0.50 - 0.23, sx * 0.50 + 0.23, ys + 0.20, ys + 0.30, 0.86, 1.50,
                  bevel=0.03, mat="black")
        us.xform(bk, rot=(-10, 0, 0), pivot=(0, ys + 0.25, 0.88))
        b.s(bk)
# 운전대 (왼쪽 +X)
SW = (0.50, -0.20, 1.33)
wheel_rim = us.torus("steer_rim", 0.19, 0.016, loc=SW, rot=(-56, 0, 0), seg=14, rseg=5, mat="black")
b.s(wheel_rim)
b.s(vu.beam("steer_col", (0.50, -0.42, 1.18), SW, 0.05, 0.05, mat="black"))
b.s(vu.beam("steer_spoke", (0.31, SW[1] + 0.04, SW[2] - 0.02), (0.69, SW[1] + 0.04, SW[2] - 0.02), 0.03, 0.02,
            mat="black"))
# 엘프 흔적: 페달 연장 블록(나무) + 운전석 방석 2단
for (x, nm) in ((0.62, "gas"), (0.44, "brake")):
    b.s(boxr(f"pedal_{nm}", x - 0.04, x + 0.04, -0.47, -0.44, 0.80, 0.92, bevel=0.005, mat="black"))
    b.s(boxr(f"pedal_ext_{nm}", x - 0.05, x + 0.05, -0.44, -0.30, 0.80, 0.90, bevel=0.01, mat="coyote"))
    b.t(boxr(f"pedal_strap_{nm}", x - 0.055, x + 0.055, -0.40, -0.37, 0.795, 0.905, mat="od"))
# 방석은 얇은 한 장 (예전 두 장 0.19 m 위에 앉으면 엘프 키트의 큰 머리가 지붕·사수 링을 뚫었다: M5 케이트, crewcheck)
for k, (z0, h, w) in enumerate(((0.90, 0.05, 0.44),)):
    cu, tufts = vu.cushion(f"drv_cushion{k}", (0.50, 0.08 - k * 0.01, z0), w, 0.40 - k * 0.03, h)
    b.s(cu)
    b.f(*tufts)
# 사수 발판: 탄약 상자 2단 + 방석 (링 아래, 사수 자리 0.92 m 뒤)
GY = PY + 0.80
for k, (z0, z1) in enumerate(((1.02, 1.34), (1.34, 1.64))):
    b.s(boxr(f"crate{k}", -0.20, 0.20, GY - 0.16, GY + 0.16, z0, z1, bevel=0.012, mat="od"))
gcu, gt = vu.cushion("gunner_cushion", (0, GY, 1.64), 0.36, 0.28, 0.08)
b.s(gcu)
b.f(*gt)

# ================================================================== 거울 + 창고 태그 / 안테나 / 밧줄 발판
for sx in (-1, 1):
    b.t(vu.tube(f"mirror_arm{sx}", [(sx * 1.07, -0.47, 1.42), (sx * 1.24, -0.50, 1.47), (sx * 1.33, -0.50, 1.52)],
                0.014, mat="black", verts=8))
    b.s(boxr(f"mirror{sx}", min(sx * 1.27, sx * 1.45), max(sx * 1.27, sx * 1.45), -0.53, -0.49, 1.40, 1.66,
             bevel=0.012, mat="black"))
    b.f(boxr(f"mirror_glass{sx}", min(sx * 1.285, sx * 1.435), max(sx * 1.285, sx * 1.435), -0.4885, -0.4875, 1.415,
             1.645, mat="paper"))
vu.tag(b, (1.185, -0.488, 1.405), scale=3.6, lines=("MNT", "V-0007", "모나티엄 창고"), yaw=8,
       cord_top=(1.18, -0.487, 1.445), f_add=b.t)
ant = [(1.03, 1.92, 1.80), (1.03, 1.86, 2.32), (1.03, 1.60, 2.56), (1.02, 1.00, 2.50), (1.01, 0.30, 2.24),
       (1.00, -0.10, 1.99)]
b.s(zcyl("ant_base", 0.035, 1.66, 1.82, x=1.03, y=1.92, verts=10, mat="black"))
b.t(vu.tube("antenna", vu.rounded_path(ant, 0.3, 2), 0.007, mat="black", verts=5))
b.t(boxr("ant_clip", 0.97, 1.03, -0.13, -0.07, ZR - 0.02, ZR + 0.01, mat="black"))
# 운전석 문 아래 밧줄 발판 (엘프용)
for y in (-0.05, 0.27):
    b.t(vu.tube(f"stirrup_rope{y}", [(1.075, y, 0.60), (1.08, y, 0.45), (1.085, y + (0.03 if y < 0 else -0.03), 0.33)],
                0.009, mat="paper", verts=6))
b.t(boxr("stirrup_rung", 1.06, 1.11, -0.04, 0.26, 0.30, 0.345, bevel=0.008, mat="coyote"))

# ================================================================== 표식 (옆면)
for sx, kw in ((1, LS), (-1, RS)):
    b.f(text(f"rear_side_no{sx}", "MNT-V07", 0.11, (sx * (DX1 + 0.002), 1.92, 1.30), mat="paint", **kw))
    b.f(text(f"hood_no{sx}", "V-07", 0.09, (sx * (FX + 0.002), -0.80, 1.10), mat="paint", **kw))

# 뒤 옆판 장갑 볼트 줄, 연료 주입구(왼쪽), 앞 펜더 등화관제등
for sx in (-1, 1):
    for y in (1.62, 1.80, 1.98, 2.16, 2.32):
        for z in (1.08, 1.20 if y < 2.2 else None):
            if z is None:
                continue
            b.f(vu.radial_disc(f"rbolt{sx}{y}{z}", (sx * (DX1 + 0.002), y, z), (sx, 0, 0), 0.013, 0.006, verts=6,
                               mat="tan_dk"))
    b.f(boxr(f"bo_marker{sx}", sx * 0.95 - 0.05, sx * 0.95 + 0.05, -2.364, -2.356, 0.90, 0.95, mat="amber"))
b.t(xcyl("fuel_cap", 0.055, DX1 - 0.005, DX1 + 0.025, y=2.20, z=1.40, verts=12, mat="black"))
b.t(xcyl("fuel_cap_ring", 0.07, DX1 - 0.005, DX1 + 0.008, y=2.20, z=1.40, verts=12, mat="tan_dk"))

# ================================================================== 문 4개 (앞 경첩, 바깥으로 70°)
for sx in (-1, 1):   # 경첩 기둥 (펜더 뒤 ~ 앞문 앞)
    b.s(boxr(f"hinge_pillar{sx}", min(sx * 0.98, sx * 1.08), max(sx * 0.98, sx * 1.08), -0.51, -0.455, 0.66, 1.33,
             mat="tan"))
DOORS = (("FL", 1, -0.46, 0.485, False), ("FR", -1, -0.46, 0.485, False),
         ("RL", 1, 0.575, 1.47, True), ("RR", -1, 0.575, 1.47, True))
for nm, sx, y0, y1, notch in DOORS:
    part = f"door_{nm}"
    xc = sx * (DX0 + DX1) / 2
    if notch:
        pts = [(y0, 0.68), (1.02, 0.68), (1.07, 0.80), (1.10, 1.045), (y1, 1.045), (y1, ZR - 0.05), (y0, ZR - 0.05)]
    else:   # 앞문 앞 가장자리 위쪽은 A필러 기울기를 따른다
        pts = [(y0, 0.68), (y1, 0.68), (y1, ZR - 0.05), (Y_WS1 + 0.045, ZR - 0.05), (y0, 1.33)]
    shell = side(part + "_shell", pts, DX1 - DX0, x=xc, bevel=0.012, seg=1, mat="tan")
    wy0, wy1 = (y0 + 0.16, y1 - 0.14) if notch else (-0.06, y1 - 0.14)
    us.cut(shell, boxr(part + "_wcut", xc - 0.1, xc + 0.1, wy0, wy1, 1.38, 1.76))
    b.p(part, shell)
    gl = boxr(part + "_glass", sx * 1.052 - 0.007, sx * 1.052 + 0.007, wy0 - 0.01, wy1 + 0.01, 1.37, 1.77)
    vu.setmat(gl, "glass")
    b.p(part, gl)
    xo = sx * DX1
    # 손잡이 (뒤쪽 가장자리 근처), 경첩 너클 둘, 아래 보강 리브
    hy = y1 - 0.20
    b.pt(part, boxr(part + "_handle", min(xo, xo + sx * 0.03), max(xo, xo + sx * 0.03), hy - 0.09, hy + 0.05,
                    1.25, 1.29, bevel=0.008, mat="black"))
    b.pt(part, boxr(part + "_handle_base", min(xo, xo + sx * 0.012), max(xo, xo + sx * 0.012), hy - 0.11, hy + 0.07,
                    1.235, 1.305, bevel=0.006, mat="tan_dk"))
    for z in (0.92, 1.58):
        b.pt(part, zcyl(part + f"_hinge{z}", 0.022, z - 0.07, z + 0.07, x=sx * (DX1 + 0.012), y=y0 + 0.012, verts=10,
                        mat="tan_dk"))
    b.p(part, boxr(part + "_rib", min(xo, xo + sx * 0.012), max(xo, xo + sx * 0.012), y0 + 0.06,
                   (1.00 if notch else y1 - 0.06), 0.96, 1.00, bevel=0.005, mat="tan"))
    # 창 둘레 장갑 볼트 + 패널선
    for (yy, zz) in ((wy0 - 0.05, 1.36), (wy1 + 0.05, 1.36), (wy0 - 0.05, 1.78), (wy1 + 0.05, 1.78),
                     ((wy0 + wy1) / 2, 1.80), ((wy0 + wy1) / 2, 1.34)):
        b.pf(part, vu.radial_disc(part + f"_bolt{yy:.2f}{zz}", (xo + sx * 0.002, yy, zz), (sx, 0, 0), 0.014, 0.006,
                                  verts=6, mat="tan_dk"))
    b.pf(part, boxr(part + "_seam", min(xo, xo + sx * 0.003), max(xo, xo + sx * 0.003), y0 + 0.03,
                    (1.00 if notch else y1 - 0.03), 1.115, 1.123, mat="tan_dk"))
    if nm in ("FL", "FR"):
        kw = LS if sx > 0 else RS
        b.pf(part, text(part + "_kr", "진압반 수송", 0.075, (xo + sx * 0.0035, (y0 + y1) / 2, 1.05), mat="paint",
                        font="kr", **kw))
    b.part(part, (sx * (DX1 + 0.012), y0 + 0.012, 1.25), rotAxis="y", rotDeg=-70 * sx)

# ================================================================== 뒤 화물칸 덮개 (해치, 앞 경첩 위로 75°)
lid = [(1.53, 1.912), (2.37, 1.482), (2.385, 1.445), (1.53, 1.868)]
b.p("hatch_rear", side("hatch_rear_lid", lid, 1.92, bevel=0.012, seg=1, mat="tan"))
b.pt("hatch_rear", vu.tube("hatch_handle", [(-0.25, 2.30, 1.53), (-0.25, 2.33, 1.56), (0.25, 2.33, 1.56),
                                            (0.25, 2.30, 1.53)], 0.012, mat="black", verts=6))
for sx in (-1, 1):
    b.pt("hatch_rear", ycyl(f"lid_hinge{sx}", 0.02, 1.50, 1.58, x=sx * 0.70, z=1.90, verts=10, mat="tan_dk"))
    b.pt("hatch_rear", boxr(f"lid_latch{sx}", sx * 0.80 - 0.04, sx * 0.80 + 0.04, 2.33, 2.40, 1.45, 1.52, bevel=0.008,
                            mat="black"))
b.part("hatch_rear", (0, 1.53, 1.89), rotAxis="x", rotDeg=75)

# ================================================================== 사수 링 (정지 하단) + 회전 포탑(링 상단 + 방호판 + 피벗)
b.s(vu.lathe("ring_base", [(ZR, 0.565), (ZR, 0.68), (ZR + 0.05, 0.68), (ZR + 0.05, 0.565)], segs=32, axis="z",
             loc=(RC[0], RC[1], 0), closed=True, smooth=30, mat="tan_dk"))
T = "turret"
b.p(T, vu.lathe("ring_top", [(ZR + 0.05, 0.57), (ZR + 0.05, 0.67), (ZR + 0.11, 0.66), (ZR + 0.11, 0.575)],
                segs=32, axis="z", loc=(RC[0], RC[1], 0), closed=True, smooth=30, mat="tan"))
ZT0 = ZR + 0.11
SH_F = RC[1] - 0.70          # 방호판 앞면 y
SH_TOP = 2.80


def vplate(name, p0, p1, z0, z1, th, *, holes=(), mat="tan", top1=None):
    """평면도 p0→p1 수직 판 (두께 th, 바깥 = 진행 방향 오른쪽). holes: [(u0, u1, z0, z1)] 비율 u.
    top1: p1 쪽 윗높이(경사 윗변)."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    z1b = z1 if top1 is None else top1
    o = side(name, [(0, z0), (L, z0), (L, z1b), (0, z1)], th, x=0, bevel=0.01, seg=1, mat=mat)
    cutters = []
    for i, (u0, u1, hz0, hz1) in enumerate(holes):
        cutters.append(boxr(f"{name}_h{i}", -th, th, u0 * L, u1 * L, hz0, hz1))
    if cutters:
        us.cut(o, cutters[0] if len(cutters) == 1 else cb.join(cutters, name + "_hc"))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
    cb.apply_modifiers(o)
    o.rotation_euler = (0, 0, math.radians(ang))
    o.location = (x0, y0, 0)
    return o


def win_glass(name, p0, p1, u0, u1, z0, z1, th=0.012):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    g = boxr(name, -th / 2, th / 2, u0 * L - 0.01, u1 * L + 0.01, z0 - 0.01, z1 + 0.01)
    cb.apply_transform(g, location=True)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
    g.rotation_euler = (0, 0, math.radians(ang))
    g.location = (x0, y0, 0)
    vu.setmat(g, "glass")
    return g


# 앞판 (가운데 + 양쪽 경사면), 옆판. 가운데 앞판에는 총 슬롯과 양쪽 방탄창
W0, W1 = 2.40, 2.71
FC = 0.30
pts_front = [(-0.66, RC[1] - 0.47), (-FC, SH_F), (FC, SH_F), (0.66, RC[1] - 0.47)]
b.p(T, vplate("sh_front_R", (-0.075, SH_F), (-FC, SH_F), ZT0, SH_TOP, 0.03,
              holes=[(0.07, 0.90, W0, W1)]))
b.p(T, vplate("sh_front_L", (FC, SH_F), (0.075, SH_F), ZT0, SH_TOP, 0.03, holes=[(0.10, 0.93, W0, W1)]))
b.p(T, vplate("sh_bridge", (0.075, SH_F), (-0.075, SH_F), 2.72, SH_TOP, 0.03))
b.p(T, win_glass("sh_glass_R", (-0.075, SH_F), (-FC, SH_F), 0.07, 0.90, W0, W1))
b.p(T, win_glass("sh_glass_L", (FC, SH_F), (0.075, SH_F), 0.10, 0.93, W0, W1))
for sx in (-1, 1):
    pa, pb = (sx * FC, SH_F), (sx * 0.66, RC[1] - 0.47)
    if sx > 0:
        pa, pb = pb, pa
    b.p(T, vplate(f"sh_wing{sx}", pa, pb, ZT0, SH_TOP, 0.03, holes=[(0.12, 0.86, W0, W1)]))
    b.p(T, win_glass(f"sh_wing_glass{sx}", pa, pb, 0.12, 0.86, W0, W1))
    # 옆판 (뒤로 낮아짐)
    qa, qb = (sx * 0.66, RC[1] - 0.47), (sx * 0.66, RC[1] + 0.20)
    if sx < 0:
        qa, qb = qb, qa
    b.p(T, vplate(f"sh_side{sx}", qa, qb, ZT0, SH_TOP if sx > 0 else 2.50, 0.03,
                  top1=2.50 if sx > 0 else SH_TOP))
    # 방호판 받침대 (링 위)
    b.p(T, vu.beam(f"sh_strut{sx}", (sx * 0.45, RC[1] - 0.30, ZT0), (sx * 0.62, RC[1] - 0.47, ZT0 + 0.30), 0.05,
                   0.05, mat="tan_dk"))
    b.p(T, vu.beam(f"sh_strut_s{sx}", (sx * 0.58, RC[1] + 0.05, ZT0), (sx * 0.645, RC[1] + 0.05, ZT0 + 0.30), 0.05,
                   0.05, mat="tan_dk"))
# 방호판 볼트 (창 둘레) + 청록 표식
for sx in (-1, 1):
    for z in (W0 - 0.04, W1 + 0.04):
        for x in (0.10, 0.28):
            b.pf(T, vu.radial_disc(f"shb{sx}{z}{x}", (sx * x, SH_F - 0.017, z), (0, -1, 0), 0.012, 0.005, verts=6,
                                   mat="tan_dk"))
b.pf(T, text("sh_no", "MNT-V07", 0.06, (0.19, SH_F - 0.017, 2.24), mat="paint", **FR))
# 피벗 받침 (링 앞쪽에서 안으로 뻗은 받침대) + 피벗
b.p(T, boxr("pintle_arm", -0.07, 0.07, RC[1] - 0.66, PY + 0.07, ZT0 - 0.005, ZT0 + 0.05, bevel=0.01, mat="tan_dk"))
b.p(T, zcyl("pintle_socket", 0.05, ZT0 + 0.05, ZT0 + 0.09, x=0, y=PY, verts=14, mat="black"))
pin = vu.pintle("m2_pintle", (0, PY, PZ), post_h=PZ - (ZT0 + 0.08))
b.p(T, *pin["main"])
b.pf(T, *pin["fine"])
b.part(T, RC, yawMin=-180, yawMax=180)

# ================================================================== 거치 무기, 자리, 탑승 위치
b.empty("mount_m2", (0, PY, PZ), parent=T, rot=(0, 0, 180), weapon="m2", yawMin=0, yawMax=0, pitchMin=-15,
        pitchMax=40, restYawDeg=180)
b.empty("seat_gunner", (0, PY + 0.80, PZ + 0.33), parent=T, controls="turret,mount_m2")
b.empty("seat_driver", (0.50, 0.12, 1.56), controls="drive")   # 얇은 방석 위 눈 (예전 두 장일 때 1.70)
b.empty("seat_passenger_1", (-0.50, 0.12, 1.55))
b.empty("seat_passenger_2", (0.50, 1.02, 1.55))
b.empty("seat_passenger_3", (-0.50, 1.02, 1.55))
b.empty("enter_driver", (1.60, 0.0, 0))
b.empty("enter_passenger_1", (-1.60, 0.0, 0))
b.empty("enter_passenger_2", (1.60, 1.00, 0))
b.empty("enter_passenger_3", (-1.60, 1.00, 0))
b.empty("enter_gunner", (-1.60, 1.00, 0))

# ================================================================== 등
for sx, nm in ((1, "L"), (-1, "R")):
    hl = ycyl(f"hl_lens{sx}", 0.086, -2.345, -2.333, x=sx * 0.50, z=0.85, verts=20)
    vu.setmat(hl, "lamp")
    b.p(f"light_head_{nm}", hl)
    b.part(f"light_head_{nm}", (sx * 0.50, -2.34, 0.85))
    tl = boxr(f"tl_lens{sx}", min(sx * 0.83, sx * 0.99), max(sx * 0.83, sx * 0.99), 2.444, 2.452, 0.96, 1.10)
    vu.setmat(tl, "tail")
    b.p(f"light_tail_{nm}", tl)
    b.part(f"light_tail_{nm}", (sx * 0.91, 2.45, 1.03))

# ================================================================== 바퀴
for nm, ya, sx, steer in (("FL", AXF, 1, 1), ("FR", AXF, -1, 1), ("RL", AXR, 1, 0), ("RR", AXR, -1, 0)):
    w = vu.wheel(f"w{nm}", TR, TW, rim_r=0.235, outer=sx, lugs=20, segs=28, nuts=8)
    c = (sx * WX, ya, TR)
    for k in ("main", "thin", "fine"):
        for o in w[k]:
            us.xform(o, loc=c)
    part = f"wheel_{nm}"
    b.p(part, *w["main"])
    b.pt(part, *w["thin"])
    b.pf(part, *w["fine"])
    b.part(part, c, radius=TR, steer=steer, width=TW)

# ================================================================== 충돌체 (단순 볼록)
b.col("COL_hull", boxr("c1", -1.12, 1.12, -2.50, 2.50, 0.50, 1.30))
b.col("COL_cab", boxr("c2", -1.07, 1.07, -0.50, 1.53, 1.30, ZR))
b.col("COL_rear", boxr("c3", -1.07, 1.07, 1.53, 2.38, 1.30, 1.62))
b.col("COL_turret", boxr("c4", -0.68, 0.68, SH_F - 0.03, RC[1] + 0.22, ZT0, SH_TOP), parent=T)

b.finish("vehicles/us/humvee.glb", outline=0.010, thin=0.004, props={
    "vehicleClass": "wheeled", "mass": 5500, "maxSpeed": 27.0, "wheelbase": WB, "track": TRK, "armor": "light",
    "drive": "4x4", "seats": "driver,passenger_1,passenger_2,passenger_3,gunner",
})
