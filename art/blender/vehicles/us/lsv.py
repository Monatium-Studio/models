"""노획 고속기동차량 (경량 공격차, 사막 순찰차 계열 롤케이지 버기) + 케이지 위 링 마운트 M2.

npm run model -- art/blender/vehicles/us/lsv.py
npm run shot -- vehicles/us/lsv.glb --views front,34,side,top

규약: docs/art/VEHICLES.md. 정면 -Y, 왼쪽 +X, 원점 = 차체 중심 아래 지면.
특정 제조사 모델이 아니라 일반적인 군용 경량 공격차 형태: 낮은 코, 드러난 튜브 롤케이지, 큰 오프로드 바퀴,
뒤 엔진 위 사수 데크, 케이지 꼭대기 사수 링(M2), 뒤에 세운 스페어 타이어. 전장 4.4 m, 전폭 2.1 m, 축거 2.85 m.
엘프식 흔적: 운전석 분홍 방석(엉덩이 + 등), 페달 나무 블록, 사수 발판 상자 + 방석, 스페어 타이어의 '초보운전' 판,
롤케이지의 창고 태그, 청록 관리번호.
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
b = vu.VBuild("lsv")

WB, TRK = 2.85, 1.80
TR, TW = 0.40, 0.30
AXF, AXR = -WB / 2, WB / 2
WX = TRK / 2
RZ = 1.80                 # 사수 링 높이
RC = (0.0, 0.70, RZ)      # 링 중심
RR = 0.50                 # 링 반지름
PY = RC[1] - 0.36         # M2 피벗 y
PZ = RZ + 0.24            # M2 고각 핀 높이
CT = 0.026                # 케이지 관 반지름
LS = dict(right=(0, 1, 0), up=(0, 0, 1))
RS = dict(right=(0, -1, 0), up=(0, 0, 1))
FR = dict(right=(1, 0, 0), up=(0, 0, 1))
BK = dict(right=(-1, 0, 0), up=(0, 0, 1))


def cage(name, pts, r=CT, rad=0.10, mat="tan"):
    return b.t(vu.tube(name, vu.rounded_path(pts, rad, 2), r, mat=mat, verts=8))


# ================================================================== 바닥, 코, 옆 포드, 대시
b.s(boxr("floor", -0.62, 0.62, -1.05, 1.85, 0.42, 0.48, bevel=0.01, mat="tan_dk"))
nose = [(-0.98, 0.46), (-1.96, 0.46), (-2.10, 0.56), (-2.12, 0.68), (-1.98, 0.80), (-1.00, 1.00)]
b.s(side("nose", nose, 1.24, bevel=0.02, seg=1, mat="tan"))
b.s(side("nose_hump", [(-1.80, 0.85), (-1.70, 0.885), (-1.06, 1.015), (-1.02, 0.995)], 0.70, bevel=0.012, seg=1,
         mat="tan"))
for sx in (-1, 1):
    b.s(boxr(f"pod{sx}", min(sx * 0.58, sx * 0.80), max(sx * 0.58, sx * 0.80), -0.98, 0.32, 0.42, 0.62,
             bevel=0.025, mat="tan"))
    for y in (-0.80, -0.50, -0.20, 0.10):
        b.f(vu.radial_disc(f"pod_bolt{sx}{y}", (sx * 0.802, y, 0.58), (sx, 0, 0), 0.010, 0.005, verts=6,
                           mat="tan_dk"))
    b.f(text(f"nose_no{sx}", "MNT-V12", 0.075, (sx * 0.622, -1.50, 0.66), mat="paint", **(LS if sx > 0 else RS)))
b.s(boxr("dash", -0.66, 0.66, -1.03, -0.90, 0.84, 1.04, bevel=0.015, mat="tan_dk"))
b.s(boxr("gauges", 0.20, 0.56, -0.905, -0.895, 0.90, 1.00, mat="black"))
for i, x in enumerate((0.27, 0.38, 0.49)):
    b.f(ycyl(f"gauge{i}", 0.032, -0.895, -0.891, x=x, z=0.95, verts=12, mat="paper"))
b.s(boxr("skid", -0.52, 0.52, -2.08, -1.30, 0.38, 0.43, bevel=0.01, mat="tan_dk"))
b.t(vu.tube("tow_loop", [(-0.10, -2.11, 0.52), (-0.10, -2.20, 0.50), (0.10, -2.20, 0.50), (0.10, -2.11, 0.52)],
            0.014, mat="black", verts=6))

# ================================================================== 엔진 박스 (뒤) = 사수 데크
eng = boxr("engine", -0.60, 0.60, 0.36, 1.84, 0.48, 0.98, bevel=0.035, seg=1, mat="tan")
b.s(eng)
b.s(boxr("deck_plate", -0.56, 0.56, 0.40, 1.78, 0.98, 1.0, mat="tan_dk"))
for sx in (-1, 1):
    for i in range(7):   # 옆 라디에이터 루버
        y = 0.95 + i * 0.11
        b.f(boxr(f"louver{sx}{i}", min(sx * 0.601, sx * 0.606), max(sx * 0.601, sx * 0.606), y, y + 0.05, 0.62, 0.86,
                 mat="black"))
    b.f(text(f"eng_no{sx}", "MNT-V12", 0.08, (sx * 0.602, 0.62, 0.74), mat="paint", **(LS if sx > 0 else RS)))
b.s(boxr("intake", -0.52, -0.22, 1.40, 1.72, 1.0, 1.12, bevel=0.02, mat="tan"))
for i in range(4):
    b.f(boxr(f"intake_slot{i}", -0.50, -0.24, 1.44 + i * 0.07, 1.47 + i * 0.07, 1.12, 1.124, mat="black"))
# 배기 (오른쪽 뒤 둘)
for k, x in enumerate((-0.30, -0.42)):
    b.t(vu.tube(f"exh{k}", [(x, 1.70, 0.60), (x, 1.92, 0.58), (x - 0.02, 2.02, 0.62)], 0.032, mat="black", verts=8))
b.empty("exhaust_1", (-0.36, 2.05, 0.62), dir="0,0,-1")

# ================================================================== 롤케이지
for sx in (-1, 1):
    cage(f"a_pillar{sx}", [(sx * 0.66, -0.98, 0.92), (sx * 0.62, -0.50, 1.70)])
    cage(f"roof_rail{sx}", [(sx * 0.62, -0.50, 1.70), (sx * 0.62, 0.30, 1.76), (sx * 0.62, 1.16, 1.76),
                            (sx * 0.66, 1.86, 1.02), (sx * 0.66, 1.96, 0.56)], rad=0.14)
    cage(f"side_lo{sx}", [(sx * 0.80, -0.98, 0.56), (sx * 0.80, 0.30, 0.56)], r=0.024)
    cage(f"side_hi{sx}", [(sx * 0.70, -0.96, 0.94), (sx * 0.76, -0.40, 0.98), (sx * 0.74, 0.30, 0.98)], r=0.024)
    cage(f"nose_strut{sx}", [(sx * 0.66, -0.98, 0.92), (sx * 0.56, -1.60, 0.86), (sx * 0.52, -2.06, 0.70)], r=0.022)
    cage(f"rear_lo{sx}", [(sx * 0.66, 1.96, 0.56), (sx * 0.62, 0.40, 0.56)], r=0.022)
    # 링 받침 브래킷
    b.t(vu.beam(f"ring_brk{sx}", (sx * 0.62, RC[1], 1.76), (sx * (RR - 0.02), RC[1], RZ - 0.02), 0.05, 0.03,
                mat="tan_dk"))
cage("main_hoop", [(-0.72, 0.30, 0.48), (-0.72, 0.30, 1.62), (-0.62, 0.30, 1.76), (0.62, 0.30, 1.76),
                   (0.72, 0.30, 1.62), (0.72, 0.30, 0.48)], r=0.030, rad=0.12)
cage("front_bar", [(-0.62, -0.50, 1.70), (0.62, -0.50, 1.70)])
cage("hoop_diag", [(-0.70, 0.30, 0.60), (0.64, 0.30, 1.68)], r=0.022)
cage("rear_bar", [(-0.62, 1.16, 1.76), (0.62, 1.16, 1.76)])
cage("rear_frame", [(-0.66, 1.96, 0.56), (0.66, 1.96, 0.56)], r=0.024)
cage("dash_bar", [(-0.66, -0.98, 0.92), (0.66, -0.98, 0.92)], r=0.024)
# 앞 범퍼 + 브러시 가드
cage("bumper", [(-0.70, -2.04, 0.58), (-0.62, -2.18, 0.58), (0.62, -2.18, 0.58), (0.70, -2.04, 0.58)], r=0.028,
     mat="black")
for sx in (-1, 1):
    cage(f"guard{sx}", [(sx * 0.30, -2.18, 0.58), (sx * 0.30, -2.18, 0.86), (sx * 0.22, -2.06, 0.94)], r=0.022,
         mat="black")
cage("guard_top", [(-0.22, -2.06, 0.94), (0.22, -2.06, 0.94)], r=0.022, mat="black")
# 지붕 등 (앞 가로대 위 둘)
for sx in (-1, 1):
    b.t(ycyl(f"roof_lamp{sx}", 0.065, -0.60, -0.50, x=sx * 0.30, z=1.79, verts=14, mat="black"))
    b.f(ycyl(f"roof_lamp_lens{sx}", 0.052, -0.604, -0.598, x=sx * 0.30, z=1.79, verts=14, mat="paper"))
    b.t(zcyl(f"roof_lamp_post{sx}", 0.012, 1.70, 1.74, x=sx * 0.30, y=-0.52, verts=6, mat="black"))

# ================================================================== 서스펜션 (긴 행정 A암 + 코일오버)
for sx in (-1, 1):
    for (y0, y1) in ((AXF - 0.20, AXF + 0.20),):
        for z0, z1 in ((0.50, 0.46), (0.68, 0.58)):
            b.s(vu.beam(f"fa{sx}{z0}a", (sx * 0.50, y0, z0), (sx * 0.72, AXF, z1), 0.04, 0.035, mat="tan_dk"))
            b.s(vu.beam(f"fa{sx}{z0}b", (sx * 0.50, y1, z0), (sx * 0.72, AXF, z1), 0.04, 0.035, mat="tan_dk"))
    b.s(xcyl(f"knuckle_f{sx}", 0.09, sx * 0.68, sx * 0.76, y=AXF, z=TR, verts=12, mat="black"))
    b.s(xcyl(f"knuckle_r{sx}", 0.09, sx * 0.68, sx * 0.76, y=AXR, z=TR, verts=12, mat="black"))
    for (ya, top) in ((AXF, (sx * 0.58, AXF + 0.10, 1.00)), (AXR, (sx * 0.58, AXR - 0.20, 1.02))):
        bot = (sx * 0.66, ya, 0.52)
        b.s(vu.beam(f"shock{sx}{ya}", bot, top, 0.045, 0.045, mat="black"))
        mid = [(bot[i] * 0.55 + top[i] * 0.45) for i in range(3)]
        b.t(vu.beam(f"spring{sx}{ya}", [bot[i] * 0.8 + top[i] * 0.2 for i in range(3)],
                    [bot[i] * 0.25 + top[i] * 0.75 for i in range(3)], 0.085, 0.085, mat="paint"))
        _ = mid
    b.s(vu.beam(f"trail{sx}", (sx * 0.58, 0.45, 0.54), (sx * 0.72, AXR, 0.42), 0.06, 0.06, mat="tan_dk"))

# ================================================================== 좌석, 조종 장치, 엘프 흔적
for sx, nm in ((1, "drv"), (-1, "pas")):
    x = sx * 0.38
    b.s(boxr(f"seat_{nm}", x - 0.22, x + 0.22, -0.48, -0.06, 0.48, 0.60, bevel=0.03, mat="black"))
    bk = boxr(f"back_{nm}", x - 0.21, x + 0.21, -0.08, 0.04, 0.56, 1.28, bevel=0.03, mat="black")
    us.xform(bk, rot=(-14, 0, 0), pivot=(0, -0.02, 0.58))
    b.s(bk)
    for dx in (-0.10, 0.10):   # 4점 벨트
        b.t(vu.beam(f"belt_{nm}{dx}", (x + dx, 0.08, 1.24), (x + dx * 0.6, -0.30, 0.66), 0.045, 0.008, mat="od"))
SWC = (0.38, -0.72, 1.02)
b.s(us.torus("steer_rim", 0.17, 0.015, loc=SWC, rot=(-50, 0, 0), seg=14, rseg=5, mat="black"))
b.s(vu.beam("steer_col", (0.38, -0.94, 0.90), SWC, 0.045, 0.045, mat="black"))
b.s(vu.beam("steer_spoke", (0.22, SWC[1] - 0.01, SWC[2] - 0.02), (0.54, SWC[1] - 0.01, SWC[2] - 0.02), 0.03, 0.02,
            mat="black"))
b.t(vu.tube("shifter", [(0.10, -0.55, 0.48), (0.10, -0.50, 0.78)], 0.012, mat="black", verts=6))
b.s(cb.sphere("shift_knob", 0.03, loc=(0.10, -0.50, 0.80), segments=8, rings=5, material=vu.M("black")))
b.t(vu.tube("grab_bar", [(-0.64, -0.92, 0.95), (-0.55, -0.86, 1.02), (-0.20, -0.86, 1.02), (-0.12, -0.92, 0.95)],
            0.014, mat="black", verts=6))
for (x, pn) in ((0.48, "gas"), (0.30, "brake")):
    b.s(boxr(f"pedal_{pn}", x - 0.035, x + 0.035, -0.97, -0.94, 0.50, 0.62, bevel=0.005, mat="black"))
    b.s(boxr(f"pedal_ext_{pn}", x - 0.045, x + 0.045, -0.94, -0.80, 0.50, 0.60, bevel=0.01, mat="coyote"))
    b.t(boxr(f"pedal_strap_{pn}", x - 0.05, x + 0.05, -0.90, -0.87, 0.495, 0.605, mat="od"))
cu, tf = vu.cushion("drv_cushion", (0.38, -0.27, 0.60), 0.40, 0.38, 0.13)
b.s(cu)
b.f(*tf)
bcu, btf = vu.cushion("drv_backcushion", (0.0, 0.0, 0.0), 0.36, 0.30, 0.10, tufts=False)
us.xform(bcu, rot=(76, 0, 0), loc=(0.38, -0.03, 0.88))
b.s(bcu)
# 사수 발판 (엔진 데크 위 상자 + 방석)
GY = PY + 0.74
b.s(boxr("g_crate", -0.20, 0.20, GY - 0.17, GY + 0.17, 1.0, 1.34, bevel=0.015, mat="od"))
b.f(text("g_crate_t", "MNT", 0.06, (0, GY - 0.172, 1.17), mat="paper", **FR))
gcu, gtf = vu.cushion("gunner_cushion", (0, GY, 1.34), 0.36, 0.30, 0.09)
b.s(gcu)
b.f(*gtf)
b.t(boxr("g_strap", -0.205, 0.205, GY - 0.02, GY + 0.02, 1.0, 1.345, mat="od"))

# ================================================================== 짐: 연료통·물통, 스페어 타이어 + 초보운전 판, 안테나, 태그
for sx, mat, lab in ((-1, "od", "FUEL"), (1, "tan_dk", "WATER")):
    x0, x1 = sorted((sx * 0.61, sx * 0.78))
    b.s(boxr(f"jerry{sx}", x0, x1, 0.44, 0.78, 0.50, 0.96, bevel=0.02, mat=mat))
    xs = sx * 0.781
    for (y0, y1, z0, z1) in ((0.47, 0.75, 0.70, 0.73), (0.47, 0.75, 0.80, 0.83)):
        b.f(boxr(f"jerry_rib{sx}{z0}", min(xs, xs + sx * 0.004), max(xs, xs + sx * 0.004), y0, y1, z0, z1, mat=mat))
    b.t(boxr(f"jerry_handle{sx}", x0 + 0.03, x1 - 0.03, 0.50, 0.72, 0.96, 1.00, bevel=0.008, mat=mat))
    b.t(boxr(f"jerry_strap{sx}", x0 - 0.005, x1 + 0.005, 0.59, 0.63, 0.50, 0.965, mat="black"))
    b.f(text(f"jerry_t{sx}", lab, 0.05, (sx * 0.782, 0.61, 0.62), mat="paper", **(LS if sx > 0 else RS)))
SP = (0.0, 2.12, 0.80)
sp = vu.wheel("spare", TR, 0.28, rim_r=0.21, outer=1, lugs=0, segs=20, nuts=5, beadlock=False, rim_segs=14)
for k in ("main", "thin", "fine"):
    for o in sp[k]:
        us.xform(o, rot=(0, 0, 90))
        us.xform(o, loc=SP)
b.s(*sp["main"])
b.t(*sp["thin"])
b.f(*sp["fine"])
b.s(boxr("spare_mount", -0.08, 0.08, 1.95, 2.02, 0.56, 0.92, bevel=0.01, mat="tan_dk"))
b.s(boxr("beginner_plate", -0.20, 0.20, 2.272, 2.282, 0.58, 0.74, bevel=0.006, mat="yellow"))
b.f(text("beginner_kr", "초보운전", 0.085, (0, 2.283, 0.66), mat="black", font="kr", **BK))
b.t(vu.tube("plate_wire", [(-0.17, 2.27, 0.74), (-0.10, 2.27, 0.92), (0.10, 2.27, 0.92), (0.17, 2.27, 0.74)],
            0.004, mat="black", verts=5))
b.s(zcyl("ant_base", 0.03, 1.02, 1.12, x=0.66, y=1.86, verts=8, mat="black"))
b.t(vu.tube("antenna", vu.rounded_path([(0.66, 1.86, 1.10), (0.66, 1.86, 2.10), (0.64, 1.70, 2.70),
                                        (0.62, 1.40, 2.90)], 0.3, 2), 0.006, mat="black", verts=5))
vu.tag(b, (0.775, -0.44, 0.905), scale=3.0, lines=("MNT", "V-0012", "모나티엄 창고"), yaw=3,
       cord_top=(0.77, -0.44, 0.955), f_add=b.t)

# ================================================================== 사수 링 (정지 하단) + 회전부(포탑)
b.t(us.torus("ring_base", RR, 0.032, loc=(RC[0], RC[1], RZ), seg=28, rseg=6, mat="tan_dk"))
T = "turret"
b.p(T, us.torus("ring_top", RR, 0.030, loc=(RC[0], RC[1], RZ + 0.055), seg=28, rseg=6, mat="tan"))
for i in range(6):   # 링 구름 블록
    a = math.radians(30 + 60 * i)
    b.p(T, boxr(f"ring_block{i}", RR * math.cos(a) - 0.03, RR * math.cos(a) + 0.03, RC[1] + RR * math.sin(a) - 0.03,
                RC[1] + RR * math.sin(a) + 0.03, RZ + 0.01, RZ + 0.045, mat="black"))
half = math.sqrt(RR ** 2 - (RC[1] - PY) ** 2)
b.p(T, vu.beam("pintle_bar", (-half, PY, RZ + 0.055), (half, PY, RZ + 0.055), 0.07, 0.05, mat="tan_dk"))
b.p(T, zcyl("pintle_socket", 0.048, RZ + 0.08, RZ + 0.12, x=0, y=PY, verts=14, mat="black"))
b.p(T, vu.beam("ring_handle", (-0.30, RC[1] + 0.40, RZ + 0.08), (0.30, RC[1] + 0.40, RZ + 0.08), 0.03, 0.03,
               mat="black"))
pin = vu.pintle("m2_pintle", (0, PY, PZ), post_h=PZ - (RZ + 0.11))
b.p(T, *pin["main"])
b.pf(T, *pin["fine"])
b.part(T, RC, yawMin=-180, yawMax=180)

b.empty("mount_m2", (0, PY, PZ), parent=T, rot=(0, 0, 180), weapon="m2", yawMin=0, yawMax=0, pitchMin=-20,
        pitchMax=50, restYawDeg=180)
b.empty("seat_gunner", (0, GY, PZ + 0.33), parent=T, controls="turret,mount_m2")
b.empty("seat_driver", (0.38, -0.30, 1.34), controls="drive")
b.empty("seat_passenger_1", (-0.38, -0.27, 1.20))
b.empty("enter_driver", (1.40, -0.30, 0))
b.empty("enter_passenger_1", (-1.40, -0.30, 0))
b.empty("enter_gunner", (0, 2.75, 0))

# ================================================================== 등
for sx, nm in ((1, "L"), (-1, "R")):
    b.s(ycyl(f"hl_house{sx}", 0.075, -2.11, -2.02, x=sx * 0.42, z=0.74, verts=16, mat="black"))
    hl = ycyl(f"hl_lens{sx}", 0.060, -2.118, -2.108, x=sx * 0.42, z=0.74, verts=16, mat="lamp")
    b.p(f"light_head_{nm}", hl)
    b.part(f"light_head_{nm}", (sx * 0.42, -2.115, 0.74))
    tl = boxr(f"tl_lens{sx}", min(sx * 0.50, sx * 0.60), max(sx * 0.50, sx * 0.60), 1.84, 1.85, 0.80, 0.88,
              mat="tail")
    b.s(boxr(f"tl_house{sx}", min(sx * 0.48, sx * 0.62), max(sx * 0.48, sx * 0.62), 1.80, 1.842, 0.78, 0.90,
             bevel=0.008, mat="black"))
    b.p(f"light_tail_{nm}", tl)
    b.part(f"light_tail_{nm}", (sx * 0.55, 1.85, 0.84))

# ================================================================== 바퀴
for nm, ya, sx, steer in (("FL", AXF, 1, 1), ("FR", AXF, -1, 1), ("RL", AXR, 1, 0), ("RR", AXR, -1, 0)):
    w = vu.wheel(f"w{nm}", TR, TW, rim_r=0.20, outer=sx, lugs=16, segs=24, nuts=6, rim_segs=16, bead_bolts=0)
    c = (sx * WX, ya, TR)
    for k in ("main", "thin", "fine"):
        for o in w[k]:
            us.xform(o, loc=c)
    part = f"wheel_{nm}"
    b.p(part, *w["main"])
    b.pt(part, *w["thin"])
    b.pf(part, *w["fine"])
    b.part(part, c, radius=TR, steer=steer, width=TW)

# ================================================================== 충돌체
b.col("COL_hull", boxr("c1", -0.82, 0.82, -2.20, 2.26, 0.38, 1.02))
b.col("COL_cage", boxr("c2", -0.76, 0.76, -0.98, 1.90, 1.02, 1.80))

b.finish("vehicles/us/lsv.glb", outline=0.008, thin=0.0035, props={
    "vehicleClass": "wheeled", "mass": 1600, "maxSpeed": 33.0, "wheelbase": WB, "track": TRK, "armor": "light",
    "drive": "4x4", "seats": "driver,passenger_1,gunner",
})
