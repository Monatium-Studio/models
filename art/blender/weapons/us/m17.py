"""M17 권총 (노획 미군 화기, 보조무기).

npm run model -- art/blender/weapons/us/m17.py
npm run shot -- weapons/us/m17.glb --views side,34,top,muzzle

원점 = 손잡이 중앙, 총구 +Y. 실측 기준(전장 0.203, 높이 0.140, 총열 4.7"). 코요테 프레임 + 코요테 PVD 슬라이드.
슬라이드는 별도 파츠(slide)라 후퇴 애니메이션이 가능하다.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m17")

ZB = 0.0645
GA = math.radians(18)
SY0, SY1 = -0.040, 0.163      # 슬라이드 뒤/앞
SB, ST = ZB - 0.012, ZB + 0.0205  # 슬라이드 아래/위
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))


def gp(t, s):
    return (t * math.cos(GA) + s * math.sin(GA), -t * math.sin(GA) + s * math.cos(GA))


# ================================================================== slide (moving)
sl_sec = [(-0.0128, SB), (0.0128, SB), (0.0128, ZB + 0.011), (0.0086, ST), (-0.0086, ST), (-0.0128, ZB + 0.011)]
slide = us.section("slide_body", sl_sec, SY0, SY1, bevel=0.0016, seg=1, mat="pvd")
cutters = []
# 배출구 (오른쪽 위)
cutters.append(us.boxr("port_cut", 0.0015, 0.02, 0.030, 0.072, ZB + 0.003, ZB + 0.03))
# 총구 구멍
cutters.append(us.ycyl("bore_cut", 0.0069, SY1 - 0.012, SY1 + 0.01, z=ZB, verts=16))
# 뒤 · 앞 세레이션
for sx in (-1, 1):
    for i in range(7):
        y = SY0 + 0.004 + i * 0.0033
        cutters.append(us.boxr(f"ser_r{sx}{i}", sx * 0.0118 - 0.003, sx * 0.0118 + 0.003, y, y + 0.0016,
                               SB + 0.004, ZB + 0.013))
    for i in range(5):
        y = SY1 - 0.034 + i * 0.0033
        cutters.append(us.boxr(f"ser_f{sx}{i}", sx * 0.0118 - 0.003, sx * 0.0118 + 0.003, y, y + 0.0016,
                               SB + 0.006, ZB + 0.012))
# 앞 아래 모따기
cutters.append(us.box("nose_cut", (0.04, 0.02, 0.02), (0, SY1 + 0.002, SB - 0.004), rot=(40, 0, 0)))
cut = cutters[0]
for c in cutters[1:]:
    cut = cb.join([cut, c], "slide_cut")
us.cut(slide, cut)
b.p("slide", slide)
# 공이 덮개 (뒷면)
b.p("slide", us.boxr("striker_plate", -0.0062, 0.0062, SY0 - 0.0008, SY0 + 0.001, SB + 0.004, ZB + 0.011,
                     bevel=0.0006, mat="black"))
# 가늠자 (야간 조준기) + 가늠쇠
for sx in (-1, 1):
    b.p("slide", us.boxr(f"rsight{sx}", min(sx * 0.0024, sx * 0.0098), max(sx * 0.0024, sx * 0.0098),
                         SY0 + 0.002, SY0 + 0.011, ST - 0.001, ST + 0.0068, bevel=0.0008, mat="black"))
    b.pf("slide", us.ycyl(f"rdot{sx}", 0.0014, SY0 + 0.0018, SY0 + 0.0021, x=sx * 0.0061, z=ST + 0.0035, verts=10,
                          mat="paper"))
b.p("slide", us.boxr("rsight_base", -0.0098, 0.0098, SY0 + 0.002, SY0 + 0.011, ST - 0.001, ST + 0.0025,
                     bevel=0.0006, mat="black"))
b.p("slide", us.boxr("fsight", -0.0018, 0.0018, SY1 - 0.011, SY1 - 0.004, ST - 0.001, ST + 0.0068,
                     bevel=0.0006, mat="black"))
b.pf("slide", us.ycyl("fdot", 0.0012, SY1 - 0.0113, SY1 - 0.011, z=ST + 0.0040, verts=10, mat="paper"))
# 광학장비 덮개판 + 나사
b.p("slide", us.boxr("optic_plate", -0.0080, 0.0080, SY0 + 0.014, SY0 + 0.052, ST - 0.0004, ST + 0.0012,
                     bevel=0.0005, mat="black"))
for y in (SY0 + 0.019, SY0 + 0.047):
    b.pf("slide", us.zcyl(f"plate_screw{y}", 0.0016, ST + 0.0012, ST + 0.0016, y=y, verts=8, mat="bright"))
# 각인 (왼쪽)
b.pf("slide", us.text("sl_m17", "M17", 0.0090, (-0.0128, 0.088, ZB + 0.0035), mat="bright", **L_))
b.pf("slide", us.text("sl_cal", "U.S. CAL 9 MM", 0.0042, (-0.0128, 0.058, ZB + 0.0040), mat="bright", **L_))
# 모나티엄 페인트 점 (슬라이드 뒤 왼쪽 위)
b.pf("slide", us.text("sl_paint", "07", 0.006, (-0.0128, SY0 + 0.033, ZB + 0.0045), mat="paint", **L_))
b.pivot("slide", (0, 0.06, ZB), move="0,0,0.030")

# ================================================================== barrel (정지)
b.s(us.ytube("barrel_crown", 0.0068, 0.0046, SY1 - 0.012, SY1 + 0.0004, z=ZB, verts=16, mat="steel"))
b.s(us.ycyl("bore_dark", 0.0047, SY1 - 0.010, SY1 - 0.009, z=ZB, verts=12, mat="black"))
b.s(us.boxr("barrel_hood", -0.0068, 0.0072, 0.031, 0.071, ZB + 0.000, ZB + 0.0175, bevel=0.0008, mat="steel"))
b.s(us.ycyl("barrel_body", 0.0068, 0.071, SY1 - 0.012, z=ZB, verts=12, mat="steel"))

# ================================================================== frame (코요테)
FB = ZB - 0.028   # 프레임 아래면 (방아쇠울 위)
frame = us.side("frame", [(-0.034, SB + 0.0005), (0.150, SB + 0.0005), (0.150, ZB - 0.020), (0.144, FB),
                          (0.098, FB), (0.034, FB), (-0.030, FB + 0.004), (-0.034, FB + 0.010)],
                0.0235, bevel=0.0018, seg=1, mat="coyote")
b.s(frame)
b.s(us.rail("acc_rail", 0.108, 0.144, origin=(0, FB), up="-z", mat="coyote"))
# 방아쇠울 (P320식 각진 앞)
tg = us.strip([(0.035, FB + 0.002), (0.036, FB - 0.014), (0.043, FB - 0.023), (0.090, FB - 0.024),
               (0.097, FB - 0.019), (0.098, FB - 0.006), (0.100, FB + 0.002)], 0.0058)
b.s(us.side("trigger_guard", tg, 0.0125, bevel=0.0018, seg=1, mat="coyote"))
# 손잡이
gpts = [(0.0230, 0.052), (0.0240, 0.012), (0.0232, -0.030), (0.0190, -0.047), (-0.0200, -0.047),
        (-0.0245, -0.040), (-0.0245, 0.020), (-0.0225, 0.046), (-0.012, 0.056)]
grip = us.side("grip", [gp(t, s) for (t, s) in gpts], 0.030, bevel=0.0085, seg=2, mat="coyote")
b.s(grip)
# 비버테일
b.s(us.side("beavertail", [(-0.012, ZB - 0.032), (0.006, SB + 0.0005), (-0.034, SB + 0.0005),
                           (-0.038, SB - 0.003), (-0.030, ZB - 0.024), (-0.018, ZB - 0.034)],
            0.024, bevel=0.003, seg=1, mat="coyote"))
# 손잡이 미끄럼 방지 리브 (양쪽)
for sx in (-1, 1):
    for i in range(5):
        s = -0.034 + i * 0.012
        y0, z0 = gp(-0.017, s)
        y1, z1 = gp(0.016, s)
        o = us.box(f"grip_rib{sx}{i}", (0.0014, math.hypot(y1 - y0, z1 - z0), 0.0030),
                   (sx * 0.0152, (y0 + y1) / 2, (z0 + z1) / 2), mat="coyote")
        o.rotation_euler = (-GA, 0, 0)
        b.s(o)
# 손 테이프 (OD, 손잡이 아래쪽 감기)
tp = [(0, *gp(0.0, s)) for s in (-0.036, -0.022)]
b.s(us.sweep("grip_tape", tp, us.rrect(0.0322, 0.0505, 0.010, n=2), side_vec=(1, 0, 0), mat="od", smooth=50))
# 랜야드 고리 + 창고 태그 (손잡이 바닥 뒤)
ly, lz = gp(-0.022, -0.050)
b.s(us.torus("lanyard_loop", 0.0040, 0.0011, loc=(0, ly, lz), rot=(0, 90, 0), seg=10, rseg=5, mat="black"))
hole = (0.0, ly - 0.004, lz - 0.020)
b.s(us.sweep("tag_cord", [(0, ly - 0.0005, lz - 0.0045), (0.0003, ly - 0.002, lz - 0.012), hole],
             us.circle_pts(0.0006, 6), mat="paint"))
TAG_W, TAG_H = 0.018, 0.028
tc = (0.0, hole[1], hole[2] - TAG_H / 2 + 0.003)
tag_pts = [(-TAG_W / 2, -TAG_H / 2), (TAG_W / 2, -TAG_H / 2), (TAG_W / 2, TAG_H / 2 - 0.005),
           (TAG_W / 2 - 0.005, TAG_H / 2), (-TAG_W / 2 + 0.005, TAG_H / 2), (-TAG_W / 2, TAG_H / 2 - 0.005)]
tag = us.side("tag", [(tc[1] + u, tc[2] + v) for (u, v) in tag_pts], 0.0008, mat="paper")
b.s(tag)
tag_fine = [us.xcyl("tag_eyelet", 0.0021, -0.0005, 0.0005, y=hole[1], z=hole[2] - 0.0004, verts=10, mat="paint")]
for sx, kw in ((-1, L_), (1, R_)):
    xx = sx * 0.00042
    tag_fine.append(us.boxr(f"tag_band{sx}", min(xx, xx + sx * 0.0002), max(xx, xx + sx * 0.0002),
                            tc[1] - TAG_W / 2, tc[1] + TAG_W / 2, tc[2] - 0.004, tc[2] + 0.0005, mat="paint"))
    tag_fine.append(us.text(f"tag_t{sx}", "MNT", 0.0065, (xx, tc[1], tc[2] + 0.0055), mat="black", **kw))
    tag_fine.append(us.text(f"tag_n{sx}", "P-0031", 0.0034, (xx + sx * 0.0002, tc[1], tc[2] - 0.0018),
                            mat="paper", **kw))
for o in [tag, b.static[-2]] + tag_fine:
    us.xform(o, rot=(0, 0, 30), pivot=hole)
b.f(*tag_fine)

# 조작부 (검정)
b.s(us.side("slide_catch", [(0.018, ZB - 0.0185), (0.074, ZB - 0.0185), (0.076, ZB - 0.0150), (0.030, ZB - 0.0135),
                            (0.023, ZB - 0.0085), (0.017, ZB - 0.0110)], 0.0024, x=-0.0128, bevel=0.0007,
            mat="black"))
b.s(us.xcyl("takedown_hub", 0.0034, -0.0145, -0.0115, y=0.090, z=ZB - 0.0195, verts=12, mat="black"))
b.s(us.side("takedown_lever", [(0.090, ZB - 0.0225), (0.103, ZB - 0.0210), (0.103, ZB - 0.0175),
                               (0.090, ZB - 0.0165)], 0.002, x=-0.0135, bevel=0.0005, mat="black"))
b.s(us.boxr("mag_release", -0.0168, -0.0140, 0.025, 0.035, ZB - 0.040, ZB - 0.031, bevel=0.0012, mat="black"))
# 세부 (아웃라인 없음): 핀, 일련번호판, 스티커
for (y, z) in ((0.046, ZB - 0.021), (0.010, ZB - 0.020)):
    b.f(us.xcyl(f"pin{y}", 0.0016, -0.0119, 0.0119, y=y, z=z, verts=8, mat="bright"))
b.f(us.boxr("serial_plate", 0.0118, 0.0121, 0.058, 0.084, FB + 0.003, FB + 0.0095, mat="steel"))
b.f(us.text("serial", "M17 0412", 0.0040, (0.0122, 0.071, FB + 0.0062), mat="black", **R_))
sx_ = -0.0119
b.f(us.boxr("sticker", sx_ - 0.0002, sx_, 0.106, 0.146, FB + 0.0025, SB - 0.0015, mat="paper"))
b.f(us.boxr("sticker_band", sx_ - 0.0004, sx_ - 0.0002, 0.138, 0.146, FB + 0.0025, SB - 0.0015, mat="paint"))
b.f(us.text("st_t", "MNT P-0031", 0.0042, (sx_ - 0.0003, 0.121, FB + 0.0118), mat="black", **L_))
b.f(us.text("st_kr", "진압반", 0.0036, (sx_ - 0.0003, 0.121, FB + 0.0058), mat="black", font="kr", **L_))

# ================================================================== moving parts
# 방아쇠
trig = [(0.049, ZB - 0.022), (0.057, ZB - 0.022), (0.058, ZB - 0.034), (0.060, ZB - 0.044), (0.057, ZB - 0.050),
        (0.0525, ZB - 0.048), (0.0515, ZB - 0.038), (0.050, ZB - 0.030)]
b.p("trigger", us.side("trigger_blade", trig, 0.0062, bevel=0.0014, seg=1, mat="black"))
b.pivot("trigger", (0, 0.053, ZB - 0.021), rotAxis="x", rotDeg=-14)

# 수동 안전장치 (양쪽, 비버테일 위 앞)
SAF = (0, -0.006, ZB - 0.0205)
for sx in (-1, 1):
    b.p("safety", us.side(f"saf_lever{sx}", [(SAF[1] - 0.006, SAF[2] - 0.0025), (SAF[1] + 0.008, SAF[2] - 0.0035),
                                            (SAF[1] + 0.011, SAF[2] - 0.0005), (SAF[1] + 0.008, SAF[2] + 0.0028),
                                            (SAF[1] - 0.006, SAF[2] + 0.0028)],
                          0.0026, x=sx * 0.0133, bevel=0.0008, mat="black"))
b.pivot("safety", SAF, rotAxis="x", rotDeg=-25, note="up=SAFE, down=FIRE")

# 탄창 (17발, 바닥판 검정 + 모나티엄 페인트 줄)
mc = gp(0.001, -0.004)
b.p("mag", us.box("mag_body", (0.0215, 0.033, 0.098), (0, mc[0], mc[1]), rot=(-18, 0, 0), bevel=0.003,
                  mat="steel"))
bc = gp(-0.0005, -0.0515)
b.p("mag", us.box("mag_base", (0.0312, 0.050, 0.0075), (0, bc[0], bc[1]), rot=(-18, 0, 0), bevel=0.0025,
                  mat="black"))
pc = gp(-0.0005, -0.0556)
b.p("mag", us.box("mag_base_paint", (0.0262, 0.040, 0.0012), (0, pc[0], pc[1]), rot=(-18, 0, 0), mat="paint"))
tc2 = gp(0.004, 0.047)
b.p("mag", us.ycyl("mag_round", 0.0048, tc2[0] - 0.012, tc2[0] + 0.006, z=tc2[1] + 0.004, verts=10, mat="coyote"))
b.pivot("mag", (0, *gp(0.0, -0.047)), move="0,-0.15,0")

# ================================================================== anchors
b.anchor("muzzle", (0, SY1 + 0.0005, ZB))
b.anchor("grip_support", (-0.020, 0.004, -0.004))
b.anchor("sight_eye", (0, -0.22, ST + 0.0068))  # 가늠쇠 윗면 = 가늠자 윗면 높이
b.anchor("eject", (0.016, 0.051, ZB + 0.016))
b.anchor("mag_well", (0, *gp(0.0, -0.047)))

b.finish("weapons/us/m17.glb", outline=0.0018, fp="0.1,-0.13,-0.26")
