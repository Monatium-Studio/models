"""M2 중기관총 (거치형, 노획 미군 화기).

npm run model -- art/blender/weapons/us/m2.py
npm run shot -- weapons/us/m2.glb --views side,34,top,34b
npm run shot -- weapons/us/m2.glb --mode fp            # 거치 사격 시점 (모델의 fpOffset)
npm run shot -- weapons/us/m2.glb --mode fp --ads 1    # 가늠자 정렬

원점 = 마운트 회전축. 요람(크래들) 아래 중앙 러그의 고각 핀 중심이고, 피벗 기둥의 수직축이 이 점을 지난다.
차량의 mount_* 에 그대로 붙인다: 요는 mount 노드, 피치는 이 루트(로컬 X축). 피벗 기둥과 클레비스는 차량 쪽
(vehicles_us.pintle)이라 링 마운트(험비, LSV)와 피벗 마운트(M1A1 전차장) 어디에나 맞는다.
실측 기준: 전장 ≈1.65 m, 총열 1.14 m. 엘프에게는 사람 키만 한 총이다.
움직이는 파츠: cover(앞 경첩), bolt, charging_handle(오른쪽 장전 손잡이), trigger(나비 방아쇠),
ammo_can(탄통), belt(탄띠).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402
import vehicles_us as vu  # noqa: E402

cb.reset()
b = us.Build("m2")

ZB = 0.135                 # 총열 축 높이 (고각 핀 위)
RW = 0.066                 # 리시버 반폭 (옆판 포함)
RB = ZB - 0.082            # 리시버 바닥
RF = ZB + 0.050            # 리시버 윗면 = 덮개 아래 이음
RT = ZB + 0.078            # 덮개 윗면
RY0, RY1 = -0.400, 0.150   # 리시버 뒤(뒷판 앞면) / 앞(트러니언 블록 앞)
CV0, CV1 = -0.300, 0.100   # 덮개 범위
ZA = RT + 0.058            # 가늠선 높이 (가늠자 홈 바닥 = 가늠쇠 끝)
MUZ = 1.075
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))

# ================================================================== receiver
rsec = [(-RW, RB + 0.008), (-RW + 0.008, RB), (RW - 0.008, RB), (RW, RB + 0.008), (RW, RF), (-RW, RF)]
b.s(us.section("receiver", rsec, RY0, CV1, bevel=0.002, seg=1, mat="black"))
# 뒤 블록 (덮개 뒤, 가늠자 받침)
rear_sec = [(-RW, RF - 0.002), (RW, RF - 0.002), (RW, RT - 0.012), (RW - 0.012, RT), (-RW + 0.012, RT),
            (-RW, RT - 0.012)]
b.s(us.section("rear_block", rear_sec, RY0, CV0 - 0.002, bevel=0.002, seg=1, mat="black"))
# 트러니언 블록 (앞, 한 단 두꺼움)
tw = RW + 0.005
tsec = [(-tw, RB - 0.004), (tw, RB - 0.004), (tw, RT - 0.014), (tw - 0.012, RT - 0.002), (-tw + 0.012, RT - 0.002),
        (-tw, RT - 0.014)]
b.s(us.section("trunnion", tsec, CV1, RY1, bevel=0.003, seg=1, mat="black"))
# 옆판 아래 보강 띠 + 위 레일 (실루엣에 가로 줄)
for sx in (-1, 1):
    x0 = sx * RW
    x1 = sx * (RW + 0.003)
    b.s(us.boxr(f"rail_lo{sx}", min(x0, x1), max(x0, x1), RY0 + 0.010, CV1 - 0.004, RB + 0.010, RB + 0.022,
                bevel=0.001, mat="black"))
    b.s(us.boxr(f"rail_hi{sx}", min(x0, x1), max(x0, x1), RY0 + 0.010, CV0 - 0.010, RF - 0.016, RF - 0.006,
                bevel=0.001, mat="black"))
# 장전 손잡이 슬롯 (오른쪽)
b.s(us.boxr("ch_slot", RW - 0.001, RW + 0.0008, -0.215, 0.010, ZB - 0.019, ZB - 0.005, mat="steel"))
# 링크 배출구 (오른쪽 앞) / 급탄 입구 테두리 (왼쪽)
b.s(us.boxr("link_port", RW - 0.001, RW + 0.0012, -0.030, 0.075, RF - 0.014, RF - 0.002, mat="steel"))
b.s(us.boxr("feed_lip", -RW - 0.012, -RW + 0.001, -0.060, 0.100, RF - 0.006, RF + 0.001, bevel=0.0015,
            mat="black"))
# 급탄판 (덮개를 열면 보임)
b.s(us.boxr("feed_tray", -RW + 0.004, RW - 0.004, -0.050, 0.092, RF, RF + 0.004, bevel=0.001, mat="steel"))
for i, x in enumerate((-0.030, 0.0, 0.030)):
    b.f(us.boxr(f"tray_groove{i}", x - 0.003, x + 0.003, -0.048, 0.090, RF + 0.004, RF + 0.0046, mat="black"))
# 리벳 (옆판)
for sx in (-1, 1):
    for y in (-0.370, -0.270, -0.170, -0.070, 0.040):
        for z in (RB + 0.032, RF - 0.026):
            if sx > 0 and -0.22 < y < 0.02 and z > ZB - 0.03:
                continue
            b.f(us.xcyl(f"rv{sx}{y}{z}", 0.0034, sx * RW, sx * (RW + 0.0014), y=y, z=z, verts=6, mat="steel"))
    for (y, z) in ((0.115, ZB + 0.040), (0.135, ZB + 0.040), (0.115, ZB - 0.050), (0.135, ZB - 0.050)):
        b.f(us.xcyl(f"trv{sx}{y}{z}", 0.0045, sx * tw, sx * (tw + 0.0016), y=y, z=z, verts=6, mat="steel"))
# 각인 (왼쪽 옆판): 일반 표기만
b.f(us.text("mk1", "U.S.  CAL .50  M2 HB", 0.0105, (-RW - 0.0016, -0.165, ZB - 0.004), mat="bright", **L_))

# ================================================================== backplate / spade grips / trigger
BP0 = RY0 - 0.026
bw = RW + 0.008
bsec = [(-bw, RB - 0.006), (bw, RB - 0.006), (bw, RT - 0.016), (bw - 0.016, RT - 0.002), (-bw + 0.016, RT - 0.002),
        (-bw, RT - 0.016)]
b.s(us.section("backplate", bsec, BP0, RY0 + 0.002, bevel=0.003, seg=1, mat="black"))
b.s(us.ycyl("buffer", 0.026, BP0 - 0.030, BP0 + 0.001, z=ZB + 0.006, verts=16, mat="black"))
b.s(us.ycyl("buffer_cap", 0.018, BP0 - 0.036, BP0 - 0.028, z=ZB + 0.006, verts=14, mat="steel"))
GX, GY = 0.090, -0.528
GZ0, GZ1 = ZB - 0.082, ZB + 0.046
for sx in (-1, 1):
    gx = sx * GX
    # 위·아래 팔 (뒷판 옆에서 뒤로 뻗어 손잡이를 잡음)
    for zz, nm in ((GZ1 + 0.004, "hi"), (GZ0 - 0.004, "lo")):
        path = [(sx * (bw - 0.010), BP0 + 0.004, zz), (sx * (GX - 0.004), BP0 - 0.040, zz),
                (gx, GY + 0.010, zz)]
        b.s(us.sweep(f"grip_arm_{nm}{sx}", path, us.rrect(0.020, 0.018, 0.006, n=2), side_vec=(0, 0, 1),
                     mat="black", smooth=45))
    # 손잡이 (고무 슬리브) + 끝 캡
    b.s(us.zcyl(f"grip{sx}", 0.0185, GZ0 + 0.004, GZ1 - 0.004, x=gx, y=GY, verts=12, mat="black"))
    for i in range(3):
        z = GZ0 + 0.026 + i * 0.030
        b.s(us.zcyl(f"grip_rib{sx}{i}", 0.0200, z, z + 0.010, x=gx, y=GY, verts=12, mat="black"))
    for zz in (GZ0 - 0.010, GZ1 + 0.002):
        b.s(us.zcyl(f"grip_cap{sx}{zz}", 0.016, zz, zz + 0.010, x=gx, y=GY, verts=10, mat="steel"))
# 노리쇠 멈치 해제 버튼 (뒷판 위 가운데)
b.s(us.boxr("bolt_latch", -0.011, 0.011, BP0 - 0.012, BP0 + 0.001, RF - 0.004, RF + 0.010, bevel=0.003,
            mat="steel"))
# 방아쇠 받침 (뒷판 아래에서 뒤로)
b.s(us.boxr("trig_bracket", -0.012, 0.012, BP0 - 0.052, BP0 + 0.001, GZ0 - 0.002, GZ0 + 0.012, bevel=0.003,
            mat="black"))

# 나비 방아쇠 (엄지로 앞으로 누름, 아래 축)
TY = BP0 - 0.046
tp = [(-0.034, ZB - 0.014), (-0.026, ZB - 0.030), (0.026, ZB - 0.030), (0.034, ZB - 0.014), (0.032, ZB + 0.010),
      (0.010, ZB + 0.002), (-0.010, ZB + 0.002), (-0.032, ZB + 0.010)]
b.p("trigger", us.section("trigger_paddle", tp, TY - 0.004, TY + 0.004, bevel=0.002, seg=1, mat="steel"))
b.p("trigger", us.boxr("trigger_stem", -0.006, 0.006, TY - 0.004, TY + 0.004, GZ0 + 0.006, ZB - 0.026,
                       bevel=0.0015, mat="steel"))
b.pivot("trigger", (0, TY, GZ0 + 0.010), rotAxis="x", rotDeg=-14)

# ================================================================== sights
# 가늠자 (뒤 블록 위, 접개식 잎 세움 + 홈)
b.s(us.boxr("rs_base", -0.020, 0.020, -0.390, -0.330, RT - 0.002, RT + 0.008, bevel=0.003, mat="black"))
NW, ND = 0.0068, 0.016     # 가늠자 홈 반폭, 깊이 (홈 어깨 = 가늠선, 가늠쇠 끝이 어깨와 수평)
leaf = [(-0.014, RT + 0.006), (0.014, RT + 0.006), (0.014, ZA), (NW, ZA), (NW - 0.001, ZA - ND),
        (-NW + 0.001, ZA - ND), (-NW, ZA), (-0.014, ZA)]
b.s(us.section("rs_leaf", leaf, -0.366, -0.360, mat="black"))
for sx in (-1, 1):   # 보호 귀
    b.s(us.side(f"rs_ear{sx}", [(-0.386, RT + 0.006), (-0.338, RT + 0.006), (-0.346, ZA - 0.016),
                                (-0.380, ZA - 0.008)], 0.004, x=sx * 0.019, mat="black"))
b.s(us.xcyl("rs_knob", 0.008, 0.021, 0.034, y=-0.352, z=RT + 0.016, verts=10, mat="steel"))
b.f(us.boxr("rs_scale", 0.0115, 0.0122, -0.3655, -0.3605, RT + 0.020, ZA + 0.004, mat="bright"))
# 가늠쇠 (트러니언 블록 위)
FY = 0.128
b.s(us.boxr("fs_base", -0.016, 0.016, FY - 0.018, FY + 0.018, RT - 0.004, RT + 0.010, bevel=0.003, mat="black"))
b.s(us.boxr("fs_post", -0.0034, 0.0034, FY - 0.003, FY + 0.003, RT + 0.008, ZA - 0.007, mat="black"))
b.f(us.boxr("fs_tip", -0.0034, 0.0034, FY - 0.003, FY + 0.003, ZA - 0.007, ZA, mat="bright"))   # 흰 가늠쇠 끝
for sx in (-1, 1):
    b.s(us.side(f"fs_ear{sx}", [(FY - 0.014, RT + 0.008), (FY + 0.014, RT + 0.008), (FY + 0.008, ZA + 0.006),
                                (FY - 0.008, ZA + 0.006)], 0.0035, x=sx * 0.0125, mat="black"))

# ================================================================== barrel group
b.s(us.ycyl("barrel_support", 0.043, RY1 - 0.002, 0.335, z=ZB, verts=20, mat="steel"))
b.s(us.ycyl("support_collar", 0.047, RY1 - 0.002, RY1 + 0.022, z=ZB, verts=20, mat="steel"))
b.s(us.ycyl("support_nose", 0.046, 0.318, 0.340, z=ZB, verts=20, r2=0.040, mat="steel"))
for j, y in enumerate((0.192, 0.240, 0.288)):   # 냉각 구멍 (엇갈림)
    for a in (0, 50, 100, 150, 200, 330):
        ar = math.radians(a + 25 * (j % 2))
        b.f(vu.radial_disc(f"hole{y}{a}", (0.0432 * math.cos(ar), y, ZB + 0.0432 * math.sin(ar)),
                           (math.cos(ar), 0, math.sin(ar)), 0.0075, 0.0016, verts=6, mat="black"))
b.s(us.ycyl("barrel", 0.0275, 0.335, MUZ - 0.080, z=ZB, verts=18, r2=0.0245, mat="steel"))
b.s(us.ycyl("barrel_ring", 0.0300, 0.335, 0.352, z=ZB, verts=18, mat="steel"))
fh = us.ytube("flash_hider", 0.030, 0.015, MUZ - 0.082, MUZ, z=ZB, verts=16, mat="steel", r_out2=0.041)
b.s(fh)
# 총열 손잡이 (QCB, 왼쪽으로 기울임) + 클램프
for (y0, y1) in ((0.372, 0.404), (0.556, 0.582)):
    b.s(us.ycyl(f"handle_clamp{y0}", 0.0335, y0, y1, z=ZB, verts=14, mat="black"))
hp = [(0, 0.388, ZB + 0.028), (0, 0.392, ZB + 0.070), (0, 0.420, ZB + 0.092), (0, 0.530, ZB + 0.092),
      (0, 0.560, ZB + 0.068), (0, 0.569, ZB + 0.028)]
handle = us.sweep("carry_handle", vu.rounded_path(hp, 0.02, 2), us.rrect(0.020, 0.016, 0.006, n=1),
                  side_vec=(1, 0, 0), mat="black", smooth=50)
us.xform(handle, rot=(0, -48, 0), pivot=(0, 0.47, ZB))
b.s(handle)
hgrip = us.ycyl("handle_grip", 0.0145, 0.428, 0.522, z=ZB + 0.092, verts=10, mat="black")
us.xform(hgrip, rot=(0, -48, 0), pivot=(0, 0.47, ZB))
b.s(hgrip)

# ================================================================== cradle (요람, 고각 핀 러그 포함)
for sx in (-1, 1):
    b.s(us.boxr(f"cradle_rail{sx}", min(sx * 0.040, sx * 0.057), max(sx * 0.040, sx * 0.057), -0.245, 0.140,
                RB - 0.030, RB - 0.002, bevel=0.004, mat="steel"))
for (y0, y1) in ((0.098, 0.140), (-0.245, -0.205)):
    b.s(us.boxr(f"cradle_x{y0}", -0.057, 0.057, y0, y1, RB - 0.030, RB - 0.002, bevel=0.004, mat="steel"))
b.s(us.boxr("cradle_rear_lug", -0.028, 0.028, -0.245, -0.205, RB - 0.002, RB + 0.014, bevel=0.003, mat="steel"))
b.s(us.boxr("cradle_front_lug", -0.020, 0.020, 0.100, 0.138, RB - 0.002, RB + 0.010, bevel=0.003, mat="steel"))
b.f(us.xcyl("front_pin", 0.0085, -tw - 0.003, tw + 0.003, y=0.124, z=RB + 0.016, verts=10, mat="bright"))
# 중앙 러그 (클레비스 안에 들어감, 폭 ±0.025) + 고각 핀
b.s(us.side("cradle_lug", [(-0.050, RB - 0.028), (0.050, RB - 0.028), (0.034, -0.010), (0.022, -0.024),
                           (-0.022, -0.024), (-0.034, -0.010)], 0.050, bevel=0.004, mat="steel"))
b.s(us.xcyl("cradle_boss", 0.028, -0.025, 0.025, y=0, z=0, verts=14, mat="steel"))
b.s(us.xcyl("elev_pin", 0.0095, -0.046, 0.046, y=0, z=0, verts=10, mat="bright"))
# 탄통 받침 (왼쪽)
TZ = -0.081
b.s(us.boxr("tray_bracket", -0.064, -0.057, -0.120, 0.120, TZ, RB - 0.004, bevel=0.002, mat="steel"))
b.s(us.boxr("tray_floor", -0.242, -0.057, -0.165, 0.170, TZ, TZ + 0.006, bevel=0.002, mat="steel"))
for (y0, y1) in ((-0.167, -0.159), (0.164, 0.172)):
    b.s(us.boxr(f"tray_lip{y0}", -0.242, -0.064, y0, y1, TZ, TZ + 0.040, bevel=0.002, mat="steel"))
b.s(us.boxr("tray_lip_out", -0.244, -0.236, -0.167, 0.172, TZ, TZ + 0.034, bevel=0.002, mat="steel"))
b.s(us.boxr("tray_strap", -0.240, -0.075, 0.048, 0.064, TZ + 0.006, TZ + 0.010, mat="black"))

# ================================================================== moving parts
# 덮개 (앞 경첩, 뒤 잠금쇠)
cov_top = [(-RW, RT - 0.012), (RW, RT - 0.012), (RW, RT - 0.008), (RW - 0.010, RT), (-RW + 0.010, RT),
           (-RW, RT - 0.008)]
b.p("cover", us.section("cover_top", cov_top, CV0, CV1 - 0.006, bevel=0.0015, seg=1, mat="black"))
b.p("cover", us.boxr("cover_skirt_R", RW - 0.005, RW, CV0, CV1 - 0.006, RF + 0.001, RT - 0.011, mat="black"))
b.p("cover", us.boxr("cover_skirt_Lr", -RW, -RW + 0.005, CV0, -0.064, RF + 0.001, RT - 0.011, mat="black"))
b.p("cover", us.boxr("cover_skirt_Lf", -RW, -RW + 0.005, 0.096, CV1 - 0.006, RF + 0.001, RT - 0.011,
                     mat="black"))
b.p("cover", us.boxr("cover_rear", -RW, RW, CV0, CV0 + 0.006, RF + 0.001, RT - 0.011, mat="black"))
b.p("cover", us.boxr("feed_hump", -RW + 0.006, RW - 0.006, -0.020, 0.062, RT - 0.004, RT + 0.012, bevel=0.004,
                     seg=1, mat="black"))
b.p("cover", us.boxr("cover_latch", -0.024, 0.024, CV0 - 0.012, CV0 + 0.012, RT - 0.004, RT + 0.008, bevel=0.003,
                     mat="steel"))
b.p("cover", us.xcyl("cover_hinge", 0.0075, -RW + 0.004, RW - 0.004, y=CV1 - 0.004, z=RT - 0.008, verts=10,
                     mat="steel"))
b.p("cover", us.boxr("feed_lever", -0.010, 0.010, -0.160, -0.030, RT - 0.001, RT + 0.005, bevel=0.002,
                     mat="black"))
for sx in (-1, 1):
    for y in (-0.270, -0.120):
        b.pf("cover", us.xcyl(f"cv_rv{sx}{y}", 0.0030, sx * RW, sx * (RW + 0.0012), y=y, z=RT - 0.018, verts=6,
                              mat="steel"))
# 엘프식 흔적: 덮개 위 한글 스티커
b.pf("cover", us.boxr("cover_sticker", 0.016, 0.052, -0.262, -0.206, RT + 0.0002, RT + 0.0008, mat="paper"))
b.pf("cover", us.text("cover_kr1", "덮개 닫고", 0.0085, (0.034, -0.226, RT + 0.0009), right=(1, 0, 0), up=(0, 1, 0),
                      mat="black", font="kr"))
b.pf("cover", us.text("cover_kr2", "쏠 것!", 0.0085, (0.034, -0.244, RT + 0.0009), right=(1, 0, 0), up=(0, 1, 0),
                      mat="red", font="kr"))
b.pivot("cover", (0, CV1 - 0.004, RT - 0.008), rotAxis="x", rotDeg=-80)

# 노리쇠 (덮개를 열면 윗면이 보임, 뒤로 0.17 m)
b.p("bolt", us.boxr("bolt_body", -0.034, 0.034, -0.290, -0.064, RF - 0.030, RF + 0.003, bevel=0.002,
                    mat="bright"))
b.p("bolt", us.boxr("bolt_stud", -0.008, 0.008, -0.230, -0.200, RF + 0.003, RF + 0.010, bevel=0.002, mat="steel"))
b.p("bolt", us.boxr("extractor", -0.012, 0.012, -0.090, -0.060, RF + 0.003, RF + 0.012, bevel=0.002, mat="steel"))
b.pivot("bolt", (0, -0.177, RF - 0.014), move="0,0,0.17")

# 장전 손잡이 (오른쪽, 뒤로 0.17 m 당김)
CHY, CHZ = -0.020, ZB - 0.012
b.p("charging_handle", us.boxr("ch_slide", RW, RW + 0.012, CHY - 0.022, CHY + 0.018, CHZ - 0.012, CHZ + 0.012,
                               bevel=0.003, mat="steel"))
b.p("charging_handle", us.boxr("ch_arm", RW + 0.008, RW + 0.054, CHY - 0.014, CHY + 0.004, CHZ - 0.007,
                               CHZ + 0.007, bevel=0.003, mat="steel"))
b.p("charging_handle", us.ycyl("ch_grip", 0.0115, CHY - 0.070, CHY + 0.006, x=RW + 0.060, z=CHZ, verts=10,
                               mat="black"))
b.pivot("charging_handle", (RW, CHY, CHZ), move="0,0,0.17")

# 탄통 (M2A1, OD) - 뚜껑은 바깥으로 열어 늘어뜨림
CX0, CX1 = -0.234, -0.078
CY0, CY1 = -0.152, 0.152
CZ0, CZ1 = TZ + 0.006, TZ + 0.006 + 0.190
can = us.boxr("can", CX0, CX1, CY0, CY1, CZ0, CZ1, bevel=0.008, seg=2, mat="od")
us.cut(can, us.boxr("can_in", CX0 + 0.004, CX1 - 0.004, CY0 + 0.004, CY1 - 0.004, CZ0 + 0.012, CZ1 + 0.02))
b.p("ammo_can", can)
b.p("ammo_can", us.boxr("can_floor_in", CX0 + 0.004, CX1 - 0.004, CY0 + 0.004, CY1 - 0.004, CZ0 + 0.010,
                        CZ1 - 0.034, mat="od"))
for i, x in enumerate((-0.208, -0.184, -0.122, -0.098)):   # 접힌 탄띠 윗단
    c0 = 0.020 - 0.069
    zz = CZ1 - 0.024
    b.p("ammo_can", us.ycyl(f"fill_case{i}", 0.0102, c0, c0 + 0.099, x=x, z=zz, verts=6, mat="brass"))
    b.p("ammo_can", us.ycyl(f"fill_bul{i}", 0.0066, c0 + 0.099, c0 + 0.138, x=x, z=zz, r2=0.001, verts=6,
                            mat="brass", cap=False))
    b.p("ammo_can", us.ycyl(f"fill_link{i}", 0.0116, c0 + 0.016, c0 + 0.030, x=x, z=zz, verts=6, mat="black"))
for (z0, z1) in ((CZ0 + 0.040, CZ0 + 0.052), (CZ0 + 0.120, CZ0 + 0.132)):   # 옆 보강 리브
    b.p("ammo_can", us.boxr(f"can_rib{z0}", CX0 - 0.003, CX0 + 0.004, CY0 + 0.020, CY1 - 0.020, z0, z1, bevel=0.002,
                            mat="od"))
b.p("ammo_can", us.boxr("can_rim", CX0 - 0.002, CX1 + 0.002, CY0 - 0.002, CY1 + 0.002, CZ1 - 0.014, CZ1,
                        bevel=0.003, mat="od"))
lid = us.boxr("can_lid", CX0 - 0.003, CX1 + 0.003, CY0 - 0.003, CY1 + 0.003, CZ1, CZ1 + 0.016, bevel=0.004,
              mat="od")
lid_h = us.boxr("lid_handle", -0.168, -0.144, -0.050, 0.050, CZ1 + 0.016, CZ1 + 0.028, bevel=0.004, mat="black")
lid_gasket = us.boxr("lid_gasket", CX0 + 0.010, CX1 - 0.010, CY0 + 0.010, CY1 - 0.010, CZ1 - 0.003, CZ1 + 0.001,
                     mat="black")
lid_latch = us.boxr("lid_latch", CX0 + 0.040, CX1 - 0.040, CY1 + 0.002, CY1 + 0.014, CZ1 - 0.010, CZ1 + 0.020,
                    bevel=0.003, mat="od")
for o in (lid, lid_h, lid_latch, lid_gasket):
    us.xform(o, rot=(0, 100, 0), pivot=(CX0 - 0.003, 0, CZ1 + 0.008))
b.p("ammo_can", lid, lid_h, lid_latch, lid_gasket)
b.p("ammo_can", us.ycyl("can_hinge", 0.006, CY0 + 0.020, CY1 - 0.020, x=CX0 - 0.003, z=CZ1 + 0.006, verts=8,
                        mat="od"))
# 탄통 표식: 노랑 스텐실 + 모나티엄 청록 띠
CXM = (CX0 + CX1) / 2
BK = dict(right=(1, 0, 0), up=(0, 0, 1))      # 뒤 끝면 (사수 쪽)
FR = dict(right=(-1, 0, 0), up=(0, 0, 1))     # 앞 끝면
b.pf("ammo_can", us.boxr("can_paint", CX0 + 0.010, CX1 - 0.010, CY0 - 0.0025, CY0 - 0.0005, CZ0 + 0.070,
                         CZ0 + 0.130, mat="paint"))
b.pf("ammo_can", us.text("can_t3", "MNT", 0.026, (CXM, CY0 - 0.0026, CZ0 + 0.108), mat="paper", **BK))
b.pf("ammo_can", us.text("can_kr", "탄약 100발", 0.0135, (CXM, CY0 - 0.0026, CZ0 + 0.084), mat="paper", font="kr",
                         **BK))
b.pf("ammo_can", us.text("can_t1", "CAL .50", 0.0240, (CXM, CY1 + 0.0006, CZ0 + 0.100), mat="yellow", **FR))
b.pivot("ammo_can", ((CX0 + CX1) / 2, 0, CZ0), move="-0.25,0,0")

# 탄띠 (.50 BMG, 링크, 4발마다 예광탄 빨간 끝) - 탄통 위에서 왼쪽 급탄구로
RY_C = 0.020                       # 탄 중심 y (탄피 0.099 + 탄두 0.039)
bp = [(-0.156, CZ1 - 0.030), (-0.154, CZ1 + 0.030), (-0.140, RF + 0.000), (-0.112, RF + 0.010),
      (-0.080, RF + 0.012), (-0.046, RF + 0.011)]
seg_len = [math.dist(bp[i], bp[i + 1]) for i in range(len(bp) - 1)]
PITCH = 0.025
total = sum(seg_len)
n = int(total / PITCH) + 1
for k in range(n):
    d = total - k * PITCH       # 급탄구 쪽 끝에서부터 배치
    i = 0
    while i < len(seg_len) - 1 and d > seg_len[i]:
        d -= seg_len[i]
        i += 1
    t = min(1.0, d / seg_len[i])
    x = bp[i][0] + (bp[i + 1][0] - bp[i][0]) * t
    z = bp[i][1] + (bp[i + 1][1] - bp[i][1]) * t
    c0 = RY_C - 0.069
    b.p("belt", us.ycyl(f"case{k}", 0.0102, c0, c0 + 0.080, x=x, z=z, verts=8, mat="brass"))
    b.p("belt", us.ycyl(f"neck{k}", 0.0102, c0 + 0.080, c0 + 0.099, x=x, z=z, r2=0.0068, verts=8, mat="brass",
                        cap=False))
    tip = "red" if k % 4 == 1 else "brass"
    b.p("belt", us.ycyl(f"bullet{k}", 0.0068, c0 + 0.099, c0 + 0.124, x=x, z=z, r2=0.0040, verts=8, mat="brass",
                        cap=False))
    b.p("belt", us.ycyl(f"tip{k}", 0.0040, c0 + 0.124, c0 + 0.138, x=x, z=z, r2=0.0006, verts=8, mat=tip))
    b.p("belt", us.ycyl(f"link{k}", 0.0118, c0 + 0.014, c0 + 0.030, x=x, z=z, verts=8, mat="black"))
b.pivot("belt", (bp[-1][0], RY_C, bp[-1][1]), feedDir="1,0,0", pitch=PITCH)

# ================================================================== 창고 태그 (총열 손잡이 왼쪽에 매달림)
hang = (-0.072, 0.476, ZB + 0.050)
vu.tag(b, (hang[0] - 0.004, hang[1], hang[2] - 0.040), scale=1.6, lines=("MNT", "H-0002", "모나티엄 창고"),
       yaw=-20, cord_top=hang)

# ================================================================== anchors
b.anchor("muzzle", (0, MUZ, ZB))
b.anchor("eject", (0, 0.010, RB - 0.034))                # 탄피: 아래 (요람 레일 사이)
b.anchor("eject_link", (RW + 0.004, 0.022, RF - 0.008))  # 링크: 오른쪽
b.anchor("mag_well", (-RW - 0.006, RY_C, RF + 0.011))    # 탄띠 입구 (왼쪽)
b.anchor("grip_L", (-GX, GY, (GZ0 + GZ1) / 2))           # 사수 왼손 (-X)
b.anchor("grip_R", (GX, GY, (GZ0 + GZ1) / 2))            # 사수 오른손 (+X)
b.anchor("sight_eye", (0, -0.680, ZA))                   # 가늠자 홈 바닥과 가늠쇠 끝을 잇는 선 위

b.finish("weapons/us/m2.glb", outline=0.003, fp="0,-0.33,-0.80",
         extra={"fpRot": "2,0,0", "mountType": "pintle", "pitchAxis": "x"})
