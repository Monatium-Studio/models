"""M240 공축 기관총 (전차 포탑 안 거치형, 노획 미군 화기).

npm run model -- art/blender/weapons/us/m240_coax.py
npm run shot -- weapons/us/m240_coax.glb --views side,34,top,34b

원점 = 앞 거치 핀 중심(공축 마운트 회전축). 총구 +Y. 개머리판·권총 손잡이가 없고 뒤쪽 아래 전기 방아쇠(솔레노이드)로
쏜다. M1A1의 mount_coax(gun_pitch 자식, 요·피치 고정)에 붙어 주포와 함께 움직인다.
실측 기준: 전장 ≈1.1 m, 총열 0.63 m. 탄띠는 왼쪽 급탄 슈트로 들어온다.
움직이는 파츠: cover(앞 경첩), bolt, charging_handle(오른쪽), belt.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import weapons_us as us  # noqa: E402
import vehicles_us as vu  # noqa: E402

cb.reset()
b = us.Build("m240_coax")

ZB = 0.050
RW = 0.036
RB, RF, RT = ZB - 0.056, ZB + 0.030, ZB + 0.050
RY0, RY1 = -0.400, 0.040
MUZ = 0.680
L_ = dict(right=(0, -1, 0), up=(0, 0, 1))
R_ = dict(right=(0, 1, 0), up=(0, 0, 1))

# ================================================================== receiver
rsec = [(-RW, RB + 0.006), (-RW + 0.006, RB), (RW - 0.006, RB), (RW, RB + 0.006), (RW, RF), (-RW, RF)]
b.s(us.section("receiver", rsec, RY0, RY1, bevel=0.0018, seg=1, mat="black"))
b.s(us.section("rear_block", [(-RW, RF - 0.002), (RW, RF - 0.002), (RW, RT - 0.008), (RW - 0.008, RT),
                              (-RW + 0.008, RT), (-RW, RT - 0.008)], RY0, -0.205, bevel=0.0018, seg=1, mat="black"))
for sx in (-1, 1):   # 옆 보강 띠 + 리벳
    x0, x1 = sorted((sx * RW, sx * (RW + 0.0022)))
    b.s(us.boxr(f"rib{sx}", x0, x1, RY0 + 0.012, RY1 - 0.010, ZB - 0.020, ZB - 0.012, bevel=0.0008, mat="black"))
    for y in (-0.36, -0.27, -0.18, -0.09, 0.0):
        b.f(us.xcyl(f"rv{sx}{y}", 0.0024, sx * RW, sx * (RW + 0.0010), y=y, z=RB + 0.016, verts=6, mat="steel"))
b.s(us.ycyl("buffer", 0.024, RY0 - 0.040, RY0 + 0.002, z=ZB - 0.004, verts=14, mat="black"))
b.s(us.ycyl("buffer_cap", 0.017, RY0 - 0.048, RY0 - 0.038, z=ZB - 0.004, verts=12, mat="steel"))
# 솔레노이드 방아쇠 상자 + 전선
b.s(us.boxr("solenoid", -0.024, 0.024, -0.330, -0.240, RB - 0.042, RB + 0.002, bevel=0.004, mat="black"))
b.s(us.sweep("sol_cable", [(0.0, -0.330, RB - 0.020), (0.0, -0.380, RB - 0.030), (0.010, -0.430, RB - 0.060),
                           (0.020, -0.470, RB - 0.110)], us.circle_pts(0.005, 6), mat="black"))
# 급탄판 (덮개를 열면 보임)
b.s(us.boxr("feed_tray", -RW + 0.004, RW - 0.004, -0.170, -0.040, RF, RF + 0.003, mat="steel"))
# 앞 트러니언 블록 + 거치 핀(원점)
b.s(us.boxr("trunnion", -RW - 0.006, RW + 0.006, -0.030, RY1 + 0.010, RB - 0.012, RF, bevel=0.003, mat="black"))
b.s(us.xcyl("mount_pin", 0.009, -RW - 0.022, RW + 0.022, y=0, z=0, verts=10, mat="bright"))
for sx in (-1, 1):
    b.s(us.xcyl(f"pin_boss{sx}", 0.016, sx * (RW + 0.006), sx * (RW + 0.014), y=0, z=0, verts=12, mat="black"))
# 뒤 거치 받침 (아래)
b.s(us.boxr("rear_mount", -0.020, 0.020, -0.345, -0.300, RB - 0.020, RB + 0.002, bevel=0.003, mat="steel"))
b.f(us.xcyl("rear_pin", 0.006, -0.026, 0.026, y=-0.3225, z=RB - 0.010, verts=8, mat="bright"))
# 각인 + 모나티엄 청록 띠
b.f(us.text("mk", "U.S.  M240C  7.62 MM", 0.0090, (-RW - 0.0012, -0.120, ZB + 0.004), mat="bright", **L_))
for sx in (-1, 1):
    x0, x1 = sorted((sx * RW, sx * (RW + 0.0012)))
    b.f(us.boxr(f"paint{sx}", x0, x1, -0.380, -0.360, RB + 0.004, RF - 0.002, mat="paint"))
b.f(us.text("mk_mnt", "MNT-C01", 0.0110, (RW + 0.0013, -0.300, ZB + 0.004), mat="paint", **R_))

# ================================================================== barrel group
b.s(us.ycyl("barrel", 0.0140, RY1, MUZ - 0.072, z=ZB, verts=14, r2=0.0128, mat="steel"))
b.s(us.ycyl("barrel_collar", 0.0200, RY1, RY1 + 0.040, z=ZB, verts=14, mat="steel"))
b.s(us.ycyl("gas_tube", 0.0085, RY1, 0.430, z=ZB - 0.026, verts=10, mat="black"))
b.s(us.boxr("gas_block", -0.014, 0.014, 0.410, 0.448, ZB - 0.040, ZB + 0.012, bevel=0.003, mat="black"))
b.s(us.xcyl("gas_reg", 0.0085, -0.018, 0.018, y=0.440, z=ZB - 0.030, verts=10, mat="steel"))
fh = us.ytube("flash_hider", 0.0170, 0.0085, MUZ - 0.074, MUZ, z=ZB, verts=12, mat="steel")
sl = None
for i, a in enumerate((90, 30, 150, -30, 210)):
    ar = math.radians(a)
    c = us.box(f"fh_slot{i}", (0.004, 0.040, 0.018), (0.017 * math.cos(ar), MUZ - 0.034, ZB + 0.017 * math.sin(ar)),
               rot=(0, 90 - a, 0))
    sl = c if sl is None else cb.join([sl, c], "fh_cut")
us.cut(fh, sl)
b.s(fh)

# ================================================================== feed chute (왼쪽, 아래로 휘어 내려감)
chute = [(-RW - 0.010, -0.100, RF - 0.006), (-RW - 0.050, -0.100, RF - 0.020), (-RW - 0.075, -0.100, RF - 0.070),
         (-RW - 0.080, -0.100, RF - 0.200)]
b.s(us.sweep("chute", vu.rounded_path(chute, 0.04, 3), us.rrect(0.030, 0.090, 0.008, n=1), side_vec=(0, 1, 0),
             mat="od", smooth=40))
b.s(us.boxr("chute_clamp", -RW - 0.016, -RW + 0.001, -0.150, -0.050, RF - 0.016, RF + 0.004, bevel=0.003,
            mat="black"))

# ================================================================== moving parts
cov = [(-RW, RT - 0.010), (RW, RT - 0.010), (RW, RT - 0.006), (RW - 0.008, RT + 0.002), (-RW + 0.008, RT + 0.002),
       (-RW, RT - 0.006)]
b.p("cover", us.section("cover_top", cov, -0.205, -0.030, bevel=0.0012, seg=1, mat="black"))
b.p("cover", us.boxr("cover_skirt_R", RW - 0.004, RW, -0.205, -0.030, RF + 0.001, RT - 0.009, mat="black"))
b.p("cover", us.boxr("cover_skirt_L", -RW, -RW + 0.004, -0.205, -0.155, RF + 0.001, RT - 0.009, mat="black"))
b.p("cover", us.boxr("cover_latch", -0.016, 0.016, -0.215, -0.198, RT - 0.006, RT + 0.006, bevel=0.002,
                     mat="steel"))
b.p("cover", us.xcyl("cover_hinge", 0.0055, -RW + 0.003, RW - 0.003, y=-0.034, z=RT - 0.006, verts=8, mat="steel"))
b.pivot("cover", (0, -0.034, RT - 0.006), rotAxis="x", rotDeg=-75)

b.p("bolt", us.boxr("bolt_body", -0.020, 0.020, -0.180, -0.050, RF - 0.020, RF + 0.002, bevel=0.0015,
                    mat="bright"))
b.pivot("bolt", (0, -0.115, RF - 0.009), move="0,0,0.15")

CHY, CHZ = -0.060, ZB - 0.006
b.p("charging_handle", us.boxr("ch_slide", RW, RW + 0.010, CHY - 0.016, CHY + 0.016, CHZ - 0.009, CHZ + 0.009,
                               bevel=0.002, mat="steel"))
b.p("charging_handle", us.boxr("ch_knob", RW + 0.008, RW + 0.034, CHY - 0.012, CHY + 0.006, CHZ - 0.012,
                               CHZ + 0.012, bevel=0.004, mat="black"))
b.pivot("charging_handle", (RW, CHY, CHZ), move="0,0,0.15")

# 탄띠 (7.62 링크, 슈트 끝에서 급탄판으로 몇 발)
BY = -0.100
for k, (x, z) in enumerate(((-RW + 0.004, RF + 0.007), (-RW - 0.008, RF + 0.003), (-RW - 0.020, RF - 0.003))):
    c0 = BY - 0.036
    b.p("belt", us.ycyl(f"case{k}", 0.0060, c0, c0 + 0.051, x=x, z=z, verts=8, r2=0.0058, mat="brass"))
    b.p("belt", us.ycyl(f"bul{k}", 0.0039, c0 + 0.051, c0 + 0.071, x=x, z=z, verts=8, r2=0.0008, mat="brass"))
    b.p("belt", us.ycyl(f"link{k}", 0.0068, c0 + 0.008, c0 + 0.018, x=x, z=z, verts=8, mat="black"))
b.pivot("belt", (-RW + 0.004, BY, RF + 0.007), feedDir="1,0,0", pitch=0.012)

# 엘프식 흔적: 작은 창고 태그 (뒤 거치 받침)
vu.tag(b, (0.026, -0.322, RB - 0.034), scale=1.2, lines=("MNT", "C-0001", "포탑 공축"), yaw=0,
       cord_top=(0.024, -0.322, RB - 0.012))

# ================================================================== anchors
b.anchor("muzzle", (0, MUZ, ZB))
b.anchor("eject", (0, -0.110, RB - 0.006))              # 탄피: 아래
b.anchor("eject_link", (RW + 0.004, -0.090, ZB + 0.012))  # 링크: 오른쪽
b.anchor("mag_well", (-RW - 0.004, BY, RF + 0.007))    # 탄띠 입구 (왼쪽)

b.finish("weapons/us/m240_coax.glb", outline=0.003, fp="0.0,-0.12,-0.55",
         extra={"mountType": "coax"})
