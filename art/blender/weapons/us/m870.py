"""M870 펌프액션 산탄총 (노획 미군 화기, 근접·돌파).

npm run model -- art/blender/weapons/us/m870.py
npm run shot -- weapons/us/m870.glb --views side,34,top,muzzle

원점 = 개머리판 손목(오른손 파지점) 중앙, 총구 +Y. 실측 기준(18.5" 총열, 7발 연장 튜브, 고스트링 조준기).
펌프(pump)는 별도 파츠라 0.09 m 후퇴 애니메이션이 가능하고, 왼손 앵커(grip_support)가 펌프를 따라간다.
왼쪽 사이드새들에 12게이지 6발.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m870")

# 리시버 좌표 (y=리시버 뒤끝, z=총열 축) → 원점(손목 중앙) 기준으로 옮김
DY, DZ = 0.045, 0.052


def P(pts):
    return [(y + DY, z + DZ) for (y, z) in pts]


def X(pts):
    return [(x, z + DZ) for (x, z) in pts]


def Y(y):
    return y + DY


def Z(z):
    return z + DZ


L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))
RW = 0.0165   # 리시버 반폭
TUBE_Z = -0.031
PUMP_TRAVEL = 0.09

# ================================================================== receiver
rec_sec = [(-RW, -0.041), (RW, -0.041), (RW, 0.004), (0.0145, 0.0115), (0.009, 0.0168), (-0.009, 0.0168),
           (-0.0145, 0.0115), (-RW, 0.004)]
rec = us.section("receiver", X(rec_sec), Y(0.006), Y(0.195), bevel=0.0015, seg=1, mat="black")
us.cut(rec, us.boxr("port_cut", 0.010, 0.03, Y(0.078), Y(0.150), Z(-0.015), Z(0.009)))
b.s(rec)
b.s(us.boxr("port_back", 0.0090, 0.0102, Y(0.078), Y(0.150), Z(-0.015), Z(0.009), mat="black"))
# 리시버 뒤 탱 (개머리판으로 이어짐)
b.s(us.side("rec_tang", P([(0.010, -0.041), (0.010, 0.0165), (0.002, 0.012), (-0.006, 0.004), (-0.006, -0.041)]),
            0.031, bevel=0.003, seg=1, mat="black"))
# 총열 고리 (리시버 앞)
b.s(us.ycyl("barrel_ring", 0.0150, Y(0.192), Y(0.204), z=Z(0), verts=16, bevel=0.0012, seg=1, mat="black"))
# 방아쇠 뭉치 판 + 방아쇠울
b.s(us.boxr("trigger_plate", -0.0145, 0.0145, Y(0.006), Y(0.118), Z(-0.050), Z(-0.040), bevel=0.0015, mat="black"))
tg = us.strip(P([(0.020, -0.049), (0.020, -0.066), (0.030, -0.078), (0.082, -0.078), (0.094, -0.068),
                 (0.100, -0.049)]), 0.0055)
b.s(us.side("trigger_guard", tg, 0.013, bevel=0.0015, seg=1, mat="black"))
# 크로스볼트 안전장치 (방아쇠울 뒤 위) / 슬라이드 해제 레버 (왼쪽)
b.s(us.boxr("slide_release", -0.0175, -0.0145, Y(0.098), Y(0.116), Z(-0.054), Z(-0.047), bevel=0.0012, mat="black"))
# 고스트링 가늠자
b.s(us.boxr("gr_base", -0.0095, 0.0095, Y(0.006), Y(0.036), Z(0.0158), Z(0.0215), bevel=0.0015, mat="black"))
for sx in (-1, 1):
    b.s(us.side(f"gr_ear{sx}", P([(0.010, 0.020), (0.034, 0.020), (0.032, 0.040), (0.020, 0.043), (0.012, 0.038)]),
                0.0032, x=sx * 0.0078, bevel=0.001, mat="black"))
b.s(us.torus("gr_ring", 0.0042, 0.0013, loc=(0, Y(0.022), Z(0.032)), rot=(90, 0, 0), seg=14, rseg=5, mat="black"))
b.s(us.boxr("gr_stem", -0.0012, 0.0012, Y(0.020), Y(0.024), Z(0.0205), Z(0.028), mat="black"))

# ================================================================== barrel / tube / muzzle
BR = 0.0114
MUZ = 0.675
b.s(us.ycyl("barrel", BR, Y(0.200), Y(MUZ - 0.004), z=Z(0), verts=20, mat="steel"))
b.s(us.ytube("muzzle_crown", BR, 0.0092, Y(MUZ - 0.004), Y(MUZ), z=Z(0), verts=20, mat="steel"))
b.s(us.ycyl("bore_dark", 0.0093, Y(MUZ - 0.012), Y(MUZ - 0.011), z=Z(0), verts=12, mat="black"))
# 가늠쇠 (램프 + 블레이드)
b.s(us.side("front_ramp", P([(MUZ - 0.040, 0.009), (MUZ - 0.008, 0.009), (MUZ - 0.008, 0.016),
                             (MUZ - 0.020, 0.016)]), 0.008, bevel=0.0012, seg=1, mat="black"))
b.s(us.side("front_blade", P([(MUZ - 0.018, 0.015), (MUZ - 0.010, 0.015), (MUZ - 0.010, 0.032),
                              (MUZ - 0.014, 0.032)]), 0.0028, bevel=0.0006, seg=1, mat="black"))
b.f(us.boxr("front_dot", -0.0009, 0.0009, Y(MUZ - 0.0181), Y(MUZ - 0.0178), Z(0.0275), Z(0.0305), mat="paint"))
# 탄창 튜브 (연장형) + 마개 + 총열 클램프
TR = 0.0133
b.s(us.ycyl("mag_tube", TR, Y(0.195), Y(0.600), z=Z(TUBE_Z), verts=18, mat="steel"))
b.s(us.ycyl("tube_cap", 0.0158, Y(0.600), Y(0.628), z=Z(TUBE_Z), verts=18, bevel=0.0025, seg=1, mat="black"))
for i in range(6):
    a = math.radians(i * 60)
    b.s(us.box(f"cap_knurl{i}", (0.0035, 0.020, 0.003), (0.0158 * math.cos(a), Y(0.614), Z(TUBE_Z) + 0.0158 * math.sin(a)),
               rot=(0, -math.degrees(a) + 90, 0), mat="black"))
clamp = [(-0.0165, TUBE_Z - 0.010), (0.0165, TUBE_Z - 0.010), (0.0165, 0.004), (0.010, 0.0145), (-0.010, 0.0145),
         (-0.0165, 0.004)]
b.s(us.section("barrel_clamp", X(clamp), Y(0.556), Y(0.578), bevel=0.0025, seg=1, mat="black"))
b.s(us.xcyl("clamp_bolt", 0.0035, -0.020, 0.020, y=Y(0.567), z=Z(-0.010), verts=10, mat="black"))
# 클램프 슬링 고리 (왼쪽) + 창고 태그
SW = (-0.022, Y(0.567), Z(-0.034))
b.s(us.torus("clamp_swivel", 0.0072, 0.0015, loc=SW, rot=(0, 0, 90), seg=12, rseg=5, mat="steel"))
hole = (SW[0] - 0.001, SW[1] + 0.002, SW[2] - 0.026)
b.s(us.sweep("tag_cord", [(SW[0], SW[1], SW[2] - 0.0072), (SW[0] - 0.0012, SW[1] + 0.001, SW[2] - 0.016), hole],
             us.circle_pts(0.0007, 6), mat="paint"))
TAG_W, TAG_H = 0.024, 0.038
tcx = (hole[0], hole[1], hole[2] - TAG_H / 2 + 0.004)
tag_pts = [(-TAG_W / 2, -TAG_H / 2), (TAG_W / 2, -TAG_H / 2), (TAG_W / 2, TAG_H / 2 - 0.006),
           (TAG_W / 2 - 0.006, TAG_H / 2), (-TAG_W / 2 + 0.006, TAG_H / 2), (-TAG_W / 2, TAG_H / 2 - 0.006)]
tag = us.side("tag", [(tcx[1] + u, tcx[2] + v) for (u, v) in tag_pts], 0.0009, x=tcx[0], mat="paper")
b.s(tag)
tag_fine = [us.xcyl("tag_eyelet", 0.0026, tcx[0] - 0.0006, tcx[0] + 0.0006, y=hole[1], z=hole[2] - 0.0005, verts=12,
                    mat="paint")]
for sx, kw in ((-1, L_), (1, R_)):
    xx = tcx[0] + sx * 0.00046
    tag_fine.append(us.boxr(f"tag_band{sx}", min(xx, xx + sx * 0.0002), max(xx, xx + sx * 0.0002), tcx[1] - TAG_W / 2,
                            tcx[1] + TAG_W / 2, tcx[2] - 0.004, tcx[2] + 0.002, mat="paint"))
    tag_fine.append(us.text(f"tag_t1{sx}", "MNT", 0.0085, (xx, tcx[1], tcx[2] + 0.0075), mat="black", **kw))
    tag_fine.append(us.text(f"tag_t2{sx}", "S-0207", 0.0042, (xx + sx * 0.0002, tcx[1], tcx[2] - 0.001),
                            mat="paper", **kw))
    tag_fine.append(us.text(f"tag_kr{sx}", "돌파조", 0.0040, (xx, tcx[1], tcx[2] - 0.0095), mat="black", font="kr", **kw))
for o in [tag, b.static[-2]] + tag_fine:
    us.xform(o, rot=(0, 0, 40), pivot=hole)
b.f(*tag_fine)

# ================================================================== stock (OD 합성)
st = P([(0.006, 0.012), (-0.010, 0.006), (-0.040, -0.011), (-0.080, -0.024), (-0.200, -0.034), (-0.284, -0.044),
        (-0.290, -0.050), (-0.299, -0.168), (-0.292, -0.176), (-0.282, -0.177), (-0.180, -0.132), (-0.105, -0.101),
        (-0.072, -0.094), (-0.046, -0.090), (-0.022, -0.075), (-0.004, -0.058), (0.008, -0.050)])
b.s(us.side("stock", st, 0.036, bevel=0.0095, seg=2, mat="od"))
b.s(us.side("recoil_pad", P([(-0.284, -0.042), (-0.302, -0.044), (-0.312, -0.172), (-0.300, -0.183),
                             (-0.293, -0.178), (-0.291, -0.050)]), 0.040, bevel=0.006, seg=2, mat="black"))
# 손목 미끄럼 방지 리브 (양쪽)
for sx in (-1, 1):
    for i in range(4):
        yy = -0.030 - i * 0.011
        b.s(us.side(f"wrist_rib{sx}{i}", P([(yy, -0.034 - i * 0.004), (yy - 0.004, -0.034 - i * 0.004),
                                            (yy - 0.004 - 0.010, -0.080), (yy - 0.010, -0.080)]),
                    0.0016, x=sx * 0.0176, mat="od"))
# 개머리 슬링 고리 (아래)
b.s(us.torus("stock_swivel", 0.0065, 0.0015, loc=(0, Y(-0.240), Z(-0.166)), rot=(0, 90, 20), seg=12, rseg=5,
             mat="steel"))
# 모나티엄 스텐실 (개머리 왼쪽, 청록 페인트)
b.f(us.text("stencil_no", "MNT-07", 0.0150, (-0.0181, Y(-0.175), Z(-0.083)), mat="paint", **L_))
b.f(us.text("stencil_kr", "진압반 특수작전부", 0.0062, (-0.0181, Y(-0.175), Z(-0.100)), mat="paint", font="kr", **L_))

# ================================================================== side saddle (왼쪽, 6발)
SX = -RW - 0.0032
b.s(us.boxr("saddle_plate", SX - 0.002, SX + 0.0004, Y(0.030), Y(0.188), Z(-0.050), Z(0.012), bevel=0.0012,
            mat="black"))
SHELL_R = 0.0104
for i in range(6):
    y = Y(0.044 + i * 0.0262)
    x = SX - 0.002 - SHELL_R
    b.s(us.zcyl(f"shell_hull{i}", SHELL_R, Z(-0.035), Z(0.030), x=x, y=y, verts=12, mat="red"))
    b.s(us.zcyl(f"shell_head{i}", SHELL_R + 0.0004, Z(-0.048), Z(-0.035), x=x, y=y, verts=12, mat="brass"))
    b.s(us.zcyl(f"shell_crimp{i}", SHELL_R - 0.0012, Z(0.030), Z(0.0315), x=x, y=y, verts=12, mat="red"))
# 고무 고정 띠 (위·아래)
for (z0, z1) in ((-0.026, -0.018), (0.014, 0.022)):
    b.s(us.boxr(f"saddle_band{z0}", SX - 0.002 - 2 * SHELL_R - 0.0008, SX - 0.002, Y(0.030), Y(0.188), Z(z0), Z(z1),
                bevel=0.0012, mat="black"))
# 리시버 오른쪽 각인, 총열 왼쪽 각인, 왼쪽 스티커 (새들 앞)
b.f(us.text("mk_rec", "U.S.  M870  12 GA", 0.0060, (RW + 0.0001, Y(0.110), Z(-0.028)), mat="bright", **R_))
b.f(us.text("mk_bbl", "12 GA  3 IN  CYL", 0.0050, (-BR - 0.0001, Y(0.260), Z(0.0)), mat="bright",
            right=(0, -1, 0), up=(0, 0, 1)))
b.f(us.boxr("sticker", -RW - 0.0002, -RW, Y(0.150), Y(0.188), Z(0.013) - 0.010, Z(0.013) - 0.0005, mat="paper"))
b.f(us.text("st_t", "MNT S-0207", 0.0040, (-RW - 0.0003, Y(0.169), Z(0.008)), mat="black", **L_))
# 핀 (리시버 양쪽 방아쇠 뭉치 핀)
for y in (0.030, 0.096):
    b.f(us.xcyl(f"pin{y}", 0.0024, -RW - 0.0003, RW + 0.0003, y=Y(y), z=Z(-0.036), verts=10, mat="bright"))

# ================================================================== moving parts
# 펌프 (골 파인 합성 포엔드 + 액션 바)
PY0, PY1 = 0.250, 0.440
path, sc = [], []
n = 22
for i in range(n + 1):
    t = i / n
    y = PY0 + (PY1 - PY0) * t
    path.append((0, Y(y), Z(TUBE_Z - 0.003)))
    edge = min(t, 1 - t)
    s_end = 0.90 + 0.10 * min(1.0, edge / 0.06)
    groove = 1.0 if (i % 2 == 0 or t < 0.10 or t > 0.90) else 0.915
    sc.append((s_end * groove, s_end * (1.0 if groove == 1.0 else 0.97)))
pump_sec = us.rrect(0.050, 0.047, 0.017, n=3)
b.p("pump", us.sweep("pump_body", path, pump_sec, side_vec=(1, 0, 0), mat="od", smooth=60, scales=sc))
for sx in (-1, 1):
    b.p("pump", us.boxr(f"action_bar{sx}", sx * 0.0128 - 0.0013, sx * 0.0128 + 0.0013, Y(0.195), Y(PY0 + 0.01),
                        Z(TUBE_Z - 0.004), Z(TUBE_Z + 0.006), mat="steel"))
b.pivot("pump", (0, Y((PY0 + PY1) / 2), Z(TUBE_Z)), move=f"0,0,{PUMP_TRAVEL}")

# 노리쇠 (배출구 안, 펌프와 같이 후퇴)
b.p("bolt", us.boxr("bolt_body", 0.0040, 0.0098, Y(0.080), Y(0.148), Z(-0.013), Z(0.007), bevel=0.0012, mat="bright"))
b.p("bolt", us.boxr("bolt_ext", 0.0060, 0.0102, Y(0.136), Y(0.146), Z(-0.004), Z(0.002), mat="steel"))
b.pivot("bolt", (0, Y(0.114), Z(-0.003)), move=f"0,0,{PUMP_TRAVEL}")

# 방아쇠
trig = P([(0.044, -0.048), (0.052, -0.048), (0.053, -0.058), (0.055, -0.066), (0.052, -0.073), (0.047, -0.069),
          (0.046, -0.060), (0.045, -0.054)])
b.p("trigger", us.side("trigger_blade", trig, 0.0055, bevel=0.0012, seg=1, mat="steel"))
b.pivot("trigger", (0, Y(0.049), Z(-0.047)), rotAxis="x", rotDeg=-12)

# 크로스볼트 안전장치 (빨간 띠 = 사격 가능)
SAF_Y, SAF_Z = Y(0.012), Z(-0.054)
b.p("safety", us.xcyl("safety_bolt", 0.0035, -0.0180, 0.0170, y=SAF_Y, z=SAF_Z, verts=12, mat="black"))
b.p("safety", us.xcyl("safety_red", 0.0036, -0.0180, -0.0150, y=SAF_Y, z=SAF_Z, verts=12, mat="red"))
b.pivot("safety", (0, SAF_Y, SAF_Z), move="0.0035,0,0", note="left=FIRE (red band shows)")

# ================================================================== anchors
b.anchor("muzzle", (0, Y(MUZ), Z(0)))
b.anchor("grip_support", (0, Y((PY0 + PY1) / 2), Z(TUBE_Z - 0.003)), parent="pump")
b.anchor("sight_eye", (0, Y(-0.12), Z(0.032)))
b.anchor("eject", (0.020, Y(0.114), Z(-0.003)))
b.anchor("mag_well", (0, Y(0.120), Z(-0.050)))

b.finish("weapons/us/m870.glb", outline=0.002, fp="0.13,-0.19,-0.28")
