"""M249 분대지원화기 (노획 미군 화기, 제압 사격).

npm run model -- art/blender/weapons/us/m249.py
npm run shot -- weapons/us/m249.glb --views side,34,top,muzzle

원점 = 권총 손잡이 중앙, 총구 +Y. 실측 기준(전장 ≈1.04 m, 총열 0.48 m).
움직이는 파츠: cover(급탄 덮개, 앞 경첩), bipod_L/R(접힌 양각대, 앞으로 접힘 → -90° 회전으로 전개),
mag(200발 천 탄통), belt(탄띠), charging_handle(오른쪽), trigger.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402

cb.reset()
b = us.Build("m249")

ZB = 0.100
GA = math.radians(22)
RW = 0.026            # 리시버 반폭
RB, RT = ZB - 0.050, ZB + 0.030   # 리시버 아래/위
RY0, RY1 = -0.115, 0.205
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))


def gp(t, s):
    return (t * math.cos(GA) + s * math.sin(GA), -t * math.sin(GA) + s * math.cos(GA))


# ================================================================== receiver (프레스 강판 상자)
rec_sec = [(-RW, RB), (RW, RB), (RW, RT - 0.004), (RW - 0.004, RT), (-RW + 0.004, RT), (-RW, RT - 0.004)]
rec = us.section("receiver", rec_sec, RY0, RY1, bevel=0.002, seg=1, mat="black")
# 링크 배출구 (오른쪽), 탄띠 입구 (왼쪽 위)
us.cut(rec, cb.join([us.boxr("link_cut", RW - 0.004, RW + 0.01, 0.120, 0.165, ZB - 0.004, ZB + 0.016),
                     us.boxr("feed_cut", -RW - 0.01, -RW + 0.006, 0.105, 0.180, ZB + 0.002, RT + 0.001)],
                    "rec_cut"))
b.s(rec)
b.s(us.boxr("feed_cut_back", -RW + 0.005, -RW + 0.0062, 0.105, 0.180, ZB + 0.002, RT, mat="steel"))
b.s(us.boxr("link_cut_back", RW - 0.0052, RW - 0.004, 0.120, 0.165, ZB - 0.004, ZB + 0.016, mat="black"))
# 리시버 옆 보강 리브 (양쪽 가로 줄)
for sx in (-1, 1):
    b.s(us.boxr(f"rec_rib{sx}", min(sx * RW, sx * (RW + 0.0022)), max(sx * RW, sx * (RW + 0.0022)), RY0 + 0.010,
                0.100, ZB - 0.016, ZB - 0.010, bevel=0.0008, mat="black"))
# 급탄판 (덮개를 열면 보임)
b.s(us.boxr("feed_tray", -RW + 0.003, RW - 0.003, 0.100, 0.190, RT - 0.001, RT + 0.002, bevel=0.0008, mat="steel"))
# 탄창 삽입구 (왼쪽 아래, STANAG) + 먼지 덮개
b.s(us.boxr("magwell_side", -RW - 0.014, -RW + 0.002, 0.112, 0.178, RB - 0.004, ZB - 0.008, bevel=0.0025,
            mat="black"))
b.s(us.boxr("magwell_flap", -RW - 0.0158, -RW - 0.0138, 0.116, 0.174, RB, ZB - 0.012, bevel=0.0008, mat="steel"))
# 뒤 가늠자 (리시버 위 뒤)
b.s(us.boxr("rs_base", -0.012, 0.012, -0.075, -0.040, RT - 0.001, RT + 0.010, bevel=0.002, mat="black"))
# 핍 가늠자 (구멍 중심 RS_Z, 가늠쇠 끝 ZB+0.071과 sight_eye가 한 직선)
RS_Y, RS_Z, AP = -0.0585, ZB + 0.058, 0.0045
for sx in (-1, 1):
    b.s(us.boxr(f"rs_leaf{sx}", min(sx * AP, sx * 0.0085), max(sx * AP, sx * 0.0085), RS_Y - 0.002, RS_Y + 0.002,
                RT + 0.008, RS_Z + 0.009, bevel=0.0008, mat="black"))
b.s(us.boxr("rs_leaf_lo", -AP, AP, RS_Y - 0.002, RS_Y + 0.002, RT + 0.008, RS_Z - AP, bevel=0.0006, mat="black"))
b.s(us.boxr("rs_leaf_hi", -AP, AP, RS_Y - 0.002, RS_Y + 0.002, RS_Z + AP, RS_Z + 0.009, bevel=0.0006, mat="black"))
b.s(us.xcyl("rs_knob", 0.0055, 0.012, 0.018, y=-0.050, z=RT + 0.005, verts=12, mat="black"))
# 리벳 (양쪽)
for sx in (-1, 1):
    for (y, z) in ((-0.100, ZB - 0.030), (-0.060, ZB - 0.030), (-0.020, ZB - 0.030), (0.020, ZB - 0.030),
                   (0.060, ZB - 0.030), (-0.100, ZB + 0.012), (0.185, ZB - 0.030), (0.185, ZB + 0.012),
                   (0.100, ZB - 0.040)):
        if sx < 0 and 0.105 < y < 0.182:
            continue
        b.f(us.xcyl(f"rivet{sx}{y}{z}", 0.0022, sx * RW, sx * (RW + 0.0008), y=y, z=z, verts=8, mat="steel"))
# 각인 (왼쪽 뒤)
b.f(us.text("mk_rec", "MG M249  5.56 MM", 0.0070, (-RW - 0.0002, -0.050, ZB + 0.010), mat="bright", **L_))
b.f(us.text("mk_us", "U.S.", 0.0090, (-RW - 0.0002, 0.050, ZB + 0.012), mat="bright", **L_))

# ================================================================== grip / trigger guard
g = [(0.017, 0.064), (0.018, 0.036), (0.024, 0.016), (0.023, 0.006), (0.017, -0.004), (0.019, -0.030),
     (0.016, -0.050), (0.010, -0.058), (-0.014, -0.060), (-0.021, -0.052), (-0.023, -0.020),
     (-0.022, 0.030), (-0.026, 0.052), (-0.030, 0.060), (-0.026, 0.066)]
b.s(us.side("grip", [gp(t, s) for (t, s) in g], 0.028, bevel=0.0085, seg=2, mat="black"))
b.s(us.boxr("trigger_housing", -0.017, 0.017, -0.030, 0.105, RB - 0.010, RB + 0.002, bevel=0.003, mat="black"))
tg = us.strip([(0.030, RB - 0.008), (0.031, RB - 0.030), (0.042, RB - 0.040), (0.094, RB - 0.040),
               (0.104, RB - 0.030), (0.104, RB - 0.008)], 0.006)
b.s(us.side("trigger_guard", tg, 0.022, bevel=0.002, seg=1, mat="black"))

# ================================================================== stock (고정식 폴리머)
st = [(RY0 + 0.004, RT - 0.004), (-0.200, RT - 0.010), (-0.352, RT - 0.016), (-0.362, RT - 0.020),
      (-0.362, ZB - 0.098), (-0.352, ZB - 0.106), (-0.335, ZB - 0.104), (-0.200, ZB - 0.064), (-0.130, ZB - 0.046),
      (RY0 + 0.004, RB + 0.004)]
b.s(us.side("stock", st, 0.040, bevel=0.009, seg=2, mat="black"))
for sx in (-1, 1):
    for i, (z0, z1) in enumerate(((ZB - 0.010, ZB - 0.004), (ZB - 0.034, ZB - 0.028))):
        b.s(us.side(f"stock_rib{sx}{i}", [(-0.140, z0), (-0.330, z0 - 0.010), (-0.330, z1 - 0.010), (-0.140, z1)],
                    0.003, x=sx * 0.0195, bevel=0.0008, mat="black"))
b.s(us.side("butt_pad", [(-0.375, RT - 0.018), (-0.360, RT - 0.018), (-0.360, ZB - 0.106), (-0.375, ZB - 0.106),
                         (-0.379, ZB - 0.090), (-0.379, RT - 0.030)], 0.043, bevel=0.005, seg=2, mat="steel"))
# 모나티엄 페인트 띠 (개머리)
b.s(us.side("stock_paint", [(-0.300, RT - 0.011), (-0.285, RT - 0.011), (-0.285, ZB - 0.083), (-0.300, ZB - 0.089)],
            0.0415, mat="paint"))
b.f(us.text("stock_no", "MNT-M03", 0.0110, (-0.0212, -0.230, ZB - 0.050), mat="paint", **L_))

# ================================================================== barrel group
BR = 0.0112
MUZ = 0.672
b.s(us.ycyl("trunnion", 0.020, RY1 - 0.004, RY1 + 0.020, z=ZB, verts=16, bevel=0.002, seg=1, mat="black"))
b.s(us.ycyl("barrel", BR, RY1 + 0.020, 0.612, z=ZB, verts=16, mat="steel"))
for i in range(4):   # 총열 냉각 홈 (링)
    y = 0.46 + i * 0.022
    b.s(us.ycyl(f"barrel_fin{i}", BR + 0.0012, y, y + 0.008, z=ZB, verts=16, mat="steel"))
# 열 차단판 (총열 위 반원 + 구멍 줄)
hs = [(math.cos(math.radians(a)) * 0.0175, ZB + math.sin(math.radians(a)) * 0.0175) for a in range(15, 166, 15)]
hs += [(math.cos(math.radians(a)) * 0.0155, ZB + math.sin(math.radians(a)) * 0.0155) for a in range(165, 14, -15)]
b.s(us.section("heat_shield", hs, RY1 + 0.020, 0.420, bevel=0.0008, seg=1, mat="black"))
for i in range(8):
    y = RY1 + 0.040 + i * 0.024
    b.f(us.boxr(f"hs_vent{i}", -0.0045, 0.0045, y, y + 0.012, ZB + 0.0174, ZB + 0.0177, mat="steel"))
# 가스관 + 가스 조절기
b.s(us.ycyl("gas_tube", 0.0092, RY1 + 0.015, 0.440, z=ZB - 0.025, verts=14, mat="black"))
b.s(us.boxr("gas_block", -0.0135, 0.0135, 0.420, 0.452, ZB - 0.038, ZB + 0.012, bevel=0.003, mat="black"))
b.s(us.xcyl("gas_regulator", 0.0085, -0.017, 0.017, y=0.444, z=ZB - 0.030, verts=12, bevel=0.0012, seg=1,
            mat="steel"))
# 양각대 요크 (가스관 위)
b.s(us.boxr("bipod_yoke", -0.016, 0.016, 0.395, 0.420, ZB - 0.040, ZB - 0.014, bevel=0.003, mat="black"))
# 가늠쇠
b.s(us.side("fs_base", [(0.590, ZB + 0.008), (0.612, ZB + 0.008), (0.612, ZB + 0.030), (0.600, ZB + 0.030)],
            0.014, bevel=0.002, seg=1, mat="black"))
b.s(us.ycyl("fs_ring", BR + 0.003, 0.592, 0.612, z=ZB, verts=16, bevel=0.0012, seg=1, mat="black"))
b.s(us.boxr("fs_post", -0.0018, 0.0018, 0.603, 0.607, ZB + 0.029, ZB + 0.071, bevel=0.0005, mat="black"))
for sx in (-1, 1):
    b.s(us.side(f"fs_ear{sx}", [(0.598, ZB + 0.026), (0.611, ZB + 0.026), (0.610, ZB + 0.070), (0.602, ZB + 0.066)],
                0.003, x=sx * 0.0085, bevel=0.0008, mat="black"))
# 소염기
fh = us.ytube("flash_hider", 0.0128, 0.0075, 0.612, MUZ, z=ZB, verts=14, mat="steel")
sl = None
for i, a in enumerate((90, 30, 150, -30, 210)):
    ar = math.radians(a)
    c = us.box(f"fh_slot{i}", (0.004, 0.036, 0.014), (0.0128 * math.cos(ar), 0.642, ZB + 0.0128 * math.sin(ar)),
               rot=(0, 90 - a, 0))
    sl = c if sl is None else cb.join([sl, c], "fh_cut")
us.cut(fh, sl)
b.s(fh)

# 운반 손잡이 (오른쪽으로 눕힘) + 창고 태그
HB = (0, 0.318, ZB)
b.s(us.ycyl("handle_clamp", BR + 0.0045, 0.300, 0.336, z=ZB, verts=16, bevel=0.002, seg=1, mat="black"))
hp = []
for i in range(9):
    t = i / 8
    yy = 0.300 + 0.150 * t
    hh = 0.060 * math.sin(math.pi * min(1.0, t * 1.15)) if t < 0.87 else 0.060 * math.sin(math.pi * 0.87 * 1.15) * (1 - t) / 0.13
    hp.append((0, yy, ZB + 0.012 + hh))
handle = us.sweep("carry_handle", hp, us.rrect(0.014, 0.022, 0.006, n=2), side_vec=(1, 0, 0), mat="black", smooth=50)
us.xform(handle, rot=(0, 62, 0), pivot=(0, 0.318, ZB))
b.s(handle)
tag_top = (0.050, 0.385, ZB + 0.020)
hole = (0.052, 0.386, ZB - 0.004)
b.s(us.sweep("tag_cord", [tag_top, (0.053, 0.3855, ZB + 0.008), hole], us.circle_pts(0.0007, 6), mat="paint"))
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
    tag_fine.append(us.text(f"tag_t2{sx}", "M-0003", 0.0042, (xx + sx * 0.0002, tcx[1], tcx[2] - 0.001),
                            mat="paper", **kw))
    tag_fine.append(us.text(f"tag_kr{sx}", "분대 화기", 0.0040, (xx, tcx[1], tcx[2] - 0.0095), mat="black", font="kr",
                            **kw))
for o in [tag, b.static[-2]] + tag_fine:
    us.xform(o, rot=(0, 0, -30), pivot=hole)
b.f(*tag_fine)

# ================================================================== moving parts
# 급탄 덮개 (앞 경첩, 레일 + 잠금 손잡이)
CV0, CV1 = 0.020, 0.198
cov_sec = [(-RW + 0.001, RT), (RW - 0.001, RT), (RW - 0.001, RT + 0.010), (RW - 0.008, RT + 0.018),
           (-RW + 0.008, RT + 0.018), (-RW + 0.001, RT + 0.010)]
b.p("cover", us.section("cover_body", cov_sec, CV0, CV1, bevel=0.0018, seg=1, mat="black"))
b.p("cover", us.rail("cover_rail", CV0 + 0.012, CV1 - 0.010, origin=(0, RT + 0.018), up="+z"))
b.p("cover", us.boxr("cover_latch", -0.018, 0.018, CV0 - 0.010, CV0 + 0.004, RT + 0.002, RT + 0.014, bevel=0.003,
                     mat="black"))
for sx in (-1, 1):
    b.pf("cover", us.xcyl(f"cover_rivet{sx}", 0.0022, sx * (RW - 0.001), sx * (RW - 0.0002), y=CV1 - 0.010,
                          z=RT + 0.006, verts=8, mat="steel"))
b.pivot("cover", (0, CV1, RT + 0.004), rotAxis="x", rotDeg=-70)

# 장전손잡이 (오른쪽 앞)
CH = (RW, 0.150, ZB - 0.014)
b.p("charging_handle", us.xcyl("ch_stem", 0.0040, RW - 0.002, RW + 0.020, y=CH[1], z=CH[2], verts=10, mat="steel"))
b.p("charging_handle", us.boxr("ch_knob", RW + 0.014, RW + 0.026, CH[1] - 0.010, CH[1] + 0.010, CH[2] - 0.009,
                               CH[2] + 0.009, bevel=0.004, seg=2, mat="black"))
b.pivot("charging_handle", CH, move="0,0,0.150")

# 방아쇠
trig = [(0.050, RB - 0.006), (0.058, RB - 0.006), (0.059, RB - 0.016), (0.062, RB - 0.026), (0.059, RB - 0.030),
        (0.054, RB - 0.026), (0.052, RB - 0.018)]
b.p("trigger", us.side("trigger_blade", trig, 0.007, bevel=0.0015, seg=1, mat="steel"))
b.pivot("trigger", (0, 0.055, RB - 0.004), rotAxis="x", rotDeg=-12)

# 양각대 다리 (앞으로 접힘)
YK = (0.407, ZB - 0.034)
for side, sx in (("L", -1), ("R", 1)):
    nm = f"bipod_{side}"
    x0 = sx * 0.011
    leg = us.ycyl(f"{nm}_tube", 0.0058, YK[0], YK[0] + 0.205, x=x0, z=YK[1] - 0.004, verts=10, mat="black")
    ext = us.ycyl(f"{nm}_ext", 0.0046, YK[0] + 0.205, YK[0] + 0.255, x=x0, z=YK[1] - 0.004, verts=10, mat="steel")
    foot = us.boxr(f"{nm}_foot", x0 - 0.007, x0 + 0.007, YK[0] + 0.250, YK[0] + 0.264, YK[1] - 0.014,
                   YK[1] + 0.004, bevel=0.003, mat="black")
    hinge = us.xcyl(f"{nm}_hinge", 0.0075, x0 - 0.006, x0 + 0.006, y=YK[0], z=YK[1], verts=12, mat="black")
    for o in (leg, ext, foot):
        us.xform(o, rot=(0, 0, -sx * 2.0), pivot=(x0, YK[0], YK[1]))
    b.p(nm, leg, ext, foot, hinge)
    b.pivot(nm, (x0, YK[0], YK[1]), rotAxis="x", rotDeg=-95, splayDegZ=sx * 12)

# 200발 천 탄통 (OD) + 탄띠
PX0, PX1 = -0.064, 0.010
PY0, PY1 = 0.100, 0.214
PZ0, PZ1 = ZB - 0.172, RB - 0.004
b.p("mag", us.boxr("pouch", PX0, PX1, PY0, PY1, PZ0, PZ1, bevel=0.012, seg=2, mat="od"))
b.p("mag", us.boxr("pouch_flap", PX0 - 0.0015, PX1 + 0.0015, PY0 - 0.0015, PY1 + 0.0015, PZ1 - 0.026, PZ1 - 0.002,
                   bevel=0.008, seg=2, mat="od"))
for i in range(3):   # MOLLE 띠 (왼쪽 면)
    z = PZ0 + 0.020 + i * 0.026
    b.p("mag", us.boxr(f"molle{i}", PX0 - 0.0022, PX0 + 0.004, PY0 + 0.010, PY1 - 0.010, z, z + 0.010, bevel=0.0012,
                       mat="od"))
b.p("mag", us.boxr("pouch_clip", -RW - 0.012, -RW + 0.002, 0.118, 0.172, PZ1 - 0.004, RB + 0.002, bevel=0.002,
                   mat="black"))
b.pf("mag", us.boxr("pouch_label", PX0 - 0.0026, PX0 - 0.0022, PY0 + 0.026, PY1 - 0.026, PZ0 + 0.072, PZ0 + 0.088,
                    mat="paper"))
b.pf("mag", us.text("pouch_t", "MNT  200 RDS", 0.0090, (PX0 - 0.0027, (PY0 + PY1) / 2, PZ0 + 0.080), mat="black",
                    **L_))
b.pivot("mag", (0, (PY0 + PY1) / 2, RB), move="0,-0.2,0")

# 탄띠: 탄통 위에서 왼쪽 급탄구로 (탄은 총구 방향, 링크는 검정)
bp = [(-0.046, PZ1 - 0.002), (-0.050, ZB - 0.034), (-0.047, ZB - 0.016), (-0.040, ZB - 0.002), (-0.032, ZB + 0.008),
      (-RW + 0.003, ZB + 0.013)]
seg_len = [math.dist(bp[i], bp[i + 1]) for i in range(len(bp) - 1)]
total = sum(seg_len)
PITCH = 0.0100
CY0 = 0.112
n = int(total / PITCH) + 1
for k in range(n):
    d = k * PITCH
    i = 0
    while i < len(seg_len) - 1 and d > seg_len[i]:
        d -= seg_len[i]
        i += 1
    t = min(1.0, d / seg_len[i])
    x = bp[i][0] + (bp[i + 1][0] - bp[i][0]) * t
    z = bp[i][1] + (bp[i + 1][1] - bp[i][1]) * t
    b.p("belt", us.ycyl(f"case{k}", 0.0048, CY0, CY0 + 0.045, x=x, z=z, verts=8, r2=0.0046, mat="brass"))
    b.p("belt", us.ycyl(f"bullet{k}", 0.0029, CY0 + 0.045, CY0 + 0.061, x=x, z=z, verts=8, r2=0.0008, mat="brass"))
    b.p("belt", us.ycyl(f"link{k}", 0.0055, CY0 + 0.006, CY0 + 0.014, x=x, z=z, verts=8, mat="black"))
    b.p("belt", us.ycyl(f"link2{k}", 0.0055, CY0 + 0.028, CY0 + 0.034, x=x, z=z, verts=8, mat="black"))
b.pivot("belt", (bp[-1][0], CY0, bp[-1][1]), feedDir="1,0,0", pitch=PITCH)

# ================================================================== anchors
b.anchor("muzzle", (0, MUZ, ZB))
b.anchor("grip_support", (0, 0.455, ZB - 0.040))  # 접힌 양각대 다리를 쥔다
b.anchor("sight_eye", (0, -0.190, RS_Z - (ZB + 0.071 - RS_Z) / (0.605 - RS_Y) * (RS_Y + 0.190)))
b.anchor("eject", (0, 0.060, RB - 0.012))
b.anchor("eject_link", (RW + 0.004, 0.142, ZB + 0.006))
b.anchor("mag_well", (-0.027, 0.157, ZB + 0.012))
b.anchor("bipod_feet", (0, 0.407, ZB - 0.290))

b.finish("weapons/us/m249.glb", outline=0.002, fp="0.14,-0.21,-0.32")
